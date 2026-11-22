"""gimg.py pieces that need no network: nothing here sends a request."""
import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import gimg


def fake_ok(seen):
    def fake(req, timeout):
        seen.append(req)
        return io.BytesIO(json.dumps({"data": []}).encode())
    return fake


def test_key_is_read_from_the_environment_only(monkeypatch, tmp_path):
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "auth.json").write_text(json.dumps({"OPENAI_API_KEY": "from-file"}))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(SystemExit):
        gimg.key()
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")
    assert gimg.key() == "from-env"


def test_official_address_and_model_by_default(monkeypatch):
    seen = []
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_IMAGE_MODEL", raising=False)
    monkeypatch.setattr(gimg, "key", lambda: "k")
    monkeypatch.setattr(gimg.urllib.request, "urlopen", fake_ok(seen))
    assert gimg.edit({"name": "x", "prompt": "p"}) == {"data": []}
    req = seen[0]
    assert req.full_url == "https://api.openai.com/v1/images/generations"
    assert req.get_header("Authorization") == "Bearer k"
    body = json.loads(req.data)
    assert body["model"] == "gpt-image-2.6-sunburst" and body["quality"] == "high"


def test_environment_overrides_address_and_model(monkeypatch, tmp_path):
    img = tmp_path / "wm.png"
    img.write_bytes(b"png")
    seen = []
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1/")
    monkeypatch.setenv("OPENAI_IMAGE_MODEL", "gpt-image-2.6-flare")
    monkeypatch.setattr(gimg, "key", lambda: "k")
    monkeypatch.setattr(gimg.urllib.request, "urlopen", fake_ok(seen))
    gimg.edit({"name": "x", "prompt": "p", "images": [str(img)]})
    gimg.edit({"name": "y", "prompt": "p", "images": [str(img)], "model": "gpt-image-2.6-sunburst"})
    assert seen[0].full_url == "https://example.test/v1/images/edits"
    assert b'name="model"\r\n\r\ngpt-image-2.6-flare\r\n' in seen[0].data
    assert b'name="image[]"; filename="wm.png"' in seen[0].data
    assert b'name="model"\r\n\r\ngpt-image-2.6-sunburst\r\n' in seen[1].data   # the job's own model wins


def test_server_errors_are_retried(monkeypatch):
    calls = []

    def fake(req, timeout):
        calls.append(1)
        if len(calls) < 3:
            raise urllib.error.HTTPError("u", 502 if len(calls) == 1 else 524, "bad gateway", {}, io.BytesIO(b"oops"))
        return io.BytesIO(json.dumps({"data": []}).encode())

    monkeypatch.setattr(gimg, "key", lambda: "k")
    monkeypatch.setattr(gimg, "WAIT", 0)
    monkeypatch.setattr(gimg.urllib.request, "urlopen", fake)
    assert gimg.edit({"name": "x", "prompt": "p"}) == {"data": []}
    assert len(calls) == 3


def test_other_errors_are_not_retried(monkeypatch):
    calls = []

    def fake(req, timeout):
        calls.append(1)
        raise urllib.error.HTTPError("u", 400, "bad request", {}, io.BytesIO(b"no"))

    monkeypatch.setattr(gimg, "key", lambda: "k")
    monkeypatch.setattr(gimg, "WAIT", 0)
    monkeypatch.setattr(gimg.urllib.request, "urlopen", fake)
    try:
        gimg.edit({"name": "x", "prompt": "p"})
    except RuntimeError as e:
        assert "http_400" in str(e)
    assert len(calls) == 1

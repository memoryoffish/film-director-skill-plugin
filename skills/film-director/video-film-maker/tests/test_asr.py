"""Offline tests for scripts/asr.py: backend choice, the audio cut and the line format (no model is loaded)."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import asr  # noqa: E402


def test_backend_is_the_first_installed_one_and_none_when_nothing_is(monkeypatch):
    have = {"whisper"}
    monkeypatch.setattr(asr.importlib.util, "find_spec", lambda name: object() if name in have else None)
    assert asr.pick_backend("auto") == "whisper"
    assert asr.pick_backend("mlx") is None
    have.clear()
    assert asr.pick_backend("auto") is None


def test_exit_code_3_when_no_backend(monkeypatch, capsys):
    monkeypatch.setattr(asr.importlib.util, "find_spec", lambda name: None)
    monkeypatch.setattr(sys, "argv", ["asr.py", "x.mp4"])
    assert asr.main() == 3
    assert "cannot be checked word by word" in capsys.readouterr().err


def test_cut_audio_takes_the_asked_seconds(tmp_path):
    src, wav = tmp_path / "tone.wav", tmp_path / "cut.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=3", str(src)], check=True)
    assert asr.cut_audio(str(src), str(wav), 1.0, 2.5)
    assert abs((wav.stat().st_size - 44) / (16000 * 2) - 1.5) < 0.05      # 16 kHz mono 16-bit
    assert not asr.cut_audio(str(tmp_path / "missing.mp4"), str(tmp_path / "no.wav"), 0.0, None)


def test_lines_are_in_film_seconds():
    assert asr.lines([{"start": 0.5, "end": 1.25, "text": " 有人在吗 "}], 10.0) == [{"start": 10.5, "end": 11.25, "text": "有人在吗"}]

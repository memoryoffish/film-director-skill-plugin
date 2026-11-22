"""Image backend: gpt-image through the official OpenAI Images API. Several input images + one prompt -> images.

Written from the official docs, checked 2026-11-22:
  edit           https://developers.openai.com/api/reference/resources/images/methods/edit
  generate       https://developers.openai.com/api/reference/resources/images/methods/generate
  guide, sizes   https://developers.openai.com/api/docs/guides/image-generation
  model          https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst
Ran for real on 2026-11-22 through an OpenAI-compatible gateway (one edit with one input image, OPENAI_BASE_URL set);
not yet run against api.openai.com itself.

A sheet: {"name", "prompt", "images": [paths, image 1 first], "size": "1536x864", "n": 1, "model", "quality"}.
With "images" it is an edit (POST /images/edits, multipart, one image[] part per image, at most 16); without, a plain
text-to-image generation (POST /images/generations, JSON). Model gpt-image-2.6-sunburst and quality high unless the sheet
says otherwise. Errors 499, 502, 503, 504, 520, 522, 524 and dropped connections are tried again twice, 20 s then 40 s
later; other errors are recorded as they are. The key is OPENAI_API_KEY from the environment, read in process and never
printed; the address is machine.IMAGE_BASE (OPENAI_BASE_URL overrides it).

Leaves, per job: OUT/<name>.png (…_2.png for n > 1) and OUT/<name>.json. A job whose OUT/<name>.json says ok is
skipped; delete that file to draw it again.
"""
from __future__ import annotations

import base64
import hashlib
import http.client
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import machine

TRIES, WAIT = 3, 20
RETRY_HTTP = {499, 502, 503, 504, 520, 522, 524}
MAX_IMAGES = 16


def key() -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set: put the OpenAI API key in that variable")
    return os.environ["OPENAI_API_KEY"]


def multipart(fields: list[tuple[str, str]], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    b = uuid.uuid4().hex
    parts = []
    for k, v in fields:
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, p in files:
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{p.name}"\r\nContent-Type: {mime}\r\n\r\n'.encode() + p.read_bytes() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={b}"


def fields(job: dict) -> dict:
    return {"model": job.get("model", "gpt-image-2.6-sunburst"), "prompt": job["prompt"], "size": job.get("size", "1536x864"),
            "quality": job.get("quality", "high"), "n": job.get("n", 1)}


def build(job: dict, k: str) -> urllib.request.Request:
    common = fields(job)
    if job.get("images"):
        body, ctype = multipart([(a, str(b)) for a, b in common.items()], [("image[]", Path(p)) for p in job["images"]])
        url = machine.IMAGE_BASE + "/images/edits"
    else:
        body, ctype, url = json.dumps(common).encode(), "application/json", machine.IMAGE_BASE + "/images/generations"
    return urllib.request.Request(url, data=body, method="POST", headers={"Authorization": "Bearer " + k, "Content-Type": ctype, "User-Agent": "film-crew-backends"})


def edit(job: dict) -> dict:
    """With "images": an edit (image 1 first). Without: a plain text-to-image generation (character sheets, props, sets)."""
    k = key()
    req = build(job, k)
    for attempt in range(1, TRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = f"http_{e.code}: {e.read(1500).decode('utf-8', 'replace').replace(k, '<key>')[:600]}"
            if e.code not in RETRY_HTTP or attempt == TRIES:
                raise RuntimeError(msg) from None
        except (urllib.error.URLError, ConnectionError, TimeoutError, http.client.HTTPException) as e:
            msg = f"connection: {str(e).replace(k, '<key>')[:300]}"
            if attempt == TRIES:
                raise RuntimeError(msg) from None
        print(f"retry {job['name']} ({attempt}/{TRIES - 1}) after {msg[:80]}", flush=True)
        time.sleep(WAIT * attempt)


def one(job: dict, out: Path) -> bool:
    state = out / f"{job['name']}.json"
    if state.exists() and json.loads(state.read_text()).get("ok"):
        return True
    t = time.time()
    try:
        resp = edit(job)
        for i, d in enumerate(resp["data"]):
            (out / (f"{job['name']}.png" if i == 0 else f"{job['name']}_{i + 1}.png")).write_bytes(base64.b64decode(d["b64_json"]))
        state.write_text(json.dumps({"ok": True, "job": job, "usage": resp.get("usage"), "images": len(resp["data"]), "seconds": round(time.time() - t)}, ensure_ascii=False, indent=1))
        print("done", job["name"], len(resp["data"]), "images", round(time.time() - t), "s", resp.get("usage"), flush=True)
        return True
    except Exception as e:  # noqa: BLE001 - record and go on with the other jobs
        state.write_text(json.dumps({"ok": False, "job": job, "error": str(e)[:800], "seconds": round(time.time() - t)}, ensure_ascii=False, indent=1))
        print("FAILED", job["name"], str(e)[:400], flush=True)
        return False


def run(jobs: list[dict], out: Path) -> list[bool]:
    out.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(machine.WORKERS["openai_image"]) as pool:
        return list(pool.map(lambda j: one(j, out), jobs))


def problem(job: dict) -> str:
    if not job.get("prompt"):
        return "prompt is required"
    if len(job.get("images") or []) > MAX_IMAGES:
        return f"at most {MAX_IMAGES} input images"
    return ""


def request(job: dict) -> dict:
    """The POST that would be sent, built by the same code as a real one; nothing is sent and no key is read.
    The multipart boundary is random per request, so body_sha256 holds for the boundary shown only."""
    req = build(job, "<key not read>")
    ctype = req.get_header("Content-type")
    out = {"model": fields(job)["model"], "method": req.get_method(), "url": req.full_url,
           "headers": {k: v for k, v in req.header_items() if k != "Authorization"},
           "body_sha256": hashlib.sha256(req.data).hexdigest(), "body_bytes": len(req.data), "fields": fields(job)}
    if ctype.startswith("multipart/"):
        out["files"] = [{"field": "image[]", "path": str(p), "sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest()}
                        for p in job["images"]]
    return out

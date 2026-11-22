#!/usr/bin/env python3
"""gpt-image through the official OpenAI Images API: several input images + one prompt -> images.

python3 gimg.py [--out DIR] JOB.json [JOB.json …]
    job: {"name", "prompt", "images": [paths, Image 1 first], "size": "1536x864", "n": 1}
Leave "images" out for a plain text-to-image generation (character sheets, props, sets).
Model gpt-image-2.6-sunburst (OPENAI_IMAGE_MODEL overrides it; a job's "model" wins), quality high unless the job says otherwise. Writes DIR/<name>.png (…_2.png) and DIR/<name>.json
(DIR defaults to ./out). A job whose DIR/<name>.json says ok is skipped; delete that file to draw it again. Four jobs run at once.
Server errors (499, 502, 503, 504, 520, 522, 524) and dropped connections are retried twice; other errors are recorded as they are.
Address: OPENAI_BASE_URL, default https://api.openai.com/v1. The key is OPENAI_API_KEY from the environment only (no file is read),
read in process and never printed. Official docs: https://developers.openai.com/api/reference/resources/images/methods/edit
and https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst (checked 2026-11-22).
"""
from __future__ import annotations

import base64, http.client, json, os, sys, time, urllib.error, urllib.request, uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DEFAULT_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-image-2.6-sunburst"
OUT = Path("out")
TRIES, WAIT = 3, 20                     # a server error or a dropped connection is tried again twice, 20 s then 40 s later
RETRY_HTTP = {499, 502, 503, 504, 520, 522, 524}


def key() -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set")
    return os.environ["OPENAI_API_KEY"]


def base() -> str:
    return os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE).rstrip("/")


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


def edit(job: dict) -> dict:
    """With "images": an edit (Image 1 first). Without: a plain text-to-image generation (character sheets, props, sets)."""
    k = key()
    common = {"model": job.get("model", os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_MODEL)), "prompt": job["prompt"], "size": job.get("size", "1536x864"),
              "quality": job.get("quality", "high"), "n": job.get("n", 1)}
    if job.get("images"):
        body, ctype = multipart([(a, str(b)) for a, b in common.items()], [("image[]", Path(p)) for p in job["images"]])
        url = base() + "/images/edits"
    else:
        body, ctype, url = json.dumps(common).encode(), "application/json", base() + "/images/generations"
    req = urllib.request.Request(url, data=body, method="POST", headers={"Authorization": "Bearer " + k, "Content-Type": ctype,
                                                                         "User-Agent": "blender-previz-gimg"})
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


def one(path: str) -> None:
    job = json.loads(Path(path).read_text())
    state = OUT / f"{job['name']}.json"
    if state.exists() and json.loads(state.read_text()).get("ok"):
        return
    t = time.time()
    try:
        resp = edit(job)
        for i, d in enumerate(resp["data"]):
            (OUT / (f"{job['name']}.png" if i == 0 else f"{job['name']}_{i + 1}.png")).write_bytes(base64.b64decode(d["b64_json"]))
        state.write_text(json.dumps({"ok": True, "job": job, "usage": resp.get("usage"), "images": len(resp["data"]), "seconds": round(time.time() - t)}, ensure_ascii=False, indent=1))
        print("done", job["name"], len(resp["data"]), "images", round(time.time() - t), "s", resp.get("usage"), flush=True)
    except Exception as e:  # noqa: BLE001 - record and go on with the other jobs
        state.write_text(json.dumps({"ok": False, "job": job, "error": str(e)[:800], "seconds": round(time.time() - t)}, ensure_ascii=False, indent=1))
        print("FAILED", job["name"], str(e)[:400], flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--out" in args:
        i = args.index("--out")
        OUT = Path(args[i + 1])
        del args[i:i + 2]
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(one, args))

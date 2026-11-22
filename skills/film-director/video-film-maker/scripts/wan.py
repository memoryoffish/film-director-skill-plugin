"""Wan 3.0 video client for the DashScope async task API (stdlib only).

Default model is `wan3.0-video`, the standard ("普通") queue; `wan3.0-video-prime` is the fast queue.
The state of every job is saved before its POST, and a POST whose acknowledgement was lost is never
replayed (the job needs review); polling resumes by task id. The key is read in process and never
printed or written to disk.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import uuid
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.environ.get("OCCUT_DASHSCOPE_BASE", "https://dashscope.aliyuncs.com/api/v1")
MODEL = "wan3.0-video"
MAX_CLIP_S = 15  # this skill's cap per clip; the API itself allows up to 30
RESOLUTIONS = ("480P", "720P", "1080P")
DEFAULT_ENV_FILES = ""
BAD_END = {"FAILED", "CANCELED", "UNKNOWN"}


def log(event: str, **fields) -> None:
    print(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **fields},
                     ensure_ascii=False), flush=True)


def read_key(env_files: list[Path] | None = None) -> str:
    if os.environ.get("DASHSCOPE_API_KEY"):
        return os.environ["DASHSCOPE_API_KEY"]
    if env_files is None:
        env_files = [Path(p) for p in os.environ.get("OCCUT_ENV_FILES", DEFAULT_ENV_FILES).split(":") if p]
    for f in env_files:
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            s = line.strip().removeprefix("export ").strip()
            if s.startswith("DASHSCOPE_API_KEY="):
                v = s.split("=", 1)[1].strip()
                if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
                    v = v[1:-1]
                if v:
                    return v
    raise SystemExit("DASHSCOPE_API_KEY not found (env var or OCCUT_ENV_FILES)")


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def data_url(path: Path) -> str:
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    kind = mime.get(Path(path).suffix.lower())
    if kind is None:
        raise ValueError(f"unsupported image type: {path}")
    return f"data:{kind};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def build_payload(job: dict) -> dict:
    """The request body with images as file references (resolved to base64 only when sending)."""
    duration = int(job.get("duration", 5))
    if not 2 <= duration <= MAX_CLIP_S:
        raise ValueError(f"{job.get('name')}: duration {duration} s is outside [2, {MAX_CLIP_S}]")
    resolution = job.get("resolution", "1080P")
    if resolution not in RESOLUTIONS:
        raise ValueError(f"{job.get('name')}: resolution {resolution} not in {RESOLUTIONS}")
    if not job.get("prompt"):
        raise ValueError(f"{job.get('name')}: empty prompt")
    media = [{"type": t, "path": str(job[t]), "sha256": sha256(job[t])}
             for t in ("first_frame", "last_frame", "reference_video") if job.get(t)]
    refs = job.get("reference_images") or []
    if len(refs) > 10:
        raise ValueError(f"{job.get('name')}: at most 10 reference images")
    media += [{"type": "reference_image", "path": str(r), "sha256": sha256(r)} for r in refs]  # 图1, 图2, … in order
    kinds = {m["type"] for m in media}
    if kinds & {"first_frame", "last_frame"} and kinds & {"reference_video", "reference_image"}:
        raise ValueError(f"{job.get('name')}: first/last frame cannot be mixed with reference video or images")
    params = {"resolution": resolution, "ratio": job.get("ratio", "adaptive" if media else "16:9"),
              "duration": duration, "audio": bool(job.get("audio", True)),
              "prompt_extend": bool(job.get("prompt_extend", False)), "watermark": False}
    if job.get("seed") is not None:
        params["seed"] = int(job["seed"])
    model = job.get("model", MODEL)
    if model.startswith("happyhorse"):
        model, params = happyhorse(model, kinds, params, job.get("name"))
    body = {"model": model, "input": {"prompt": job["prompt"]}, "parameters": params}
    if media:
        body["input"]["media"] = media
    return body


def happyhorse(model: str, kinds: set, params: dict, name: str | None) -> tuple[str, dict]:
    """HappyHorse (same DashScope endpoint) has one model per mode and fewer parameters: text (-t2v), first frame
    (-i2v, follows the frame's ratio), reference images (-r2v, referred to as [Image 1], [Image 2] … in the prompt).
    No last frame, no reference video, no audio or prompt_extend switch."""
    if kinds & {"last_frame", "reference_video"}:
        raise ValueError(f"{name}: {model} has no last frame or reference video")
    mode = "i2v" if "first_frame" in kinds else "r2v" if "reference_image" in kinds else "t2v"
    if model.count("-") == 1:  # "happyhorse-1.1" -> pick the model for this mode
        model = f"{model}-{mode}"
    elif not model.endswith(mode):
        raise ValueError(f"{name}: {model} does not take this input ({mode})")
    keep = {"resolution", "duration", "watermark", "seed"} | ({"ratio"} if mode != "i2v" else set())
    params = {k: v for k, v in params.items() if k in keep}
    if params.get("ratio") == "adaptive":
        params["ratio"] = "16:9"
    return model, params


def wire_payload(payload: dict, upload=None) -> dict:
    """Replace file references by URLs, checking the file did not change since planning: images go inline
    as base64; videos are uploaded with `upload(path) -> oss://...` (DashScope temporary storage, 48 h)."""
    body = json.loads(json.dumps(payload))
    for m in body["input"].get("media", []):
        if sha256(m["path"]) != m["sha256"]:
            raise RuntimeError(f"{m['path']} changed after the job was planned")
        path = m.pop("path")
        m.pop("sha256")
        if m["type"] == "reference_video":
            if upload is None:
                raise RuntimeError("a reference video needs an uploader")
            m["url"] = upload(path)
        else:
            m["url"] = data_url(path)
    return body


def multipart(fields: dict, file_field: str, path: Path) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in fields.items()]
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{Path(path).name}"'
                 f'\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + Path(path).read_bytes() + b"\r\n")
    return b"".join(parts) + f"--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


class Client:
    def __init__(self, key: str, base: str = BASE):
        self.key, self.base = key, base
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(self, method: str, path: str, payload: dict | None = None, oss: bool = False) -> dict:
        headers = {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"}
        if method == "POST":
            headers["X-DashScope-Async"] = "enable"
        if oss:
            headers["X-DashScope-OssResourceResolve"] = "enable"
        req = urllib.request.Request(self.base + path, method=method, headers=headers,
                                     data=json.dumps(payload).encode() if payload else None)
        try:
            with self.opener.open(req, timeout=120 if method == "POST" else 30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read(4000).decode("utf-8", "replace").replace(self.key, "<redacted>")
            log("api_error", method=method, http_status=e.code, body=body[:600])
            raise RuntimeError(f"http_{e.code}: {body[:300]}") from None

    def upload(self, path: str, model: str) -> str:
        """Put a local file in DashScope temporary storage (valid 48 h) and return its oss:// URL."""
        policy = self.request("GET", f"/uploads?action=getPolicy&model={model}")["data"]
        key = f"{policy['upload_dir']}/{uuid.uuid4().hex[:8]}_{Path(path).name}"
        body, ctype = multipart({"OSSAccessKeyId": policy["oss_access_key_id"], "Signature": policy["signature"],
                                 "policy": policy["policy"], "x-oss-object-acl": policy["x_oss_object_acl"],
                                 "x-oss-forbid-overwrite": policy["x_oss_forbid_overwrite"], "key": key,
                                 "success_action_status": "200"}, "file", Path(path))
        req = urllib.request.Request(policy["upload_host"], data=body, method="POST",
                                     headers={"Content-Type": ctype})
        with self.opener.open(req, timeout=300) as r:
            if r.status != 200:
                raise RuntimeError(f"upload failed: http {r.status}")
        log("uploaded", path=str(path), oss=f"oss://{key}")
        return f"oss://{key}"

    def download(self, url: str, dst: Path) -> None:
        tmp = dst.with_suffix(".partial")
        with self.opener.open(url, timeout=300) as stream, tmp.open("wb") as f:
            while chunk := stream.read(1 << 20):
                f.write(chunk)
        tmp.replace(dst)


def save(path: Path, value: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1))
    tmp.replace(path)


def probe(video: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames",
                          "-of", "json", str(video)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def submit(state: dict, path: Path, client: Client) -> None:
    if state.get("status"):
        raise RuntimeError(f"{state['name']}: an earlier POST has no task id; review before resubmitting")
    model = state["payload"]["model"]
    wire = wire_payload(state["payload"], lambda p: client.upload(p, model))  # uploads happen before the POST
    oss = any(m["url"].startswith("oss://") for m in wire["input"].get("media", []))
    state["status"] = "dispatching"
    save(path, state)  # never replay a POST whose acknowledgement was lost
    response = client.request("POST", "/services/aigc/video-generation/video-synthesis", wire, oss=oss)
    task = response.get("output", {})
    if not task.get("task_id"):
        raise RuntimeError(f"{state['name']}: submission returned no task id")
    state.update(task_id=task["task_id"], status=task.get("task_status", "PENDING"),
                 request_id=response.get("request_id"), submitted_utc=time.time())
    save(path, state)
    log("submitted", name=state["name"], task_id=state["task_id"], model=state["payload"]["model"])


def run_job(job: dict, out_dir: Path, client: Client, poll_s: float = 10.0) -> dict:
    """Submit (once) and poll one job until its video is downloaded. Returns the saved state."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{job['name']}.json"
    planned = build_payload(job)
    state = json.loads(path.read_text()) if path.exists() else {
        "name": job["name"], "job": {k: str(v) if isinstance(v, Path) else v for k, v in job.items()},
        "payload": planned}
    if state["payload"] != planned:
        raise RuntimeError(f"{job['name']}: an earlier job with this name had other parameters; use a new name")
    if state.get("status") == "DOWNLOADED":
        return state
    if not state.get("task_id"):
        submit(state, path, client)
    video = out_dir / f"{job['name']}.mp4"
    while state.get("status") != "DOWNLOADED":
        resp = client.request("GET", "/tasks/" + state["task_id"])
        task = resp.get("output", {})
        state["status"] = task.get("task_status", "UNKNOWN")
        if state["status"] == "SUCCEEDED":
            client.download(task["video_url"], video)
            state.update(status="DOWNLOADED", media=probe(video), usage=resp.get("usage") or task.get("usage"),
                         timing={k: task.get(k) for k in ("submit_time", "scheduled_time", "end_time")},
                         actual_prompt=task.get("actual_prompt"))
            save(path, state)
            log("downloaded", name=job["name"], usage=state["usage"], timing=state["timing"])
        elif state["status"] in BAD_END:
            state["failure"] = {k: task.get(k) for k in ("code", "message")}
            save(path, state)
            raise RuntimeError(f"{job['name']}: {state['status']} {state['failure']}")
        else:
            save(path, state)
            time.sleep(poll_s)
    return state

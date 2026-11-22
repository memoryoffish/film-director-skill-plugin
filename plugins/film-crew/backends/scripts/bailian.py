"""DashScope backend: Wan 3.0 and HappyHorse 1.1 through the DashScope async task API (stdlib only).

Official docs (Alibaba Cloud Model Studio, checked 2026-11-22):
  Wan 3.0        https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference
  HappyHorse     https://help.aliyun.com/zh/model-studio/happyhorse-text-to-video-api-reference (and the
                 -image-to-video- and -reference-to-video- pages next to it)
  addresses      https://help.aliyun.com/zh/model-studio/regions

Default model is `wan3.0-video`, the standard ("普通") queue; `wan3.0-video-prime` is the fast queue; `happyhorse-1.1`
picks its -t2v / -i2v / -r2v model from the inputs. The state of every job is saved before its POST, and a POST whose
acknowledgement was lost is never replayed (the job needs review); polling resumes by task id. The key is
DASHSCOPE_API_KEY from the environment, read in process and never printed or written to disk. The address is
machine.DASHSCOPE_BASE (DASHSCOPE_BASE_URL overrides it).

Ran for real on 2026-11-20 and again on 2026-11-22 with the key read from DASHSCOPE_API_KEY (examples/smoke/).

Leaves, per job: OUT/<name>.json (state), OUT/<name>.mp4 (the clip), and one line in logs/results.jsonl.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import threading
import uuid
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import machine

BASE = machine.DASHSCOPE_BASE
SUBMIT = "/services/aigc/video-generation/video-synthesis"
MODEL = "wan3.0-video"
MAX_CLIP_S = 15  # this backend's cap per clip; the API itself allows up to 30
RESOLUTIONS = ("480P", "720P", "1080P")
BAD_END = {"FAILED", "CANCELED", "UNKNOWN"}
RESULTS = Path("logs") / "results.jsonl"
_lock = threading.Lock()


def log(event: str, **fields) -> None:
    print(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **fields},
                     ensure_ascii=False), flush=True)


def read_key() -> str:
    if not os.environ.get("DASHSCOPE_API_KEY"):
        raise SystemExit("DASHSCOPE_API_KEY is not set: put the Model Studio (DashScope) API key in that variable")
    return os.environ["DASHSCOPE_API_KEY"]


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

    def build(self, method: str, path: str, payload: dict | None = None, oss: bool = False) -> urllib.request.Request:
        headers = {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"}
        if method == "POST":
            headers["X-DashScope-Async"] = "enable"
        if oss:
            headers["X-DashScope-OssResourceResolve"] = "enable"
        return urllib.request.Request(self.base + path, method=method, headers=headers,
                                      data=json.dumps(payload).encode() if payload else None)

    def request(self, method: str, path: str, payload: dict | None = None, oss: bool = False) -> dict:
        req = self.build(method, path, payload, oss)
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
    response = client.request("POST", SUBMIT, wire, oss=oss)
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


def one(job: dict, client: Client, out: Path, results: Path = RESULTS) -> bool:
    """Run one job to the end and append its outcome to `results`. A dropped connection while polling only resumes
    polling (no new submission); a failed or rejected task is recorded and not retried."""
    state_path, ok, err, state = out / f"{job['name']}.json", False, "", None
    for _ in range(30):
        try:
            state, ok = run_job(job, out, client), True
            break
        except Exception as e:  # noqa: BLE001 - decide below whether it is the task or the connection
            err = f"{type(e).__name__}: {e}"[:600]
            state = json.loads(state_path.read_text()) if state_path.exists() else {}
            if state.get("task_id") and state.get("status") not in BAD_END:
                log("poll_error_resuming", name=job["name"], error=err)
                time.sleep(30)
                continue
            break
    with _lock, results.open("a") as f:
        f.write(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "name": job["name"], "ok": ok,
                            "usage": (state or {}).get("usage") if ok else None, "error": None if ok else err,
                            "task_id": (state or {}).get("task_id")}, ensure_ascii=False) + "\n")
    return ok


def run(jobs: list[dict], out: Path) -> list[bool]:
    """Run jobs, a few at once. A job that already has OUT/<name>.mp4 is skipped."""
    out.mkdir(parents=True, exist_ok=True)
    RESULTS.parent.mkdir(exist_ok=True)
    jobs = [j for j in jobs if not (out / f"{j['name']}.mp4").exists()]
    client = Client(read_key())
    with ThreadPoolExecutor(machine.WORKERS["bailian"]) as pool:
        done = list(pool.map(lambda j: one(j, client, out), jobs))
    log("all_done", jobs=len(jobs))
    return done


def problem(job: dict) -> str:
    """Why this backend cannot take the sheet ("" when it can). Reads the media files, sends nothing."""
    try:
        build_payload(job)
    except (ValueError, OSError, KeyError) as e:
        return str(e)
    return ""


def request(job: dict) -> dict:
    """The POST that would submit this job, built by the same code as a real submission; nothing is sent or uploaded.
    A reference video would first be uploaded to DashScope temporary storage: it shows as a placeholder oss:// URL."""
    payload = build_payload(job)
    videos = [m["path"] for m in payload["input"].get("media", []) if m["type"] == "reference_video"]
    wire = wire_payload(payload, lambda p: f"oss://<not uploaded: {Path(p).name}>")
    oss = any(m["url"].startswith("oss://") for m in wire["input"].get("media", []))
    req = Client("<key not read>").build("POST", SUBMIT, wire, oss=oss)
    return {"model": payload["model"], "method": req.get_method(), "url": req.full_url,
            "headers": {k: v for k, v in req.header_items() if k != "Authorization"},
            "body_sha256": hashlib.sha256(req.data).hexdigest(), "body_bytes": len(req.data),
            "uploads": [f"{p} -> DashScope temporary storage (48 h)" for p in videos], "payload": payload}

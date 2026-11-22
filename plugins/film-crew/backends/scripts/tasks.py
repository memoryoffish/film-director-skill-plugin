"""What the Ark and MiniMax adapters share (stdlib only): a job is a task that is submitted once, polled by its id and
downloaded, with the same records as bailian.py.

An adapter passes its own module as `api`. The module has:
    KEY_ENV, BASE, SUBMIT    the environment variable holding the key, the address, the create-task path
    WORKERS                  its key in machine.WORKERS
    build_payload(job)       {"model", "content", "parameters"}, files as references made by media_item(); raises
                             ValueError when the backend cannot take the sheet
    created_id(response)     the task id in the create-task response
    task_path(task_id)       the query-task path
    result(response)         {"status" (the vendor's, lower case), "video_url", "last_frame_url", "seconds", "usage",
                              "error", "created_at", "updated_at"} from a query-task response

The body sent is the payload with its parameters at the top level and every file inline as a base64 data URL
(wire_payload()). Leaves, per job: OUT/<name>.json (state, saved before the POST, so a POST whose acknowledgement was
lost is never replayed), OUT/<name>.mp4, OUT/<name>.last_frame_url when the task returned its last frame (a link that
lasts 24 h), and one line in logs/results.jsonl. The state has the fields bailian.py writes: status (DOWNLOADED, or
FAILED with the vendor's status in `failure`; upper case while it runs), payload.parameters.resolution, usage.duration
(seconds of video made), timing.submit_time / end_time.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import machine

RESULTS = Path("logs") / "results.jsonl"
BAD_END = {"failed", "cancelled", "expired"}
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".mp4": "video/mp4"}
_lock = threading.Lock()


def log(event: str, **fields) -> None:
    print(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **fields},
                     ensure_ascii=False), flush=True)


def read_key(env: str) -> str:
    if not os.environ.get(env):
        raise SystemExit(f"{env} is not set: put the API key in that environment variable")
    return os.environ[env]


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def data_url(path) -> str:
    kind = MIME.get(Path(path).suffix.lower())
    if kind is None:
        raise ValueError(f"unsupported file type: {path}")
    return f"data:{kind};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def media_item(kind: str, value: str, role: str) -> dict:
    """One content item for a file the sheet names (kind "image_url" or "video_url"), held as path + sha256 until it is
    sent. "@NAME" as an image is the last frame the earlier job NAME got back."""
    if str(value).startswith("@"):
        ref = {"last_frame_of": str(value)[1:]}
    else:
        ref = {"path": str(value), "sha256": sha256(value)}
    return {"type": kind, kind: ref, "role": role}


def wire_payload(payload: dict, out: Path | None) -> dict:
    """The body to POST: parameters at the top level, files inline (checked unchanged since planning), "@NAME" replaced
    by the link in OUT/NAME.last_frame_url (a placeholder when `out` is None)."""
    body = {"model": payload["model"], "content": json.loads(json.dumps(payload["content"])), **payload["parameters"]}
    for item in body["content"]:
        ref = item.get(item["type"])
        if not isinstance(ref, dict):
            continue
        if "last_frame_of" in ref:
            name = ref.pop("last_frame_of")
            if out is None:
                ref["url"] = f"<last frame of {name}, read from OUT/{name}.last_frame_url when sending>"
                continue
            link = out / f"{name}.last_frame_url"
            if not link.exists():
                raise ValueError(f"no last frame for {name}: run {name} first, with \"return_last_frame\": true")
            ref["url"] = link.read_text().strip()
        else:
            path = ref.pop("path")
            if sha256(path) != ref.pop("sha256"):
                raise RuntimeError(f"{path} changed after the job was planned")
            ref["url"] = data_url(path)
    return body


class Client:
    def __init__(self, key: str, base: str):
        self.key, self.base = key, base

    def build(self, method: str, path: str, body: dict | None = None) -> urllib.request.Request:
        headers = {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"}
        return urllib.request.Request(self.base + path, method=method, headers=headers,
                                      data=json.dumps(body).encode() if body is not None else None)

    def call(self, method: str, path: str, body: dict | None = None) -> dict:
        try:
            with urllib.request.urlopen(self.build(method, path, body), timeout=120 if method == "POST" else 30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            text = e.read(4000).decode("utf-8", "replace").replace(self.key, "<redacted>")
            log("api_error", method=method, http_status=e.code, body=text[:600])
            raise RuntimeError(f"http_{e.code}: {text[:300]}") from None

    def download(self, url: str, dst: Path) -> None:
        tmp = dst.with_suffix(".partial")
        with urllib.request.urlopen(url, timeout=300) as stream, tmp.open("wb") as f:
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


def stamp(t) -> str | None:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) if t else None


def submit(api, state: dict, path: Path, out: Path, client: Client) -> None:
    if state.get("status"):
        raise RuntimeError(f"{state['name']}: an earlier POST has no task id; review before resubmitting")
    body = wire_payload(state["payload"], out)
    state["status"] = "dispatching"
    save(path, state)  # never replay a POST whose acknowledgement was lost
    task_id = api.created_id(client.call("POST", api.SUBMIT, body))
    if not task_id:
        raise RuntimeError(f"{state['name']}: submission returned no task id")
    state.update(task_id=task_id, status="SUBMITTED", submitted_utc=time.time())
    save(path, state)
    log("submitted", name=state["name"], task_id=task_id, model=state["payload"]["model"])


def run_job(api, job: dict, out: Path, client: Client, poll_s: float = 10.0) -> dict:
    """Submit (once) and poll one job until its video is downloaded. Returns the saved state."""
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{job['name']}.json"
    planned = api.build_payload(job)
    state = json.loads(path.read_text()) if path.exists() else {"name": job["name"], "job": job, "payload": planned}
    if state["payload"] != planned:
        raise RuntimeError(f"{job['name']}: an earlier job with this name had other parameters; use a new name")
    if state.get("status") == "DOWNLOADED":
        return state
    if not state.get("task_id"):
        submit(api, state, path, out, client)
    video = out / f"{job['name']}.mp4"
    while True:
        r = api.result(client.call("GET", api.task_path(state["task_id"])))
        status = str(r.get("status") or "unknown").lower()
        state["timing"] = {"submit_time": stamp(r.get("created_at"))}
        if status == "succeeded":
            client.download(r["video_url"], video)
            if r.get("last_frame_url"):
                link = out / f"{job['name']}.last_frame_url"
                link.write_text(r["last_frame_url"])
                link.chmod(0o600)
            state.update(status="DOWNLOADED", media=probe(video), last_frame=bool(r.get("last_frame_url")),
                         usage={**(r.get("usage") or {}), "duration": r.get("seconds")})
            state["timing"]["end_time"] = stamp(r.get("updated_at"))
            save(path, state)
            log("downloaded", name=job["name"], usage=state["usage"], timing=state["timing"])
            return state
        if status in BAD_END:
            state.update(status="FAILED", failure={"status": status, "error": r.get("error")})
            state["timing"]["end_time"] = stamp(r.get("updated_at"))
            save(path, state)
            raise RuntimeError(f"{job['name']}: {status} {r.get('error')}")
        state["status"] = status.upper()
        save(path, state)
        time.sleep(poll_s)


def one(api, job: dict, client: Client, out: Path, results: Path = RESULTS) -> bool:
    """Run one job to the end and append its outcome to `results`. A dropped connection while polling only resumes
    polling (no new submission); a failed or rejected task is recorded and not retried."""
    state_path, ok, err, state = out / f"{job['name']}.json", False, "", None
    for _ in range(30):
        try:
            state, ok = run_job(api, job, out, client), True
            break
        except Exception as e:  # noqa: BLE001 - decide below whether it is the task or the connection
            err = f"{type(e).__name__}: {e}"[:600]
            state = json.loads(state_path.read_text()) if state_path.exists() else {}
            if state.get("task_id") and state.get("status") != "FAILED":
                log("poll_error_resuming", name=job["name"], error=err)
                time.sleep(30)
                continue
            break
    with _lock, results.open("a") as f:
        f.write(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "name": job["name"], "ok": ok,
                            "usage": (state or {}).get("usage") if ok else None, "error": None if ok else err,
                            "task_id": (state or {}).get("task_id")}, ensure_ascii=False) + "\n")
    return ok


def run(api, jobs: list[dict], out: Path) -> list[bool]:
    """Run jobs, a few at once. A job that already has OUT/<name>.mp4 is skipped."""
    out.mkdir(parents=True, exist_ok=True)
    RESULTS.parent.mkdir(exist_ok=True)
    jobs = [j for j in jobs if not (out / f"{j['name']}.mp4").exists()]
    client = Client(read_key(api.KEY_ENV), api.BASE)
    with ThreadPoolExecutor(max(1, machine.WORKERS[api.WORKERS])) as pool:
        done = list(pool.map(lambda j: one(api, j, client, out), jobs))
    log("all_done", jobs=len(jobs))
    return done


def problem(api, job: dict) -> str:
    """Why this backend cannot take the sheet ("" when it can). Reads the media files, sends nothing."""
    try:
        api.build_payload(job)
    except (ValueError, OSError, KeyError) as e:
        return str(e)
    return ""


def request(api, job: dict) -> dict:
    """The POST that would submit this job, built by the same code as a real submission; nothing is sent and no key is
    read. `body` is that body with each inline file shortened to its path and size; body_sha256 is of the full body
    (a "@NAME" first frame is a placeholder here, the link itself is read when sending)."""
    payload = api.build_payload(job)
    body = wire_payload(payload, None)
    req = Client("<key not read>", api.BASE).build("POST", api.SUBMIT, body)
    shown = json.loads(json.dumps(body))
    for item, planned in zip(shown["content"], payload["content"]):
        ref = planned.get(planned["type"])
        if isinstance(ref, dict) and "path" in ref:
            item[item["type"]]["url"] = f"<base64 data URL of {ref['path']}, {len(item[item['type']]['url'])} chars>"
    return {"model": payload["model"], "method": req.get_method(), "url": req.full_url,
            "headers": {k: v for k, v in req.header_items() if k != "Authorization"},
            "body_sha256": hashlib.sha256(req.data).hexdigest(), "body_bytes": len(req.data), "body": shown,
            "files": [{"role": c["role"], **c[c["type"]]} for c in payload["content"]
                      if isinstance(c.get(c["type"]), dict) and "path" in c[c["type"]]]}

"""Volcengine Ark (火山方舟) backend: Seedance 2.5 and 2.0 through the official video generation task API (stdlib only).

Written from the official docs, checked 2026-11-22:
  create task        https://ark.volcengine.com/region:cn-beijing/docs/create-video-generation-task-api
  query task         https://ark.volcengine.com/region:cn-beijing/docs/get-video-generation-task-api
  address and key    https://ark.volcengine.com/region:cn-beijing/docs/base-url-and-authentication
  @图片N in prompts  https://ark.volcengine.com/region:cn-beijing/docs/seedance-2-5 (提示词规则)
Not yet run with a real key: the requests were checked offline against these docs only.

A sheet picks the model with "model": "seedance-2.5" or "seedance-2.0", or the official model id. Sheets written the plain
way (Wan style: "720P", "seed", 图N) are rewritten first (rewrite(), idempotent). Images go inline as base64 data URLs.
A reference video is refused: Ark takes videos only as public URLs or asset ids, and this backend sends local files.
With a first frame, Seedance 2.5 only takes ratio "adaptive" (the clip follows the frame), so that is what is sent.
"@NAME" as first_frame is the last frame the earlier job NAME got back (that job needs "return_last_frame": true; the
link lasts 24 h).

The key is ARK_API_KEY from the environment; the address is machine.ARK_BASE (ARK_BASE_URL overrides it).
Leaves, per job: see tasks.py (OUT/<name>.json, OUT/<name>.mp4, OUT/<name>.last_frame_url, logs/results.jsonl).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import machine
import tasks

SD25, SD20 = "doubao-seedance-2-5-260628", "doubao-seedance-2-0-260128"
MODELS = {"seedance-2.5": SD25, "seedance-2.0": SD20, SD25: SD25, SD20: SD20}
LIMITS = {SD25: ((4, 30), 30), SD20: ((4, 15), 9)}  # seconds per clip, reference images
RESOLUTIONS = ("480p", "720p", "1080p", "4k")
RATIOS = ("16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive")
KEY_ENV, BASE, WORKERS = "ARK_API_KEY", machine.ARK_BASE, "ark_video"
SUBMIT = "/contents/generations/tasks"
API = sys.modules[__name__]


def rewrite(job: dict) -> dict:
    """What a plain sheet needs for Seedance: no seed (Seedance 2.x has no seed parameter), lower-case resolution, image N
    called @图片N in the prompt. Applying it to a sheet already rewritten changes nothing."""
    job = {k: v for k, v in job.items() if k != "seed"}
    job["model"] = job.get("model") or "seedance-2.5"
    if "resolution" in job:
        job["resolution"] = str(job["resolution"]).lower()
    job["prompt"] = re.sub(r"图(\d+)", r"@图片\1", job.get("prompt") or "")
    return job


def build_payload(job: dict) -> dict:
    job = rewrite(job)
    name, model = job.get("name"), MODELS.get(job["model"])
    if model is None:
        raise ValueError(f"{name}: no Ark model {job['model']!r}")
    (lo, hi), max_refs = LIMITS[model]
    if job.get("reference_video"):
        raise ValueError(f"{name}: Ark takes a reference video only as a public URL or asset id, so this backend sends "
                         "none: feed reference images, or a first (and last) frame")
    if not job["prompt"]:
        raise ValueError(f"{name}: empty prompt")
    if "duration" not in job:
        raise ValueError(f"{name}: duration is required")
    if not lo <= int(job["duration"]) <= hi:
        raise ValueError(f"{name}: duration must be {lo}..{hi} s")
    resolution = job.get("resolution", "720p")
    if resolution not in RESOLUTIONS:
        raise ValueError(f"{name}: resolution {resolution} not in {RESOLUTIONS}")
    refs = job.get("reference_images") or []
    if len(refs) > max_refs:
        raise ValueError(f"{name}: at most {max_refs} reference images")
    ratio = "adaptive" if job.get("first_frame") and model == SD25 else job.get("ratio", "16:9")
    if ratio not in RATIOS:
        raise ValueError(f"{name}: ratio {ratio} not in {RATIOS}")
    content = [{"type": "text", "text": job["prompt"]}]
    content += [tasks.media_item("image_url", job[r], r) for r in ("first_frame", "last_frame") if job.get(r)]
    content += [tasks.media_item("image_url", p, "reference_image") for p in refs]  # @图片1, @图片2, … in order
    params = {"resolution": resolution, "ratio": ratio, "duration": int(job["duration"]),
              "generate_audio": bool(job.get("audio", True)), "watermark": False}
    if job.get("return_last_frame"):
        params["return_last_frame"] = True
    return {"model": model, "content": content, "parameters": params}


def created_id(response: dict) -> str | None:
    return response.get("id")


def task_path(task_id: str) -> str:
    return f"{SUBMIT}/{task_id}"


def result(response: dict) -> dict:
    content = response.get("content") or {}
    return {"status": response.get("status"), "video_url": content.get("video_url"),
            "last_frame_url": content.get("last_frame_url"), "seconds": response.get("duration"),
            "usage": response.get("usage"), "error": response.get("error"),
            "created_at": response.get("created_at"), "updated_at": response.get("updated_at")}


def problem(job: dict) -> str:
    return tasks.problem(API, job)


def run(jobs: list[dict], out: Path) -> list[bool]:
    return tasks.run(API, jobs, out)


def request(job: dict) -> dict:
    return tasks.request(API, job)

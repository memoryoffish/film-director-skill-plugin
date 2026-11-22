"""MiniMax backend: MiniMax H3-Max through the official video generation V2 task API (stdlib only).

Written from the official docs, checked 2026-11-22:
  create task   https://platform.minimax.io/docs/api-reference/video-generation-v2-create
                (China site: https://platform.minimax.cn/docs/api-reference/video-generation-v2-create)
  query task    https://platform.minimax.io/docs/api-reference/video-generation-v2-query
  guide         https://platform.minimax.io/docs/guides/video-generation
Not yet run with a real key: the requests were checked offline against these docs only.

A sheet picks the model with "model": "minimax-h3" or the official id "MiniMax-H3-Max". H3-Max is 5..15 s, "480P" or
"768P", at most 9 reference images; no seed, no last frame returned. Text-to-video needs a concrete ratio; with a first
frame the clip follows the frame and "adaptive" is sent. Images, and a reference video (.mp4), go inline as base64 data
URLs. The sheet's "prompt_extend" picks the prompt expansion: true is "balanced" (the API's default), false or absent is
"disabled". The prompt is sent as written (the docs call images 图1, 图2 and videos 视频1, as the sheets do).

The key is MINIMAX_API_KEY from the environment; the address is machine.MINIMAX_BASE (MINIMAX_BASE_URL overrides it; a
key belongs to one site, China or international).
Leaves, per job: see tasks.py (OUT/<name>.json, OUT/<name>.mp4, logs/results.jsonl).
"""
from __future__ import annotations

import sys
from pathlib import Path

import machine
import tasks

MODELS = {"minimax-h3": "MiniMax-H3-Max", "MiniMax-H3-Max": "MiniMax-H3-Max"}
DURATION, MAX_REFS, MAX_PROMPT = (5, 15), 9, 7000
RESOLUTIONS = ("480P", "768P")
RATIOS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16", "adaptive")
KEY_ENV, BASE, WORKERS = "MINIMAX_API_KEY", machine.MINIMAX_BASE, "minimax_video"
SUBMIT = "/v2/video_generation"
API = sys.modules[__name__]


def build_payload(job: dict) -> dict:
    name, model = job.get("name"), MODELS.get(job.get("model") or "minimax-h3")
    if model is None:
        raise ValueError(f"{name}: no MiniMax model {job.get('model')!r}")
    prompt = job.get("prompt") or ""
    if not prompt:
        raise ValueError(f"{name}: empty prompt")
    if len(prompt) > MAX_PROMPT:
        raise ValueError(f"{name}: the prompt is longer than {MAX_PROMPT} characters")
    if "duration" not in job:
        raise ValueError(f"{name}: duration is required")
    lo, hi = DURATION
    if not lo <= int(job["duration"]) <= hi:
        raise ValueError(f"{name}: duration must be {lo}..{hi} s")
    resolution = str(job.get("resolution", "768P")).upper()
    if resolution not in RESOLUTIONS:
        raise ValueError(f"{name}: resolution {resolution} not in {RESOLUTIONS}")
    refs, video = job.get("reference_images") or [], job.get("reference_video")
    if len(refs) > MAX_REFS:
        raise ValueError(f"{name}: at most {MAX_REFS} reference images")
    if video and Path(video).suffix.lower() != ".mp4":
        raise ValueError(f"{name}: the reference video goes inline as data:video/mp4, so it must be an .mp4")
    ratio = "adaptive" if job.get("first_frame") else job.get("ratio", "16:9")
    if ratio not in RATIOS:
        raise ValueError(f"{name}: ratio {ratio} not in {RATIOS}")
    if ratio == "adaptive" and not (job.get("first_frame") or refs or video):
        raise ValueError(f"{name}: text-to-video needs a ratio other than adaptive")
    content = [{"type": "text", "text": prompt}]
    content += [tasks.media_item("image_url", job[r], r) for r in ("first_frame", "last_frame") if job.get(r)]
    content += [tasks.media_item("image_url", p, "reference_image") for p in refs]  # 图1, 图2, … in order
    if video:
        content.append(tasks.media_item("video_url", video, "reference_video"))  # 视频1
    params = {"resolution": resolution, "duration": int(job["duration"]), "ratio": ratio,
              "generate_audio": bool(job.get("audio", True)),
              "extra": {"prompt_expansion_mode": "balanced" if job.get("prompt_extend") else "disabled"}}
    return {"model": model, "content": content, "parameters": params}


def created_id(response: dict) -> str | None:
    return response.get("task_id")


def task_path(task_id: str) -> str:
    return f"/v2/query/video_generation/{task_id}"


def result(response: dict) -> dict:
    task = response.get("task", response)
    usage = task.get("usage") or {}
    return {"status": task.get("status"), "video_url": (task.get("content") or {}).get("url"), "last_frame_url": None,
            "seconds": usage.get("output_seconds", task.get("duration")), "usage": usage, "error": task.get("error"),
            "created_at": task.get("created_at"), "updated_at": task.get("updated_at")}


def problem(job: dict) -> str:
    return tasks.problem(API, job)


def run(jobs: list[dict], out: Path) -> list[bool]:
    return tasks.run(API, jobs, out)


def request(job: dict) -> dict:
    return tasks.request(API, job)

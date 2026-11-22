#!/usr/bin/env python3
"""Cut a reference image for Wan's reference_images mode out of one frame of a clip.

    python3 refcrop.py CLIP FRAME X Y W H OUT.png [--min 540]

Exports frame FRAME at full resolution, crops the box (pixels of the source frame) and, if the shorter side is below
--min, upscales it with Lanczos to reach --min. The API rejects images with a side under 240 px. At 720P a person's
upper body is often only ~300 px: crop it natively and let --min bring it to 540. A prop (a watch, a pan) can be
cropped tight with --min 240. Prints the native crop size and the saved size.
"""
from __future__ import annotations

import argparse
import functools
import subprocess
from pathlib import Path

import cv2
import numpy as np

API_MIN = 240


@functools.lru_cache(maxsize=None)
def passthrough() -> tuple:
    """Keep every frame as it is: -fps_mode on ffmpeg 5.1 and later (newer ones dropped -vsync), -vsync 0 on older ones."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-h", "long"], capture_output=True, text=True).stdout
    return ("-fps_mode", "passthrough") if "-fps_mode" in out else ("-vsync", "0")


def frame_at(clip: str | Path, frame: int) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(clip), "-vf", f"select=eq(n\\,{frame})",
                          *passthrough(), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    if not raw:
        raise SystemExit(f"{clip}: no frame {frame}")
    return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)


def refcrop(clip: str | Path, frame: int, box: tuple[int, int, int, int], out: str | Path, min_side: int = 540) -> dict:
    img = frame_at(clip, frame)
    hh, ww = img.shape[:2]
    x, y, w, h = box
    x0, y0, x1, y1 = max(0, x), max(0, y), min(ww, x + w), min(hh, y + h)
    crop = img[y0:y1, x0:x1]
    ch, cw = crop.shape[:2]
    s = max(1.0, max(min_side, API_MIN) / min(ch, cw))
    if s > 1.0:
        crop = cv2.resize(crop, (int(round(cw * s)), int(round(ch * s))), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(str(out), crop)
    return {"out": str(out), "frame": frame, "box": [x0, y0, x1 - x0, y1 - y0], "saved": [crop.shape[1], crop.shape[0]],
            "scale": round(s, 3)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("frame", type=int)
    for k in ("x", "y", "w", "h"):
        ap.add_argument(k, type=int)
    ap.add_argument("out")
    ap.add_argument("--min", type=int, default=540, help="upscale until the shorter side reaches this (>= 240)")
    a = ap.parse_args()
    r = refcrop(a.clip, a.frame, (a.x, a.y, a.w, a.h), a.out, a.min)
    print(f"{r['out']}: frame {r['frame']} box {r['box']} -> saved {r['saved'][0]}x{r['saved'][1]} (x{r['scale']:.2f})")


if __name__ == "__main__":
    main()

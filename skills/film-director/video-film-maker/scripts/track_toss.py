#!/usr/bin/env python3
"""Track a tossed object (a pancake, a ball) by colour, ignoring look-alikes that do not move.

    python3 track_toss.py CLIP REF_FRAME START END OUT.json [--hsv-lo 8 90 150] [--hsv-hi 26 235 255] [--diff 60]

Per frame START..END: pixels inside the OpenCV HSV range AND different from REF_FRAME (taken before the toss, so
static objects of the same colour and the object still lying in the pan are ignored); the largest blob's centre,
top and bottom. Prints the highest frame (smallest centre y). Wan's tossed objects hover at the top for 0.2-1 s,
so cut a match on action at the highest point, not at a time-normalised phase of the flight.
"""
from __future__ import annotations

import argparse
import json

import cv2
import numpy as np


def read_frames(clip: str, want: set[int]) -> dict[int, np.ndarray]:
    cap = cv2.VideoCapture(clip)
    out, i = {}, 0
    while i <= max(want):
        ok, f = cap.read()
        if not ok:
            break
        if i in want:
            out[i] = f
        i += 1
    return out


def track(clip: str, ref_i: int, start: int, end: int, lo=(8, 90, 150), hi=(26, 235, 255), diff: int = 60) -> list[dict]:
    frames = read_frames(clip, {ref_i, *range(start, end + 1)})
    ref = cv2.GaussianBlur(frames[ref_i], (5, 5), 0).astype(np.int16)
    res = []
    for k in range(start, end + 1):
        if k not in frames:
            break
        f = frames[k]
        col = cv2.inRange(cv2.cvtColor(f, cv2.COLOR_BGR2HSV), np.array(lo), np.array(hi))
        moved = (np.abs(cv2.GaussianBlur(f, (5, 5), 0).astype(np.int16) - ref).sum(2) > diff).astype(np.uint8) * 255
        m = cv2.morphologyEx(cv2.bitwise_and(col, moved), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        n, _, st, cen = cv2.connectedComponentsWithStats(m)
        if n > 1:
            j = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            x, y, w, h, a = (int(v) for v in st[j])
            res.append({"i": k, "cx": round(float(cen[j][0]), 1), "cy": round(float(cen[j][1]), 1), "top": y,
                        "bottom": y + h, "w": w, "h": h, "area": a})
        else:
            res.append({"i": k})
    return res


def highest(res: list[dict]) -> dict | None:
    seen = [d for d in res if "cy" in d]
    return min(seen, key=lambda d: d["cy"]) if seen else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("ref", type=int)
    ap.add_argument("start", type=int)
    ap.add_argument("end", type=int)
    ap.add_argument("out")
    ap.add_argument("--hsv-lo", type=int, nargs=3, default=[8, 90, 150])
    ap.add_argument("--hsv-hi", type=int, nargs=3, default=[26, 235, 255])
    ap.add_argument("--diff", type=int, default=60)
    a = ap.parse_args()
    res = track(a.clip, a.ref, a.start, a.end, tuple(a.hsv_lo), tuple(a.hsv_hi), a.diff)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=0)
    top = highest(res)
    print("highest:", top)


if __name__ == "__main__":
    main()

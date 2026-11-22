#!/usr/bin/env python3
"""Does one colour fill the frame? Per frame: share of pixels in a hue range, the frame's median colour (HSV hue,
CIE L*a*b*) and the worst cell of a 4x8 grid (Delta E 76 from the frame's median colour).

    python3 colorfill.py CLIP OUT.json [--hue 8 50] [--smin 90] [--vmin 60] [--fill 0.97] [--max-de 12] [--every 6]

--hue is in degrees (0-360); LO > HI wraps through 0 (red: --hue 340 20). Default is orange (the orange-flesh /
sunset example). A frame counts as filled when the share is >= --fill and the worst cell is <= --max-de (the same
4x8 Lab grid and threshold as the occlusion cover check, LEAK_MAX 12). Prints every --every-th frame and the filled
runs; writes all frames to OUT.json. Use it for both sides of a colour match: A's last filled frame and B's first ones.
It cannot see a dissolve between two pictures of the same colour; look at the filled seconds frame by frame.
"""
from __future__ import annotations

import argparse
import json

import cv2
import numpy as np


def lab_of(bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(bgr.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(float)
    return np.stack([lab[:, 0] * 100 / 255, lab[:, 1] - 128, lab[:, 2] - 128], 1)


def in_hue(h: np.ndarray, lo_deg: float, hi_deg: float) -> np.ndarray:
    hd = h.astype(np.float32) * 2  # OpenCV hue units are degrees / 2
    return (hd >= lo_deg) & (hd <= hi_deg) if lo_deg <= hi_deg else (hd >= lo_deg) | (hd <= hi_deg)


def fill_stats(bgr: np.ndarray, hue: tuple[float, float] = (8, 50), smin: int = 90, vmin: int = 60,
               rows: int = 4, cols: int = 8) -> dict:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    share = float((in_hue(hsv[..., 0], *hue) & (hsv[..., 1] >= smin) & (hsv[..., 2] >= vmin)).mean())
    med = np.median(bgr.reshape(-1, 3), 0)
    lab = lab_of(med[None])[0]
    mh = cv2.cvtColor(med.reshape(1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2HSV)[0, 0]
    h, w = bgr.shape[:2]
    worst = 0.0
    for r in range(rows):
        for c in range(cols):
            cell = bgr[r * h // rows:(r + 1) * h // rows, c * w // cols:(c + 1) * w // cols]
            worst = max(worst, float(np.linalg.norm(lab_of(np.median(cell.reshape(-1, 3), 0)[None])[0] - lab)))
    return {"share": round(share, 3), "hue_deg": int(mh[0]) * 2, "L": round(float(lab[0]), 1),
            "a": round(float(lab[1]), 1), "b": round(float(lab[2]), 1), "worst_cell_dE": round(worst, 1)}


def runs(idx: list[int]) -> list[list[int]]:
    out: list[list[int]] = []
    for i in idx:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("out")
    ap.add_argument("--hue", type=float, nargs=2, default=[8, 50])
    ap.add_argument("--smin", type=int, default=90)
    ap.add_argument("--vmin", type=int, default=60)
    ap.add_argument("--fill", type=float, default=0.97)
    ap.add_argument("--max-de", type=float, default=12.0)
    ap.add_argument("--every", type=int, default=6)
    a = ap.parse_args()
    cap = cv2.VideoCapture(a.clip)
    res, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        d = {"i": i, **fill_stats(f, tuple(a.hue), a.smin, a.vmin)}
        d["filled"] = d["share"] >= a.fill and d["worst_cell_dE"] <= a.max_de
        res.append(d)
        if i % a.every == 0:
            print(json.dumps(d))
        i += 1
    filled = runs([d["i"] for d in res if d["filled"]])
    with open(a.out, "w") as fh:
        json.dump({"clip": a.clip, "hue": a.hue, "fill": a.fill, "max_de": a.max_de, "filled_runs": filled,
                   "frames": res}, fh, indent=0)
    print("filled runs (frames):", filled or "none")


if __name__ == "__main__":
    main()

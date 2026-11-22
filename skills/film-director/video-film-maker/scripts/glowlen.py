#!/usr/bin/env python3
"""How long a glow (bloom / flash) is actually visible.

    python3 glowlen.py GLOW.mp4 REF.mp4 F0 F1 [--thr 0.03]

GLOW.mp4 is the edit with the glow; REF.mp4 is the same edit without it (same plan with the bloom replaced by a
dissolve of the same overlap). Prints the per-frame mean-luma lift of GLOW over REF between frames F0 and F1 and the
frames where it exceeds --thr: that run is how long the eye sees the glow. A glow that lands on a dark picture
reads shorter than the same glow on a bright one, which is why the bloom back into a dark scene is made longer.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

FPS = 30


def lumas(path: str | Path) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(float(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).mean()) / 255)
    return np.array(out)


def glow_length(glow: str | Path, ref: str | Path, f0: int, f1: int, thr: float = 0.03) -> dict:
    d = lumas(glow)[f0:f1 + 1] - lumas(ref)[f0:f1 + 1]
    vis = [f0 + i for i, v in enumerate(d) if v > thr]
    return {"frames": len(vis), "seconds": round(len(vis) / FPS, 3), "first": vis[0] if vis else None,
            "last": vis[-1] if vis else None, "peak_lift": round(float(d.max()), 3) if len(d) else 0.0,
            "lift": [round(float(v), 3) for v in d]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("glow")
    ap.add_argument("ref")
    ap.add_argument("f0", type=int)
    ap.add_argument("f1", type=int)
    ap.add_argument("--thr", type=float, default=0.03)
    a = ap.parse_args()
    r = glow_length(a.glow, a.ref, a.f0, a.f1, a.thr)
    print(f"frames {a.f0}-{a.f1}: visible (lift>{a.thr}) {r['frames']} frames = {r['seconds']:.2f} s, "
          f"from {r['first']} to {r['last']}; peak lift {r['peak_lift']:.2f}")
    print("  lift:", " ".join(f"{v:.2f}" for v in r["lift"]))


if __name__ == "__main__":
    main()

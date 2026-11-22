#!/usr/bin/env python3
"""Spectral peaks per step: is there music in this clip?

    python3 peaks.py CLIP [--step 0.5] [--n 4]

Per step: RMS dBFS and the strongest spectral peaks (Hz) between 60 and 5000 Hz with their level above the median
bin (dB). Steady peaks = hum or drone; peaks that hop between notes from step to step = music. Wan adds music even
when the prompt says "no music", so check every clip that will be heard.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np

SR, WIN = 44100, 8192


def peaks(clip: str | Path, step: float = 0.5, n: int = 4) -> list[dict]:
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(clip), "-ac", "1", "-ar", str(SR),
                                      "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
    f = np.fft.rfftfreq(WIN, 1 / SR)
    sel = (f >= 60) & (f <= 5000)
    idx = np.where(sel)[0]
    rows, t = [], 0.0
    while t + WIN / SR <= len(x) / SR:
        seg = x[int(t * SR): int(t * SR) + WIN].astype(np.float64)
        pd = 10 * np.log10(np.abs(np.fft.rfft(seg * np.hanning(WIN))) ** 2 + 1e-12)
        med = np.median(pd[sel])
        cand = sorted((i for i in idx[1:-1] if pd[i] > pd[i - 1] and pd[i] >= pd[i + 1]), key=lambda i: -pd[i])
        picked: list[int] = []
        for i in cand:
            if all(abs(f[i] - f[j]) > 25 for j in picked):
                picked.append(i)
            if len(picked) == n:
                break
        rows.append({"t": round(t, 3), "rms_db": round(float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)), 1),
                     "peaks": [(round(float(f[i])), round(float(pd[i] - med))) for i in sorted(picked)]})
        t += step
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--step", type=float, default=0.5)
    ap.add_argument("--n", type=int, default=4)
    a = ap.parse_args()
    for r in peaks(a.clip, a.step, a.n):
        print(f"{r['t']:5.2f} {r['rms_db']:6.1f}  " + "  ".join(f"{hz:6.0f}Hz+{db:4.0f}" for hz, db in r["peaks"]))


if __name__ == "__main__":
    main()

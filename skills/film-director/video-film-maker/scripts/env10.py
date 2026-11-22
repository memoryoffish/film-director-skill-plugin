#!/usr/bin/env python3
"""Fine loudness envelope: RMS dBFS per short step (default 20 ms) between two times, mono 44.1 kHz.

    python3 env10.py CLIP T0 T1 [--step-ms 20]

Use it to find where a sound actually starts (Wan's sound often starts 0.3-0.6 s later than the prompt says) and to
check a seam for a dip: around a cut the level should stay within a few dB of the context.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np

SR = 44100


def envelope(clip: str | Path, t0: float, t1: float, step_ms: float = 20.0) -> list[tuple[float, float]]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(clip), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    step = step_ms / 1000
    n = int(SR * step)
    out, k = [], 0
    while t0 + k * step < t1 - 1e-9:
        t = t0 + k * step
        s = x[int(round(t * SR)): int(round(t * SR)) + n]
        rms = float(np.sqrt(np.mean(s ** 2))) if len(s) else 0.0
        out.append((round(t, 3), round(20 * np.log10(rms + 1e-9), 1)))
        k += 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("t0", type=float)
    ap.add_argument("t1", type=float)
    ap.add_argument("--step-ms", type=float, default=20.0)
    a = ap.parse_args()
    env = envelope(a.clip, a.t0, a.t1, a.step_ms)
    print(Path(a.clip).name, " ".join(f"{t:.2f}:{db:.0f}" for t, db in env))


if __name__ == "__main__":
    main()

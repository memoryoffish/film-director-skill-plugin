#!/usr/bin/env python3
"""Where the sound is in a clip.

    python3 audio_probe.py CLIP [--step 0.25] [--band LO HI]

ffmpeg volumedetect (whole clip), astats RMS per step (full band and, with --band, band-limited), and a numpy
spectrum per step: the dominant frequency in 200-8000 Hz and how tonal it is (peak bin over median bin, dB; a
whistle or horn is far above broadband noise). Prints a table and writes CLIP.audio.json.
"Tonal" alone does not tell music from noise: steady rain measured 29-37 dB here, a solo piano 73-81. To check for
music look at peaks.py (peaks that hop between notes) or a spectrogram (stacked horizontal lines).
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np


def volumedetect(clip):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(clip), "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    mean = re.search(r"mean_volume: (-?[0-9.]+)", err)
    mx = re.search(r"max_volume: (-?[0-9.]+)", err)
    return (float(mean.group(1)) if mean else None, float(mx.group(1)) if mx else None)


def astats_rms(clip, step, pre=""):
    n = int(round(44100 * step))
    graph = (f"{pre}aresample=44100,asetnsamples=n={n}:p=0,astats=metadata=1:reset=1,"
             f"ametadata=print:key=lavfi.astats.Overall.RMS_level:file=/dev/stdout")
    out = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(clip), "-af", graph, "-f", "null", "-"],
                         capture_output=True, text=True).stdout
    t = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", out)]
    v = [max(-120.0, float(x)) if "inf" not in x else -120.0 for x in re.findall(r"RMS_level=(-?[0-9.inf]+)", out)]
    return list(zip(t, v))


def spectrum_rows(clip, full, step, band=None):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(clip), "-ac", "1", "-ar", "44100",
                          "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    sr, w = 44100, 4096
    hop = int(sr * step)
    f = np.fft.rfftfreq(w, 1 / sr)
    sel = (f >= 200) & (f <= 8000)
    rows = []
    for i, (t, r) in enumerate(full):
        c = int(t * sr + hop / 2)
        seg = x[max(0, c - w // 2): c + w // 2]
        if len(seg) < w:
            seg = np.pad(seg, (0, w - len(seg)))
        P = np.abs(np.fft.rfft(seg * np.hanning(w))) ** 2 + 1e-12
        pk = int(np.argmax(np.where(sel, P, 0)))
        rows.append({"t": round(t, 3), "rms_db": round(r, 1),
                     "band_db": round(band[i][1], 1) if band and i < len(band) else None,
                     "peak_hz": int(round(float(f[pk]))),
                     "tonal_db": round(float(10 * np.log10(P[pk] / np.median(P[sel]))), 1)})
    return rows


def probe(clip, step=0.25, band=None):
    clip = Path(clip)
    mean, mx = volumedetect(clip)
    full = astats_rms(clip, step)
    bnd = astats_rms(clip, step, f"highpass=f={band[0]},lowpass=f={band[1]},") if band else None
    return {"clip": str(clip), "mean_volume_db": mean, "max_volume_db": mx, "step_s": step, "band": band,
            "rows": spectrum_rows(clip, full, step, bnd)}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("clip")
    p.add_argument("--step", type=float, default=0.25)
    p.add_argument("--band", type=float, nargs=2)
    a = p.parse_args()
    clip = Path(a.clip)
    rep = probe(clip, a.step, a.band)
    clip.with_suffix(".audio.json").write_text(json.dumps(rep, indent=1))
    print(f"{clip.name}: volumedetect mean {rep['mean_volume_db']} dB, max {rep['max_volume_db']} dB")
    print("    t    rms   band  peakHz tonal")
    for r in rep["rows"]:
        b = "" if r["band_db"] is None else f"{r['band_db']:6.1f}"
        print(f"{r['t']:5.2f} {r['rms_db']:6.1f} {b:>6} {r['peak_hz']:6d} {r['tonal_db']:5.1f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""camera-move transition effects applied on a joined clip, around one cut.

    camfx.py whip  IN.mp4 OUT.mp4 --cut N [--n 6] [--peak 280]
        horizontal box blur, length rising over the n frames before the cut and falling over the n frames from it
    camfx.py zoom  IN.mp4 OUT.mp4 --cut N [--n 6] [--total 3.0] [--shutter 2.0] [--ca X,Y] [--cb X,Y]
        digital zoom-in across the cut (HusseinsDrama's Premiere recipe: scale up into the cut, the next shot
        arrives from smaller with mirrored edges and settles at 100%), plus radial zoom blur that peaks at the cut
    camfx.py sheet IN.mp4 OUT.png --cut N [--before 9] [--after 9] [--cols 6]
    camfx.py center CLIP.mp4 FRAME [--box X0,Y0,X1,Y1]
        centre of the brightest region of one frame, as fractions of width/height; --box (fractions) limits the
        search, e.g. to the tunnel exit when lamps on the tunnel ceiling are brighter than the exit
    camfx.py label IN.mp4 OUT.mp4 --cut N --a TEXT --b TEXT
        burn occut join's call labels (top-left text, coloured bottom strip) after the effects, so the zoom and
        blur do not distort them; frames before --cut get --a, the rest get --b

--cut is the index (in IN.mp4) of the first frame after the cut. Video is re-encoded (x264 crf 16), audio copied.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import occut  # noqa: E402


def bell(n: int) -> list[float]:
    """Speed profile over the 2n frames around the cut: 1 - cos, 0 at the ends, ~1 at the cut."""
    return [(1 - math.cos(2 * math.pi * (j + 0.5) / (2 * n))) / 2 for j in range(2 * n)]


def whip_frame(rgb: np.ndarray, length: int) -> np.ndarray:
    length = max(1, int(round(length)) | 1)
    if length == 1:
        return rgb
    k = np.full((1, length), 1.0 / length, np.float32)
    return cv2.filter2D(rgb, -1, k, borderType=cv2.BORDER_REFLECT)


def zoom_frame(rgb: np.ndarray, scale: float, dlog: float, center: tuple[float, float], shutter: float,
               samples: int = 16) -> np.ndarray:
    """Scale about `center` (pixels), averaging scales spread over the frame's share of the zoom (radial blur).
    Edges uncovered when scale < 1 are filled by mirroring, like Premiere's Replicate + Mirror."""
    h, w = rgb.shape[:2]
    cx, cy = center
    acc = np.zeros(rgb.shape, np.float32)
    ts = np.linspace(-0.5, 0.5, samples) if dlog * shutter > 1e-4 else [0.0]
    for t in ts:
        s = scale * math.exp(t * dlog * shutter)
        m = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]])
        acc += cv2.warpAffine(rgb, m, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return np.clip(acc / len(ts) + 0.5, 0, 255).astype(np.uint8)


def process(src: Path, dst: Path, fx: dict[int, callable]) -> None:
    info = occut.video_info(src)
    w, h, fps = info["w"], info["h"], info["fps"]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-nostdin", "-i", str(src), "-f", "rawvideo", "-pix_fmt",
                            "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                            f"{w}x{h}", "-r", f"{fps}", "-i", "-", "-i", str(src), "-map", "0:v", "-map", "1:a?",
                            "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy",
                            "-movflags", "+faststart", str(dst)], stdin=subprocess.PIPE)
    size, i = w * h * 3, 0
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        f = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        if i in fx:
            f = fx[i](f)
        enc.stdin.write(np.ascontiguousarray(f).tobytes())
        i += 1
    enc.stdin.close()
    if dec.wait() or enc.wait():
        raise RuntimeError("ffmpeg failed")


def cmd_whip(a) -> dict:
    prof = bell(a.n)
    lengths = {a.cut - a.n + j: a.peak * p for j, p in enumerate(prof)}
    process(Path(a.src), Path(a.dst), {i: (lambda f, L=L: whip_frame(f, L)) for i, L in lengths.items()})
    return {"blur_px": {i: int(round(L)) | 1 for i, L in lengths.items()}}


def cmd_zoom(a) -> dict:
    info = occut.video_info(Path(a.src))
    w, h = info["w"], info["h"]
    ca = [float(v) for v in a.ca.split(",")]
    cb = [float(v) for v in a.cb.split(",")]
    S, n = math.log(a.total), a.n
    plan, fx = {}, {}
    for j in range(2 * n):
        u = (j + 0.5) / (2 * n)
        s_log = S * (u - math.sin(2 * math.pi * u) / (2 * math.pi))
        dlog = S * (1 - math.cos(2 * math.pi * u)) / (2 * n)
        before = j < n
        scale = math.exp(s_log if before else s_log - S)
        c = (ca[0] * w, ca[1] * h) if before else (cb[0] * w, cb[1] * h)
        i = a.cut - n + j
        plan[i] = {"scale": round(scale, 3), "blur_dlog": round(dlog * a.shutter, 3)}
        fx[i] = lambda f, s=scale, d=dlog, c=c: zoom_frame(f, s, d, c, a.shutter)
    process(Path(a.src), Path(a.dst), fx)
    return {"frames": plan}


def cmd_sheet(a) -> dict:
    frames, fps = occut.decode(Path(a.src), 480)
    idx = list(range(max(0, a.cut - a.before), min(len(frames), a.cut + a.after)))
    tiles = [(frames[i], f"{'B' if i >= a.cut else 'A'} f{i} {i / fps:.2f}s") for i in idx]
    if not a.bottom:
        occut.sheet(tiles, Path(a.dst), cols=a.cols, width=320)
    else:  # frame labels at the bottom-left, clear of call labels burned into the top-left corner
        rows = []
        for r in range(0, len(tiles), a.cols):
            row = []
            for rgb, label in tiles[r:r + a.cols]:
                t = np.ascontiguousarray(cv2.resize(rgb, (320, int(320 * rgb.shape[0] / rgb.shape[1])),
                                                    interpolation=cv2.INTER_AREA)[..., ::-1])
                y = t.shape[0] - 12
                cv2.putText(t, label, (6, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA)
                cv2.putText(t, label, (6, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)
                row.append(t)
            row += [np.zeros_like(row[0])] * (a.cols - len(row))
            rows.append(np.hstack(row))
        cv2.imwrite(str(a.dst), np.vstack(rows))
    return {"frames": idx, "cut": a.cut, "cut_s": round(a.cut / fps, 3)}


def cmd_label(a) -> dict:
    dst = Path(a.dst)
    parts = []
    for k, (text, cond) in enumerate(((a.a, f"lt(n,{a.cut})"), (a.b, f"gte(n,{a.cut})"))):
        txt = dst.with_name(f".{dst.stem}_label{k}.txt")
        txt.write_text(text, encoding="utf-8")
        parts.append(f"drawtext=fontfile={occut.LABEL_FONT}:textfile={txt}:x=h/40:y=h/40:fontsize=h/28:"
                     f"fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=10:enable='{cond}',"
                     f"drawbox=x=0:y=ih-ih/90:w=iw:h=ih/90:color={occut.LABEL_COLORS[k]}@0.95:t=fill:"
                     f"enable='{cond}'")
    subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", a.src, "-vf", ",".join(parts),
                    "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)
    return {"cut": a.cut, "a": a.a, "b": a.b}


def bright_center(rgb: np.ndarray, box: tuple[float, float, float, float] | None = None) -> dict:
    """Centre of the brightest 1% of a (blurred) frame, as fractions of width/height; box = (x0, y0, x1, y1) in
    fractions restricts the search."""
    g = cv2.GaussianBlur(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), (0, 0), 6).astype(np.float32)
    h, w = g.shape
    x0, y0, x1, y1 = box or (0.0, 0.0, 1.0, 1.0)
    c0, r0 = int(round(x0 * w)), int(round(y0 * h))
    sub = g[r0:max(r0 + 1, int(round(y1 * h))), c0:max(c0 + 1, int(round(x1 * w)))]
    level = float(np.percentile(sub, 99))
    ys, xs = np.nonzero(sub >= level)
    return {"x": round(float(xs.mean() + c0) / w, 3), "y": round(float(ys.mean() + r0) / h, 3), "level": level,
            "box": [x0, y0, x1, y1]}


def cmd_center(a) -> dict:
    frames, _ = occut.decode(Path(a.src), 480)
    box = tuple(float(v) for v in a.box.split(",")) if a.box else None
    return bright_center(frames[a.frame], box)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("whip", "zoom", "sheet"):
        s = sub.add_parser(name)
        s.add_argument("src"); s.add_argument("dst"); s.add_argument("--cut", type=int, required=True)
        if name in ("whip", "zoom"):
            s.add_argument("--n", type=int, default=6)
        if name == "whip":
            s.add_argument("--peak", type=float, default=280)
        if name == "zoom":
            s.add_argument("--total", type=float, default=3.0)
            s.add_argument("--shutter", type=float, default=2.0)
            s.add_argument("--ca", default="0.5,0.5"); s.add_argument("--cb", default="0.5,0.5")
        if name == "sheet":
            s.add_argument("--before", type=int, default=9); s.add_argument("--after", type=int, default=9)
            s.add_argument("--cols", type=int, default=6)
            s.add_argument("--bottom", action="store_true", help="frame labels at the bottom-left")
    c = sub.add_parser("center"); c.add_argument("src"); c.add_argument("frame", type=int)
    c.add_argument("--box", help="search only inside X0,Y0,X1,Y1 (fractions of width/height)")
    lb = sub.add_parser("label"); lb.add_argument("src"); lb.add_argument("dst")
    lb.add_argument("--cut", type=int, required=True); lb.add_argument("--a", required=True); lb.add_argument("--b", required=True)
    a = p.parse_args()
    out = {"whip": cmd_whip, "zoom": cmd_zoom, "sheet": cmd_sheet, "center": cmd_center,
           "label": cmd_label}[a.cmd](a)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

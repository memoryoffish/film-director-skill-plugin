"""Check and cut generated clips: where the cuts really are, frame-exact pieces with clean audio edges, joining, frames to look at.

    from cut import dur, fps_of, frames, cuts, split_unit, piece, tail, join, sheet, strip, trio, onsets
    python3 cut.py cuts CLIP [0.12]               # times of the hard cuts inside a clip (0.2 by default; 0.12 for two dark shots)
    python3 cut.py sheet OUT.jpg "0.5,2,3.4" CLIP [CLIP …]      # one row per clip, one frame per time; "5" = five frames spread evenly
    python3 cut.py strip OUT.jpg CLIP [STEP] [T0] [T1]          # frames every STEP s (0.1) with their time, to find the frame where things touch
    python3 cut.py pairs OUT.jpg A1 B1 [A2 B2 …]                # images side by side, two pairs per row (white model | keyframe, or | a frame)
    python3 cut.py trio OUT.jpg WM KEY CLIP [WM KEY CLIP …]     # one row per shot: white model | keyframe | first, middle, last frame of the clip
    python3 cut.py frame CLIP 3.6 OUT.png                       # one frame of a clip
    python3 cut.py onsets CLIP                                  # times of the sharpest sounds (hits, bangs), to line them up with the picture
Pieces keep the source's frame rate and are cut in whole frames; join() lays picture and sound separately, so a film of many
pieces is exactly as long as its pieces (joining with the sound inside added a dozen milliseconds at every seam).
"""
from __future__ import annotations

import array, subprocess, sys, tempfile
from fractions import Fraction
from pathlib import Path

AUDIO = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def _passthrough() -> list:
    """Keep every frame as it is: -fps_mode on ffmpeg 5.1 and later, -vsync on older ones (ffmpeg 4.4 has no -fps_mode)."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-h", "long"], capture_output=True, text=True).stdout
    return ["-fps_mode", "passthrough"] if "-fps_mode" in out else ["-vsync", "passthrough"]


def enc(fps) -> list:
    return ["-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(fps), *AUDIO, "-movflags", "+faststart"]


def _probe(p, entries, stream="v:0") -> str:
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", entries, "-of", "csv=p=0", str(p)],
                          capture_output=True, text=True).stdout.strip()


def dur(p) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def fps_of(p) -> Fraction:
    """Frame rate of the clip's picture (Wan 3.0 gives 30, Seedance 24)."""
    return Fraction(_probe(p, "stream=r_frame_rate").split(",")[0])


def frames(p) -> int:
    """Number of picture frames in the clip."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return int(out.strip().split(",")[0])


def has_audio(p) -> bool:
    return bool(_probe(p, "stream=index", "a"))


def cuts(path, lo=0.2) -> list[float]:
    """Times of the hard cuts inside a clip (ffmpeg scene detection). A cut between two views of the same place scores as low as
    0.22, so the default is 0.2; between two dark shots use 0.12. A slow drift or a morph does not show up here: look at a sheet too."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", f"select='gt(scene,{lo})',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [float(l.split("pts_time:")[1].split()[0]) for l in r.stderr.splitlines() if "pts_time:" in l]


def piece(src, t0, length, dst, fps=None):
    """Cut whole frames: from the frame at t0, round(length * fps) frames (fps = the source's). The sound is cut to exactly the
    same length (padded with silence if the source runs out) with a 30 ms fade at both ends, so joined pieces do not click."""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    fps = Fraction(fps) if fps else fps_of(src)
    f0, n = round(t0 * fps), round(length * fps)
    L = float(n / fps)
    vf = f"trim=start_frame={f0}:end_frame={f0 + n},setpts=PTS-STARTPTS,scale=1280:720"
    af = (f"atrim=start={float(f0 / fps):.6f},asetpts=PTS-STARTPTS,apad,atrim=end={L:.6f},"
          f"afade=t=in:st=0:d=0.03,afade=t=out:st={max(0.0, L - 0.03):.6f}:d=0.03")
    ins = ["-i", str(src)] + ([] if has_audio(src) else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"])
    a = "0:a" if has_audio(src) else "1:a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f"[0:v]{vf}[v];[{a}]{af}[a]", "-map", "[v]", "-map", "[a]",
                    *enc(fps), str(dst)], check=True)
    return dst


def tail(src, length, dst, fps=None):
    """The last `length` seconds of a clip, counted in whole frames from its end (a first + last frame clip that should land on
    its last frame). Mind that some clips jump in their very last frames: look before you take the end."""
    fps = Fraction(fps) if fps else fps_of(src)
    n = round(length * fps)
    return piece(src, float((frames(src) - n) / fps), float(n / fps), dst, fps)


def join(parts, dst):
    """Join pieces end to end: the pictures are copied as they are, the sounds are cut to the length of their own picture and
    laid one after another, then put together once. Pieces must share size, codec and frame rate (piece() makes them so)."""
    dst = Path(dst)
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        vl, al = d / "v.txt", d / "a.txt"
        vlines, alines = [], []
        for i, p in enumerate(parts):
            p = Path(p).resolve()
            L = float(frames(p) / fps_of(p))
            v, a = d / f"v{i}.mp4", d / f"a{i}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-map", "0:v:0", "-c", "copy", str(v)], check=True)
            if has_audio(p):
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-map", "0:a:0", "-af", f"apad,atrim=end={L:.6f}",
                                "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(a)], check=True)
            else:
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{L:.6f}",
                                "-c:a", "pcm_s16le", str(a)], check=True)
            vlines.append(f"file '{v}'\n")
            alines.append(f"file '{a}'\n")
        vl.write_text("".join(vlines))
        al.write_text("".join(alines))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(vl), "-f", "concat", "-safe", "0", "-i", str(al),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", *AUDIO, "-movflags", "+faststart", str(dst)], check=True)
    return dst


def split_unit(src, lengths, tol=0.9, lo=0.2):
    """A multi-shot clip against its schedule. lengths = shot lengths in seconds. Returns {"wanted", "found", "extra", "edges"}:
    wanted cut times, the detected cut nearest to each (None = missing), cuts nobody asked for, and the shot edges to cut at.
    lo = the cut-detection threshold (0.12 for dark shots)."""
    found = cuts(src, lo)
    wanted, t = [], 0.0
    for L in lengths[:-1]:
        t += L
        wanted.append(round(t, 3))
    near = [min((f for f in found if abs(f - w) <= tol), key=lambda f: abs(f - w), default=None) for w in wanted]
    extra = [f for f in found if f not in near and f < sum(lengths) - 0.1]
    edges = [0.0, *[n if n is not None else w for n, w in zip(near, wanted)], min(dur(src), sum(lengths))]
    return {"wanted": wanted, "found": near, "extra": extra, "edges": edges}


def _font(size):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/STHeiti Medium.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def _grab(clip, indices, w, d):
    """Frames number `indices` (0 = first) of a clip, as Pillow images w wide: decodes the clip once, so it is exact and quick."""
    from PIL import Image
    d = Path(d)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vf", f"scale={w}:-2", *_passthrough(), "-start_number", "0",
                    str(d / "f_%05d.jpg")], check=True)
    out = []
    for i in indices:
        f = d / f"f_{i:05d}.jpg"
        out.append(Image.open(f).convert("RGB") if f.exists() else None)
    for f in d.glob("f_*.jpg"):
        f.unlink()
    return out


def sheet(out, times, clips, w=320):
    from PIL import Image
    h = w * 9 // 16
    rows = []
    with tempfile.TemporaryDirectory() as d:
        for r, c in enumerate(clips):
            ts = times if isinstance(times, (list, tuple)) else [dur(c) * (i + 0.5) / times for i in range(times)]
            row = []
            for k, t in enumerate(ts):
                f = Path(d) / f"{r}_{k}.jpg"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(c), "-frames:v", "1", "-vf", f"scale={w}:{h}", str(f)])
                row.append(Image.open(f).copy() if f.exists() else Image.new("RGB", (w, h)))
            rows.append(row)
    img = Image.new("RGB", (w * max(len(r) for r in rows), h * len(rows)))
    for r, row in enumerate(rows):
        for k, im in enumerate(row):
            img.paste(im, (k * w, r * h))
    img.save(out, quality=88)
    return out


def strip(out, clip, step=0.1, t0=0.0, t1=None, w=256, cols=10):
    """Frames every `step` seconds from t0 to t1 (default: the end; the very last frame is always included), each labelled with
    its time and frame number. For finding the frame where a fist meets the glass, where a move has landed, or a jump at the end."""
    from PIL import Image, ImageDraw
    fps, n = fps_of(clip), frames(clip)
    last = n - 1 if t1 is None else min(n - 1, round(t1 * fps))
    idx, t = [], t0
    while round(t * fps) <= last:
        idx.append(round(t * fps))
        t += step
    if idx[-1] != last:
        idx.append(last)
    with tempfile.TemporaryDirectory() as d:
        ims = _grab(clip, idx, w, d)
    h = ims[0].height
    font = _font(max(12, w // 16))
    img = Image.new("RGB", (w * min(cols, len(idx)), (h + 0) * ((len(idx) + cols - 1) // cols)), (0, 0, 0))
    dr = ImageDraw.Draw(img)
    for k, (i, im) in enumerate(zip(idx, ims)):
        x, y = (k % cols) * w, (k // cols) * h
        if im:
            img.paste(im, (x, y))
        label = f"{float(i / fps):.2f}s · f{i}" + (" · 末帧" if i == n - 1 else "")
        dr.rectangle([x, y, x + w // 2 + 20, y + w // 14 + 6], fill=(0, 0, 0))
        dr.text((x + 4, y + 2), label, fill=(255, 255, 0), font=font)
    img.save(out, quality=88)
    return out


def frame(clip, t, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{float(t):.2f}", "-i", str(clip), "-frames:v", "1", str(out)], check=True)
    return out


def pairs(out, items, w=480):
    """items = [(a, b), …] image files; each pair side by side, two pairs per row."""
    from PIL import Image
    h = w * 9 // 16
    img = Image.new("RGB", (w * 4, h * ((len(items) + 1) // 2)))
    for i, pair in enumerate(items):
        for j, f in enumerate(pair):
            if Path(f).exists():
                img.paste(Image.open(f).convert("RGB").resize((w, h)), ((i % 2) * 2 * w + j * w, (i // 2) * h))
    img.save(out, quality=88)
    return out


def trio(out, rows, w=360):
    """One row per shot: the white-model still | the keyframe | the clip's first, middle and last-but-two frames.
    rows = [(white model png, keyframe png or "-", clip), …]. A wrong place is then easy to pin on one step: white model,
    keyframe, or video."""
    from PIL import Image, ImageDraw
    h = w * 9 // 16
    head = 30
    img = Image.new("RGB", (w * 5, head + h * len(rows)), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    font = _font(18)
    for k, t in enumerate(("白模", "关键帧", "成片 头", "成片 中", "成片 尾")):
        dr.text((k * w + 6, 5), t, fill=(0, 0, 0), font=font)
    with tempfile.TemporaryDirectory() as d:
        for r, (wm, key, clip) in enumerate(rows):
            y = head + r * h
            for k, f in enumerate((wm, key)):
                if f and f != "-" and Path(f).exists():
                    img.paste(Image.open(f).convert("RGB").resize((w, h)), (k * w, y))
            n = frames(clip)
            for k, im in enumerate(_grab(clip, [0, n // 2, max(0, n - 3)], w, d)):
                if im:
                    img.paste(im.resize((w, h)), ((2 + k) * w, y))
            dr.text((6, y + 4), Path(clip).stem, fill=(255, 255, 0), font=font)
    img.save(out, quality=88)
    return out


def _onsets(x, rate, top=8, win=0.01):
    """x = mono samples. Times (s) where the loudness jumps most sharply, with the jump in dB: the hits and bangs of a clip."""
    import math
    n = max(1, int(rate * win))
    db = []
    for i in range(0, len(x) - n + 1, n):
        seg = x[i:i + n]
        db.append(10 * math.log10(sum(v * v for v in seg) / n + 1e-9))
    rise = [db[i] - max(db[max(0, i - 8):i]) if i else 0.0 for i in range(len(db))]
    peaks = [i for i in range(1, len(db) - 1) if rise[i] > 6 and rise[i] >= rise[i - 1] and rise[i] >= rise[i + 1]]
    best = sorted(sorted(peaks, key=lambda i: -rise[i])[:top])
    return [(round(i * win, 2), round(rise[i], 1)) for i in best]


def onsets(clip, top=8):
    """The sharpest sounds in a clip: [(time in s, how many dB louder than the 80 ms before)]. Put a hit's time next to the frame
    where the two things touch (strip()); if the sound is late, shift it in the edit."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = array.array("h", raw)
    return _onsets([v / 32768 for v in x], 16000, top)


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == "pairs":
        print(pairs(a[0], list(zip(a[1::2], a[2::2]))))
    elif cmd == "trio":
        print(trio(a[0], [tuple(a[i:i + 3]) for i in range(1, len(a), 3)]))
    elif cmd == "frame":
        print(frame(a[0], a[1], a[2]))
    elif cmd == "cuts":
        print(" ".join(f"{t:.2f}" for t in cuts(a[0], float(a[1]) if len(a) > 1 else 0.2)))
    elif cmd == "strip":
        print(strip(a[0], a[1], *(float(v) for v in a[2:5])))
    elif cmd == "onsets":
        for t, rise in onsets(a[0]):
            print(f"{t:.2f} s  +{rise} dB")
    elif cmd == "sheet":
        t = a[1]
        sheet(a[0], [float(x) for x in t.split(",")] if "," in t or "." in t else int(t), a[2:])
        print(a[0])

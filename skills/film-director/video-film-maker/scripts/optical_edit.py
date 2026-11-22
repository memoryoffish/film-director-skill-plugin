#!/usr/bin/env python3
"""Frame-exact editor for optical transitions: cut / flash (white) / bloom (soft glow) / dissolve / fade_black.

    python3 optical_edit.py PLAN.json OUT.mp4

PLAN = {"segments": [{"clip": abs.mp4, "start": f0, "end": f1, "xform": {"s":1,"dx":0,"dy":0}?,
                      "label": "Wan 调用 #1 · ..."?, "call": 1?}, ...],
        "transitions": [{"type": "cut", "audio_xfade": 0.3?}
                        | {"type": "flash", "rise": 2, "white": 2, "fall": 3, "sfx": true}
                        | {"type": "bloom", "rise": 6, "overlap": 4, "fall": 9, "level": 0.5, "sfx": true, "audio_xfade": 0.6?}
                        | {"type": "dissolve", "frames": 30} | {"type": "fade_black", "out": 15, "black": 6, "in": 15}],
        "sfx": [{"wav": abs.wav, "at": out_frame, "gain_db": 0}]?}
start/end are inclusive source frame numbers; every clip needs an audio stream; the output size is the first clip's.
"label" is burned top-left and "call" (Wan call number) colours the strip along the bottom, like occut.py join.
Writes OUT.mp4 (H.264 crf 16 + AAC) and OUT.json (where each transition lands: glow range, peak, first frame of the
next segment). See transitions/optical.md for the bloom settings used there.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import occut  # noqa: E402

FPS, SR = 30, 44100
W, H = 1280, 720  # replaced by the first clip's size in main()


def read_frames(path, f0, f1):
    cap = cv2.VideoCapture(str(path)); cap.set(cv2.CAP_PROP_POS_FRAMES, f0); out = []
    for _ in range(f0, f1 + 1):
        ok, f = cap.read()
        if not ok: raise SystemExit(f"{path}: frame {f0 + len(out)} missing")
        out.append(f)
    return out


def read_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def xform(frames, x):
    """x = {"s","dx","dy"} for every frame, or a list of [s, dx, dy] per frame (frames past the list stay as they are)."""
    if not x: return frames
    per = x if isinstance(x, list) else [[x.get("s", 1.0), x.get("dx", 0.0), x.get("dy", 0.0)]] * len(frames)
    out = []
    for i, f in enumerate(frames):
        if i >= len(per) or per[i] == [1, 0, 0]: out.append(f); continue
        s, dx, dy = per[i]
        m = np.float32([[s, 0, (1 - s) * W / 2 + dx], [0, s, (1 - s) * H / 2 + dy]])  # scale about centre, then shift
        out.append(cv2.warpAffine(f, m, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT))
    return out


def to_white(f, a):
    # exposure-style flash: brighten first, then wash to white
    x = f.astype(np.float32) / 255.0
    x = np.clip(x * (1 + 2.5 * a), 0, 1)
    x = x + (1 - x) * a ** 1.5
    return (x * 255 + 0.5).astype(np.uint8)


def glow(f, a, level, warm=(0.94, 0.97, 1.0)):
    """soft flash: exposure lift + highlight bloom (wide blur) + radial haze toward warm white, never pure white.
    a = envelope 0..1; level (0..1) scales all three, so a low level keeps the picture readable at the peak."""
    if a <= 0: return f
    k = a * level
    x = f.astype(np.float32) / 255.0
    x = 1 - (1 - x) ** (1 + 1.6 * k)                                   # lift, highlights roll off
    y = x @ np.float32([0.114, 0.587, 0.299])
    hi = np.clip((y - 0.45) / 0.55, 0, 1) ** 1.5
    small = cv2.resize(x * hi[..., None], (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 6 + 14 * a)                 # 24-80 px at full size
    bloom = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
    x = 1 - (1 - x) * (1 - np.clip(1.3 * k * bloom, 0, 1))              # screen the glow on
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    w = (0.75 * k * (1 - 0.35 * np.clip(r2 / 2, 0, 1)))[..., None]      # softer toward the corners
    x = x + (np.float32(warm) - x) * w
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


def ease(u):
    return float(np.sin(np.clip(u, 0, 1) * np.pi / 2) ** 2)


def flash_sfx():
    """riser (0.33 s) into a shutter click + low hit; returns (stereo, index of the hit)."""
    rng = np.random.default_rng(3)
    n_r = int(0.33 * SR); t = np.arange(n_r) / SR
    noise = rng.standard_normal(n_r)
    hp = np.diff(noise, prepend=0)                     # airy, high-passed noise
    riser = hp * (t / t[-1]) ** 3 * 0.10
    n_t = int(0.6 * SR); tt = np.arange(n_t) / SR; tail = np.zeros(n_t)
    for off, amp in ((0.0, 0.55), (0.065, 0.35)):     # two-blade shutter "ka-chik"
        i0 = int(off * SR); k = np.arange(n_t - i0) / SR
        click = rng.standard_normal(n_t - i0) * np.exp(-k / 0.0015) + np.sin(2 * np.pi * 3100 * k) * np.exp(-k / 0.006)
        tail[i0:] += amp * click
    f = 85 * np.exp(-tt / 0.08) + 42                   # low thump, pitch falling
    tail += 0.45 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.18)
    mono = np.concatenate([riser, tail]).astype(np.float32)
    mono *= 0.5 / np.abs(mono).max()                   # peak 0.5 before gain_db
    return np.stack([mono, mono], 1), n_r


def ramp(n, up=True):
    a = (np.arange(n) + 0.5) / n
    a = np.sin(a * np.pi / 2) ** 2                      # smooth
    return (a if up else 1 - a).astype(np.float32)


LABEL_FONT, LABEL_COLORS = occut.LABEL_FONT, occut.LABEL_COLORS  # same look as occut.py join


def label_filter(segs, seg_start, n_frames, out_path):
    """drawtext + bottom strip per segment, switched on at the frame where that segment's first frame lands."""
    parts = []
    for i, s in enumerate(segs):
        if not s.get("label"): continue
        a = seg_start[i]; b = seg_start[i + 1] - 1 if i + 1 < len(segs) else n_frames - 1
        txt = Path(out_path).with_name(f".{Path(out_path).stem}_label{i}.txt"); txt.write_text(s["label"], encoding="utf-8")
        on = f"enable='between(t,{(a - 0.5) / FPS:.4f},{(b + 0.5) / FPS:.4f})'"
        col = LABEL_COLORS[(int(s.get("call", i + 1)) - 1) % len(LABEL_COLORS)]
        parts.append(f"drawtext=fontfile={LABEL_FONT}:textfile={txt}:x=h/40:y=h/40:fontsize=h/28:fontcolor=white:"
                     f"box=1:boxcolor=black@0.55:boxborderw=10:{on}")
        parts.append(f"drawbox=x=0:y=ih-ih/90:w=iw:h=ih/90:color={col}@0.95:t=fill:{on}")
    return ",".join(parts)


def main(plan_path, out_path):
    global W, H
    plan = json.loads(Path(plan_path).read_text())
    segs, trans = plan["segments"], plan.get("transitions", [])
    cap = cv2.VideoCapture(str(segs[0]["clip"]))
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    assert len(trans) == len(segs) - 1
    audio_cache = {}
    video = []            # output frames
    regions = []          # audio regions: dict(src, a, b (source seconds), at (output seconds), fin, fout (seconds))
    marks = []
    sfx = list(plan.get("sfx", []))
    prev_tail = None
    seg_start = []
    for i, s in enumerate(segs):
        fr = xform(read_frames(s["clip"], s["start"], s["end"]), s.get("xform"))
        t = trans[i - 1] if i else None
        reg = {"src": s["clip"], "a": s["start"] / FPS, "b": (s["end"] + 1) / FPS, "fin": 0.0, "fout": 0.0}
        if t is None:
            reg["at"] = 0.0; first_at = 0; video += fr
        else:
            kind = t["type"]; cut_at = len(video)
            if kind == "cut":
                reg["at"] = cut_at / FPS
                h = t.get("audio_xfade", 0.1) / 2
                prev_tail["b"] += h; prev_tail["fout"] = 2 * h
                reg["a"] -= h; reg["at"] -= h; reg["fin"] = 2 * h
                first_at = len(video); video += fr
                marks.append({"type": "cut", "frame": cut_at, "sec": round(cut_at / FPS, 3)})
            elif kind == "flash":
                rise, white, fall = t.get("rise", 2), t.get("white", 2), t.get("fall", 3)
                for k in range(rise):
                    a = (k + 1) / (rise + 1)
                    video[-rise + k] = to_white(video[-rise + k], a)
                w0 = len(video)
                video += [np.full((H, W, 3), 255, np.uint8)] * white
                for k in range(fall):
                    fr[k] = to_white(fr[k], 1 - (k + 1) / (fall + 1))
                reg["at"] = len(video) / FPS
                ext = white / FPS + 0.04
                prev_tail["b"] += ext; prev_tail["fout"] = ext + 0.06
                reg["a"] -= ext; reg["at"] -= ext; reg["fin"] = ext + 0.04
                first_at = len(video); video += fr
                if t.get("sfx", True):
                    sfx.append({"synth": "flash", "at": w0, "gain_db": t.get("sfx_db", -3)})
                marks.append({"type": "flash", "first_bright": w0 - rise, "white": [w0, w0 + white - 1],
                              "last_bright": w0 + white + fall - 1, "sec": round(w0 / FPS, 3)})
            elif kind == "dissolve":
                n = t["frames"]; st = len(video) - n
                for k in range(n):
                    a = (k + 1) / (n + 1)
                    video[st + k] = cv2.addWeighted(video[st + k], 1 - a, fr[k], a, 0)
                video += fr[n:]; first_at = st
                reg["at"] = st / FPS; reg["fin"] = n / FPS; prev_tail["fout"] = n / FPS
                marks.append({"type": "dissolve", "frames": [st, st + n - 1],
                              "sec": [round(st / FPS, 3), round((st + n) / FPS, 3)]})
            elif kind == "fade_black":
                o, bk, n = t.get("out", 15), t.get("black", 6), t.get("in", 15)
                for k in range(o):
                    g = 1 - (k + 1) / (o + 1)
                    video[-o + k] = (video[-o + k].astype(np.float32) * g + 0.5).astype(np.uint8)
                b0 = len(video)
                video += [np.zeros((H, W, 3), np.uint8)] * bk
                for k in range(n):
                    g = (k + 1) / (n + 1)
                    fr[k] = (fr[k].astype(np.float32) * g + 0.5).astype(np.uint8)
                reg["at"] = len(video) / FPS; reg["fin"] = n / FPS; prev_tail["fout"] = o / FPS
                first_at = len(video); video += fr
                marks.append({"type": "fade_black", "fade_out": [b0 - o, b0 - 1], "black": [b0, b0 + bk - 1],
                              "fade_in": [b0 + bk, b0 + bk + n - 1], "sec": round(b0 / FPS, 3)})
            elif kind == "bloom":
                rise, ov, fall, lv = t.get("rise", 6), t.get("overlap", 4), t.get("fall", 9), t.get("level", 0.55)
                st = len(video) - ov                                     # overlap: A and B cross-dissolve at the peak
                for k in range(ov):
                    wgt = (k + 1) / (ov + 1)
                    video[st + k] = cv2.addWeighted(video[st + k], 1 - wgt, fr[k], wgt, 0)
                for k in range(rise):                                    # A frames before the peak
                    idx = st - rise + k
                    video[idx] = glow(video[idx], ease((k + 1) / (rise + 1)), lv)
                for k in range(ov):                                      # peak plateau
                    video[st + k] = glow(video[st + k], 1.0, lv)
                for k in range(fall):                                    # B frames after the peak
                    fr[ov + k] = glow(fr[ov + k], ease(1 - (k + 1) / (fall + 1)), lv)
                video += fr[ov:]; first_at = st
                if "audio_xfade" in t:                                   # longer sound crossfade: A keeps sounding under B
                    xf = float(t["audio_xfade"]); ext = max(0.06, xf - ov / FPS)
                    reg["at"] = st / FPS - 0.06; reg["a"] -= 0.06; reg["fin"] = xf
                    prev_tail["b"] += ext; prev_tail["fout"] = ov / FPS + ext
                    prev_tail["fit_fade"] = True                         # if A's audio runs out, finish the fade where it ends
                else:
                    xf = ov / FPS + 0.12
                    reg["at"] = st / FPS - 0.06; reg["a"] -= 0.06; reg["fin"] = xf
                    prev_tail["b"] += 0.06; prev_tail["fout"] = xf
                mid = st + ov // 2
                if t.get("sfx", True):
                    sfx.append({"synth": "flash", "at": mid, "gain_db": t.get("sfx_db", 0)})
                marks.append({"type": "bloom", "level": lv, "glow": [st - rise, st + ov + fall - 1],
                              "peak_overlap": [st, st + ov - 1], "first_frame_of_next": st,
                              "sec": [round((st - rise) / FPS, 3), round((st + ov + fall) / FPS, 3)]})
            else:
                raise SystemExit(f"unknown transition {kind}")
        regions.append(reg); prev_tail = reg; seg_start.append(first_at)
    # ---- audio mix
    total = int(round(len(video) / FPS * SR)); mix = np.zeros((total, 2), np.float32)
    for r in regions:
        src = audio_cache.setdefault(r["src"], read_audio(r["src"]))
        a, b = int(round(r["a"] * SR)), int(round(r["b"] * SR)); at = int(round(r["at"] * SR))
        seg = np.zeros((b - a, 2), np.float32)
        lo, hi = max(a, 0), min(b, len(src))
        if hi > lo: seg[lo - a:hi - a] = src[lo:hi]
        env = np.ones(len(seg), np.float32)
        if r["fin"] > 0:
            k = min(int(r["fin"] * SR), len(seg)); env[:k] *= ramp(k, True)
        if r["fout"] > 0:
            end = len(seg)
            if r.get("fit_fade") and hi - a < len(seg):                  # source audio ends early: fade out before it ends
                end = max(hi - a, 0); env[end:] = 0
            k = min(int(r["fout"] * SR), end); env[end - k:end] *= ramp(k, False)
        seg *= env[:, None]
        o0, o1 = max(at, 0), min(at + len(seg), total)
        mix[o0:o1] += seg[o0 - at:o1 - at]
    for s in sfx:
        if s.get("synth") == "flash":
            clip, hit = flash_sfx(); start = int(round(s["at"] / FPS * SR)) - hit
        else:
            clip = read_audio(s["wav"]); start = int(round(s["at"] / FPS * SR))
        clip = clip * (10 ** (s.get("gain_db", 0) / 20))
        o0, o1 = max(start, 0), min(start + len(clip), total)
        mix[o0:o1] += clip[o0 - start:o1 - start]
    peak = float(np.abs(mix).max())
    if peak > 0.98: mix *= 0.98 / peak
    wav = Path(out_path).with_suffix(".mix.f32")
    wav.write_bytes(mix.astype(np.float32).tobytes())
    vf = label_filter(segs, seg_start, len(video), out_path)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-nostdin", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(wav)] + (["-vf", vf] if vf else []) + [
                            "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path)], stdin=subprocess.PIPE)
    for f in video: enc.stdin.write(f.tobytes())
    enc.stdin.close(); enc.wait(); wav.unlink()
    for p in Path(out_path).parent.glob(f".{Path(out_path).stem}_label*.txt"): p.unlink()
    rep = {"out": str(out_path), "frames": len(video), "seconds": round(len(video) / FPS, 3), "transitions": marks,
           "segments": [{"clip": s["clip"], "start": s["start"], "end": s["end"], "out_first": seg_start[i],
                         "label": s.get("label")} for i, s in enumerate(segs)]}
    Path(out_path).with_suffix(".json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("out")
    a = ap.parse_args()
    main(a.plan, a.out)

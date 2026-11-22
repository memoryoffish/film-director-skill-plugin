#!/usr/bin/env python3
"""occlusion-cut: hide the cut between two AI clips inside a frame that an object in the scene fully covers.

    occut.py gen   JOBS.json OUT_DIR [--workers 4]      submit/resume Wan 3.0 jobs (standard queue)
    occut.py tail  CLIP.mp4 OUT_DIR [--window 2]        pick the cut frame in the tail, write it as PNG
    occut.py seam  A.mp4 CUT B.mp4 OUT_DIR [--b-skip 1] measure the seam A[..CUT] + B[b_skip..]
    occut.py join  PLAN.json OUT.mp4                    frame-exact concat, audio crossfaded across cuts
    occut.py chain BOARD.json OUT_DIR                   shot after shot: generate, cut, next first frame, join

Needs ffmpeg/ffprobe, numpy and opencv. Every report is JSON next to its inputs.
"""
from __future__ import annotations

import argparse
import functools
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wan  # noqa: E402

LEAK_MAX = 12.0        # a frame is covered when no cell of a 4x8 grid differs from the median cell by more
                       # than this (CIE Lab ΔE); calibrated on 2026-11-10 Wan 3.0 tails (covered 3.7–7.8,
                       # background leaking at an edge 34–48)
FLOW_W, FLOW_H = 160, 90
MOTION_S = 0.5         # seconds of motion measured on each side of the cut
STILL = 0.02           # below this many frame-widths per second the picture counts as stopped
SPEED_RANGE = (0.5, 2.0)
HARD_CUT = 0.3         # ffmpeg scene score of an ordinary hard cut
XFADE_S = 0.25         # audio crossfade across each cut
LABEL_FONTS = {  # usual CJK font files; set $OCCUT_FONT to use another one
    "linux": ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
              "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"],
    "darwin": ["/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
               "/System/Library/Fonts/Supplemental/Songti.ttc", "/Library/Fonts/Arial Unicode.ttf"],
}


def label_font() -> str:
    """Font for the call labels: $OCCUT_FONT, else the first usual CJK font found on this platform."""
    if os.environ.get("OCCUT_FONT"):
        return os.environ["OCCUT_FONT"]
    paths = LABEL_FONTS.get(sys.platform, LABEL_FONTS["linux"])
    return next((p for p in paths if Path(p).exists()), paths[0])


LABEL_FONT = label_font()
LABEL_COLORS = ["0x6ea8fe", "0xf0a35e", "0x5ecb8a", "0xe0605e", "0xc58af9", "0xf2d45c"]


# ---------- decoding and per-frame measures ----------

def video_info(path: Path) -> dict:
    meta = wan.probe(path)
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    num, den = (int(x) for x in v["r_frame_rate"].split("/"))
    return {"w": int(v["width"]), "h": int(v["height"]), "fps": num / den,
            "duration": float(meta["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in meta["streams"])}


def decode(path: Path, width: int = 480) -> tuple[np.ndarray, float]:
    info = video_info(path)
    height = int(round(width * info["h"] / info["w"] / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-vf",
                          f"scale={width}:{height}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, height, width, 3), info["fps"]


def frame_count(path: Path) -> int:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", str(path)], capture_output=True, text=True,
                         check=True)
    return int(out.stdout.strip())


def leak(rgb: np.ndarray, rows: int = 4, cols: int = 8) -> float:
    """Largest colour distance of a grid cell from the median cell: background showing past the occluder."""
    lab = cv2.cvtColor(rgb.astype(np.float32) / 255.0, cv2.COLOR_RGB2LAB)
    h, w = lab.shape[:2]
    m = np.array([[lab[r * h // rows:(r + 1) * h // rows, c * w // cols:(c + 1) * w // cols].reshape(-1, 3).mean(0)
                   for c in range(cols)] for r in range(rows)])
    return float(np.linalg.norm(m - np.median(m.reshape(-1, 3), 0), axis=2).max())


def frame_info(rgb: np.ndarray) -> dict:
    """Compressed size is the proxy for how much a frame shows (the reference video's 单帧数据量);
    leak says whether anything but the occluder shows."""
    ok, buf = cv2.imencode(".jpg", np.ascontiguousarray(rgb[..., ::-1]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise RuntimeError("jpeg encode failed")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    return {"kb": round(len(buf) / 1024, 2), "leak": round(leak(rgb), 2), "luma": round(float(gray.mean()), 1),
            "std": round(float(gray.std()), 1), "lap": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 1)}


def choose_cut(kb: list[float], lk: list[float], fps: float, window_s: float) -> int:
    """Among the covered frames of the tail window the least informative one (later on ties);
    when none is covered, the frame that leaks least."""
    idx = range(max(0, len(kb) - int(round(window_s * fps))), len(kb))
    ok = [i for i in idx if lk[i] <= LEAK_MAX]
    if ok:
        best = min(kb[i] for i in ok)
        return max(i for i in ok if kb[i] == best)
    best = min(lk[i] for i in idx)
    return max(i for i in idx if lk[i] == best)


def flow_series(frames: np.ndarray) -> list[tuple[float, float]]:
    """Per consecutive pair: mean horizontal flow and mean flow magnitude, in frame widths per frame."""
    small = [cv2.resize(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY), (FLOW_W, FLOW_H), interpolation=cv2.INTER_AREA)
             for f in frames]
    out = []
    for a, b in zip(small, small[1:]):
        flow = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        out.append((float(flow[..., 0].mean()) / FLOW_W, float(np.hypot(flow[..., 0], flow[..., 1]).mean()) / FLOW_W))
    return out


def motion(frames: np.ndarray, fps: float) -> dict:
    """Mean horizontal velocity (negative: picture moves left, i.e. camera moves right) and speed, per second."""
    s = flow_series(frames)
    if not s:
        return {"dx": 0.0, "speed": 0.0}
    return {"dx": round(float(np.mean([d for d, _ in s])) * fps, 4),
            "speed": round(float(np.mean([m for _, m in s])) * fps, 4)}


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))
    return 99.0 if mse == 0 else round(10 * np.log10(255.0 ** 2 / mse), 2)


def scene_scores(frames: np.ndarray, fps: float) -> list[float]:
    """ffmpeg's scene score of every frame against the previous one (the score the reference video plots)."""
    h, w = frames.shape[1:3]
    proc = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                           f"{w}x{h}", "-r", f"{fps}", "-i", "-", "-vf",
                           "select='gte(scene,0)',metadata=print:file=-", "-f", "null", "-"],
                          input=frames.tobytes(), capture_output=True, check=True)
    return [float(x) for x in re.findall(r"lavfi\.scene_score=([0-9.]+)", proc.stdout.decode())]


def sheet(tiles: list[tuple[np.ndarray, str]], path: Path, cols: int = 5, width: int = 320) -> None:
    rows = []
    for i in range(0, len(tiles), cols):
        row = []
        for rgb, label in tiles[i:i + cols]:
            t = cv2.resize(rgb, (width, int(width * rgb.shape[0] / rgb.shape[1])), interpolation=cv2.INTER_AREA)
            t = np.ascontiguousarray(t[..., ::-1])
            cv2.putText(t, label, (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(t, label, (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)
            row.append(t)
        row += [np.zeros_like(row[0])] * (cols - len(row))
        rows.append(np.hstack(row))
    cv2.imwrite(str(path), np.vstack(rows))


@functools.lru_cache(maxsize=None)
def passthrough() -> tuple:
    """Keep every frame as it is: -fps_mode on ffmpeg 5.1 and later (newer ones dropped -vsync), -vsync 0 on older ones."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-h", "long"], capture_output=True, text=True).stdout
    return ("-fps_mode", "passthrough") if "-fps_mode" in out else ("-vsync", "0")


def export_frame(video: Path, index: int, dst: Path) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", str(video), "-vf",
                    f"select=eq(n\\,{index})", "-frames:v", "1", *passthrough(), str(dst)], check=True)


# ---------- Wan's own cuts inside one generation ----------

JUMP_K = 3             # compare frame i-3 with frame i+3
JUMP_FLAG = 0.25       # colour-histogram distance worth a look (fast pans and reveals reach 0.25-0.35)
JUMP_CUT = 0.40        # above this it was a cut/dissolve in every clip we checked


def hist_jumps(frames: np.ndarray) -> np.ndarray:
    """Bhattacharyya distance between HSV histograms of frames i-k and i+k (0 at the ends)."""
    hs = []
    for f in frames:
        h = cv2.calcHist([cv2.cvtColor(f, cv2.COLOR_RGB2HSV)], [0, 1, 2], None, [16, 4, 4], [0, 180, 0, 256, 0, 256])
        hs.append(cv2.normalize(h, h))
    d = np.zeros(len(frames))
    for i in range(JUMP_K, len(frames) - JUMP_K):
        d[i] = cv2.compareHist(hs[i - JUMP_K], hs[i + JUMP_K], cv2.HISTCMP_BHATTACHARYYA)
    return d


SEAM_GUARD_S = 1.0     # seconds next to a seam that must be free of Wan's own cuts


def seam_cuts(own: dict, head_s: float = 0.0, tail_s: float = 0.0) -> list[dict]:
    """Likely own cuts that would break a seam: within head_s after the start of the used range (right after the
    incoming seam) or tail_s before its end (what the outgoing seam relies on). Wan cutting elsewhere inside a clip
    is part of the clip's content and is fine: this skill is about the joins between clips."""
    start, end, fps = own["range"][0], own["range"][1], own["fps"]
    return [c for c in own["candidates"] if c["likely_cut"] and
            ((head_s > 0 and c["frame"] <= start + head_s * fps) or (tail_s > 0 and c["frame"] >= end - tail_s * fps))]


def own_cuts(clip: Path, out_dir: Path, start: int = 0, end: int | None = None) -> dict:
    """Candidate places where Wan cut or dissolved by itself inside the used range of one clip. The numbers only
    pick candidates (a fast pan can score like a dissolve); the sheets are for looking at every one of them."""
    frames, fps = decode(clip, width=320)
    end = len(frames) - 1 if end is None else min(end, len(frames) - 1)
    d = hist_jumps(frames)
    rng = range(max(start, JUMP_K), min(end, len(frames) - 1 - JUMP_K) + 1)
    peaks = [i for i in rng if d[i] >= JUMP_FLAG and d[i] == max(d[max(start, i - 5):i + 6])]
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = clip.stem
    near = lambda j: max(start, min(end, j))  # never index past the used range (a negative index wraps to the end)
    tiles = [(frames[near(j)], f"{near(j)} {near(j) / fps:.2f}s") for i in peaks for j in (i - 6, i - 2, i, i + 2, i + 6)]
    if tiles:
        sheet(tiles, out_dir / f"{stem}_jumps.png", cols=5, width=256)
    step = max(1, int(round(fps / 4)))
    sheet([(frames[j], f"{j / fps:.2f}s") for j in range(start, end + 1, step)], out_dir / f"{stem}_overview.png",
          cols=10, width=160)
    rep = {"clip": str(clip), "range": [start, end], "fps": fps, "median": round(float(np.median(d[list(rng)])), 3) if len(rng) else None,
           "candidates": [{"frame": i, "t": round(i / fps, 2), "d": round(float(d[i]), 3),
                           "likely_cut": bool(d[i] >= JUMP_CUT)} for i in peaks]}
    (out_dir / f"{stem}_jumps.json").write_text(json.dumps(rep, indent=1))
    return rep


# ---------- tail: where to cut ----------

def tail_report(clip: Path, out_dir: Path, window_s: float = 2.0) -> dict:
    frames, fps = decode(clip)
    infos = [frame_info(f) for f in frames]
    kb, lk = [i["kb"] for i in infos], [i["leak"] for i in infos]
    median = float(np.median(kb))
    cut = choose_cut(kb, lk, fps, window_s)
    covered = [i for i, v in enumerate(lk) if v <= LEAK_MAX]
    hold = 0
    while cut - hold - 1 >= 0 and lk[cut - hold - 1] <= LEAK_MAX:
        hold += 1
    n_m = max(2, int(round(MOTION_S * fps)))
    rep = {"clip": str(clip), "fps": fps, "frames": len(frames), "cut": cut, "cut_s": round(cut / fps, 3),
           "cut_kb": kb[cut], "median_kb": round(median, 2), "cut_ratio": round(kb[cut] / median, 3),
           "covered": lk[cut] <= LEAK_MAX, "covered_frames_before_cut": hold,
           "first_covered_s": round(covered[0] / fps, 3) if covered else None,
           "frames_after_cut": len(frames) - 1 - cut, "cut_frame": infos[cut],
           "motion_into_cut": motion(frames[max(0, cut - n_m):cut + 1], fps),
           "kb_tail": kb[max(0, len(kb) - int(round(window_s * fps))):],
           "leak_tail": lk[max(0, len(lk) - int(round(window_s * fps))):]}
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = clip.stem
    export_frame(clip, cut, out_dir / f"{stem}_cut.png")
    rep["cut_png"] = str((out_dir / f"{stem}_cut.png").resolve())
    picks = np.linspace(max(0, len(frames) - int(3 * fps)), cut, 10).round().astype(int)
    sheet([(frames[i], f"{i} {kb[i]:.0f}KB L{lk[i]:.0f}") for i in picks], out_dir / f"{stem}_tail.png")
    (out_dir / f"{stem}_tail.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


# ---------- seam: how the cut plays ----------

def match_frame(target: np.ndarray, frames: np.ndarray, limit: int) -> tuple[int, float]:
    """The frame among the first `limit` most like `target` (where an extension's copy of the input ends)."""
    scores = [psnr(target, f) for f in frames[:limit]]
    best = int(np.argmax(scores))
    return best, scores[best]


def seam_report(a: Path, cut: int, b: Path, out_dir: Path, b_skip: int | None = 1, tag: str | None = None) -> dict:
    """b_skip=None: B is an extension whose head repeats A up to the cut; skip past the best match."""
    fa, fps = decode(a)
    fb, fps_b = decode(b)
    if fa.shape[1:] != fb.shape[1:]:
        fb = np.stack([cv2.resize(f, (fa.shape[2], fa.shape[1]), interpolation=cv2.INTER_AREA) for f in fb])
    matched = None
    if b_skip is None:
        idx, score = match_frame(fa[cut], fb, int(round(6 * fps_b)))
        b_skip, matched = idx + 1, {"b_index": idx, "psnr": score}
    n_m = max(2, int(round(MOTION_S * fps)))
    into = motion(fa[max(0, cut - n_m):cut + 1], fps)
    out = motion(fb[b_skip:b_skip + n_m + 1], fps_b)
    n_s = int(round(fps))
    joined = np.concatenate([fa[max(0, cut - n_s):cut + 1], fb[b_skip:b_skip + n_s]])
    scores = scene_scores(joined, fps)
    at = min(cut, n_s) + 1  # index of the first B frame in the joined window
    others = scores[:at] + scores[at + 1:]
    a_hold = 0
    while cut - a_hold >= 0 and leak(fa[cut - a_hold]) <= LEAK_MAX:
        a_hold += 1
    b_hold = 0
    while b_skip + b_hold < len(fb) and leak(fb[b_skip + b_hold]) <= LEAK_MAX:
        b_hold += 1
    moving = abs(into["dx"]) >= STILL and abs(out["dx"]) >= STILL
    ratio = round(abs(out["dx"]) / abs(into["dx"]), 3) if abs(into["dx"]) >= STILL else None
    rep = {"a": str(a), "cut": cut, "b": str(b), "b_skip": b_skip, "matched": matched,
           "seam_scene_score": round(scores[at], 4) if at < len(scores) else None,
           "max_other_scene_score": round(max(others), 4) if others else None,
           "hard_cut_level": HARD_CUT, "b_first_vs_a_cut_psnr": psnr(fa[cut], fb[b_skip - 1]) if b_skip else None,
           "motion_into_cut": into, "motion_out_of_cut": out,
           "same_direction": moving and (into["dx"] < 0) == (out["dx"] < 0),
           "speed_ratio": ratio,
           "speed_ok": ratio is not None and SPEED_RANGE[0] <= ratio <= SPEED_RANGE[1],
           "covered_a_frames": a_hold, "covered_b_frames": b_hold,
           "covered_total_s": round((a_hold + b_hold) / fps, 3)}
    out_dir.mkdir(parents=True, exist_ok=True)
    name = tag or f"{a.stem}__{b.stem}"
    ia = [max(0, cut - k) for k in (24, 18, 12, 6, 0)]
    ib = [min(len(fb) - 1, b_skip + k) for k in (0, 6, 12, 18, 24)]
    sheet([(fa[i], f"A{i}") for i in ia] + [(fb[i], f"B{i}") for i in ib], out_dir / f"{name}_seam.png")
    (out_dir / f"{name}_seam.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


# ---------- join ----------

def ramp_source(t: float, k: float, ramp_s: float) -> float:
    """Source time shown at output time t when a segment's head plays k times fast and eases linearly
    back to normal speed over ramp_s output seconds (used to cancel the slow start of a first-frame clip)."""
    if k <= 1 or ramp_s <= 0:
        return t
    if t <= ramp_s:
        return k * t - (k - 1) * t * t / (2 * ramp_s)
    return t + (k - 1) * ramp_s / 2


def ramp_expr(k: float, ramp_s: float, fps: float) -> str:
    """ffmpeg setpts expression (in seconds) inverting ramp_source for input frame N."""
    s_end = ramp_s * (k + 1) / 2
    src = f"(N/{fps})"
    return (f"if(lte({src},{s_end:.6f}),{ramp_s}*({k}-sqrt({k * k:.6f}-2*{k - 1:.6f}*{src}/{ramp_s}))/{k - 1:.6f},"
            f"{src}-{s_end - ramp_s:.6f})")

def dissolve_graph(segments: list[dict], fps: float) -> list[str]:
    """Concatenate [v0]…[vk-1] into [v]; where segment i has dissolve d, its first d frames are blended
    frame by frame (weights 1/(d+1) … d/(d+1)) over the previous segment's last d frames."""
    k, parts, out = len(segments), [], []
    dis = [0] + [int(segments[i].get("dissolve", 0)) for i in range(1, k)]
    for i in range(k):
        n, head, tail = segments[i]["frames_out"], dis[i], dis[i + 1] if i + 1 < k else 0
        cuts = [("h", 0, head)] if head else []
        cuts += [("m", head, n - tail)] + ([("t", n - tail, n)] if tail else [])
        out.append(f"[v{i}]split={len(cuts)}" + "".join(f"[s{i}{c}]" for c, _, _ in cuts))
        out += [f"[s{i}{c}]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS[p{i}{c}]" for c, a, b in cuts]
        if head:
            d = head
            w = f"(T*{fps}+1)/{d + 1}"  # T is 0, 1/fps, … after setpts; N is 1-based in ffmpeg 4.4, so avoid it
            out.append(f"[p{i - 1}t][p{i}h]blend=all_expr='A*(1-{w})+B*{w}'[b{i}]")
            parts.append(f"[b{i}]")
        parts.append(f"[p{i}m]")
    out.append("".join(parts) + f"concat=n={len(parts)}:v=1:a=0[v]")
    return out


def audio_seams(segments: list[dict], infos: list[dict], fps: float, x: float) -> list[tuple[str, float]]:
    """How to crossfade the audio at each cut: ("post", d) runs the earlier clip d s past the cut; ("pre", d)
    starts the later clip's own audio d s before its first frame; ("cut", 0.02) is a hard cut with tiny fades.
    The earlier clip often has no audio after the cut (it was used to its last frame); fading it out before the
    cut instead made the level dip at every such seam."""
    plans = []
    for a, b, ia, ib in zip(segments, segments[1:], infos, infos[1:]):
        tail = ia["duration"] - (a["end"] + 1) / fps if ia["audio"] else 0.0
        pre = b["start"] / fps if ib["audio"] else 0.0
        if tail >= x:
            plans.append(("post", x))
        elif pre >= x:
            plans.append(("pre", x))
        elif max(tail, pre) >= 0.02:
            plans.append(("post", tail) if tail >= pre else ("pre", pre))
        else:
            plans.append(("cut", 0.02))
    return plans


def join(segments: list[dict], dst: Path, xfade_s: float = XFADE_S) -> dict:
    """segments: [{clip, start, end, head_speed?, ramp_s?, dissolve?}] with inclusive frame indices. Video is
    cut frame-exact; each segment's audio runs xfade_s past its cut where the clip has it and is crossfaded into
    the next one. head_speed > 1 plays the segment's head that much faster, easing to 1x over ramp_s.
    dissolve = N blends this segment's first N frames over the previous segment's last N frames (used when
    both sides of the cut are covered frames that do not match exactly, e.g. reference-image mode).
    label = text burned into the segment's top-left corner, with a coloured strip along the bottom that changes
    colour at every segment boundary (to show where one generation call ends and the next begins)."""
    infos = [video_info(Path(s["clip"])) for s in segments]
    w, h, fps = infos[0]["w"], infos[0]["h"], infos[0]["fps"]
    plans = audio_seams(segments, infos, fps, xfade_s)
    args, vf, af, t = ["ffmpeg", "-v", "error", "-nostdin", "-y"], [], [], 0.0
    for i, (s, info) in enumerate(zip(segments, infos)):
        args += ["-i", s["clip"]]
        n = s["end"] - s["start"] + 1
        k_head, ramp = float(s.get("head_speed", 1.0)), float(s.get("ramp_s", 0.0))
        saved = int(round(ramp * (k_head - 1) / 2 * fps)) if k_head > 1 and ramp > 0 else 0
        if saved:  # whole frames saved, so the tail after the ramp lands exactly on source frames
            ramp = 2 * saved / (fps * (k_head - 1))
        shift = saved / fps
        if shift and n / fps <= ramp * (k_head + 1) / 2:
            raise ValueError(f"segment {i} is shorter than its speed ramp")
        n_out = n - saved
        retime = f",setpts='({ramp_expr(k_head, ramp, fps)})/TB',fps={fps},trim=end_frame={n_out}" if shift else ""
        mark = ""
        if s.get("label"):
            txt = Path(dst).with_name(f".{Path(dst).stem}_label{i}.txt")
            txt.write_text(s["label"], encoding="utf-8")
            mark = (f",drawtext=fontfile={LABEL_FONT}:textfile={txt}:x=h/40:y=h/40:fontsize=h/28:fontcolor=white:"
                    f"box=1:boxcolor=black@0.55:boxborderw=10,"
                    f"drawbox=x=0:y=ih-ih/90:w=iw:h=ih/90:color={LABEL_COLORS[i % len(LABEL_COLORS)]}@0.95:t=fill")
        vf.append(f"[{i}:v]trim=start_frame={s['start']}:end_frame={s['end'] + 1},setpts=PTS-STARTPTS{retime},"
                  f"scale={w}:{h}:flags=lanczos,setsar=1,fps={fps}{mark},format=yuv420p,settb=AVTB[v{i}]")
        dis = int(s.get("dissolve", 0)) if i else 0
        if dis and (dis >= n_out or dis >= segments[i - 1]["frames_out"]):
            raise ValueError(f"segment {i}: dissolve of {dis} frames is longer than a segment")
        t -= dis / fps
        a0, a1 = s["start"] / fps + shift, (s["end"] + 1) / fps
        pin = plans[i - 1] if i > 0 else None
        pout = plans[i] if i < len(plans) else None
        lead = pin[1] if pin and pin[0] == "pre" else 0.0  # this segment's own audio from before its first frame
        a0e = max(0.0, a0 - lead)
        a1x = min(a1 + (pout[1] if pout and pout[0] == "post" else 0.0), info["duration"])
        src = (f"[{i}:a]atrim={a0e:.4f}:{a1x:.4f},asetpts=PTS-STARTPTS," if info["audio"] else
               f"anullsrc=r=48000:cl=stereo,atrim=0:{a1x - a0e:.4f},")
        chain = src + "aresample=48000,aformat=channel_layouts=stereo"
        if pin:
            chain += f",afade=t=in:d={pin[1]:.4f}"
        if pout:
            chain += f",afade=t=out:st={max(0.0, a1x - a0e - pout[1]):.4f}:d={pout[1]:.4f}"
        af.append(chain + f",adelay={int(round(max(0.0, t - lead) * 1000))}:all=1[a{i}]")
        s["placed_s"], s["frames_out"], t = round(t, 4), n_out, t + n_out / fps
    k = len(segments)
    graph = ";".join(vf + af + dissolve_graph(segments, fps) + ["".join(f"[a{i}]" for i in range(k)) +
                                     f"amix=inputs={k}:normalize=0:duration=longest,atrim=0:{t:.4f}[a]"])
    cur = "v"
    subprocess.run(args + ["-filter_complex", graph, "-map", f"[{cur}]", "-map", "[a]", "-c:v", "libx264",
                           "-crf", "16", "-preset", "slow", "-c:a", "aac", "-b:a", "192k", "-movflags",
                           "+faststart", str(dst)], check=True)
    return {"out": str(dst), "duration_s": round(t, 3), "segments": segments, "info": video_info(dst)}


# ---------- chain ----------

def shot_job(board: dict, shot: dict, take: int, first_frame: str | None) -> dict:
    job = {**board.get("defaults", {}), **{k: v for k, v in shot.items()
                                           if k not in ("end", "mode", "use_clip", "head_leak_max")}}
    job["name"] = shot["name"] if take == 1 else f"{shot['name']}_t{take}"
    if take > 1 and job.get("seed") is not None:
        job["seed"] = int(job["seed"]) + take - 1
    if first_frame:
        job["first_frame"] = first_frame
    return job


RAMP_S = 1.2           # seconds over which a slow-starting B head eases back to normal speed
RAMP_BELOW = 0.85      # speed ratio under which the head is sped up
RAMP_MAX = 2.5


HEAD_LEAK_MAX = 16.0   # reference mode: B's own opening cover usually leaves a thin edge (leak 14-20 seen)


def head_cover(clip: Path, window_s: float = 1.5, leak_max: float = LEAK_MAX) -> list[int]:
    """The first run of covered frames in the opening window (reference-image mode starts on its own cover)."""
    frames, fps = decode(clip)
    run: list[int] = []
    for i in range(min(len(frames), int(round(window_s * fps)))):
        if leak(frames[i]) <= leak_max:
            run.append(i)
        elif run:
            break
    return run


def take_problems(seam: dict | None, tail: dict | None) -> list[str]:
    """The checklist items a take fails (only those a retake can fix)."""
    out = []
    if tail is not None and not tail["covered"]:
        out.append(f"tail not covered (leak {tail['cut_frame']['leak']})")
    if seam is not None:
        into, outm = seam["motion_into_cut"]["dx"], seam["motion_out_of_cut"]["dx"]
        if abs(into) >= STILL and abs(outm) < STILL:
            out.append("B starts still")
        elif abs(into) >= STILL and (into < 0) != (outm < 0):
            out.append("B moves the other way")
    return out


def head_ramp(seam: dict | None) -> dict:
    r = seam and seam.get("speed_ratio")
    if not r or r >= RAMP_BELOW:
        return {}
    return {"head_speed": round(min(RAMP_MAX, 1 / r), 3), "ramp_s": RAMP_S}


def finish(raw: Path, dst: Path, target_s: float | None, fade_in: float, fade_out: float,
           trim_from: str = "end") -> dict:
    """Cut to target_s (from the end, or from the start so the last shot's ending survives) and fade."""
    dur = video_info(raw)["duration"]
    end = min(dur, target_s) if target_s else dur
    skip = dur - end if trim_from == "start" else 0.0
    vf = [f"fade=t=in:st=0:d={fade_in}"] if fade_in else []
    af = [f"afade=t=in:st=0:d={fade_in}"] if fade_in else []
    if fade_out:
        vf.append(f"fade=t=out:st={end - fade_out:.3f}:d={fade_out}")
        af.append(f"afade=t=out:st={end - fade_out:.3f}:d={fade_out}")
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", f"{skip:.3f}", "-i", str(raw), "-t", f"{end:.3f}"]
    cmd += (["-vf", ",".join(vf)] if vf else []) + (["-af", ",".join(af)] if af else [])
    subprocess.run(cmd + ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-c:a", "aac", "-b:a", "192k",
                          "-movflags", "+faststart", str(dst)], check=True)
    return {"out": str(dst), "info": video_info(dst)}


def run_chain(board: dict, out_dir: Path, client: wan.Client) -> dict:
    """Shot after shot: generate, check the seam with the previous shot and this shot's tail, retake (seed+1)
    a failing take up to `takes` times, then join with sped-up heads where B starts slow."""
    takes, window = int(board.get("takes", 1)), float(board.get("window_s", 2.0))
    out_dir = Path(out_dir).resolve()  # reports and plans keep absolute clip paths
    shots, prev, plan, report = board["shots"], None, [], {"shots": []}
    path = out_dir / "chain.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    for si, shot in enumerate(shots):
        last = si == len(shots) - 1
        refs_mode = prev is not None and shot.get("mode", board.get("mode")) == "refs"
        for take in range(1, takes + 1):
            job = shot_job(board, shot, take, None if refs_mode else prev and prev["cut_png"])
            if refs_mode:  # identity from reference images; Wan cannot mix them with a first frame
                job["reference_images"] = board["identity_refs"]
            if shot.get("use_clip"):
                clip, state = Path(shot["use_clip"]), {}
            else:
                state = wan.run_job(job, out_dir / "clips", client)
                clip = out_dir / "clips" / f"{job['name']}.mp4"
            lmax = float(shot.get("head_leak_max", board.get("head_leak_max", HEAD_LEAK_MAX)))  # per shot: a lit cover
            head = head_cover(clip, leak_max=lmax) if refs_mode else None
            b_skip = (head[0] if head else 0) if refs_mode else 1
            seam = prev and seam_report(Path(prev["clip"]), prev["cut"], clip, out_dir / "seams", b_skip=b_skip)
            tail = None if last else tail_report(clip, out_dir / "cuts", window)
            problems = take_problems(seam, tail) + (["B head not covered"] if refs_mode and not head else [])
            used = (0 if prev is None else b_skip, tail["cut"] if tail else None)
            own = own_cuts(clip, out_dir / "owncuts", used[0], used[1])
            near = seam_cuts(own, RAMP_S if prev is not None else 0.0, 0.0 if last else window)
            problems += [f"Wan own cut at frame {c['frame']} next to a seam" for c in near]
            entry = {"shot": shot["name"], "take": take, "clip": str(clip), "usage": state.get("usage"),
                     "seam": seam, "tail": tail, "head_cover": head, "problems": problems,
                     "own_cut_candidates": [c for c in own["candidates"] if c not in near]}
            report["shots"].append(entry)
            path.write_text(json.dumps(report, ensure_ascii=False, indent=1))
            wan.log("take", shot=shot["name"], take=take, problems=entry["problems"],
                    cut=tail and tail["cut"], leak=tail and tail["cut_frame"]["leak"],
                    speed_ratio=seam and seam["speed_ratio"], seam_score=seam and seam["seam_scene_score"])
            if not entry["problems"] or shot.get("use_clip"):
                break
        else:
            report["stopped"] = f"{shot['name']}: still {entry['problems']} after {takes} takes"
            break
        end = tail["cut"] if tail else frame_count(clip) - 1
        seg = {"clip": str(clip), "start": 0 if prev is None else b_skip, "end": end, **head_ramp(seam)}
        if refs_mode and head:  # both sides are covered but not the same frame: blend inside the cover
            d = min(int(board.get("dissolve_frames", 6)), prev["covered"])
            if d >= 2:
                seg["dissolve"] = d
        plan.append(seg)
        prev = tail and {"clip": str(clip), "cut": tail["cut"], "cut_png": tail["cut_png"],
                         "covered": tail["covered_frames_before_cut"] + 1}
    (out_dir / "plan.json").write_text(json.dumps(plan, indent=1))
    if "stopped" not in report:
        report["joined"] = join(plan, out_dir / "film_raw.mp4")
        report["film"] = finish(out_dir / "film_raw.mp4", out_dir / board.get("film_name", "film.mp4"),
                                board.get("target_s"), float(board.get("fade_in_s", 0)),
                                float(board.get("fade_out_s", 0)), board.get("trim_from", "end"))
    path.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    return report


# ---------- CLI ----------

def cmd_gen(args: argparse.Namespace) -> None:
    jobs = json.loads(Path(args.jobs).read_text())
    client = wan.Client(wan.read_key())
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(wan.run_job, j, Path(args.out), client): j["name"] for j in jobs}
        for f in as_completed(futures):
            try:
                f.result()
                wan.log("job_done", name=futures[f])
            except Exception as e:  # noqa: BLE001 - report each job as it ends, keep the others
                wan.log("job_failed", name=futures[f], error=f"{type(e).__name__}: {str(e)[:400]}")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("jobs"); g.add_argument("out"); g.add_argument("--workers", type=int, default=4)
    t = sub.add_parser("tail"); t.add_argument("clip"); t.add_argument("out"); t.add_argument("--window", type=float, default=2.0)
    s = sub.add_parser("seam"); s.add_argument("a"); s.add_argument("cut", type=int); s.add_argument("b")
    s.add_argument("out"); s.add_argument("--b-skip", default="1", help="frames of B to drop, or 'auto' for extensions")
    s.add_argument("--tag")
    j = sub.add_parser("join"); j.add_argument("plan"); j.add_argument("dst"); j.add_argument("--xfade", type=float, default=XFADE_S)
    c = sub.add_parser("chain"); c.add_argument("board"); c.add_argument("out")
    oc = sub.add_parser("cuts", help="find Wan's own cuts/dissolves inside the used range of one clip")
    oc.add_argument("clip"); oc.add_argument("out"); oc.add_argument("--start", type=int, default=0)
    oc.add_argument("--end", type=int)
    a = p.parse_args(argv)
    if a.cmd == "gen":
        cmd_gen(a)
    elif a.cmd == "tail":
        print(json.dumps(tail_report(Path(a.clip), Path(a.out), a.window), ensure_ascii=False, indent=1))
    elif a.cmd == "seam":
        skip = None if a.b_skip == "auto" else int(a.b_skip)
        print(json.dumps(seam_report(Path(a.a), a.cut, Path(a.b), Path(a.out), skip, a.tag), indent=1))
    elif a.cmd == "join":
        print(json.dumps(join(json.loads(Path(a.plan).read_text()), Path(a.dst), a.xfade), indent=1))
    elif a.cmd == "cuts":
        print(json.dumps(own_cuts(Path(a.clip), Path(a.out), a.start, a.end), indent=1))
    elif a.cmd == "chain":
        rep = run_chain(json.loads(Path(a.board).read_text()), Path(a.out), wan.Client(wan.read_key()))
        print(json.dumps({k: rep.get(k) for k in ("stopped", "film")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

"""Cut the 5F sequence of 《沙发》 from the generated clips, several ways, plus per-shot pieces for the page.

python3 cut_fin.py            writes out/fin/cut_<way>.mp4 and out/fin/shots/<way>_<shot>.mp4
Ways: GF  = one clip per shot, gpt keyframe as first (and last) frame
      URI = one clip per unit (multi-shot), white-model stills as reference images
      URG = one clip per unit, gpt keyframes as reference images
      URV = one clip per unit, white-model previz as reference video
PICK says which seed is used where; change it after looking at the takes.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLIPS, OUT = HERE / "clips", HERE / "out/fin"
SHOTS = [("s51", 3.5), ("s52", 2.6), ("s53", 3.5), ("s54", 3.4), ("s55", 2.4), ("s56", 2.55), ("s57", 3.25), ("s61", 5.2), ("s62", 7.4)]
UNITS = {"U5a": ["s51", "s52", "s53"], "U5b": ["s54", "s55", "s56", "s57"], "U6": ["s61", "s62"]}
LASTF = {"s51", "s53"}
OLD = [0, 3.5, 6.1, 9.6, 13.0, 15.4, 17.95, 21.6, 26.3, 34.1]       # shot boundaries inside out/fin/old_seg.mp4
PICK = json.loads((HERE / "pick.json").read_text()) if (HERE / "pick.json").exists() else {}
ENC = ["-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def piece(src, t0, length, dst):
    """Cut [t0, t0 + length) with a 30 ms audio fade at both ends, so joined pieces do not click."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    af = f"afade=t=in:st=0:d=0.03,afade=t=out:st={length - 0.03:.3f}:d=0.03"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-i", str(src), "-t", f"{length:.3f}", "-vf", "scale=1280:720", "-af", af, *ENC, str(dst)], check=True)
    return dst


def join(parts, dst):
    lst = dst.with_suffix(".txt")
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(dst)], check=True)
    lst.unlink()
    return dst


def cuts(path, lo=0.25):
    """Times of the hard cuts inside a multi-shot clip (ffmpeg scene detection)."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", f"select='gt(scene,{lo})',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [float(l.split("pts_time:")[1].split()[0]) for l in r.stderr.splitlines() if "pts_time:" in l]


def nearest(found, want, tol=0.9):
    c = [t for t in found if abs(t - want) <= tol]
    return min(c, key=lambda t: abs(t - want)) if c else want


if __name__ == "__main__":
    shots = OUT / "shots"
    report = {}
    # ---- GF / GF2: one clip per shot (GF2 = the slim prompt: motion, camera and sound only)
    for way, tag, seed0 in (("GF", "", 9201), ("GF2", "2", 9301)):
        parts = []
        for n, length in SHOTS:
            seed = PICK.get(way, {}).get(n, seed0)
            src = CLIPS / f"{n}_{'GFL' if n in LASTF else 'GF'}{tag}_s{seed}.mp4"
            if not src.exists():
                parts = None
                break
            t0 = max(0.0, dur(src) - length - 0.05) if n in LASTF else 0.0     # first+last clips: keep the end (it lands on the last frame)
            parts.append(piece(src, t0, length, shots / f"{way}_{n}.mp4"))
        if parts:
            join(parts, OUT / f"cut_{way}.mp4")
            report[way] = dur(OUT / f"cut_{way}.mp4")
    # ---- unit ways: one clip per unit, trimmed to the unit's length
    for way in ("URI", "URG", "URV"):
        parts = []
        for u, names in UNITS.items():
            seed = PICK.get(way, {}).get(u, 9101)
            src = CLIPS / f"{u}_{way}_s{seed}.mp4"
            if not src.exists():
                parts = None
                break
            lens = [dict(SHOTS)[n] for n in names]
            found = cuts(src)
            edges, t = [0.0], 0.0
            for L in lens[:-1]:
                t += L
                edges.append(nearest(found, t))
            edges.append(min(dur(src), sum(lens)))
            report[f"{way}_{u}_s{seed}"] = {"wanted": [round(sum(lens[:i + 1]), 2) for i in range(len(lens) - 1)], "found": [round(x, 2) for x in found]}
            parts.append(piece(src, 0, sum(lens), shots / f"{way}_{u}.mp4"))
            for n, a, b in zip(names, edges, edges[1:]):
                piece(src, a + 0.03, b - a - 0.06, shots / f"{way}_{n}.mp4")
        if parts:
            join(parts, OUT / f"cut_{way}.mp4")
            report[way] = dur(OUT / f"cut_{way}.mp4")
    # ---- the old film, shot by shot
    for (n, _l), a, b in zip(SHOTS, OLD, OLD[1:]):
        piece(OUT / "old_seg.mp4", a, b - a, shots / f"old_{n}.mp4")
    print(json.dumps(report, ensure_ascii=False, indent=1))

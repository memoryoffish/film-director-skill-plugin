#!/usr/bin/env python3
"""查一份镜头清单的格式（不读清单里写的文件，只看清单本身）。格式见 shots-manifest.md。

    python3 check_manifest.py <清单.shots.json…>      有问题打出来，退出码 1；都没问题退出码 0

在别的脚本里用：from check_manifest import check；check(清单) → 问题列表（没问题是空的）。只用标准库。
"""
from __future__ import annotations

import json
import pathlib
import sys

FEEDS = ("T2V", "I2V", "FLF2V", "R2V")
KINDS = ("wm", "ref", "key", "img")


def _stem(rel: str) -> str:
    return pathlib.PurePosixPath(rel).stem


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _strs(x) -> bool:
    return isinstance(x, list) and all(isinstance(v, str) for v in x)


def _attempts(where: str, a, used_name: str, out: list) -> None:
    """重抽 / 重画的明细：每次 {name, used, status, error, seed, diff, was, why}；用上的最多一次，就是这一条。"""
    if not isinstance(a, list) or not all(isinstance(t, dict) and isinstance(t.get("name"), str) and isinstance(t.get("used"), bool)
                                          for t in a):
        out.append(f"{where}.attempts: want a list of {{name, used, …}}")
        return
    used = [t["name"] for t in a if t["used"]]
    if used and used != [used_name]:
        out.append(f"{where}.attempts: the one used should be {used_name!r}, found {used}")
    for t in a:
        if not _strs(t.get("diff", [])) or not isinstance(t.get("was", {}), dict):
            out.append(f"{where}.attempts[{t['name']}]: diff is a list of field names, was is an object")


def check(m: dict) -> list[str]:
    out: list[str] = []
    if not isinstance(m, dict):
        return ["the manifest is not a JSON object"]
    for k in ("film", "root", "video"):
        if not isinstance(m.get(k), str) or not m.get(k):
            out.append(f"{k}: missing or not a string")
    if "/" in str(m.get("film", "")):
        out.append("film: no '/' (it is a folder and file name)")
    if not isinstance(m.get("shots"), list) or not m.get("shots"):
        return out + ["shots: missing or empty"]
    pics, ijobs = m.get("pictures"), m.get("image_jobs")
    for k, v in (("pictures", pics), ("image_jobs", ijobs), ("roles", m.get("roles"))):
        if v is not None and not isinstance(v, dict):
            out.append(f"{k}: want an object")
    pics = pics if isinstance(pics, dict) else {}
    ijobs = ijobs if isinstance(ijobs, dict) else {}
    names = []
    for i, s in enumerate(m["shots"]):
        w = f"shots[{i}]"
        if not isinstance(s, dict) or not isinstance(s.get("name"), str) or not s.get("name"):
            out.append(f"{w}: want an object with a name")
            continue
        w = f"shots[{i}] ({s['name']})"
        names.append(s["name"])
        if not (_num(s.get("t0")) and _num(s.get("t1")) and s["t0"] <= s["t1"]):
            out.append(f"{w}: t0, t1 are seconds in the film, t0 <= t1")
        v = s.get("video")
        fed: list[str] = []
        if v is not None:
            if not isinstance(v, dict) or not isinstance(v.get("name"), str) or v.get("feed") not in FEEDS:
                out.append(f"{w}.video: want {{name, feed}} with feed one of {'/'.join(FEEDS)}")
                v = None
            else:
                need = {"T2V": (), "I2V": ("first",), "FLF2V": ("first", "last"), "R2V": ()}[v["feed"]]
                out += [f"{w}.video: feed {v['feed']} needs {k}" for k in need if not isinstance(v.get(k), str)]
                if "refs" in v and not _strs(v["refs"]):
                    out.append(f"{w}.video.refs: want a list of paths")
                fed = [v[k] for k in need if isinstance(v.get(k), str)]
                if v["feed"] == "R2V":
                    fed += (v.get("refs") or [])[:9]
                for t in v.get("takes") or []:
                    if not (isinstance(t, list) and len(t) == 3 and isinstance(t[0], str) and t[1] in (True, False, None)
                            and isinstance(t[2], bool)):
                        out.append(f"{w}.video.takes: each take is [name, true/false/null, used true/false]")
                        break
                if "sent" in v and not isinstance(v["sent"], dict):
                    out.append(f"{w}.video.sent: want an object (the job file as written)")
                if "status" in v and not isinstance(v["status"], (str, type(None))):
                    out.append(f"{w}.video.status: want a string or null")
                if "attempts" in v:
                    _attempts(f"{w}.video", v["attempts"], v["name"], out)
        for rel, kf in (s.get("keyframes") or {}).items():
            if rel not in fed:
                out.append(f"{w}.keyframes[{rel}]: a keyframe here must be one of the pictures the video uses directly")
            if not isinstance(kf, dict) or not _strs(kf.get("inputs")):
                out.append(f"{w}.keyframes[{rel}]: want {{prompt, inputs: [paths]}}")
        for rel, im in (s.get("images") or {}).items():
            if not isinstance(im, dict) or im.get("kind", "img") not in KINDS or not isinstance(im.get("title"), str):
                out.append(f"{w}.images[{rel}]: want {{kind: {'/'.join(KINDS)}, title}}")
        for k in ("stills", "named_stills"):
            if k in s and not (isinstance(s[k], list) and len(s[k]) == 2 and all(isinstance(x, (str, type(None))) for x in s[k])):
                out.append(f"{w}.{k}: want [start, end], each a path or null")
        if "own_ref" in s:
            refs = ((v or {}).get("sent") or {}).get("reference_images", (v or {}).get("refs")) or []
            if not (isinstance(s["own_ref"], int) and 0 <= s["own_ref"] < len(refs)):
                out.append(f"{w}.own_ref: want an index into this video's reference pictures (it has {len(refs)})")
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        out.append(f"shots: names used twice: {dup}")
    flag = m.get("flag")
    if flag is not None and not (isinstance(flag, dict) and _num(flag.get("t")) and set(flag.get("shots") or []) <= set(names)):
        out.append("flag: want {t: seconds, shots: [names of shots in this film], note}")
    for rel, p in pics.items():
        if not isinstance(p, dict) or not isinstance(p.get("label"), str):
            out.append(f"pictures[{rel}]: want an object with a label")
            continue
        if "made_by" in p and p["made_by"] not in ijobs:
            out.append(f"pictures[{rel}].made_by: {p['made_by']!r} is not in image_jobs")
        if p.get("keyframe") and _stem(rel) not in ijobs:
            out.append(f"pictures[{rel}]: keyframe, but {_stem(rel)!r} is not in image_jobs")
        if "still" in p and not (isinstance(p["still"], list) and len(p["still"]) == 2 and p["still"][1] in ("a", "b")):
            out.append(f"pictures[{rel}].still: want [shot, 'a' or 'b']")
    for k, j in ijobs.items():
        if not isinstance(j, dict) or not _strs(j.get("inputs")):
            out.append(f"image_jobs[{k}]: want {{prompt, inputs: [paths]}}")
            continue
        if "attempts" in j:
            _attempts(f"image_jobs[{k}]", j["attempts"], k, out)
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    bad = 0
    for f in sys.argv[1:]:
        try:
            problems = check(json.loads(pathlib.Path(f).read_text(encoding="utf-8")))
        except (OSError, ValueError) as e:
            problems = [f"cannot read: {e}"]
        print(f"{f}: {'ok' if not problems else f'{len(problems)} problems'}")
        for p in problems:
            print(f"  {p}")
        bad += bool(problems)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

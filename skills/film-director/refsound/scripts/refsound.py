#!/usr/bin/env python3
# refsound：照「听过的人留下的信号」从 Freesound 给每种声音挑一批靠得住的录音。
#   search  只用标准库。照 spec 里每种声音的查询词取公开搜索页，按规则筛、排，下载排在前面的 MP3 预览。
#   check   要 ffmpeg 与 numpy。把预览解码，量声音本身，定最后的清单。
# 规则与每条规则的来由写在 ../GUIDE.md。选材的四条基本规则出自 vibe-motion/sound（B 站「浙大猫学长」），这里只借用规则，代码是另写的。
# 用法：
#   python3 refsound.py search <spec.json> <输出目录> [--only 声音键 ...] [--exclude 编号清单.json ...] [--revet]
#   python3 refsound.py check  <spec.json> <输出目录> [--only 声音键 ...]
import argparse
import html
import json
import math
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import numpy as np      # 只有 check 用
except ImportError:
    np = None

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) refsound (reference sound selection)"}
SEARCH_URL = "https://freesound.org/search/?"
LICENSES = {"cc0": "Creative Commons 0", "by": "Attribution"}
DEFAULTS = {"pages": 4, "keep": 16, "n": 12, "per_user": 3, "licenses": ["cc0", "by"]}
PAUSE_S, DOWNLOAD_THREADS = 0.6, 4
# 评分落成数：贝叶斯平均，评分人数少的往 PRIOR_RATING 靠
PRIOR_RATING, PRIOR_N = 3.9, 10
# 描述说是手机或内置话筒录的，但评分的人够多、分也高：听过的人的判断比字面更可信，留下
TRUST_N, TRUST_R = 30, 4.3
# 评分的人不少而平均分低：听过的人明确不满意，下载量再高也不要
LOW_N, LOW_R = 5, 3.0
# 量声音的门槛
SR, CLIP_MAX, LOWFREQ_MAX, ACTIVE_MIN, TAIL_MAX, TAIL_MIN_S = 48000, 0.01, 0.8, 0.6, 0.6, 1.0
SKIPS = {"ambient", "lowfi", "synth", "lowfreq", "tail"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ONBOARD = ["built-in mic", "builtin mic", "built in mic", "internal mic"]      # 写了录音机型号时，说的是录音机自带的话筒，不算低保真
PHONE = ONBOARD + ["laptop mic", "phone", "iphone", "android", "smartphone", "cellphone"]
LOWFI = PHONE + ["webcam", "made with my mouth", "with my mouth", "my mouth", "mouth", "lips", "tongue", "vocalized", "vocalised",
                 "vocal imitation", "imitation", "beatbox", "voice acting", "fake", "faked", "faux", "simulated", "simulation", "artificial"]
# 描述里这些说法后面几个词之内跟着声源词：上传者自己说的是「像」这种声音
HEDGE = ["could be", "sounds like", "sound like", "sounding like", "similar to", "resembles", "resembling", "imitating", "simulating",
         "simulates", "supposed to be", "meant to be", "pretending", "mimics", "mimicking", "emulates", "emulating"]
HEDGE_WORDS = 6
# 否定词紧挨着声源词（中间至多两个冠词或副词）：上传者自己说的是「不是」这种声音
NEGATION = r"(?:not|isn't|isnt|is not|no|never|without)(?: (?:a|an|the|really|actually|real|actual)){0,2}"
# 词尾：must 的词认 owl/owls、bark/barking；其余词表只认复数。不按任意词头匹配（cork 不认 corkscrew，class 不认 classical）
VERB, PLURAL = r"(?:s|es|ed|ing)?", r"(?:s|es)?"
SYNTH = ["synth", "synthesized", "synthesised", "synthesizer", "midi", "vst", "soundfont", "generated", "sfxr", "8-bit", "8bit", "chiptune",
         "remix", "processed", "pitched", "reversed", "reverse", "glitch", "distorted", "edm", "dubstep", "trap", "sound design", "designed",
         "stock instruments", "virtual instrument", "virtual", "vsti", "kontakt", "plugin", "plug-in", "sampler", "sample library", "jingle",
         "studio one", "fl studio", "garageband", "lmms", "musescore"]
AMBI = ["ambience", "ambiance", "ambient", "atmosphere", "atmo", "soundscape", "people", "crowd", "party", "festival", "market", "restaurant",
        "cafe", "event", "walla", "city", "traffic", "street", "tv", "television", "radio show", "podcast"]
AMBI_GLUED = 7      # 这么长的环境词连写在别的词里也认（folkfestival）
GEAR = ["zoom", "h4n", "h2n", "h1n", "h5", "h6", "tascam", "dr-40", "dr-05", "dr-100", "sound devices", "mixpre", "sennheiser", "mkh", "rode",
        "nt1", "nt2", "nt4", "nt5", "ntg", "neumann", "akg", "shure", "sm57", "sm58", "sony pcm", "pcm-d", "pcm-m10", "olympus ls", "ls-10",
        "marantz", "fostex", "edirol", "r-09", "r-26", "audio-technica", "at2020", "oktava", "binaural", "x/y", "xy stereo", "ms stereo",
        "condenser", "shotgun", "lavalier", "contact mic", "hydrophone", "field recorder", "recorder", "96khz", "24bit", "24-bit", "96k"]


def read(p: str | Path) -> Any:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write(p: str | Path, obj: Any) -> None:
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def load_spec(path: str, only: list[str] | None) -> tuple[dict, dict]:
    spec = read(path)
    cfg = {**DEFAULTS, **{k: spec[k] for k in DEFAULTS if k in spec}}
    bad = [x for x in cfg["licenses"] if x not in LICENSES]
    if bad:
        sys.exit(f"spec 的 licenses 只认 {sorted(LICENSES)}，看到 {bad}")
    sounds = spec.get("sounds") or {}
    for key, s in sounds.items():
        lists = [s.get("queries"), s.get("reject", [])] + (s["must"] if isinstance(s.get("must"), list) else [None])
        if not s.get("queries") or not s.get("must") or not all(isinstance(g, list) and all(isinstance(w, str) and w for w in g) for g in lists) \
                or not all(s["must"]):
            sys.exit(f"spec 的 {key}：queries、must 的每一组、reject 都要写成字符串的列表；queries 与 must 不能空")
        if s.get("kind") not in ("continuous", "event"):
            sys.exit(f"spec 的 {key}：kind 要写 continuous（持续的声音）或 event（一下一下的声音）")
        dur = s.get("dur")
        if not isinstance(dur, list) or len(dur) != 2 or not all(isinstance(x, (int, float)) for x in dur) or dur[0] >= dur[1]:
            sys.exit(f"spec 的 {key}：dur 要写成 [最短秒数, 最长秒数]")
        if set(s.get("skip", [])) - SKIPS:
            sys.exit(f"spec 的 {key}：skip 只认 {sorted(SKIPS)}")
    missing = [k for k in only or [] if k not in sounds]
    if missing:
        sys.exit(f"spec 里没有这些声音：{missing}")
    return cfg, {k: s for k, s in sounds.items() if not only or k in only}


def fetch(url: str, tries: int = 3) -> bytes:
    host = urllib.parse.urlparse(url).hostname or ""      # 预览的网址取自页面，只认 freesound.org 的 https
    if not url.startswith("https://") or not (host == "freesound.org" or host.endswith(".freesound.org")):
        raise ValueError(f"不是 freesound.org 的 https 网址：{url[:80]}")
    for n in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception:
            if n == tries - 1:
                raise
            time.sleep(2 + 2 * n)


def parse(page: str) -> list[dict]:
    # 公开搜索页上每条结果的卡片：下载量、评分与人数、时长、许可、标签、上传日期、描述
    rows = []
    for blk in page.split('class="bw-search__result"')[1:]:
        g = lambda k: (re.search(rf'data-{k}="([^"]*)"', blk) or [None, ""])[1]  # noqa: E731
        if not g("sound-id"):
            continue
        lic = re.search(r'title="License: ([^"]+)"', blk)
        rt = re.search(r'aria-label="Average rating of ([\d.]+)"', blk)
        rn = re.search(r'bw-rating__count[^>]*>\((\d+)\)', blk)
        desc = re.search(r'<div class="max-h-60px[^"]*"\s*>\s*(.*?)\s*</div>', blk, re.S)
        date = re.search(rf"({'|'.join(MONTHS)}) \d+\w*, (\d{{4}})", blk)
        tags = sorted(set(urllib.parse.unquote(t).lower() for t in re.findall(r'/browse/tags/([^/"?]+)/', blk)))
        rows.append({"id": int(g("sound-id")), "title": html.unescape(g("title")), "username": g("username"),
                     "duration_s": float(g("duration") or 0), "downloads": int(g("num-downloads") or 0),
                     "samplerate": float(g("samplerate") or 0), "tags": tags,
                     "uploaded": f"{date[1]} {date[2]}" if date else None,
                     "year": int(date[2]) + (MONTHS.index(date[1]) + 0.5) / 12 if date else None,
                     "rating": float(rt[1]) if rt else None, "n_ratings": int(rn[1]) if rn else 0,
                     "license": lic.group(1) if lic else None, "preview": g("mp3").replace("-lq.mp3", "-hq.mp3"),
                     "description": html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", desc[1]))).strip() if desc else ""})
    return rows


def norm(text: str) -> str:
    return re.sub(r"[-_\s]+", " ", text.lower())


def has(text: str, words: list[str], ending: str = PLURAL) -> list[str]:
    # 整词（或短语）匹配，词尾照 ending；text 要先过 norm
    return [w for w in words if re.search(rf"(?<![a-z0-9]){re.escape(norm(w))}{ending}(?![a-z0-9])", text)]


def hedged(text: str, source: list[str]) -> str | None:
    src = "(?:" + "|".join(re.escape(norm(w)) for w in source) + f"){VERB}(?![a-z0-9])"
    like = "|".join(re.escape(h) for h in HEDGE)
    m = (re.search(rf"(?<![a-z0-9])(?:{like})(?:\W+\w+){{0,{HEDGE_WORDS - 1}}}?\W+{src}", text)
         or re.search(rf"(?<![a-z0-9]){NEGATION} {src}", text))
    return m[0] if m else None


def vet(c: dict, s: dict, licenses: list[str]) -> str | None:
    # 返回不要这一条的原因；None 是通过
    skip = set(s.get("skip", []))
    named = norm(f"{c['title']} {' '.join(c['tags'])}")
    text = f"{named} {norm(c['description'])}"
    if c.get("excluded"):
        return f"在排除清单里（{c['excluded']}）"
    if c["license"] not in licenses:
        return f"许可是 {c['license']}"
    if not has(named, s["must"][0], VERB):
        return f"标题和标签里没有写明声源（缺 {s['must'][0][0]} 一类的词）"
    for group in s["must"][1:]:
        if not has(text, group, VERB):
            return f"标题、标签与描述里没有 {group[0]} 一类的词"
    ambi = [] if "ambient" in skip else AMBI
    bad = has(text, s.get("reject", []) + ambi) or [w for w in ambi if len(w) >= AMBI_GLUED and w in text]
    if bad:
        return f"描述与要的不符（{bad[0]}）"
    like = hedged(text, s["must"][0])
    if like:
        return f"描述说只是像、或者不是这种声音（{like}）"
    low = [] if "lowfi" in skip else has(text, LOWFI)
    if has(text, GEAR):
        low = [w for w in low if w not in ONBOARD]
    if low and not (c["n_ratings"] >= TRUST_N and (c["rating"] or 0) >= TRUST_R and all(w in PHONE for w in low)):
        return f"低保真或模仿（{low[0]}）"
    syn = [] if "synth" in skip else has(text, SYNTH)
    if syn:
        return f"合成或处理过（{syn[0]}）"
    if c["n_ratings"] >= LOW_N and (c["rating"] or 5) < LOW_R:
        return f"评分的人不少、分却低（★{c['rating']}，{c['n_ratings']} 人）"
    if not (s["dur"][0] <= c["duration_s"] <= s["dur"][1]):
        return f"时长 {c['duration_s']:.1f} s 不在 {s['dur'][0]}～{s['dur'][1]} s"
    return None


def signals(c: dict, now_year: float) -> dict:
    # 排序分 = log10(下载量) + 0.5·log10(每年下载量) + 0.3·(贝叶斯评分 − 先验) + 写了录音设备的小幅加分
    years = max(0.5, now_year - c["year"]) if c["year"] else 8.0
    per_year = round(c["downloads"] / years, 1)
    bayes = round((c["n_ratings"] * (c["rating"] or PRIOR_RATING) + PRIOR_N * PRIOR_RATING) / (c["n_ratings"] + PRIOR_N), 3)
    gear = has(norm(f"{c['title']} {c['description']}"), GEAR)
    return {"gear": gear, "downloads_per_year": per_year, "bayes_rating": bayes,
            "score": round(math.log10(1 + c["downloads"]) + 0.5 * math.log10(1 + per_year) + 0.3 * (bayes - PRIOR_RATING)
                           + (0.15 if gear else 0.0), 3)}


def load_excluded(files: list[str] | None) -> dict[int, str]:
    out = {}
    for f in files or []:
        d = read(f)
        for i, why in (d.items() if isinstance(d, dict) else ((i, Path(f).name) for i in d)):
            out.setdefault(int(i), str(why))
    return out


def cmd_search(a: argparse.Namespace) -> None:
    cfg, sounds = load_spec(a.spec, a.only)
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_p = out_dir / "candidates.json"
    out = read(out_p) if out_p.exists() else {}
    excluded = load_excluded(a.exclude)
    licenses = [LICENSES[x] for x in cfg["licenses"]]
    lic_f = "license:(" + " OR ".join(f'"{x}"' for x in licenses) + ")"
    now = datetime.now(timezone.utc)
    now_year = now.year + (now.timetuple().tm_yday - 0.5) / 365.25
    for key, s in sounds.items():
        if a.revet:
            if key not in out:
                sys.exit(f"--revet 要先有 {out_p} 里 {key} 的候选")
            rows, fetched, at_year = out[key]["candidates"], out[key]["fetched"], out[key]["now_year"]
        else:
            cands = {}
            for q in s["queries"]:
                for page in range(1, cfg["pages"] + 1):
                    url = SEARCH_URL + urllib.parse.urlencode({"q": q, "s": "Automatic by relevance", "f": lic_f, "page": page})
                    got = parse(fetch(url).decode("utf-8", "replace"))
                    for r in got:
                        cands.setdefault(r["id"], {**r, "queries": []})["queries"].append(q)
                    time.sleep(PAUSE_S)
                    if len(got) < 15:
                        break
            rows, fetched, at_year = list(cands.values()), now.strftime("%Y-%m-%d"), now_year
            if not rows:
                print(f"{key}：一条都没搜到。查询词太偏，或者 Freesound 的搜索页结构变了（parse 认不出结果卡片）", file=sys.stderr)
        for r in rows:
            r["excluded"] = excluded.get(r["id"]) or r.get("excluded")      # 记在候选里，--revet 不带 --exclude 也不会放回来
            r["rejected"] = vet(r, s, licenses)
            r.update(signals(r, at_year))
            r["lowfi_but_trusted"] = bool(not r["rejected"] and "lowfi" not in s.get("skip", [])
                                          and has(norm(f"{r['title']} {' '.join(r['tags'])} {r['description']}"), PHONE))
        rows.sort(key=lambda r: -r["score"])
        ok, per_user = [], {}
        for r in rows:
            if r["rejected"]:
                continue
            if per_user.get(r["username"], 0) >= cfg["per_user"]:
                r["rejected"] = f"同一个上传者（{r['username']}）已经取了 {cfg['per_user']} 条"
                continue
            per_user[r["username"]] = per_user.get(r["username"], 0) + 1
            ok.append(r)
        keep = ok[:cfg["keep"]]
        d = out_dir / "previews" / key
        d.mkdir(parents=True, exist_ok=True)

        def grab(r: dict) -> bool:
            p = d / f"{r['id']}.mp3"
            try:
                if not p.exists() or p.stat().st_size == 0:
                    tmp = p.with_suffix(".part")
                    tmp.write_bytes(fetch(r["preview"]))
                    tmp.replace(p)
            except Exception as e:      # 一条下载不了不拖累别的
                r["rejected"] = f"预览下载不了（{type(e).__name__}）"
                return False
            r["preview_file"] = str(p.relative_to(out_dir))
            return True

        with ThreadPoolExecutor(DOWNLOAD_THREADS) as pool:
            got = list(pool.map(grab, keep))
        keep = [r for r, g in zip(keep, got) if g]
        out[key] = {"note": s.get("note", ""), "kind": s["kind"], "queries": s["queries"], "fetched": fetched, "now_year": round(at_year, 3),
                    "n_found": len(rows), "n_ok": len(ok), "kept": [r["id"] for r in keep], "candidates": rows}
        write(out_p, out)
        top = "；".join(f"{r['id']} ↓{r['downloads']} ★{r['rating']}({r['n_ratings']})" for r in keep[:4])
        print(f"{key:16s} 搜到 {len(rows):3d} 条，过了文字筛选 {len(ok):3d} 条，取 {len(keep):2d} 条预览；排在前面的：{top}", flush=True)


def decode(path: Path) -> "np.ndarray":
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], check=True,
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def measure(x2: "np.ndarray") -> dict:
    w = SR // 10
    seconds = len(x2) / SR
    if len(x2) < w:      # 不足一帧（0.1 s）的补零到一帧
        x2 = np.concatenate([x2, np.zeros((w - len(x2), 2))])
    x = x2.mean(axis=1)
    n = len(x) // w
    db = 10 * np.log10(np.mean(x[: n * w].reshape(n, w) ** 2, axis=1) + 1e-20)
    on = np.flatnonzero(db >= db.max() - 25.0)
    head = x[: min(len(x), SR * 60)]
    spec = np.abs(np.fft.rfft(head)) ** 2
    f = np.fft.rfftfreq(len(head), 1 / SR)
    tot = spec.sum() + 1e-20
    band = lambda lo, hi: round(float(spec[(f >= lo) & (f < hi)].sum() / tot), 3)  # noqa: E731
    return {"duration_s": round(seconds, 2), "peak": round(float(np.abs(x2).max()), 4),
            "clip_fraction": round(float(np.mean(np.abs(x2) >= 0.999)), 5),
            "active_fraction": round(float(np.mean(db >= db.max() - 30.0)), 3),
            "tail_fraction": round(float((n - 1 - on[-1]) / max(1, n)), 3) if len(on) else 1.0,
            "energy_share": {"<100Hz": band(0, 100), "100-500Hz": band(100, 500), "500-2kHz": band(500, 2000),
                             "2k-8kHz": band(2000, 8000), ">8kHz": band(8000, SR)}}


def judge(m: dict, s: dict) -> str | None:
    skip = set(s.get("skip", []))
    lo, hi = s["dur"]
    if not (lo <= m["duration_s"] <= hi + 1):
        return f"解码后时长 {m['duration_s']} s 不在范围里"
    if m["peak"] < 1e-3:
        return "几乎没有声音"
    if m["clip_fraction"] > CLIP_MAX:
        return f"削波 {m['clip_fraction']:.1%}"
    if "lowfreq" not in skip and m["energy_share"]["<100Hz"] > LOWFREQ_MAX:
        return f"能量的 {m['energy_share']['<100Hz']:.0%} 在 100 Hz 以下"
    if s["kind"] == "continuous" and m["active_fraction"] < ACTIVE_MIN:
        return f"活动比例 {m['active_fraction']} 低于 {ACTIVE_MIN}（大半时间没声音）"
    tail_s = m["tail_fraction"] * m["duration_s"]
    if s["kind"] == "event" and "tail" not in skip and m["tail_fraction"] > TAIL_MAX and tail_s > TAIL_MIN_S:
        return f"尾巴 {tail_s:.1f} s，占全长的 {m['tail_fraction']:.0%}"
    return None


def cmd_check(a: argparse.Namespace) -> None:
    if np is None:
        sys.exit("check 要 numpy（pip install numpy）与 ffmpeg")
    cfg, sounds = load_spec(a.spec, a.only)
    out_dir = Path(a.out)
    cands = read(out_dir / "candidates.json")
    sel_p, chk_p = out_dir / "selection.json", out_dir / "checks.json"
    selection = read(sel_p) if sel_p.exists() else {}
    checks = read(chk_p) if chk_p.exists() else {}
    for key, s in sounds.items():
        if key not in cands:
            sys.exit(f"{out_dir / 'candidates.json'} 里没有 {key}，先跑 search")
        c = cands[key]
        rows = {r["id"]: r for r in c["candidates"]}
        checks[key], ok = {}, []
        for i in c["kept"]:
            try:
                m = measure(decode(out_dir / rows[i]["preview_file"]))
                m["rejected"] = judge(m, s)
            except (KeyError, OSError, subprocess.CalledProcessError) as e:      # 一条坏的不拖累别的
                m = {"rejected": f"预览缺了或解不出来（{type(e).__name__}）"}
            checks[key][str(i)] = m
            if m["rejected"] is None:
                ok.append(rows[i])
        files = []
        for r in ok[:cfg["n"]]:
            url = f"https://freesound.org/people/{r['username']}/sounds/{r['id']}/"
            files.append({"freesound_id": r["id"], "title": r["title"], "username": r["username"], "url": url,
                          "license": "CC0" if r["license"] == LICENSES["cc0"] else "CC-BY",
                          "credit": None if r["license"] == LICENSES["cc0"] else f"\"{r['title']}\" by {r['username']} ({url}), CC BY",
                          "file": r["preview_file"], "downloads": r["downloads"], "downloads_per_year": r["downloads_per_year"],
                          "rating": r["rating"], "n_ratings": r["n_ratings"], "uploaded": r["uploaded"], "score": r["score"],
                          "gear": r["gear"], "lowfi_but_trusted": r["lowfi_but_trusted"], "description": r["description"],
                          "checks": checks[key][str(r["id"])]})
        selection[key] = {"note": c["note"], "kind": c["kind"], "fetched": c["fetched"], "n_found": c["n_found"], "n_text_ok": c["n_ok"],
                          "n_previews": len(c["kept"]), "n_signal_ok": len(ok), "files": files}
        print(f"{key:16s} 预览 {len(c['kept']):2d} 条，过了量声音 {len(ok):2d} 条，取用 {len(files):2d} 条", flush=True)
        write(sel_p, selection)      # 每种声音做完就落盘
        write(chk_p, checks)
        table = ["| 声音 | 搜到 | 过了文字筛选 | 下载预览 | 过了量声音 | 取用 | 取用里排在最前的三条（编号 ↓下载量 ★评分(人数)） |", "|---|---|---|---|---|---|---|"]
        for k, g in selection.items():
            top = "；".join(f"{f['freesound_id']} ↓{f['downloads']} ★{f['rating']}({f['n_ratings']})" for f in g["files"][:3])
            table.append(f"| {g['note'] or k} | {g['n_found']} | {g['n_text_ok']} | {g['n_previews']} | {g['n_signal_ok']} | {len(g['files'])} | {top} |")
        (out_dir / "TABLE.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    by = sum(f["license"] == "CC-BY" for g in selection.values() for f in g["files"])
    print(f"清单 {sel_p}；表 {out_dir / 'TABLE.md'}；CC-BY 的 {by} 条用的时候要署名（selection.json 里每条的 credit）")


def main() -> None:
    ap = argparse.ArgumentParser(description="照「听过的人留下的信号」从 Freesound 挑参考录音")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("search", cmd_search), ("check", cmd_check)):
        p = sub.add_parser(name)
        p.add_argument("spec")
        p.add_argument("out")
        p.add_argument("--only", nargs="+", help="只做这几种声音")
        p.set_defaults(fn=fn)
        if name == "search":
            p.add_argument("--exclude", nargs="+", help="不要的 Freesound 编号：JSON 列表，或 {编号: 原因}")
            p.add_argument("--revet", action="store_true", help="不联网，用已有的候选重新按规则筛、排")
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

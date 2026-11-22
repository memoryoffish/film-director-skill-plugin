#!/usr/bin/env python3
"""Progress page for a film being made: every unit, every take as a playable video, what is happening now, money and
time so far. One local HTML file that reloads itself (not while a video is playing).

    python3 progress.py OUT_DIR --jobs DIR [DIR ...] [--remote HOST] [--cuts GLOB ...] [--local-cuts GLOB ...]
                        [--events progress.jsonl] [--story story.md] [--units units.json] [--order U1,U2,...]
                        [--title T] [--estimate-cny N]
                        [--price list|discount] [--every SECONDS]

--jobs: folders with wan.py job files (NAME.json + NAME.mp4; takes named <unit>_t<n>).
--remote: the jobs (and --cuts) live on this ssh host; job files are re-read each time, videos copied once.
--cuts: rough cuts / the film (newest first on the page); --local-cuts for files on this machine.
--story: the story in plain text or markdown (one-line logline, beats), shown at the top.
--units: JSON {"U1": "what this unit shows in the story", ...}, shown on each unit.
--events: one JSON object per line, appended by whoever makes the film:
    {"t": "15:02", "unit": "U2", "take": "U2_t1", "state": "pass|retake|check|note", "what": "第 1 次多了人声"}
--every: rebuild every N seconds until stopped (run it in tmux). Without it, build once.
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from budget import load as load_budget, unit_price  # noqa: E402

BAD = {"FAILED", "CANCELED", "UNKNOWN"}
TAKE = re.compile(r"^(?P<unit>.+)_t(?P<n>\d+)$")
STATE = {"pass": ("合格", "ok"), "retake": ("要重抽", "warn"), "check": ("检查中", "run"), "gen": ("生成中", "run"),
         "fail": ("失败", "bad"), "todo": ("待检查", "idle")}
MANIFEST = r"""
import glob, json, os, sys
out = []
for pat in json.loads(sys.argv[1]):
    for p in glob.glob(os.path.expanduser(pat), recursive=True):
        if os.path.isfile(p):
            st = os.stat(p); out.append([os.path.abspath(p), st.st_size, st.st_mtime])
print(json.dumps(out))
"""


def sh(cmd: list[str], data: bytes | None = None) -> bytes:
    return subprocess.run(cmd, input=data, stdout=subprocess.PIPE, check=True).stdout


def sync(host: str, patterns: list[str], media: Path, newest: int | None = None) -> dict[str, Path]:
    """Copy matching remote files into media/ (job json every time, videos when new or changed)."""
    files = json.loads(sh(["ssh", host, "python3", "-", shlex.quote(json.dumps(patterns))], MANIFEST.encode()))
    if newest:
        files = sorted(files, key=lambda f: f[2], reverse=True)[:newest]
    if not files:
        return {}
    root = os.path.commonpath([os.path.dirname(f[0]) for f in files])
    local, need = {}, []
    for path, size, _ in files:
        dst = media / os.path.relpath(path, root)
        local[path] = dst
        if path.endswith(".json") or not dst.exists() or dst.stat().st_size != size:
            need.append(os.path.relpath(path, root))
    if need:
        media.mkdir(parents=True, exist_ok=True)
        tar = sh(["ssh", host, "tar", "cf", "-", "-C", root, *need])
        sh(["tar", "xf", "-", "-C", str(media)], tar)
    return local


def jobs_from(paths: list[Path]) -> list[dict]:
    out = []
    for p in paths:
        if p.suffix != ".json":
            continue
        try:
            s = json.loads(p.read_text())
        except Exception:
            continue
        if not isinstance(s, dict) or not s.get("task_id") and not s.get("status"):
            continue
        m = TAKE.match(s.get("name", p.stem))
        unit, n = (m["unit"], int(m["n"])) if m else (s.get("name", p.stem), 1)
        mp4 = p.with_suffix(".mp4")
        out.append({"name": s.get("name", p.stem), "unit": unit, "n": n, "status": s.get("status", "?"),
                    "submitted": s.get("submitted_utc") or 0, "timing": s.get("timing") or {}, "usage": s.get("usage") or {},
                    "res": ((s.get("payload") or {}).get("parameters") or {}).get("resolution", "720P"),
                    "model": (s.get("payload") or {}).get("model") or "wan3.0-video",
                    "video": mp4 if mp4.exists() else None})
    return out


def read_events(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    ev = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            ev.append(json.loads(line))
        except Exception:
            continue
    return ev


def take_state(j: dict, ev: list[dict]) -> str:
    if j["status"] in BAD:
        return "fail"
    if j["status"] != "DOWNLOADED":
        return "gen"
    mine = [e for e in ev if e.get("take") == j["name"] and e.get("state") in STATE]
    if not mine and j.get("latest"):  # a verdict about the unit applies to its newest take
        mine = [e for e in ev if e.get("unit") == j["unit"] and not e.get("take") and e.get("state") in STATE]
    return mine[-1]["state"] if mine else "todo"


def minutes(j: dict) -> str:
    t = j["timing"]
    try:
        a = datetime.strptime(t["submit_time"][:19], "%Y-%m-%d %H:%M:%S")
        b = datetime.strptime(t["end_time"][:19], "%Y-%m-%d %H:%M:%S")
        return f"{(b - a).seconds / 60:.1f} 分钟"
    except Exception:
        return f"已等 {(time.time() - j['submitted']) / 60:.0f} 分钟" if j["submitted"] else ""


def rel(p: Path, out: Path) -> str:
    return html.escape(os.path.relpath(p, out))


def collect(host: str | None, patterns: list[str], media: Path, newest: int | None = None) -> list[Path]:
    if not patterns:
        return []
    if host:
        return list(sync(host, patterns, media, newest).values())
    return [Path(p) for pat in patterns for p in sorted(glob.glob(os.path.expanduser(pat), recursive=True))]


def build(a: argparse.Namespace) -> Path:
    out = Path(a.out).resolve()
    jobs = jobs_from(collect(a.remote, [str(Path(d) / x) for d in a.jobs for x in ("*.json", "*.mp4")], out / "media" / "jobs"))
    cuts = collect(a.remote, a.cuts or [], out / "media" / "cuts", newest=3) + collect(None, a.local_cuts or [], out)
    cuts = sorted({c for c in cuts if c.suffix == ".mp4" and c.exists()}, key=lambda c: c.stat().st_mtime, reverse=True)[:3]
    ev = read_events(Path(a.events) if a.events else None)
    data = load_budget()
    spent = sum((j["usage"].get("duration") or 0) * unit_price(data, j["model"], j["res"], a.price)
                for j in jobs if j["status"] == "DOWNLOADED")
    order = a.order.split(",") if a.order else []
    units: dict[str, list[dict]] = {}
    for j in sorted(jobs, key=lambda j: (order.index(j["unit"]) if j["unit"] in order else len(order), j["submitted"], j["n"])):
        units.setdefault(j["unit"], []).append(j)
    for u in units.values():
        u.sort(key=lambda j: j["n"])
        u[-1]["latest"] = True
    first = min((j["submitted"] for j in jobs if j["submitted"]), default=time.time())
    (out / "index.html").write_text(page(a, out, units, ev, cuts, spent, (time.time() - first) / 60), encoding="utf-8")
    return out / "index.html"


def page(a, out: Path, units: dict, ev: list[dict], cuts: list[Path], spent: float, elapsed: float) -> str:
    e = html.escape
    story = Path(a.story).read_text(encoding="utf-8").strip() if a.story and Path(a.story).exists() else ""
    udesc = json.loads(Path(a.units).read_text(encoding="utf-8")) if a.units and Path(a.units).exists() else {}
    recent = list({str(x.get('what', '')): x for x in ev}.values())[-4:][::-1]  # same sentence once
    now = "".join(f"<li><span class='t'>{e(str(x.get('t', '')))}</span> {e(str(x.get('what', '')))}</li>" for x in recent)
    est = f" / 估 ¥{a.estimate_cny:g}" if a.estimate_cny else ""
    pct = min(100, spent / a.estimate_cny * 100) if a.estimate_cny else 0
    rows = []
    for name, takes in units.items():
        last = takes[-1]
        st = take_state(last, ev)
        lab, cls = STATE[st]
        cells = []
        for j in takes:
            s = take_state(j, ev)
            notes = "".join(f"<li>{e(str(x.get('what', '')))}</li>" for x in [x for x in ev if x.get("take") == j["name"]][-3:])
            vid = (f"<video controls preload='metadata' src='{rel(j['video'], out)}#t=0.5'></video>" if j["video"]
                   else f"<div class='ph'>{e(STATE[s][0])}<br>{e(minutes(j))}</div>")
            cells.append(f"<figure class='{STATE[s][1]}'>{vid}<figcaption><b>{e(j['name'])}</b> · {e(STATE[s][0])} · "
                         f"{e(minutes(j))} · 计 {j['usage'].get('duration', '–')} 秒<ul>{notes}</ul></figcaption></figure>")
        unotes = "".join(f"<li>{e(str(x.get('what', '')))}</li>" for x in [x for x in ev if x.get("unit") == name and not x.get("take")][-3:])
        about = f"<p class='about'>{e(str(udesc.get(name, '')))}</p>" if udesc.get(name) else ""
        rows.append(f"<section class='unit'><h3><span class='chip {cls}'>{e(lab)}</span> {e(name)} <small>抽了 {len(takes)} 次</small></h3>{about}"
                    f"<ul class='un'>{unotes}</ul><div class='takes'>{''.join(cells)}</div></section>")
    strip = "".join(f"<span class='{STATE[take_state(t[-1], ev)][1]}'>{e(n)}</span>" for n, t in units.items())
    cutv = "".join(f"<figure class='cut'><video controls preload='metadata' src='{rel(c, out)}#t=3'></video><figcaption>{e(c.parent.name + '/' + c.name)} · "
                   f"{datetime.fromtimestamp(c.stat().st_mtime):%H:%M}</figcaption></figure>" for c in cuts)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>{e(a.title)} · 进度</title><style>
body{{margin:0;background:#121417;color:#e6e3dc;font:14px/1.55 -apple-system,"PingFang SC",sans-serif}}main{{max-width:1500px;margin:0 auto;padding:20px}}
h1{{font-size:22px;margin:0}}.meta{{color:#8d887e}}.bar{{height:8px;background:#2a2d33;border-radius:4px;width:320px;display:inline-block;vertical-align:middle}}
.bar i{{display:block;height:8px;border-radius:4px;background:#e0a45a;width:{pct:.0f}%}}.now{{background:#1b1e23;border-left:3px solid #6fa8ff;padding:8px 14px;margin:12px 0}}
.now ul{{margin:0;padding-left:18px}}.t{{color:#8d887e;margin-right:6px}}.strip{{display:flex;gap:3px;margin:10px 0}}.strip span{{padding:3px 8px;border-radius:3px;font-size:12px;background:#2a2d33}}
.ok{{--c:#4fbf80}}.warn{{--c:#e0a45a}}.run{{--c:#6fa8ff}}.bad{{--c:#e26a6a}}.idle{{--c:#777}}.strip span{{border-bottom:3px solid var(--c)}}
.chip{{font-size:12px;padding:1px 8px;border-radius:9px;border:1px solid var(--c);color:var(--c)}}.unit{{border-top:1px solid #2a2d33;padding:10px 0}}
h3{{margin:4px 0;font-size:15px}}small{{color:#8d887e;font-weight:400}}.takes{{display:flex;gap:12px;overflow-x:auto}}
figure{{margin:0;width:340px;flex:none;border-top:3px solid var(--c)}}video{{width:100%;background:#000;display:block}}
figcaption{{font-size:12.5px;color:#bdb8ae;padding:4px 2px}}figcaption ul,.un{{margin:2px 0;padding-left:16px;color:#d7d2c8}}
.ph{{height:191px;background:#1b1e23;display:flex;align-items:center;justify-content:center;text-align:center;color:#8d887e}}
.story{{background:#1b1e23;padding:8px 14px;margin:12px 0;border-left:3px solid #e0a45a}}.story summary{{cursor:pointer;font-weight:600}}
.story div{{white-space:pre-wrap;color:#d7d2c8;max-height:320px;overflow:auto;margin-top:6px}}.about{{margin:2px 0 6px;color:#e0c89a}}
.cuts{{display:flex;flex-wrap:wrap;gap:14px}}.cut{{width:460px;--c:#6fa8ff}}</style></head><body><main>
<h1>{e(a.title)} · 进度</h1><p class="meta">更新 {datetime.now():%H:%M:%S} · 开工 {elapsed:.0f} 分钟 · 花费 ¥{spent:.0f}{est}（{'原价' if a.price == 'list' else '折扣价'}）
<span class="bar"><i></i></span> · 放视频时不自动刷新</p>
{f'<details class="story" open><summary>故事</summary><div>{e(story)}</div></details>' if story else ''}
<div class="now"><b>现在</b><ul>{now or '<li>（还没有记录）</li>'}</ul></div>
<div class="strip">{strip}</div>{'<h2>剪出来的</h2><div class="cuts">' + cutv + '</div>' if cutv else ''}
<h2>各单元</h2>{''.join(rows)}</main><script>
setInterval(()=>{{if(![...document.querySelectorAll('video')].some(v=>!v.paused))location.reload()}},{max(15, a.every or 60) * 1000});
</script></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out"); ap.add_argument("--jobs", nargs="+", required=True); ap.add_argument("--remote")
    ap.add_argument("--cuts", nargs="*"); ap.add_argument("--local-cuts", nargs="*"); ap.add_argument("--events"); ap.add_argument("--story"); ap.add_argument("--units")
    ap.add_argument("--order"); ap.add_argument("--title", default="片子"); ap.add_argument("--estimate-cny", type=float)
    ap.add_argument("--price", default="list", choices=["list", "discount"]); ap.add_argument("--every", type=int)
    a = ap.parse_args()
    while True:
        try:
            print(datetime.now().strftime("%H:%M:%S"), build(a), flush=True)
        except subprocess.CalledProcessError as err:  # ssh dropped: keep the last page, try again next round
            print("sync failed:", err, flush=True)
        if not a.every:
            break
        time.sleep(a.every)


if __name__ == "__main__":
    main()

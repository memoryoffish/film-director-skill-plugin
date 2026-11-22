#!/usr/bin/env python3
"""展示台：一部片每一镜喂进去了什么、出来了什么，几部片做成一页。只读镜头清单和清单里写的媒体文件。

    python3 console.py <清单.shots.json…> OUT_DIR [--workflows DIR] [--title T] [--view console|graph]
                       [--compact] [--max-side N] [--no-encode]

清单：一部片一个，../formats/read_run.py 从运行目录读出来的（或拍片的 skill 自己写的），格式见
../formats/shots-manifest.md。页面用到清单里的这些：镜头表（name、t0、t1、what）、成片 video、每镜的 video
（name、prompt，另加的 sent、status、attempts），另加的片头几项（genre、model、previz、flag、recon、plan、seconds、
roles）、每镜的 feed_note、stills、named_stills、own_ref，和两张表 pictures、image_jobs。另加的几项都可以没有。

--workflows：../comfyui/scripts/shots2comfy.py 写工作流的目录（它的 --out，默认 <ComfyUI>/user/default/workflows/filmkit），
    里面一部片一个文件夹。给了才做「节点图」视图：每一镜那份工作流原样嵌进页面（认文件里 extra.filmkit 的 film、shot；
    同一镜有几份时，用 shots2comfy 写的、没人动过的那份），页面照它画，「导出 ComfyUI」下载的就是这一份。
    这一部片有哪一镜找不到工作流，这部片就不做节点图（打一行说缺哪几镜）。
--view：打开时先看哪个视图，console（展示台，默认）或 graph（节点图）。
--compact（精简，片子多、要少传文件时用）：成片每镜只抽中间一帧（也当时间线的小图），白模尾帧只在这一镜喂了尾帧时才用，
    图的长边上限 960（不精简时 1280）。--max-side 另设长边上限。
--no-encode：不把成片和预演转码进 OUT_DIR，数据里 film / previz 写 null。展示台嵌在别的页面里、视频另有地址时用
    （成片还是要能读到，用来抽帧）。

写出 OUT_DIR/index.html、OUT_DIR/data.json（页面里内嵌的数据，别的页面嵌展示台时读它）和 OUT_DIR/<film>/：
图转成 JPEG，成片每镜取头、中、尾三帧加一张小图（精简时只取中间一帧），成片和预演转成网页用的码率。
所有媒体都写成 <i data-k data-src>，发布时只需给 data-src 签名。重跑时已有的文件不重做。
节点图的数据（每部片的 graph 字段）：
    graph.wfz     各镜的 [文件名, 工作流全文]（第 i 个是第 i 镜），整个列表 JSON → gzip → base64；页面用浏览器自带的
                  DecompressionStream('gzip') 解
    graph.media   工作流里 FilmKitImage、FilmKitKeyframe 的 file（运行目录里的相对路径）→ 页面里的媒体名
    img[相对路径]  一张图：f = 页面里的媒体名；白模静帧另有 shot、end（a 首 / b 尾）、note（站位描述）
    key[关键帧名]  出图任务：rel、f、size、ins（喂给出图模型的图）、ok、use（当过哪几镜的首帧 / 尾帧 / 参考图）、
                  p（出图 prompt，keys 里已有时省掉）、takes（重画）
    job[任务名]    视频任务：first、last、refs、video（参考视频）、w（model、duration、seed、resolution、ratio、audio）、
                  shots（切成了哪几镜）、st（这一次的结果）、takes（重抽）
    shot[i]       wm：这一镜按镜头名的白模静帧（没喂进去的也记下，时间线下面「白模」那一行用）
    takes 每次：n 名字、used、st、err、seed、diff（和用上的那次比哪几项输入不一样）、was（改了的图原来是哪张）、why
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import gzip
import hashlib
import json
import pathlib
import re
import subprocess
import sys

SMALL = 240
SENT = ("prompt", "first_frame", "last_frame", "reference_images", "video", "reference_video", "name")   # 不是参数的几项
VIDEO = ["-c:v", "libx264", "-crf", "23", "-maxrate", "3M", "-bufsize", "6M", "-preset", "medium", "-threads", "12"]
AUDIO = ["-c:a", "aac", "-b:a", "160k"]
PICTURE = (".png", ".jpg", ".jpeg", ".webp")


def to_jpg(src: pathlib.Path, dst: pathlib.Path, side: int) -> None:
    from PIL import Image
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.thumbnail((side, side))
    im.save(dst, "JPEG", quality=82)


def grab(film: pathlib.Path, t: float, dst: pathlib.Path, width: int) -> None:
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(film), "-frames:v", "1",
                    "-vf", f"scale='min({width},iw)':-2", "-q:v", "3", str(dst)], check=True)


def probe(f: pathlib.Path) -> tuple[float, bool]:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", str(f)],
                       capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    return float(j["format"]["duration"]), any(s.get("codec_type") == "audio" for s in j.get("streams", []))


def encode(src: pathlib.Path, dst: pathlib.Path) -> None:
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".part.mp4")
    audio = AUDIO if probe(src)[1] else ["-an"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), *VIDEO, *audio, "-movflags", "+faststart", str(tmp)], check=True)
    tmp.rename(dst)


def stem(rel: str) -> str:
    return pathlib.PurePosixPath(rel).stem


def take(a: dict) -> dict:
    """清单里重抽 / 重画的一次 → 页面里的写法。"""
    return {"n": a["name"], "used": a["used"], "st": a.get("status"), "err": a.get("error"), "seed": a.get("seed"),
            "diff": a.get("diff") or [], "was": a.get("was") or {}, "why": a.get("why")}


def film_graph(m: dict, img, console_keys: dict) -> dict:
    """节点图的实体表，从清单里来：从每一镜的视频任务往上追（清单里 keyframe 为真的图是关键帧，再追它的出图输入），
    每样东西只存一份。img(相对路径) → 媒体名（同时排进转图队列）；console_keys：展示台已经记下 prompt 的关键帧。"""
    run, pics, ijobs = pathlib.Path(m["root"]), m.get("pictures") or {}, m.get("image_jobs") or {}
    film_model = re.split(r"[（(；;]", m.get("model", ""))[0].strip()
    G = {"img": {}, "key": {}, "job": {}, "shot": []}

    def add_img(rel: str) -> None:
        if rel in G["img"]:
            return
        e = {"f": img(rel)}
        p = pics.get(rel) or {}
        if p.get("still"):
            e.update(shot=p["still"][0], end=p["still"][1])
            if p.get("note"):
                e["note"] = p["note"]
        G["img"][rel] = e

    def add_key(rel: str, user: tuple | None) -> None:
        """一张喂进去的图：是关键帧就记出图任务（再往上找它用的图），不是就只是一张图。"""
        k = stem(rel)
        if (pics.get(rel) or {}).get("keyframe"):
            e = G["key"].get(k)
            if e is None:
                j = ijobs[k]
                e = G["key"][k] = {"rel": rel, "f": img(rel), "size": j.get("size"), "ins": list(j["inputs"]), "ok": j.get("ok"), "use": []}
                if k not in console_keys:
                    e["p"] = j.get("prompt", "")
                if j.get("attempts"):
                    e["takes"] = [take(a) for a in j["attempts"]]
                for r in j["inputs"]:
                    add_key(r, None)
            if user and list(user) not in e["use"]:
                e["use"].append(list(user))
        else:
            add_img(rel)

    for s in m["shots"]:
        name, v = s["name"], s.get("video")
        G["shot"].append({"wm": list(s.get("named_stills") or [None, None])})
        if not v:
            continue
        jn, j = v["name"], v.get("sent") or {}
        for k, zh in (("first_frame", "首帧"), ("last_frame", "尾帧")):
            if j.get(k):
                add_key(j[k], (name, zh))
        for r in j.get("reference_images") or []:
            add_key(r, (name, "参考图"))
        if jn not in G["job"]:
            rv = j.get("video") or j.get("reference_video")   # 喂进视频模型的参考视频（只有真喂了才有）
            G["job"][jn] = {"first": j.get("first_frame"), "last": j.get("last_frame"), "refs": list(j.get("reference_images") or []),
                            "video": rv if rv and (run / rv).is_file() else None,
                            "w": {"model": j.get("model") or film_model, "duration": j.get("duration"), "seed": j.get("seed"),
                                  "resolution": j.get("resolution"), "ratio": j.get("ratio"), "audio": j.get("audio")},
                            "shots": [], "st": v.get("status")}
            if v.get("attempts"):
                G["job"][jn]["takes"] = [take(a) for a in v["attempts"]]
        G["job"][jn]["shots"].append(name)
    return G


def untouched(wf: dict) -> bool:
    """shots2comfy 写的、之后没人动过的那份：extra.filmkit.sha1 和去掉它以后的原文对得上。"""
    fk = dict(wf["extra"]["filmkit"])
    mark = fk.pop("sha1", None)
    rest = {**wf, "extra": {**wf["extra"], "filmkit": fk}}
    return mark == hashlib.sha1(json.dumps(rest, ensure_ascii=False, indent=1).encode("utf-8")).hexdigest()


def comfy_workflows(folder: pathlib.Path, m: dict, img) -> dict:
    """每一镜一份 ComfyUI 工作流，读 shots2comfy 写在 <folder>/<film>/ 下的文件，原文照搬（导出的和 ComfyUI 里的一个字节不差）。"""
    best: dict[str, tuple] = {}
    for p in sorted((folder / m["film"]).glob("*.json")):
        text = p.read_text(encoding="utf-8")
        try:
            wf = json.loads(text)
            film, shot = wf["extra"]["filmkit"]["film"], wf["extra"]["filmkit"]["shot"]
        except (ValueError, KeyError, TypeError):
            continue
        rank = 0 if untouched(wf) else 1          # 人在 ComfyUI 里存过的那份（「（人改过）」）排在后面
        if film == m["film"] and (shot not in best or rank < best[shot][0]):
            best[shot] = (rank, p.name, text, wf)
    missing = [s["name"] for s in m["shots"] if s["name"] not in best]
    if missing:
        print(f"{m['film']}: no ComfyUI workflow in {folder / m['film']} for {missing[:8]}{' …' if len(missing) > 8 else ''}; no graph view")
        return {}
    wfs, media = [], {}
    for s in m["shots"]:
        _, fname, text, wf = best[s["name"]]
        for n in wf["nodes"]:
            f = ((n.get("properties") or {}).get("filmkit") or {}).get("file")
            if f and f not in media and pathlib.PurePosixPath(f).suffix.lower() in PICTURE:
                media[f] = img(f)
        wfs.append([fname, text])
    raw = json.dumps(wfs, ensure_ascii=False, separators=(",", ":")).encode()
    return {"wfz": base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode(), "media": media}


def build(m: dict, out: pathlib.Path, pool: cf.Executor, enc: cf.Executor, futs: list, compact: bool, side: int,
          do_encode: bool, workflows: pathlib.Path | None) -> dict:
    run, key = pathlib.Path(m["root"]), m["film"]
    pics, ijobs = m.get("pictures") or {}, m.get("image_jobs") or {}
    film_src = pathlib.Path(m["video"])
    previz_src = pathlib.Path(m["previz"]) if m.get("previz") else None
    plan = bool(m.get("plan"))          # 还没开拍：没有成片，时间线按镜头表
    seconds = float(m.get("seconds") or m["shots"][-1]["t1"]) if plan else probe(film_src)[0]
    do_encode = do_encode and not plan
    done: dict[str, str | None] = {}

    def inrun(rel: str) -> str:
        """有的任务写的是绝对路径：换成运行目录里的相对路径，媒体名里不带机器上的路径。"""
        p = pathlib.PurePosixPath(rel)
        if not p.is_absolute():
            return rel
        try:
            return pathlib.Path(rel).resolve().relative_to(run).as_posix()
        except ValueError:
            return f"ext/{p.name}"

    def img(rel: str | None) -> str | None:
        """清单里的一张图 → 输出里的 JPEG（相对 OUT_DIR）；排进转换队列。"""
        if not rel:
            return None
        if rel not in done:
            src = run / rel
            done[rel] = None
            if src.is_file():
                done[rel] = f"{key}/{pathlib.PurePosixPath(inrun(rel)).with_suffix('.jpg')}"
                futs.append(pool.submit(to_jpg, src, out / done[rel], side))
        return done[rel]

    label = lambda rel: (pics.get(rel) or {}).get("label") or stem(rel)    # 清单没写说明的图，写文件名
    keys: dict[str, dict] = {}

    def key_job(rel: str) -> str | None:
        """这张图有出图任务（清单里的 made_by）时，第一次碰到就记下出图用的图和 prompt。"""
        k = (pics.get(rel) or {}).get("made_by")
        if k and k not in keys:
            j = ijobs[k]
            keys[k] = {"prompt": j.get("prompt", ""),
                       "in": [{"f": img(r), "l": f"图{i + 1} {label(r)}"} for i, r in enumerate(j["inputs"])]}
        return k

    def fed(rel: str | None, zh: str) -> dict | None:
        if not rel:
            return None
        return {"f": img(rel), "l": f"{zh} {stem(rel)}", "k": key_job(rel)}

    shots = []
    for s in m["shots"]:
        name, t0, t1 = s["name"], float(s["t0"]), float(s["t1"])
        v = s.get("video") or {}
        j = v.get("sent") or {}
        tail = not compact or bool(j.get("last_frame"))
        first, last = fed(j.get("first_frame"), "首帧"), fed(j.get("last_frame"), "尾帧")
        refs = [{"f": img(r), "l": label(r), "k": key_job(r)} for r in j.get("reference_images") or []]
        a, b = s.get("stills") or [None, None]
        row = {"n": name, "t0": t0, "t1": t1, "what": s.get("what", ""), "feed": s.get("feed_note", ""), "job": v.get("name", ""),
               "model": j.get("model", ""), "dur": j.get("duration"), "seed": j.get("seed"), "vp": v.get("prompt", ""),
               "wm": [img(a), img(b) if tail else None],
               "first": first, "last": last, "refs": refs, "kref": s.get("own_ref"),
               "params": {k: x for k, x in j.items() if k not in SENT and not isinstance(x, (dict, list))},   # 发给视频模型的参数
               "rv": j.get("video") or j.get("reference_video") or None,      # 喂进视频模型的参考视频（相对路径）
               "film": [None, None, None], "th": f"{key}/film/{name}_t.jpg"}
        for k, t in enumerate((t0 + 0.12, (t0 + t1) / 2, t1 - 0.12)):
            if (compact and k != 1) or plan:
                continue
            rel = f"{key}/film/{name}_{k}.jpg"
            row["film"][k] = rel
            futs.append(pool.submit(grab, film_src, min(max(0.0, t), seconds - 0.05), out / rel, side))
        if plan:
            row["th"] = row["wm"][0]
        elif compact:
            row["th"] = row["film"][1]
        else:
            futs.append(pool.submit(grab, film_src, (t0 + t1) / 2, out / row["th"], SMALL))
        shots.append(row)

    if do_encode:
        futs.append(enc.submit(encode, film_src, out / key / "film.mp4"))
        if previz_src:
            futs.append(enc.submit(encode, previz_src, out / key / "previz.mp4"))
    graph = film_graph(m, img, keys) if workflows else None
    if graph:
        print(f"{key}: graph {len(graph['key'])} keyframes, {len(graph['job'])} video jobs, "
              f"{sum(1 for j in graph['job'].values() if j.get('takes'))} with retakes")
        graph.update(comfy_workflows(workflows, m, img))
    missing = [s["n"] for s in shots if not s["job"]]
    print(f"{key}: {len(shots)} shots, {len(keys)} keyframe jobs, no video job for: {missing or 'none'}")
    return {"key": key, "title": m.get("title", key), "genre": m.get("genre", ""), "model": m.get("model", ""),
            "seconds": round(seconds, 3), "film": f"{key}/film.mp4" if do_encode else None,
            "previz": f"{key}/previz.mp4" if do_encode and previz_src else None,
            "flag": m.get("flag"), "shots": shots, "keys": keys, "graph": graph,
            "note": m.get("recon"), "plan": plan, "roles": m.get("roles") or {}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", metavar="清单… OUT_DIR")
    ap.add_argument("--workflows", help="shots2comfy 写工作流的目录（里面一部片一个文件夹）；给了才做节点图")
    ap.add_argument("--title", default="展示台")
    ap.add_argument("--view", default="console", choices=("console", "graph"))
    ap.add_argument("--compact", action="store_true")
    ap.add_argument("--max-side", type=int)
    ap.add_argument("--no-encode", action="store_true")
    a = ap.parse_args()
    if len(a.paths) < 2:
        ap.error("give at least one manifest and OUT_DIR")
    *manifests, out = [pathlib.Path(p).expanduser().resolve() for p in a.paths]
    workflows = pathlib.Path(a.workflows).expanduser().resolve() if a.workflows else None
    side = a.max_side or (960 if a.compact else 1280)
    out.mkdir(parents=True, exist_ok=True)
    futs: list[cf.Future] = []
    with cf.ThreadPoolExecutor(8) as pool, cf.ThreadPoolExecutor(2) as enc:
        films = [build(json.loads(p.read_text(encoding="utf-8")), out, pool, enc, futs, a.compact, side, not a.no_encode, workflows)
                 for p in manifests]
        for f in futs:
            f.result()
    media = sorted({p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file() and p.suffix in (".jpg", ".mp4")
                    and not p.name.endswith(".part.mp4")})
    raw = json.dumps({"title": a.title, "compact": a.compact, "view": a.view, "films": films}, ensure_ascii=False)
    (out / "data.json").write_text(raw)
    data = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    page = (pathlib.Path(__file__).parent / "console_template.html").read_text()
    page = page.replace("<!--MEDIA-->", "".join(f'<i data-k="{m}" data-src="{m}"></i>' for m in media))
    page = page.replace("/*DATA*/{}", data)
    (out / "index.html").write_text(page)
    print(f"{len(films)} films, {len(media)} media files -> {out / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

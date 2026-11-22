#!/usr/bin/env python3
"""拍片运行目录 → 镜头清单。认识运行目录的只有这一个文件：ComfyUI 那一头（../comfyui/scripts/shots2comfy.py）和
网页查看器（../viewer/scripts/console.py）都只读它写出来的清单。

    python3 read_run.py CONFIG.json --out DIR [--films k1,k2]

CONFIG（路径相对 CONFIG 所在目录，可以用 ~）：
    {"films": [{"key": "zz_demo", "run": "runs/zz_demo",
                "film": "成片，默认 <run>/film.mp4", "previz": "白模预演，默认 <run>/previz.mp4",
                "flag": {"t": 9.5, "shots": ["S3"], "note": "这一处的问题，一句话"}}]}
    别的键（title、compact、view、graph、encode、max_side）是页面的设置，这里不读。
写出 DIR/<key>.shots.json，一部片一个。格式见 shots-manifest.md：ComfyUI 用的那几项和 shots2comfy.py 开头写的一样；
另加的几项（可以没有）只有网页查看器用。只用标准库。

运行目录里读这些（都只读）：
    meta.json        title, genre, model, seconds, recon（镜头表是重建的：从哪重建的）, plan（还没开拍）,
                     shots: [{name, t0, t1, what, feed, job / clip / source / src}]
    jobs/*.json      视频任务：prompt, first_frame, last_frame, reference_images, video / reference_video，其余是参数
    keys/<k>.json    关键帧的出图记录（job.images、job.prompt、job.size，ok）；没有就依次找 jobs_img/、imgjobs/、图旁边同名的 .json
    wm/**/<镜>_a.png 白模静帧（首），_b.png（尾）；wm/notes.json 站位描述 {"S3": …, "S3_end": …}（包在 {"notes": {…}} 里也认）
    refs/README.md   每张参考图是谁（「- `girl.png`：女孩，全身」）
    clips/results.jsonl 或 clips/<名>.json  每一次生成的结果（认重抽、报没报错）
    edl.json         剪辑表（运行目录、edit/、cut/ 或 work/ 下，可以没有）
一镜用哪条视频任务：这一镜的 job、clip、source、src、feed、name 里第一个是任务名的词；都没有再查剪辑表。

两套认法并存：ComfyUI 用的几项一套，网页查看器另加的几项一套。两边在几处宽窄不一样（哪张图算关键帧、
重抽怎么归、一次生成的结果怎么认、白模静帧怎么找），清单里各写各的，见 shots-manifest.md 的「两份事实宽窄不一样」一节。
这些都是按文件名和目录认的；认不出来的不写或写 null，不另外猜。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

# ---------- ComfyUI 用的几项 ----------
RETAKE = re.compile(r"(?<=\d)[rb]$|_[tv]\d+$|_B$")   # v3 → v3r、v4 → v4b、s5_t1 → s5_t2、s6_t1 → s6_v2、s7_B
KEY_REDRAW = re.compile(r"(?<=[ab])\d+$")              # k_s02_a → k_s02_a2
TOKEN = re.compile(r"[A-Za-z0-9_\-]+")
SHOT_FIELDS = ("job", "clip", "source", "src", "feed", "name")   # 这一镜用哪条视频任务：写任务名的字段，job 优先
OK_STATUS = {"DOWNLOADED", "SUCCEEDED", "SUCCESS", "DONE", "OK"}
BAD_STATUS = {"FAILED", "ERROR", "CANCELED", "CANCELLED", "TIMEOUT", "EXPIRED"}
WM_STILL = re.compile(r"(.+)_([ab])")                  # wm/S3_a.png：S3 开头那一帧的白模；_b 是结尾

# ---------- 网页查看器另加的几项 ----------
REF_DIRS = ("refs", "refs_img", "cast", "img", "images", "assets")         # 参考图（定妆、场景图）放的地方
KEY_DIR = re.compile(r"^(keys|kf\w*)$")                                   # 关键帧放的地方
REF_LIKE = re.compile(r"^(ref|cast|char|costume|style|look|plate)", re.I)  # 放在 keys/ 里的定妆图、场景图，看名字认
JOB_TAKE = re.compile(r"(?:_t\d+|_v\d+|_B|(?<=\d)[rb])$")   # v3r、v4b、s7_B、s5_t3、s6_v2 → 底名
KEY_TAKE = re.compile(r"(?<=[ab])\d+$")                      # k_s02_a2 → k_s02_a
WM_PATH = re.compile(r"^wm/(.+)_([ab])\.png$")
DIFF = ("prompt", "first_frame", "last_frame", "reference_images", "images", "duration", "seed", "model", "resolution", "ratio")


def load(p: pathlib.Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def stem(rel: str) -> str:
    return pathlib.PurePosixPath(rel).stem


def kind_of(rel: str) -> str:
    top = pathlib.PurePosixPath(rel).parts[0]
    return {"keys": "key", "wm": "wm", "refs": "ref"}.get(top, "img")


def belongs(key: str, shot: str) -> bool:
    """关键帧名里有这一镜的镜头名：k_s08_a、k_S3、k_S20b（S20 的尾帧）都算。"""
    return any(t == shot or t in (shot + "a", shot + "b") for t in key.split("_"))


def feed_of(j: dict) -> str:
    if j.get("reference_images") or j.get("video") or j.get("reference_video"):
        return "R2V"
    if j.get("first_frame") and j.get("last_frame"):
        return "FLF2V"
    return "I2V" if j.get("first_frame") else "T2V"


def edl_jobs(run: pathlib.Path, names: set, jobs: dict) -> dict:
    """镜头名 → 视频任务，从剪辑表里找：哪种格式都行（一条是 dict 或 list），一条里有一项等于镜头名、有一个词是任务名就算。"""
    out = {}
    for p in (run / "edl.json", run / "edit" / "edl.json", run / "cut" / "edl.json", run / "work" / "edl.json"):
        d = load(p)
        rows = d if isinstance(d, list) else next((d[k] for k in ("shots", "clips", "edl", "items")
                                                    if isinstance(d, dict) and isinstance(d.get(k), list)), [])
        for e in rows:
            vals = [str(v) for v in (e.values() if isinstance(e, dict) else e if isinstance(e, list) else [])]
            shot = next((v for v in vals if v in names), None)
            job = next((t for v in vals for t in TOKEN.findall(v) if t in jobs), None)
            if shot and job:
                out.setdefault(shot, job)
    return out


class Run:
    """一部片的运行目录：镜头表、视频任务、关键帧任务、每一次生成的结果。"""

    def __init__(self, cfg: dict, base: pathlib.Path):
        path = lambda p: (base / pathlib.Path(p).expanduser()).resolve()
        self.key = cfg["key"]
        self.dir = path(cfg["run"])
        self.film = path(cfg["film"]) if cfg.get("film") else self.dir / "film.mp4"
        self.meta = load(self.dir / "meta.json") or {}
        self.shots = self.meta.get("shots", [])
        self.jobs: dict[str, dict] = {}
        self.job_names: list[str] = []
        for p in sorted((self.dir / "jobs").glob("*.json")):
            j = load(p)
            if isinstance(j, dict) and "prompt" in j:
                self.job_names.append(p.stem)
                self.jobs.setdefault(p.stem, j)
                self.jobs.setdefault(j.get("name") or p.stem, j)
        # 这一镜的 job、clip、source、src、feed、name 里第一个是任务名的词；都没有再查剪辑表（edl.json）
        edl = edl_jobs(self.dir, {s["name"] for s in self.shots}, self.jobs)
        self.shot_job = [next((t for k in SHOT_FIELDS for t in TOKEN.findall(str(s.get(k) or "")) if t in self.jobs), None)
                         or edl.get(s["name"]) for s in self.shots]
        self.used_jobs = {j for j in self.shot_job if j}
        self.results, self.order = self._results()
        self._keys: dict[str, dict | None] = {}
        self.key_files = {p.stem for p in (self.dir / "keys").glob("*.png")}
        self.referenced = self._referenced()
        # 每张图被哪一镜的视频任务直接用、当什么用：{相对路径: [(镜头名, 首帧/尾帧/参考图), …]}
        self.use: dict[str, list[tuple[str, str]]] = {}
        for s, jn in zip(self.shots, self.shot_job):
            j = self.jobs.get(jn) or {}
            for r, role in ((j.get("first_frame"), "首帧"), (j.get("last_frame"), "尾帧"),
                            *((x, "参考图") for x in j.get("reference_images") or [])):
                if r:
                    self.use.setdefault(r, []).append((s["name"], role))

    def _results(self) -> tuple[dict[str, bool | None], dict[str, int]]:
        res: dict[str, bool | None] = {}
        order: dict[str, int] = {}
        rp = self.dir / "clips" / "results.jsonl"
        if rp.is_file():
            for i, line in enumerate(rp.read_text(encoding="utf-8").splitlines()):
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("name"):
                    res[d["name"]] = bool(d.get("ok"))
                    order.setdefault(d["name"], i)
        for p in sorted((self.dir / "clips").glob("*.json")):
            d = load(p)
            if isinstance(d, dict) and d.get("status") and p.stem not in res:
                st = str(d["status"]).upper()
                res[p.stem] = True if st in OK_STATUS else False if st in BAD_STATUS else None
                order.setdefault(p.stem, len(order) + 10_000)
        return res, order

    def key_job(self, name: str) -> dict | None:
        """关键帧是怎么出的：{images, prompt, size}；不是生成的（比如从片子里抽的帧）返回 None。"""
        if name not in self._keys:
            d = load(self.dir / "keys" / f"{name}.json")
            j = d.get("job", d) if isinstance(d, dict) else None
            if not (isinstance(j, dict) and j.get("images")):
                j = load(self.dir / "jobs_img" / f"{name}.json")
            self._keys[name] = j if isinstance(j, dict) and j.get("images") else None
        return self._keys[name]

    def _referenced(self) -> set[str]:
        """被哪个视频任务或关键帧任务用到过的文件（相对路径）。没用到的关键帧就是重画前的那张。"""
        out = set()
        for j in self.jobs.values():
            out.update(x for x in (j.get("first_frame"), j.get("last_frame"), *(j.get("reference_images") or [])) if x)
        for name in self.key_files:
            out.update((self.key_job(name) or {}).get("images") or [])
        return out

    def takes(self, job: str) -> list[list]:
        """这条视频任务一共生成了几次：[[名字, 成没成, 用没用上], …]，按生成先后排。"""
        base = RETAKE.sub("", job)
        group = [n for n in self.job_names if RETAKE.sub("", n) == base and (n == job or n not in self.used_jobs)]
        if self.results:
            group = [n for n in group if n in self.results or n == job]
        group.sort(key=lambda n: (self.order.get(n, 1 << 30), n))
        return [[n, self.results.get(n), n == job] for n in group]

    def redraws(self, name: str) -> list[list]:
        """关键帧重画：同一张的前几版（没被任何任务用到），加上用上的这一版。"""
        base = KEY_REDRAW.sub("", name)
        alts = sorted(s for s in self.key_files if s != name and KEY_REDRAW.sub("", s) == base
                      and f"keys/{s}.png" not in self.referenced)
        return [[s, True, False] for s in alts] + [[name, True, True]] if alts else []

    def origin(self, rel: str, shot: str) -> str:
        """别的镜头的关键帧叫什么：「s01 的首帧」「S20 的尾帧」。是哪一镜的，先看名字对得上哪一镜（k_s10_a2 → s10），
        再看有没有镜头直接拿它当首帧、尾帧、参考图；都没有的是统一画面用的，叫「基准画面 · k_base」。"""
        named = [s["name"] for s in self.shots if s["name"] != shot and belongs(stem(rel), s["name"])]
        users = [u[0] for u in self.use.get(rel, []) if u[0] != shot]
        who = (named or users or [None])[0]
        if not who:
            return f"基准画面 · {stem(rel)}"
        role = next((r for s, r in self.use.get(rel, []) if s == who), "参考图")
        return f"{who} 的{'关键帧' if role == '参考图' else role}"

    def image(self, rel: str, shot: str) -> dict:
        """一张现成的图在这一镜的清单里怎么写。标题要短（比节点宽会被截掉）。"""
        k, nm = kind_of(rel), stem(rel)
        if k == "wm":
            m = WM_STILL.fullmatch(nm)
            return {"kind": k, "title": f"白模 · {m.group(1)} {'开头' if m.group(2) == 'a' else '结尾'}" if m else f"白模 · {nm}"}
        if k == "ref":
            return {"kind": k, "title": f"参考图 · {nm}", "short": nm}
        if k == "key":
            return {"kind": k, "title": f"{nm}（这一镜的，不是生成的）" if belongs(nm, shot) else self.origin(rel, shot)}
        return {"kind": k, "title": f"图 · {nm}"}

    def shot(self, i: int) -> dict:
        """第 i 镜在清单里的那一条。"""
        s, job = self.shots[i], self.shot_job[i]
        name = s["name"]
        out = {"name": name, "what": s.get("what", ""), "t0": float(s["t0"]), "t1": float(s["t1"])}
        j = self.jobs.get(job) if job else None
        if not j:
            return out
        video = {"name": job, "feed": feed_of(j)}
        if video["feed"] in ("I2V", "FLF2V"):
            video["first"] = j["first_frame"]
        if video["feed"] == "FLF2V":
            video["last"] = j["last_frame"]
        if video["feed"] == "R2V":
            video["refs"] = list(j.get("reference_images") or [])
            if j.get("video") or j.get("reference_video"):
                video["ref_video"] = j.get("video") or j.get("reference_video")
        fed = [video[k] for k in ("first", "last") if k in video] + video.get("refs", [])[:9]
        own = {r for r in fed if kind_of(r) == "key" and self.key_job(stem(r))}        # 这一镜自己的关键帧：展开一层
        if sum(1 for y in self.shot_job if y == job) > 1:
            # 一条生成切成几镜（分镜单元）：只展开名字对得上这一镜的那张（k_s08_a ↔ s08）；
            # 别的镜头的关键帧对这一次生成只是参考图，当输入图。名字都对不上就照旧全展开。
            own = {r for r in own if belongs(stem(r), name)} or own
        keyframes: dict[str, dict] = {}
        images: dict[str, dict] = {}

        def keyframe(rel: str) -> None:
            if rel in keyframes:
                return
            kj = self.key_job(stem(rel))
            keyframes[rel] = {"prompt": kj.get("prompt", ""), "size": kj.get("size") or "1536x864",
                              "inputs": list(kj["images"]), "takes": self.redraws(stem(rel))}
            for r in kj["images"]:
                keyframe(r) if r in own and r != rel else images.setdefault(r, self.image(r, name))

        for r in fed:
            keyframe(r) if r in own else images.setdefault(r, self.image(r, name))
        video.update(model=j.get("model") or self.meta.get("model", "").split("（")[0].strip(), prompt=j.get("prompt", ""),
                     duration=int(j.get("duration") or 5), seed=int(j.get("seed") or 0),
                     resolution=j.get("resolution") or "720P", ratio=j.get("ratio") or "16:9", audio=bool(j.get("audio", True)),
                     takes=self.takes(job), shots=[x["name"] for x, y in zip(self.shots, self.shot_job) if y == job])
        out.update(video=video, keyframes=keyframes, images=images)
        return out

    def head(self) -> dict:
        return {"film": self.key, "title": self.meta.get("title", self.key), "root": str(self.dir), "video": str(self.film)}

    def manifest(self) -> dict:
        """这部片的镜头清单（ComfyUI 用的那几项，格式见 shots-manifest.md 前半）。"""
        return {**self.head(), "shots": [self.shot(i) for i in range(len(self.shots))]}


# ---------- 网页查看器另加的几项 ----------

def roles(run: pathlib.Path) -> dict:
    """refs/README.md 里每张定妆图是谁：「- `girl.png`：女孩，全身」→ {"girl": "女孩，全身"}。"""
    try:
        text = (run / "refs" / "README.md").read_text(encoding="utf-8")
    except Exception:
        return {}
    return {pathlib.PurePosixPath(m.group(1)).stem: m.group(2).strip()
            for m in re.finditer(r"`([^`]+\.(?:png|jpe?g|webp))`\s*[：:]\s*(.+)", text)}


def pics_for_shots(prompt: str, clip: list) -> dict:
    """「图4、图5依次是镜头1、镜头2开头的画面参考」→ {clip[0]: 3, clip[1]: 4}（参考图的下标从 0 起）。"""
    m = re.search(r"((?:图\d+\s*[、，,和与及]?\s*)+)依次是((?:镜头\d+\s*[、，,和与及]?\s*)+)", prompt)
    if not m:
        return {}
    pics = [int(x) for x in re.findall(r"图(\d+)", m.group(1))]
    shots = [int(x) for x in re.findall(r"镜头(\d+)", m.group(2))]
    return {clip[k - 1]: p - 1 for p, k in zip(pics, shots) if 0 < k <= len(clip)}


def _base(name: str, pat: re.Pattern) -> str:
    while True:
        b = pat.sub("", name)
        if b == name or not b:
            return name
        name = b


def _diff(a: dict, b: dict) -> list[str]:
    return [k for k in DIFF if (a.get(k) or None) != (b.get(k) or None)]


def attempt(name: str, used: bool, rec: dict, job: dict, used_job: dict) -> dict:
    """重抽 / 重画的一次。was：改了的那几项输入原来是什么（只记图，不记 prompt）；why：为什么重抽，运行目录里没有记录，null。"""
    diff = [] if used else _diff(job, used_job)
    return {"name": name, "used": used, "status": rec.get("st"), "error": rec.get("err"), "seed": job.get("seed"), "diff": diff,
            "was": {k: job.get(k) for k in diff if k in ("first_frame", "last_frame", "reference_images", "images")}, "why": None}


def records(run: pathlib.Path) -> dict[str, dict]:
    """每一次视频生成的结果：clips/results.jsonl（name、ok、utc）或 clips/<名>.json（status、error）。"""
    rec: dict[str, dict] = {}
    rj = run / "clips" / "results.jsonl"
    if rj.is_file():
        for line in rj.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
            except Exception:
                continue
            if isinstance(d, dict) and d.get("name"):
                rec[d["name"]] = {"st": "ok" if d.get("ok") else "failed", "err": d.get("error"), "t": d.get("utc")}
    for p in sorted((run / "clips").glob("*.json")) if (run / "clips").is_dir() else []:
        d = load(p)
        if isinstance(d, dict) and d.get("status"):
            st = {"DOWNLOADED": "ok", "FAILED": "failed"}.get(d["status"], d["status"].lower())
            rec.setdefault(d.get("name") or p.stem, {"st": st, "err": d.get("error"), "t": d.get("submitted_utc")})
    return rec


def viewer_facts(run: Run, cfg: dict, base: pathlib.Path) -> tuple[dict, dict, list[dict], dict[str, dict]]:
    """清单里另加的几项：(片头的几项, 片尾的两张表 pictures、image_jobs, 每一镜的几项, 每条视频任务的几项)。"""
    path = lambda p: (base / pathlib.Path(p).expanduser()).resolve()
    rd, meta, jobs = run.dir, run.meta, run.jobs
    names = {s["name"] for s in run.shots}

    def inrun(rel: str) -> str:
        """有的任务写的是绝对路径：换成运行目录里的相对路径。"""
        p = pathlib.PurePosixPath(rel)
        if not p.is_absolute():
            return rel
        try:
            return pathlib.Path(rel).resolve().relative_to(rd).as_posix()
        except ValueError:
            return f"ext/{p.name}"

    # 一张关键帧当了哪几镜的首帧 / 尾帧：写进图的说明
    use: dict[str, list[str]] = {}
    for s, jn in zip(run.shots, run.shot_job):
        j = jobs.get(jn, {})
        for k, zh in (("first_frame", "首帧"), ("last_frame", "尾帧")):
            if j.get(k):
                use.setdefault(j[k], []).append(f"{s['name']} {zh}")

    def label(rel: str) -> str:
        """按图从哪来写：wm/ → 白模；名字像定妆图、场景图的 → 参考图；当过首帧尾帧的、keys/ 一类 → 关键帧；refs/ img/ 一类 → 参考图。"""
        p = pathlib.PurePosixPath(inrun(rel))
        top = p.parts[0] if len(p.parts) > 1 else ""
        u = use.get(rel, [])
        if top == "wm":
            return f"白模 {p.stem}"
        if REF_LIKE.match(p.stem):
            return f"参考图 {p.stem}"
        if u or KEY_DIR.match(top):       # 当过首帧、尾帧的（放在 img/ 里的也是），或者放在 keys/ 里
            return f"关键帧 {p.stem}" + (f"（{u[0]}{' 等' if len(u) > 1 else ''}）" if u else "")
        if top in REF_DIRS:
            return f"参考图 {p.stem}"
        return p.stem

    found: dict[str, dict] = {}     # 出图任务名 → 出图记录（job），按名字找到的

    def key_job(rel: str) -> str | None:
        """这张图有出图记录时返回出图任务名。按这个次序找：keys/、jobs_img/、imgjobs/、图旁边同名的 .json。"""
        k = stem(rel)
        if k not in found:
            j = None
            for q in (rd / "keys" / f"{k}.json", rd / "jobs_img" / f"{k}.json", rd / "imgjobs" / f"{k}.json",
                      (rd / inrun(rel)).with_suffix(".json")):
                d = load(q)
                j = d.get("job", d) if isinstance(d, dict) else None
                if isinstance(j, dict) and j.get("images"):
                    break
            if not (isinstance(j, dict) and j.get("images")):
                return None
            found[k] = j
        return k

    # 白模静帧：wm/ 下面（可以分子目录）叫 <镜>_a.png / _b.png 的那张；没有就用这一镜的关键帧出图时真用的那张白模
    wm_files: dict[str, str] = {}
    if (rd / "wm").is_dir():
        for q in sorted((rd / "wm").rglob("*.png")):
            wm_files.setdefault(q.name, q.relative_to(rd).as_posix())

    def key_shot(k: str) -> str | None:
        m = re.match(r"^[kK]_?(.+)$", k)
        if not m or REF_LIKE.match(k):
            return None
        return next((c for c in (m.group(1), re.sub(r"_?[ab]\d*$", "", m.group(1))) if c in names), None)

    def wm_still(name: str, end: str, kstems: list) -> str | None:
        if f"{name}_{end}.png" in wm_files:
            return wm_files[f"{name}_{end}.png"]
        for k in kstems:
            for q in (found.get(k) or {}).get("images") or []:
                if inrun(q).startswith("wm/"):
                    return q
        return None

    sent_pics: list[str] = []
    shot_x = []
    for s, jn in zip(run.shots, run.shot_job):
        name = s["name"]
        j = jobs.get(jn, {})
        fk = key_job(j["first_frame"]) if j.get("first_frame") else None
        lk = key_job(j["last_frame"]) if j.get("last_frame") else None
        rr = j.get("reference_images") or []
        rk = [key_job(r) for r in rr]
        sent_pics += [x for x in (j.get("first_frame"), j.get("last_frame"), *rr) if x]
        # 单元任务里哪张参考图是这一镜的画面：prompt 写了「图4、图5依次是镜头1、镜头2开头的画面」就照它；
        # 否则参考图里关键帧的个数和这条生成切成的镜头数一样时按次序对上；再不行按名字
        clip = [x["name"] for x, jn2 in zip(run.shots, run.shot_job) if jn and jn2 == jn]
        said = pics_for_shots(j.get("prompt") or "", clip)
        kix = [i for i, r in enumerate(rr) if rk[i] and not REF_LIKE.match(rk[i]) and pathlib.PurePosixPath(inrun(r)).parts[0] not in REF_DIRS]
        if name in said and said[name] < len(rr):
            kref = said[name]
        elif kix and len(kix) == len(clip):
            kref = kix[clip.index(name)]
        else:
            kref = next((i for i in kix if key_shot(rk[i]) == name), None)
        own = [rk[kref]] if kref is not None and rk[kref] else []
        x: dict = {}
        if "feed" in s:
            x["feed_note"] = s["feed"]
        stills = [wm_still(name, "a", [fk, *own]), wm_still(name, "b", [lk])]
        if any(stills):
            x["stills"] = stills
        named = [f"wm/{name}_{e}.png" if (rd / "wm" / f"{name}_{e}.png").is_file() else None for e in "ab"]
        if any(named):
            x["named_stills"] = named
        if kref is not None:
            x["own_ref"] = kref
        shot_x.append(x)

    # 节点图的读法：keys/ 下有出图记录（keys/ 或 jobs_img/ 里）的图才算关键帧，从各镜的视频往上追
    notes = load(rd / "wm" / "notes.json") or {}
    notes = notes["notes"] if isinstance(notes.get("notes"), dict) else notes
    rec = records(rd)
    kjobs: dict[str, dict] = {}
    for d in (rd / "keys", rd / "jobs_img"):
        for p in sorted(d.glob("*.json")) if d.is_dir() else []:
            if p.stem in kjobs:
                continue
            raw = load(p)
            j = raw.get("job", raw) if isinstance(raw, dict) else None
            if isinstance(j, dict) and j.get("images"):
                done = bool(raw.get("ok", True)) if raw is not j else (rd / "keys" / f"{p.stem}.png").is_file()
                kjobs[p.stem] = {**j, "ok": done}
    is_key = lambda rel: rel.startswith("keys/") and stem(rel) in kjobs
    reach: dict[str, None] = {}

    def walk(rel: str) -> None:
        k = stem(rel)
        if is_key(rel) and k not in reach:
            reach[k] = None
            for r in kjobs[k]["images"]:
                walk(r)

    for r in sent_pics:
        walk(r)

    # 重抽：同底名、没被别的镜头用上的视频任务；重画：同底名、哪一镜都没追到的关键帧
    used = {j for j in run.shot_job if j}
    all_jobs = sorted({j.get("name") or n for n, j in jobs.items()})
    video_x: dict[str, dict] = {}
    for jn in run.shot_job:
        if not jn or jn in video_x:
            continue
        e = video_x[jn] = {"sent": {k: v for k, v in jobs[jn].items() if k != "prompt"}}
        if (rec.get(jn) or {}).get("st") is not None:
            e["status"] = rec[jn]["st"]
        b = _base(jn, JOB_TAKE)
        fam = [n for n in all_jobs if _base(n, JOB_TAKE) == b and (n == jn or n not in used)]
        if len(fam) > 1:
            fam.sort(key=lambda n: (str((rec.get(n) or {}).get("t") or "~"), n))
            e["attempts"] = [attempt(n, n == jn, rec.get(n) or {}, jobs[n], jobs[jn]) for n in fam]

    # 两张表：用到的每一张图（直接喂进视频的，和出这些图用到的，一层层往上），每一个出图任务
    pictures: dict[str, dict] = {}
    todo = list(sent_pics)
    while todo:
        rel = todo.pop(0)
        if rel in pictures:
            continue
        e = pictures[rel] = {"label": label(rel)}
        k = key_job(rel)
        if k:
            e["made_by"] = k
            todo += found[k]["images"]
        if is_key(rel):
            e["keyframe"] = True
        m = WM_PATH.match(rel)
        if m:
            e["still"] = [m.group(1), m.group(2)]
            t = notes.get(m.group(1) if m.group(2) == "a" else f"{m.group(1)}_end")
            if t:
                e["note"] = t
    image_jobs: dict[str, dict] = {}
    for k in [*found, *reach]:
        if k in image_jobs:
            continue
        j = found.get(k) or kjobs[k]
        e = image_jobs[k] = {"prompt": j.get("prompt", ""), "inputs": list(j["images"])}
        if "size" in j:
            e["size"] = j["size"]
        if k in kjobs:
            e["ok"] = kjobs[k]["ok"]
        if k in reach:
            b = _base(k, KEY_TAKE)
            fam = sorted(n for n in kjobs if _base(n, KEY_TAKE) == b and (n == k or n not in reach))
            if len(fam) > 1:
                e["attempts"] = [attempt(n, n == k, {"st": "ok" if kjobs[n]["ok"] else "failed"}, kjobs[n], kjobs[k]) for n in fam]

    head: dict = {k: meta[k] for k in ("genre", "model") if k in meta}
    previz = path(cfg["previz"]) if cfg.get("previz") else rd / "previz.mp4"
    if previz.is_file():
        head["previz"] = str(previz)
    if "flag" in cfg:
        head["flag"] = cfg["flag"]
    if "recon" in meta:
        head["recon"] = meta["recon"]
    if meta.get("plan"):                # 还没开拍：没有成片，片长照镜头表写的
        head["plan"] = True
        if "seconds" in meta:
            head["seconds"] = meta["seconds"]
    who = roles(rd)
    if who:
        head["roles"] = who
    return head, {"pictures": pictures, "image_jobs": image_jobs}, shot_x, video_x


def manifest(cfg: dict, base: pathlib.Path) -> dict:
    """一部片的镜头清单：ComfyUI 用的几项在前，网页查看器另加的几项跟在各自那一层的后面。"""
    run = Run(cfg, base)
    m = run.manifest()
    head, tables, shot_x, video_x = viewer_facts(run, cfg, base)
    shots = []
    for s, x in zip(m["shots"], shot_x):
        if "video" in s:
            s = {**s, "video": {**s["video"], **video_x[s["video"]["name"]]}}
        shots.append({**s, **x})
    return {**run.head(), **head, "shots": shots, **tables}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("config")
    ap.add_argument("--out", required=True, help="清单写到这个目录：<key>.shots.json")
    ap.add_argument("--films", default="", help="只读这几部（key，逗号隔开）")
    a = ap.parse_args()
    conf_path = pathlib.Path(a.config).expanduser().resolve()
    conf = load(conf_path)
    films = set(filter(None, a.films.split(",")))
    out = pathlib.Path(a.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in conf["films"]:
        if films and f["key"] not in films:
            continue
        m = manifest(f, conf_path.parent)
        (out / f"{m['film']}.shots.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{m['film']}: {len(m['shots'])} shots, {sum(1 for s in m['shots'] if 'video' not in s)} without a video job, "
              f"{len(m['pictures'])} pictures, {len(m['image_jobs'])} image jobs")
        n += 1
    print(f"{n} manifests -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

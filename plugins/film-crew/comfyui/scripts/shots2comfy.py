#!/usr/bin/env python3
"""镜头清单 → ComfyUI：ComfyUI 这一头给拍片 skill 的接口。

    python3 shots2comfy.py <清单.json…> [--comfy <ComfyUI 目录>] [--url http://127.0.0.1:8188] [--shots S22,s16]
                           [--out <工作流目录>] [--index <回执>] [--prune] [--no-run]

拍片的 skill 把「每一镜用了什么、出了什么」写成一份清单交过来，它不用知道 ComfyUI 的任何事；这个脚本也不认识任何
拍片 skill 的目录结构，清单里写什么就放什么。人在 ComfyUI 里只看、只拿，不在里面改；要调整是告诉 agent，agent 用
自己的工具改完，把清单再交一次。ComfyUI 这一头不调任何生成接口，也不回头去动 skill 的文件。

清单（一部片一个文件；图的路径都相对 root）：
    {"film": "zz_demo",                     片的 key：ComfyUI 里的文件夹名、文件名都用它
     "title": "接口演示",                    可以不写
     "root": "<放图的目录>", "video": "<成片 mp4>",
     "shots": [{
       "name": "S3", "what": "她把杯子放到桌上", "t0": 8.0, "t1": 12.0,             t0、t1 是这一镜在成片里的起止（秒）
       "video": {                            这一镜的视频是怎么生成的；一条生成切成几镜时，几镜写同一条
         "name": "v3r", "feed": "I2V",       喂法：T2V 文生 / I2V 首帧 / FLF2V 首尾帧 / R2V 参考图
         "first": "keys/k_S3.png",           这种喂法用到的才写：first、last、refs（一列）、ref_video
         "model": "Wan 3.0", "prompt": "…", "duration": 5, "seed": 0, "resolution": "720P", "ratio": "16:9", "audio": true,
         "takes": [["v3", true, false], ["v3r", true, true]],          每一次生成 [名字, 成没成, 用没用上]；只有一次可以不写
         "shots": ["S3"]},                                              这条生成切成了哪几镜；只有这一镜可以不写
       "keyframes": {                        视频直接用的图里，这一镜自己出的关键帧：展开看它是怎么出的
         "keys/k_S3.png": {"prompt": "…", "size": "1536x864",
                           "inputs": ["wm/S3_a.png", "keys/k_base.png", "refs/girl_front.png"],
                           "takes": []}},                               重画过的写 [[名字, true, 用没用上], …]
       "images": {                           这一镜里其余每一张现成的图
         "wm/S3_a.png": {"kind": "wm", "title": "白模 · S3 开头"},
         "keys/k_base.png": {"kind": "key", "title": "基准画面 · k_base"},
         "refs/girl_front.png": {"kind": "ref", "title": "参考图 · girl_front", "short": "girl_front"}}}]}
    kind：wm 白模静帧（只属于这一镜，不进 Imported）、ref 参考图、key 别的镜头的关键帧或基准画面、img 其他。
    title 是这张图的节点标题；只喂给视频的图，标题前面加上它的角色（首帧 · …），有 short 就接 short。
    关键帧的名字是文件名去掉扩展名（k_S22）。清单里的名字就是 ComfyUI 里显示的名字，人说哪一镜、哪张图，说的就是它。

一镜的图，从左往右，到视频节点为止（它就是这一镜）：
  输入    这一镜的关键帧用到的图：白模静帧（白模 · S22 开头）、参考图、别的镜头的关键帧（S20 的尾帧，不再往上追）。FilmKitImage
  关键帧  这一镜的视频任务直接用的关键帧，标题先写角色（首帧 · k_S22）。FilmKitKeyframe，口按用了几张图来
  视频    按喂法一个节点：文生 / 首帧 / 首尾帧 / 参考图，口只有这种喂法要的；节点上直接放成片里这一镜的那几秒。
          标题写重抽：生成 N 次，K 次报错
  外面套一个框，框的标题就是这一镜：镜头名、起止、拍什么。
排法：输入图排成 1～3 列的格子（挑打开时放得最大的那种）| 这一镜的关键帧上下叠 | 视频；线只在两列之间的空当里走，
要越过一列时走横缝、两头放拐点（ComfyUI 自带的 reroute），不从节点背后过。
简单的一镜（首帧生视频、三张输入图）在 1600×900、左边栏开着时能按 100% 整个放下。

做四件事（留在 ComfyUI 里的，就是人做完这部片会留下、接手要用的那些）：
  1. 登记：每部片的 root、成片、关键帧文件写进 <comfy>/custom_nodes/comfyui_filmkit/filmkit_runs.json，节点包按 film 找文件。
  2. 出工作流：<out>/<film>/<镜头名 拍什么>.json（ComfyUI 的 UI 格式，0.4 版；Workflows 面板只列文件名，
     带上拍什么，一列下来就是镜头表）。--out 默认 <comfy>/user/default/workflows/filmkit。
     人在 ComfyUI 里改过、存过的工作流不盖、不删：每份工作流里记着自己的 sha1，对不上就是人动过的，
     挪成「<镜头名>（人改过）<拍什么>.json」留在旁边，并在最后报出来。
  3. 跨镜头反复用的图（参考图、基准画面）拷进 <comfy>/input 最上层，文件名 filmkit__<片>__…（见 flat()）：
     人在 Assets 面板的 Imported 里看得到，能插成 LoadImage 接着用。节点自己还是直接读 root。
     白模静帧不拷：它只是那一镜的输入，在那一镜的图里从节点的口就能拿；两百多张放进去，十来张参考图就被埋了。
  4. 把每一镜排队跑一遍（--url 那台 ComfyUI；回放，只读文件）：节点包把这一镜的关键帧和视频留在 <comfy>/output
     （filmkit__<片>__k_S22.png、…__S22.mp4），人在 Assets 面板的 Generated 里看得到。文件已经在、源头没变的不重写。
     倒着排（最后一镜先跑），面板里第一镜在最上面。ComfyUI 没开、或给了 --no-run 就不跑，只放文件。
  --prune（没给 --shots 时）：删掉这几部片在 out 里没人动过的旧工作流，和 input、output 里这几部片已经用不到的
  filmkit__ 文件。只动带 filmkit 记号的，人自己的文件不碰。
回执（--index，默认 <comfy>/user/filmkit_index.json）：每镜的工作流文件、喂法、节点数、打开时的缩放、
留在 output 里的文件名（kept）、这一次跑的结果（run）。只发几镜（--shots）时，别的镜头的回执留着不动。
<comfy> 不给就读环境变量 COMFYUI_DIR，--url 不给就读 COMFYUI_URL。只用标准库。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import struct
import sys
import time
import urllib.error
import urllib.request
import uuid

# 喂法 → 节点类型、标题里的叫法、这种喂法的口（[接口名, 中文名, 类型]；autogrow 的口另算）
FEEDS = {
    "T2V": ("FilmKitT2V", "文生视频"),
    "I2V": ("FilmKitI2V", "首帧生视频"),
    "FLF2V": ("FilmKitFLF2V", "首尾帧生视频"),
    "R2V": ("FilmKitR2V", "参考图生视频"),
}
# 节点颜色用 ComfyUI 自带的那几种（标题栏 color、底 bgcolor）：白模蓝、参考紫、关键帧黄、视频绿
COLOR = {"wm": ("#223", "#335"), "ref": ("#323", "#535"), "key": ("#432", "#653"), "img": ("#222", "#333"),
         "job": ("#232", "#353")}
TITLE = 30                                             # 节点标题栏的高度，画在节点位置的上面
GAP_X, GAP_Y, GAP_LEAF = 64, 44, 44                    # 两列之间、上下两个节点之间（含下面那个的标题栏）、格子里两列图之间
LEAF_W, KEY_W, JOB_W = 210, 320, 400                   # 带控件的节点前端最窄给 210
PROMPT_H = {"key": 112, "job": 132}                    # 提示词框的高度，和 web/filmkit.js 里定的一样
MEDIA_MARGIN, PORTRAIT_CAP = 6, 0.8                    # 图、视频四周留的边；竖图最高到宽的 0.8 倍。也和 filmkit.js 一样
LANE, LANE_PAD, ROUTE_PAD = 9, 14, 14                  # 并排两条线隔多远；一条横缝上下留多少；拐点离它绕过的那一列多远
PAD = 14
GROUP_FONT = (24, 20, 18, 16)
GROUP_COLOR = "#8AA"
# 1600×900 的窗口、左边栏开着时，画布上看得见的那一块（x, y, 宽, 高）：存进工作流的视图按它算。
# 装了节点包的前端打开时会按实际窗口重新摆一次（web/filmkit.js 的 fitShot）。
VIEW = (380, 90, 1208, 798)


def load(p: pathlib.Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def stem(rel: str) -> str:
    return pathlib.PurePosixPath(rel).stem


def flat(film: str, rel: str) -> str:
    """我们放进 ComfyUI 的 input、output 目录的文件叫什么：filmkit__<片>__<运行目录里的相对路径，/ 换成 __>。
    节点包留在 output 里的也是这个规矩（filmkit__<片>__k_S22.png、filmkit__<片>__S22.mp4，见 kept_names()）。

    带 filmkit__ 记号：清理时只动带记号的，碰不到人自己的文件。
    摊平放在最上层：LoadImage / LoadVideo 的下拉列表只列最上层的文件，前端（1.59）拿值去对这个列表，对不上就报
    「Missing Inputs：A required media input has no file selected」；资产系统开着时，把 Assets 卡片插成节点还会丢掉子目录。"""
    return f"filmkit__{film}__{rel.replace('/', '__')}"


def clock(t: float) -> str:
    m, s = divmod(max(0.0, t), 60)
    return f"{int(m)}:{s:04.1f}"


def takes_note(takes: list[list], verb: str) -> str:
    """重抽在 ComfyUI 里画不出线，写进标题：「 · 生成 3 次，1 次报错」。只有一次就不写。"""
    if len(takes) < 2:
        return ""
    bad = sum(1 for t in takes if t[1] is False)
    return f" · {verb} {len(takes)} 次" + (f"，{bad} 次报错" if bad else "")


def image_size(p: pathlib.Path) -> tuple[int, int]:
    """图的宽高，只读文件头（PNG、JPEG）；读不出来按 16:9 算。排版要用：节点按图的比例定高，不留白边。"""
    try:
        with p.open("rb") as f:
            head = f.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    marker, size = struct.unpack(">HH", f.read(4))
                    if 0xFFC0 <= marker <= 0xFFCF and marker not in (0xFFC4, 0xFFC8, 0xFFCC):
                        h, w = struct.unpack(">xHH", f.read(5))
                        return w, h
                    f.seek(size - 2, 1)
    except (OSError, struct.error):
        pass
    return 16, 9


def shot_graph(film: dict, shot: dict) -> dict:
    """清单里的一镜 → 一镜的图：{nodes: {id: node}}。node = {kind, type, title, widgets, inputs, outputs, props, wh}。

    inputs = [[接口名, 中文名, 类型, 来源节点 id 或 None], …]，次序就是节点上口的次序。
    同一张图只放一个节点，喂了几处就连几根线；摆在哪、线怎么走是 layout() 的事。"""
    key, root = film["film"], pathlib.Path(film["root"])
    name, t0, t1 = shot["name"], float(shot["t0"]), float(shot["t1"])
    nodes: dict[str, dict] = {}
    v = shot.get("video")
    feed = v["feed"] if v else None
    images, own = shot.get("images") or {}, shot.get("keyframes") or {}             # own：这一镜自己的关键帧，展开一层
    fed: list[tuple[str, str]] = []                                               # 视频任务直接用的图：[(相对路径, 角色)]，按口的次序
    if feed in ("I2V", "FLF2V"):
        fed.append((v["first"], "首帧"))
    if feed == "FLF2V":
        fed.append((v["last"], "尾帧"))
    if feed == "R2V":
        fed += [(r, f"参考图{k + 1}") for k, r in enumerate((v.get("refs") or [])[:9])]
    role_of: dict[str, str] = {}
    for r, role in fed:
        role_of.setdefault(r, role)
    for_keys = {x for kf in own.values() for x in kf["inputs"][:8]}               # 这一镜的关键帧用到的图

    def leaf(rel: str, role: str = "") -> str:
        """一张现成的图。标题要短（比节点宽会被截掉）：白模 · S3 开头、参考图 · girl、S20 的尾帧、基准画面 · k_base；
        只喂给视频任务的先写角色：首帧 · S21 的尾帧、参考图4 · s09 的关键帧（关键帧也用它的不写，角色看视频节点的口）。"""
        if rel in nodes:
            return rel
        im = images.get(rel) or {"title": f"图 · {stem(rel)}"}
        role = "" if rel in for_keys else role
        nodes[rel] = {"kind": im.get("kind", "img"), "type": "FilmKitImage",
                      "title": f"{role} · {im.get('short') or im['title']}" if role else im["title"],
                      "widgets": [key, rel], "inputs": [], "outputs": [["IMAGE", "图", "IMAGE"]],
                      "props": {"file": rel}, "wh": image_size(root / rel)}
        return rel

    def keyframe(rel: str) -> str:
        if rel in nodes:
            return rel
        kf = own[rel]
        redraws = kf.get("takes") or []
        n = {"kind": "key", "type": "FilmKitKeyframe",
             "title": f"{role_of[rel]} · {stem(rel)}{takes_note(redraws, '画了')}",
             "widgets": [kf.get("prompt", ""), kf.get("size") or "1536x864", key, stem(rel), "replay"],
             "inputs": [], "outputs": [["IMAGE", "关键帧", "IMAGE"]], "props": {"file": rel, "takes": redraws},
             "wh": image_size(root / rel)}
        nodes[rel] = n
        for k, r in enumerate(kf["inputs"][:8]):
            n["inputs"].append([f"images.image{k}", f"图{k + 1}", "IMAGE", keyframe(r) if r in own and r != rel else leaf(r)])
        # 能自动增减的口，前端总在末尾留一个空的；前端脚本打开时把它收起来
        n["inputs"].append([f"images.image{len(n['inputs'])}", f"图{len(n['inputs']) + 1}", "IMAGE", None])
        return rel

    if v:
        ntype, said = FEEDS[feed]
        job = v["name"]
        takes = v.get("takes") or []
        shots = v.get("shots") or [name]
        cut = f" · 一条切成 {len(shots)} 镜" if len(shots) > 1 else ""
        ins: list[list] = []
        for r, role in fed:
            slot = {"首帧": "first_frame", "尾帧": "last_frame"}.get(role) or f"refs.ref{len(ins)}"
            ins.append([slot, role, "IMAGE", keyframe(r) if r in own else leaf(r, role)])
        if feed == "R2V":
            ins.append([f"refs.ref{len(ins)}", f"参考图{len(ins) + 1}", "IMAGE", None])
            rv = v.get("ref_video")
            if rv and (root / rv).is_file():
                nodes[rv] = {"kind": "wm", "type": "LoadVideo", "title": f"参考视频 · {stem(rv)}",
                             "widgets": [flat(key, rv), "image"], "inputs": [],
                             "outputs": [["VIDEO", None, "VIDEO"]], "props": {"file": rv}, "wh": (16, 9)}
            ins.append(["ref_video", "参考视频", "VIDEO", rv if rv in nodes else None])
        nodes["job"] = {"kind": "job", "type": ntype, "title": f"{said} · {job}{takes_note(takes, '生成')}{cut}",
                        # 前端会在叫 seed 的参数后面自动加一个「生成后怎么换种子」的控件，widgets_values 里要给它占一格；
                        # 回放必须是 fixed，不然每排一次队种子就被前端改掉。
                        "widgets": [v.get("model") or "", v.get("prompt", ""),
                                    int(v.get("duration") or 5), int(v.get("seed") or 0), "fixed",
                                    v.get("resolution") or "720P", v.get("ratio") or "16:9", bool(v.get("audio", True)),
                                    key, job, "replay", t0, t1, name],
                        "inputs": ins, "outputs": [["VIDEO", "视频", "VIDEO"]],
                        "props": {"job": job, "feed": feed, "takes": takes, "shots": shots}, "wh": (16, 9)}
    return {"film": key, "title": film.get("title", key), "shot": name, "t0": t0, "t1": t1,
            "what": shot.get("what", ""), "job": v["name"] if v else None, "feed": feed, "nodes": nodes}


def media_h(width: int, wh: tuple[int, int], cap: float = PORTRAIT_CAP) -> int:
    """节点里那张图、那段视频占多高：和 web/filmkit.js 的 media() 同一个算法。"""
    inner = width - 2 * MEDIA_MARGIN
    return round(min(inner * wh[1] / wh[0], inner * cap)) + 2 * MEDIA_MARGIN


def size_of(n: dict) -> list[int]:
    """节点大小（不算标题栏），照前端实际排出来的量：口一行 20，第一个控件从 20×口数+6 开始，控件之间不留缝，底下留 8；
    藏起来的参数、没接线的可选口不占地方；图、视频按自己的比例定高，不留白边。"""
    t = n["type"]
    top = 20 * max(sum(1 for x in n["inputs"] if x[3]), len(n["outputs"]), 1) + 6
    if t == "FilmKitImage":
        return [LEAF_W, top + media_h(LEAF_W, n["wh"]) + 8]
    if t == "LoadVideo":
        return [260, 290]
    if t == "FilmKitKeyframe":
        return [KEY_W, top + PROMPT_H["key"] + media_h(KEY_W, n["wh"]) + 8]
    return [JOB_W, top + 24 + PROMPT_H["job"] + 24 + media_h(JOB_W, n["wh"], 9) + 8]    # model、提示词、duration、这一镜的视频


def place(g: dict, leaf_cols: int) -> dict:
    """输入图排成 leaf_cols 列的格子时，整镜怎么摆。返回 {pos, size, points, via, group, view}，不动 g。

    从左到右：输入图的格子 | 直接喂视频的那一列（这一镜的关键帧上下叠，首帧在上；只喂视频的图跟在下面）| 视频。
    线只在两列之间的空当里斜着走；要越过一列时走这一列里的一条横缝，两头各放一个拐点（ComfyUI 自带的 reroute）：
      · 格子里靠外的图：线从它这一行上面的缝里横着过去，过了最靠里的一列再散开去各个口；
      · 一张图既喂关键帧、又直接喂视频：去视频的那根从中间那一列的顶上或底下绕过去，哪边近走哪边；
      · 首帧派生出尾帧（同一列、往回接）：从两张关键帧中间的缝里横着穿回左边。"""
    N = g["nodes"]
    size = {nid: size_of(n) for nid, n in N.items()}
    users: dict[str, list[tuple[str, int]]] = {nid: [] for nid in N}
    for nid, n in N.items():
        for k, x in enumerate(n["inputs"]):
            if x[3]:
                users[x[3]].append((nid, k))
    to_job = lambda nid: min(k for d, k in users[nid] if d == "job")
    keys = [nid for nid, n in N.items() if n["type"] == "FilmKitKeyframe"]
    pictures = [nid for nid, n in N.items() if n["type"] in ("FilmKitImage", "LoadVideo")]
    # 中间那一列：这一镜的关键帧，加上只喂视频的图（没有关键帧时，图全进格子，格子就挨着视频）
    mid = sorted(keys + [nid for nid in pictures if keys and all(d == "job" for d, _ in users[nid])], key=to_job)
    rank = {nid: i for i, nid in enumerate(mid)}
    rank["job"] = len(mid)
    leaves = sorted((nid for nid in pictures if nid not in rank), key=lambda nid: min((rank[d], k) for d, k in users[nid]))
    cols = max(1, min(leaf_cols, len(leaves)))
    rows = [leaves[r:r + cols] for r in range(0, len(leaves), cols)]              # 一行里第 0 张最靠里（挨着中间那一列）
    leaf_w = max((size[nid][0] for nid in leaves), default=0)
    mid_w = max((size[nid][0] for nid in mid), default=0)
    pos: dict[str, list[float]] = {}
    points: dict[tuple, dict] = {}                                                # 拐点：键 → {pos, parent}
    via: dict[tuple[str, int], tuple] = {}                                        # (目标节点, 第几个口) → 这根线最后一个拐点的键

    def point(key: tuple, x: float, y: float, parent: tuple | None) -> tuple:
        points.setdefault(key, {"pos": [x, y], "parent": parent})
        return key

    # 输入图的格子
    grid_right = cols * leaf_w + (cols - 1) * GAP_LEAF if leaves else 0
    col_x = [grid_right - (c + 1) * leaf_w - c * GAP_LEAF for c in range(cols)]   # 第 0 列最靠里
    y, start = 0.0, {}                                                            # start：一张图的线从哪个拐点出发（靠里的没有）
    for row in rows:
        y += LANE_PAD + LANE * (len(row) - 1) if len(row) > 1 else 0              # 这一行上面给靠外的图留的横缝
        for c, nid in enumerate(row):
            pos[nid] = [col_x[c], y]
            if c:
                lane = y - TITLE - LANE_PAD / 2 - LANE * (c - 1)
                a = point(("row", nid, 0), col_x[c - 1] - ROUTE_PAD, lane, None)
                start[nid] = point(("row", nid, 1), grid_right + ROUTE_PAD, lane, a)
        y += max(size[nid][1] for nid in row) + GAP_Y
    # 中间那一列。先粗排一遍知道多高，好决定去视频的线从上面还是下面绕
    mid_x = grid_right + GAP_X if leaves else 0
    back = {i: [] for i in range(len(mid))}                                       # 第 i 个下面那条缝里，往回接的线
    cross = []                                                                    # 格子里的图直接喂视频：要越过中间这一列
    for nid in N:
        for d, k in users[nid]:
            if nid in rank and d in rank and d != "job":
                back[max(rank[nid], rank[d]) - 1].append((nid, d, k))
            elif nid in leaves and d == "job" and mid:
                cross.append((nid, d, k))
    tall = sum(size[nid][1] + GAP_Y for nid in mid)
    over = [c for c in cross if pos[c[0]][1] <= tall - pos[c[0]][1]]
    under = [c for c in cross if c not in over]
    y = LANE_PAD + LANE * len(over) if over else 0
    mid_top = y
    for i, nid in enumerate(mid):
        pos[nid] = [mid_x + mid_w - size[nid][0], y]                              # 窄的靠右：出口都在这一列的右边线上
        for n_th, (src, dst, k) in enumerate(back[i]):
            lane = y + size[nid][1] + LANE_PAD / 2 + LANE * n_th + 2
            a = point(("back", src, dst, k, 0), mid_x + mid_w + ROUTE_PAD, lane, None)
            via[(dst, k)] = point(("back", src, dst, k, 1), mid_x - ROUTE_PAD, lane, a)
        y += size[nid][1] + (LANE_PAD + LANE * len(back[i]) if back[i] else 0) + GAP_Y
    for n_th, (src, dst, k) in enumerate(over):
        lane = mid_top - TITLE - LANE_PAD / 2 - LANE * n_th
        a = point(("over", src, k, 0), mid_x - ROUTE_PAD, lane, start.get(src))
        via[(dst, k)] = point(("over", src, k, 1), mid_x + mid_w + ROUTE_PAD, lane, a)
    for n_th, (src, dst, k) in enumerate(under):
        lane = y - GAP_Y + LANE_PAD + LANE * n_th
        a = point(("under", src, k, 0), mid_x - ROUTE_PAD, lane, start.get(src))
        via[(dst, k)] = point(("under", src, k, 1), mid_x + mid_w + ROUTE_PAD, lane, a)
    for nid in leaves:                                                            # 其余的线：靠外的图从它那条横缝的出口出发
        for d, k in users[nid]:
            if nid in start:
                via.setdefault((d, k), start[nid])
    if "job" in N:
        pos["job"] = [(mid_x + mid_w + GAP_X) if mid else (grid_right + GAP_X if leaves else 0), 0.0]
    # 整镜的范围（节点连标题栏、拐点），挪到从 0 开始
    dx = -min([p[0] for p in pos.values()] + [q["pos"][0] for q in points.values()])
    dy = -min([p[1] - TITLE for p in pos.values()] + [q["pos"][1] - 6 for q in points.values()])
    for p in [*pos.values(), *(q["pos"] for q in points.values())]:
        p[0], p[1] = round(p[0] + dx, 1), round(p[1] + dy, 1)
    w = max([pos[nid][0] + size[nid][0] for nid in N] + [q["pos"][0] for q in points.values()])
    h = max([pos[nid][1] + size[nid][1] for nid in N] + [q["pos"][1] + 6 for q in points.values()])
    # 外面的框：标题就是这一镜（镜头名、起止、拍什么），字号按框的宽度挑，太长才截
    head = f"{g['shot']} · {clock(g['t0'])}–{clock(g['t1'])}"
    font, title = GROUP_FONT[-1], f"{head} · {g['what']}" if g["what"] else head
    for font in GROUP_FONT:
        if text_width(title, font) <= w + 2 * PAD - 16:
            break
    else:
        while len(title) > len(head) + 4 and text_width(title + "…", font) > w + 2 * PAD - 16:
            title = title[:-1]
        title += "…"
    box = [-PAD, -font - 16, w + 2 * PAD, h + font + 16 + PAD]
    vx, vy, vw, vh = VIEW
    scale = min(1.0, vw / box[2], vh / box[3])
    view = {"scale": round(scale, 4),
            "offset": [round((vx + (vw - box[2] * scale) / 2) / scale - box[0], 1), round(vy / scale - box[1], 1)]}
    return {"pos": pos, "size": size, "points": points, "via": via, "view": view,
            "group": {"title": title, "font_size": font, "bounding": [round(v, 1) for v in box]}}


def layout(g: dict) -> None:
    """定每个节点的 pos、size，线的拐点，整镜的框和打开时的视图。输入图排几列，挑打开时能放得最大的那种（一样大就少排几列）。"""
    best = None
    for leaf_cols in (1, 2, 3):
        cand = place(g, leaf_cols)
        if best is None or cand["view"]["scale"] > best["view"]["scale"] + 0.03:
            best = cand
    for nid, n in g["nodes"].items():
        n["pos"], n["size"] = best["pos"][nid], best["size"][nid]
    g.update(points=best["points"], via=best["via"], group=best["group"], view=best["view"])


def text_width(text: str, font: int) -> float:
    """标题大概多宽：汉字、全角标点算一个字宽，其余算 0.56 个。"""
    return sum(font * (1.0 if ord(ch) > 0x2E80 else 0.56) for ch in text)


def to_comfy(g: dict) -> dict:
    """抽象的图 → ComfyUI 的 UI 格式工作流（0.4 版）。"""
    N = g["nodes"]
    order = sorted(N, key=lambda n: (N[n]["pos"][0], N[n]["pos"][1]))
    ids = {nid: k + 1 for k, nid in enumerate(order)}
    links, out_links = [], {nid: [] for nid in N}
    for nid in order:
        for k, x in enumerate(N[nid]["inputs"]):
            if x[3]:
                links.append([len(links) + 1, ids[x[3]], 0, ids[nid], k, x[2]])
                out_links[x[3]].append(len(links))
    nodes = []
    for nid in order:
        n, t = N[nid], N[nid]["type"]
        node = {"id": ids[nid], "type": t, "pos": n["pos"], "size": n["size"], "flags": {}, "order": order.index(nid),
                "mode": 0, "title": n["title"], "inputs": [], "outputs": [],
                "properties": {"Node name for S&R": t, "filmkit": n["props"]}, "widgets_values": n["widgets"]}
        for k, x in enumerate(n["inputs"]):
            lid = next((L[0] for L in links if L[3] == ids[nid] and L[4] == k), None)
            node["inputs"].append({"name": x[0], "label": x[1], "type": x[2], "link": lid})
        for k, (oname, label, otype) in enumerate(n["outputs"]):
            o = {"name": oname, "type": otype, "links": (out_links[nid] if k == 0 else []) or None}
            if label:
                o["label"] = label
            node["outputs"].append(o)
        if n["kind"] in COLOR:
            node["color"], node["bgcolor"] = COLOR[n["kind"]]
        nodes.append(node)
    # 拐点（ComfyUI 自带的 reroute）：一串拐点靠 parentId 从目标往来源连；一根线记它最后经过的那个
    rid = {key: k + 1 for k, key in enumerate(g["points"])}
    through: dict[tuple, list[int]] = {key: [] for key in g["points"]}
    link_parent = []
    for L in links:
        key = g["via"].get((order[L[3] - 1], L[4]))
        if key:
            link_parent.append({"id": L[0], "parentId": rid[key]})
        while key:
            through[key].append(L[0])
            key = g["points"][key]["parent"]
    reroutes = [{"id": rid[key], "pos": q["pos"], "linkIds": through[key],
                 **({"parentId": rid[q["parent"]]} if q["parent"] else {})}
                for key, q in g["points"].items() if through[key]]
    group = {"id": 1, "color": GROUP_COLOR, "flags": {}, **g["group"]}
    extra = {"ds": g["view"], "filmkit": {**{k: g[k] for k in ("film", "title", "shot", "t0", "t1", "what", "job", "feed")},
                                           "view": g["view"]}}
    if reroutes:
        extra.update(reroutes=reroutes, linkExtensions=link_parent)
    return {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"filmkit/{g['film']}/{g['shot']}")), "revision": 0,
            "last_node_id": len(nodes), "last_link_id": len(links), "nodes": nodes, "links": links, "groups": [group],
            "config": {}, "extra": extra, "version": 0.4}


def file_name(shot: dict) -> str:
    """工作流的文件名：镜头名 + 拍什么（S3 她把杯子放到桌上.json）。ComfyUI 的 Workflows 面板只列文件名，
    这样一列下来就是一张镜头表（放不下的名字，选中时面板会自己滚动着显示）。"""
    what = re.sub(r'[\\/:*?"<>|\s]+', " ", shot.get("what") or "").strip()
    return f"{shot['name']} {what}".strip() + ".json"


def sealed(wf: dict) -> str:
    """工作流写成文本，里面记一笔这份文本的 sha1（extra.filmkit.sha1）。下回重出时，文件和这笔对得上，就是我们写的、
    没人动过，可以直接换掉；对不上，就是人在 ComfyUI 里改过、存过的（前端存的时候会留着 extra.filmkit），留着不盖。"""
    wf["extra"]["filmkit"].pop("sha1", None)
    mark = hashlib.sha1(json.dumps(wf, ensure_ascii=False, indent=1).encode("utf-8")).hexdigest()
    wf["extra"]["filmkit"]["sha1"] = mark
    return json.dumps(wf, ensure_ascii=False, indent=1)


def untouched(p: pathlib.Path) -> bool:
    """这个工作流文件是不是 shots2comfy 写的、之后没人动过。没有记号的（人自己存进来的、别处来的）一律不算。"""
    try:
        wf = json.loads(p.read_text(encoding="utf-8"))
        mark = wf["extra"]["filmkit"].pop("sha1")
    except (ValueError, KeyError, TypeError, AttributeError):
        return False
    return mark == hashlib.sha1(json.dumps(wf, ensure_ascii=False, indent=1).encode("utf-8")).hexdigest()


def aside(p: pathlib.Path) -> pathlib.Path:
    """人改过的那份挪到哪：同一个文件夹里「S3（人改过）她把杯子放到桌上.json」。记号紧跟镜头名：Workflows 面板里
    名字长了只显示开头，记号放末尾看不见；这样排序也还紧挨着原来那一镜。"""
    head, _, tail = p.stem.partition(" ")
    k = 1
    while True:
        q = p.with_name(f"{head}（人改过{'' if k == 1 else f' {k}'}）{tail}.json")
        if not q.exists():
            return q
        k += 1


def kept_names(film: str, g: dict) -> set[str]:
    """跑一遍这一镜，节点包留在 output 里的文件名（和节点包的 kept()、shot_paths() 一个规矩）。"""
    names = {flat(film, pathlib.PurePosixPath(n["props"]["file"]).name) for n in g["nodes"].values()
             if n["type"] == "FilmKitKeyframe"}
    if "job" in g["nodes"]:
        names.add(flat(film, re.sub(r"[^A-Za-z0-9_.\-]+", "_", g["shot"]) + ".mp4"))
    return names


def stage(film: dict, graphs: list[dict], comfy: pathlib.Path) -> tuple[int, set[str]]:
    """把这部片跨镜头反复用的图（参考图、基准画面）和参考视频拷进 ComfyUI 的 input 目录最上层（文件名见 flat()）：
    人在 Assets 面板的 Imported 里看得到，能插成 LoadImage 接着用；参考视频是 LoadVideo 要读的。
    不拷的两种：白模静帧（只是那一镜的输入，在那一镜的图里从节点的口拿；Assets 面板一次只加载最近 100 件、
    搜索也只搜加载出来的，两百多张静帧会把十来张参考图埋掉）；某一镜自己的关键帧（它是那一镜的产出，跑过就在 output 里）。

    只能拷，不能链：ComfyUI（0.46 起）校验路径时两边都取 realpath，指到 input 外面的软链一律当成不存在。
    返回 (新拷了几个, 这部片用到的文件名)。"""
    root = pathlib.Path(film["root"])
    nodes = [n for g in graphs for n in g["nodes"].values()]
    own = {n["props"]["file"] for n in nodes if n["type"] == "FilmKitKeyframe"}
    rels = {n["props"]["file"] for n in nodes
            if n["type"] == "LoadVideo" or (n["type"] == "FilmKitImage" and n["kind"] != "wm")} - own
    made, names = 0, set()
    for rel in sorted(rels):
        src, dst = root / rel, comfy / "input" / flat(film["film"], rel)
        names.add(dst.name)
        if not src.is_file():
            continue
        if dst.is_symlink():
            dst.unlink()
        st = src.stat()
        if dst.is_file() and dst.stat().st_size == st.st_size and int(dst.stat().st_mtime) == int(st.st_mtime):
            continue
        shutil.copy2(src, dst)
        made += 1
    return made, names


def register(films: list[dict], comfy: pathlib.Path) -> pathlib.Path:
    """节点包按 film 找文件用的登记表：root（run）、成片（film）、关键帧名 → 文件（keys）。"""
    reg = (comfy / "custom_nodes" / "comfyui_filmkit").resolve() / "filmkit_runs.json"
    data = load(reg) or {}
    for f in films:
        data[f["film"]] = {"run": str(f["root"]), "film": str(f["video"]),
                           "keys": {stem(rel): rel for s in f["shots"] for rel in (s.get("keyframes") or {})}}
    reg.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return reg


# 排队用的格式里，每种节点的参数叫什么（按 widgets_values 的次序；None 是前端自己加的那一格，不发）
VIDEO_WIDGETS = ("model", "prompt", "duration", "seed", None, "resolution", "ratio", "audio", "film", "name", "mode", "t0", "t1", "shot")
WIDGETS = {"FilmKitImage": ("film", "file"), "FilmKitKeyframe": ("prompt", "size", "film", "name", "mode"),
           "LoadVideo": ("file", None), **{t: VIDEO_WIDGETS for t, _ in FEEDS.values()}}


def api_prompt(wf: dict) -> dict:
    """UI 格式的工作流 → 排队用的格式（和前端 graphToPrompt 出的一样）：{节点号: {inputs, class_type, _meta}}。"""
    src = {L[0]: [str(L[1]), L[2]] for L in wf["links"]}
    out = {}
    for n in wf["nodes"]:
        ins = {k: val for k, val in zip(WIDGETS[n["type"]], n["widgets_values"]) if k}
        ins.update({i["name"]: src[i["link"]] for i in n["inputs"] if i.get("link") is not None})
        out[str(n["id"])] = {"inputs": ins, "class_type": n["type"], "_meta": {"title": n["title"]}}
    return out


def call(url: str, body: dict | None = None, timeout: float = 30):
    """对 ComfyUI 发一个请求（不走代理：服务器上常设着代理，本机地址也会被送过去）。返回 (状态码, 解出来的 JSON 或 None)。"""
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=timeout) as r:
            code, text = r.status, r.read()
    except urllib.error.HTTPError as e:
        code, text = e.code, e.read()
    try:
        return code, json.loads(text)
    except ValueError:
        return code, None


def run_shot(url: str, wf: dict, timeout: float = 300) -> str:
    """把一镜排进队列跑一遍，等它跑完。工作流原文跟着一起交（和前端点 Run 一样），节点包存文件时写进去。
    返回 "success"，或者一句出了什么错。"""
    code, r = call(url + "/prompt", {"prompt": api_prompt(wf), "extra_data": {"extra_pnginfo": {"workflow": wf}}})
    pid = (r or {}).get("prompt_id")
    if not pid:
        return f"not queued ({code}): {json.dumps(r, ensure_ascii=False)[:300]}"
    end = time.time() + timeout
    while time.time() < end:
        h = call(f"{url}/history/{pid}")[1] or {}
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "success":
                return "success"
            errs = [f"{m[1].get('node_type')}: {m[1].get('exception_message', '').strip()[:200]}"
                    for m in st.get("messages", []) if m[0] == "execution_error"]
            return f"{st.get('status_str', '?')}: {'; '.join(errs)}"
        time.sleep(0.2)
    return f"no result after {timeout:.0f}s"


def publish(films: list[dict], comfy: pathlib.Path, out: pathlib.Path | None = None, shots: set[str] | None = None,
            index_path: pathlib.Path | None = None, prune: bool = False, url: str = "", run: bool = True) -> int:
    """清单 → ComfyUI：登记、出工作流、放参考图、每镜跑一遍、写回执。返回退出码（有一镜没跑成是 1）。"""
    out = out or comfy / "user" / "default" / "workflows" / "filmkit"
    index_path = index_path or comfy / "user" / "filmkit_index.json"
    shots = shots or set()
    reg = register(films, comfy)
    index, queue, copied, pruned, by_hand, no_video = [], [], 0, 0, [], []
    for film in films:
        key = film["film"]
        folder = out / key
        folder.mkdir(parents=True, exist_ok=True)
        graphs, written, keep = [], set(), set()
        for s in film["shots"]:
            if shots and s["name"] not in shots:
                continue
            if not s.get("video"):                              # 还没有视频任务的镜头：没东西可放，不出工作流，最后报出来
                no_video.append(f"{key} {s['name']}")
                continue
            g = shot_graph(film, s)
            layout(g)
            graphs.append(g)
            keep |= kept_names(key, g)
            wf = to_comfy(g)
            p = folder / file_name(s)
            for old in folder.glob("*.json"):                  # 这一镜以前的文件（改过拍什么、旧的命名）；人动过的留着
                if old != p and (old.stem == s["name"] or old.stem.startswith(s["name"] + " ")) and untouched(old):
                    old.unlink()
            if p.exists() and not untouched(p):                # 人在 ComfyUI 里改过、存过：挪到旁边，不盖
                by_hand.append(p.rename(aside(p)))
            p.write_text(sealed(wf), encoding="utf-8")
            written.add(p)
            index.append({"film": key, "shot": s["name"], "file": str(p.relative_to(out)), "feed": g["feed"],
                          "nodes": len(wf["nodes"]), "links": len(wf["links"]), "scale": g["view"]["scale"],
                          "takes": len(g["nodes"].get("job", {}).get("props", {}).get("takes", [])),
                          "kept": sorted(kept_names(key, g))})
            if wf["nodes"]:
                queue.append((index[-1], wf))
        n, used = stage(film, graphs, comfy)
        copied += n
        if prune and not shots:
            for old in folder.glob("*.json"):                  # 已经没有的镜头留下的工作流；人动过的、人自己存进来的留着
                if old not in written and untouched(old):
                    old.unlink()
                    pruned += 1
            for sub, names in (("input", used), ("output", keep)):
                for f in (comfy / sub).glob(flat(key, "*")):
                    if f.name not in names:
                        f.unlink()
                        pruned += 1
    ran = run and bool(url) and call(url + "/system_stats", timeout=5)[0] == 200 if queue else False
    if ran:
        if copied:                                             # 新拷进 input 的图，让资产库现在就扫进去（没开资产系统时这个地址没有，不管）
            call(url + "/api/assets/seed?wait=true", {"roots": ["input"]}, timeout=120)
        for k, (entry, wf) in enumerate(reversed(queue)):      # 倒着跑：Assets 面板按文件时间从新到旧排，第一镜最后写、在最上面
            entry["run"] = run_shot(url, wf)
            if entry["run"] != "success" or (k + 1) % 20 == 0 or k + 1 == len(queue):
                print(f"  ran {k + 1}/{len(queue)}  {entry['film']} {entry['shot']}: {entry['run']}", flush=True)
    failed = [x for x in index if x.get("run") not in (None, "success")]
    # 回执：这一次没发的（别的片的；只发几镜时这部片别的镜头的）原来的回执留着
    receipt = load(index_path) or []
    if shots:
        fresh = {(x["film"], x["shot"]): x for x in index}
        receipt = [fresh.pop((x.get("film"), x.get("shot")), x) for x in receipt] + list(fresh.values())
    else:
        receipt = [x for x in receipt if x.get("film") not in {f["film"] for f in films}] + index
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
    n = [x["nodes"] for x in index] or [0]
    sc = sorted(x["scale"] for x in index) or [0]
    print(f"{len(films)} films, {len(index)} shots -> {out}  (nodes per shot max {max(n)}, mean {sum(n) / len(n):.1f}; "
          f"scale in the stored view min {sc[0]:.2f}, median {sc[len(sc) // 2]:.2f}, at 100%: {sum(1 for x in sc if x >= 1)}); "
          f"registered {reg}; copied {copied} new input files; pruned {pruned} stale files")
    print(f"ran {len(queue) - len(failed)}/{len(queue)} shots in ComfyUI ({url}); receipt {index_path}" if ran else
          f"not run in ComfyUI ({'--no-run' if not run else 'no shot with nodes' if not queue else 'not reachable: ' + (url or 'no --url')}): "
          f"workflows and pictures are in place, keyframes and clips appear in Assets after each shot is run once; receipt {index_path}")
    if no_video:
        print("no video job yet, no workflow written: " + ", ".join(no_video))
    for p in by_hand:
        print(f"changed by a person, kept as: {p}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("manifests", nargs="+", help="镜头清单，一部片一个 json")
    add_arguments(ap)
    a = ap.parse_args()
    films = [json.loads(pathlib.Path(m).expanduser().read_text(encoding="utf-8")) for m in a.manifests]
    return publish(films, **options(a))


def add_arguments(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--comfy", default=os.environ.get("COMFYUI_DIR"),
                    help="ComfyUI 目录（里面有 input/、custom_nodes/comfyui_filmkit）；不给就读环境变量 COMFYUI_DIR")
    ap.add_argument("--url", default=os.environ.get("COMFYUI_URL") or "http://127.0.0.1:8188", help="ComfyUI 的地址，跑每一镜用")
    ap.add_argument("--out", default="", help="工作流写到哪；默认 <comfy>/user/default/workflows/filmkit")
    ap.add_argument("--shots", default="", help="只发这几镜（镜头名，逗号隔开）")
    ap.add_argument("--index", default="", help="回执写到哪；默认 <comfy>/user/filmkit_index.json。别放进工作流目录，"
                    "不然会被当成一个工作流列出来")
    ap.add_argument("--prune", action="store_true", help="删掉这几部片没人动过的旧工作流，和 input、output 里已经用不到的 "
                    "filmkit__ 文件；人改过的工作流、人自己的文件不碰")
    ap.add_argument("--no-run", action="store_true", help="只放文件，不排队跑")


def options(a: argparse.Namespace) -> dict:
    if not a.comfy:
        sys.exit("where is ComfyUI? give --comfy <dir> or set COMFYUI_DIR")
    path = lambda p: pathlib.Path(p).expanduser().resolve()
    return {"comfy": path(a.comfy), "out": path(a.out) if a.out else None, "shots": set(filter(None, a.shots.split(","))),
            "index_path": path(a.index) if a.index else None, "prune": a.prune, "url": a.url.rstrip("/"), "run": not a.no_run}


if __name__ == "__main__":
    sys.exit(main())

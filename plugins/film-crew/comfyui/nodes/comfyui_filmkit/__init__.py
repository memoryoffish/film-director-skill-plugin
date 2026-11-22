"""拍片用的 ComfyUI 节点包。

一次拍片运行里由我们自己的工具做的几步，在 ComfyUI 里各是一个节点。视频生成按喂法分成四个，每个只带这种喂法要的口：

    FilmKitImage      运行目录里一张现成的图：白模静帧、参考图、别的镜头的关键帧
    FilmKitKeyframe   几张图（白模静帧、参考图、别的关键帧）+ 提示词 → 一张关键帧（拍片时由图像模型画出来，比如 gpt-image）
    FilmKitT2V        文生视频：只有提示词
    FilmKitI2V        首帧生视频：首帧
    FilmKitFLF2V      首尾帧生视频：首帧 + 尾帧
    FilmKitR2V        参考图生视频：几张参考图，可加一段参考视频

一镜的图到视频节点为止：它就是这一镜，节点上直接放成片里这一镜的那几秒（t0–t1）。

film、name、file、shot、执行方式、t0、t1 等是节点找文件用的，标成 advanced，前端脚本（web/filmkit.js）把它们藏起来；
节点上只露这一步要看的：输入、提示词、模型、时长。图和成片都由前端直接从运行目录取（/filmkit/file、/filmkit/film），
一打开就显示、视频自己播，不用先跑。

执行方式（mode）= replay：读运行目录里已经出好的文件，不调任何接口。跑一遍留下的，和人自己做完这一镜留下的一样，
人可以从 Assets 面板接着用（插成 LoadImage / LoadVideo、打开它的工作流、下载）：
    output/filmkit__<片>__<关键帧名>.png   这一镜的关键帧
    output/filmkit__<片>__<镜头名>.mp4     成片里这一镜
名字里是运行目录里的名字（k_S22、S22），人和 agent 说的是同一个；文件里带着这一镜的工作流（和 SaveImage / SaveVideo 一样），
拖回 ComfyUI 就能打开。喂进去的图不算这一镜产出的，不回预览（其中跨镜头用的参考图、基准画面，shots2comfy.py 放进 input，在 Imported 里）。
我们放进 ComfyUI 的文件都带 filmkit__ 记号、放在最上层：清理时只动带记号的，碰不到人自己的文件；
放最上层是因为资产系统开着时，前端（1.59）把 Assets 卡片插成节点会丢掉子目录，子目录里的文件插出来读不到。
文件已经在、源头没变，再跑就不重写。
资产系统开着（--enable-assets）时只写文件、不报给前端（不回 ui）：ComfyUI 跑完以后会自己扫一遍 output（最多 10 秒一次），
把没报过的文件登记上，开着的 Assets 面板自己多出卡片。这样登记的资产不挂在某一次 Run 上，一个文件一张卡片，
「Open as workflow」读的是文件里带的工作流，重启以后照样打得开。报了的话卡片挂在那一次 Run 上：前端只去问那次 Run 的记录
（重启就没了，不会退回去读文件），同一个文件每报一次还多一张卡片。资产系统没开时面板只列这次启动以后报过的，
那种情况下每次跑都照报。
generate 还没接，选了会报错。
文件按 film 在 filmkit_runs.json 里找（scripts/shots2comfy.py 照清单写；也可以用环境变量 FILMKIT_RUNS 指到别处）：
    {"zz_demo": {"run": "<清单里的 root，下面叫运行目录>", "film": "<成片 mp4>", "keys": {"k_S22": "keys/k_S22.png"}}}
节点包不认识任何拍片 skill 的目录结构，只认这张表和工作流里写的相对路径。
"""
from __future__ import annotations

import json
import os
import re

import numpy as np
import torch
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
from typing_extensions import override

import folder_paths
from comfy.cli_args import args
from comfy_api.latest import ComfyExtension, InputImpl, Types, io, ui

HERE = os.path.dirname(os.path.realpath(__file__))
WEB_DIRECTORY = "./web"          # web/filmkit.js：藏参数、口改中文名、打开就有图和视频、把整镜摆进窗口
MODES = ["replay", "generate"]
CATEGORY = "filmkit"


def runs_file() -> str:
    return os.environ.get("FILMKIT_RUNS") or os.path.join(HERE, "filmkit_runs.json")


def run_entry(film: str) -> dict:
    with open(runs_file(), encoding="utf-8") as f:
        entry = json.load(f).get(film)
    if not entry:
        raise ValueError(f"{runs_file()} 里没有 film={film!r}：先把这部片的清单交给 shots2comfy.py（它会登记）")
    return entry


def need_replay(mode: str) -> None:
    if mode != "replay":
        raise NotImplementedError("generate 还没接；先用 replay")


def replay_fingerprint(src: str, kept_path: str | None = None):
    """回放读的文件没变、留下的那件还在，就不重跑（和 LoadImage 一样看文件）：运行目录里的图重画了、成片重剪了，
    或者留在 output 里的那件被删了，再跑才会重读、重留。"""
    return [os.path.getmtime(src), kept_path is None or os.path.isfile(kept_path)]


def kept(film: str, name: str) -> tuple[str, ui.SavedResult]:
    """这一镜留在 ComfyUI 里的一件东西：output/filmkit__<片>__<name>（和 shots2comfy.py 的 flat() 一个规矩）。
    返回 (路径, 给前端的记录)。"""
    file = f"filmkit__{film}__{name}"
    return os.path.join(folder_paths.get_output_directory(), file), ui.SavedResult(file, "", io.FolderType.output)


def stale(path: str, src: str) -> bool:
    return not os.path.isfile(path) or os.path.getmtime(path) < os.path.getmtime(src)


def declare() -> bool:
    """留下的文件要不要报给前端（回 ui）：资产系统开着不报，让 ComfyUI 自己扫进库；没开才报。见文件头。"""
    return args.disable_assets


def workflow_meta(cls) -> dict:
    """和 SaveImage / SaveVideo 一样，把这一次的工作流写进文件：把图或视频拖回 ComfyUI 就能打开这一镜。"""
    if args.disable_metadata:
        return {}
    meta = dict(cls.hidden.extra_pnginfo or {})
    if cls.hidden.prompt is not None:
        meta["prompt"] = cls.hidden.prompt
    return meta


def image_tensor(path: str) -> torch.Tensor:
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return torch.from_numpy(np.asarray(im).astype(np.float32) / 255.0)[None, ...]


MEDIA = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".webm", ".mov"}


def run_file(film: str, rel: str) -> str:
    """运行目录里的一个文件（只认登记过的运行目录、只认图片和视频，路径不许跑出运行目录）。"""
    root = os.path.realpath(run_entry(film)["run"])
    path = os.path.realpath(os.path.join(root, rel))
    if os.path.commonpath((root, path)) != root or os.path.splitext(path)[1].lower() not in MEDIA:
        raise ValueError(f"{film}/{rel}：不在运行目录里，或不是图片、视频")
    return path


try:  # 前端脚本直接从这里取图和成片：节点一打开就有图、视频自己播，不用把东西拷进 input、temp
    from aiohttp import web
    from server import PromptServer

    @PromptServer.instance.routes.get("/filmkit/file")
    async def filmkit_file(request):
        try:
            path = run_file(request.query.get("film", ""), request.query.get("rel", ""))
        except Exception:
            return web.Response(status=404)
        return web.FileResponse(path) if os.path.isfile(path) else web.Response(status=404)

    @PromptServer.instance.routes.get("/filmkit/film")
    async def filmkit_film(request):
        """这部片的成片。视频节点从里面放这一镜的 t0–t1（浏览器按字节范围取，不用先裁出来）。"""
        try:
            path = run_entry(request.query.get("film", ""))["film"]
        except Exception:
            return web.Response(status=404)
        return web.FileResponse(path) if os.path.isfile(path) else web.Response(status=404)
except Exception:  # 不在 ComfyUI 里（比如单独导入做测试）就不挂
    pass


def run_inputs() -> list:
    return [io.String.Input("film", default="", advanced=True),
            io.String.Input("name", default="", advanced=True),
            io.Combo.Input("mode", options=MODES, default="replay", display_name="执行方式", advanced=True)]


class FilmKitImage(io.ComfyNode):
    @classmethod
    def fingerprint_inputs(cls, film: str = "", file: str = "", **_):
        return replay_fingerprint(run_file(film, file))

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="FilmKitImage",
            display_name="FilmKit 图",
            category=CATEGORY,
            description="运行目录里一张现成的图：白模静帧、参考图、别的镜头的关键帧。直接从运行目录读。",
            inputs=[io.String.Input("film", default="", advanced=True),
                    io.String.Input("file", default="", advanced=True)],
            outputs=[io.Image.Output(display_name="图")],
        )

    @classmethod
    def execute(cls, film: str, file: str) -> io.NodeOutput:
        return io.NodeOutput(image_tensor(run_file(film, file)))


def key_paths(film: str, name: str) -> tuple[str, str, ui.SavedResult]:
    # 关键帧的文件在哪，看登记表（清单里写的路径）；登记表里没有这一栏时，按 keys/<name>.png 找
    src = run_file(film, (run_entry(film).get("keys") or {}).get(name) or f"keys/{name}.png")
    return (src, *kept(film, os.path.basename(src)))


class FilmKitKeyframe(io.ComfyNode):
    @classmethod
    def fingerprint_inputs(cls, film: str = "", name: str = "", mode: str = "replay", **_):
        return replay_fingerprint(*key_paths(film, name)[:2]) if mode == "replay" else mode

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="FilmKitKeyframe",
            display_name="FilmKit 关键帧",
            category=CATEGORY,
            description="几张图 + 提示词 → 一张关键帧。提示词里的 Image 1/2/3 就是第 1/2/3 个口。"
                        "replay 读登记的那张关键帧，留一份在 output（filmkit__<片>__<文件名>）。",
            inputs=[
                io.Autogrow.Input("images", template=io.Autogrow.TemplatePrefix(
                    io.Image.Input("image", optional=True), prefix="image", min=1, max=8)),
                io.String.Input("prompt", multiline=True, default=""),
                io.String.Input("size", default="1536x864", advanced=True),
                *run_inputs(),
            ],
            outputs=[io.Image.Output(display_name="关键帧")],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, prompt: str, size: str, film: str, name: str, mode: str, images=None) -> io.NodeOutput:
        need_replay(mode)
        src, path, result = key_paths(film, name)
        if stale(path, src):
            meta = PngInfo()
            for k, v in workflow_meta(cls).items():
                meta.add_text(k, json.dumps(v))
            with Image.open(src) as im:                    # 像素原样，只多写一段工作流
                im.save(path, format="PNG", pnginfo=meta, compress_level=4)
        return io.NodeOutput(image_tensor(src), ui=ui.SavedImages([result]) if declare() else None)


def video_inputs() -> list:
    return [io.String.Input("model", default=""),
            io.String.Input("prompt", multiline=True, default=""),
            io.Int.Input("duration", default=5, min=1, max=60),
            io.Int.Input("seed", default=0, min=0, max=2**31 - 1, advanced=True),
            io.String.Input("resolution", default="720P", advanced=True),
            io.String.Input("ratio", default="16:9", advanced=True),
            io.Boolean.Input("audio", default=True, advanced=True),
            *run_inputs(),
            io.Float.Input("t0", default=0.0, min=0.0, step=0.001, advanced=True),
            io.Float.Input("t1", default=0.0, min=0.0, step=0.001, advanced=True),
            io.String.Input("shot", default="", advanced=True)]


def shot_paths(film: str, name: str, shot: str) -> tuple[str, str, ui.SavedResult]:
    """(成片, 这一镜留下的 mp4, 给前端的记录)。文件按镜头名叫（…__S22.mp4）：一条生成切成几镜时，每镜各是一段。"""
    return (run_entry(film)["film"], *kept(film, re.sub(r"[^A-Za-z0-9_.\-]+", "_", shot or name) + ".mp4"))


def replay_shot(cls, film: str, name: str, shot: str, mode: str, t0: float, t1: float) -> io.NodeOutput:
    """这一镜在成片里的那几秒：裁出来留在 output（filmkit__<片>__<镜头名>.mp4），交给下游的也是它。"""
    need_replay(mode)
    if t1 <= t0:
        raise ValueError(f"{name}：t1 要大于 t0（{t0}–{t1}）")
    film_path, path, result = shot_paths(film, name, shot)
    # 过期：成片比它新（重剪过），或者长度对不上（这一镜的起止改了）
    if stale(path, film_path) or abs(InputImpl.VideoFromFile(path).get_duration() - (t1 - t0)) > 0.2:
        cut = InputImpl.VideoFromFile(film_path).as_trimmed(t0, t1 - t0)
        if cut is None:
            raise ValueError(f"{name}：成片里裁不出 {t0}–{t1}")
        cut.save_to(path, format=Types.VideoContainer.MP4, codec=Types.VideoCodec.AUTO, metadata=workflow_meta(cls) or None)
    return io.NodeOutput(InputImpl.VideoFromFile(path), ui=ui.PreviewVideo([result]) if declare() else None)


# 喂法 → (节点名, 显示名, 说明, 这种喂法的口)
FEEDS = [
    ("FilmKitT2V", "FilmKit 文生视频", "只有提示词。", lambda: []),
    ("FilmKitI2V", "FilmKit 首帧生视频", "首帧 + 提示词。",
     lambda: [io.Image.Input("first_frame", display_name="首帧")]),
    ("FilmKitFLF2V", "FilmKit 首尾帧生视频", "首帧 + 尾帧 + 提示词。",
     lambda: [io.Image.Input("first_frame", display_name="首帧"), io.Image.Input("last_frame", display_name="尾帧")]),
    ("FilmKitR2V", "FilmKit 参考图生视频", "几张参考图（可加一段参考视频）+ 提示词。",
     lambda: [io.Autogrow.Input("refs", template=io.Autogrow.TemplatePrefix(
                  io.Image.Input("ref", optional=True), prefix="ref", min=1, max=9)),
              io.Video.Input("ref_video", display_name="参考视频", optional=True)]),
]


def video_node(node_id: str, display: str, desc: str, links) -> type[io.ComfyNode]:
    class Node(io.ComfyNode):
        @classmethod
        def fingerprint_inputs(cls, film: str = "", name: str = "", shot: str = "", mode: str = "replay", **_):
            return replay_fingerprint(*shot_paths(film, name, shot)[:2]) if mode == "replay" else mode

        @classmethod
        def define_schema(cls) -> io.Schema:
            return io.Schema(
                node_id=node_id, display_name=display, category=CATEGORY,
                description=desc + "一次生成调用，也是这一镜的终点。replay 交出成片里这一镜的 t0–t1，"
                                   "留一份在 output（filmkit__<片>__<镜头名>.mp4）。",
                inputs=[*links(), *video_inputs()],
                outputs=[io.Video.Output(display_name="视频")],
                hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
                is_output_node=True,
            )

        @classmethod
        def execute(cls, model: str, prompt: str, duration: int, seed: int, resolution: str, ratio: str,
                    audio: bool, film: str, name: str, mode: str, t0: float, t1: float, shot: str = "", **_) -> io.NodeOutput:
            return replay_shot(cls, film, name, shot, mode, t0, t1)

    Node.__name__ = Node.__qualname__ = node_id
    return Node


VIDEO_NODES = [video_node(*f) for f in FEEDS]


class FilmKitExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [FilmKitImage, FilmKitKeyframe, *VIDEO_NODES]


async def comfy_entrypoint() -> FilmKitExtension:
    return FilmKitExtension()

# nodes：ComfyUI 节点包

`comfyui_filmkit/` 整个目录链进（或拷进）ComfyUI 的 `custom_nodes/`，重启 ComfyUI。日志里出现 `custom_nodes/comfyui_filmkit` 一行、`/object_info/FilmKitI2V` 取得到、`/extensions` 里有 `comfyui_filmkit/filmkit.js`，就是装上了。

| 节点 | 显示名 | 做什么 |
|---|---|---|
| FilmKitImage | FilmKit 图 | root 里一张现成的图（白模静帧、参考图、别的镜头的关键帧） |
| FilmKitKeyframe | FilmKit 关键帧 | 几张图 + 提示词 → 一张关键帧；口按用了几张来（图1、图2…） |
| FilmKitT2V | FilmKit 文生视频 | 只有提示词 |
| FilmKitI2V | FilmKit 首帧生视频 | 首帧 |
| FilmKitFLF2V | FilmKit 首尾帧生视频 | 首帧 + 尾帧 |
| FilmKitR2V | FilmKit 参考图生视频 | 几张参考图（参考图1、参考图2…），可加一段参考视频 |

四个视频节点是输出节点，也是一镜的终点：节点上直接放成片里这一镜的那几秒。

- `web/filmkit.js`：藏起找文件用的参数（film、name、shot、执行方式、seed、t0、t1……）；口改中文名、收起没接线的可选口；给图节点加 `<img>`、视频节点加 `<video>`（打开就有图、视频自己播），跑完以后不让前端再加一份预览；提示词框定高、字号 12；打开我们的工作流时把整镜摆进看得见的那块，线画成直的；人在回放的节点上改了提示词，提示一句「这是回放」。
- 两个只读接口：`/filmkit/file`（运行目录里的图片、视频）、`/filmkit/film`（登记的成片，浏览器按字节范围取）。
- 回放留下的，是人接手要用的：这一镜的关键帧 `output/filmkit__<片>__<关键帧名>.png`、这一镜的视频 `output/filmkit__<片>__<镜头名>.mp4`，文件里带着这一镜的工作流，出现在 Assets 面板的 Generated 里。文件已经在、源头没变，再跑不重写、不重复；资产系统开着时节点只写文件、不报给前端，由 ComfyUI 自己扫进库（卡片重启以后还点得回这一镜）；喂进去的图不回预览，temp 里不写东西。
- 口、参数的次序和约定见 [methods/01-mapping.md](../methods/01-mapping.md)；写法和坑见 [methods/03-nodes.md](../methods/03-nodes.md)。
- 文件在哪登记在 `comfyui_filmkit/filmkit_runs.json`（每台机器自己的，由 `scripts/shots2comfy.py` 照清单写，不进本目录的版本）：`{"<片的 key>": {"run": "<清单里的 root>", "film": "<成片>", "keys": {"<关键帧名>": "<文件>"}}}`。节点包只认这张表和工作流里的相对路径，不认识任何拍片 skill 的目录结构。
- 依赖 ComfyUI 自带的 `comfy_api.latest`（0.46.0 上写的）、numpy、Pillow、torch，不另装包，不用 ffmpeg。

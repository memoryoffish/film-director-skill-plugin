# 01 对应关系：我们的步骤 ↔ ComfyUI 节点

一句话：拍片流程里「调一次工具」的那几步各对一个节点，判断不对节点；一镜只放这一镜必要的那几个，到视频节点为止；口按运行记录里的输入一一对上，参数的次序以真前端读回来的为准。

## 什么进得去，什么进不去

| 拍片的步骤 | 在我们这里是什么 | 进 ComfyUI 吗 |
|---|---|---|
| 分镜：剧本、节拍、镜头表、时长 | agent 写的文字 | 只放这一镜：外面那个框的标题（镜头名、起止、拍什么），也是工作流的文件名 |
| 定妆：参考图 | gpt-image 出的图 | 当输入图（FilmKitImage）；出图这一步以后做成节点 |
| 白模·搭、看和算：scene.py、静帧、站位描述、越轴检查 | Blender 代码和算出来的图、文字 | 只放喂进去的那张静帧；站位描述、平面图、全片预演不放 |
| 白模转关键帧、关键帧派生 | 出图脚本调图像模型（比如 gpt-image） | 这一镜的关键帧：**FilmKitKeyframe**；别的镜头的关键帧只当输入图 |
| 生成：一次调用 | 生成脚本调视频模型 | 按喂法一个节点：**FilmKitT2V / I2V / FLF2V / R2V**，节点上直接放成片里这一镜的那几秒 |
| 生成后检查、决定重抽 | agent 看片判断 | 不进；重抽次数写在视频节点标题上 |
| 衔接、后期：入点、剪辑、调色、声音 | 剪辑脚本 + 判断 | 不进（视频节点上放的就是剪好的成片里这一段） |
| 验收、盲选 | 人和 agent 看 | 不进 |

## 约定（2026-11-19 在 ComfyUI 0.46.0 / 前端 1.59.6 上核对过）

`scripts/shots2comfy.py` 照这张表把清单写成工作流；`../viewer` 节点图视图的「导出 ComfyUI 工作流」按钮下载的就是它出的那一份。

| 清单里的东西 | 节点类型 | 输入口（次序就是口号） | widgets_values（依次） | 输出 |
|---|---|---|---|---|
| 现成的图：白模静帧、参考图、别的镜头的关键帧、不是生成的帧 | FilmKitImage | — | [film, file] | IMAGE「图」 |
| 这一镜的关键帧 | FilmKitKeyframe | `images.image0`、`images.image1`……用了几张写几个，再加一个空口；label 图1、图2…… | [prompt, size, film, name, mode] | IMAGE「关键帧」 |
| 文生视频（输出节点） | FilmKitT2V | — | [model, prompt, duration, seed, **"fixed"**, resolution, ratio, audio, film, name, mode, t0, t1, shot] | VIDEO「视频」 |
| 首帧生视频 | FilmKitI2V | first_frame（首帧） | 同上 | VIDEO |
| 首尾帧生视频 | FilmKitFLF2V | first_frame、last_frame | 同上 | VIDEO |
| 参考图生视频 | FilmKitR2V | `refs.ref0`……再加一个空口（label 参考图1…）、ref_video | 同上 | VIDEO |
| 这一镜的框 | 分组框（groups 里一项） | — | `{title, bounding, font_size, color}` | — |
| 线的拐点 | reroute（`extra.reroutes` + `extra.linkExtensions`） | — | `{id, pos, linkIds, parentId}`；线记它最后经过的那个 | — |
| 参考视频（这批数据里没有） | LoadVideo | — | [`filmkit__<片>__<路径>`, "image"] | VIDEO |

- `film` 是片的 key（如 `zz_demo`）；`file` 是相对清单里 root 的路径（`wm/S3_a.png`）；`name` 是关键帧名（文件名去掉扩展名）或任务名；`t0`、`t1` 是这一镜在成片里的起止秒数；`shot` 是镜头名（留在 output 里的那段视频按它叫）；`mode`（显示名「执行方式」）是 `replay`。节点按 film 去登记表里找 root、成片、关键帧的文件，工作流里不写服务器路径。
- **喂法、哪些关键帧展开，清单里写明了**：`video.feed` 是哪种就用哪种节点；`keyframes` 里列了的才展开成关键帧节点，它们用到的图里，又在 `keyframes` 里的才连过去，其余都是 FilmKitImage。拍片运行目录里这些怎么认，见 [../formats/read_run.py](../../formats/read_run.py)。
- **同一张图只放一个节点**，喂了几处连几根线（女孩的参考图既喂关键帧、又直接喂视频，是一个节点两根线）。
- **标题说人话、要短**（比节点宽会被截掉）：
  - 输入图：用清单里写的 `title`（`白模 · S3 开头`、`参考图 · girl_front`、`s01 的首帧`、`基准画面 · k_base`）。
  - 只喂给视频任务的图，标题先写角色：`首帧 · S21 的尾帧`、`参考图1 · girl`（清单里有 `short` 就接 short）、`参考图5 · s10 的关键帧`；关键帧也用它的不写角色（角色看视频节点的口）。
  - 这一镜的关键帧：`首帧 · k_S3`、`尾帧 · k_s21_b`、`参考图3 · k_s08_a`；重画过加 ` · 画了 2 次`。
  - 视频节点：`首帧生视频 · v3r · 生成 2 次`，有报错加 `，1 次报错`，一条切成几镜加 ` · 一条切成 3 镜`。
  - 框：`S3 · 0:08.0–0:12.0 · 她把杯子放到桌上`，字号 24，放不下依次降到 20、18、16，再放不下才截。
- **颜色**：用 ComfyUI 自带的节点颜色（`color` / `bgcolor`）：白模蓝 #223/#335、参考紫 #323/#535、关键帧黄 #432/#653、视频绿 #232/#353；框 #8AA。
- **seed 后那一格 `"fixed"`**：前端给叫 seed 的参数自动加一个「生成后怎么换种子」的控件，不占这一格，后面的参数整体错一位。回放必须是 fixed。
- **藏起来的参数**：film、file、name、shot、mode、size、seed（连带那个控件）、resolution、ratio、audio、t0、t1 在节点定义里标 advanced，由前端脚本藏起来；设置里打开「Always show advanced widgets」就照常显示（空口也跟着显示）。
- `properties.filmkit` 放清单里的原路径、重抽明细（`takes: [[名字, 成没成, 用没用上], …]`）、喂法；`extra.filmkit` 放 `{film, title, shot, t0, t1, what, job, feed, view, sha1}`，`view` 是出工作流时算的视图（和 `extra.ds` 一样），前端脚本拿它认「头一回打开」；`sha1` 是这份工作流去掉这一项以后的文本的 sha1，重出时拿它认「人有没有改过」。

## 能换成官方节点的

| 我们的节点 | 官方的 | 换的时候注意 |
|---|---|---|
| FilmKitImage | LoadImage | 图已经在 input 最上层（`filmkit__<片>__…`，从 Assets 的 Imported 插进来就是它）；带子目录的值前端报 Missing Inputs，软链 ComfyUI 不认；多出文件名、上传按钮、MASK 口；预览最少占 220 高 |
| FilmKitR2V（Seedance） | ByteDance2ReferenceNodeV2（Partner） | 口叫 `model.reference_images.image_1…`、`model.reference_videos.video_1`；走 Comfy 账号和 Comfy Credits，不用自己配的接口 key |
| FilmKitI2V / FLF2V（Wan） | Wan 的 Partner 节点 | 同上 |
| FilmKitKeyframe | OpenAI GPT Image 的 Partner 节点 | 多张输入图要先拼成一批；同样走 Comfy 账号 |
| 视频节点上的画面 | 核心节点 Video Slice + SaveVideo | SaveVideo 每跑一次往 output 写一个带序号的新文件，Assets 面板里多一张卡片；我们的节点同一镜只留一个文件 |

## 伪代码

```
for 清单里的每一镜 s:
    视频节点 = FilmKit<s.video.feed>(video 的参数, t0, t1)，口：首帧 ← 图(video.first, "首帧") …
    图(路径, 角色):
        在 s.keyframes 里 → FilmKitKeyframe，标题「角色 · 名字」，
            口：图i ← 它的 inputs（又在 s.keyframes 里的才连过去，否则 FilmKitImage）
        否则 → FilmKitImage（同一张图只建一个；标题用 s.images 里写的）
    框的标题 = 镜头名 · 起止 · 拍什么
```

---
name: film-crew
description: 导演身边的剧组：拍片的方法（film-director 里的 video-film-maker、blender-previz）管怎么拍，这里是拍的时候用的四样工具，装一次全有。backends 把任务单（一次生成要什么的 JSON）交给视频、图像模型的官方接口，出片出图，key 走环境变量，每个模型一张能力卡；viewer 把拍片的运行目录做成网页——拍片进行中的进度页（每一次生成都能看，花了多少时间和钱）、拍完的展示台（每一镜喂进模型的图、首尾帧、参考图、prompt、参数和成片对照）和节点图（每镜谁喂给了谁，能导出 ComfyUI 工作流）；comfyui 把每一镜放进 ComfyUI 给人看、给人接手，只回放不生成；formats 是它们之间两份交接文件（任务单、镜头清单）的格式、检查脚本，和把运行目录读成清单的脚本。Use when a film run needs a video or an image generated from a job sheet, a look at the exact request before it is sent, a model chosen by its capability card (feeds, length, reference images, price, speed), a live progress page while shots are generating, a showcase page or node graph of what each shot was fed and what came out, the shots opened in ComfyUI as workflows, or a run directory turned into a shots manifest — 任务单 / 出片 / 出图 / 选模型 / 能力卡 / 进度页 / 每一次生成都能看 / 展示台 / 节点图 / 镜头清单 / 读运行目录 / 接 ComfyUI / 导出 ComfyUI / 百炼 / 火山方舟 / MiniMax / OpenAI Images / film-crew.
---

# film-crew

一句话：拍片的方法管「怎么拍」，这里是拍的时候用的工具——调模型、看进度、拍完给人看。四块并排，各有自己的 `overview.md`；路径都相对本目录。

## 四块各管什么

| 块 | 管什么 | 什么时候用 | 先读 |
|---|---|---|---|
| `backends/` | 任务单进，片子和图出 | 要生成一段视频或一组图；想先看会发什么请求；要选模型 | [backends/overview.md](backends/overview.md) |
| `viewer/` | 运行目录 → 给人看的网页 | 拍片进行中看每一次生成（进度页）；拍完看每一镜喂了什么、出了什么（展示台、节点图） | [viewer/overview.md](viewer/overview.md) |
| `comfyui/` | 每一镜放进 ComfyUI | 人想在 ComfyUI 里看一镜是怎么做出来的，把关键帧和片拿去接着用 | [comfyui/overview.md](comfyui/overview.md) |
| `formats/` | 两份交接文件的格式 | 写或查任务单；把运行目录读成镜头清单 | [formats/overview.md](formats/overview.md) |

四块之间只靠两份文件来往：**任务单**（一次生成要什么）交给后端；**镜头清单**（一部片每一镜用了什么、出了什么）交给两个查看器。

## 拍一部片时它们在哪出场

1. **开拍**：进度页起在 tmux 里，之后每一次生成出来它都会列上——`python3 viewer/scripts/progress.py <输出目录> --jobs <项目>/clips --prices backends/cards/prices.json --every 60`。
2. **生成**：每一次生成写一张任务单放进 `<项目>/jobs/`（视频）、`<项目>/jobs_img/`（图）。先 `python3 backends/scripts/filmgen.py request <单子>` 看会发什么，再 `run`。后端调的是各家的官方接口：阿里云百炼（Wan 3.0、HappyHorse 1.1）、火山方舟（Seedance 2.5 / 2.0）、MiniMax（H3-Max）、OpenAI Images（gpt-image 2.6）。选哪个模型看 [backends/cards/](backends/cards/overview.md)。
3. **拍完**：在运行目录里写一份镜头表 `meta.json`（每一镜叫什么、在成片里从第几秒到第几秒、用的哪条生成），再 `python3 formats/read_run.py <配置> --out <清单目录>` 读成镜头清单，`python3 formats/check_manifest.py` 查一遍。
4. **给人看**：网页是 `python3 viewer/scripts/console.py <清单…> <输出目录>`；要进 ComfyUI 是 `python3 comfyui/scripts/shots2comfy.py <清单…> --comfy <ComfyUI 目录>`。网页上的节点图照 ComfyUI 那份工作流画，要它就先跑 `shots2comfy.py`，再给 `console.py` 加 `--workflows`。

要装的：Python 3.10 以上。`backends`、`formats`、进度页和 `shots2comfy.py` 只用标准库（`backends` 量成片时长时用 ffprobe）；展示台（`console.py`）另要 Pillow 和 ffmpeg；`send` 要 ssh，对面机器上要有 tmux；ComfyUI 节点包在 ComfyUI 自己的环境里跑（用它带的 Pillow、numpy）。

每一步的参数、做完查什么，在那一块的 `overview.md` 里。

## 规矩

- **key 只从环境变量读**（`DASHSCOPE_API_KEY`、`ARK_API_KEY`、`MINIMAX_API_KEY`、`OPENAI_API_KEY`），不写进任何文件，不打印。没设 key 时 `request` 照样能用。
- **查看器只读**：不改运行目录，不调生成接口。人在 ComfyUI 或网页上看到要调整的，告诉 agent，agent 改完再交一次。
- **先看再发**：每张单子先 `request`；要重来或换参数，存成一张新名字的单子。
- **做出来的页面照人的开法自己看一遍**，再交给人。

# viewer：拍片运行的网页查看器

一句话：拍片的 skill 拍完留下一个运行目录，先把它读成镜头清单，这里再把清单做成给人看的网页——展示台看每一镜喂进去了什么、出来了什么，节点图看每一镜谁喂给了谁，进度页看正在拍的片子每一次生成。路径都相对本目录。

## 核心思路

1. **查看器只分析拍片留下的东西。** 拍片的方法不用为它改。运行目录只在一处读（`../formats/read_run.py` → 镜头清单），要另外写的只有一份镜头表 `meta.json`（见 [../formats](../formats/overview.md)）；这里只读清单、清单里写的图和视频，和 `../comfyui` 写出来的工作流文件。
2. **一份清单，两个查看器。** ComfyUI 和网页读同一份清单：ComfyUI 用的几项不变；网页另要的事实（白模预演、白模的站位、参考图是谁、每一次生成的结果……）跟在后面，都可以没有，ComfyUI 不看。格式见 `../formats/shots-manifest.md`。
3. **最显眼的是视频模型拿到的东西。** 展示台右栏先放「喂进视频模型的」：发出去的每张图照发送的次序（图N · 从哪来 · 是谁）、参考视频、参数、prompt 全文；下面每镜一行：白模静帧（只给出图模型看，标「不进视频」）→ 这一镜的关键帧（怎么出的收起来）→ 成片这一镜。
4. **节点图照 ComfyUI 里那份画。** 页面不自己排节点，每镜嵌 `../comfyui` 写出来的那份工作流原文，照它的位置、大小、标题、口和线画；「导出 ComfyUI」下载的就是那份文件，一个字节不差。
5. **一屏放下，不先下载视频。** 1440×820 里顶栏、两栏、时间线都在；视频 `preload="none"`，没播放时拿这一镜的中间帧当海报。片子多时用 `--compact` 精简成一镜一张图。

## 怎么用

1. **读成清单**：先在运行目录里写好镜头表 `meta.json`，再 `python3 ../formats/read_run.py films.json --out manifests/`。配置里写每部片的运行目录、成片、预演、想让页面打开就停在的时刻和一句话。
2. **要节点图，先出工作流**：`python3 ../comfyui/scripts/shots2comfy.py manifests/*.shots.json --comfy <ComfyUI 目录> [--no-run]`；工作流写在 `<ComfyUI>/user/default/workflows/filmkit/`（`--out` 可以另指）。
3. **做页面**：`python3 scripts/console.py manifests/*.shots.json site/ --workflows <工作流目录> [--view graph] [--compact]`。在读得到成片和图的机器上跑（要 Pillow、ffmpeg）。
4. **照人的开法看一遍**：首页点片卡、点时间线、切节点图、播放，1440×820 和手机宽度各看一次；查什么见 [methods/01-console.md](methods/01-console.md)、[methods/02-graph.md](methods/02-graph.md) 末尾。
5. **拍片进行中**：`python3 scripts/progress.py <输出目录> --jobs <clips 目录> [--prices <价格表>] [--every 60]` 放进 tmux，见 [methods/03-progress.md](methods/03-progress.md)。

## 在哪

- 做法：[methods/](methods/overview.md)（展示台、节点图、进度页）。
- 脚本和模板：[scripts/](scripts/overview.md)。
- 风格：[styles/](styles/overview.md)（页面换一身样子：`fancy` 深色放映厅、`warm` 拍片手账；不选就是本来的样子）。
- 从运行目录到页面的一遍命令：[examples/](examples/overview.md)。
- 测试：[tests/](tests/overview.md)，不联网。
- 清单的格式和读运行目录的脚本：[../formats](../formats/overview.md)；ComfyUI 那一头：[../comfyui](../comfyui/overview.md)。

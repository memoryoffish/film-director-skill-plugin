# backends

一句话：任务单进，片子和图出；按单子里的 `model` 找到那家官方接口的适配去调，留下生成记录。路径都相对本目录。

## 是什么

- 一条命令 [scripts/filmgen.py](scripts/filmgen.py)，三种用法：`run` 在这台机器上生成；`send` 把一个项目的视频任务连同用到的图送到另一台机器上，在 tmux 里跑完再一条条取回；`request` 只打印会发出去的请求（地址、不带 key 的请求头、请求体和它的哈希），不发、不传、不读 key。
- 单子的格式在 [../formats/job-sheet.md](../formats/job-sheet.md)。单子只写要什么；哪个模型收什么，写在这里的能力卡上。
- 四个适配，按单子里的 `model` 选：

| 适配 | 官方接口 | 模型（官方型号名） | 单子里写 | key 的环境变量 | 真跑过 |
|---|---|---|---|---|---|
| [bailian.py](scripts/bailian.py) | 阿里云百炼 | `wan3.0-video`、`wan3.0-video-prime`、`happyhorse-1.1-t2v` / `-i2v` / `-r2v` | 不写，或型号名；`happyhorse-1.1` 按喂法挑 | `DASHSCOPE_API_KEY` | Wan 3.0 跑过（2026-11-22，key 从环境变量读）；HappyHorse 没有 |
| [ark_video.py](scripts/ark_video.py) | 火山方舟 | `doubao-seedance-2-5-260628`、`doubao-seedance-2-0-260128` | `seedance-2.5`、`seedance-2.0`，或型号名 | `ARK_API_KEY` | 没有 |
| [minimax_video.py](scripts/minimax_video.py) | MiniMax | `MiniMax-H3-Max` | `minimax-h3`，或型号名 | `MINIMAX_API_KEY` | 没有 |
| [openai_image.py](scripts/openai_image.py) | OpenAI Images | `gpt-image-2.6-sunburst`、`gpt-image-2.6-flare` | 出图单子不写，或型号名 | `OPENAI_API_KEY` | 改图一张经一个兼容 OpenAI 接口的网关跑通（2026-11-22）；没有直接对 api.openai.com 跑过 |

「没有」的两个是照官方文档写成的，请求格式离线核对过，还没有用真的 key 跑过；出图适配也是照官方文档写的。每个适配文件开头写着照的是哪几页官方文档。

## 怎么用

在项目目录里跑（单子里的相对路径从项目目录算起）：

```
python3 <本目录>/scripts/filmgen.py request jobs/v01.json jobs_img/k_s1.json   # 看会发什么
python3 <本目录>/scripts/filmgen.py run jobs_img/k_s1.json --out keys          # 在这台机器上出
python3 <本目录>/scripts/filmgen.py send . --wait 540                          # 视频送到另一台机器上跑，取回 clips/
```

1. 写单子，放进 `jobs/`（视频）、`jobs_img/`（图）。
2. `request` 看一眼：用哪个适配、哪个模型、什么喂法、发到哪、请求体是什么。收不了的单子在这里就会说为什么。
3. `run`：视频默认放 `clips/`，图默认放 `out/`，`--out` 可改。要让查看器读到，关键帧用 `--out keys`、参考图用 `--out refs`（[read_run.py](../formats/read_run.py) 只认这两个目录里的图）；已经出好的跳过；收不了的单子当场拒、不跑；有拒的或失败的，退出码 1。
4. `send`：只送 `jobs/*.json`；已经有成片或失败过的跳过，文件还没齐的先跳过；等到 `--wait` 秒还没完就退出（码 3），再调一次接着等。tmux 会话名和远端目录打印在屏幕上。
5. 要重来或换参数，存成一个新名字的单子。

## key、地址、机器

都在 [local/machine.py](local/machine.py)，全部从环境变量读，仓库里没有 key、没有机器名。

- **key**：各适配在进程里读上表那一列的环境变量（名字照各家官方文档），不打印、不写进文件。`send` 这一头不读 key；在另一台机器上跑时，key 要在那台机器上 tmux 会话看得到的环境里。
- **地址**：默认是官方地址（百炼北京、方舟 cn-beijing、MiniMax 中国站、OpenAI），换地域或站点设 `DASHSCOPE_BASE_URL`、`ARK_BASE_URL`、`MINIMAX_BASE_URL`、`OPENAI_BASE_URL`。
- **send 送到哪**：`FILM_SEND_HOST`（ssh 主机）、`FILM_SEND_REMOTE`（那台机器上放项目的目录，相对 home），这两个不设，`send` 说一句就退出；可选 `FILM_SEND_SESSION`（tmux 会话名，默认 `film_{project}`）、`FILM_SEND_PYTHON`（默认 `python3 -I`）。
- **并发**：每个适配同时跑几条，在 `machine.WORKERS`。

## 文件

| 在哪 | 是什么 |
|---|---|
| [scripts/](scripts/overview.md) | 命令、四个适配、送任务的 send、读单子的 sheets；每个文件留下什么记录 |
| [cards/](cards/overview.md) | 能力卡（每个模型收什么、几秒、多大、多少钱）和单价 prices.json |
| [local/machine.py](local/machine.py) | key 的变量名、地址、send 的机器、并发 |
| [examples/](examples/overview.md) | 例子单子、命令和真跑过的那一条的结果 |
| [tests/](tests/overview.md) | 单元测试（不连网） |

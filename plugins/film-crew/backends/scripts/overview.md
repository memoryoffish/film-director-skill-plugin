# scripts：命令和适配

一句话：`filmgen.py` 是唯一的命令；它读单子，按 `model` 交给四个适配之一；地址、key 的变量名、并发数都从 `../local/machine.py` 拿。

| 文件 | 是什么 |
|---|---|
| [filmgen.py](filmgen.py) | 命令：`run`、`send`、`request` |
| [sheets.py](sheets.py) | 读单子：视频还是图片、什么喂法、交给哪个适配 |
| [bailian.py](bailian.py) | 百炼适配：Wan 3.0、HappyHorse 1.1（异步任务：提交、轮询、下载），参考视频先传到百炼的临时存储 |
| [ark_video.py](ark_video.py) | 火山方舟适配：Seedance 2.5 / 2.0；`rewrite()` 是给 Seedance 的机械改写 |
| [minimax_video.py](minimax_video.py) | MiniMax 适配：MiniMax H3-Max |
| [tasks.py](tasks.py) | 方舟和 MiniMax 共用的一段：提交一次、按任务 ID 轮询、下载，写记录 |
| [openai_image.py](openai_image.py) | 出图适配：OpenAI Images，gpt-image 2.6（有输入图走 `/images/edits`，没有走 `/images/generations`） |
| [send.py](send.py) | `filmgen.py send`：打包单子、用到的图和本目录的代码，ssh 到 `FILM_SEND_HOST`，tmux 里跑 `filmgen.py run`，一条条取回 |

## 单子交给谁（sheets.py）

1. 视频还是图片：`kind` → `model` 以 `gpt-image` 开头或有 `images` / `size` / `n` / `quality` → 图片；其余是视频。
2. 喂法：只看媒体字段（文生、首帧、首尾帧、参考图、参考视频；图片是改图、文生图）。只有尾帧、首尾帧和参考图混写，当场拒。
3. 适配：图片 → openai_image；视频的 `model` 不写、以 `wan` 或 `happyhorse` 开头 → bailian；`seedance-2.5`、`seedance-2.0` 或方舟的型号名 → ark_video；`minimax-h3`、`MiniMax-H3-Max` → minimax_video；别的模型名当场拒。

## 每个适配都有的三个函数

| 函数 | 做什么 | 谁用 |
|---|---|---|
| `problem(job)` | 这个适配收不收这张单子（不发请求、不读 key），收就返回空串 | `run` 开跑前、`send` 送之前 |
| `run(jobs, out)` | 一批单子，几条一起跑（并发数在 `machine.WORKERS`），写记录，返回每条成没成 | `run` |
| `request(job)` | 组出和真发一样的请求，只返回地址、不带凭据的请求头、请求体的 sha256 和大小，以及能看懂的请求体 | `request` |

`request` 里和真发不一样的地方：百炼的参考视频要先上传，显示成一个占位的 `oss://` 地址；方舟、MiniMax 的请求体里内联的图和视频缩成「路径 + 长度」，哈希是完整请求体的；首帧写 `"@NAME"` 的显示成占位，链接要到真发时才从 `OUT/NAME.last_frame_url` 读；出图的 multipart 分隔串每次随机，哈希只对显示的那个分隔串成立。

## 图和视频怎么交

- 百炼：图转成 base64 data URL 放进请求体；参考视频先传到百炼的临时存储（48 小时有效），交 `oss://` 地址。
- 方舟：图转成 base64 data URL；不收本地参考视频（方舟的参考视频只收公网链接或素材 ID）。
- MiniMax：图和参考视频（只认 .mp4）都转成 base64 data URL。
- 方舟、MiniMax 的请求体官方上限都是 64 MB，base64 会让文件变大约三分之一；大的图和视频官方建议换公网链接，这几个适配只传本地文件。
- OpenAI：multipart，每张输入图一个 `image[]`。

## 留下的记录

| 文件 | 谁写 | 字段 |
|---|---|---|
| `OUT/<name>.json`（视频，百炼） | bailian | `name`、`job`（单子原样）、`payload`（请求体，图写成文件路径加 sha256）、`status`（提交前写 `dispatching`，之后是接口的状态，下载完 `DOWNLOADED`）、`task_id`、`request_id`、`submitted_utc`；成了再加 `media`（ffprobe）、`usage`、`timing`、`actual_prompt`；失败加 `failure` |
| `OUT/<name>.json`（视频，方舟、MiniMax） | tasks | `name`、`job`（单子原样）、`payload`（`model`、`content`（图写成文件路径加 sha256）、`parameters`；真发时 `parameters` 放到请求体顶层）、`status`（提交前 `dispatching`，之后 `SUBMITTED`、`QUEUED`、`RUNNING`，下载完 `DOWNLOADED`，失败 `FAILED`）、`task_id`、`submitted_utc`、`timing`（`submit_time`、`end_time`）；成了加 `media`（ffprobe）、`usage`（接口回的用量，加上 `duration`：成片秒数）、`last_frame`；失败加 `failure`（接口的状态和错误） |
| `OUT/<name>.last_frame_url` | tasks | 方舟交回的官方尾帧链接（单子写了 `return_last_frame`），24 小时有效，权限 600；下一段首帧写 `"@<name>"` 时读它 |
| `logs/results.jsonl`（每行一条） | bailian、tasks | `utc`、`name`、`ok`、`usage`、`error`、`task_id` |
| `OUT/<name>.json`（图） | openai_image | `ok`、`job`、`usage`（token）、`images`（几张）、`seconds`；失败时 `error` |

视频状态文件的 `status`、`submitted_utc`、`timing`、`usage.duration`、`payload.model`、`payload.parameters.resolution` 几个字段，查看器（`../viewer/`）的进度页也读。`send` 判断失败看 `clips/results.jsonl` 里 `ok` 为假的。

提交前先存状态：提交的回执丢了（没拿到任务 ID），这一条不会自动重发，状态停在 `dispatching`，`results.jsonl` 记失败；查清楚以后换个名字再送。轮询时断线只接着轮询，不重新提交。

## 接一个新模型或一家新接口

1. 同一家接口的新模型：在适配里认这个模型名（`sheets.backend()` 的判断、各适配的 `MODELS`），写一张能力卡。
2. 新的一家：先找官方文档，照它写一个适配，文件开头写明照的哪几页、哪天查的；有 `problem`、`run`、`request` 三个函数，记录照上表的样子写（异步任务的可以用 tasks.py）；默认地址、并发数加进 `machine.py`，key 从官方文档写的那个环境变量读；在 `sheets.backend()` 里加一个分支。
3. 加测试：模型名选到这个适配、请求体照官方文档的样子、`request` 不发东西；有机械改写的，测改写做两遍和一遍一样。
4. `request` 看一遍，再真跑一条最短的。

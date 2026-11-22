# scripts：Wan 3.0 上的参考实现

各步的思路和伪代码在 Wan 3.0（百炼 `wan3.0-video`）上跑通时，用的就是这些脚本。换别的模型时，思路照用，`wan.py` 和提示词要换。默认参数和门槛汇总在 [refs/practical/config.md](../refs/practical/config.md)；每个案例（`examples/edit/<方法>/*.md`、`examples/transitions/<方法>/*.md`）的「复现」一节有当时实际跑的命令和参数。

生成：

| 脚本 | 做什么 |
|---|---|
| `wan.py` | Wan 3.0 异步任务客户端：建任务（文生、首帧、首尾帧、参考图、参考视频）、轮询、下载；POST 之前先存状态，回执丢了也不重发请求；参考视频先传到百炼的临时存储。key 只在进程里读，不打印 |
| `occut.py gen` | 批量生成（`--workers` 默认 4，比我们用的并发多，按 config 改小） |
| `movie.py` | 按 plan 跑一部混合多种转场的片（文生 / 参考图 / 续写；接缝支持遮挡、色彩、续写），每次生成后检查和这一段相连的接缝，不合格换种子重拍。只支持一组参考图、一个种子；带参考图时画幅在代码里固定为 16:9 |
| `refcrop.py` | 从片子里按原生像素裁参考图，不够大再放大 |

检查：

| 脚本 | 做什么 |
|---|---|
| `occut.py cuts` | 找模型自带的切镜（颜色分布跳变；相邻帧画面差这一路还没有） |
| `occut.py seam` | 量接缝：场景分、方向、速度比、复述段 |
| `audio_probe.py` / `env10.py` / `peaks.py` | 声音在哪、多响（每 0.25 s / 20 ms 的 RMS、主频）、有没有配乐（谱峰在音符间跳） |
| `asr.py` | 语音识别：转写有人说话的那几秒，逐字对台词、查多出来的人声。装了 mlx-whisper 或 openai-whisper 哪个就用哪个；都没装时以退出码 3 退出，这时台词不算核对过 |
| `colorfill.py` | 某种颜色占满画面没有（占比 + 4×8 格最偏的一格） |
| `glowlen.py` | 光晕实际看得见多久 |
| `track_toss.py` | 抛起物体的最高点 |

衔接：

| 脚本 | 做什么 |
|---|---|
| `occut.py tail` | 在尾部找被盖满的剪点（选的是盖满帧里信息最少的一帧，和方法里「留够叠化就剪」不一样，用时手动挑） |
| `occut.py join` | 帧精确拼接：声音交叉淡化、B 开头加速、遮挡帧叠化、调用标注（标注要一个中文字体：先读环境变量 `OCCUT_FONT`，没设就在 Linux、macOS 的常见位置找；ffmpeg 要带 drawtext） |
| `occut.py chain` | 按分镜表一段接一段跑遮挡转场 |
| `optical_edit.py` | 光学类剪辑：硬切、光晕（闪白）、纯白闪、叠化、淡出淡入，逐帧缩放平移（形状叠化）。光晕的合成音效默认开，可以关 |
| `camfx.py` | 推镜穿越、甩镜的数字效果（缩放 + 径向模糊 / 横向模糊），`center --box` 找出口光的中心，`label`（给剪点前后两段各加一个角标）、`sheet`（把剪点前后的帧拼成一张检查图） |

后期（画面 / 声音）：拳馆大片版和 4 部复刻用的渲染、调色、稳定、对照图、换声脚本都还在各片的目录里（路径见 [examples/films](../examples/films/overview.md) 各篇的出处），没收进这里。

测试在 [`../tests/`](../tests/overview.md)（合成视频和声音，不联网）：`CUDA_VISIBLE_DEVICES= python3 -m pytest -q -p no:cacheprovider tests/`，要 ffmpeg、numpy、opencv、pytest。
- [wan.py](wan.py) 也能调 HappyHorse 1.1：job 里写 `"model": "happyhorse-1.1"`，按有没有首帧、参考图自动选 `-t2v` / `-i2v` / `-r2v`，只发它认的参数（见 [../refs/practical/models.md](../refs/practical/models.md)）。
- [budget.py](budget.py)：预算。`estimate` 按计划估时间和钱并写好问用户的话，`netcheck` 现测网络和典型值比，`actual` 统计已经生成的计费秒数和花费。见 [../stages/common/budget.md](../stages/common/budget.md)。
- [progress.py](progress.py)：进度页。读任务记录（记录可以在远程机器上），把每一次生成的视频拷到本机、做成能播的网页，加上事件、花费、最新粗剪；`--every` 定时重建。见 [../stages/common/visualize.md](../stages/common/visualize.md)。

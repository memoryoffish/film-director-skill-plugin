# MiniMax H3-Max（官方型号名 `MiniMax-H3-Max`）

一句话：MiniMax H3 系列里出片快的那个；480P / 768P，5–15 秒，声音可开可关。

官方文档（2026-11-22 查）：[创建视频生成任务](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)（[中国站](https://platform.minimax.cn/docs/api-reference/video-generation-v2-create)）、[查询任务](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)、[视频生成指南](https://platform.minimax.cn/docs/guides/video-generation)；下表「官方」指这几页。

| 项 | 经这个后端 | 出处和日期 |
|---|---|---|
| 后端、单子里写 | `scripts/minimax_video.py`；`"model": "minimax-h3"` 或 `"MiniMax-H3-Max"` | minimax_video.py |
| 地址和 key | 默认中国站 `https://api.minimax.cn`；国际站的账号设 `MINIMAX_BASE_URL=https://api.minimax.io`。key 是 `MINIMAX_API_KEY`，跟着站点走。H3 系列要用按量付费的 API | machine.py；官方 |
| 改写 | 提示词原样；`resolution` 改大写；`seed` 不往外传（接口没有 seed） | minimax_video.py；官方 |
| 喂法 | 文生、首帧、首尾帧、参考图、参考视频；首帧 / 尾帧和参考图、参考视频互斥。官方还收只给尾帧、参考音频，单子格式没有这两种 | 官方；minimax_video.py |
| 单条时长 | 5–15 秒，整数秒，单子里必须写（H3-Max 不收 4 秒） | 官方 |
| 分辨率 | 480P、768P，不写是 768P；768P 实际 1344×768、24 fps | 官方；作者实测，2026-11（最后一句） |
| 画幅 | 文生：单子的 `ratio`（不写是 16:9），不能是 adaptive（后端当场拒）。首帧、首尾帧：跟图走，后端传 adaptive。参考图、参考视频：单子的 `ratio`（不写是 16:9），也可以写 adaptive。可选 adaptive、21:9、16:9、4:3、1:1、3:4、9:16 | 官方；minimax_video.py |
| 参考图 | 最多 9 张；每边 256–5760 像素，宽高比 0.4–2.5，单张不超过 30 MB；JPG、JPEG、PNG、WEBP、HEIC、HEIF（后端只认 png、jpg、webp）；整个请求不超过 64 MB | 官方 |
| 参考视频 | 后端一次传一段，只认 .mp4，转成 base64 放进请求体。官方：最多 3 段，单段 2–15 秒、合计不超过 15 秒，单个不超过 50 MB，23.976–60 fps；大文件官方建议用公网链接 | 官方；minimax_video.py |
| 提示词 | 最多 7000 字。提示词扩写：单子的 `prompt_extend` 为真时 `balanced`（官方默认），不写或为假时 `disabled` | 官方；minimax_video.py |
| 提示词里怎么叫 | 后端不改写。官方例子写「人物参考图1 图2」「参考视频1」「音色参考音频1」 | 官方中文 API 参考和指南 |
| 拒收 | 提示词有敏感内容报 1026（422）。写实人脸的输入图试过一次没被拒 | 官方；作者实测，2026-11（第二句） |
| 声音 | 单子的 `audio` 就是 `generate_audio`，默认开；普通话台词说得对 | 官方；minimax_video.py；作者实测，2026-11（最后一句） |
| 官方尾帧 | 没有（接口不回尾帧，`return_last_frame` 不传） | 官方 |
| 价格 | 中国站：输出 768P 0.50 元/秒、480P 0.33 元/秒；输入视频 768P 0.97、480P 0.37 元/秒；每个任务前 2 张图免费，之后每张 0.50 元；音频输入免费。国际站：输出 768P $0.08、480P $0.05 每秒。[prices.json](prices.json) 里放的是中国站的输出价 | [中国站价格页](https://platform.minimax.cn/docs/pricing/overview)、[国际站价格页](https://platform.minimax.io/docs/guides/pricing-video)，2026-11-22 查 |
| 出片时间 | 文生 5 秒约 14 秒出片；首帧、首尾帧、参考图约 30 秒 | 作者实测，2026-11 |
| 这个后端实测 | 没有：照官方文档写成，请求格式离线核对过，还没有用真的 key 跑过 | — |

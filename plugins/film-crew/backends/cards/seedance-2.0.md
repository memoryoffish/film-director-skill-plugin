# Seedance 2.0（官方型号名 `doubao-seedance-2-0-260128`）

一句话：和 2.5 同一个方舟接口、同一把 key，单条最长 15 秒、参考图最多 9 张；首帧时可以自己定画幅。

官方文档同 [seedance-2.5.md](seedance-2.5.md)（创建、查询视频生成任务，错误码），另有 [Seedance 2.0 系列教程](https://ark.volcengine.com/region:cn-beijing/docs/seedance-2-0)，2026-11-22 查。

| 项 | 经这个后端 | 出处和日期 |
|---|---|---|
| 后端、单子里写 | `scripts/ark_video.py`；`"model": "seedance-2.0"` 或 `"doubao-seedance-2-0-260128"` | ark_video.py |
| 改写 | 和 2.5 一样：去掉 `seed`，`resolution` 改小写，`图N` 改成 `@图片N` | ark_video.py `rewrite()` |
| 喂法 | 文生、首帧、首尾帧、参考图；首帧、首尾帧和参考图互斥；参考视频后端不收（同 2.5） | 官方；ark_video.py |
| 单条时长 | 4–15 秒，整数秒，单子里必须写 | 官方 |
| 分辨率 | 480p、720p、1080p、4k，不写是 720p；输出 24 fps；4k 是 10bit、H.265 编码 | 官方 |
| 画幅 | 单子的 `ratio`（不写是 16:9），首帧、首尾帧时也照传；可选 16:9、4:3、1:1、3:4、9:16、21:9、adaptive | 官方；ark_video.py |
| 参考图 | 最多 9 张；每张宽高比 0.4–2.5，每边 300–6000 像素，小于 30 MB；整个请求不超过 64 MB | 官方 |
| 提示词里怎么叫 | `@图片N`（后端改写） | 官方；ark_video.py |
| 拒收 | 不支持直接上传含真人人脸的参考图 / 视频（同 2.5） | 官方 |
| 声音 | 单子的 `audio` 就是 `generate_audio`，默认开 | ark_video.py；官方 |
| 官方尾帧 | 同 2.5（`return_last_frame`） | 官方 |
| 价格 | 按 token 计费：输入不含视频时，480p、720p 每百万 token 46 元，1080p 51 元，4k 26 元（输入含视频时 28、31、16 元）。价格页给的折合价（16:9、输出 5 秒、输入不含视频）：480p 0.46、720p 0.99、1080p 2.48、4k 5.05 元/秒，[prices.json](prices.json) 里放的是这个 | [方舟模型价格页](https://ark.volcengine.com/region:cn-beijing/docs/model-pricing)，2026-11-22 查 |
| 出片时间 | 没测 | — |
| 这个后端实测 | 没有：照官方文档写成，请求格式离线核对过，还没有用真的 key 跑过 | — |

# Seedance 2.5（官方型号名 `doubao-seedance-2-5-260628`）

一句话：火山方舟的视频模型；单条 4–30 秒、参考图最多 30 张；不收含真人人脸的参考图。

官方文档（2026-11-22 查）：[创建视频生成任务](https://ark.volcengine.com/region:cn-beijing/docs/create-video-generation-task-api)、[查询视频生成任务](https://ark.volcengine.com/region:cn-beijing/docs/get-video-generation-task-api)、[Seedance 2.5 系列教程](https://ark.volcengine.com/region:cn-beijing/docs/seedance-2-5)、[错误码](https://ark.volcengine.com/region:cn-beijing/docs/error-codes)；下表「官方」指这几页。

| 项 | 经这个后端 | 出处和日期 |
|---|---|---|
| 后端、单子里写 | `scripts/ark_video.py`；`"model": "seedance-2.5"` 或 `"doubao-seedance-2-5-260628"` | ark_video.py |
| 改写 | 后端先把单子改成它要的样子：去掉 `seed`（Seedance 2.x 没有这个参数），`resolution` 改小写，提示词里的 `图N` 改成 `@图片N`；已经改过的原样用 | ark_video.py `rewrite()`；官方 |
| 喂法 | 文生、首帧、首尾帧、参考图；首帧、首尾帧和参考图互斥。参考视频后端不收：方舟的参考视频只收公网链接或素材 ID，不收 base64，这个后端只传本地文件 | 官方；ark_video.py |
| 单条时长 | 4–30 秒，整数秒，单子里必须写（官方另有 -1 让模型自己定，后端不用） | 官方 |
| 分辨率 | 480p、720p、1080p、4k，不写是 720p；输出 24 fps；1080p、4k 是 10bit、H.265 编码，少数播放器放不了 | 官方 |
| 画幅 | 文生、参考图：单子的 `ratio`（不写是 16:9），可选 16:9、4:3、1:1、3:4、9:16、21:9、adaptive。首帧、首尾帧只能 adaptive（跟首帧走），后端自动改成 adaptive | 官方；ark_video.py |
| 参考图 | 最多 30 张；每张宽高比 0.4–2.5，每边 300–6000 像素，小于 30 MB；整个请求不超过 64 MB；官方收 jpeg、png、webp、bmp、tiff、gif、heic、heif（后端只认 png、jpg、webp） | 官方；ark_video.py |
| 图怎么交 | 本地图转成 base64 data URL 放进请求体（官方建议大文件别用 base64） | ark_video.py；官方 |
| 提示词里怎么叫 | `@图片1`、`@图片2`……（单子里写 `图N`，后端会改） | 官方 Seedance 2.5 教程「提示词规则」 |
| 拒收 | 不支持直接上传含真人人脸的参考图 / 视频，报 `InputImageSensitiveContentDetected.PrivacyInformation`；官方另有预置虚拟人像、已授权真人素材的办法，这个后端没接。动漫、插画、背影、白模人偶能过 | 官方；作者实测，2026-11（最后一句） |
| 账号 | 账号设的模型用量上限到了，报 `SetLimitExceeded`（429），这个模型的服务暂停，要到控制台改上限或关「安心体验模式」。开通 2.x 模型要满足余额等条件 | 官方错误码页；官方创建任务页 |
| 声音 | 单子的 `audio` 就是 `generate_audio`，默认开 | ark_video.py；官方 |
| 官方尾帧 | 单子写 `"return_last_frame": true`，成功后 `clips/<name>.last_frame_url` 是官方尾帧（jpeg，24 小时有效），下一段首帧写 `"@<name>"`。本地截的帧常被审核拦下 | ark_video.py；官方；作者实测，2026-11（最后一句） |
| 价格 | 按 token 计费，只对成功的视频计费：输入不含视频时，480p、720p 每百万 token 70 元，1080p 77 元，4k 31 元（输入含视频时 42、46、19 元）；token 约等于（输入视频秒数 + 输出秒数）× 宽 × 高 × 帧率 / 1024。价格页给的折合价（16:9、输出 5 秒、输入不含视频）：480p 0.67、720p 1.51、1080p 3.74、4k 6.03 元/秒，[prices.json](prices.json) 里放的是这个 | [方舟模型价格页](https://ark.volcengine.com/region:cn-beijing/docs/model-pricing)，2026-11-22 查 |
| 出片时间 | 4–10 秒的片：首帧中位约 150 秒，首尾帧中位约 127 秒，参考图约 200 秒 | 作者实测，2026-11 |
| 这个后端实测 | 没有：照官方文档写成，请求格式离线核对过，还没有用真的 key 跑过 | — |

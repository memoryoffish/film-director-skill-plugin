# HappyHorse 1.1（`happyhorse-1.1-t2v` / `-i2v` / `-r2v`）

一句话：和 Wan 3.0 同一个百炼接口、同一把 key，一种喂法一个模型，没有尾帧和参考视频。

官方文档（2026-11-22 查）：[文生视频](https://help.aliyun.com/zh/model-studio/happyhorse-text-to-video-api-reference)、[图生视频（首帧）](https://help.aliyun.com/zh/model-studio/happyhorse-image-to-video-api-reference)、[参考生视频](https://help.aliyun.com/zh/model-studio/happyhorse-reference-to-video-api-reference) 三页 API 参考，和[视频生成模型列表](https://help.aliyun.com/zh/model-studio/video-generate-edit-model)。

| 项 | 经这个后端 | 出处和日期 |
|---|---|---|
| 后端、单子里写 | `scripts/bailian.py`；写 `"model": "happyhorse-1.1"`，后端按输入挑 `-t2v`（文生）、`-i2v`（首帧）、`-r2v`（参考图）；直接写带后缀的也行，但要和输入对得上 | bailian.py |
| 喂法 | 文生、首帧、参考图；没有尾帧、参考视频（后端直接拒） | bailian.py；官方三页 API 参考 |
| 单条时长 | 官方 3–15 秒，不写是 5 秒；后端的检查和 Wan 共用，放到 2 秒，2 秒的单子能过后端、会被接口拒 | 官方；bailian.py |
| 分辨率 | 480P、720P、1080P，不写是 1080P；输出 24 fps | bailian.py；官方模型列表 |
| 画幅 | 首帧模式跟着首帧走，后端不传画幅；文生、参考图模式传 `ratio`，adaptive 换成 16:9。官方可选 16:9（默认）、9:16、1:1、4:3、3:4、4:5、5:4、9:21、21:9 | bailian.py；官方 |
| 参考图 | 官方 1–9 张，短边不低于 400 像素，单张不超过 20 MB；后端的检查和 Wan 共用，放到 10 张 | 官方参考生视频页；bailian.py |
| 提示词里怎么叫 | [Image 1]、[Image 2]，要写明是图里的哪个东西，例如「[Image 1]中身着红色旗袍的女性」 | 官方参考生视频页 |
| 拒收 | 没测 | — |
| 声音 | 出有声视频，没有开关；后端不传 `audio` | 官方模型列表；bailian.py |
| 别的参数 | 不收 `prompt_extend`、`audio`；收 `resolution`、`duration`、`seed`、`watermark`（后端固定关；官方默认开，水印字是「Happy Horse」） | bailian.py；官方 |
| 价格 | 元/秒，-t2v、-i2v、-r2v 一样（华北2 北京）：480P 0.45、720P 0.9、1080P 1.2；输入不计费，按成功生成的秒数计；北京地域每个模型有 10 秒免费额度（开通后 90 天内）。数据在 [prices.json](prices.json) 的 `happyhorse-1.1-t2v` / `-i2v` / `-r2v` | [百炼模型价格页](https://help.aliyun.com/zh/model-studio/model-pricing)，2026-11-22 查 |
| 出片时间 | 一次试调，480P 3 秒：文生 71 秒，首帧 128 秒 | 作者实测，2026-11 |
| 这个后端实测 | 没有 | — |

两处后端的检查比官方宽（时长放到 2 秒、参考图放到 10 张），收了也会被接口拒，写单子时照官方的写。

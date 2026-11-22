# gpt-image 2.6（`gpt-image-2.6-sunburst`，更快的 `gpt-image-2.6-flare`）

一句话：OpenAI 的出图模型，走官方 Images 接口；定妆图、白模转关键帧都用它，画质默认 high。

官方文档（2026-11-22 查）：[Images 改图 API](https://developers.openai.com/api/reference/resources/images/methods/edit)、[Images 出图 API](https://developers.openai.com/api/reference/resources/images/methods/generate)、[图像生成指南](https://developers.openai.com/api/docs/guides/image-generation)、[模型页](https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst)、[提示词指南](https://developers.openai.com/api/docs/guides/image-prompting)；下表「官方」指这几页。

| 项 | 经这个后端 | 出处和日期 |
|---|---|---|
| 后端、单子里写 | `scripts/openai_image.py`；不写 `model` 是 `gpt-image-2.6-sunburst`（也是官方改图接口的默认）；写 `"gpt-image-2.6-flare"` 换快的 | openai_image.py；官方 |
| 喂法 | 有 `images` 是改图（`POST /v1/images/edits`，multipart，每张一个 `image[]`），没有是只凭文字出图（`POST /v1/images/generations`，JSON） | openai_image.py；官方 |
| 尺寸 | `size` 不写是 `1536x864`。官方：推荐 `1024x1024`、`1536x1024`、`1024x1536`；Sunburst、Flare 也收自定的「宽x高」：两边都是 16 的倍数，画幅 1:3 到 3:1，每边不超过 3840，总像素 655,360 到 8,294,400；或 `auto` | openai_image.py；官方指南 |
| 画质 | `quality` 不写是 `high`；官方还有 low、medium、xhigh、max、auto（官方默认 auto） | openai_image.py；官方指南 |
| 张数 | `n` 不写是 1（官方 1–10）；第 2 张起存成 `<name>_2.png`…… | openai_image.py；官方 |
| 输入图 | 官方最多 16 张，多了后端当场拒；按顺序是提示词里的 image 1、image 2…… | 官方；openai_image.py |
| 提示词里怎么叫 | 官方提示词指南的例子写「image 1」「the second image」，说清楚哪张图里的什么东西放到哪、什么不要变；用英文写 | 官方提示词指南 |
| 拒收 | 没测 | — |
| 报错重试 | 499、502、503、504、520、522、524 和断线：后端自己隔 20 秒、40 秒再试两次；别的错照记 | openai_image.py |
| 价格 | 按 token 计费，不按张：图像 token 输入 $8、输出 $30 每百万，文本输入 $5 每百万；批量接口减半（这个后端不走批量）。一张多少用官方指南里的计算器估；每张用了多少 token 记在 `<name>.json` 的 `usage` 里。[prices.json](prices.json) 是按秒计的视频价，没有它 | [OpenAI 价格页](https://developers.openai.com/api/docs/pricing)，2026-11-22 查 |
| 出图时间 | 一张中位 25–40 秒（一次并行 4 张） | 作者实测，2026-11 |
| 这个后端实测 | 改图一张（1 张输入图，1536x864，high）经一个兼容 OpenAI 接口的网关跑通，57 秒；文生图两张（1536x864，high）经同一类网关跑通，各约 2 分钟；没有直接对 api.openai.com 跑过 | 2026-11-22 |

画出来的图会和输入不一致（背景、站位、尺度），出图后要和白模并排看。

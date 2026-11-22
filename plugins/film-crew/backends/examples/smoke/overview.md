# smoke：每家接口一张最短的单子

一个小项目目录，三张最短的单子，没有人。Wan 3.0 那条真跑过（`send` 送到服务器一次，`run` 一次）；gpt-image 那张经兼容网关跑通过一次；MiniMax H3-Max 那张照官方文档组请求，还没有用真的 key 跑过，先拿来看 `request` 打印什么。换了机器、换了 key 或改了适配以后，照这里每家跑一条最短的。

## 单子

| 文件 | 适配 | 模型 | 要什么 |
|---|---|---|---|
| jobs/smoke_wan.json | bailian | wan3.0-video | 文生，2 秒（最短），480P，窗边冒热气的茶壶 |
| jobs/smoke_h3.json | minimax_video | MiniMax-H3-Max（单子里写 `minimax-h3`） | 文生，5 秒（最短），768P，同一个画面 |
| jobs_img/smoke_img.json | openai_image | gpt-image-2.6-sunburst（不写 `model` 时的默认） | 改图：把 media/box_wm.png（白模里一个方块）画成照片里的木箱，1536x864，high |

## 命令（在这个文件夹里）

```
python3 ../../scripts/filmgen.py request jobs/*.json jobs_img/*.json   # 先看会发什么
python3 ../../scripts/filmgen.py send . --wait 900                     # 两条视频，送到 FILM_SEND_HOST 上跑
python3 ../../scripts/filmgen.py run jobs_img/smoke_img.json --out keys # 一张图，在这台机器上出
```

`send` 之前先设 `FILM_SEND_HOST`、`FILM_SEND_REMOTE`，并在那台机器上备好 `DASHSCOPE_API_KEY`、`MINIMAX_API_KEY`；`run` 出图要这台机器上有 `OPENAI_API_KEY`（见 [../../overview.md](../../overview.md) 的「key、地址、机器」）。

## 结果

| 单子 | 结果 |
|---|---|
| smoke_wan | 2026-11-20 真跑：提交到生成完 68 秒，下载完再 3 秒；clips/smoke_wan.mp4 是 854×480、30 fps、2.02 秒、带音轨。`send` 从打包到取回共 1 分 34 秒（每 30 秒查一次），服务器上的 tmux 会话跑完自己退了。2026-11-22 在服务器上用 `run` 再跑一次（key 从 `DASHSCOPE_API_KEY` 读）：提交到下载完 92 秒，出来的片规格相同；同一天 `send` 也再送了一次，取回成功 |
| smoke_h3 | 没跑 |
| smoke_img | 2026-11-22 经一个兼容 OpenAI 接口的网关跑通（设 `OPENAI_BASE_URL`）：57 秒出一张 1536x864 的图；没有直接对 api.openai.com 跑过，结果文件没放进来 |

## 留下的

| 文件 | 是什么 |
|---|---|
| clips/smoke_wan.json | 百炼的状态文件（请求体、task_id、DOWNLOADED、ffprobe、usage、timing） |
| clips/results.jsonl | 那一条的结果（服务器上的 logs/results.jsonl，取回时挪过来） |
| clips/smoke_wan.mp4 | 成片 |
| media/box_wm.png | 改图的输入：脚本画的白模静帧 |

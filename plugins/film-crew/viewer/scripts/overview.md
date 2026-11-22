# scripts

| 文件 | 在哪跑 | 做什么 |
|---|---|---|
| [console.py](console.py) | 读得到成片和图的机器（要 Pillow、ffmpeg） | 镜头清单 → 一页展示台（几部片一页）：图转 JPEG，成片每镜抽帧，成片和预演转成网页码率；给了 `--workflows` 再加节点图，每镜嵌 `../comfyui` 写出的工作流原文。写 `index.html`、`data.json`（页面里内嵌的数据，别的页面嵌展示台时读它）和每部片一个媒体文件夹。重跑时已有的文件不重做 |
| [console_template.html](console_template.html) | — | 页面模板：样式、版面、脚本都在里面；`console.py` 把数据和媒体表填进去 |
| [progress.py](progress.py) | 拍片的机器，或经 ssh 读它的本机 | 进度页：每个单元每一次生成一格（能放的视频、状态、用了几分钟、计费几秒），现在在干什么，花了多少时间（给了价格表再写钱）。只用标准库 |
| [styles.py](styles.py) | 被上面的脚本调用 | 把 [styles/](../styles/overview.md) 里选中的风格装进一页：每套风格一块 `<style>`、它的脚本，几套时加一个切换。不选风格时不调用，页面不变 |

```bash
# 展示台 + 节点图（几部片一页；参数的意思在 console.py 开头）
python3 console.py a.shots.json b.shots.json c.shots.json site \
    --workflows <ComfyUI>/user/default/workflows/filmkit --title <页面标题> --view graph

# 片子多、要嵌进片卡页：精简，不转码（片卡上已经有视频）
python3 console.py manifests/*.shots.json site --compact --no-encode

# 进度页：每 60 秒重做一次，放进 tmux
python3 progress.py page --jobs <运行目录>/clips --prices ../backends/cards/prices.json \
    --events <运行目录>/progress.jsonl --title <片名> --every 60

# 进度页换一身样子：只给一套就一直用它；给几套，页面上多一个切换，第一套是默认
python3 progress.py page --jobs <运行目录>/clips --style warm
python3 progress.py page --jobs <运行目录>/clips --style plain,fancy,warm
```

- 清单从哪来、长什么样：`../formats/shots-manifest.md`。`console.py` 不读运行目录，也不 import `../comfyui`：工作流是读它写出来的文件（认文件里 `extra.filmkit` 的 `film`、`shot`）。
- 放进 tmux 或后台跑 `console.py` 时命令末尾加 `< /dev/null`：不然 ffmpeg 会读 stdin，把后面喂进去的命令吃掉。
- 媒体都写成 `<i data-k data-src>`，发到要签名的存储时只给 `data-src` 签名。
- 价格表的结构是 `{"wan_price_cny_per_s": {模型: {"list": {"720P": 0.6}, "discount": {…}}}}`，`../backends/cards/prices.json` 就是这个结构。不给就只写时间。

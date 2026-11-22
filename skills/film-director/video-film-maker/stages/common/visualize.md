# 可视化：随时看得到片子现在什么样

一句话：从开始生成起，开一个进度页：每个单元、每一次生成都能直接播，现在在做什么、为什么重抽、花了多少、离预算多远，一眼看到；生成后的检查图、验收的对照页也都是可视化的一部分。

## 什么时候做

- 预算报完、用户同意后，生成开始之前，把进度页启动起来，告诉用户页面在哪。
- 每做一步记一行事件：提交了什么、查出什么、为什么重抽、合格没有。
- 用户问「到哪了」，先给进度页，再用一两句话说。

## 进度页上有什么

- **故事**：一句话故事和节拍，可以收起来。
- **现在**：最近几条事件；开工多久、花了多少，对着预算的进度条。
- **一条时间线**：每个单元一格，颜色是状态：灰 待检查、蓝 生成中或检查中、绿 合格、黄 要重抽、红 失败。
- **剪出来的**：最新的几版粗剪和成片，能播。
- **各单元**：先写这一段在故事里要拍什么，下面每一次生成一个播放器，标第几次、状态、生成用了多久、计费几秒、这一次的结论；还在生成的显示已经等了多久。

## 怎么做

```bash
python3 scripts/progress.py progress/ --remote HOST --jobs "~/work/clips" --cuts "~/work/edit/**/film.mp4" \
    --events progress.jsonl --story story.md --units units.json --order U1,U2,U3 \
    --title 《片名》 --estimate-cny 146 --every 60
```

- `story.md` 放一句话故事和节拍；`units.json` 写每个单元在故事里拍什么（`{"U2": "司机从后视镜看老人，问第一句"}`）。都从计划里抄，开工前写好。
- 脚本放进 tmux 一直跑。每轮刷新都重读一遍服务器上的任务记录；每个视频只拷一次到本机。
- 页面是本机的一个 html，开着会自己刷新；有视频在播的时候不刷新。
- 事件每做一步往 `progress.jsonl` 追加一行：

  ```json
  {"t": "15:02", "unit": "U2", "take": "U2_t1", "state": "retake", "what": "第 1 次多了人声，改写声音段重抽"}
  ```

  - `state` 写结论：查完合格写 `pass`，要重抽写 `retake`，正在查写 `check`，别的写 `note`。只说单元、不说第几次时，算在这个单元最新的那一次生成上。
  - `what` 写给人看的一句话：做了什么、为什么。
- 要在别的设备上看，把整个文件夹传到 OSS；先问用户传到哪，没人回答就不传（见 [规矩](rules.md)「没人回答时」）。

## 和 film-crew 的进度页

同一个仓库里的 film-crew 插件也带一个进度页（`plugins/film-crew/viewer/scripts/progress.py`）。两个是同一套页面，参数相同（都有 `--remote`），读的都是每段视频旁边的状态文件（`NAME.json` + `NAME.mp4`）和同一份事件文件 `progress.jsonl`，换一个不用改记录。区别在：

- **本 skill 的 `scripts/progress.py`**：不装插件就能用；读 `wan.py`、`occut.py gen` 写下的任务记录，花费按本 skill 的 [budget-data.json](../../refs/practical/budget-data.json) 算；页面只有一种样子。只用本 skill 的脚本拍 Wan 3.0、HappyHorse 时用它。
- **film-crew 的**：任务交给 film-crew 的 backends 发时用它（Seedance、MiniMax 的任务也认）；花费要用 `--prices` 给一张价格表，不给只显示时间；`--style` 能换 fancy、warm 两种样子。拍完要做展示台、节点图，也在 film-crew 的 viewer 里。

## 别的可视化

- 每次生成后的检查图（切点、帧条、频谱；帧条是按时间顺序抽帧拼成的缩略图）：见 [生成后检查](../3-generation/checks.md)。
- 原片和生成逐镜对照、盲选：见 [剪辑与成片](../4-edit/overview.md)。
- 花费和预算的数字：见 [预算](budget.md)。

## 局限

- 状态只有记了才准：没记事件的单元一直是「待检查」。
- 视频都拷到本机，一部片几百 MB。
- 「生成用了多久」从提交算起，排队也算在里面。

# 刀切橙子推到果肉满屏 → 满屏橙色晚霞，拉开是海边

版本：当前推荐

微距镜头里刀切开熟透的橙子，镜头推到果肉占满画面（#1）；硬切到满屏橙色晚霞，拉开露出海边和海鸥（#2）。转场在 7.20 s。

（示例视频：ex-match-cut-01.mp4，没有放进仓库。刀切橙子推到果肉满屏 → 满屏橙色晚霞，拉开是海边（5.7–9.7 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| #1 橙子 | 文生 | 8 s | 3（第 1 次没推满；第 2 次靠自带叠化推进去，不能用；用第 3 次） |
| #2 晚霞 | 文生 | 8 s | 1 |

模型：Wan 3.0，720P。

## 提示词原文

**调用 #1 第 1 次 `a_orange`（文生，8 s，seed 41）—— 没用**

> Macro close-up, realistic cinematic food photography, one continuous shot, no cuts, no dissolves. On a dark wooden cutting board in soft warm daylight, a sharp chef's knife slices straight down through a whole ripe orange. From 0 to 2 seconds the knife cuts the orange in half and the two halves fall apart, revealing the glistening juicy flesh. From 2 to 5 seconds the camera pushes in steadily and continuously toward the cut face of one half. From 5 to 8 seconds the camera is so close that the orange flesh fills the entire frame edge to edge: only the evenly lit, bright, vivid saturated orange juicy pulp is visible, no rind, no white pith, no board, no knife, nothing else, and the camera almost stops, drifting very slowly. Sound: the crisp crunch of the knife cutting through the orange, juice dripping onto the board, a quiet kitchen, no music, no speech.

**调用 #1 第 2 次 `a_orange_v2`（文生，8 s，seed 43）—— 没用**

> Macro close-up, realistic cinematic food photography, one continuous shot, no cuts, no dissolves. On a dark wooden cutting board in soft warm daylight, a sharp chef's knife slices straight down through a whole ripe orange. From 0 to 2 seconds the knife cuts the orange in half and the two halves fall apart, revealing the glistening juicy flesh. From 2 to 5 seconds the camera pushes in steadily and continuously toward the cut face of one half, aiming at the juicy pulp of one segment halfway between the white center and the rind, and keeps going into an extreme macro. From 5 to 8 seconds the camera is so close that only the glistening juice sacs of that one segment fill the entire frame edge to edge: big, evenly lit, bright, vivid saturated orange juice vesicles everywhere; the white center, the rind, the board and the knife are all outside the frame, nothing but orange, and the camera almost stops, drifting very slowly. Sound: the crisp crunch of the knife cutting through the orange, juice dripping onto the board, a quiet kitchen, no music, no speech.

**调用 #1 第 3 次 `a_orange_v3`（文生，8 s，seed 44）—— 用的是这次**

> Macro close-up, realistic cinematic food photography, one continuous shot, no cuts, no dissolves: one single continuous camera move with no dissolve, no fade, no cut and no superimposition at any moment; never show two images at the same time. On a dark wooden cutting board in soft warm daylight, a sharp chef's knife slices straight down through a whole ripe orange. From 0 to 2 seconds the knife cuts the orange in half and the two halves fall apart, revealing the glistening juicy flesh. From 2 to 6 seconds the camera pushes in slowly, steadily and continuously, in one smooth unbroken move, toward the cut face of one half, aiming at the juicy pulp of one segment halfway between the white center and the rind, until it is an extreme macro. From 6 to 8 seconds the camera is so close that only the glistening juice sacs of that one segment fill the entire frame edge to edge: big, evenly lit, bright, vivid saturated orange juice vesicles everywhere; the white center, the rind, the board and the knife are all outside the frame, nothing but orange, and the camera almost stops, drifting very slowly. Sound: the crisp crunch of the knife cutting through the orange, juice dripping onto the board, a quiet kitchen, no music, no speech.

**调用 #2 `b_sunset`（文生，8 s，seed 42）**

> Realistic cinematic photography, one continuous shot, no cuts, no dissolves: one single continuous camera move with no fade and no superimposition at any moment. The shot opens with the entire frame filled edge to edge by a smooth glowing sunset sky of bright, vivid saturated orange, the same orange as the flesh of a ripe orange: only evenly lit orange sky is visible, no sun, no cloud edges, no horizon, nothing else. The camera holds still for the first second. From 1 to 8 seconds the camera slowly and continuously pulls back and tilts down, revealing a wide orange sunset sky over a calm sea, the low sun glowing just above the horizon, gentle waves washing onto a quiet beach, and a single seagull gliding across the sky from left to right. Sound: gentle waves on the shore, soft sea wind, one distant seagull cry, no music, no speech.

## 剪辑关键数字

- 剪点两边颜色：ΔE 9，亮度 L* 65.5 对 68.2，B 稍红。没调色、没缩放。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_orange · 文生 · 8 s · seed 41
a_orange_v2 · 文生 · 8 s · seed 43
a_orange_v3 · 文生 · 8 s · seed 44
b_sunset · 文生 · 8 s · seed 42
```

`cut.sh`：

```bash
# color_match example: orange flesh fills the frame (call #1) -> hard cut -> orange sunset sky fills the frame (call #2)
OC=scripts/occut.py
# generation, in the order it was run (jobs.json = all takes; finished jobs are not resubmitted)
python3 $OC gen jobs_take1.json clips --workers 1      # a_orange (take 1 of call #1), b_sunset (call #2)
python3 make_a_v2.py && python3 $OC gen jobs_a_v2.json clips --workers 1   # take 2: push further in (take 1 never filled the frame)
python3 make_a_v3.py && python3 $OC gen jobs_a_v3.json clips --workers 1   # take 3: no-dissolve wording (take 2 had a Wan dissolve at ~162-174)
# checks
for c in a_orange a_orange_v2 a_orange_v3 b_sunset; do python3 colorfill.py clips/$c.mp4 work/${c}_color.json 12; python3 frames.py clips/$c.mp4 0 239 8 work/${c}_overview.png 320 6; done
python3 $OC cuts clips/a_orange_v3.mp4 work/cuts_used_a_orange_v3 --start 0 --end 215
python3 $OC cuts clips/b_sunset.mp4 work/cuts_used_b_sunset --start 0 --end 239
# cut: A last frame 215 (pulp fills the frame from ~200), B first frame 0 (sky fills the frame)
python3 $OC join plan.json demo.mp4 --xfade 0.25
python3 $OC cuts demo.mp4 work/cuts_used_demo --start 0 --end 455
python3 classic/cutsheet.py demo.mp4 216 sheet.png 10 10 1 165
```

`plan.json`：

```json
[
 {"clip": "clips/a_orange_v3.mp4", "start": 0, "end": 215, "label": "Wan 调用 #1 · 文生 · 切橙子、推到果肉满屏（8s 素材，第 3 次生成）"},
 {"clip": "clips/b_sunset.mp4", "start": 0, "end": 239, "label": "Wan 调用 #2 · 文生 · 满屏橙色晚霞、拉开到海边（8s 素材）"}
]
```

不在 skill 里的一次性脚本：`make_a_v2.py`、`make_a_v3.py`、`frames.py`、`cutsheet.py`（都没有放进仓库）。

脚本：`scripts/colorfill.py`。

## 生成后检查的结果

- 满屏判断：目标颜色占比 ≥ 0.97，并且 4×8 格里最偏的一格也不偏。第 3 次占比 0.89（顶边露白色果心、两下角露一点果皮），照用了。

## 踩的坑和改法

- 推满要给足时间（≥ 4 秒），推向「中间一块」，写明哪些东西在画外，一开头就写防叠化。
- 两张同色画面之间的叠化检测器看不出来（第 2 次第 162–174 帧就是），满屏那几秒要逐帧看重影。
- B 写「the same orange as the flesh of a ripe orange」，两边颜色就对得很近。

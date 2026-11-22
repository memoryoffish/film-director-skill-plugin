# 木屋厨房颠锅抛煎饼，剪在煎饼最高点

版本：当前推荐

穿红格子衬衫的男人颠锅把煎饼抛起：正面中全景（#1）→ 他右侧约 60° 的中景（#2）。剪在煎饼最高点 3.27 s；剪点后煎饼落回锅里 15 帧，A 自己落是 16 帧。

（示例视频：ex-match-on-action-01.mp4，没有放进仓库。木屋厨房颠锅抛煎饼，剪在煎饼最高点（1.77–5.77 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| #1 a_wide | 文生 | 8 s | 1 |
| #2 b_close_ref | 参考图（只放人物：上半身、全身） | 6 s | 3（第 3 次给到 60°；第 1、2 次角度不够） |

模型：Wan 3.0，720P。

## 提示词原文

**调用 #1 `a_wide`（文生，8 s，seed 51）**

> Realistic cinematic photography, one continuous shot, no cuts, no dissolves. Wide shot, static camera at eye level from the front, showing the whole kitchen corner with plenty of space above his head. A rustic log cabin kitchen in the morning: walls of dark weathered round logs, a black cast-iron stove against the back wall, copper pots hanging on the wall, a small window on the left letting in soft morning light. A young man in his twenties with short tousled brown hair and light stubble, wearing a red plaid flannel shirt with the sleeves rolled up and dark blue jeans, stands in the middle of the kitchen facing the camera, his whole body visible, holding a black cast-iron frying pan by its long handle in his right hand, with one large golden pancake in the pan. From 0 to 3 seconds he gently shakes the pan to loosen the pancake. At 3 seconds he tosses the pancake high into the air with a quick upward flick of the pan; the pancake flies up well above his head, flipping over once in the air, and at about 4 seconds it falls back down and lands flat in the pan. From 4 to 8 seconds he grins and keeps shaking the pan gently. Sound: butter sizzling in the pan, a soft whoosh and a soft slap when the pancake lands, quiet kitchen ambience, no music, no speech.

**调用 #2 第 1 次 `b_close_ref`（参考图 图1 图2，6 s，seed 52）—— 没用**

> Realistic cinematic photography, one continuous shot, no cuts, no dissolves. Close-up from a clearly different angle than a frontal wide shot: the camera is low at the height of the frying pan, to his right side at a three-quarter angle about 45 degrees off his front, looking slightly upward; the black cast-iron frying pan, his hand and forearm, his chest and his face fill the frame, with room above his head where the pancake flies. The same rustic log cabin kitchen in the morning: walls of dark weathered round logs, copper pots hanging on the wall, a small window with soft morning light and a shelf of glass jars behind him, softly out of focus. The man in 图1 and 图2 (keep his face, skin tone, short tousled brown hair, light stubble, red plaid flannel shirt with rolled-up sleeves and dark blue jeans exactly as in 图1 and 图2; use only the person from those images, not their background) holds the same black cast-iron frying pan as in 图2 by its handle in his right hand, with one large golden pancake in it. From 0 to 1.5 seconds he gently shakes the pan. At 1.5 seconds he tosses the pancake high into the air with a quick upward flick of the pan; it flies up above his head, flipping over once, stays in the air for about 1.3 seconds, and at about 3 seconds falls back down and lands flat in the pan with a soft slap. From 3 to 6 seconds he grins and keeps shaking the pan gently. Sound: butter sizzling in the pan, a soft whoosh and a soft slap when the pancake lands, quiet kitchen ambience, no music, no speech.

**调用 #2 第 2 次 `b_close_ref_v2`（参考图 图1 图2，6 s，seed 53）—— 没用**

> Realistic cinematic photography, one continuous shot, no cuts, no dissolves. Medium close-up, a chest-up shot from a clearly different angle than a frontal wide shot: a locked-off camera on a tripod that never moves, never pulls back, never zooms and never tilts, placed at the height of his chest, to his right side at a three-quarter angle about 45 degrees off his front, looking slightly upward. The frame shows only his face, his shoulders and chest, his right hand and the black cast-iron frying pan held at chest height near the bottom edge of the frame. Behind him, softly out of focus: walls of dark weathered round logs and copper pots hanging on the wall, soft morning light from a small window. The man in 图1 and 图2 (keep his face, skin tone, short tousled brown hair, light stubble and red plaid flannel shirt with rolled-up sleeves exactly as in 图1 and 图2; use only the person from those images, not their background) holds the same black cast-iron frying pan as in 图2 by its handle in his right hand, with one large golden pancake in it. From 0 to 1.5 seconds he gently shakes the pan. At 1.5 seconds he tosses the pancake up with a quick flick of the pan: it rises to the height of his eyes, staying inside the frame, flips over once and falls straight back, landing flat in the pan with a soft slap at about 2.8 seconds; the whole flight takes about 1.3 seconds, a natural quick toss, not slow motion. From 3 to 6 seconds he grins and keeps shaking the pan gently while the camera stays exactly where it is. Sound: butter sizzling in the pan, a soft whoosh and a soft slap when the pancake lands, quiet kitchen ambience, no music, no speech.

**调用 #2 第 3 次 `b_close_ref_v3`（参考图 图1 图2，6 s，seed 54）—— 用的是这次**

> Realistic cinematic photography, one continuous shot, no cuts, no dissolves. Medium close-up side view, a chest-up shot: a locked-off camera on a tripod that never moves, never pulls back, never zooms and never tilts, placed at the height of his chest exactly at his right side, so we see him in right profile, facing the right side of the frame. The frame shows only his face in profile, his shoulder and chest, his right hand and the black cast-iron frying pan held out in front of him at chest height in the lower right part of the frame, with empty space above the pan where the pancake flies. Behind him, softly out of focus: the black cast-iron stove and its stove pipe and copper pots hanging on the dark weathered log wall of the same rustic log cabin kitchen, soft morning light. The man in 图1 and 图2 (keep his face, skin tone, short tousled brown hair, light stubble and red plaid flannel shirt with rolled-up sleeves exactly as in 图1 and 图2; use only the person from those images, not their background) holds the same black cast-iron frying pan as in 图2 by its handle in his right hand, with one large golden pancake in it. From 0 to 1.5 seconds he gently shakes the pan. At 1.5 seconds he tosses the pancake up with a quick flick of the pan: it rises to the height of his eyes, staying inside the frame, flips over once and falls straight back, landing flat in the pan with a soft slap at about 2.8 seconds; the whole flight takes about 1.3 seconds, a natural quick toss, not slow motion. From 3 to 6 seconds he grins and keeps shaking the pan gently while the camera stays exactly where it is. Sound: butter sizzling in the pan, a soft whoosh and a soft slap when the pancake lands, quiet kitchen ambience, no music, no speech.

## 剪辑关键数字

- 找剪点：煎饼的颜色 + 和抛起前那一帧比差异，追踪它的高度，剪在最高点。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_wide · 文生 · 8 s · seed 51
b_close_ref · 参考图 · 6 s · seed 52 · 参考图 = refs/ref1_upper.png, refs/ref2_full.png
b_close_ref_v2 · 参考图 · 6 s · seed 53 · 参考图 = refs/ref1_upper.png, refs/ref2_full.png
b_close_ref_v3 · 参考图 · 6 s · seed 54 · 参考图 = refs/ref1_upper.png, refs/ref2_full.png
```

`cut.sh`：

```bash
# match_on_action example: frontal medium-wide toss (call #1) -> cut at the top of the flight -> side medium shot, pancake falls into the pan (call #2)
OC=scripts/occut.py
python3 $OC gen jobs_a.json clips --workers 1                                   # call #1 a_wide
python3 refcrops.py clips/a_wide.mp4 200 refs ref1_upper:470,20,360,360 ref2_full:430,20,440,700   # person-only refs from call #1 frame 200
python3 $OC gen jobs_b.json clips --workers 1                                   # call #2 take 1 b_close_ref
python3 make_b_v2.py && python3 $OC gen jobs_b_v2.json clips --workers 1       # take 2
python3 make_b_v3.py && python3 $OC gen jobs_b_v3.json clips --workers 1       # take 3 (used)
# pancake flight: golden pixels that differ from a frame before the toss, largest blob
python3 pancake.py clips/a_wide.mp4 60 88 140 work/a_wide_pancake.json
python3 pancake.py clips/b_close_ref_v3.mp4 20 40 95 work/b_v3_pancake.json
# cut: A last frame 112 (highest point, cy=82), B first frame 70 (B apex 66-72, cy min 166 at 68)
python3 $OC cuts clips/a_wide.mp4 work/cuts_used_a_wide --start 15 --end 112
python3 $OC cuts clips/b_close_ref_v3.mp4 work/cuts_used_b_close_ref_v3 --start 70 --end 179
python3 $OC join plan.json demo.mp4 --xfade 0.25
python3 $OC cuts demo.mp4 work/cuts_used_demo --start 0 --end 207
python3 classic/cutsheet.py demo.mp4 98 sheet.png 10 10 1 165
```

`plan.json`：

```json
[
 {"clip": "clips/a_wide.mp4", "start": 15, "end": 112, "label": "Wan 调用 #1 · 文生 · 正面中全景（8s 素材）"},
 {"clip": "clips/b_close_ref_v3.mp4", "start": 70, "end": 179, "label": "Wan 调用 #2 · 参考图×2（只放人物，取自调用 #1）· 右侧约 60° 中景（6s 素材，第 3 次生成）"}
]
```

不在 skill 里的一次性脚本：`refcrops.py`、`make_b_v2.py`、`make_b_v3.py`、`pancake.py`、`cutsheet.py`（都没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`frames.py`。

## 生成后检查的结果

- 人、衣服、锅、厨房都一致。

## 踩的坑和改法

- 要的近景给成了腰以上中景（只比 A 紧约 1.6 倍），这一刀主要靠角度：Wan 给的角度和景别都偏保守，写 45° 只给 15–30°，写正侧面才给到 60°。
- 抛起的东西会让镜头上摇、后拉去跟，要写死三脚架机位。
- 飞起的东西在 Wan 里会在最高处悬停，按时间归一找剪点会对错，剪在最高点更稳。
- 第 3 次里煎饼每 5 帧有 2–3 帧停住，下落有点卡（3.27–3.83 s）。

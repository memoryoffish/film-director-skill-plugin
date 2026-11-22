# 黄昏走进石头过道，推开尽头的门到海边柠檬树露台

版本：当前推荐

黄昏不点灯的石头过道越走越暗，尽头是一扇关紧的门、门缝漏一点光；接缝在 9.00 s（最暗处）；#2 续写推开门，光慢慢变亮，外面是海边的柠檬树露台。

（示例视频：ex-doorway-01.mp4，没有放进仓库。黄昏走进石头过道，推开尽头的门到海边柠檬树露台（7.5–11.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 | 用到 |
|---|---|---|---|---|
| #1 过道 | 文生 | 9 s | 3（前两次是阴天白天的过道和楼梯，不够暗） | 到最暗处 |
| #2 推门 | 续写（参考视频 = #1 第 180–269 帧） | 8 s | 1 | 复述段之后 |

模型：Wan 3.0，720P，共 4 次。

## 提示词原文

**调用 #1 第 1 次 `a_passage`（文生，9 s，seed 501，没用上）**

> Cinematic live-action film footage, soft overcast daylight, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A narrow cobbled lane in an old hillside village of whitewashed stone houses under a soft grey sky. A woman in her thirties with a long dark braid, wearing a rust-orange wool coat, dark grey trousers and brown leather boots, carrying a small wicker basket in her right hand, walks away from the camera up the lane to an old, heavy wooden door in a thick stone wall. The camera follows close behind her at walking pace. At 2 seconds she pushes the door open and steps through into a long, narrow, windowless stone passage, and the camera follows her through the doorway. Inside, the only light is the daylight coming in through the door behind them; the far end of the passage is closed by a second old wooden door, so no daylight can be seen ahead. At about 5 seconds the heavy door swings shut behind them with a dull thud and the daylight is cut off; she keeps walking forward in the dark and the camera keeps following her. From 7 to 9 seconds the frame is almost completely black, with only the faintest outline of her back and of the closed wooden door in front of her. Sound: her footsteps on the cobbles, the creak of the old door, a dull thud as it closes, then her footsteps echoing softly in the stone passage, and very faintly from beyond the far door the sound of sea waves and gulls; no music of any kind: no piano, no guitar, no strings, no drums, no music box, no melody, no singing, no speech.

**调用 #1 第 2 次 `a_stairs`（文生，9 s，seed 502，没用上）**

> Cinematic live-action film footage, soft overcast daylight, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A narrow cobbled lane in an old hillside village of whitewashed stone houses under a soft grey sky. A woman in her thirties with a long dark braid, wearing a rust-orange wool coat, dark grey trousers and brown leather boots, carrying a small wicker basket in her right hand, walks away from the camera up the lane to an old, heavy wooden door in a thick stone wall. The camera follows close behind her at walking pace. At 2 seconds she pushes the door open and steps through; just inside, a steep, narrow stone staircase under a low stone vault leads straight down into the dark. She walks down the stairs and the camera follows close behind her, looking down the stairs past her shoulder. The only light is the daylight from the doorway above and behind them, and it falls away as they go down; there is no window, no opening and no light below, and the bottom of the staircase cannot be seen. From 7 to 9 seconds the frame is almost completely black, with only the faintest outline of her back and braid. Sound: her footsteps on the cobbles, the creak of the old door, then her footsteps on the stone steps echoing softly in the stairwell, and very faintly from somewhere below the sound of sea waves and gulls; no music of any kind: no piano, no guitar, no strings, no drums, no music box, no melody, no singing, no speech.

**调用 #1 第 3 次 `a_dusk`（文生，9 s，seed 503，用上了）**

> Cinematic live-action film footage, 35mm lens, one continuous shot, no cuts, no dissolves, no text. Late dusk, soft dim blue light just after sunset, no lamps lit: a narrow cobbled lane in an old hillside village of whitewashed stone houses. A woman in her thirties with a long dark braid, wearing a rust-orange wool coat, dark grey trousers and brown leather boots, carrying a small wicker basket in her right hand, walks away from the camera up the lane to an old, heavy wooden door in a thick stone wall. The camera follows close behind her at walking pace. At 2 seconds she pushes the door open and steps through into a long, narrow, windowless stone passage with a low stone vault, and the camera follows her through the doorway and deeper inside. There are no windows, no openings and no lamps in the passage; the far end is closed by a second old wooden door that is shut tight, with only a very thin, faint line of light under it. The dim dusk light from the doorway behind them fades away as they walk deeper in. From 6 seconds the passage is pitch dark, and from 7 to 9 seconds the frame is almost completely black, with only the faintest outline of her back and braid. Sound: her footsteps on the cobbles, the creak of the old door, then her footsteps echoing softly in the stone passage; no music of any kind: no piano, no guitar, no strings, no drums, no music box, no melody, no singing, no speech.

**调用 #2 `b_terrace_ext`（续写，参考视频 = a_dusk 第 180–269 帧，duration 11，seed 511）**

> 将视频1向后延长8秒。延长部分：在几乎全黑的石头过道里，穿铁锈橙色呢子大衣、拖着一条深色长辫子、右手提着小藤篮的她，继续往前走到过道尽头那扇关着的旧木门前，门的边缘透出几道细细的光，镜头保持同样的速度跟在她身后；她推开木门，门慢慢打开，外面柔和的黄昏天光一点一点照进过道，光线随着门越开越大慢慢变亮，不要突然变亮；她跨出门，来到房子背后一片朝着大海的石头露台，露台边有几棵柠檬树，远处是暮色里灰蓝色的海面和几点渔村的灯光，镜头跟着她走出门、沿着露台向前，然后慢慢停下。电影实拍质感，一镜到底，没有剪辑，没有叠化，没有跳变，没有文字。声音：过道里脚步的回声，木门吱呀一声被推开，接着海浪声和远处海鸥的叫声慢慢变大，没有音乐，没有钢琴，没有弦乐，没有人声。

## 剪辑关键数字

- #1 最后 1 秒平均亮度 11.9。
- 续写把接缝提亮了（12.4 → 17.6）：剪辑里把 B 开头乘回 A/B 的亮度比，保持到 B 自己开始变亮（推门）时再用 1–1.5 秒放开，接缝看不出来。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_passage · 文生 · 9 s · seed 501
a_stairs · 文生 · 9 s · seed 502
a_dusk · 文生 · 9 s · seed 503
b_terrace_ext · 续写 · 11 s · seed 511 · 参考视频 = a_dusk_last3s.mp4
```

`cut.sh`：

```bash
# doorway_v2: what was run, in order (from this directory)
O=scripts/occut.py
python3 $O gen jobs_a.json clips --workers 1      # call 1 take 1 a_passage (seed 501): not dark, far door leaks light
python3 $O gen jobs_a_t2.json clips --workers 1   # call 1 take 2 a_stairs (seed 502): stair tunnel with the sea showing at the bottom
python3 $O gen jobs_a_t3.json clips --workers 1   # call 1 take 3 a_dusk (seed 503, dusk): used
for c in a_passage a_stairs a_dusk; do python3 v2check.py luma clips/$c.mp4 --step 0.5; python3 v2check.py dark clips/$c.mp4; python3 v2check.py music clips/$c.mp4 --spec checks/spec_$c.png; python3 $O cuts clips/$c.mp4 owncuts; done
python3 $O join plan_last3s.json a_dusk_last3s.mp4        # A frames 180-269 (last 3 s) with audio
python3 $O gen jobs_b.json clips --workers 1              # call 2 b_terrace_ext (reference_video, 11 s, seed 511)
python3 $O seam clips/a_dusk.mp4 269 clips/b_terrace_ext.mp4 seams/ --b-skip auto   # -> b_skip 90 (PSNR 23.96)
python3 $O cuts clips/b_terrace_ext.mp4 owncuts --start 90
python3 v2check.py music clips/b_terrace_ext.mp4 --spec checks/spec_b.png
python3 v2check.py luma clips/b_terrace_ext.mp4 --step 0.25
# seam luma: A 269 = 12.4, B 90 = 17.6 (x1.42) -> pull B's head down to A and let it go while the door opens
python3 lumaramp.py clips/b_terrace_ext.mp4 clips/b_terrace_ext_lm.mp4 --start 90 --gain0 0.70 --hold 1.0 --ramp 1.5
python3 $O join plan_demo.json demo.mp4                   # A 0-269 + B(lm) 90-329, labelled
python3 $O join plan_demo_nofix.json checks/demo_nofix.mp4  # same cut without the brightness fix, for comparison
python3 te_sheet.py demo.mp4 sheet.png 9.0; python3 te_sheet.py checks/demo_nofix.mp4 checks/sheet_nofix.png 9.0
```

`plan_last3s.json`：

```json
[
 {"clip": "clips/a_dusk.mp4", "start": 180, "end": 269}
]
```

`plan_demo.json`：

```json
[
 {"clip": "clips/a_dusk.mp4", "start": 0, "end": 269, "label": "Wan 调用 #1 · 文生 · 9s（暮色里走进石头过道）"},
 {"clip": "clips/b_terrace_ext_lm.mp4", "start": 90, "end": 329, "label": "Wan 调用 #2 · 续写（参考视频 = #1 最后 3 秒）· 11s（推门到海边露台）"}
]
```

不在 skill 里的一次性脚本：`v2check.py`、`lumaramp.py`、`te_sheet.py`（都没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`merge_jobs.py`。

## 生成后检查的结果

| 调用 | 第几次 | 种子 | 最后 1 秒平均亮度 | 亮像素（>100） | 结果 |
|---|---|---|---|---|---|
| #1 | 1 `a_passage`（阴天白天、直过道、身后关门） | 501 | 24.6 | 1.24 % | **不合格**：门没关；尽头的门关着，但门上方和顶上透光，暗不下去 |
| #1 | 2 `a_stairs`（阴天白天、往下的楼梯） | 502 | 29.9 | 5.92 % | **不合格**：楼梯底开了个看得见海的口子，越走越亮 |
| #1 | 3 `a_dusk`（黄昏、不点灯、尽头门关紧） | 503 | 11.9 | 0.78 % | **合格**：只有门缝几道细光 |
| 第一版 | `a_cave_v3` | 42 | 16.0 | 1.67 % | 对照：出口一直看得见 |
| #2 | 1 `b_terrace_ext` | 511 | — | — | **合格**：PSNR 23.96，场景分 0.055；亮度跳 1.42 倍，在剪辑里补；推门后约 3.5 秒从 19 升到 100 |

## 踩的坑和改法

- 第一版要「洞里转弯、看不到尽头」，四次都没做成；改成「尽头一扇关着的门」，出口就看不见了。
- 阴天白天的过道走到底只降到亮度 25；写「黄昏、不点灯」才够暗。
- A 的提示词别写门那头的东西在前面或下面：写了「下面传来海浪声」，楼梯底就开出一个看得见海的口子。
- 「门在身后关上」做不出来：镜头跟在人后面，门在镜头后面。

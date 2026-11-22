# 徒步者走进山崖洞穴，出来是瀑布山谷

版本：反面案例

背橙色背包的徒步者走进山崖上的天然洞穴，#2 续写走出洞口是瀑布山谷。接缝在 8.00 s（洞里最暗处），能看出来。

（示例视频：ex-doorway-03.mp4，没有放进仓库。徒步者走进山崖洞穴，出来是瀑布山谷（6.5–10.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| #1 山洞 | 文生 | 8 s | 3（提示词一次比一次强调转弯，第三次换了种子） |
| #2 山谷 | 续写（参考视频 = #1 第 150–239 帧） | 8 s | 1 |

模型：Wan 3.0，720P。

## 提示词原文

**调用 #1 第一版 `a_cave`（文生，8 s，seed 41，没用上）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. Soft, diffused overcast light in the mountains: a steep grey rock cliff with a narrow trail along its base. A young man in a dark grey hiking jacket, khaki trousers and brown hiking boots, carrying a bright orange backpack, walks along the trail toward the mouth of a natural cave in the cliff; inside, the cave passage curves to the left, so its far end cannot be seen. The camera follows close behind him. From 3 seconds he enters the cave and the camera follows him inside and around the curve; the light falls away smoothly and the passage becomes completely dark, and from 7 to 8 seconds the frame is almost fully black with only the faintest outline of his silhouette and the orange backpack. Sound: his footsteps on gravel and rock, echoing inside the cave, and the faint distant rush of a waterfall, no music, no speech.

**调用 #1 第二版 `a_cave_v2`（文生，8 s，seed 41，没用上）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. Soft, diffused overcast light in the mountains: a steep grey rock cliff with a narrow trail along its base. A young man in a dark grey hiking jacket, khaki trousers and brown hiking boots, carrying a bright orange backpack, walks along the trail toward the dark mouth of a deep natural cave in the cliff. It is a cave, not a tunnel: no daylight and no opening can be seen inside it. A few meters inside, the cave passage bends sharply to the left, so its far end cannot be seen. The camera follows close behind him. From 3 seconds he enters the cave and the camera follows him inside and around the bend to the left; the daylight from the entrance falls away smoothly behind them and the passage becomes completely dark, and from 7 to 8 seconds the frame is almost fully black with only the faintest outline of his silhouette and the orange backpack. Sound: his footsteps on gravel and rock, echoing inside the cave, and the faint distant rush of a waterfall, no music, no speech.

**调用 #1 第三版 `a_cave_v3`（文生，8 s，seed 42，用上了）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. Soft, diffused overcast light in the mountains: a steep grey rock cliff with a narrow trail along its base. A young man in a dark grey hiking jacket, khaki trousers and brown hiking boots, carrying a bright orange backpack, walks along the trail toward the dark mouth of a deep natural cave in the cliff. Inside the cave it is pitch-dark and no daylight can be seen ahead. The camera follows close behind him. From 3 seconds he enters the cave; at about 5 seconds he turns left around a rock corner inside the cave and the camera turns left with him, so the daylight of the entrance is left behind; the light falls away smoothly and after the turn the passage is completely dark, and from 7 to 8 seconds the frame is almost fully black with only the faintest outline of his silhouette and the orange backpack. Sound: his footsteps on gravel and rock, echoing inside the cave, and the faint distant rush of a waterfall, no music, no speech.

**调用 #2 `b_valley_ext`（续写，参考视频 = a_cave_v3 第 150–239 帧，duration 11，seed 41）**

> 将视频1向后延长8秒。延长部分：穿深灰色冲锋衣、背着橙色背包的他继续沿着昏暗的弯曲洞道往前走，镜头保持同样的速度跟在他身后；前方转角处慢慢透出柔和的天光，光线随着他走近一点一点变亮，不要突然变亮；他走出洞穴的另一端，来到山崖上的一条小路，眼前是一片郁郁葱葱的绿色山谷，远处一道白色瀑布从山崖上落下，镜头跟着他沿小路向前。电影实拍质感，一镜到底，没有剪辑，没有叠化，没有文字。声音：洞里的脚步回声慢慢变成开阔的瀑布水声和鸟鸣，没有音乐，没有人声。

## 剪辑关键数字

- 出口的光约 6.5 秒内慢慢变亮。
- 续写开头复述的 3 秒整体比原片亮一倍，接缝处亮度从 11 跳到 22。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_cave · 文生 · 8 s · seed 41
a_cave_v2 · 文生 · 8 s · seed 41
a_cave_v3 · 文生 · 8 s · seed 42
b_valley_ext · 续写 · 11 s · seed 41 · 参考视频 = a_cave_v3_last3s.mp4
```

`cut.sh`：

```bash
# doorway demo: what was run, in order (from this directory)
O=scripts/occut.py
python3 $O gen jobs1.json clips --workers 1; python3 $O gen jobs1b.json clips --workers 1; python3 $O gen jobs1c.json clips --workers 1   # call 1, three versions
python3 $O join plan_last3s.json a_cave_v3_last3s.mp4       # a_cave_v3 frames 150-239
python3 $O gen jobs2.json clips --workers 1                 # call 2 b_valley_ext (reference_video, 11 s)
python3 $O seam clips/a_cave_v3.mp4 239 clips/b_valley_ext.mp4 seams/ --b-skip auto   # -> b_skip 94
python3 $O cuts clips/a_cave_v3.mp4 owncuts; python3 $O cuts clips/b_valley_ext.mp4 owncuts --start 94
python3 $O join plan_demo.json demo.mp4                     # A 0-239 + B 94-329, labelled
python3 te_sheet.py demo.mp4 sheet.png 8.0
```

`plan_last3s.json`：

```json
[
 {"clip": "clips/a_cave_v3.mp4", "start": 150, "end": 239}
]
```

`plan_demo.json`：

```json
[
 {"clip": "clips/a_cave_v3.mp4", "start": 0, "end": 239, "label": "Wan 调用 #1 · 文生 · 8s（走进山洞、变暗）"},
 {"clip": "clips/b_valley_ext.mp4", "start": 94, "end": 329, "label": "Wan 调用 #2 · 续写（参考视频 = #1 最后 3 秒）· 11s（出洞到瀑布山谷）"}
]
```

不在 skill 里的一次性脚本：`te_sheet.py`（没有放进仓库）。

## 生成后检查的结果

- 三版洞都是直的，出口一直看得见；接缝的亮度跳变看得出来。

## 踩的坑和改法

- 天然山洞上「转弯、看不到尽头」三次都没生成出来 → 用尽头一扇关着的门（案例 01）。
- 只改提示词不换种子，构图几乎不变。
- 续写在暗处会把亮度带偏 → 剪辑里把 B 开头压回 A 的亮度再慢慢放开。
- 山谷要拍出绿色用了阴天；柔和、低反差的光（黄昏或阴天）都行。

# 圆月 → 发光的圆形钟面（图形匹配）

版本：早期版本

夜空里的圆月推到画面正中（#1），硬切到同样位置的圆形钟面，镜头后拉露出夜里的火车站大厅（#2）。转场 4.00 s。

（示例视频：ex-match-cut-03.mp4，没有放进仓库。圆月推到画面正中，硬切到同样位置的圆形钟面，后拉露出火车站大厅（2.5–6.5 s））

## 模型与调用

| 调用 | 方式 | 时长 |
|---|---|---|
| #1 a_moon | 文生 | 6 s |
| #2 b_clock | 文生 | 6 s |

模型：Wan 3.0，720P，各 1 次。

## 提示词原文

**a_moon（6 s，seed 11，wan3.0-video，720P）**

> Night sky above the dark silhouette of old city rooftops. A bright full moon hangs in a clear deep navy sky. The camera slowly pushes in toward the moon and tilts up so the rooftops leave the bottom of the frame. From 4 to 6 seconds the camera holds still: the round full moon is exactly in the center of the frame, its diameter about one third of the frame height, glowing pale white with soft grey craters, surrounded only by dark navy sky. Realistic cinematic photography. Sound: soft night wind, faint distant city hum, no music, no speech.

**b_clock（6 s，seed 12）**

> The shot opens on a round illuminated white clock face exactly in the center of the frame, its diameter about one third of the frame height, glowing softly against a dark background, with slim black hands and black hour marks. The camera holds still for the first second. From 1 to 6 seconds the camera slowly pulls back and tilts down, revealing that the glowing clock hangs high on the wall of an old railway station hall at night; below it, a young woman in a long red wool coat, black ankle boots and a low dark bun, carrying a small brown leather suitcase, walks across the hall from left to right. Realistic cinematic photography. Sound: echoing station hall ambience, distant footsteps, a soft clock tick, no music, no speech.

## 剪辑关键数字

- 逐帧找画面里最大的亮圆：月亮半径 113.9 px，钟面 247.1 px，圆心几乎重合。
- 在 A 最后 2 秒加数码推镜，把月亮放大 2.169 倍对齐钟面（smoothstep，Lanczos），停 0.5 秒再切。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_moon · 文生 · 6 s · seed 11
b_clock · 文生 · 6 s · seed 12
```

`cut.sh`：

```bash
python3 circles.py clips/a_moon.mp4 150 work/a_moon_discs.json
python3 circles.py clips/b_clock.mp4 150 work/b_clock_discs.json
python3 edit.py   # push-in on A tail + occut join (plan.json)
python3 ../cutsheet.py demo.mp4 120 sheet.png 10 10
```

`plan.json`：

```json
[
 {"clip": "work/a_moon_zoom.mp4", "start": 0, "end": 119},
 {"clip": "clips/b_clock.mp4", "start": 0, "end": 134}
]
```

不在 skill 里的一次性脚本：`circles.py`、`edit.py`、`cutsheet.py`（都没有放进仓库）。

## 生成后检查的结果

- 两段都没有自带切镜。

## 踩的坑和改法

- 钟面比要求大一倍多：要对齐只能缩小 B（出黑边）或放大 A；放大 2.17 倍后月亮比原片软。

# 厨房里中年男厨师切葱，接着下锅翻炒

版本：旧版（有一处凭空出现的勺子）

#1 切葱，#2 续写倒葱、放刀、拿锅铲翻炒、颠锅。接缝在 8.00 s，场景分 0.050，人和厨房都对得上。

（示例视频：ex-extension-02.mp4，没有放进仓库。厨房里中年男厨师切葱，接着下锅翻炒（6.5–10.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| #1 切葱 | 文生 | 8 s | 1 |
| #2 翻炒 | 续写（参考视频 = #1 最后 3 秒） | 8 s | 1 |

模型：Wan 3.0，720P。

## 提示词原文

**调用 #1 `a_chop`（文生，8 s，seed 31）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A bright, sunlit home kitchen with white tiles and a window above the counter. A middle-aged man with short black hair graying at the temples, wearing a white T-shirt and a dark blue apron, stands at the counter and chops a bunch of green onions on a wooden cutting board with a chef's knife, in quick, even strokes. To his right, on the gas stove, a black wok heats with a little oil, a thin wisp of smoke rising from it. Medium shot from the front; the camera moves slowly and steadily to the right along the counter. From 0 to 6 seconds he chops the last of the green onions. From 6 to 8 seconds he sweeps the chopped green onions onto the flat of the knife blade with his left hand, lifts them and turns toward the wok. Sound: the crisp rhythmic tap of the knife on the wooden board and a soft hiss from the hot wok, no music, no speech.

**调用 #2 `b_fry_ext`（续写，参考视频 = 调用 #1 第 150–239 帧，duration 11，seed 31）**

> 将视频1向后延长8秒。延长部分：同一间明亮的家庭厨房，同一位穿白色T恤、系深蓝色围裙、头发两鬓斑白的中年男人，把刀面上切好的青葱倒进右边灶台上冒着热气的黑色炒锅里，葱一下锅就滋滋作响、冒起白烟；他放下刀，拿起锅铲快速翻炒，又握住锅柄颠了两下锅。镜头保持和视频1完全相同的速度继续缓慢向右移动，跟到灶台前，然后慢慢停下。电影实拍质感，一镜到底，没有剪辑，没有叠化，没有文字。声音：葱落进热油里滋啦一声爆响，接着是锅铲刮过铁锅的翻炒声，没有音乐，没有人声。

## 剪辑关键数字

- 复述段和原片的相似度只有 18–28 dB（常见是 32–34），最像的一帧 25 dB，照样接得上。
- 镜头不动时量不出速度比，要逐帧看动作接没接上。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_chop · 文生 · 8 s · seed 31
b_fry_ext · 续写 · 11 s · seed 31 · 参考视频 = a_chop_last3s.mp4
```

`cut.sh`：

```bash
# extension demo: what was run, in order (from this directory)
O=scripts/occut.py
python3 $O gen jobs1.json clips --workers 1                 # call 1 a_chop
python3 $O join plan_last3s.json a_chop_last3s.mp4          # A frames 150-239 (last 3 s) with audio
python3 $O gen jobs2.json clips --workers 1                 # call 2 b_fry_ext (reference_video, 11 s)
python3 $O seam clips/a_chop.mp4 239 clips/b_fry_ext.mp4 seams/ --b-skip auto   # -> b_skip 87
python3 $O cuts clips/a_chop.mp4 owncuts; python3 $O cuts clips/b_fry_ext.mp4 owncuts --start 87
python3 $O join plan_demo.json demo.mp4                     # A 0-239 + B 87-329, labelled
python3 te_sheet.py demo.mp4 sheet.png 8.0
```

`plan_last3s.json`：

```json
[
 {"clip": "clips/a_chop.mp4", "start": 150, "end": 239}
]
```

`plan_demo.json`：

```json
[
 {"clip": "clips/a_chop.mp4", "start": 0, "end": 239, "label": "Wan 调用 #1 · 文生 · 8s（切葱）"},
 {"clip": "clips/b_fry_ext.mp4", "start": 87, "end": 329, "label": "Wan 调用 #2 · 续写（参考视频 = #1 最后 3 秒）· 11s（下锅翻炒）"}
]
```

不在 skill 里的一次性脚本：`te_sheet.py`（没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`tonal.py`。

## 生成后检查的结果

- 接缝看不出来；一把勺子在 B 里凭空出现。

## 踩的坑和改法

- A 提前把葱倒进了锅，B 还写着「倒进锅里」，Wan 自己圆过去了：B 的提示词要看完 A 的结尾再写。
- 勺子凭空出现：B 要写明只用画面里已有的东西（见案例 01）。

# 雨夜窗前的钢琴家 → 音乐厅的掌声（声音搭桥）

版本：旧版

#1 雨夜窗前的年轻钢琴家，雨声越来越密；剪在雨声最密处，硬切到 #2 音乐厅里满音量的掌声。转场 4.87 s。

（示例视频：ex-sound-02.mp4，没有放进仓库。雨夜窗前的钢琴家 → 音乐厅的掌声（声音搭桥）（3.37–7.37 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 sb_a_window | 文生 | 8 s | 第 90–235 帧 |
| #2 sb_b_hall | 参考图（脸 600×600、上半身 540×590，截自 #1） | 8 s | 第 9–239 帧 |

模型：Wan 3.0，720P，各 1 次。

## 提示词原文

**调用 #1 `sb_a_window`（文生，8 s，seed 61，720P，16:9，audio true，prompt_extend 关）**

> Cinematic live-action film footage, night, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A small dark apartment room at night. A young male pianist in his mid-twenties, with short wavy black hair, clean-shaven, wearing a black suit jacket over a white shirt with an open collar, sits quietly on a piano bench beside a closed upright piano, facing a tall window on the right side of the frame, so we see his face in three-quarter view, softly lit by a small warm lamp. Rain beats against the window glass; raindrops and streams of water run down the pane, the city lights outside are blurred. He does not play; his hands rest on his knees and he sits still, watching the rain. From 0 to 8 seconds the camera slowly pushes in from a medium shot to a close-up of his face beside the window. The rain grows steadily heavier and denser: from 0 to 3 seconds scattered drops tap on the glass, from 3 to 6 seconds the rain thickens, from 6 to 8 seconds a dense hammering downpour drums on the glass. Sound: rain on the window glass growing steadily denser and louder, from a light scattered patter to a dense roaring downpour of countless drops from 6 seconds to the end, no music, no piano notes, no instruments, no speech.

**调用 #2 `sb_b_hall`（参考图 图1 `refs/ref1_face.png`、图2 `refs/ref2_upper.png`，8 s，seed 62，720P，16:9，audio true，prompt_extend 关）**

> Cinematic live-action film footage, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A large concert hall brightly lit by warm golden stage lights, a full audience in red velvet seats. The young man in 图1 and 图2 (keep his face, skin tone, short wavy black hair, black suit jacket and white shirt exactly as in 图1 and 图2; use only the person from those images, not their background, window, lamp, upright piano or room) has just finished playing a concert on the stage. From the very first frame the whole audience is already clapping, thunderous applause that continues without a break from 0 to 8 seconds. From 0 to 2 seconds he sits at a black concert grand piano, his hands just lifted from the keys; from 2 to 4 seconds he stands up and turns toward the audience; from 4 to 8 seconds he bows deeply and smiles. Shot from the front rows: the clapping hands of the audience in the soft-focus foreground, him on the bright stage in a medium shot, his face clearly visible; the camera is static. Sound: thunderous continuous applause of a large audience from the very first frame to the end, no music, no piano notes, no orchestra, no instruments, no speech, no shouting.

## 剪辑关键数字

- 剪点前后 RMS 一直在 −11～−17 dBFS，接缝处没掉。
- 掌声 0.30 s 才到满音量，所以 #2 从第 9 帧用。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
sb_a_window · 文生 · 8 s · seed 61
sb_b_hall · 参考图 · 8 s · seed 62 · 参考图 = refs/ref1_face.png, refs/ref2_upper.png
```

`cut.sh`：

```bash
# sound_bridge example: rain on the window (call #1) -> applause in the concert hall (call #2), cut on the sound
cd .
python3 scripts/occut.py join plan.json demo.mp4 --xfade 0.12 > join.json
```

`plan.json`：

```json
[
 {"clip": "clips/sb_a_window.mp4", "start": 90, "end": 235, "label": "Wan 调用 #1 · 文生 · 8s（雨夜窗前）"},
 {"clip": "clips/sb_b_hall.mp4", "start": 9, "end": 239, "label": "Wan 调用 #2 · 参考图（图1 脸、图2 上半身，截自 #1）· 8s（音乐厅）"}
]
```

## 生成后检查的结果

- 两段都没有音乐（频谱里只有宽带噪声）。

## 踩的坑和改法

- 响度接上了，但音色差得远（雨在 100–600 Hz，掌声在 550–1100 Hz），声音这一跳不够明显。
- #2 他背对或侧对镜头、脸小；手一直在琴键上像还在弹。

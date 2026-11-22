# 书房老人和旧怀表 ↔ 麦田里的回忆（两次光晕）

版本：当前推荐

傍晚昏暗的书房里，白发老人打开旧怀表凝视（#1）；第一次光晕闪进回忆：金色麦田里小男孩举着同一块怀表奔跑（#2）；第二次光晕更长，慢慢退回书房（回到 #1 后半段）。光晕 1：4.30–4.93 s，调用边界 4.50 s；光晕 2：8.17–9.10 s，调用边界 8.37 s。

（示例视频：ex-flash-01.mp4，没有放进仓库。书房老人和旧怀表 ↔ 麦田里的回忆（两次光晕）（3.0–10.87 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 fw_a_study | 文生 | 10 s | 第 0–138 帧、第 195–299 帧 |
| #2 fw_b_wheat | 参考图（图1 = #1 第 150 帧裁出的怀表，280×250） | 6 s | 第 60–179 帧 |

模型：Wan 3.0，720P，各生成 1 次。

## 提示词原文

**调用 #1 `fw_a_study`（文生，10 s，seed 71，720P，16:9，audio true，prompt_extend 关）**

> Cinematic live-action film footage, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A dim old study at dusk, the last amber light coming through a window, shelves of old books in shadow. An old man in his eighties with thin white hair and a short white beard, wearing a dark brown cardigan over a grey shirt, sits in a worn leather armchair. In his hand is an old brass pocket watch on a brass chain, its hinged lid engraved with a small swallow, a white enamel dial with black Roman numerals. From 0 to 3 seconds he slowly opens the lid with his thumb and holds the open watch in his palm up in front of his chest, so the watch is large and clearly visible. From 3 to 6 seconds he gazes down at the watch face without moving, and the camera slowly pushes in. From 6 to 10 seconds he slowly lifts his eyes from the watch and stares into the distance, lost in memory, his eyes glistening, a faint smile. Medium close-up from the front, his face and the watch both in the frame. Sound: a quiet room, the slow ticking of the pocket watch, a soft click when the lid opens, no music, no speech.

**调用 #2 `fw_b_wheat`（参考图 图1 `refs/ref1_watch.png`，6 s，seed 72，720P，16:9，audio true，prompt_extend 关）**

> The pocket watch in 图1 (keep the watch exactly as in 图1: its brass case, the hinged lid engraved with a swallow, the white enamel dial with black Roman numerals and the brass chain; use only the watch from that image, not the old hands, the beard, the old man or the room). A memory of a bright summer afternoon long ago. Cinematic live-action shot, one continuous shot, no cuts, no dissolves, no text, overexposed warm sunlight. A small boy about seven years old with short light brown hair, in a white shirt and brown shorts, runs through a field of tall golden wheat, holding the open pocket watch from 图1 up high in his raised right hand, the watch glinting in the sun; the handheld camera runs alongside him at his height, close enough that the watch in his hand is clearly visible. From 3 to 6 seconds he stops, brings the watch close to his face and laughs. Soft hazy glow, sun flares, warm golden tones, a dreamy memory feeling. Sound: wind rustling through the wheat, skylarks singing, his running footsteps, no music, no speech.

## 剪辑关键数字

- 光晕不到纯白（level 0.5），sin² 缓动。
- 进回忆（暗 → 亮）：提亮 6 帧 + 峰值叠化 4 帧 + 回落 9 帧 = 0.63 s。
- 回书房（亮 → 暗）：回落 18 帧 = 0.93 s，声音交叉 0.6 s。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
fw_a_study · 文生 · 10 s · seed 71
fw_b_wheat · 参考图 · 6 s · seed 72 · 参考图 = refs/ref1_watch.png
```

`cut.sh`：

```bash
# flash_white example: study (call #1) -> bloom -> wheat-field memory (call #2) -> longer bloom -> study (call #1, later part)
cd .
E=scripts/optical_edit.py
python3 make_plan.py
python3 $E plan.json demo.mp4 > /dev/null
python3 $E noglow_plan.json check/noglow.mp4 > /dev/null
```

`plan.json`：

```json
{
 "segments": [
  {"clip": "clips/fw_a_study.mp4", "start": 0, "end": 138, "call": 1, "label": "Wan 调用 #1 · 文生 · 10s（书房）"},
  {"clip": "clips/fw_b_wheat.mp4", "start": 60, "end": 179, "call": 2, "label": "Wan 调用 #2 · 参考图（图1 怀表，截自 #1）· 6s（回忆）"},
  {"clip": "clips/fw_a_study.mp4", "start": 195, "end": 299, "call": 1, "label": "Wan 调用 #1 · 文生 · 10s（书房，从 6.5s 接着用）"}
 ],
 "transitions": [
  {"type": "bloom", "rise": 6, "overlap": 4, "fall": 9, "level": 0.5, "sfx": true, "sfx_db": 0},
  {"type": "bloom", "rise": 6, "overlap": 4, "fall": 18, "level": 0.5, "sfx": true, "sfx_db": 0, "audio_xfade": 0.6}
 ]
}
```

不在 skill 里的一次性脚本：`make_plan.py`（没有放进仓库）。

## 生成后检查的结果

- 两段都没有自带切镜。

## 踩的坑和改法

- 只锁一块怀表也行：原生小图 280×250 就够，写「use only the watch from that image, not the old hands, the beard …」，表盖图案、表盘、表链都保住了。
- 提示词里描述图案的词会被画进场景：写了表盖上刻着燕子，麦田上空就飞过一只燕子。
- 书房和麦田两段都生成了配乐（写了 no music 也有）。

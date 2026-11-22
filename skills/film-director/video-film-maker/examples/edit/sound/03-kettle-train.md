# 厨房水壶尖啸 → 站台机车汽笛（声音搭桥）

版本：早期版本

#1 她在厨房，水壶在身边尖啸；接缝处接 #2 她在站台、机车鸣笛。转场 4.00 s，画面剪点和声音搭桥在同一处。

（示例视频：ex-sound-03.mp4，没有放进仓库。声音搭桥：厨房水壶尖啸 → 站台机车汽笛（2.5–6.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 sb2_a_kitchen | 文生 | 8 s | 第 105–224 帧 |
| #2 sb2_b_platform | 参考图（上半身、腰以下，截自 #1） | 8 s | 第 50–169 帧 |

模型：Wan 3.0，720P，各 1 次。

## 提示词原文

**调用 #1 `sb2_a_kitchen`（文生，8 s，seed 51，720P，audio true）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no text. Early morning in a small old kitchen with pale blue tiles. A young woman in a long red wool coat, black ankle boots and a low dark bun, no hat, stands beside an old gas stove, her small brown leather suitcase on the floor beside her; on the stove a dented stainless steel kettle sits on a blue gas flame. At first the camera shows her full figure from head to boots; from 0 to 5 seconds the camera slowly pushes in until she and the kettle fill the frame in a medium close-up, her face clearly visible in three-quarter view as she buttons her coat. At 5 seconds a strong jet of white steam shoots from the kettle's spout and it starts to whistle; from 5.5 to 8 seconds it whistles loudly and continuously, a piercing high-pitched shriek, and she turns her head to look at it. Sound: gas burner hissing and water rumbling, then a loud piercing kettle whistle from 5 seconds to the end, no music, no speech.

**调用 #2 `sb2_b_platform`（参考图 图1 `refs/ref_upper.png`、图2 `refs/ref_full.png`，8 s，seed 52，720P，16:9，audio true）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no text. A country railway station platform in the morning; a vintage black steam locomotive stands at the platform. From the very first frame a thick jet of white steam bursts from the brass whistle on top of its boiler and the whistle blows a loud, long, piercing shriek from 0 to 3 seconds; from 3 seconds the locomotive starts to pull away slowly to the right, puffing steam. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or kitchen), no hat, stands on the platform in the foreground holding the suitcase, watching the locomotive, her face visible in three-quarter view. Wide shot, the camera is static. Sound: a loud long steam whistle from 0 to 3 seconds, then rhythmic chugging and hissing steam, no music, no speech.

## 剪辑关键数字

- #1 的声音在剪点后多留 0.12 s 淡出，#2 的声音从剪点淡入 0.12 s。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
sb2_a_kitchen · 文生 · 8 s · seed 51
sb2_b_platform · 参考图 · 8 s · seed 52 · 参考图 = refs/ref_upper.png, refs/ref_full.png
```

实际跑的：

```bash
python3 scripts/occut.py join plan.json demo.mp4 --xfade 0.12
```

`plan.json`：

```json
[
 {"clip": "clips/sb2_a_kitchen.mp4", "start": 105, "end": 224, "label": "Wan 调用 #1 · 文生 · 8s"},
 {"clip": "clips/sb2_b_platform.mp4", "start": 50, "end": 169, "label": "Wan 调用 #2 · 参考图（图1 上半身、图2 腰以下，取自调用 #1）· 8s"}
]
```

## 生成后检查的结果

- 用到的片段里没有自带切镜（#2 从第 50 帧起用）。

## 踩的坑和改法

- #2 在第 40–48 帧自己叠化，残影拖到第 48 帧，就在接缝后面 → 从第 50 帧起用。

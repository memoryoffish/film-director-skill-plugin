# 红大衣的背推满画面 → 满屏红灯笼

版本：早期版本

女人穿红大衣背对镜头走在灰色街道上，镜头推到红呢子占满画面（#1）；硬切到仰拍的一片红灯笼，接着下摇露出灯笼老街（#2）。转场 4.00 s。

（示例视频：ex-match-cut-02.mp4，没有放进仓库。红大衣的背推满画面 → 满屏红灯笼，下摇露出老街（2.5–6.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| #1 a_coat | 文生 | 6 s | 1 |
| #2 b_lanterns | 文生 | 6 s | 2（第 1 次后拉时自带 2 帧叠化跳到远景） |

模型：Wan 3.0，720P。

## 提示词原文

**a_coat（6 s，seed 21，wan3.0-video，720P）**

> A grey winter street in an old European town. A young woman in a long bright red wool coat, black ankle boots and a low dark bun, carrying a small brown leather suitcase, walks away from the camera along the pavement, seen from behind at medium distance. The camera follows her and moves closer and closer to her back. From 4 to 6 seconds the camera is so close to her back that the bright red wool of her coat fills the entire frame edge to edge: only the red woollen fabric texture is visible, nothing else. Realistic cinematic photography. Sound: her footsteps on the pavement, light winter wind, no music, no speech.

**b_lanterns（v1，6 s，seed 22；只用在修之前的 demo 里）**

> The shot opens with the entire frame filled edge to edge by bright red paper lanterns, tightly packed and seen very close, only red visible. The camera holds still for the first second. From 1 to 6 seconds the camera slowly pulls back, revealing many rows of red lanterns hanging above a narrow old stone street at dusk, with a few people walking far below. Realistic cinematic photography. Sound: lanterns rustling softly in the wind, quiet evening street ambience, no music, no speech.

**b_lanterns_v2（v2，6 s，seed 22；现在的 demo 用这一版）**

> One continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. The shot opens looking up at a dense canopy of bright red paper lanterns that fills the entire frame edge to edge, tightly packed and seen very close, only red visible. The camera holds still for the first second. From 1 to 6 seconds the camera tilts down slowly and continuously, revealing many rows of red lanterns hanging above a narrow old stone street at dusk, with a few people walking far below. Realistic cinematic photography. Sound: lanterns rustling softly in the wind, quiet evening street ambience, no music, no speech.

## 剪辑关键数字

- A 第 60–179 帧 + B v2 第 0–134 帧；A 满屏红后留 12 帧再切。
- A 最后一帧色相 354.6°、偏暗；B 第一帧 357°、更亮（灯笼在发光）。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_coat · 文生 · 6 s · seed 21
b_lanterns · 文生 · 6 s · seed 22
b_lanterns_v2 · 文生 · 6 s · seed 22
```

`cut.sh`：

```bash
# 2026-11-11 own-cut fix: B is b_lanterns_v2 (regenerated, one continuous tilt-down); old demo kept as demo_before_owncut_fix.mp4
python3 scripts/occut.py gen jobs_v2.json clips/ --workers 1
python3 scripts/occut.py cuts clips/b_lanterns_v2.mp4 ../owncut_check/cm2 --start 0 --end 179
python3 scripts/occut.py join plan.json demo.mp4 --xfade 0.25
python3 ../cutsheet.py demo.mp4 120 sheet.png 10 10
```

`plan.json`：

```json
[
 {"clip": "clips/a_coat.mp4", "start": 60, "end": 179},
 {"clip": "clips/b_lanterns_v2.mp4", "start": 0, "end": 134}
]
```

不在 skill 里的一次性脚本：`cutsheet.py`（没有放进仓库）。

## 生成后检查的结果

- B v2 一镜到底的下摇，没有切镜；但开头灯笼只占约 85%，露出几块天和墙。

## 踩的坑和改法

- 从灯笼特写一路「后拉」到整条街，Wan 第一次靠叠化跳过去 → 改成「下摇」并在开头写「一个连续镜头，不许切」。

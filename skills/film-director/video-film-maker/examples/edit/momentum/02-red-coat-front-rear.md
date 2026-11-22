# 红大衣女子迈步：侧面切到前方 45° / 后方 45°

版本：早期版本

#1 侧面跟拍她迈步，#2 分两版：前方 45° 低机位、后方 45° 肩高。剪点都在 #1 迈步前倾的第 120 帧，调用边界 4.03 s。

（示例视频：ex-momentum-02.mp4，没有放进仓库。红大衣女子迈步前倾：侧面跟拍切到前方 45° 低机位（2.53–6.53 s））

当时还拍了后方版，没有放进仓库。

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 侧面 | 文生（沿用第二版） | 8 s | 到第 120 帧 |
| #2 前方版 mom_b4_front | 参考图（只放人物） | 6 s | 第 56 帧起 |
| #2 后方版 mom_b4_rear | 参考图（只放人物） | 6 s | 第 84 帧起 |

模型：Wan 3.0，720P。

## 提示词原文

**mom_b4_front（参考图，6 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A quiet sunny old-town sidewalk along a long wall of pale cream limestone blocks with a few small dark vent openings near the ground. The camera is low at knee height in front of her and off to the side, at a three-quarter front angle about 45 degrees from straight ahead, so the stone wall runs diagonally from the near edge of the frame into the distance behind her and we see her face and the front of her coat. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background) is already in the middle of a big decisive step forward at the very first frame, her body leaning forward strongly into the stride; she completes the step and walks toward and past the camera. Sound: street ambience and her footsteps, no music, no speech.

**mom_b4_rear（参考图，6 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A quiet sunny old-town sidewalk along a long wall of pale cream limestone blocks with a few small dark vent openings near the ground. The camera is at shoulder height behind her and off to the side, at a three-quarter rear angle about 45 degrees from straight behind, so the stone wall runs diagonally away into the distance ahead of her and we see her back and one side of her face. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background) is already in the middle of a big decisive step forward at the very first frame, her body leaning forward strongly into the stride; she completes the step and keeps walking away along the wall. Sound: street ambience and her footsteps, no music, no speech.


## 剪辑关键数字

- 前方版第 42→44 帧是自带的硬切（落在要用的开头），所以从第 56 帧（切换之后、步子张开）起用。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
mom_b4_front · 参考图 · 6 s · seed 7 · 参考图 = exp/r7/refs/mom_upper.png, exp/r7/refs/mom_full.png
mom_b4_rear · 参考图 · 6 s · seed 7 · 参考图 = exp/r7/refs/mom_upper.png, exp/r7/refs/mom_full.png
```

调用 #1 沿用 `exp/r5/clips/m_a.mp4`（文生，侧面）。

`demos_r9.py`：

```python
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
import occut
E = Path("exp")
C, D = E / "r9/clips", E / "r9/demos"
D.mkdir(exist_ok=True)
A = str(E / "r5/clips/m_a.mp4")
la = "Wan 调用 #1 · 文生 · 6s（侧面）"
out = {}
for tag, clip, k, cap in (("front", "mom_b4_front", 56, "前方 45° 低机位"), ("rear", "mom_b4_rear", 84, "后方 45° 肩高")):
    r = occut.join([{"clip": A, "start": 0, "end": 120, "label": la},
                    {"clip": str(C / f"{clip}.mp4"), "start": k, "end": 179,
                     "label": f"Wan 调用 #2 · 参考图（只放人物，场景用文字写）· 6s（{cap}）"}], D / f"momentum_v3_{tag}.mp4")
    out[tag] = {"demo": str(D / f"momentum_v3_{tag}.mp4"), "boundary_s": r["segments"][1]["placed_s"], "b_start": k}
fa, fps = occut.decode(C / "push_a3.mp4")
fb, _ = occut.decode(C / "push_b3_ext.mp4")
k, score = occut.match_frame(fa[-1], fb, int(6 * fps))
r = occut.join([{"clip": str(C / "push_a3.mp4"), "start": 0, "end": len(fa) - 1, "label": "Wan 调用 #1 · 文生 · 8s（黄昏，门洞内转弯、变暗）"},
                {"clip": str(C / "push_b3_ext.mp4"), "start": k + 1, "end": len(fb) - 1,
                 "label": "Wan 调用 #2 · 续写（参考视频 = #1 最后 3 秒）· 11s"}], D / "doorway_v3.mp4")
out["doorway"] = {"demo": str(D / "doorway_v3.mp4"), "boundary_s": r["segments"][1]["placed_s"], "match": [k, score]}
fd, fps = occut.decode(D / "doorway_v3.mp4", width=160)
out["doorway"]["luma"] = [round(float(f.mean()), 1) for f in fd[::15]]
json.dump(out, open(D / "r9_demos.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
```

实际跑的：

```bash
python3 demos_r9.py
```

不在 skill 里的一次性脚本：`demos_r9.py`（没有放进仓库）。

## 生成后检查的结果

- 后方版一个连续镜头，从第 84 帧（已转到后方 45°）起用。

## 踩的坑和改法

- 第一次重做参考图里放了场景截图，两版都还是侧面：**场景参考图会锁住机位** → 只放人物，场景用文字写（同样的浅色石灰岩墙和人行道，墙沿对角线延伸到远处）。
- 两个机位差不多的镜头本质上还是跳切：要有明显的视角变化，动作要大。

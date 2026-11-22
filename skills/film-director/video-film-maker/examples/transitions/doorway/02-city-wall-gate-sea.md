# 黄昏穿过城墙门洞，门洞转弯变暗，出来是海边

版本：旧版（明暗过渡可用）

红大衣女子在黄昏走进城墙门洞，门洞向左转弯、亮度从 102 平滑降到 27；接缝在最暗处 8.0 s；#2 续写，光随着她走近慢慢变亮（约 6 秒从 27 到 115）。

（示例视频：ex-doorway-02.mp4，没有放进仓库。黄昏穿过城墙门洞，最暗处接缝，续写里光随着她走近慢慢变亮（6.5–10.5 s））

## 模型与调用

| 调用 | 方式 | 时长 |
|---|---|---|
| #1 push_a3 | 文生 | 8 s |
| #2 push_b3_ext | 续写（参考视频 = #1 最后 3 秒） | 11 s |

模型：Wan 3.0，720P。

## 提示词原文

**push_a3（文生，8 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. At dusk with soft warm low light, an old stone city wall by the sea. A young woman in a long red wool coat, black ankle boots and a low dark bun, carrying a small brown leather suitcase in her right hand walks toward a deep arched gate passage in the thick wall; inside, the passage curves to the left, so its far end cannot be seen. The camera follows close behind her. From 3 seconds she enters the passage and the camera follows her inside and around the curve; the light falls away smoothly and the passage becomes completely dark, and from 7 to 8 seconds the frame is almost fully black with only the faintest outline of her silhouette. Sound: her footsteps echoing on stone, distant waves muffled by the wall, no music, no speech.

**push_b3_ext（参考视频（续写），11 s）**

> 将视频1向后延长8秒。延长部分：她继续沿着昏暗的弯道往前走，镜头保持同样的速度跟在她身后；前方转角处慢慢透出暖黄的暮光，光线随着她走近一点一点变亮，不要突然变亮；她走出门洞的另一端，来到城墙外黄昏的海边步道，平静的海面映着暮色，镜头跟着她沿步道向前。电影实拍质感，一镜到底，没有剪辑，没有叠化，没有文字。声音：石头上的脚步回声慢慢变成开阔的海浪声，没有音乐，没有人声。


## 剪辑关键数字

- 复述段对上的那一帧：第 90 帧，25.9 dB。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
push_a3 · 文生 · 8 s · seed 7
push_b3_ext · 续写 · 11 s · seed 7 · 参考视频 = push_a3_last3s.mp4
```

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

- 用到的片段逐帧查过，没有自带切换。

## 踩的坑和改法

- 更早一版正午走进门洞，墙外的海太刺眼、明暗变化太明显 → 改成黄昏、门洞转弯、续写里写「光线随着她走近一点一点变亮，不要突然变亮」。
- 最暗处没到全黑（27），转弯处还有一点光。

# 她走进隧道，从另一头走出来到海边

版本：早期版本

镜头一直跟在红大衣女子身后，她自己走进隧道口、成了背影，衬着出口的光（#1）；推镜冲向她头顶上方那片光，剪到 #2 已在隧道另一头、她继续往出口走，走出来是海边。转场 6.40 s。

（示例视频：ex-zoom-through-04.mp4，没有放进仓库。她走进隧道，推镜冲向出口的光，剪到隧道另一头继续走向海边（4.9–8.9 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 a_into_tunnel | 文生 | 8 s | 第 45–236 帧 |
| #2 b_out_ref | 参考图（截自 #1） | 8 s | 第 146–239 帧 |

模型：Wan 3.0，720P，各 1 次。

## 提示词原文

**调用 #1：a_into_tunnel（文生，8 s，生成 1 次），demo 用第 45–236 帧**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. A young woman in a long red wool coat, black ankle boots and a low dark bun, carrying a small brown leather suitcase in her right hand, walks away from the camera along an old disused railway track through a green summer valley, toward the round dark mouth of a stone railway tunnel cut into the hillside about fifteen steps ahead of her, which sits in the center of the frame. The camera follows a few steps behind her at shoulder height the whole time, always keeping her in the middle of the frame, and never passes her. From 0 to 3 seconds she walks toward the tunnel mouth. At about 3 seconds she walks into the tunnel and the camera follows her inside. From 4 to 8 seconds she keeps walking deeper into the dark tunnel, seen from behind, a dark silhouette in the middle of the frame against the small bright round exit far ahead at the other end of the tunnel, which sits in the center of the frame just above her shoulders; her red coat is faintly lit. Sound: crickets and footsteps on gravel, then echoing footsteps inside the tunnel, no music, no speech.

**参考图**，都从调用 #1 截取，脚本是 `v3/refs.py`**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. The woman in 图1 and 图2 (keep her face, skin tone, hair, low dark bun, long red wool coat, black ankle boots and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background) walks away from the camera along the railway track inside the same dark stone railway tunnel as 图3, now near its far end, carrying the suitcase in her right hand. From the very first frame she is in the middle of the frame, seen from behind, a few steps ahead of the camera, walking toward the bright round exit of the tunnel, which is only about six steps ahead of her and sits in the center of the frame just above her shoulders. The camera follows behind her at her walking pace and never passes her. The exit grows steadily larger, and at about 3 seconds she steps out of the tunnel into dazzling daylight; the camera follows her out onto a railway track on a coastal cliff high above a deep blue sea. From 4 to 8 seconds she keeps walking along the track by the sea, and the camera follows behind her. Sound: echoing footsteps in the tunnel, fading into waves, wind and seagulls, no music, no speech.

## 剪辑关键数字

- A 最后 6 帧以光 (0.49, 0.28) 为中心放大 1.00 → 1.58 倍加径向模糊；B 前 5 帧从 0.63 倍放大回 1.00 倍。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_into_tunnel · 文生 · 8 s · seed 7
b_out_ref · 参考图 · 8 s · seed 7 · 参考图 = refs/ref1_upper.png, refs/ref2_full.png, refs/ref3_tunnel.png
```

`edit.sh`：

```bash
# zoom_through v3: Wan call #1 = a_into_tunnel (text-to-video): the camera stays behind her the whole time and she
# walks into the tunnel herself; at the cut she is a silhouette against the far exit.
# Wan call #2 = b_out_ref (reference images 图1 upper body / 图2 full body / 图3 tunnel, all cut from call #1):
# she walks on toward the exit at the other end and out onto the coast; same position, back to camera, same direction.
# Digital zoom + radial blur across the cut (HusseinsDrama recipe, as v1/v2), centred on the light above her head.
V=.
T=scripts
OCCUT=scripts/occut.py
A0=${A0:-45}; A1=${A1:-236}; B0=${B0:-146}; B1=${B1:-239}; CA=${CA:-0.49,0.28}; CB=${CB:-0.5,0.22}
cd "$V"
cat > plan.json <<JSON
[{"clip": "$V/clips/a_into_tunnel.mp4", "start": $A0, "end": $A1},
 {"clip": "$V/clips/b_out_ref.mp4", "start": $B0, "end": $B1}]
JSON
python3 "$OCCUT" join plan.json joined.mp4 > join.json            # audio crossfade 0.25 s (default)
CUT=$((A1 - A0 + 1))
python3 "$T/camfx.py" zoom joined.mp4 zoomed.mp4 --cut $CUT --n 6 --total 3.0 --shutter 2.0 \
    --ca "$CA" --cb "$CB" > fx.json
python3 "$T/camfx.py" label zoomed.mp4 demo.mp4 --cut $CUT \
    --a "Wan 调用 #1 · 文生 · 8s" --b "Wan 调用 #2 · 参考图（取自调用 #1）· 8s" > label.json
python3 "$T/camfx.py" sheet demo.mp4 sheet.png --cut $CUT --before 12 --after 12 --bottom > sheet.json
echo "cut=$CUT"
```

`plan.json`：

```json
[
 {"clip": "clips/a_into_tunnel.mp4", "start": 45, "end": 236},
 {"clip": "clips/b_out_ref.mp4", "start": 146, "end": 239}
]
```

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`grid.py`、`make_jobs.py`、`refs.py`、`wan_calls.py`。

## 生成后检查的结果

- 两段里她都在画面正中、背对镜头、往远处走，位置、朝向前后一致。

## 踩的坑和改法

- 更早一版镜头从她身边越过去、自己先冲进隧道，看不到她进去；到 #2 她又在镜头前面 → 写死「镜头一直在她身后、不超过她」。
- 隧道太短显得仓促：隧道要长。

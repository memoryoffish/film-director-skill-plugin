# 红色老火车穿过长隧道（第一版）

版本：旧版

同一组素材的第一版剪法：推镜冲向出口的小光点，#2 从出口光长到 #1 末尾出口光约 2.5 倍大的那一帧接，之后在隧道里还走了约 2.6 秒出口才长大、火车冲出。转场 8.00 s。

（示例视频：ex-zoom-through-03.mp4，没有放进仓库。红色老火车穿过长隧道（第一版）（6.5–10.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 z1_into_tunnel | 文生 | 10 s | 第 60–299 帧 |
| #2 z2_out_ref | 参考图 | 8 s | 第 48–160 帧 |

模型：Wan 3.0，720P，各 1 次。

## 提示词原文

**调用 #1：z1_into_tunnel（文生，10 s），用第 60–299 帧**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. A short vintage passenger train: a red steam locomotive with a black smokestack and brass trim pulling three red wooden carriages with cream window frames, a round red lamp on the back of the last carriage, runs away from the camera along a single railway track through a green mountain valley, toward the dark arched mouth of a long stone tunnel cut into the mountainside, which sits in the center of the frame. The camera follows a short distance behind the last carriage, slightly above its roof, the whole time, always keeping the back of the train in the middle of the frame, and never passes the train. From 0 to 2 seconds the train approaches the tunnel mouth, and at about 2 seconds it runs into the tunnel; the camera follows it inside. From 3 to 10 seconds the train runs deeper and deeper into the very long, dark tunnel, seen from behind: the back of the last red carriage is a dark shape faintly lit by its own red lamp in the lower middle of the frame. The arched tunnel is much taller than the train, and far ahead, just above the roof of the train, the far end of the tunnel is only a tiny bright point of daylight in the center of the frame. Sound: the rhythmic clatter of the wheels and the chuff of the steam engine, which become a loud echoing roar inside the tunnel, no music, no speech.

**参考图都从调用 #1 截（`refs.py 90 440 240 860 720 299`）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. The same vintage train as in 图1 (a short vintage passenger train: a red steam locomotive with a black smokestack and brass trim pulling three red wooden carriages with cream window frames, a round red lamp on the back of the last carriage; keep the train exactly as in 图1; use only the train from 图1, not its background) runs away from the camera along the track inside the same long dark stone tunnel as 图2, now near its far end. From the very first frame the camera is already inside the tunnel, a short distance behind the last carriage and slightly above its roof, with the back of the train in the lower middle of the frame and the bright arched exit of the tunnel ahead, just above the roof of the train, in the center of the frame. The camera follows the train at its speed and never passes it. The exit grows quickly larger, and at about 2 seconds the train bursts out of the tunnel into dazzling sunlight; the camera follows it out. From 3 to 8 seconds the train runs along a track high on a mountainside among huge sunlit snow-covered peaks under a deep blue sky, seen from behind, and the camera keeps following it. Sound: the loud echoing roar of the train inside the tunnel, opening out into the clatter of the wheels, the chuff of the engine and mountain wind, no music, no speech.

## 剪辑关键数字

- 推镜 + 径向模糊在剪点前后各 6 帧。
- 隧道里约 6.6 秒。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
z1_into_tunnel · 文生 · 10 s · seed 7
z2_out_ref · 参考图 · 8 s · seed 7 · 参考图 = refs/ref1_train.png, refs/ref2_tunnel.png
```

`edit.sh`：

```bash
# zoom_through example (推镜穿越, zoom-through.md 第三版 with a long tunnel).
# Wan call #1 = z1_into_tunnel (text-to-video): the camera follows behind the red vintage train into a long tunnel;
#   at the cut the far exit is a small bright point just above the train roof.
# Wan call #2 = z2_out_ref (reference images 图1 the train / 图2 inside the tunnel, both cut from call #1): near the
#   far end the train runs out into sunlit snowy mountains, the camera still behind it.
# Digital zoom + radial blur across the cut (HusseinsDrama recipe via camfx.py), centred on the exit light.
D=.
T=scripts
OCCUT=scripts/occut.py
A0=${A0:-0}; A1=${A1:-299}; B0=${B0:-0}; B1=${B1:-239}; CA=${CA:-0.5,0.36}; CB=${CB:-0.5,0.36}
cd "$D"
cat > plan.json <<JSON
[{"clip": "$D/clips/z1_into_tunnel.mp4", "start": $A0, "end": $A1},
 {"clip": "$D/clips/z2_out_ref.mp4", "start": $B0, "end": $B1}]
JSON
python3 "$OCCUT" join plan.json joined.mp4 > join.json            # audio crossfade 0.25 s (default)
CUT=$((A1 - A0 + 1))
python3 "$T/camfx.py" zoom joined.mp4 zoomed.mp4 --cut $CUT --n 6 --total 3.0 --shutter 2.0 \
    --ca "$CA" --cb "$CB" > fx.json
python3 "$T/camfx.py" label zoomed.mp4 demo.mp4 --cut $CUT \
    --a "Wan 调用 #1 · 文生 · 10s" --b "Wan 调用 #2 · 参考图（图1 火车、图2 隧道里，取自调用 #1）· 8s" > label.json
python3 "$T/camfx.py" sheet demo.mp4 sheet.png --cut $CUT --before 12 --after 12 --bottom > sheet.json
echo "cut=$CUT"
```

`plan.json`：

```json
[
 {"clip": "clips/z1_into_tunnel.mp4", "start": 60, "end": 299},
 {"clip": "clips/z2_out_ref.mp4", "start": 48, "end": 160}
]
```

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`exit_size.py`、`light.py`、`make_jobs.py`、`peek.py`、`refs.py`、`wan_calls.py`。

## 生成后检查的结果

- 光点穿过剪点一直在变大。

## 踩的坑和改法

- 推得不够远：剪过去以后还在隧道里走 2.6 秒 → 第二版直接接到车头冲出洞口。
- 主体会挡满隧道（火车）时，镜头放在它后上方，并写明拱顶比它高很多，出口的光才不会被挡住。
- #2 写了 never passes，5 秒后镜头还是越过了车尾：出隧道后约 1 秒就收。

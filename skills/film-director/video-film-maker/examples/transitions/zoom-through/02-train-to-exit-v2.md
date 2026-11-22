# 红色老火车穿过长隧道：一路推到车头冲出洞口

版本：第二版（只改剪辑）

镜头跟在火车车尾后上方开进长隧道（#1），推镜冲向远处出口的光，剪到 #2 火车头正冲出洞口那几帧，外面是阳光下的雪山。转场 8.00 s，推镜在 7.60–8.27 s。

（示例视频：ex-zoom-through-02.mp4，没有放进仓库。红色老火车穿过长隧道：一路推到车头冲出洞口（6.5–9.6 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 z1_into_tunnel | 文生 | 10 s | 第 60–299 帧 |
| #2 z2_out_ref | 参考图（火车 + 隧道里的整幅画面，都截自 #1） | 8 s | 第 100–147 帧 |

模型：Wan 3.0，720P；这一版没有新调用，重剪第一版的素材。

## 提示词原文

**调用 #1：z1_into_tunnel（文生，10 s），用第 60–299 帧**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. A short vintage passenger train: a red steam locomotive with a black smokestack and brass trim pulling three red wooden carriages with cream window frames, a round red lamp on the back of the last carriage, runs away from the camera along a single railway track through a green mountain valley, toward the dark arched mouth of a long stone tunnel cut into the mountainside, which sits in the center of the frame. The camera follows a short distance behind the last carriage, slightly above its roof, the whole time, always keeping the back of the train in the middle of the frame, and never passes the train. From 0 to 2 seconds the train approaches the tunnel mouth, and at about 2 seconds it runs into the tunnel; the camera follows it inside. From 3 to 10 seconds the train runs deeper and deeper into the very long, dark tunnel, seen from behind: the back of the last red carriage is a dark shape faintly lit by its own red lamp in the lower middle of the frame. The arched tunnel is much taller than the train, and far ahead, just above the roof of the train, the far end of the tunnel is only a tiny bright point of daylight in the center of the frame. Sound: the rhythmic clatter of the wheels and the chuff of the steam engine, which become a loud echoing roar inside the tunnel, no music, no speech.

**调用 #2：z2_out_ref（参考图，8 s），用第 100–147 帧（第一版用第 48–160 帧）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. The same vintage train as in 图1 (a short vintage passenger train: a red steam locomotive with a black smokestack and brass trim pulling three red wooden carriages with cream window frames, a round red lamp on the back of the last carriage; keep the train exactly as in 图1; use only the train from 图1, not its background) runs away from the camera along the track inside the same long dark stone tunnel as 图2, now near its far end. From the very first frame the camera is already inside the tunnel, a short distance behind the last carriage and slightly above its roof, with the back of the train in the lower middle of the frame and the bright arched exit of the tunnel ahead, just above the roof of the train, in the center of the frame. The camera follows the train at its speed and never passes it. The exit grows quickly larger, and at about 2 seconds the train bursts out of the tunnel into dazzling sunlight; the camera follows it out. From 3 to 8 seconds the train runs along a track high on a mountainside among huge sunlit snow-covered peaks under a deep blue sky, seen from behind, and the camera keeps following it. Sound: the loud echoing roar of the train inside the tunnel, opening out into the clatter of the wheels, the chuff of the engine and mountain wind, no music, no speech.

## 剪辑关键数字

- 不对称推镜：A 推到 R×0.8 倍（R = B 开头出口宽 ÷ A 末尾出口宽；这次 7.56 → 6），B 从约 0.8 倍放大回 1 倍（B 开头不低于约 0.75），剪点两边出口光一样大（204 / 206 像素）。
- B 开头的模糊和 A 最后一帧一样强。
- B 收在第 147 帧，镜头开始升高越过车顶之前。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
z1_into_tunnel · 文生 · 10 s · seed 7
z2_out_ref · 参考图 · 8 s · seed 7 · 参考图 = examples/zoom_through/refs/ref1_train.png, examples/zoom_through/refs/ref2_tunnel.png
```

`edit.sh`：

```bash
# zoom_through v2 (推镜穿越) - re-edit of round 1's two Wan calls, no new generation.
# A = ../zoom_through/clips/z1_into_tunnel.mp4 (call #1, text): the camera follows the red train into the long tunnel.
# B = ../zoom_through/clips/z2_out_ref.mp4 (call #2, reference images): near the far end, the train runs out into
#     snowy mountains.  Round 1 used B 48-160 at normal speed: after the zoom the exit light grew slowly for 2.6 s.
# This version keeps pushing until the locomotive breaks out of the tunnel:
#   HS>1: B's in-tunnel part (B0..breakout) is played HS times faster, easing to 1x over RAMP s (occut join
#         head_speed/ramp_s), so the real forward motion of call #2 continues the zoom; the train keeps its size.
#   HS=1: B starts at the breakout frame and only the digital zoom bridges the gap (brief's literal version).
# Then the digital zoom + radial blur across the cut (camfx.py zoom, centred on the exit light), then call labels.
#   A0 A1 B0 B1 HS RAMP N TOTAL CA CB OUT, or AEND NA NB BSTART for zoom2.py (env vars, defaults below)
D=.
R1=examples/zoom_through/clips
S=scripts
A0=${A0:-60}; A1=${A1:-299}; B0=${B0:-48}; B1=${B1:-150}; HS=${HS:-5}; RAMP=${RAMP:-0.62}
N=${N:-6}; TOTAL=${TOTAL:-3.0}; CA=${CA:-0.502,0.354}; CB=${CB:-0.501,0.350}; OUT=${OUT:-demo.mp4}
cd "$D"; W=work/$(basename "${OUT%.mp4}"); mkdir -p work "$(dirname "$OUT")"
cat > $W.plan.json <<JSON
[{"clip": "$R1/z1_into_tunnel.mp4", "start": $A0, "end": $A1},
 {"clip": "$R1/z2_out_ref.mp4", "start": $B0, "end": $B1, "head_speed": $HS, "ramp_s": $RAMP}]
JSON
python3 "$S/occut.py" join $W.plan.json $W.joined.mp4 > $W.join.json        # audio crossfade 0.25 s (default)
CUT=$((A1 - A0 + 1))
if [ -n "${AEND:-}" ]; then   # asymmetric zoom (zoom2.py): A pushes in to AEND over NA frames, B starts at BSTART
  python3 zoom2.py $W.joined.mp4 $W.zoomed.mp4 --cut $CUT --na ${NA:-12} --nb ${NB:-8} --a-end $AEND \
      --b-start ${BSTART:-0.8} --ca "$CA" --cb "$CB" > $W.fx.json
else
  python3 "$S/camfx.py" zoom $W.joined.mp4 $W.zoomed.mp4 --cut $CUT --n $N --total $TOTAL --shutter 2.0 \
      --ca "$CA" --cb "$CB" > $W.fx.json
fi
LB="Wan 调用 #2 · 参考图（图1 火车、图2 隧道里，取自调用 #1）· 8s"
[ "$HS" != "1" ] && LB="$LB · 开头 ${HS}× 加速"
python3 "$S/camfx.py" label $W.zoomed.mp4 "$OUT" --cut $CUT --a "Wan 调用 #1 · 文生 · 10s" --b "$LB" > $W.label.json
python3 "$S/camfx.py" sheet "$OUT" "${OUT%.mp4}_sheet.png" --cut $CUT --before 12 --after 24 --bottom > $W.sheet.json
echo "$OUT cut=$CUT ($(python3 -c "print(round($CUT/30,2))") s)"
```

实际跑的：

```bash
B0=100 B1=147 HS=1 AEND=6 NA=12 NB=8 BSTART=0.8 CA=0.502,0.352 CB=0.505,0.33 OUT=demo.mp4 ./edit.sh
```

不在 skill 里的一次性脚本：`zoom2.py`（没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`exit_size.py`。

## 生成后检查的结果

- 剪点两边出口显示大小差 ≤ 1.3 倍；推镜收住时正好车头出洞；接缝声音掉得不超过 3 dB。

## 踩的坑和改法

- 代价：车尾大小在剪点跳了约 6 倍（藏在模糊里）。
- 隧道里的时间从 6.6 秒缩到约 4.5 秒。
- 找出口光中心要框住出口，整幅最亮的 1% 会落在隧道顶灯或洞外的亮处。

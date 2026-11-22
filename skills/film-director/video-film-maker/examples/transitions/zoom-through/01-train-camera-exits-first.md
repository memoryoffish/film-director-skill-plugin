# 红色老火车：镜头先冲出隧道、回头停在洞口，火车再慢慢开出来

版本：当前推荐

镜头跟着火车车尾开进长隧道（#1），推镜冲向出口的光；剪到 #2 时镜头已独自在出口前，冲出隧道、在雪山间转身回头对着洞口停住，约 1.2 秒后火车才冒着白汽慢慢开出来。转场 8.00 s，推镜 7.60–8.27 s。

（示例视频：ex-zoom-through-01.mp4，没有放进仓库。红色老火车：镜头先冲出隧道、回头停在洞口，火车再慢慢开出来（6.5–10.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 | 用到 |
|---|---|---|---|---|
| #1 z1_into_tunnel | 文生（沿用第一轮） | 10 s | 1 | 第 60–299 帧 |
| #2 z2_exit_first | 参考图（只放火车：#1 第 90 帧裁出 420×480） | 12 s | 2（take 1 镜头前面就是火车，不合格；take 2 合格） | 第 24–329 帧 |

模型：Wan 3.0，720P。

## 提示词原文

**能用的理由：镜头一直在车尾后上方，没超过火车；出口的光一直露在车顶上方正中；隧道里约 4 秒、最后洞壁还在往后流。这几条第二版都量过，见下面清单。第一轮的提示词原文**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. A short vintage passenger train: a red steam locomotive with a black smokestack and brass trim pulling three red wooden carriages with cream window frames, a round red lamp on the back of the last carriage, runs away from the camera along a single railway track through a green mountain valley, toward the dark arched mouth of a long stone tunnel cut into the mountainside, which sits in the center of the frame. The camera follows a short distance behind the last carriage, slightly above its roof, the whole time, always keeping the back of the train in the middle of the frame, and never passes the train. From 0 to 2 seconds the train approaches the tunnel mouth, and at about 2 seconds it runs into the tunnel; the camera follows it inside. From 3 to 10 seconds the train runs deeper and deeper into the very long, dark tunnel, seen from behind: the back of the last red carriage is a dark shape faintly lit by its own red lamp in the lower middle of the frame. The arched tunnel is much taller than the train, and far ahead, just above the roof of the train, the far end of the tunnel is only a tiny bright point of daylight in the center of the frame. Sound: the rhythmic clatter of the wheels and the chuff of the steam engine, which become a loud echoing roar inside the tunnel, no music, no speech.

**take 1：seed 7（不合格）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. The camera flies fast through the last stretch of a long, dark arched stone tunnel, straight toward its exit. From the very first frame the bright arched exit of the tunnel is straight ahead in the center of the frame, glowing with dazzling daylight, about a quarter of the frame wide, framed by the dark stone walls. There is no train in front of the camera: the train is still far behind the camera, deep inside the tunnel. At about 1 second the camera bursts out of the tunnel into blinding sunlight and keeps flying forward, rising a little above the railway track, which leaves the tunnel along a ledge on a steep mountainside among huge sunlit snow-covered peaks under a deep blue sky. From 2 to 5 seconds the camera swings around in a wide, smooth half-circle and turns to look back the way it came, until it faces the tunnel: the dark arched stone portal set in a sheer rock face, snowy peaks rising above it, the empty track running out of the portal toward the camera. From 5 seconds to the end the camera stays completely still at this spot, like a tripod shot, looking at the dark portal. At about 6 seconds the same vintage train as in 图1 (a short vintage passenger train: a red steam locomotive with a black smokestack and brass trim pulling three red wooden carriages with cream window frames and grey roofs; keep the train exactly as in 图1; use only the train from 图1, not its background) slowly comes out of the dark tunnel portal, locomotive first, white steam billowing out of the portal around it, and rolls slowly along the track toward the camera, until the locomotive and the first carriage are out in the sunlight. Sound: the echoing roar inside the tunnel and a rush of wind as the camera bursts out, then only quiet mountain wind; then the deep rumble and chuff of the steam train echoing inside the tunnel, growing louder until the train comes out, its wheels clattering, no music, no speech.

**改了三处**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. A camera drone flies alone, fast, through the last stretch of a long, dark, empty arched stone railway tunnel, straight toward its exit. From the very first frame the bright arched exit is straight ahead in the center of the frame, glowing with dazzling daylight, about a quarter of the frame wide, framed by the dark stone walls; the tunnel ahead of the camera is completely empty, only the two rails running toward the light. At about 1 second the camera bursts out of the tunnel into blinding sunlight and keeps flying forward a little above the track, which leaves the tunnel along a ledge on a steep mountainside among huge sunlit snow-covered peaks under a deep blue sky. From 2 to 5 seconds the camera swings around in a wide, smooth half-circle until it faces back toward the tunnel it has just flown out of: the dark arched stone portal set in a sheer rock face, snowy peaks rising above it, the empty track running out of the portal toward the camera. From 5 seconds to the end the camera holds still at this spot, looking at the dark portal. No train is visible before 6 seconds. At about 6 seconds a train slowly comes out of the dark portal, locomotive first, white steam billowing out around it, and rolls slowly along the track toward the camera until the locomotive and the first carriage are out in the sunlight. It is the train shown in 图1 (a short vintage passenger train: a red steam locomotive with a black smokestack and brass trim pulling three red wooden carriages with cream window frames and grey roofs; 图1 shows it from behind, here it is seen from the front; keep its colours and details exactly as in 图1; use only the train from 图1, not its background). Sound: the echoing roar inside the tunnel and a rush of wind as the camera bursts out, then only quiet mountain wind; then the deep rumble and chuff of the steam train echoing inside the tunnel, growing louder until the train comes out, its wheels clattering, no music, no speech.

## 剪辑关键数字

- B 从出口已经很亮、还在洞里的第 24 帧接：出口 277 像素，A 末帧 34 像素，R = 8.1；离出洞不到 1 秒。
- 不对称推：A 最后 12 帧推到 6.5 倍（= R × 0.8），B 前 8 帧从 0.8 倍回到 1 倍，两边显示出来的出口一样大（221 / 222 像素）。
- 推近时出口从 (0.502, 0.352) 滑到 B 的位置 (0.50, 0.486)，剪点两边亮光在同一位置；不滑会跳 97 像素。
- 声音交叉 0.25 s；出洞后只剩风，火车的声音先从洞里渐响，火车再出来。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
z1_into_tunnel · 文生 · 10 s · seed 7
z2_exit_first_t1 · 参考图 · 12 s · seed 7 · 参考图 = refs/ref1_train.png
z2_exit_first_t2 · 参考图 · 12 s · seed 11 · 参考图 = refs/ref1_train.png
```

`edit.sh`：

```bash
# zoom_through v3 (推镜穿越): the push carries the camera out of the tunnel ahead of the train.
# A = ../zoom_through/clips/z1_into_tunnel.mp4 (call #1, text, round 1, reused): the camera follows the red train into
#     the long tunnel; the far exit is a small light just above the train roof.
# B = clips/$TAKE.mp4 (call #2, reference image 图1 = the train from call #1): from the first frame the camera is in the
#     last metres of the tunnel heading for the bright exit, no train ahead; it bursts out, flies on, turns to look
#     back at the portal and holds; then the train slowly comes out.
# Cut: A's last NA frames push in on the exit light to AEND x (zoom3.py, the exit glides to where it is in B with
#      GLIDE=1, so the train below it drops out of frame); B starts at frame B0 at BSTART x and eases back to 1 over NB.
#   env: TAKE A0 A1 B0 B1 NA NB AEND BSTART CA CB GLIDE OUT
D=.
R1=examples/zoom_through/clips
S=scripts
TAKE=${TAKE:-z2_exit_first_t1}; A0=${A0:-60}; A1=${A1:-299}; B0=${B0:-0}; B1=${B1:-359}
NA=${NA:-12}; NB=${NB:-8}; AEND=${AEND:-6}; BSTART=${BSTART:-0.8}; CA=${CA:-0.502,0.352}; CB=${CB:-0.5,0.45}
GLIDE=${GLIDE:-1}; OUT=${OUT:-demo.mp4}
cd "$D"; W=work/$(basename "${OUT%.mp4}"); mkdir -p work "$(dirname "$OUT")"
cat > $W.plan.json <<JSON
[{"clip": "$R1/z1_into_tunnel.mp4", "start": $A0, "end": $A1},
 {"clip": "$D/clips/$TAKE.mp4", "start": $B0, "end": $B1}]
JSON
python3 "$S/occut.py" join $W.plan.json $W.joined.mp4 > $W.join.json        # audio crossfade 0.25 s (default)
CUT=$((A1 - A0 + 1))
G=""; [ "$GLIDE" = "1" ] && G="--glide"
python3 zoom3.py $W.joined.mp4 $W.zoomed.mp4 --cut $CUT --na $NA --nb $NB --a-end $AEND --b-start $BSTART \
    --ca "$CA" --cb "$CB" $G > $W.fx.json
python3 "$S/camfx.py" label $W.zoomed.mp4 "$OUT" --cut $CUT --a "Wan 调用 #1 · 文生 · 10s" \
    --b "Wan 调用 #2 · 参考图（图1 火车，取自调用 #1）· 12s" > $W.label.json
python3 "$S/camfx.py" sheet "$OUT" "${OUT%.mp4}_sheet.png" --cut $CUT --before 12 --after 12 --bottom > $W.sheet.json
echo "$OUT cut=$CUT ($(python3 -c "print(round($CUT/30,2))") s)"
```

实际跑的：

```bash
TAKE=z2_exit_first_t2 B0=24 B1=329 AEND=6.5 CB=0.5,0.486 OUT=demo.mp4 ./edit.sh
```

不在 skill 里的一次性脚本：`zoom3.py`（没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`exit_size.py`、`make_jobs.py`、`probe.py`。

## 生成后检查的结果

- #1 沿用：镜头一直在主体后面，出口露在车顶上方（34 像素），隧道里约 4 秒，结尾洞壁还在往后流，剪点前 1.2 秒没有自带切镜。
- #2 take 2：第一帧在空隧道里、出口在正中；约 1.7 s 出洞；转身半圈后停住；火车车头在前慢慢出来，和 #1 是同一列。
- #2 第 0–8 帧曝光跳了一下，被报成很可能是切镜；逐帧看是连续的，这几帧本来也不用。

## 踩的坑和改法

- take 1 第 0 帧镜头前面就是火车车尾（图1 是背影，Wan 照着把火车放到了镜头前），后来又从另一个洞开出一列 → take 2 写明镜头独自飞、隧道是空的只有两条铁轨、「No train is visible before 6 seconds」、「图1 shows it from behind, here it is seen from the front」，并换种子。
- 参考图只放主体，不放隧道里的整幅画面（那张图里火车就在镜头前，正好和要的相反）。
- 「镜头不超过主体」只管 #1；#2 就是要镜头先出去。也不要出洞后约 1 秒就收。
- #1 里出口和火车之间要留空当，不然剪点处火车会一下子消失。
- 转身用了约 3.3 秒（要求 2–5 秒内完成），车灯 5.4 s 就在洞里亮了；停住后镜头还有很慢的前移；火车最后从镜头左边擦过，在擦过时收住。火车有点玩具感，白汽偏卡通。

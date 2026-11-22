# 晨雾松林 → 升到云海之上 → 扎进云里 → 落到日出雪山顶

版本：当前推荐

戴红头巾的登山者：#1 晨雾松林，#2 镜头升过树冠到云海之上、结尾一头扎进满屏的云，#3 从云里降到日出的雪山顶。接缝 2.00 s（#1→#2）、9.97 s（#2→#3，在满屏的云里），都是同一帧硬切。

（示例视频：ex-bridge-01.mp4，没有放进仓库。晨雾松林 → 升到云海之上 → 扎进云里 → 落到日出雪山顶（0.5–4.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 b1_forest | 文生 | 6 s | 第 120–179 帧 |
| #2 b2_rise | 首帧 = #1 第 179 帧 | 8 s | 第 1–239 帧 |
| #3 b3_descend | 首帧 = #2 第 239 帧（满屏是云） | 8 s | 第 1–239 帧 |

模型：Wan 3.0，720P，各生成 1 次。

## 提示词原文

**#1 b1_forest（文生，6 s，16:9），用第 120–179 帧**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. Early morning in a dense pine forest on a mountainside, filled with thick white mist. Tall straight pine trunks stand in soft receding layers of fog, pale shafts of dawn light fall between the branches, dew glistens on the needles. No people, no animals. The camera stays level, looking straight ahead. From 0 to 3 seconds it glides slowly forward between the trunks; from 3 to 6 seconds it starts to rise straight up, the trunks sliding down past the frame, and it is still rising at the last frame. Sound: quiet forest ambience, soft dripping dew and distant birdsong, no music, no speech.

**#2 b2_rise（首帧 = #1 第 179 帧，8 s），用第 1–239 帧**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. One single continuous camera move with no dissolve, no fade, no cut and no superimposition at any moment. The camera keeps rising straight up through the misty pine forest, staying level and looking straight ahead: the pine trunks slide down past the frame, and at about 1.5 seconds the camera passes up through the dense dark branches of the canopy, needles brushing past the lens. At about 2.5 seconds it breaks out above the treetops and keeps rising out of the white mist, and by 4 seconds it is high above a vast sea of soft white clouds glowing gold and pink in the sunrise, with snowy mountain peaks rising far away above the clouds. From 4 to 6 seconds the camera flies forward over the sea of clouds toward the distant peaks. From 6 to 8 seconds it dives forward and down into a thick bank of cloud, until white cloud fills the entire frame for the last second. Never show two scenes at the same time. Sound: forest ambience fading into a rising rush of wind, no music, no speech.

**#3 b3_descend（首帧 = #2 第 239 帧，满屏是云，8 s），用第 1–239 帧**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. One single continuous camera move with no dissolve, no fade, no cut and no superimposition at any moment. The first frame is the inside of a thick white cloud glowing softly with sunrise light. The camera keeps moving forward and down through the cloud; the cloud thins and tears apart into drifting wisps, and at about 2 seconds the camera comes out of the cloud, revealing a snow-covered mountain summit just below, its snow glowing pink and gold in the low sunrise. The camera keeps descending smoothly toward the summit, and from 5 to 8 seconds it arrives at eye level on the narrow snowy summit, where a lone mountaineer stands facing the rising sun: a red headscarf tied over the head, a dark grey down jacket, black climbing trousers and boots, an ice axe in one hand. The mountaineer stands still on the summit, the red headscarf fluttering in the wind. Never show two scenes at the same time. Sound: muffled wind inside the cloud, then strong open mountain wind and the faint crunch of snow, no music, no speech.

## 剪辑关键数字

- 首帧模式那一段从第 1 帧起用（第 0 帧就是上一段的最后一帧），所以两处接缝帧级一致，不用叠化。
- #3 从满屏的云起步，前 2.7 秒几乎不动，开头加速压短。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
b1_forest · 文生 · 6 s · seed 7
b2_rise · 首帧 · 8 s · seed 7 · 首帧 = refs/b1_last.png
b3_descend · 首帧 · 8 s · seed 7 · 首帧 = refs/b2_cloud.png
```

`cut.sh`：

```bash
# bridge example (首尾帧过渡段 split into calls, bridge.md 第三版).
# #1 b1_forest (text) -> #2 b2_rise (first frame = #1 frame 179, so the seam is frame-exact; #2 frame 0 is skipped)
# -> #3 b3_descend (first frame = #2 frame 239, a frame full of cloud; seam frame-exact inside the cloud, #3 frame 0
# skipped). #3 barely moves for its first ~2.7 s (first-frame mode from a textureless frame), so its head plays
# HEAD_SPEED times fast, easing back to 1x over RAMP_S output seconds (occut join head_speed / ramp_s).
D=.
OCCUT=scripts/occut.py
A0=${A0:-120}; HEAD_SPEED=${HEAD_SPEED:-3}; RAMP_S=${RAMP_S:-1.2}
cd "$D"
cat > plan.json <<JSON
[{"clip": "$D/clips/b1_forest.mp4", "start": $A0, "end": 179, "label": "Wan 调用 #1 · 文生 · 6s"},
 {"clip": "$D/clips/b2_rise.mp4", "start": 1, "end": 239, "label": "Wan 调用 #2 · 首帧（= #1 最后一帧）· 8s"},
 {"clip": "$D/clips/b3_descend.mp4", "start": 1, "end": 239, "head_speed": $HEAD_SPEED, "ramp_s": $RAMP_S,
  "label": "Wan 调用 #3 · 首帧（= #2 最后一帧，满屏是云）· 8s"}]
JSON
python3 "$OCCUT" join plan.json demo.mp4 > demo.json
python3 - <<'PY'
import json
d = json.load(open("demo.json"))
for s in d["segments"]:
    print(s["clip"].split("/")[-1], "placed_s", s["placed_s"], "frames_out", s["frames_out"])
print("duration", d["duration_s"])
PY
```

`plan.json`：

```json
[
 {"clip": "clips/b1_forest.mp4", "start": 120, "end": 179, "label": "Wan 调用 #1 · 文生 · 6s"},
 {"clip": "clips/b2_rise.mp4", "start": 1, "end": 239, "label": "Wan 调用 #2 · 首帧（= #1 最后一帧）· 8s"},
 {"clip": "clips/b3_descend.mp4", "start": 1, "end": 239, "head_speed": 3, "ramp_s": 1.2, "label": "Wan 调用 #3 · 首帧（= #2 最后一帧，满屏是云）· 8s"}
]
```

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`make_jobs.py`、`peek.py`、`sheet.py`、`wan_calls.py`。

## 生成后检查的结果

- 两处接缝都是同一帧；三段用到的范围逐帧看过。#3 开头雾在原地散开，是一个场景里的雾在散，不是两层画面叠化。

## 踩的坑和改法

- 一次首尾帧（两头差别太大）时，Wan 在中间自己叠化过去来凑尾帧，等于没有过渡 → 拆成三次调用，#2 只给首帧。
- 画面里没人时 #3 用首帧（= #2 满屏是云的最后一帧），云里的接缝就帧级一致。
- 从满屏的云起步会慢：开头加速，或首帧挑云还在动的那一帧。

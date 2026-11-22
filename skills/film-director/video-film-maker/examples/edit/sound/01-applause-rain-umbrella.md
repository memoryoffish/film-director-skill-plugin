# 音乐厅的掌声 → 雨夜里雨点打在伞面上（声音搭桥）

版本：当前推荐

#1 音乐厅里她在台上，观众雷动的掌声；剪在掌声最密处，接 #2 雨夜里雨点密密打在她的伞面上。转场 7.30 s，两边都看得见声音来源、都是正脸。

（示例视频：ex-sound-01.mp4，没有放进仓库。音乐厅的掌声 → 雨夜里雨点打在伞面上（声音搭桥）（5.8–9.8 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| #1 音乐厅 | 文生 | 10 s | 2 |
| #2 雨夜伞 | 参考图（截自 #1 第 255 帧） | 8 s | 3 |

模型：Wan 3.0，720P，共 5 次。

## 提示词原文

**第 1 次（种子 2101）的提示词**

> Cinematic live-action film footage, warm golden stage light, long lens, one continuous shot, no cuts, no dissolves, no text. A large concert hall at the end of a piano recital. A young woman pianist in her late twenties, with a short straight black bob haircut and a blunt fringe, wearing a long-sleeved dark emerald-green velvet dress stands on the bright stage beside a black concert grand piano, facing the audience and the camera; she has finished playing, her hands are away from the keys. The whole audience is clapping. Shot from the middle of the audience at standing eye level through a long lens: in the lower part of the frame, in the soft-focus foreground, the raised hands of many audience members clap hard and fast, always in motion and clearly visible; beyond them she stands in the center of the frame, seen from the waist up, her face clearly visible and well lit. From 0 to 3 seconds she stands still with her hands at her sides and looks out at the audience, moved; from 3 to 5 seconds she bows deeply; from 5 to 10 seconds she straightens up and smiles warmly straight toward the camera, her hands held together at her chest. The camera pushes in very slowly toward her over the clapping hands, which stay in the foreground until the last frame. Sound: thunderous applause of a large audience, countless hands clapping fast, dense and continuous from the very first frame to the last frame without fading, growing even louder at the end, no music, no piano notes, no instruments, no cheering, no whistling, no speech.

**第 3 次的提示词**

> Cinematic live-action film footage, night, 35mm lens, one continuous shot, no cuts, no dissolves, no text. Heavy rain at night on a narrow old street of wet cobblestones, lit by warm street lamps. The woman in 图1 and 图2 (keep her face, skin tone, short straight black bob with a blunt fringe and long-sleeved dark emerald-green velvet dress exactly as in 图1 and 图2; use only the person from those images, not their background, stage, piano, audience or hands) walks slowly toward the camera alone, holding a large black umbrella tilted back over her shoulder, so her face is clearly visible under it. A street lamp behind her backlights the rain: from the very first frame the rain is already pouring, hard drops hammer the taut top of the umbrella and bounce off it in a bright halo of spray, and splash in the puddles around her feet. The camera moves backward in front of her at her walking pace, at her eye level, framing her from the waist up with the whole umbrella in the frame. She looks ahead, calm, a faint smile. Sound: an extremely loud, close downpour: countless small, hard raindrops patter so fast and so densely on the taut fabric of the umbrella right above her that they merge into one continuous, bright, crisp crackling roar, already at full volume on the very first frame with no fade-in and staying at full volume to the last frame, with splashing on the cobblestones, no music, no piano notes, no instruments, no thunder, no speech.

## 剪辑关键数字

- 雨声比掌声轻约 9 dB：剪辑里给雨声 +9 dB 再加限幅；剪点后半秒比剪点前低约 3 dB，没有断。
- 声音交叉淡化 0.12 s，从剪点开始。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
sb2_a_s2101 · 文生 · 10 s · seed 2101
sb2_a_s2102 · 文生 · 10 s · seed 2102
sb2_b_s2201 · 参考图 · 8 s · seed 2201 · 参考图 = refs/sb2_a_s2102_face.png, refs/sb2_a_s2102_body.png
sb2_b_s2202 · 参考图 · 8 s · seed 2202 · 参考图 = refs/sb2_a_s2102_face.png, refs/sb2_a_s2102_body.png
sb2_b_s2203 · 参考图 · 8 s · seed 2203 · 参考图 = refs/sb2_a_s2102_face.png, refs/sb2_a_s2102_body.png
```

`cut.sh`：

```bash
# sound_bridge v2: applause (call #1, text) -> rain drumming on her umbrella (call #2, reference images cut from #1).
# The cut sits where the applause is densest (A ends at frame A1); B starts where its rain is at full level (B0).
# The rain came out ~9 dB quieter than the applause, so B's audio is raised by GAIN dB with a limiter (the take has
# single drops peaking at 0 dBFS) before the join; video is copied.  occut join: hard cut, audio crossfade 0.12 s from
# the cut (A's applause runs 0.12 s past the cut and fades, B's rain fades in from the cut).
#   A=sb2_a_s2102 B=sb2_b_s2203 A0=45 A1=263 B0=9 B1=158 GAIN=9 ./cut.sh
D=.
OCCUT=scripts/occut.py
A=${A:-sb2_a_s2102}; B=${B:-sb2_b_s2203}; A0=${A0:-45}; A1=${A1:-263}; B0=${B0:-9}; B1=${B1:-158}; GAIN=${GAIN:-9}
OUT=${OUT:-demo.mp4}
cd "$D"
ffmpeg -v error -nostdin -y -i clips/$B.mp4 -c:v copy -af "volume=${GAIN}dB,alimiter=limit=0.89:attack=5:release=50" \
    -c:a aac -b:a 192k clips/${B}_g${GAIN}.mp4
cat > plan.json <<JSON
[{"clip": "$D/clips/$A.mp4", "start": $A0, "end": $A1, "label": "Wan 调用 #1 · 文生 · 10s（音乐厅掌声）"},
 {"clip": "$D/clips/${B}_g${GAIN}.mp4", "start": $B0, "end": $B1, "label": "Wan 调用 #2 · 参考图（图1 脸、图2 上半身，截自 #1）· 8s（雨打伞面，声音 +${GAIN} dB）"}]
JSON
python3 "$OCCUT" join plan.json "$OUT" --xfade 0.12 > join.json
echo "$OUT: cut at frame $(( A1 - A0 + 1 )) = $(python3 -c "print(round(($A1 - $A0 + 1) / 30, 2))") s"
```

`plan.json`：

```json
[
 {"clip": "clips/sb2_a_s2102.mp4", "start": 45, "end": 263, "label": "Wan 调用 #1 · 文生 · 10s（音乐厅掌声）"},
 {"clip": "clips/sb2_b_s2203_g11.mp4", "start": 9, "end": 158, "label": "Wan 调用 #2 · 参考图（图1 脸、图2 上半身，截自 #1）· 8s（雨打伞面，声音 +11 dB）"}
]
```

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`make_jobs.py`、`sheet.py`、`texture.py`。

## 生成后检查的结果



## 踩的坑和改法

- 两种声音质感要像：剪点两边各 1 秒，频谱质心差 ≤ 0.5 个倍频程、频带轮廓相关 ≥ 0.5。第一版（雨 → 掌声）质心差 1.2、相关 −0.45，这一版 0.2、0.64。
- 都是「无数细小撞击」、主频相近的一对最稳。提示词能推音色：写「雨点密到连成一片明亮的噼啪声」后，质心从 640 Hz 到 970 Hz。
- 要写「already at full volume on the very first frame with no fade-in」才会一开头就满音量。
- Wan 在钢琴侧面画了很像真实品牌的字样：提示词写 unbranded / no logo。

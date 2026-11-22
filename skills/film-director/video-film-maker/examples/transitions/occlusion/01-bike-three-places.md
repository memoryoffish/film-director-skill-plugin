# 骑车女孩穿过三个地方（遮挡 + 参考图锁人物）

版本：当前推荐

戴贝雷帽的女孩骑车：城市街道 → 河边步道 → 乡间田野。两个遮挡转场：5.30–5.47 s 货车车厢挡住、12.87–13.03 s 铁路桥墩挡住，各在盖满的帧之间叠化 6 帧。

（示例视频：ex-occlusion-01.mp4，没有放进仓库。骑车女孩穿过三个地方（遮挡 + 参考图锁人物）（3.8–7.8 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 | 用到 |
|---|---|---|---|---|
| #1 城市 | 文生 | 7 s | 2（第 1 次结尾没盖满） | 结尾被货车车厢盖满前 |
| #2 河边 | 参考图（图1 上半身、图2 全身，截自 #1） | 8 s | 2（第 2 次为门闩重抽，没变好，用第 1 次） | 开头车厢盖满 → 结尾桥墩盖满 |
| #3 田野 | 参考图 | 10 s | 1 | 开头桥墩盖满 → 第 4–6 秒停车，之后静止 |

模型：Wan 3.0（wan3.0-video，720P），共生成 5 次。

## 提示词原文

**调用 #1 第 1 次 `s1_city`（文生，7 s，seed 101，没用上）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. On a sunny morning in an old city street lined with small shops and plane trees, a young woman in her twenties in a green canvas jacket, a beige wool beret, light blue jeans and white sneakers, with a small brown leather bag across her body, riding an old-fashioned black city bicycle with a wicker basket on the front, rides steadily from left to right along the bike lane. The camera tracks sideways alongside her, moving smoothly to the right at her riding pace and keeping her in the middle of the frame, her face in clear profile. From 0 to 5 seconds she simply rides. From 5 to 7 seconds the camera keeps moving right at exactly the same speed while the plain, flat, windowless dark navy side of the cargo box of a parked box truck, in deep shadow, out of focus, so close to the lens that it is wider and taller than the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark navy paint of the cargo box, edge to edge, with no windows, no wheels and nothing else visible. Sound: only the natural sounds of the street: light city traffic, the soft whir of her bicycle chain and her tyres on the asphalt; no music of any kind: no piano, no guitar, no strings, no drums, no music box, no melody, no singing, no speech.

**调用 #1 第 2 次 `s1_city_t2`（文生，7 s，seed 102，用上了）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. On a sunny morning in an old city street lined with small shops and plane trees, a young woman in her twenties in a green canvas jacket, a beige wool beret, light blue jeans and white sneakers, with a small brown leather bag across her body, riding an old-fashioned black city bicycle with a wicker basket on the front, rides steadily from left to right along the bike lane. The camera tracks sideways alongside her, moving smoothly to the right at her riding pace and keeping her in the middle of the frame, her face in clear profile. From 0 to 5 seconds she simply rides. From 5 to 7 seconds the camera keeps moving right at exactly the same speed while the plain, flat, windowless dark navy side of the cargo box of a parked box truck, in deep shadow, out of focus, so close to the lens that it fills the whole frame from top to bottom, with its lower edge, its wheels and the road always below the bottom of the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark navy paint of the cargo box, edge to edge, with no windows, no wheels and nothing else visible. Sound: raw on-location ambient sound only, recorded live in the street: light city traffic, the soft whir of her bicycle chain and her tyres on the asphalt. There is no background score and no music at all: no piano, no guitar, no strings, no melody, no singing, no speech.

**调用 #2 第 1 次 `s2_river`（参考图 图1、图2，8 s，seed 201，用上了）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. The first frame is fully covered by the blurred, plain, flat, windowless dark navy side of a truck's cargo box very close to the lens, in deep shadow and out of focus, with the tops of its black wheels along the bottom edge of the frame. The camera keeps moving to the right; from the very first frame the cargo box slides out of the frame to the left, revealing a riverside promenade in soft morning sun, a row of willow trees along the path and the calm wide river behind it. The young woman in 图1 and 图2 (keep her face, skin tone, hair, green canvas jacket, beige wool beret, light blue jeans, white sneakers, small brown leather bag and old-fashioned black bicycle with a wicker basket exactly as in 图1 and 图2; use only the woman and her bicycle from those images, not their background or street), rides the bicycle steadily from left to right in the middle of the frame along the promenade, and the camera keeps tracking alongside her at her riding pace. From 1 to 6 seconds she rides on along the river; ahead, the promenade passes under an old railway bridge. From 6 to 8 seconds the camera keeps moving right at exactly the same speed while an enormous, very wide, plain dark grey concrete pillar of the railway bridge, in deep shadow, out of focus, so close to the lens that it is wider and taller than the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred, smooth dark grey concrete of the pillar, edge to edge, with nothing else visible. Sound: gentle river water, birdsong and the soft whir of her bicycle chain; no music of any kind: no piano, no guitar, no strings, no drums, no music box, no melody, no singing, no speech.

**只改开头第一句，照 A 剪点帧实际画出来的样子写，其余和第 1 次相同**

> The first frame is fully covered by the flat, windowless dark navy side of a box truck's cargo box very close to the lens, sharp and in focus, in soft shade: a vertical door seam with a dark metal latch bar near the middle, and the tops of its black wheels along the bottom edge of the frame; nothing else is visible.

**调用 #3 `s3_fields`（参考图 图1、图2，10 s，seed 301，最后一段，不遮挡）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. The first frame is fully covered by the blurred, smooth, plain dark grey concrete of an enormous bridge pillar very close to the lens, in deep shadow and out of focus, edge to edge. The camera keeps moving to the right; from the very first frame the pillar slides out of the frame to the left, revealing a narrow country road through open green fields under a soft morning sky, low hills in the distance. The young woman in 图1 and 图2 (keep her face, skin tone, hair, green canvas jacket, beige wool beret, light blue jeans, white sneakers, small brown leather bag and old-fashioned black bicycle with a wicker basket exactly as in 图1 and 图2; use only the woman and her bicycle from those images, not their background or street), rides the bicycle from left to right in the middle of the frame, and the camera keeps tracking alongside her at her riding pace. From 1 to 4 seconds she rides on. From 4 to 6 seconds she slowly brakes, the bicycle rolls to a stop and she puts her left foot down on the road; the camera slows down with her and stops moving. From 6 to 10 seconds she stays still, standing astride the stopped bicycle and looking out over the fields, and the camera holds completely still. Sound: wind over the fields, skylarks and the soft whir of her bicycle chain that fades out as she stops; no music of any kind: no piano, no guitar, no strings, no drums, no music box, no melody, no singing, no speech.

## 剪辑关键数字

- 剪点取盖满段的**最后一帧**，叠化才能做满 6 帧（工具自动取的剪点在盖满段前部，只够 2–3 帧）。
- B 开头被跳过的盖满帧之后约 1.2 秒内加速（速度比低于 0.85 才加）。
- 声音交叉淡化 0.25 s。全片 21.07 s，多出来的是结尾停车后的静止段。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
s1_city · 文生 · 7 s · seed 101
s1_city_t2 · 文生 · 7 s · seed 102
s2_river · 参考图 · 8 s · seed 201 · 参考图 = refs/ref_upper.png, refs/ref_full.png
s3_fields · 参考图 · 10 s · seed 301 · 参考图 = refs/ref_upper.png, refs/ref_full.png
s2_river_t2 · 参考图 · 8 s · seed 202 · 参考图 = refs/ref_upper.png, refs/ref_full.png
```

`cut.sh`：

```bash
# occlusion_v2: what was run, in order (from this directory)
O=scripts/occut.py
R=scripts/refcrop.py
python3 $O gen jobs_s1.json clips --workers 1        # call 1 take 1 s1_city (seed 101): music 1.5-7 s -> re-roll
python3 $O gen jobs_s1_t2.json clips --workers 1     # call 1 take 2 s1_city_t2 (seed 102, sound line reworded): used
for c in s1_city s1_city_t2; do python3 $O tail clips/$c.mp4 cuts/; python3 v2check.py music clips/$c.mp4 --spec checks/spec_$c.png; python3 $O cuts clips/$c.mp4 owncuts; done
python3 $R clips/s1_city_t2.mp4 60 390 165 300 300 refs/ref_upper.png --min 540    # 图1
python3 $R clips/s1_city_t2.mp4 60 298 160 500 500 refs/ref_full.png --min 480     # 图2
python3 make_jobs_b.py jobs_s2_t1.json 201 301 s2_river; python3 make_jobs_b.py jobs_s3_t1.json 201 301 s3_fields
python3 $O gen jobs_s2_t1.json clips --workers 1 & python3 $O gen jobs_s3_t1.json clips --workers 1; wait   # calls 2 and 3 in parallel (both only need the refs)
python3 $O gen jobs_s2_t2.json clips --workers 1     # call 2 take 2 s2_river_t2 (head written from the real A cut frame): no better, unused
python3 $O tail clips/s2_river.mp4 cuts/
python3 v2check.py match clips/s1_city_t2.mp4 194 clips/s2_river.mp4 0 3 6         # seam 1: do the two covers look alike
python3 v2check.py match clips/s2_river.mp4 236 clips/s3_fields.mp4 0 3 6          # seam 2
python3 $O seam clips/s1_city_t2.mp4 194 clips/s2_river.mp4 seams/ --b-skip 0     # speed ratio 0.751 -> head_speed 1.332
python3 $O seam clips/s2_river.mp4 238 clips/s3_fields.mp4 seams/ --b-skip 0      # speed ratio 0.411 -> head_speed 2.433
for c in s2_river s3_fields; do python3 v2check.py music clips/$c.mp4 --spec checks/spec_$c.png; python3 $O cuts clips/$c.mp4 owncuts; done
python3 v2check.py motion clips/s3_fields.mp4 7 10                                  # last shot stopped
python3 make_demo.py plan_demo.json demo.mp4                                         # labelled, 0.3 s fade in, 0.8 s fade out
python3 te_sheet.py demo.mp4 sheet.png 5.3 12.8667
```

`plan_demo.json`：

```json
[
 {"clip": "clips/s1_city_t2.mp4", "start": 30, "end": 194, "label": "Wan 调用 #1 · 文生 · 7s（城市街道）"},
 {"clip": "clips/s2_river.mp4", "start": 0, "end": 238, "dissolve": 6, "head_speed": 1.332, "ramp_s": 1.2, "label": "Wan 调用 #2 · 参考图（图1 上半身、图2 全身，取自 #1）· 8s（河边步道）"},
 {"clip": "clips/s3_fields.mp4", "start": 0, "end": 270, "dissolve": 6, "head_speed": 2.433, "ramp_s": 1.2, "label": "Wan 调用 #3 · 参考图（同上）· 10s（乡间田野，停车）"}
]
```

不在 skill 里的一次性脚本：`v2check.py`、`make_jobs_b.py`、`make_demo.py`、`te_sheet.py`（都没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`merge_jobs.py`。

## 生成后检查的结果

| 调用 | 第几次 | 种子 | 结果 |
|---|---|---|---|
| #1 | 1 `s1_city` | 101 | **不合格**：有配乐（400–2000 Hz 的窄峰从 1.5 秒连续到 7.0 秒，共 5.5 秒；频谱上 700–950 Hz、1.4–1.7 kHz 成组横线换音高）。另外只有第 200–204 帧盖满，底部露出车轮和路面。 |
| #1 | 2 `s1_city_t2` | 102 | **合格**：只在开头 0.5 秒有一点和弦，demo 不用这段。第 185–194 帧盖满，共 10 帧。底部仍露车轮，加的那句没生效。车厢是清楚的，不是虚的。 |
| #2 | 1 `s2_river` | 201 | **合格**，用上了：开头第 0–8 帧盖满。接缝 1 纹理比 0.45、ΔE 4.4，在门槛边上。结尾第 212–238 帧盖满，共 27 帧。没有配乐，人物对得上。 |
| #2 | 2 `s2_river_t2` | 202 | **没变好**，没用：开头也是清楚的车厢，但门闩在另一个位置，纹理比 0.51；跨接缝的平均像素差 18.3，第 1 次是 17.1。货车约 1.7 秒才移开；结尾的盖满断成两截。 |
| #3 | 1 `s3_fields` | 301 | **合格**：开头第 0–12 帧盖满。接缝 2 纹理比 0.48、ΔE 4.4–4.9，两边都是虚的水泥。约 6.5 秒停住，7–10 秒静止。没有配乐。 |

## 踩的坑和改法

- 第一版三个毛病：第 1 段有配乐（写了 no music 也有）→ 提示词只要现场环境声、点名排除乐器，生成后看频谱；第 2 个接缝树干从虚变实 → B 开头的遮挡物写成和 A 剪点帧一样虚、一样的材质（两处纹理比 0.45、0.48）；最后一段 6 秒没停住 → 10 秒长、第 4–6 秒停、后面静止。
- 货车三次都被画成对焦清楚、带门闩和车轮的车厢，门闩在 6 帧叠化里会淡掉，重抽 #2 也没变好。遮挡物优先选柱子、墙、桥墩。
- 第一段先查完再截参考图：它一重抽，参考图和后面所有段都得重做。
- 盖满要亲眼看四条边：底部露出车轮和路面时格子颜色差也只有 11.2。

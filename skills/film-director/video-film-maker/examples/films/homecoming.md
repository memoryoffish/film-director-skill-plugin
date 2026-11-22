# 成片《回家》：一个人走过一整年回家（4 个遮挡转场）

红大衣女子提着皮箱走过雨夜站台 → 秋林 → 黄昏雪镇 → 红灯笼夜街 → 日出海边，60 秒、1080P。镜头全程向右跟拍，每段最后约 2 秒一个巨大、虚焦、深色的东西从右边贴着镜头横穿盖满画面，下一段从同一种遮挡物开始、往左移开。

（示例视频：film-homecoming.mp4，没有放进仓库。第 1 个遮挡转场：雨夜站台的水泥柱从右边盖满画面，移开是秋林（7.9–11.9 s））

当时还做了标注版，没有放进仓库。

## 模型与调用

| 段 | 地点 | 结尾遮挡物 | 请求次数 |
|---|---|---|---|
| 1 | 雨夜站台 | 虚焦水泥柱 | 1 |
| 2 | 秋林 | 虚焦树干 | 1 |
| 3 | 黄昏雪镇 | 虚焦木屋墙角（以路人开头盖不满，换掉了） | 7 |
| 4 | 红灯笼夜街 | 虚焦木柱 | 4 |
| 5 | 日出海边 | 不遮挡，停步看海、淡出 | 7 |

模型：Wan 3.0，1080P，13–15 s 一段；第 2–5 段用第 1 段截的两张参考图（上半身、全身）锁人物；共 20 次请求。

## 提示词原文

**s1_platform（13 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no text. At night on a rainy train platform, a young woman in a long red wool coat, black ankle boots and a low dark bun, carrying a small brown leather suitcase in her right hand walks steadily from left to right along the wet concrete, which shines under the station lamps; a long train waits beside the platform. The camera tracks sideways alongside her, moving smoothly to the right at her walking pace and keeping her in the middle of the frame. From 0 to 11 seconds she simply walks while rain falls through the lamplight. From 11 to 13 seconds the camera keeps moving right at exactly the same speed while an enormous, very wide, out-of-focus dark concrete pillar of the station, in deep shadow, so close to the lens that it is wider than the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark concrete of the pillar, edge to edge, with nothing else visible. Sound: steady rain, a distant train horn and her footsteps, no music, no speech.

**s2_forest（13 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no text. The first frame is fully covered by the blurred dark concrete of an enormous pillar very close to the lens. The camera keeps moving to the right; from the very first frame the pillar slides out of the frame to the left, revealing a forest path at dawn in autumn, golden leaves on the ground and mist between the trees. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walks steadily from left to right in the middle of the frame, and the camera keeps tracking alongside her at her walking pace. From 2 to 11 seconds she walks on through the scene. From 11 to 13 seconds the camera keeps moving right at exactly the same speed while an enormous, very wide, out-of-focus dark tree trunk very close to the lens enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark bark of the trunk, edge to edge, with nothing else visible. Sound: rustling leaves, birdsong and her footsteps, no music, no speech.

**s3_snow_b（13 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no text. The first frame is fully covered by the blurred dark bark of an enormous tree trunk very close to the lens. The camera keeps moving to the right; from the very first frame the trunk slides out of the frame to the left, revealing a snowy village street at dusk, warm lights glowing in the windows of wooden houses. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walks steadily from left to right in the middle of the frame, and the camera keeps tracking alongside her at her walking pace. From 2 to 11 seconds she walks on through the scene. From 11 to 13 seconds the camera keeps moving right at exactly the same speed while an enormous, very wide, out-of-focus dark wooden wall of a house corner, in deep shadow, so close to the lens that it is wider than the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark wood of the wall, edge to edge, with nothing else visible. Sound: crunching snow under her boots and soft wind, no music, no speech.

**s4_lanterns_b（13 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no text. The first frame is fully covered by the blurred dark wood of an enormous wooden wall very close to the lens. The camera keeps moving to the right; from the very first frame the wall slides out of the frame to the left, revealing a narrow old street at night lit by rows of red paper lanterns, small stalls on both sides. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walks steadily from left to right in the middle of the frame, and the camera keeps tracking alongside her at her walking pace. From 2 to 11 seconds she walks on through the scene. From 11 to 13 seconds the camera keeps moving right at exactly the same speed while an enormous, very wide, out-of-focus dark wooden pillar of an old gateway, in deep shadow, so close to the lens that it is wider than the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark wood of the pillar, edge to edge, with nothing else visible. Sound: a soft distant crowd murmur, wind chimes and her footsteps, no music, no clear speech.

**s5_sea_c（15 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no text. The first frame is fully covered by the blurred dark wood of an enormous wooden wall very close to the lens. The camera keeps moving to the right; from the very first frame the wall slides out of the frame to the left, revealing a seaside promenade at sunrise, the calm sea and a low golden sun on the right. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walks steadily from left to right in the middle of the frame, and the camera keeps tracking alongside her at her walking pace. She walks on; from 9 seconds she slows down, stops at the railing, sets the suitcase down beside her and looks out at the sea, while the camera slows down smoothly and comes to rest. Sound: gentle waves, seagulls and her footsteps, no music, no speech.


## 剪辑关键数字

- 每个接缝在两边的遮挡帧之间叠化 6 帧；B 开头被盖满的那几帧跳过，起步慢就在约 1.2 秒内加速。
- 4 个接缝的场景检测分都在 0.01 左右（硬切是 1.0）。
- 成片截到 60 秒（从头截），开头淡入 0.5 s、结尾淡出 1.5 s。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

实际跑的：

```bash
python3 scripts/occut.py chain board.json .
```

`plan.json`：

```json
[
 {"clip": "film_v2/clips/s1_platform.mp4", "start": 0, "end": 370},
 {"clip": "clips/s2_forest.mp4", "start": 0, "end": 377, "head_speed": 2.252, "ramp_s": 1.2, "dissolve": 5},
 {"clip": "clips/s3_snow_b.mp4", "start": 9, "end": 388, "head_speed": 1.359, "ramp_s": 1.2, "dissolve": 6},
 {"clip": "clips/s4_lanterns_b.mp4", "start": 0, "end": 382, "head_speed": 2.5, "ramp_s": 1.2, "dissolve": 6},
 {"clip": "clips/s5_sea_c.mp4", "start": 0, "end": 449, "dissolve": 6}
]
```

`board.json（分镜表，提示词见上）`：

```json
{
 "takes": 4,
 "window_s": 2.0,
 "target_s": 60,
 "trim_from": "start",
 "fade_in_s": 0.5,
 "fade_out_s": 1.5,
 "film_name": "homecoming_60s_refs.mp4",
 "defaults": {"model": "wan3.0-video", "resolution": "1080P", "ratio": "16:9", "audio": true, "prompt_extend": false, "seed": 11},
 "mode": "refs",
 "dissolve_frames": 6,
 "identity_refs": ["refs/ref_upper.png", "refs/ref_full.png"],
 "shots": [
  {"name": "s1_platform", "duration": 13, "use_clip": "film_v2/clips/s1_platform.mp4"},
  {"name": "s2_forest", "duration": 13, "use_clip": "clips/s2_forest.mp4"},
  {"name": "s3_snow_b", "duration": 13, "use_clip": "clips/s3_snow_b.mp4"},
  {"name": "s4_lanterns_b", "duration": 13, "use_clip": "clips/s4_lanterns_b.mp4"},
  {"name": "s5_sea_c", "duration": 15, "head_leak_max": 56}
 ]
}
```

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`label_film.py`。

## 生成后检查的结果

- 每段生成后自动查：结尾盖满、下一段开头盖满、方向一致、速度比、接缝附近没有自带切镜；不合格换种子重拍，每段最多 4 次。
- 第 3、5 段各请求了 7 次，大多是参考图模式下开头没被遮挡物盖满。

## 踩的坑和改法

- 只给首帧不给参考图时（第一版），首帧里看不清人，第 2、5 段明显换了人 → 改用参考图。
- 以路人的黑大衣开头的那段三次都没盖满：开头的遮挡物只能用物体，不能用人。
- 海边那段的木墙被日出从一侧照亮，画面是盖满的，格子颜色差却到 56，被误判成没盖满 → 受光的遮挡物要放宽门槛、人眼确认。

## 出处

运行目录里的 board.json、chain.json、wan_requests.json 和分镜表 board_homecoming_refs*.json（没有放进仓库）。

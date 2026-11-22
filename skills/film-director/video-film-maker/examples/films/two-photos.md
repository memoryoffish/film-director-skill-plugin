# 成片《两张照片》：遮挡为主，色彩匹配和声音搭桥点缀，首尾媒介转变

书桌上一张旧照片活过来（雨夜站台）→ 秋林 → 黄昏雪镇 → 红灯笼夜街 → 日出海边 → 海边的画面又变回一张照片，放在开头那张旁边。64.6 秒、1080P、7 次调用。

（示例视频：film-two-photos.mp4，没有放进仓库。首 · 媒介转变：书桌上的旧照片推满画面、活过来成了雨夜站台（3.6–7.6 s））

当时还做了标注版，没有放进仓库。

## 模型与调用

| 转场在 | 手法 |
|---|---|
| 5.10 s | 首 · 媒介转变（续写接缝，白边被推出画面，照片活过来） |
| 15.13 s | 遮挡 ①（虚焦水泥柱） |
| 25.30 s | 遮挡 ②（虚焦树干） |
| 35.83 s | 色彩匹配（红大衣的背 → 满屏红灯笼） |
| 45.50 s | 遮挡 ③（木墙）+ 声音搭桥（汽笛跨过接缝） |
| 57.27 s | 尾 · 媒介转变（续写接缝，后拉升高，变回照片） |

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| c1 书桌 | 参考图 | 6 s | 1 |
| c2 照片活过来 | 续写 c1 | 13 s | 8 |
| c3 秋林 | 参考图 | 12 s | 1 |
| c4 雪镇 | 参考图 | 11 s | 1 |
| c5 灯笼 | 参考图 | 11 s | 1 |
| c6 海边 | 参考图 | 12 s | 1 |
| c7 变回照片 | 续写 c6 | 10 s | 1 |

模型：Wan 3.0，1080P；人物用《回家》的两张参考图锁住。

## 提示词原文

**c1_desk（参考图 · 书桌旧照，6 s）**

> Cinematic live-action close-up at night, warm desk lamp light, one continuous shot, no cuts, no dissolves, no text. An old colour photograph with a thin white border lies flat on a dark wooden desk, next to a pair of reading glasses and a cup of tea, lit by the warm light of a desk lamp. The photograph shows a rainy night train platform: a green train with a yellow stripe waits beside the wet platform, which shines under the station lamps, and on the platform stands the woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background), seen from the side, full figure, in the middle of the photograph, her small brown leather suitcase standing on the ground beside her. It is a flat printed photograph: everything in it is completely still. From 0 to 6 seconds the camera moves slowly and steadily straight down toward the photograph, pushing in; by 5 seconds the photograph fills the whole frame and its white border slides out past the edges of the frame, so that in the last second only the picture inside the photograph is visible, edge to edge. Sound: a quiet room at night, a clock ticking softly, no music, no speech.

**c2_platform_e（续写 · 照片活过来 · 雨夜站台，13 s）**

> 将视频1向后延长10秒。延长部分和视频1是同一个连续镜头，镜头一直在动，没有任何剪辑、叠化或淡入淡出。延长部分第0到1秒：镜头继续慢慢向前推，相纸的白边被推出画面的四边，照片占满整个画面；白边一直是不透明的实物，不会变透明，也不会淡出。第1到3秒：占满画面的照片原地活了过来：雨丝开始落下，站台的灯光闪了几下，湿漉漉的地面泛起水光，褪色的颜色慢慢变得鲜艳真实，静止的照片就这样变成了真实的雨夜火车站台；同时照片里那位女子（同一个人，脸、深色低发髻、红色长款羊毛大衣、黑色短靴都不变）右手提着棕色小皮箱迈开步子向右走，镜头开始在她身侧向右平移跟拍，并且连续地、慢慢地往后拉开一点，露出她的全身和身后整节绿色的火车。景别的变化完全靠镜头连续后拉完成，不是叠化：画面里任何时候都只有一个画面，同一个人不会出现两次。第3到8秒：她沿着站台从画面左边向右边稳步走，镜头在她身侧向右平移跟拍，速度和她走路一样，让她一直在画面中间。第8到10秒：镜头保持同样的速度继续向右移动，一根巨大、很宽、虚焦的深色水泥柱（站台的柱子，处在深深的阴影里）离镜头非常近、比画面还宽，从画面右边进入并向左滑动，直到完全挡住整个画面；最后一帧被虚焦的深色水泥完全盖满，从边到边，什么别的都看不见。电影实拍质感。One single continuous camera move with no dissolve, no fade, no cut and no superimposition at any moment; never show two scenes at the same time; the framing changes only by the camera physically pulling back. One continuous shot, no cuts, no dissolves. Sound: steady rain, a distant train horn and her footsteps, no music, no speech.

**c3_forest（参考图 · 秋林，12 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. The first frame is fully covered by the blurred dark concrete of an enormous, very wide, out-of-focus dark concrete pillar in deep shadow, very close to the lens, wider than the frame. The camera keeps moving to the right; from the very first frame the pillar slides out of the frame to the left, revealing a forest path at dawn in autumn, golden leaves on the ground and mist between the trees. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walks steadily from left to right in the middle of the frame, and the camera keeps tracking alongside her at her walking pace. From 2 to 10 seconds she walks on along the path. From 10 to 12 seconds the camera keeps moving right at exactly the same speed while an enormous, very wide, out-of-focus dark tree trunk, in deep shadow, so close to the lens that it is wider than the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark bark of the trunk, edge to edge, with nothing else visible. Sound: rustling leaves, birdsong and her footsteps, no music, no speech.

**c4_snow（参考图 · 黄昏雪镇，11 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. The first frame is fully covered by the blurred dark bark of an enormous, very wide, out-of-focus dark tree trunk very close to the lens, wider than the frame. The camera keeps moving to the right; from the very first frame the trunk slides out of the frame to the left, revealing a snowy village street at dusk, warm lights glowing in the windows of wooden houses. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walks steadily from left to right in the middle of the frame, and the camera keeps tracking alongside her at her walking pace. From 2 to 7 seconds she walks on through the snow. From 7 to 9 seconds the camera glides smoothly around behind her and moves closer and closer to her back as she keeps walking. From 9 to 11 seconds the camera is so close to her back that the bright red wool of her coat fills the entire frame edge to edge: only the red woollen fabric texture is visible, nothing else. Sound: crunching snow under her boots and soft wind, no music, no speech.

**c5_lanterns（参考图 · 灯笼夜街，11 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. One single continuous camera move with no dissolve, no fade and no cut at any moment. The shot opens looking up at a dense canopy of glowing deep red paper lanterns that fills the entire frame edge to edge, tightly packed and seen very close, only red visible. For the first second the camera holds still on the red lanterns. From 1 to 3 seconds the camera tilts down slowly and continuously and then pulls back a little, revealing a narrow old street at night lit by rows of red paper lanterns, small stalls on both sides, and the woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walking steadily from left to right in the middle of the frame; the camera then tracks alongside her to the right at her walking pace. From 3 to 9 seconds she walks on along the street. From 9 to 11 seconds the camera keeps moving right at exactly the same speed while an enormous, very wide, out-of-focus dark wooden wall of a house corner, in deep shadow, so close to the lens that it is wider than the frame, enters from the right edge of the frame and slides left until it completely covers the entire frame. The last frame is fully covered by the blurred dark wood of the wall, edge to edge, with nothing else visible. Sound: lanterns rustling softly, a soft distant crowd murmur and her footsteps; from 8 seconds to the very end a deep, low ship horn sounds from a distant harbour, long and continuous; no music, no speech.

**c6_sea（参考图 · 日出海边，12 s）**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. The first frame is fully covered by the blurred dark wood of an enormous, very wide, out-of-focus dark wooden wall in deep shadow, very close to the lens, wider than the frame. The camera keeps moving to the right; from the very first frame the wall slides out of the frame to the left, revealing a seaside promenade at sunrise: the calm sea, a low golden sun, and a white ferry sailing slowly across the sea. The woman in 图1 and 图2 (keep her face, skin tone, hair, long red wool coat, black ankle boots, low dark bun and small brown leather suitcase exactly as in 图1 and 图2; use only the person from those images, not their background or train), carrying the suitcase in her right hand, walks steadily from left to right in the middle of the frame, and the camera keeps tracking alongside her at her walking pace. From 5 seconds she slows down, and by 7 seconds she stops at the railing, sets the suitcase down beside her and looks out at the sea, while the camera slows down smoothly and comes to rest. From 8 to 12 seconds she stands still at the railing looking out at the sea and the ferry; the camera holds still. Sound: from the very first second the deep, low horn of the ferry is still sounding, long and continuous, fading out by 3 seconds; gentle waves, seagulls and her footsteps; no music, no speech.

**c7_photo（续写 · 变回照片，10 s）**

> 将视频1向后延长7秒。延长部分和视频1是同一个连续镜头，没有剪辑，没有叠化，没有文字。延长部分第0到4秒：女子（红色长款羊毛大衣、深色低发髻，棕色小皮箱放在身边）一直静静站在栏杆边望着大海，镜头连续地慢慢向后拉、向上升高；画面四周出现相纸的白边，海边日出的整幅画面停住，变成一张静止的照片：原来它是平放在夜里木书桌上的一张照片。第4到7秒：镜头继续慢慢后拉、升高，露出更多书桌：这张海边照片的旁边放着另一张旧照片，照片里是雨夜站台上穿红大衣的她和绿色的火车；台灯的暖光照着两张照片，旁边有一副眼镜和一杯茶；最后镜头缓缓停住。电影实拍质感。One continuous shot, no cuts, no dissolves. Sound: the waves and seagulls fade away and give way to a quiet room at night with a clock ticking softly, no music, no speech.


## 剪辑关键数字

- 遮挡接缝在盖满的帧之间叠化 6 帧；c3 起步速度只有 c2 的 0.27，开头 1.2 秒内加速到 2.5 倍。
- 续写接缝：在复述还对得上（≥ 24 dB）的最后一帧剪上一段，续写从下一帧接。
- 开头淡入 0.5 s，结尾淡出 1.5 s；计划里没写目标时长，所以 64.6 秒没截。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

实际跑的：

```bash
python3 scripts/movie.py movie_two_photos.json .
```

`movie_two_photos.json（plan，提示词见上）`：

```json
{
 "title": "两张照片",
 "film_name": "two_photos",
 "identity_refs": ["film_v3/refs/ref_upper.png", "film_v3/refs/ref_full.png"],
 "defaults": {"model": "wan3.0-video", "resolution": "1080P", "ratio": "16:9", "audio": true, "prompt_extend": false, "seed": 21},
 "takes": 3,
 "workers": 4,
 "dissolve_frames": 6,
 "fade_in_s": 0.5,
 "fade_out_s": 1.5,
 "calls": [
  {"name": "c1_desk", "mode": "refs", "duration": 6, "label": "参考图 · 书桌旧照", "seam_out": {"method": "extension"}},
  {"name": "c2_platform_e", "mode": "extension", "of": "c1_desk", "input_s": 3, "duration": 13, "label": "续写 · 照片活过来 · 雨夜站台", "seam_in": {"method": "extension"}, "seam_out": {"method": "occlusion", "window_s": [11, 13]}},
  {"name": "c3_forest", "mode": "refs", "duration": 12, "label": "参考图 · 秋林", "seam_in": {"method": "occlusion"}, "seam_out": {"method": "occlusion", "window_s": [10, 12]}},
  {"name": "c4_snow", "mode": "refs", "duration": 11, "label": "参考图 · 黄昏雪镇", "seam_in": {"method": "occlusion"}, "seam_out": {"method": "color", "window_s": [9, 11]}},
  {"name": "c5_lanterns", "mode": "refs", "duration": 11, "label": "参考图 · 灯笼夜街", "seam_in": {"method": "color"}, "seam_out": {"method": "occlusion", "window_s": [9, 11], "note": "同时是声音搭桥：汽笛从 c5 结尾响过接缝，c6 开头还在响"}},
  {"name": "c6_sea", "mode": "refs", "duration": 12, "label": "参考图 · 日出海边", "seam_in": {"method": "occlusion", "note": "声音搭桥：开头汽笛还在响"}, "seam_out": {"method": "extension"}},
  {"name": "c7_photo", "mode": "extension", "of": "c6_sea", "input_s": 3, "duration": 10, "label": "续写 · 变回照片", "seam_in": {"method": "extension"}}
 ]
}
```

## 生成后检查的结果

- 每次生成后自动查它参与的接缝（盖满、满屏红、续写对得上、接缝附近有没有自带切镜），不合格换种子重拍，最多 3 次；不互相依赖的调用并行跑。

## 踩的坑和改法

- c2 生成了 8 次：前几版要么没照抄 c1 的最后 3 秒（14–16 dB，硬接会跳），要么照片变实景时整幅叠化（画面里叠着两个她）。Wan 想换景别时就用叠化换 → 给它一个「镜头连续后拉」去换景别，并写明白边只能被推出画面、不会变透明。
- 续写复述上一段时会放慢，到上一段最后一秒常常对不上 → 让上一段提前结束。
- c4 开头树干没完全盖住，左边漏一条亮灯的木屋，叠化时闪约 0.2 秒。
- c6 她没照提示词放下皮箱；汽笛响到约 5.5 秒（要求 3 秒内淡掉）。

## 出处

运行目录里的 movie.json、run1.log 和 plan 文件 movie_two_photos.json（没有放进仓库）。

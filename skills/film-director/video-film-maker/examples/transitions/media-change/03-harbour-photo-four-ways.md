# 书桌上的旧照片变成真的海港：四种调用方式对比

版本：四种调用方式对比（续写最好）

台灯下书桌上的旧照片，镜头推近（#1 相同），#2 分别用首帧、首尾帧、参考图、续写四种方式做照片变实景，四版连放 39.5 秒。续写版接缝硬切，速度比 0.69，最顺。

（示例视频：ex-media-change-03.mp4，没有放进仓库。四版连放里的 (d) 续写版：推近书桌上的旧照片，硬切接续写，照片变成真的海港（30.03–34.03 s））

## 模型与调用

| 版本 | #2 的方式 | 接缝 | 速度比 |
|---|---|---|---|
| (a) | 首帧 = #1 最后一帧 | 叠化 6 帧（开头冻住 + 往后跳被剪掉） | 0.18 |
| (b) | 首帧 + 尾帧 | 叠化 6 帧（开头自带叠化被剪掉） | 0.62 |
| (c) | 参考图（照片当图1） | 叠化 10 帧 | 0.20 |
| (d) | 续写（#1 最后 3 秒） | 硬切 | **0.69** |

模型：Wan 3.0，720P，seed 7。

## 提示词原文

**(b) mc_b_firstlast（8 s，16:9；`first_frame` = `refs/photo_mc1f179.png`，`last_frame` = `refs/real_last_mc2f170.png`）**

> The still photograph comes to life and turns into a real place. From 0 to 2 seconds the image is a flat, faded paper photograph lying on a desk, and the camera keeps pushing forward. From 2 seconds the water in the photograph begins to ripple, the boats start to rock, clouds drift and seagulls fly, and the faded print colours become vivid and real. The camera keeps pushing forward smoothly through the photograph white border, the paper edges slide away out of the frame, and by 5 seconds we are inside a real live-action seaside harbour on a sunny day, the camera gliding forward over the water toward the pier where a young woman in a long red wool coat with a low dark bun stands holding a small brown leather suitcase. Sound: the soft ticking clock fades out and is replaced by waves, seagulls and harbour wind, no music, no speech.

**(b) 重新生成的 mc_b_firstlast_v2（同样的首尾帧，提示词在上面这段后面加一句；**没用上**，原因见最后一节）**

> …（同上）… One continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away and never pulls back; it only keeps moving forward.

**(c) mc_c_refimage（8 s，16:9；`reference_images` = [`refs/photo_mc1f179.png`]）**

> 图1 is an old faded paper photograph of a seaside harbour lying on a dark wooden desk. The video opens on exactly this view as in 图1: the photograph fills most of the frame, with its white border and the desk visible at the edges. The still photograph comes to life and turns into a real place. From 0 to 2 seconds the image is a flat, faded paper photograph lying on a desk, and the camera keeps pushing forward. From 2 seconds the water in the photograph begins to ripple, the boats start to rock, clouds drift and seagulls fly, and the faded print colours become vivid and real. The camera keeps pushing forward smoothly through the photograph white border, the paper edges slide away out of the frame, and by 5 seconds we are inside a real live-action seaside harbour on a sunny day, the camera gliding forward over the water toward the pier where a young woman in a long red wool coat with a low dark bun stands holding a small brown leather suitcase. Sound: the soft ticking clock fades out and is replaced by waves, seagulls and harbour wind, no music, no speech.

**(d) mc_d_extend（11 s，ratio adaptive；`reference_video` = `refs/mc1_last3s.mp4`，即调用 #1 第 90–179 帧连声音）**

> 将视频1向后延长8秒。延长部分：镜头保持和视频1完全相同的速度继续向下推近桌上的照片。从延长部分开始，静止的照片活了过来：照片里的海水开始荡漾，渔船轻轻摇晃，云在飘，海鸥飞起来，褪色的相纸颜色变得鲜艳真实。镜头平稳地继续向前推，穿过照片的白边，相纸的边缘和书桌滑出画面；延长部分开始 3 秒后，画面已经完全是真实的晴天海边小港口，镜头贴着水面向码头滑去，码头上站着一位穿红色长款羊毛大衣、深色头发挽成低发髻、手提棕色小皮箱的年轻女子。电影实拍质感，一镜到底，没有剪辑，没有文字。声音：轻轻的钟表滴答声渐渐淡出，换成海浪声、海鸥声和港口的风声，没有音乐，没有人声。

## 剪辑关键数字

- 每段从调用 #1 第 60 帧（2.0 s）开始用；(a)(b) 的接点改成「#1 里和 #2 新起点最像的那一帧」，靠 6 帧叠化盖住。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
mc_b_firstlast · 首尾帧 · 8 s · seed 7 · 首帧 = refs/photo_mc1f179.png · 尾帧 = refs/real_last_mc2f170.png
mc_c_refimage · 参考图 · 8 s · seed 7 · 参考图 = refs/photo_mc1f179.png
mc_d_extend · 续写 · 11 s · seed 7 · 参考视频 = refs/mc1_last3s.mp4
mc_b_firstlast_v2 · 首尾帧 · 8 s · seed 7 · 首帧 = refs/photo_mc1f179.png · 尾帧 = refs/real_last_mc2f170.png
```

调用 #1 mc_1_photo 沿用第一版；(a)(b)(c) 的 plan 在同目录 `plan_a/b/c.json`。

`cut.sh`：

```bash
# media_change v2: the same photo push-in (call #1) followed by four different second calls; each version labelled
python3 make_plans.py
for k in a b c d; do python3 scripts/optical_edit.py plan_$k.json demo_$k.mp4 > /dev/null; done
python3 make_plans.py   # second pass: now it knows each version's length for the reel
python3 scripts/optical_edit.py plan_reel.json demo.mp4 > /dev/null   # (a)(b)(c)(d) back to back with a short dip to black
```

`plan_d.json`：

```json
{
 "segments": [
  {"clip": "classic/media_change/clips/mc_1_photo.mp4", "start": 60, "end": 179, "call": 1, "label": "(d) Wan 调用 #1 · 文生 · 6s（桌上照片推近）"},
  {"clip": "clips/mc_d_extend.mp4", "start": 90, "end": 329, "call": 2, "label": "(d) Wan 调用 #2 · 视频续写（视频1 = #1 最后 3s）· 11s · 从它的 3s 起用"}
 ],
 "transitions": [
  {"type": "cut", "audio_xfade": 0.1}
 ]
}
```

不在 skill 里的一次性脚本：`make_plans.py`（没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`add_b2.py`、`deskshare.py`、`motion_after.py`、`report.py`、`seams_v2.py`。

## 生成后检查的结果

- 首帧、首尾帧版在 #2 里都有自带的冻住、跳变或整幅叠化，开头只能剪掉，帧级一致的好处就没了。

## 踩的坑和改法

- 换景别（照片 → 全景）用续写最顺，因为它看得到前一段的运动。
- 续写版 11.0–11.5 s 右边一条渔船变半透明后消失。

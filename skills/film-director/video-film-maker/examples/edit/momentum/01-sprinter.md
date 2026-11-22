# 清晨红跑道上的短跑手：侧面跟拍切到右前方

版本：当前推荐

白背心蓝短裤的女短跑手，侧面跟拍（#1）→ 右前方约 50°（#2），剪在左腿蹬地前冲上，同一条腿接着蹬出去。转场 3.80 s，两边步频只差 2%。

（示例视频：ex-momentum-01.mp4，没有放进仓库。清晨红跑道上的短跑手：侧面跟拍切到右前方（2.3–6.3 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 a_side | 文生 | 8 s | 到剪点 |
| #2 b_front45_ref | 参考图（只放人物） | 8 s | 4.63 s 以后 |

模型：Wan 3.0，720P，各 1 次。

## 提示词原文

**调用 #1 `a_side`（文生，8 s，seed 61）**

> Realistic cinematic sports footage, natural light, one continuous shot, no cuts, no dissolves. At dawn in an empty outdoor athletics stadium: a red running track with white lane lines, low golden morning sun, light mist over the empty stands. A young female sprinter with a dark high ponytail, wearing a white athletic tank top, blue running shorts and white running spikes, sprints along the track. Side tracking shot: the camera travels alongside her at hip height at exactly her speed, seeing her from her right side in full profile, her whole body in frame, running from left to right across the frame. She is already sprinting at full speed at the very first frame and never starts from standing: big powerful strides, each stride she drives her knee high and pushes off the track hard with her back leg fully extended, her body leaning forward, arms pumping. She keeps sprinting at full speed for the whole shot. Sound: her spikes striking the track in a fast rhythm, her breathing, quiet morning birds, no music, no speech.

**调用 #2 `b_front45_ref`（参考图 图1 图2，8 s，seed 62）**

> Realistic cinematic sports footage, natural light, one continuous shot, no cuts, no dissolves. The same empty outdoor athletics stadium at dawn: a red running track with white lane lines, a green infield, empty stands with red and yellow seats under a long roof, low golden morning sun and light haze. A very different camera position from a side view: the camera is low near the ground at knee height, in front of her and off to her right side, at a three-quarter front angle about 45 degrees from straight ahead, looking slightly up at her; it travels backward ahead of her at her speed so she stays large in the frame, and the white lane lines run diagonally from the near corner of the frame into the distance behind her; we see her face and the front of her body. The woman in 图1 and 图2 (keep her face, skin tone, dark high ponytail, white athletic tank top, blue running shorts and white running spikes exactly as in 图1 and 图2; use only the person from those images, not their background) is already sprinting at full speed at the very first frame and never starts from standing: big powerful strides, each stride she drives her knee high and pushes off the track hard with her back leg fully extended, her body leaning forward, arms pumping, running toward the camera and slightly toward the right side of the frame. She keeps sprinting at full speed for the whole shot. Sound: her spikes striking the track in a fast rhythm, her breathing, no music, no speech.

## 剪辑关键数字

- 剪点对同一条腿：每步左右腿交替，接反会别扭。
- 两边都在跑时光流量上升沿用不上，要逐帧对步态。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_side · 文生 · 8 s · seed 61
b_front45_ref · 参考图 · 8 s · seed 62 · 参考图 = refs/ref1_upper.png, refs/ref2_full.png
```

`cut.sh`：

```bash
# momentum example: side tracking sprint (call #1) -> cut on the push-off -> front ~45 deg (call #2, person-only refs)
OC=scripts/occut.py
python3 $OC gen jobs_a.json clips --workers 1                                   # call #1 a_side
python3 refcrops.py clips/a_side.mp4 112 refs ref1_upper:470,60,320,320 ref2_full:330,60,480,560   # person-only refs from call #1 frame 112
python3 $OC gen jobs_b.json clips --workers 1                                   # call #2 b_front45_ref
# gait read frame by frame: frames.py sheets + work/gait_zoom.png, work/legs.png
python3 frames.py clips/a_side.mp4 126 151 1 work/a_side_126_151.png 320 7
python3 frames.py clips/b_front45_ref.mp4 118 145 1 work/b_front_118_145.png 320 7
# cut: A last frame 137 (left leg pushing off, toe still down, right knee driving), B first frame 139 (same leg, next phase)
python3 $OC cuts clips/a_side.mp4 work/cuts_used_a_side --start 24 --end 137
python3 $OC cuts clips/b_front45_ref.mp4 work/cuts_used_b_front45_ref --start 139 --end 239
python3 $OC join plan.json demo.mp4 --xfade 0.25
python3 $OC cuts demo.mp4 work/cuts_used_demo --start 0 --end 214
python3 classic/cutsheet.py demo.mp4 114 sheet.png 10 10 1 165
```

`plan.json`：

```json
[
 {"clip": "clips/a_side.mp4", "start": 24, "end": 137, "label": "Wan 调用 #1 · 文生 · 侧面跟拍（8s 素材）"},
 {"clip": "clips/b_front45_ref.mp4", "start": 139, "end": 239, "label": "Wan 调用 #2 · 参考图×2（只放人物，取自调用 #1）· 前方约 45°→正面（8s 素材）"}
]
```

不在 skill 里的一次性脚本：`refcrops.py`、`frames.py`、`cutsheet.py`（都没有放进仓库）。

## 生成后检查的结果

- 剪点后机位还在转，但动势接得上。

## 踩的坑和改法

- #2 前 3.5 秒还像参考图的侧面，之后镜头才绕到前方 → 至少生成 8 秒、只用后半段。
- 写了低机位，实际在腰的高度。

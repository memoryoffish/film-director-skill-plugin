# 站台上放下皮箱：全景切腰部以下

版本：早期版本

女人走进站台、弯腰放皮箱（#1 正面全景），皮箱放到一半时切到腰部以下（#2），皮箱从同样的进度接着落下。转场 3.87 s。

（示例视频：ex-match-on-action-02.mp4，没有放进仓库。站台上弯腰放皮箱，放到一半从全景切到腰部以下（2.37–6.37 s））

## 模型与调用

| 调用 | 方式 | 时长 | 用到 |
|---|---|---|---|
| #1 a_wide | 文生 | 8 s | 第 15–130 帧 |
| #2 b_close_ref | 参考图 ×3（上半身、全身带皮箱、空站台；都截自 #1） | 6 s | 第 73–179 帧 |

模型：Wan 3.0，720P。

## 提示词原文

**调用 #2 的提示词（原文，seed 33）**

> Close-up shot, static camera at knee height, seen from the front, framing the woman from her waist down to the platform floor. The woman in 图1 and 图2 (keep her face, skin tone, hair, clothes - the long red wool coat closed and tied with its belt at the waist, the white top, bare legs and black ankle boots - exactly as in 图1 and 图2; use only the person from those images, not their background), holding the same small brown leather suitcase as in 图2 in her right hand, which is on the left side of the frame, the suitcase hanging at knee height. She is in the same place as 图3: the grey concrete railway platform with the yellow tactile safety strip, overcast morning light. From 0 to 1 second she stands still holding the suitcase. From 1 to 2 seconds she bends forward at the waist and lowers the suitcase to the ground in one smooth, fairly quick motion lasting about one second, setting it down on the concrete next to her right boot with a soft thud. From 2 to 3 seconds she lets go of the handle. From 3 to 6 seconds she straightens up and the suitcase stands still on the ground beside her boots. Realistic cinematic photography. Sound: quiet platform ambience, a soft thud when the suitcase touches the ground, no music, no speech.

**调用 #1 的提示词（第一版原文，seed 31）**

> Wide full shot of an empty railway platform on an overcast morning, static camera at eye level, the whole body visible. A young woman in a long red wool coat, black ankle boots and a low dark bun, carrying a small brown leather suitcase in her right hand, walks into the frame from the left and stops in the center, facing the camera; the suitcase is on the left side of the frame. From 3 to 5 seconds she slowly bends her knees and lowers the suitcase to the ground beside her right foot, setting it down on the concrete. From 5 to 8 seconds she straightens up, lets go of the handle and looks down the track. Realistic cinematic photography. Sound: quiet platform ambience, her footsteps, a soft thud when the suitcase touches the ground, no music, no speech.

## 剪辑关键数字

- 剪点找两段里动作的同一阶段（皮箱高度），切在放到一半时。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
b_close_ref · 参考图 · 6 s · seed 33 · 参考图 = refs/ref1_upper.png, refs/ref2_full.png, refs/ref3_scene.png
```

`cut.sh`：

```bash
# call #1 = first-version a_wide (symlinked); reference images for call #2 cut from it
python3 refcrops.py 100 0            # refs/ref1_upper.png ref2_full.png ref3_scene.png + refs/refs.json
python3 make_jobs.py                 # jobs.json (b_close_ref, reference_images 图1 图2 图3)
python3 scripts/occut.py gen jobs.json clips/ --workers 1
python3 track.py clips/b_close_ref.mp4 work/b_close_ref_track.json "[300,250,760,720]"
python3 phase_v2.py work/a_wide_track.json 112 149 work/b_close_ref_track.json 48 89   # -> A last 130, B first 73
python3 scripts/occut.py join plan.json demo.mp4 --xfade 0.25   # plan.json has the call labels
python3 ../../cutsheet.py demo.mp4 116 sheet.png 10 10 1 160
```

`plan.json`：

```json
[
 {"clip": "clips/a_wide.mp4", "start": 15, "end": 130, "label": "Wan 调用 #1 · 文生 · 全景（8s 素材）"},
 {"clip": "clips/b_close_ref.mp4", "start": 73, "end": 179, "label": "Wan 调用 #2 · 参考图×3（取自调用 #1）· 腰部以下（6s 素材）"}
]
```

不在 skill 里的一次性脚本：`refcrops.py`、`make_jobs.py`、`track.py`、`phase_v2.py`、`cutsheet.py`（都没有放进仓库）。

## 生成后检查的结果

- 两段里大衣都系着腰带，同一只皮箱。

## 踩的坑和改法

- 两次各自文生、不用参考图时：同一句服装描述也保不住衣服（全景里系着腰带，特写里敞开），下放速度差近一倍 → 参考图 + 提示词写「用大约一秒放下」。
- 只换景别、角度不变时可以加场景图；要换角度就只放人物，场景图会把机位锁成 #1 那样。

# 雨夜站台 ↔ 海滩回忆：第二次光晕的两档时长

版本：推荐参数的出处

红大衣女子在站台（#1），光晕闪进海滩回忆（#2），再闪回站台。只改剪辑，出两档：第二次光晕 0.93 s（档 1）和 1.50 s（档 2）。

（示例视频：ex-flash-02.mp4，没有放进仓库。档 1：雨夜站台的红大衣女子，光晕闪进海滩回忆、再闪回站台（2.0–8.6 s））

当时还做了档 2（第二次光晕 1.50 s），没有放进仓库。

## 模型与调用

| 调用 | 方式 | 用到 |
|---|---|---|
| #1 fw_a_platform | 文生 | 源第 0–106、150–239 帧 |
| #2 fw_b_memory_ref | 参考图 | 源第 96–179 帧 |

模型：Wan 3.0，720P；这一版没有新的调用。

## 提示词原文

**fw_a_platform（8 s）**

> Cinematic live-action shot, dusk. A young woman in a long red wool coat, black ankle boots and a low dark bun stands alone on an empty railway platform, a small brown leather suitcase at her feet. Medium close-up from the front, slightly to the side; the camera slowly pushes in toward her face. From 0 to 4 seconds she holds an old photograph in both hands and looks down at it. From 4 to 8 seconds she slowly lifts her eyes and stares into the distance, lost in thought, a faint smile. Cool blue evening light, platform lamps glowing behind her, shallow depth of field. Sound: quiet station ambience, soft wind, no music, no speech.

**调用 #2 fw_b_memory_ref（参考图模式，6 s，720P，16:9，seed 7，带声音，prompt_extend 关；`reference_images` = [`refs/ref1_face.png`, `refs/ref2_body.png`]）**

> The woman in 图1 and 图2 (keep her face, skin tone, eyes, eyebrows and dark hair in a low bun exactly as in 图1 and 图2; use only the person from those images, not their background, and not her red coat) on a bright summer day in the past. Cinematic live-action shot, overexposed warm sunlight. She wears a light white summer dress and laughs as she runs barefoot along a sunlit beach at the edge of the waves; the handheld camera follows her from the side. From 3 to 6 seconds she turns back toward the camera and smiles. Soft hazy glow, sun flares, warm golden tones, a dreamy memory feeling. Sound: gentle waves, wind, distant seagulls, no music, no speech.

## 剪辑关键数字

```
第一次（两档相同）: bloom rise 6, overlap 4, fall 9,  level 0.5, sfx
档 1 第二次:        bloom rise 6, overlap 4, fall 18, level 0.5, sfx, audio_xfade 0.6   # 0.93 s
档 2 第二次:        bloom rise 6, overlap 6, fall 33, level 0.5, sfx, audio_xfade 1.0   # 1.50 s
```

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
fw_a_platform · 文生 · 8 s · seed 7
fw_b_memory_ref · 参考图 · 6 s · seed 7 · 参考图 = classic/flash_white/v2/refs/ref1_face.png, classic/flash_white/v2/refs/ref2_body.png
```

`cut.sh`：

```bash
# flash_white v3: v2's soft bloom (level 0.5), second bloom (memory -> platform) made longer and slower to fade; no new Wan calls
E=scripts/optical_edit.py
python3 make_plans.py
python3 $E plan_mid.json demo.mp4 > /dev/null        # 档 1：第二次 28 帧，约为第一次的 1.5 倍
python3 $E plan_long.json demo_long.mp4 > /dev/null  # 档 2：第二次 45 帧，约为第一次的 2.4 倍，退得更慢
for k in mid long; do python3 $E noglow_plan_$k.json /tmp/fw_v3_noglow_$k.mp4 > /dev/null; done
```

`plan_mid.json`：

```json
{
 "segments": [
  {"clip": "classic/flash_white/clips/fw_a_platform.mp4", "start": 0, "end": 106, "call": 1, "label": "Wan 调用 #1 · 文生 · 8s（站台）"},
  {"clip": "classic/flash_white/v2/clips/fw_b_memory_ref.mp4", "start": 96, "end": 179, "call": 2, "label": "Wan 调用 #2 · 参考图（图1 脸、图2 全身，截自 #1）· 6s（回忆）"},
  {"clip": "classic/flash_white/clips/fw_a_platform.mp4", "start": 150, "end": 239, "call": 1, "label": "Wan 调用 #1 · 文生 · 8s（站台，从 5.0s 接着用）"}
 ],
 "transitions": [
  {"type": "bloom", "rise": 6, "overlap": 4, "fall": 9, "level": 0.5, "sfx": true, "sfx_db": 0},
  {"type": "bloom", "rise": 6, "overlap": 4, "fall": 18, "level": 0.5, "sfx": true, "sfx_db": 0, "audio_xfade": 0.6}
 ]
}
```

`plan_long.json`：

```json
{
 "segments": [
  {"clip": "classic/flash_white/clips/fw_a_platform.mp4", "start": 0, "end": 106, "call": 1, "label": "Wan 调用 #1 · 文生 · 8s（站台）"},
  {"clip": "classic/flash_white/v2/clips/fw_b_memory_ref.mp4", "start": 96, "end": 179, "call": 2, "label": "Wan 调用 #2 · 参考图（图1 脸、图2 全身，截自 #1）· 6s（回忆）"},
  {"clip": "classic/flash_white/clips/fw_a_platform.mp4", "start": 150, "end": 239, "call": 1, "label": "Wan 调用 #1 · 文生 · 8s（站台，从 5.0s 接着用）"}
 ],
 "transitions": [
  {"type": "bloom", "rise": 6, "overlap": 4, "fall": 9, "level": 0.5, "sfx": true, "sfx_db": 0},
  {"type": "bloom", "rise": 6, "overlap": 6, "fall": 33, "level": 0.5, "sfx": true, "sfx_db": 0, "audio_xfade": 1.0}
 ]
}
```

不在 skill 里的一次性脚本：`make_plans.py`（没有放进仓库）。

## 生成后检查的结果

- 拿同一剪辑不加光的版本逐帧比平均亮度，量「看得见的光」：档 1 第二次 0.80 s，档 2 1.30 s，第一次 0.53 s。

## 踩的坑和改法

- 两次光晕帧数一样时，第二次显得短：从亮的回忆落回暗的站台，光一退就暗，前半段的提亮又落在本来就亮的画面上。所以回到暗处的那次要更长、退得更慢。
- 第一版是纯白 2 帧，太硬；光晕（相加混合、调透明度）柔和得多。

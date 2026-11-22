# 钢琴声延续到雨夜街道（L-cut）

版本：早期版本

#1 她在屋里弹钢琴，4.00 s 画面切到窗外雨夜街道（#2），钢琴声保持原音量 1.5 秒、再用 1.5 秒淡出，雨声 2 秒淡入。

（示例视频：ex-sound-04.mp4，没有放进仓库。L-cut：屋里弹钢琴，画面切到雨夜街道，钢琴声延续（2.5–6.5 s））

## 模型与调用

| 调用 | 方式 | 时长 |
|---|---|---|
| #1 lc_a_piano | 文生 | 8 s |
| #2 lc_b_street | 文生 | 6 s |

模型：Wan 3.0，720P，各 1 次。

## 提示词原文

**`lc_a_piano`（8 s，seed 21，720P，audio true）**

> Night, a warm lamp-lit apartment living room. A young woman in a long red wool coat, black ankle boots and a low dark bun sits at an upright wooden piano and plays a slow, gentle melody with both hands, swaying slightly. Medium shot from the side, the camera is static. A tall window behind the piano shows rain streaking down the dark glass. Sound: a solo upright piano playing a slow, gentle, melancholic melody continuously from the first second to the last, faint rain on the window, no other instruments, no speech.

**`lc_b_street`（6 s，seed 22，720P，audio true）**

> Night, a rainy city street seen from a third-floor window looking down: wet black asphalt reflecting yellow streetlights and red neon signs, heavy rain falling. From 1 to 5 seconds a single dark car drives slowly from right to left through the puddles, and a pedestrian with a black umbrella walks along the sidewalk. The camera is static. Sound: heavy steady rain, water hissing under the car tyres as it passes through puddles, a distant low city hum, no music, no speech.

## 剪辑关键数字

- A 声音用到素材 8.00 s：切后 1.5 s 保持原音量，5.50–7.00 淡出；B 声音 4.00–6.00 淡入。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
lc_a_piano · 文生 · 8 s · seed 21
lc_b_street · 文生 · 6 s · seed 22
```

`cut.sh`：

```bash
# L-cut: the piano (A) keeps playing over the rainy street (B), then fades away while the rain comes up.
#   picture: A lc_a_piano frames 30-149 (1.0-5.0 s) | B lc_b_street frames 0-179 (0-6.0 s)  -> cut at 4.000 s
#   sound:   A 1.0-8.0 s placed at 0.0: full until 5.5 s (1.5 s past the cut), afade out 5.5-7.0 s
#            B 0-6.0 s placed at 4.0 (adelay 4000, in sync with its picture), afade in 4.0-6.0 s
cd .
ffmpeg -v error -nostdin -y -i clips/lc_a_piano.mp4 -i clips/lc_b_street.mp4 -filter_complex "\
[0:v]trim=start_frame=30:end_frame=150,setpts=PTS-STARTPTS[va];\
[1:v]trim=start_frame=0:end_frame=180,setpts=PTS-STARTPTS[vb];\
[va][vb]concat=n=2:v=1:a=0,format=yuv420p[v];\
[0:a]atrim=1.0:8.0,asetpts=PTS-STARTPTS,afade=t=out:st=5.5:d=1.5[aa];\
[1:a]atrim=0:6.0,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=2.0,adelay=4000:all=1[ab];\
[aa][ab]amix=inputs=2:normalize=0:duration=longest,atrim=0:10.0[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 16 -preset slow -c:a aac -b:a 192k -movflags +faststart demo.mp4
```

## 生成后检查的结果

- 钢琴 8 秒一直在，没有别的乐器和人声。

## 踩的坑和改法

- 判断钢琴还在不在：看 200–8000 Hz 最强谱峰比中位数高多少（只有钢琴 73–81 dB）；这个数不通用（纯雨声也能到 29–37），更稳的是看谱峰在不在音符间跳。

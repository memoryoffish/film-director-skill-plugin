# 美术馆的风车油画活过来（第一版）

版本：旧版

同一幅风车油画，#2 续写生成了 3 次；用的第 3 次真实感从下往上一点点漫上去，没有整幅叠化，但天空到最后还带一点油画感。接缝 4.00 s，油画变实景约 5.7–8.7 s。

（示例视频：ex-media-change-02.mp4，没有放进仓库。美术馆的风车油画活过来（第一版）（2.5–10.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 |
|---|---|---|---|
| #1 m1_gallery | 文生 | 6 s | 1 |
| #2 续写 | 参考视频 = #1 第 90–179 帧 | 11–13 s | 3 |

模型：Wan 3.0，720P。

## 提示词原文

**调用 #1：m1_gallery（文生，6 s，16:9，生成 1 次），用第 60–179 帧**

> Cinematic live-action film footage, natural light, 35mm lens, one continuous shot, no cuts, no dissolves, no jumps, the camera never cuts away. A quiet art museum gallery with a plain white wall and a pale wooden floor, lit by soft even daylight from skylights. On the wall hangs a single oil painting in a thin gilded frame: a golden wheat field under a blue summer sky with white clouds, and an old wooden windmill with four lattice sails standing in the middle of the field, painted in thick, visible impasto brushstrokes. The painting hangs at eye level exactly in the center of the frame, seen straight on. No people. From 0 to 6 seconds the camera pushes slowly and steadily straight toward the painting, and at the last frame the painting fills almost the whole frame, with only a thin strip of the gilded frame visible at the edges. Everything in the painting is still. Sound: quiet gallery room tone with faint distant footsteps, no music, no speech.

**第 1 次 m2_extend（11 s = 3 + 8，没用上）****

> 将视频1向后延长8秒。延长部分：镜头保持和视频1完全相同的速度，继续笔直地向前推近墙上的油画，金色画框从画面四边滑出去，画面里只剩下这幅油画。从延长部分一开始，静止的油画就活了过来：金色的麦田开始随风起伏，一波一波的麦浪从远处推过来，风车的四片叶子开始慢慢转动，天上的白云在飘，厚厚的油画笔触和颜料质感渐渐变成真实的阳光、麦穗和木头。镜头平稳地继续向前推进画里；延长部分开始 3 秒后，画面已经完全是真实的夏日金色麦田，一座真实的老木头风车立在麦田中间，叶片缓缓转动，镜头贴着麦穗上方向风车滑去，麦穗随风起伏。电影实拍质感，自然光，一镜到底，没有剪辑，没有叠化，没有跳变，没有文字。声音：美术馆里安静的环境声渐渐淡出，换成风吹麦田的沙沙声、风车木叶转动的吱呀声和远处的鸟叫，没有音乐，没有人声。

**第 2 次 m2_extend_v2（13 s = 3 + 10，没用上）****

> 将视频1向后延长10秒。延长部分：镜头保持和视频1完全相同的速度，继续笔直地向前推近墙上的油画，金色画框从画面四边滑出去，画面里只剩下这幅油画。从延长部分一开始，油画就活了过来，并且一点一点变成真实的世界：先是麦田开始随风起伏，风车的四片叶子开始转动，天上的云开始飘；接着油画的笔触、厚厚的颜料和画布的纹理逐渐消失，麦穗、天空、云、风车和远处的村庄全都变成照片级真实的实景。延长部分开始 4 秒后，画面里已经没有任何油画的痕迹，完全是一段真实拍摄的夏日金色麦田：真实的蓝天和柔软的真实白云，一座真实的老木头风车立在麦田中间，叶片缓缓转动，真实的阳光照在麦穗上，麦浪一波一波随风起伏。镜头继续平稳地贴着麦穗上方向风车滑去。电影实拍质感，自然光，一镜到底，没有剪辑，没有叠化，没有跳变，没有文字。声音：（同第 1 次）

**第 3 次 m2_extend_v3（13 s = 3 + 10，demo 用第 90–389 帧）****

> 将视频1向后延长10秒。延长部分：镜头一直保持和视频1完全相同的速度，不停地笔直向前推进，从头到尾不减速、不停下。金色画框从画面四边滑出去，画面里只剩下这幅油画。从延长部分一开始，油画就活了过来：麦田开始随风起伏，风车的四片叶子开始转动，天上的云开始飘。同时，随着镜头向前推进，真实感从画面最下方的麦穗开始，一路向上蔓延：先是近处的麦穗变成真实的麦穗，接着中间的麦田和风车变成真实的木头风车，最后远处的村庄、天空和云也变成真实的蓝天白云；油画的笔触和厚厚的颜料一路向上消退。这是同一个画面里的逐渐变化，始终只有一个画面，没有两个画面叠在一起，风车始终只有一套叶片，没有重影。延长部分开始 4 秒后，画面里已经没有任何油画的痕迹，完全是一段真实拍摄的夏日金色麦田，一座真实的老木头风车立在麦田中间，叶片缓缓转动，麦浪一波一波随风起伏，镜头继续贴着麦穗上方向风车滑去。电影实拍质感，自然光，一镜到底，没有剪辑，没有叠化，没有跳变，没有文字。声音：美术馆里安静的环境声渐渐淡出，换成风吹麦田的沙沙声、风车木叶转动的吱呀声和远处的鸟叫，没有音乐，没有人声。

## 剪辑关键数字

- 3 次续写都在延长部分一开始就停住，速度比约 0.2–0.5。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
m1_gallery · 文生 · 6 s · seed 7
m2_extend · 续写 · 11 s · seed 7 · 参考视频 = refs/m1_last3s.mp4
m2_extend_v2 · 续写 · 13 s · seed 7 · 参考视频 = refs/m1_last3s.mp4
m2_extend_v3 · 续写 · 13 s · seed 7 · 参考视频 = refs/m1_last3s.mp4
```

`cut.sh`：

```bash
# media_change example: Wan call #1 m1_gallery (text-to-video, push in on the painting) + Wan call #2 = continuation
# (reference video = #1's last 3 s, i.e. frames 90-179). Call #2's first 90 frames re-draw the input; it is used
# from B0, the frame after the re-drawn part. Hard cut on the call boundary, audio crossfaded 0.25 s, call labels
# burned in by occut join.
#   ./cut.sh                      -> demo.mp4 with take 3 (m2_extend_v3), A 60-179 + B 90-389  (the delivered demo)
#   TAKE=m2_extend    A1=155 B1=329 OUT=demo_take1.mp4 ./cut.sh   (take 1, re-draw lags #1 by ~0.8 s, so A ends at 155)
#   TAKE=m2_extend_v2 A1=153 B1=389 OUT=demo_take2.mp4 ./cut.sh   (take 2)
D=.
OCCUT=scripts/occut.py
TAKE=${TAKE:-m2_extend_v3}; A0=${A0:-60}; A1=${A1:-179}; B0=${B0:-90}; B1=${B1:-389}; OUT=${OUT:-demo.mp4}
DUR=$(python3 -c "import json; print(json.load(open('$D/clips/$TAKE.json'))['payload']['parameters']['duration'])")
cd "$D"
cat > "plan_${OUT%.mp4}.json" <<JSON
[{"clip": "$D/clips/m1_gallery.mp4", "start": $A0, "end": $A1, "label": "Wan 调用 #1 · 文生 · 6s"},
 {"clip": "$D/clips/$TAKE.mp4", "start": $B0, "end": $B1, "label": "Wan 调用 #2 · 续写（参考视频 = #1 最后 3 秒）· ${DUR}s"}]
JSON
python3 "$OCCUT" join "plan_${OUT%.mp4}.json" "$OUT" > "${OUT%.mp4}.json"
echo "$OUT: boundary at frame $(( A1 - A0 + 1 )) = $(python3 -c "print(round(($A1 - $A0 + 1) / 30, 2))") s"
```

`plan_last3s.json`：

```json
[
 {"clip": "clips/m1_gallery.mp4", "start": 90, "end": 179}
]
```

`plan_demo.json`：

```json
[
 {"clip": "clips/m1_gallery.mp4", "start": 60, "end": 179, "label": "Wan 调用 #1 · 文生 · 6s"},
 {"clip": "clips/m2_extend_v3.mp4", "start": 90, "end": 389, "label": "Wan 调用 #2 · 续写（参考视频 = #1 最后 3 秒）· 13s"}
]
```

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`add_v2.py`、`add_v3.py`、`make_jobs.py`、`match.py`、`peek.py`、`sheet.py`、`wan_calls.py`。

## 生成后检查的结果

- 第 1 次只有近处的麦穗变真，天空和风车一直是油画；第 2 次全变成实景，但用的是约 0.8 秒整幅叠化（画的叶片和真叶片叠在一起）；第 3 次写成「从下往上蔓延、始终一个画面、只有一套叶片」才成。

## 踩的坑和改法

- 厚涂油画这种风格化媒介比照片难变真。
- 媒介「变」过去要写成局部、逐渐的变化；整幅两层叠在一起就是叠化过去，不算。

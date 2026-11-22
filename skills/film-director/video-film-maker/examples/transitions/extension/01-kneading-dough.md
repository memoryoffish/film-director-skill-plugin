# 乡村厨房揉面，接着滚圆、撒粉、放进发酵篮

版本：当前推荐

一个人在乡村厨房揉面（#1），续写接着滚圆、撒粉、端起发酵篮放进去（#2）。接缝在 8.00 s，场景分 0.026，亮度 107.3 → 107.9。

（示例视频：ex-extension-01.mp4，没有放进仓库。乡村厨房揉面，接着滚圆、撒粉、放进发酵篮（6.5–10.5 s））

## 模型与调用

| 调用 | 方式 | 时长 | 抽了几次 | 用到 |
|---|---|---|---|---|
| #1 揉面 | 文生 | 8 s | 1 | 到结尾 |
| #2 发酵篮 | 续写（参考视频 = #1 第 150–239 帧） | 8 s | 1 | 复述段之后 |

模型：Wan 3.0，720P。

## 提示词原文

**调用 #1 `a_knead`（文生，8 s，seed 401）**

> Cinematic live-action film footage, soft natural window light, 35mm lens, one continuous shot, no cuts, no dissolves, no text. A rustic farmhouse kitchen in the morning. A young woman with short curly red hair and freckles, wearing a sage-green linen shirt with rolled-up sleeves and a cream-coloured apron, stands behind a sturdy wooden table and kneads a large ball of pale bread dough on a floured wooden board. On the table there are exactly three things: the wooden board with the dough in the middle, a small white ceramic bowl of flour at the back left, and an empty round rattan proofing basket at the front right. Nothing else is on the table. Medium shot from the front at table height, looking slightly down, the whole table top in frame; the camera is locked off and does not move. From 0 to 6 seconds she kneads the dough with the heels of her hands, pushing it away, folding it back and turning it. From 6 to 8 seconds she stops kneading and begins to round the dough into a smooth ball, cupping it with both hands and turning it on the board. Sound: the soft thump and slap of the dough on the wooden board and birds outside the window; no music of any kind: no piano, no guitar, no strings, no drums, no music box, no melody, no singing, no speech.

**调用 #2 `b_basket_ext`（续写，参考视频 = 调用 #1 第 150–239 帧，duration 11，seed 401）**

> 将视频1向后延长8秒。延长部分：同一间乡村厨房，同一位红色短卷发、脸上有雀斑、穿浅绿色亚麻衬衫、系米色围裙的年轻女人，接着用双手把案板上的面团滚成光滑的圆球；然后用右手从左后方的白色小碗里抓一小撮面粉，撒进右前方空的藤编发酵篮里；再双手捧起面团，放进发酵篮，轻轻按一下；最后拍掉手上的面粉，双手搭在桌沿上，看着篮子里的面团。只用画面里已经有的东西：木案板、面团、白色小碗里的面粉、藤编发酵篮；桌上不出现任何新的东西，也没有东西凭空消失。镜头和视频1一样固定不动，景别不变。电影实拍质感，一镜到底，没有剪辑，没有叠化，没有跳变，没有文字。声音：面团在案板上的轻拍声、面粉撒落的沙沙声、窗外的鸟叫，没有音乐，没有钢琴，没有弦乐，没有人声。

## 剪辑关键数字

- 复述段里和 #1 最后一帧最像的是第 68 帧（不是输入长度对应的第 89 帧）：复述比输入短，从那一帧的下一帧接。
- 声音交叉淡化 0.25 s。

## 复现（scripts/ 的命令和参数）

运行目录：自己的工作目录；脚本用 skill 里的 `scripts/`。

生成（提示词见上；其他参数用默认）：

```
a_knead · 文生 · 8 s · seed 401
b_basket_ext · 续写 · 11 s · seed 401 · 参考视频 = a_knead_last3s.mp4
```

`cut.sh`：

```bash
# extension_v2: what was run, in order (from this directory)
O=scripts/occut.py
python3 $O gen jobs_a.json clips --workers 1                  # call 1 a_knead (8 s, seed 401)
python3 v2check.py music clips/a_knead.mp4 --spec checks/spec_a_knead.png; python3 $O cuts clips/a_knead.mp4 owncuts
python3 $O join plan_last3s.json a_knead_last3s.mp4           # A frames 150-239 (last 3 s) with audio
python3 $O gen jobs_b.json clips --workers 1                  # call 2 b_basket_ext (reference_video, 11 s, seed 401)
python3 $O seam clips/a_knead.mp4 239 clips/b_basket_ext.mp4 seams/ --b-skip auto   # -> b_skip 69 (PSNR 25.6)
python3 $O cuts clips/b_basket_ext.mp4 owncuts --start 69
python3 v2check.py music clips/b_basket_ext.mp4 --spec checks/spec_b.png
python3 v2check.py diff clips/a_knead.mp4 239 clips/b_basket_ext.mp4 329 checks/diff_a239_b329.png   # what changed on the table
python3 $O join plan_demo.json demo.mp4                      # A 0-239 + B 69-329, labelled
python3 te_sheet.py demo.mp4 sheet.png 8.0
```

`plan_last3s.json`：

```json
[
 {"clip": "clips/a_knead.mp4", "start": 150, "end": 239}
]
```

`plan_demo.json`：

```json
[
 {"clip": "clips/a_knead.mp4", "start": 0, "end": 239, "label": "Wan 调用 #1 · 文生 · 8s（揉面）"},
 {"clip": "clips/b_basket_ext.mp4", "start": 69, "end": 329, "label": "Wan 调用 #2 · 续写（参考视频 = #1 最后 3 秒）· 11s（滚圆、入篮）"}
]
```

不在 skill 里的一次性脚本：`v2check.py`、`te_sheet.py`（都没有放进仓库）。

运行目录里另有（检查、出图、拼 jobs 用，不在 skill 里）：`merge_jobs.py`。

## 生成后检查的结果

- A：桌上始终是提示词里列的三样东西，不增不减；机位固定。
- B：每样东西要么一直在，要么看得到被人拿进拿走；篮子是她用手端过去的；没有把 A 做完的动作再做一遍。

## 踩的坑和改法

- 「东西不凭空出现」的写法一次就成：A 把物品列死、加一句「Nothing else is on the table」；B 写「只用画面里已有的东西，不出现新东西、也不凭空消失」；不要点名说不要什么东西（点名反而会画出来）。
- B 的提示词要看完 A 的结尾再写，从 A 停在的那个动作写起。

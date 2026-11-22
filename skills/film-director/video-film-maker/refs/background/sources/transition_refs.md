# 转场 / 换镜 / 镜头衔接 参考视频清单

检索日期 2026-11-10。B 站条目都用 view 接口查过，YouTube 条目都打开过视频页，标题、UP 主、时长、日期、播放量都是当时取到的数。YouTube 不公开收藏数，记为「—」。「讲的方法」一栏照标题、简介、标签概括，没看视频内容。

已排除：BV1TkxJ6iEVS《如何丝滑的解决AI视频的衔接问题》（泽央zeyang）。

## 1. AI 视频专门的衔接 / 转场

### 首尾帧、尾帧接续与接缝问题（B 站）

- [神级AI短片必备，4大电影级转场](https://www.bilibili.com/video/BV1PBhG69EHM) — AI视次方 · 6:05 · 2026-08-25 · 32.9万/2706 — 用 Wan3.0（多参考 + 30 秒）演示 4 种电影级转场；是哪 4 种简介没写，需看视频
- [首尾帧接不上？问题不在工作流，在你随手抽的那张尾帧](https://www.bilibili.com/video/BV1hUxx6dEKt) — 82年の汽水 · 3:16 · 2026-11-01 · 63/3 — 抽尾帧接下一段前先问 4 件事：下一段要出现的东西这一帧里全不全、脸停在哪（同一镜头往回退 0.05/0.4/0.8 秒，运动量差 4.6 倍）、道具完整吗、声音切在哪；MiniMax H3 + ComfyUI
- [AI运镜小课堂-如何彻底消除首尾帧视频的"刹车感"](https://www.bilibili.com/video/BV16fEgztEYt) — 地质大学博士说AI · 2:21 · 2025-05-11 · 1.8万/1455 — 首尾帧拼接因前后内容、速度、方向不同会有「刹车感」，作者用 Sora 把拼接处再过一遍来消除
- [AI首尾帧不卡顿，终于给闺女做成了这条一镜到底](https://www.bilibili.com/video/BV1YpFezvEA1) — 恺渘老爹 · 1:08 · 2026-02-05 · 2.1万/346 — 38 个镜头（20 实拍 + 18 AI）接成一镜到底，难点是实拍和 AI 片段接点的卡顿刹车感，变速、补帧都不行；最后用的稳定做法简介没写，需看视频
- [全网独家！一招解决AI视频续写穿帮！](https://www.bilibili.com/video/BV1LjVZ6REMD) — 刺猬星球super-i · 1:55 · 2026-06-01 · 1.2万/1390 — 作者认为用首尾帧续接是最差的办法，给出四种做法：视频延展法、故事版、动作重叠法、直接剪掉
- [AI视频拼接的详细教程](https://www.bilibili.com/video/BV15B766nELy) — 栗子也该开点脑洞 · 18:14 · 2026-06-05 · 8.5万/7737 — 按「发现问题 → 解决思路 → 案例演示」系统讲 AI 视频拼接难题；具体手法简介没列，需看视频
- [AI视频总翻车？问题根本不在提示词](https://www.bilibili.com/video/BV12Sc2zbE8X) — 杰瑞Chang · 3:00 · 2026-03-13 · 11.7万/9952 — 一个地球转场翻车二三十次后的结论：首尾帧转场成败在两张图的「方向」，不在提示词；附一个判断这组首尾帧值不值得跑的筛选器
- [独家！我居然用seedance2.0 测出了长篇幅漫剧的焚决？！九宫格+尾帧衔接+角色卡竟是最终答案！coze+seedance 2.0协同创作成完美闭环！](https://www.bilibili.com/video/BV18QcEzWEoM) — 阿P手把手教会你AI · 16:54 · 2026-02-13 · 10.4万/9104 — 按上一段 15 秒的尾帧往下接，同时喂九宫格参考图和角色卡，保持人物一致、剧情连贯；Coze 生成九宫格
- [MINIMAX-H3视频续写，加入过渡片段，丝滑无缝衔接](https://www.bilibili.com/video/BV13CYv6iEuo) — 哈龙0102 · 10:40 · 2026-09-13 · 2741/144 — 用 MiniMax H3 视频续写，在两段之间插一段过渡片段来接（ComfyUI 工作流）

### AI 创意转场（B 站）

- [我用AI复刻了3种苹果发布会的神级无缝转场！](https://www.bilibili.com/video/BV1UQwezYEBg) — 无名NonameS · 1:59 · 2026-03-18 · 10.4万/1.6万 — 三种转场：钻入式（镜头掠过 A 钻进 B）、玩具屋（把俯拍全景改成微缩景观再接）、空间平移，都是先备好两端画面再用首尾帧连起来，简介附提示词
- [别再硬剪了！AI视频无缝转场，看完这篇就会](https://www.bilibili.com/video/BV1wz5r6ZEL2) — 果糖萱AIGC · 3:30 · 2026-05-16 · 407/20 — 拿 AI 短片《牌子》当例子讲三种手法：形状匹配、动作延续、镜头穿越，和硬切做对比，附提示词

### YouTube

- [8 Genius Ways to Use First Frame & Last Frame in Your AI Videos](https://www.youtube.com/watch?v=FeWDcpwTCNA) — Curious Refuge · 15:17 · 2026-02-11 · 3.4万/— — 首尾帧的 8 种用法，官网博客有逐镜拆解
- [How to Create Single Continuous Shots with Veo in Google Flow (AI Video Tutorial)](https://www.youtube.com/watch?v=6iBc4aoiwf4) — AI Video School · 16:12 · 2025-07-21 · 10.8万/— — 用 Veo 做连续长镜头的两种办法：Clip Extension 续写（Veo 2）、Frames to Video（Veo 3，带音频）
- [How I Connect Real Footage With AI Transitions](https://www.youtube.com/watch?v=4N_rE8N8O_M) — Tyler Stalman · 9:27 · 2025-12-09 · 29.4万/— — 在两段实拍之间用 AI 生成本来拍不出来的过渡，让它看起来自然
- [MiniMax H3 Context Loop Explained — Generate Long Videos with Scene Continuity in Comfy UI](https://www.youtube.com/watch?v=eSDey7wAK60) — AI Ninja · 12:11 · 2026-09-13 · 4.3万/— — 长视频不一次生成，而是一段一段生成，每段拿上一段的上下文来保持连续（ComfyUI 工作流）

## 2. 经典电影 / 剪辑转场手法

### 总览

- [【电影剪辑】镜头衔接/转场教科书式经典案例解说](https://www.bilibili.com/video/BV1wJ411s7Hq) — 豚村长 · 11:41 · 2019-12-26 · 7.9万/7250 — RocketJump Film School《Cuts & Transitions 101》的中字搬运（原片 https://www.youtube.com/watch?v=OAH0MoAv2CI ，453.9万播放）：逐个列举并定义各种剪辑和转场，配经典和现代电影片例
- [Ultimate Guide to Scene Transitions – Every Editing Transition Explained \[The Shot List, Ep 9\]](https://www.youtube.com/watch?v=TKXBAaQB03U) — StudioBinder · 19:28 · 2021-11-29 · 147.8万/— — 9 种基本转场（含 J-cut、match cut、淡入等）的定义和片例
- [17种常见的无技巧转场（看完没收藏，你比导演强）](https://www.bilibili.com/video/BV1N34y1L7yo) — 费无极-短视频编导 · 30:54 · 2022-06-03 · 42.0万/5.8万 — 不靠特效、靠镜头内容衔接的 17 种无技巧转场；具体是哪 17 种简介没列，需看视频

### 遮挡 / 隐藏剪辑点 / 一镜到底拆解

- [【基础篇】二十五期：遮挡转场这样用。](https://www.bilibili.com/video/BV1WN411a7vK) — 详细而完备的剪辑课 · 2:06 · 2023-08-07 · 2.4万/1066 — 趁画面里的东西挡住镜头或主体的那一瞬切到下一镜（标签含遮黑转场、剪辑点）
- [【拉片系列】"一镜到底" 在后期怎么剪辑？](https://www.bilibili.com/video/BV1nG4y1z73s) — 阿次的寶藏片場 · 12:53 · 2022-09-10 · 3.9万/1694 — 拉片拆解一镜到底在后期怎么拼，主要靠遮罩藏接缝；附拉片工程和遮罩素材
- [伪长镜头的剪辑方法——"一镜到底"让摄影机停不下来](https://www.bilibili.com/video/BV1Dx4y1A7KD) — 小小影视人 · 4:23 · 2023-03-17 · 3.9万/1179 — 以《1917》为例讲全片 60 多个镜头怎么骗过观众，以及影史上伪长镜头手法的演变
- [Movie Breakdown | The Hidden Cuts of: 1917](https://www.youtube.com/watch?v=ZAQoY3ioci0) — HarrisonTheEditor · 4:07 · 2020-01-29 · 53.1万/— — 逐个标出《1917》里藏起来的剪辑点
- [Movie Breakdown | The Hidden Cuts of: Birdman](https://www.youtube.com/watch?v=KYfiblQccHo) — HarrisonTheEditor · 2:04 · 2023-03-21 · 1.2万/— — 逐个标出《鸟人》里藏剪辑点的位置，并说明藏剪的原因（如换镜头）
- [How to fake a LONG TAKE with hidden cuts! | 4 editing tricks](https://www.youtube.com/watch?v=NkdHY74uatQ) — Steve Ramsden · 9:25 · 2022-08-20 · 16.9万/— — 4 种把连续动作伪装成一个长镜头的隐藏剪辑技巧，参照《1917》《鸟人》《人类之子》《007：幽灵党》《王牌特工》教堂戏和希区柯克

### 匹配剪辑

- [【干货】"无缝剪辑"，你必须知道的3种匹配剪辑手法](https://www.bilibili.com/video/BV1vf421f7ra) — 泰迪熊本熊-TBK- · 6:36 · 2024-03-19 · 13.3万/4852 — 匹配剪辑三类：图形匹配、运动匹配、声音搭桥
- [一条视频学会10+相似性转场 也就是匹配剪辑](https://www.bilibili.com/video/BV1zeGe6cESK) — 李神仙z · 3:39 · 2026-05-23 · 4480/456 — 相似性转场分六类：形状和构图、动作与运动轨迹、运镜方向、色彩、材质/介质、声音

### 甩镜

- [Art of the Whip Pan Shot: Motivating Your Swish Pan Effects & Transitions #whippan #swishpan](https://www.youtube.com/watch?v=ZhYvs7rrGnw) — StudioBinder · 6:38 · 2019-05-06 · 28.6万/— — 甩镜（whip / swish pan）是什么、怎样让甩镜有动机，以及影视剧里用甩镜做转场的例子

### 动作剪辑与连续性

- [如何选择剪辑点？抓住动作与剪辑的关联！](https://www.bilibili.com/video/BV1oM4y1j7Gy) — 董肯特 · 9:01 · 2023-07-12 · 9.6万/6932 — 讲剪辑点怎么选：抓住动作和剪辑的关系（动作剪辑的底层逻辑），配电影拉片
- [让电影剪辑变丝滑的秘诀！全盘托出！连续性剪辑和不连续性剪辑](https://www.bilibili.com/video/BV1Py4y197Nf) — Lancy大梦想家 · 11:09 · 2023-02-03 · 2324/103 — 连续性剪辑的规则（标签含 180 度、30 度原则），并和不连续剪辑对比

### 声音先行

- [用好L-Cut和J-Cut，摆脱新手剪辑的帽子](https://www.bilibili.com/video/BV1WJ411W7Si) — Gaiamount · 4:57 · 2019-12-25 · 2.7万/2578 — Fandor《SFX Secrets: The J Cut & The L Cut》中字（原片 https://www.youtube.com/watch?v=eyH-a964kAs ，49.6万播放）：声音比画面先切或晚切，让剪辑显得无缝

### 闪白 / 空镜

- [5种"闪白"的剪辑思维技巧用法！剪辑教程/镜头语言/剪辑节奏/音效设计/旅拍/vlog/广告宣传片/pr/fcpx/剪辑师](https://www.bilibili.com/video/BV1nm411Z7ug) — 南门录像厅 · 5:45 · 2024-03-04 · 11.2万/5891 — 闪白的 5 种用法，从传统的闪回记忆讲到在日常视频里做节奏和转场
- [学剪辑第14天 无技巧转场之"空镜头转场"](https://www.bilibili.com/video/BV1JP411S7V8) — 做后期的李三点 · 4:09 · 2023-04-16 · 1.2万/547 — 用空镜头过渡的无技巧转场；具体例子简介没写，需看视频

## 3. 跨镜头一致性（直接服务于衔接）

- [多段 AI 视频怎么拼才不穿帮？人物站位一致性保姆级教程](https://www.bilibili.com/video/BV19KJm6GEfq) — 小勇学AI · 13:21 · 2026-10-15 · 1240/61 — 多段 AI 视频拼起来怎么不穿帮，重点是前后镜头人物站位不跑偏；在一个无限画布平台上演示
- [AI人物总乱跑？3张参考图锁死站位 AI视频里，人物和道具一换镜头就乱跑？这次用自制短片实测一套站位锁定方法](https://www.bilibili.com/video/BV1msat6rE7z) — AI漫剧设计人 · 2:31 · 2026-09-28 · 3260/320 — 用 3 张参考图（标签含三视图）锁住换镜后人物和道具的站位，用自制短片实测
- [AI视频场景一致性完整工作流：俯视图、九宫格、全景图与GPT-image2调整方法拆解](https://www.bilibili.com/video/BV1jP9aBJEXr) — HiShineAi · 6:37 · 2026-04-30 · 14.3万/1.7万 — 5 种场景一致性方案：俯视图 + 九宫格、720° 全景截图、Seedance 2.0 全能参考、360° 环绕动态捕捉、GPT-image2 出分镜
- [AI视频人物总变脸？这份指南教你稳住角色一致性](https://www.bilibili.com/video/BV19kZRBsEfJ) — 大象学长_ · 6:03 · 2026-02-18 · 14.1万/1.4万 — 像制片一样管理「AI 演员资产」，靠一个关键提示词让同一角色在不同场景、大幅运镜下保持一致；是哪个词简介没说，需看视频
- [收藏！AI影片色调统一保姆级教程](https://www.bilibili.com/video/BV1DxArz4ED6) — ANUOai · 2:35 · 2026-02-26 · 8248/679 — 用色彩迁移统一各镜头的色调，用九宫格分镜保持光影一致，从单帧做到成片
- [Wan2.2 Fun Vace首尾帧偏色不完美解决方案+混元Image2.1确认comfyui复现仍有问题](https://www.bilibili.com/video/BV1tWpLzaEo7) — AIwood爱屋研究室 · 3:32 · 2025-09-13 · 6962/99 — Wan2.2 Fun VACE 和官方首尾帧接出来会偏色、画质下降，比较 ComfyUI 官方流和 KJ 流各自的代价（作者自己说方案不完美）
- [MINIMAX-H3长视频注噪淡化，处理色差 画质 闪烁](https://www.bilibili.com/video/BV1tK8U6tEvr) — 哈龙0102 · 5:07 · 2026-08-23 · 1983/70 — MiniMax H3 分段接长视频时出现的色差、画质下降、闪烁，用注噪和淡化处理；简介只有网盘链接，细节需看视频
- [Color Grade Mismatched Footage for ONE Consistent Look - DaVinci Resolve](https://www.youtube.com/watch?v=UshybSkwHoE) — Daniel Batal · 23:39 · 2026-08-21 · 3.7万/— — 在达芬奇里把来源不同、互不匹配的素材调成同一种外观（后期统一色调）

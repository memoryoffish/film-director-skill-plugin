---
name: film-director
description: 照剧本当导演，用 AI 视频模型拍短片的合订版 skill，三部分：拍片的全流程（分镜、定妆与关键帧、生成与检查、剪辑，带接法库）；拍之前在 Blender 里把一场戏搭成白模，管住位置、朝向、机位和切点；从 Freesound 挑靠得住的音效。做法和具体模型无关，默认电影感。Use when the user wants to make an AI film or short from a script, remake a film scene shot by shot, plan shots and cuts for AI video, join AI clips without visible seams, block a scene in Blender when positions, facing, eyelines or camera angles keep coming out wrong or several shots must show the same place from different cameras, or pick sound effects or reference recordings from Freesound — AI 电影 / 电影质感 / 大片感 / 分镜 / 定妆 / 参考图 / 台词 / 配音 / 补人声 / 口型 / 表演 / 打斗 / 复刻电影 / 进度页 / 镜头时长 / 升格 / 宽银幕 / 调色 / 声音设计 / 视频衔接 / 转场 / 首尾帧 / 续写 / 一镜到底 / 匹配剪辑 / 闪白 / J-cut / L-cut / 盲选 / 白模 / 预演 / previz / blocking / 机位 / 轴线 / 越轴 / 反打 / 视线 / 同一个地方几个机位 / 参考视频控制运镜 / 找音效 / 选音效 / 标准声音 / 参考录音 / 参考集 / Freesound.
---

# film-director

一句话：拿到剧本，像导演一样先想清楚观众该看见什么，把片子设计好，再一段段生成、检查，最后剪成片。三部分各管一件事，路径都相对本目录。

| 要做什么 | 读哪份 |
| --- | --- |
| 从剧本拍一部片：分镜、定妆与关键帧、生成与检查、剪辑；两段之间怎么接 | [video-film-maker/GUIDE.md](video-film-maker/GUIDE.md) |
| 一场戏空间上容易错（几个机位要认得出是同一个地方、谁在谁左边、门往哪开、间距），先在 Blender 里搭白模，量清楚再拍，成片对着白模查 | [blender-previz/GUIDE.md](blender-previz/GUIDE.md) |
| 视频模型配的音效不满意，从 Freesound 挑现成的录音（只取 CC0 和 CC-BY，带署名） | [refsound/GUIDE.md](refsound/GUIDE.md) |

- 拍片从 video-film-maker 读起，它会在要用白模、要找音效的地方指过来。白模和音效两部分也能单独用：手里有镜头表就能搭白模，有要找的声音就能挑录音。
- 三部分里提到「blender-previz skill」「video-film-maker skill」「refsound」，指的就是本目录下同名的子文件夹。

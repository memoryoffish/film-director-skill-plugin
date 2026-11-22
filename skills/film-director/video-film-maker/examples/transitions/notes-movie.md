# 衔接怎么搭配：细节

从 [衔接怎么搭配](../../transitions/movie.md) 挪来的原文：主干表（带例子）、点缀和首尾呼应的例子、plan 的伪代码、几条规则的细节。整部片怎么搭的见 [《两张照片》](../films/two-photos.md)、[《回家》](../films/homecoming.md)、[四种类型](../films/genre-tests.md)。

## 先定主干（原文）

| 片子 | 主干方法 | 例子 |
|---|---|---|
| 旅程、一镜到底感，要换很多地方 | [遮挡转场](../../transitions/occlusion.md) | 《回家》：4 次遮挡转场；《两张照片》：3 次遮挡 + 色彩匹配 + 声音搭桥，首尾媒介转变 |
| 同一场景的连续动作，只是被单次时长切开 | [视频续写](../../transitions/extension.md)；要换机位用 [动作匹配](../../stages/4-edit/match-on-action.md) | 雪镇敲门 |
| 回忆、故事里的故事、照片和现实来回 | [媒介转变](../../transitions/optical.md)、[闪白](../../transitions/optical.md) | 照片推近 → 活过来 |
| 大空间跨越（地面 ↔ 天空、城里 ↔ 海边） | [首尾帧过渡段](../../transitions/bridge.md)（拆成几次调用） | 松林 → 云上 → 雪山 |
| 剧情片、动作片：一场戏里很多镜头 | [分镜单元](../../stages/3-generation/shot-unit.md)（单元之间切镜）、[动作匹配](../../stages/4-edit/match-on-action.md) / [动势剪辑](../../stages/4-edit/momentum.md) | 拳馆大片版、4 部电影复刻；打斗《铁桥》 |

## 点缀（原文）

- 画面呼应：[色彩匹配](../../transitions/match-cut.md)（满屏的红大衣 → 满屏的红灯笼）、图形匹配。

## 首尾呼应（原文）

- 开头「照片 → 实景」（媒介转变），结尾「实景 → 照片」（放回同一张桌上）。
- 开头从云里降下来，结尾升回云里。
- 开头和结尾的遮挡物是同一种东西，镜头运动方向相同。

## Plan（原文）和伪代码

- **时间线**：衔接用的东西几秒出现（例：11–13 秒遮挡物从右侧进来盖满）。

```
plan = [{调用名, 方式: 文生 | 参考图 | 续写(接哪次调用, 喂最后几秒), 时长, 提示词, 时间线, 和前一段怎么接, 和后一段怎么接}, ...]
generate independent calls in parallel; extensions after their source
for call in plan:
    for take in 1..TAKES:
        clip = generate(call, seed + take)
        start, end, problems = check(clip, 和前一段怎么接, 和后一段怎么接)   # 盖满 / 满屏同色 / 复述对得上
        problems += own_cuts_near(clip, start, end)                       # 只查接缝附近
        if not problems: accept(call, clip, start, end); break
    else: stop and report
film = join(accepted, dissolve at occlusion seams, head speed-up where B starts slow)
trim to TARGET, fade in/out
```

## 好用的规则（原文）

- **同一场景因为单次时长被拆成几段**：想把剪点完全藏住，就安排一个会横穿镜头的东西做遮挡。

## 全片的一致性（原文）

- 每段用同一组人物参考图（从人物第一次出现的那段截）。

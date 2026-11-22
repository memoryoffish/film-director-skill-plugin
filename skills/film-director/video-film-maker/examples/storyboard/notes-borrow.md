# 借鉴：细节和拉片拆出来的规律

从 [借鉴](../../stages/1-storyboard/from-films.md) 挪来的原文：每一类规律要问什么、伪代码、《奎迪》《悟空传》和 4 部复刻原片拆出来的完整规律和数字。拉片报告本身在仓库里的 `../../refs/background/film-refs`。

## 拆出规律：每一类问什么

   - 镜头长度：快切多快、什么时候放长、高潮后怎么变；
   - 景别搭配：哪些景别接在一起、有没有跳过中间的尺度；
   - 空间：什么时候给大全景、隔多久重新交代一次；
   - 动作：剪在哪一刻、动作前后接什么（大特写、反应镜头）；
   - 视线和方向：谁在左谁在右、先看再看见；
   - 声音：哪里收、哪里全静、哪里一声进来；
   - 反复出现的机位和母题。

## 伪代码

```
for beat in beats if beat.borrow:
    scenes = similar_scenes(beat.situation, n=2..3)          # 处境相近，不必同类型
    for s in scenes: s.shots = breakdown(s)                  # 见 notes-remake.md「拆镜」
    rules  = common_patterns(scenes) + chosen_styles(scenes) # 长度、景别、空间、动作、视线、声音、母题
    beat.shots = design(beat, rules)                         # 只用规律，画面是自己的
    for shot in beat.shots: shot.note = rule_used(shot)
review(film, against=shot_list)                              # 不对原片
```

## 拉片拆出来的规律（原文）

- 《奎迪》（2015）最后一回合：71 镜，中位 1.42 秒，77% 手持。每两三个打斗镜头插一个约 1 秒的反应镜头（教练、对手教练、女友、在家看电视的母亲），最后十秒收紧到一比一交替；打斗中两次用低机位广角的大全景重新交代空间；只有击倒那一镜是慢动作；击倒后镜头长度翻倍；首尾用一对镜像的 A、B 镜头呼应。仓库里的 `../../refs/background/film-refs/breakdown/creed_final/beats.md`「Editing grammar」。
- 《悟空传》（2017）天尊之战：大场面前后一架尺度阶梯（大全景里很小的人 → 中近景）；蓄力 → 兵器插入 → 攻击的大全景；每次撞击接一个吃力或反应的特写；转场藏在火、闪白、前景擦过、甩镜里；每拍至少一个 3 秒以上的镜头。仓库里的 `../../refs/background/film-refs/breakdown/wkz_tianzun/beats.md`。
- 4 部复刻的原片各有一节剪辑规律：《亡命驾驶》主角全是固定机位、劫匪用手持，用机位分出冷静和慌乱，警车只隔着玻璃远远出现；《沙丘》巨虫只在大全景或巨口大特写里出现，没有中间尺度；《敦刻尔克》每个主观镜头前先有一个看的特写；《英雄》慢动作的湖面和实速的山坡交替，一颗水珠带着剪辑从对决走到灵床。`../../refs/background/film-refs/new/breakdown/<片名>/beats.md`。

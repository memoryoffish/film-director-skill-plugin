# 复刻：细节

从 [复刻](../../stages/1-storyboard/from-films.md) 挪来的原文：拆镜和照着拍几步的细节（自动拆镜会漏、会多的情况）、伪代码、规则和案例的原文。正文只留了步骤，这里的编号对应正文的步骤；要细节时来这里。

## 拆镜

1. 先量原片画幅（有没有黑边，16:9 还是 2.39:1）。
2. 自动拆镜只当候选：
   - 会漏：暗场、亮而低反差的段落、慢叠化、藏在镜头里的短闪切、藏在甩镜里的切；
   - 会多：闪光、爆炸、甩镜、车灯眩光、影子扫过脸；
   - 两路一起量（颜色分布跳变 + 相邻帧画面差），每个边界把亮度拉开逐帧看。
3. 拆解本身也会写错（转向写反、左右写反、位置写错）。
4. 按节拍分段，每拍写它做到了什么（见 [节拍](../../stages/1-storyboard/script.md)）。

## 照着拍

5. 定剪法：原片太长就删戏外的镜头、裁长镜头。
6. 原片里模型拍不出的（剪影、开关灯、叠在画面上的脸、水里的倒影、匹配叠化）先标出来。
7. 单元内的切点按帧号换算成秒。

## 伪代码

```
cuts  = candidates(film, color_jumps) ∪ candidates(film, frame_diff)
cuts  = verify(cuts, frames around every boundary, brightened)       # 补漏切、删误报
shots = [describe(film, a, b) for a, b in pairs(cuts)]               # 景别、机位、左右、朝向、动作
shots = recheck(shots, first / mid / last frames of the original)    # 拆解也会写错
beats, grammar, hard = summarize(shots)                              # 借鉴到这里为止
units = group(shots, max_len=MAX_CALL)                               # 同一种光一组；动作接动作、视线接主观镜头放一起
for u in units: u.table = [(f - u.first_frame) / fps for f in u.cut_frames]
```

## 好用的规则

- 单元分组：很长的镜头单独一个单元，重抽时不连带别的。
- 原片很暗时，按正常曝光生成、剪辑里再压暗：照文件的暗度做，夜和晨一样暗，时间跳跃读不出来（一次实测）。

## 案例（原文）

- [复刻《敦刻尔克》第一次空战](../films/remake-dunkirk.md)：自动拆镜漏了两个闪切；面罩状态靠两套参考图。
- [复刻《亡命驾驶》Getaway](../films/remake-drive.md)：1:1 复刻；拆解有两处转向写反，修复时才发现。
- [复刻《沙丘》夜行 + 沙虫](../films/remake-dune.md)：自动拆镜漏掉一大半；原片很暗，按正常曝光生成再调暗。
- [复刻《英雄》湖面之战](../films/remake-hero.md)：慢镜头加长；叠脸、倒影交给剪辑。

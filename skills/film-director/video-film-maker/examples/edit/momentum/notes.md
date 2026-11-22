# 动势剪辑：细节

从 [动势剪辑](../../../stages/4-edit/momentum.md) 挪来的原文：伪代码、带数字的规则、同一条教学视频里的两个相关做法。每次实际用的值见各案例。

## 伪代码

```
steps_a = gait_phases(A); steps_b = gait_phases(B[later_half])
cut_a   = frame where leading foot pushes off and body leans forward
start_b = same leg, same phase in B (after camera has settled at new angle)
join(A[..cut_a], B[start_b..])
```

## 好用的规则（原文，带数字）

- 剪在**迈步前倾、前脚蹬地**的那一帧；两步之间脚并拢处切会跳。
- **视角变化 ≥ 30°**（写 45°）；两边都在动，不从静止突然起步。
- #2 至少生成 **8 秒**，只用新机位到位以后的部分。
- 认腿按「离镜头近的那条腿」；每步左右腿交替，接错腿会别扭。
- 两边步频差几个百分点内不用变速。

## 相关的两个点（同一条视频里）

- **声音先行引出下一个空间**：先听到下一个空间的声音，再切过去（见 [声音类](../../../stages/4-edit/sound.md) 的 J-cut）。
- **全景跳近景**：动作节拍处直接从全景切近景（见 [两极镜头](../../../transitions/extremes.md)）。

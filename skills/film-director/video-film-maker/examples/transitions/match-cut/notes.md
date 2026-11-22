# 匹配剪辑：细节

从 [匹配剪辑](../../../transitions/match-cut.md) 挪来的原文：图形匹配、色彩匹配的伪代码，带数字的思路、规则和检查，没试过的补救。门槛在 [refs/practical/config-transitions.md](../../../refs/practical/config-transitions.md)「色彩匹配满屏」；每次实际用的值见各案例。

## 图形匹配：带数字的思路、规则和检查（原文）

1. 两段都写死主体的**位置和大小**（正中、直径约画高 1/3）；A 最后约 2 秒镜头停住，B 开头先停约 1 秒再展开新场景。

- 原视频建议把素材保留 2–5 帧逐一对齐。

- 两边主体的位置、大小差多少：差 2 倍以上要在剪辑里放大补，补完太软就重抽。

## 图形匹配：伪代码

```
ca, ra = median(find_shape(A[-10:])); cb, rb = median(find_shape(B[:15]))
for f in A[cut-1.5s : cut]:  scale, shift = smoothstep(1 → rb/ra, ca → cb)
join(A_zoomed, B)
```

## 色彩匹配：带数字的思路、规则和检查（原文）

2. #2：从满屏同色开始，先停约 1 秒再拉开。颜色**直接点名 A 的东西**（「和熟橙子果肉一样的橙色」），两边就对得很近。

- 推镜给足 **4 秒以上**，提示词一开头就写「一个连续的镜头运动，没有叠化、没有两层画面」。
- A 满屏后留 **12–16 帧**再切；B 先停约 **1 秒**再拉开。
- 差一点满屏时，可以在剪辑里补一点放大（没试过）。

- B 揭开后紧跟着有没有自带切镜（接缝后约 1.2 秒内）。

## 色彩匹配：伪代码

```
fill(f) = share of pixels with hue in [H0, H1]  and  max block color distance small
a_end   = first fill frame in A.tail + HOLD
b_start = first fill frame in B
```

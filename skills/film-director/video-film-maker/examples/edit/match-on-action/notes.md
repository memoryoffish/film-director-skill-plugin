# 动作匹配：细节

从 [动作匹配](../../../stages/4-edit/match-on-action.md) 挪来的原文：伪代码、速度差的数字。每次实际用的值见各案例。

## 伪代码

```
pa = progress(A, object)          # 物体位置归一成 0..1（静止 → 落地）
pb = progress(B, object)
cut_a = last frame with pa < 0.5;  start_b = first frame with pb > pa[cut_a]
# 抛起物：cut_a = apex(A), start_b = apex(B)（物体可能在最高处悬停，按时间归一会对错）
join(A[..cut_a], B[start_b..], audio_crossfade=0.25s)
```

## 速度差

- 两边动作速度差在 10–20% 以内不用管；差得多再变速。

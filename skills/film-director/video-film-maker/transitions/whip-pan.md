# 甩镜（whip pan / swish pan）

一句话：A 结尾摄影机原地极快地横摇，画面糊成横向拖影，剪点藏在最糊的几帧里；B 开头沿同一方向甩进来再停住，落到新场景。少用。

## 什么时候用

要把场景换到别的地方、别的时间；甩镜也能延续上一场的势头。

## 思路

1. A：先固定机位，再**摄影机自己**极快地甩出去（写明没有东西从镜头前经过，不然模型会让一列火车开过来当遮挡）；到最后一帧还在甩。
2. B：开头还在同方向甩，约 1 秒减速停住，落到新场景。
3. 剪点：A 取甩镜里最糊、还没有别的东西入画的一帧；B 从还在甩的一帧起。两边方向要一致。
4. 甩得不够糊时，剪点前后各几帧加人工横向模糊。

```
blur(f)  = sharpness(f)  (laplacian variance);  dir(f) = horizontal flow
cut_a    = argmin blur over A.whip;   start_b = first frame in B still whipping
assert sign(dir(A near cut)) == sign(dir(B near start))
for k in -N..N: horizontal box blur with length L(k) = PEAK * (1 - cos) shape, max at the cut
```

## 好用的规则

- 两段甩的方向写成一样。
- 人工模糊：剪点前后各 **6 帧**，模糊核的长度（也就是拖影有多长）先升后降，峰值约画面宽的 **1/5**（1280 宽时约 280 像素）。
- B 甩入约 **1 秒**后停稳。

## 生成后检查（不合格就重抽）

- A 是摄影机自己甩，还是有东西从镜头前经过（后者重抽，删掉提示词里会动的大东西）。
- 甩的方向两边一致。
- 甩完有没有别的东西闯进来（只用到它之前）。

# 视频续写：细节

从 [视频续写](../../../transitions/extension.md) 挪来的原文：伪代码、原来的规则（喂几秒、生成时长、官方写法的出处）、两种同类做法（未实测）。门槛在 [refs/practical/config-transitions.md](../../../refs/practical/config-transitions.md)「衔接检查」；每次实际用的值见各案例。

## 伪代码

```
inp = A[cut - 3s : cut]
B = extend(inp, prompt, duration = 3s + EXTRA)
for a in A[cut] down to A[cut - 3s]:                  # 从 A 结尾往回找
    k = best_match(a, B[: 3s + 2s])                     # B 里最像 a 的帧
    if similarity(a, B[k]) >= MATCH: break
else:
    retake()                                            # 模型重画了输入，硬接会跳
join([A[..a], B[k+1 ..]])
```

## 好用的规则（原文）

- 喂最后 **2–3 秒**（看得到完整的运动）；生成时长 = 3 + 延长秒数。
- 接缝放在复述还对得上的最后一帧；**让 A 提前结束，不要往后跳 B**。
- 镜头不动时看动作有没有接上（速度量不出来，逐帧看）。
- **东西不凭空出现**：#1 把画面里的东西列死，加一句「别的什么都没有」；#2 写「只用画面里已有的东西，不出现新东西，也不凭空消失」。不要点名说不要什么东西（点名反而会画出来）。
- #2 的提示词看完 #1 的结尾再写，从 #1 **实际**停下的动作写起。
- 续写可以同时带参考图，用来锁人物和道具（输入里看不到脸时尤其要带）。
- 提示词：中文写「将视频1向后延长 N 秒」「一镜到底，没有剪辑，没有叠化，没有跳变」「声音：……，没有音乐，没有人声」；官方写法见 [wan3-pe](../../../refs/practical/prompt-skills/overview.md)「案例 B：完整视频首段 + 向后续写」、[sd25-pe](../../../refs/practical/prompt-skills/overview.md)「视频延长模板」。

## 同类做法（未实测）

- **动作重叠法**（刺猬星球）：下一段开头先把上一段最后的动作做完，剪辑时在重叠的动作里找衔接点。
- **Sora Blend**（地质大学博士）：A 延长到 10 秒 → 用后半段和 B 做 blend → 替换后 2 倍速。

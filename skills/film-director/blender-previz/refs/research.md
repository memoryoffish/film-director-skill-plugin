# 调研：别人怎么用 Blender 白模管 AI 视频

2026-11-17 查的。每条后面是出处；带「我们」的一列是在 Wan 3.0 上自己遇到的。这一篇是摘要；逐条原话、读过的全部链接和资产许可证核对在 [sources/](sources/overview.md)（完整调研 [research.md](sources/research.md)、[sources.md](sources/sources.md)、[assets.md](sources/assets.md)）。

## 结论

- 主流接法已经换成「白模视频当参考视频」，不再喂深度图、姿态图。 出处：Seedance 2.5、Wan 3.0、Kling 4.0 的官方文档都写了白模：[Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)、[Wan 3.0 官方提示词指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)、[Kling 4.0 官方博客](https://kling.ai/blog/kling-4-ai-video-model)
- 分工有共识：白模管位置、朝向、机位、运镜、切点；参考图管长相、衣服；提示词管表演、光和禁令，并写明三者冲突时听谁的。 出处：[7ohnson 的白模 harness](https://github.com/7ohnson/VLM-Generation-Harness)、[ComfyUI 官方工作流](https://github.com/Comfy-Org/workflows)、[Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)
- 白模里错的，模型照学：走太快成片就瞬移，平光被抄成平光，占位方块变成方盒子家具，轨迹线和文字会漏进画面。 出处：[娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)、[7ohnson 实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md)、[Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)
- 人偶越粗越好；四肢可以没有，朝向标记必须有；最怕「有一点动作但很僵」的中间态。 出处：[scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)（同场景三种人偶对照）、[GrandVisionsAI（X，同提示词对照）](https://x.com/GrandVisionsAI/status/2096993565599490465)、[娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)、[ComfyUI 官方短片](https://www.youtube.com/watch?v=2BCnIRyVWIk)；反例：[7ohnson 铁律](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md)（裸圆柱认不出朝向）
- 片段要短：10–15 秒保得住机位和布局，20–30 秒会漂；单个镜头超过 6–7 秒，模型会自己加切点。 出处：[scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)（28 条成片的统计）、[7ohnson 实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md)
- 不是每个镜头都值得搭：固定机位、单人、原地转、正反打，写清左右就够；空间要连起来的镜头才明显有用。 出处：[娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)、[DeepWhite（B 站）](https://www.bilibili.com/video/BV1xBWv6qEC7)、[Mixar](https://www.mixar.app/blog/blender-blockout-to-video)
- Wan 3.0 的白模路线只有官方文档，没找到任何社区实测；实测几乎全在 Seedance 2.5 上。 出处：所以下面一节是我们自己在 Wan 3.0 上测的

## 几种接法

| 接法 | 别人怎么做 | 出处 |
|---|---|---|
| 白模视频当参考视频 | Blender 渲一段预演（≤15 秒，可含多个镜头和切点），连同人物参考图走「参考生视频」；提示词写明白模只提供走位、机位、切点，逐个说明哪个人偶是谁。 | [Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)、[Wan 3.0 官方提示词指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)、[ComfyUI 官方工作流](https://github.com/Comfy-Org/workflows)、[TanLuAI（X 长文，带完整提示词）](https://x.com/TanLuAI/status/2099124935285461329)、[DeepWhite（B 站）](https://www.bilibili.com/video/BV1xBWv6qEC7)、[adilinthewild（X）](https://x.com/adilinthewild/status/2093662540119281877)（6 人 4 次切镜没换座）、[7ohnson 实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md)（16 秒 7 镜，切点最大偏差 0.07 秒） |
| 每个镜头一张白模图，当参考图 | 别人的做法是把机位静帧转写实后当首帧（见下一行）；直接把白模图当参考图是我们加测的。 | 相近的做法：[Blockout](https://github.com/wassermanproductions/blockout) 的 stills 档、[LibTV 导演台测评](https://www.sohu.com/a/1030583709_122571656) |
| 白模图转写实，当首帧或首尾帧 | 取白模机位图，用图像模型转成成片的样子，当首帧；运动靠文字，或再给白模视频。首帧看不到的地方会被乱编，可再补一张参考帧。 | [LTX-2.5 Layout-to-Render 模型卡](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Layout-To-Render)、[flick.art](https://flick.art/blog/blender-ai-filmmaking)、[时光之刃（B 站）](https://www.bilibili.com/video/BV1z3NJ6NEDM)、[Luma Ray 3.2 官方](https://lumalabs.ai/learning-center/articles/ray-3-2-video-to-video)；反对：[scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)（单张风格帧会把构图和形状带进视频） |
| 白模不喂模型，只算事实写进提示词 | 脚本从几何算出每个镜头谁在画面左右、谁挡谁、景别，抄进提示词，并查越轴。成本最低。 | [娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)（四人几十个机位，左右一次没写错）、[nana-whitebox](https://github.com/nawusijia/nana-whitebox)、[7ohnson 铁律](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md) |
| 细白模逐帧「上色」 | 3D 里模型、动画、机位都做完整，渲 clay render，让模型只换材质和颜色。 | [Wan 3.0 官方提示词指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)（官方示例）、[Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)（细粒度） |
| 深度图、姿态图控制（开源模型） | Blender 直接渲深度通道当控制视频。2025 年的主流，2026 年社区基本转去了参考视频。 | [VACE 官方](https://github.com/ali-vilab/VACE/blob/main/UserGuide.md)、[LTX IC-LoRA 文档](https://docs.ltx.io/open-source-model/usage-guides/ic-lo-ra)、[CozyClay 指南](https://cozyclay.org/greybox-to-video/) |

我们在 Wan 3.0 上各测到什么，见 [examples/feeding-tests.md](../examples/feeding-tests.md)。

## 白模该做成什么样

| | 别人的说法 | 出处 | 我们 |
|---|---|---|---|
| 人偶 | 真实身高和比例；一定要看得出正面（面罩、鼻子块、胸牌）。多数来源说别带四肢，只平移；要特定肢体动作才上带骨骼的假人配真动作。 | [Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)、[scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)、[娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)、[ComfyUI 官方短片](https://www.youtube.com/watch?v=2BCnIRyVWIk) | 我们两种都有：带关节的人偶（鼻子 + 胸牌）自己看、当参考图、转首帧；当参考视频的预演里只放没有四肢的替身（脸牌 + 鼻子）。带关节人偶当参考视频时，站姿和动作都被抄进成片。 |
| 颜色 | 各家相反：Seedance 官方示例按颜色指认角色；也有人实测高饱和色会被读成衣服颜色，主张给模型的那版全灰。没有对照。 | 上色：[Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)、[scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)、[TanLuAI（X 长文，带完整提示词）](https://x.com/TanLuAI/status/2099124935285461329)；不上色：[7ohnson 的白模 harness](https://github.com/7ohnson/VLM-Generation-Harness)、[CozyClay 指南](https://cozyclay.org/greybox-to-video/) | 同一个楼梯镜头，蓝/红身份色的人偶当参考图，朝向对 2/2；换成衣服颜色的人偶 0/2（阿杰被画成面朝镜头）。只有这一组，先按身份色用。 |
| 场景 | 细节可以糙，体积、遮挡、尺度要准（门 2 米高）；要有地面和至少一个不对称地标；要看穿的地方必须是真的洞。 | [娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)、[CozyClay 指南](https://cozyclay.org/greybox-to-video/)、[Mixar](https://www.mixar.app/blog/blender-blockout-to-video)、[ai-muninn（H3 本地实测）](https://ai-muninn.com/en/blog/blender-blocking-h3-ref2va-rtx5090)、[7ohnson 铁律](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md) | 遇到了：门洞后面没放东西，被画成关着的门板；坐面高度算错，人被画成坐在靠背上。给门加了深色门框、屋里加了墙和地板之后就对了。 |
| 手和道具 | 没有共识：一派在白模里把手摆到道具上（道具特写里必须有手），一派人偶不要手、接触靠文字。 | 摆手：[7ohnson 铁律](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md)、[CozyClay 指南](https://cozyclay.org/greybox-to-video/)；不要手：[ai-muninn（H3 本地实测）](https://ai-muninn.com/en/blog/blender-blocking-h3-ref2va-rtx5090)、[TanLuAI（X 长文，带完整提示词）](https://x.com/TanLuAI/status/2099124935285461329) | 我们给人偶加了「手够到某个点」的解算，推沙发、开门锁、端饭盒的手都摆到位；转首帧时这些手的位置都被照着画了。 |
| 画面 | 给模型的那一版什么都不叠：轨迹线、坐标轴、相机视锥、镜号、文字都会漏进成片。要给人看的标注另渲一版。 | [Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)、[CozyClay 指南](https://cozyclay.org/greybox-to-video/)、[7ohnson 铁律](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md) | 我们的白模图不叠任何东西；平面图和布局说明另外出，只给人看。 |
| 速度和时长 | 按真人速度走，起停加缓动；白模和成片同画幅、同帧率、同长度；每段 ≤15 秒、每镜 ≤6 秒。 | [娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)、[ComfyUI 官方工作流](https://github.com/Comfy-Org/workflows)、[7ohnson 实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md)、[Wan 3.0 接口文档](https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference)（参考视频合计 ≤15 秒、≥16 fps，输入加输出 ≤30 秒） | 参考视频按输入秒数加输出秒数计费。 |

## 提示词怎么写

| | 写法 | 出处 |
|---|---|---|
| 写明只从白模拿什么 | 「文本中写明希望参考白模视频中的什么元素」；有参考图时「需写明参考图和白模的对应关系」，例如「将 [图片 1] 中穿灰色衣服的男人对应 [视频 1] 中的红色模型」。 | [Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689) |
| Wan 3.0 的写法 | 「参考图 1、图 2 的人物角色，仅参考视频 1 的视频动作……参考视频只用于动作控制，不继承其人物外观。最终画面正常彩色」。 | [Wan 3.0 官方提示词指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide) |
| 冲突时听谁的 | 「位置与朝向听白模的 · 长相与光听资产图的 · 其余听 prompt 的」；每张参考图都声明只取什么、不取什么。 | [7ohnson 提示词规范](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/03-prompt-spec.md) |
| 运镜只说一次 | 白模已经管了路线、机位和运镜，正文里不要再写一套不同的镜头运动，否则模型同时收到两套指令。 | [鱼摆摆喂（B 站）](https://www.bilibili.com/video/BV19gtc6aEQY)、[CozyClay 指南](https://cozyclay.org/greybox-to-video/) |
| 人偶不提供肢体动作 | 「几何人物只表示位置和移动方向，不提供肢体动作参考……不迁移方块滑行、僵硬姿态或机械摆动」；负面词点名「白模方块、几何人形、刚性滑行、塑料皮肤」。 | [TanLuAI（X 长文，带完整提示词）](https://x.com/TanLuAI/status/2099124935285461329) |
| 光 | 白模是平光，要写明光按文字来；否则平光会被抄走。 | [7ohnson 实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md)、[Runway 官方](https://help.runwayml.com/hc/en-us/articles/57074952895635) |
| 我们用的那一段（白模图当参考图） | 「图4、图5、图6依次是镜头1、镜头2、镜头3开头的白模站位示意图，只用来定每个镜头的机位、构图和站位：蓝色人偶的位置、朝向、姿势和动作就是阿杰的，红色人偶的就是小周的，绿色方块就是沙发的位置和方向……不要把人偶、白模的纯色质感、胸前的白牌画进成片；人和沙发的样子用前面几张参考图，场景的样子按文字写的来。」 | 自己的实测，多镜头单元 2/2 全对 |

## 翻车点

| 毛病 | 改法 | 出处 | 我们遇到没有 |
|---|---|---|---|
| 灰模材质、方块出现在成片里 | 提示词声明不采用白模外观；负面词点名；小道具不给造型 | [Wan 3.0 官方提示词指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)（官方负向清单）、[7ohnson 实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md) | 没遇到 |
| 人偶迈腿或程序化走路 → 成片走得僵、滑步 | 去掉四肢只平移，或给真动作 | [scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)、[娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW)、[DeepWhite（B 站）](https://www.bilibili.com/video/BV1xBWv6qEC7)、[Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689) | 遇到：参考视频抄了僵直的手臂 |
| 走得太快、起停太突然 → 成片瞬移 | 按真人速度，加缓动 | [娜乌斯嘉AI（B 站，三组对照）](https://www.bilibili.com/video/BV1aTWm6jEqW) | 没测 |
| 白模里的空白被照字面画 | 该是洞的地方后面要有东西；尺寸按真实的来 | [7ohnson 铁律](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md)、[Mixar](https://www.mixar.app/blog/blender-blockout-to-video) | 遇到：空门洞成了门板，人坐到了靠背上 |
| 身份互换、多出人 | 每个人偶单独映射；人偶在画面里要够大；人偶旁边不放零碎小块 | [Wan 3.0 官方提示词指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)、[Seedance 2.5 官方提示词指南](https://www.volcengine.com/docs/82379/2607689)、[DeepWhite（B 站）](https://www.bilibili.com/video/BV1xBWv6qEC7)、[scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills) | 遇到：参考视频里两个都成了阿杰；过肩镜头多出人 |
| 衣服图案跑到背面 | 提示词写明图案在胸前、从背后看不到 | 自己的实测 | 遇到：背影镜头里恐龙印在了后背 |
| 镜头在动还是人在动，模型分不清 | 场景里放地面和不对称地标；提示词写明「运动由镜头产生」 | [有趣的80后程序员（B 站）](https://www.bilibili.com/video/BV188tE6kEVL)、[ai-muninn（H3 本地实测）](https://ai-muninn.com/en/blog/blender-blocking-h3-ref2va-rtx5090) | 没遇到（都有墙、门、栏杆） |
| 长片段后半段漂、模型自己加切点 | 10–15 秒一段，单镜 ≤6 秒 | [scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)、[7ohnson 实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md) | 没遇到（最长 13 秒） |
| 参考图和白模场景对不上 → 场景错乱 | 场景图和白模出自同一个布局 | [DeepWhite（B 站）](https://www.bilibili.com/video/BV1xBWv6qEC7)、[302.AI 评测](https://302.ai/blog/302-ai-benchmark-lab-review-on-wan-3-0-video/) | 没遇到（没给场景图） |
| 首帧看不到的区域被乱编 | 补一张反打方向的参考帧 | [时光之刃（B 站）](https://www.bilibili.com/video/BV1z3NJ6NEDM)、[TanLuAI（X 长文，带完整提示词）](https://x.com/TanLuAI/status/2099124935285461329) | 遇到一点：只给首帧时大动作会跑，加尾帧就稳 |
| 相机被墙挡住、头出画 | 渲之前程序检查，每镜首中末帧出图看 | [7ohnson 铁律](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md)、[B 站：GPT-6 操作 Blender 白模预演](https://www.bilibili.com/video/BV1x7Yx6YEM6) | 遇到：脚本里加了「头出画」「镜头钻进人」两条报警 |

## 说法相反的

| 问题 | 两边 | 我们 |
|---|---|---|
| 人偶要不要四肢 | 不要（Seedance 官方、多数社区） / 要（7ohnson：裸圆柱认不出朝向和「在走」） | 带姿势的静态人偶当参考图没问题；当参考视频时僵。胶囊替身测过：正面、人不大的走位跟拍自然，静止时站成柱子；背影、人大的跟拍被画成柱子（见 [stages/1-build/fidelity.md](../stages/1-build/fidelity.md)）。 |
| 上不上色 | 上（Seedance 官方、scenario） / 给模型的那版全灰（7ohnson、CozyClay） | 身份色 2/2，衣服色 0/2（一组）。全灰没测。 |
| 外观用什么锁 | 白模首帧转写实（LTX、flick.art） / 用普通角色图和场景图（scenario、ComfyUI） | 两种都行：转首帧最稳但一镜一条；参考图能一次出多镜头。 |
| 白模带不带光 | 平光（7ohnson） / 带明暗（Luma、Blockout） | 没测；我们是一盏太阳灯。 |

## 值得读的工具

- [scenario 的 Blender 白模 skill](https://github.com/scenario-labs/skills)：给 agent 的 Blender 白模 skill，纯脚本、无头跑；人偶四档、对比实验、检查项。MIT。最值得读。
- [7ohnson 的白模 harness](https://github.com/7ohnson/VLM-Generation-Harness)：白模 harness：遮挡和占幅计算、切点核验、15 条铁律。MIT。
- [ComfyUI 官方工作流](https://github.com/Comfy-Org/workflows)：官方白模 → Seedance 2.5 工作流，带完整提示词和素材。
- [nana-whitebox](https://github.com/nawusijia/nana-whitebox)：俯视图摆人和机位，自动算左右、越轴、台词时长。MIT。
- [Blockout](https://github.com/wassermanproductions/blockout)：开源预演应用，导出参考视频 + 深度 + 机位静帧 + 俯视走位图。Apache-2.0。

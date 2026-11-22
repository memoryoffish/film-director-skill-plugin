# 3D 白模预演 → AI 视频：2025–2026 年的人实际怎么做

调研日期 2026-11-17。范围：B 站（字幕 + 评论）、X（搜索 + 公开接口读正文）、官方文档、GitHub、博客、YouTube 文字稿。读过的全部链接在 [sources.md](sources.md)，资产在 [assets.md](assets.md)。两份更细的底稿：[notes/models_notes.md](notes/models_notes.md)（各模型官方文档逐条引语）、[notes/tools_notes.md](notes/tools_notes.md)（工具逐项）。

**标注约定**

- 【官方】官方文档、官方仓库、官方模型卡的原文。
- 【实测】作者自己做了并给出结果；有同条件对照的写「对照」。
- 【经验】作者做过之后的说法，没有对照。
- 【宣传】厂商稿、平台合作视频、推广帖（步骤可信，效果评价不算证据）。
- 【转述】我没看到原文，只在搜索摘要或别人的引用里看到。
- 没标「转述」的引语都是从原页面、原字幕、原帖里读到的。B 站字幕是 AI 字幕，错别字（白魔、白膜）已按意思改回「白模」。

---

## 先说结论

1. **2026 年 7–8 月起主流接法换了。** Seedance 2.5 把「白模参考/渲染」做成官方任务，Wan 3.0、Kling 4.0 也把白模写进了官方文档，MiniMax H3 的参考生视频同样能吃。现在多数人不再喂深度图或姿态图，而是把一段白模 playblast 直接当**参考视频**，外观交给参考图和提示词。深度 / 姿态控制主要剩开源模型（Wan VACE、Wan Fun、LTX IC-LoRA）在用，闭源里只有 Kling 4.0 写了收深度图视频。
2. **分工有共识**（十几个来源一致）：白模管位置、朝向、机位、运镜、切点和时间；参考图管长相、服装、材质；提示词管表演、台词、光和禁令。提示词里要写明「只从白模拿什么、不拿什么」，以及三者冲突时听谁的。
3. **人偶越粗越好，有三个同条件对照（都是单次或少量生成）和两家官方说法支持**；反例也有。能对上的共识是：四肢可以没有，**朝向标记必须有**；要四肢就给真动作，最怕「有一点动作但很僵」的中间态。
4. **人偶上不上色，各家说法相反**，没有对照实验能判。Seedance 官方示例用颜色指认角色；有人实测高饱和色、描边、文字会被抄进成片，主张给模型的那一版全灰。
5. **白模里错的，模型照学**：走太快成片就瞬移，平光被抄成平光，占位方块被抄成方盒子家具，叠加的轨迹线和文字会漏进画面。
6. **片段要短**：参考白模 10–15 秒保得住机位和布局，20–30 秒会漂；单个镜头超过 6–7 秒，模型会自己加切点。
7. **Wan 3.0 的白模路线只有官方文档，没找到任何社区实测。** 社区实测几乎全在 Seedance 2.5 上，其次是 MiniMax H3、LTX。我们要用 Wan 3.0，得自己先测。
8. **不是每个镜头都值得搭白模。** 固定机位、单人、原地转、正反打，写清左右的文字就够；空间要连起来（楼梯接二楼、穿过人群、绕过前景、多机位同一房间）才明显有用。

---

## 0. 做法总表

| # | 做法 | 步骤一句话 | 给模型的控制信号 | 模型 / 工具 | 谁在用 | 证据强度 |
|---|---|---|---|---|---|---|
| A | **粗白模视频当参考视频**（最主流） | Blender 里用几何体摆人、景、机位，渲一段 playblast；连同人物 / 场景参考图一起走「参考生视频」，提示词写明白模只提供走位、运镜、切点 | 白模 mp4（参考视频）+ 参考图 + 文字映射（哪个几何体是谁） | Seedance 2.5、Wan 3.0、Kling 4.0、MiniMax H3；Blender / Three.js / 各家预演台 | [Seedance 官方](https://www.volcengine.com/docs/82379/2607689)、[Wan 3.0 官方](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)、[ComfyUI 官方工作流](https://github.com/Comfy-Org/workflows)、[scenario skill](https://github.com/scenario-labs/skills)、[TanLuAI](https://x.com/TanLuAI/status/2099124935285461329)、[DeepWhite](https://www.bilibili.com/video/BV1xBWv6qEC7)、[娜乌斯嘉AI](https://www.bilibili.com/video/BV1aTWm6jEqW)、[7ohnson](https://github.com/7ohnson/VLM-Generation-Harness)、[adilinthewild](https://x.com/adilinthewild/status/2093662540119281877)、[ai-muninn](https://ai-muninn.com/en/blog/blender-blocking-h3-ref2va-rtx5090) | **强**（Seedance 2.5 上：官方 + 多人实测 + 三个对照）；Wan 3.0 / Kling 4.0 只有官方说法 |
| B | **细白模「上色」重渲染** | 建模、动画、机位都做完整，渲 clay render；让模型只换材质和颜色，其余逐帧不动 | 细白模 mp4 + 「除材质与颜色外一律不改」的提示词 | Wan 3.0（官方示例）、Seedance 2.5 细粒度、即梦 Clay Renderer 插件 | [Wan 3.0 官方](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)、[Seedance 官方](https://www.volcengine.com/docs/82379/2607689)、[浩克肥虫](https://www.bilibili.com/video/BV1FdMk65EqW)【宣传】、[AIStackLabX](https://x.com/AIStackLabX/status/2096631495712751753)【宣传】 | 中（官方明确；社区多是推广稿，面向已有 3D 资产的人） |
| C | **转写实的首帧 + 白模视频** | 取白模第 1 帧，用图像模型转成成片样子；它当首帧（或关键帧），白模视频管运动 | 写实首帧 / 关键帧 + 白模视频（参考或控制） | LTX-2.5 Layout-to-Render、Seedance（提示词指定首帧）、Luma Ray 3.2（关键帧贴回源帧号）、Runway Aleph 2.0（改一帧带全段）；图像侧 Nano Banana、Seedream、gpt-image | [LTX 模型卡](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Layout-To-Render)、[flick.art](https://flick.art/blog/blender-ai-filmmaking)、[Polypro](https://x.com/Polypro_io/status/2114796010476314631)、[时光之刃](https://www.bilibili.com/video/BV1z3NJ6NEDM)、[Luma 官方](https://lumalabs.ai/learning-center/articles/ray-3-2-video-to-video) | 中（官方模型卡 + 几个个人流程；scenario 明确反对单张转风格帧） |
| D | **只用白模静帧** | 每个机位渲一张白模图，图像模型转写实，当首帧 / 首尾帧 / 多关键帧；运镜靠文字 | 首帧、首尾帧、关键帧序列 | Veo 3.1、Runway Gen-4.5、Kling、Vidu、Pika 等没有参考视频的模型；LibTV 导演台、Blockout 的 stills 档、Runway .glb | [LibTV 测评](https://www.sohu.com/a/1030583709_122571656)、[Blockout profiles](https://github.com/wassermanproductions/blockout)、[Runway 官方](https://help.runwayml.com/hc/en-us/articles/57074952895635)、[时光之刃](https://www.bilibili.com/video/BV1z3NJ6NEDM)（场景不重合时直接生两帧） | 中偏弱（产品都这么设计，没人给对照；动作大时关键帧会卡） |
| E | **深度 / 姿态 / 线稿控制视频**（开源） | Blender 直接渲深度通道（或骨架图、线稿），当 control video；外观给参考图或首帧 | depth / pose / canny / normal 序列 | Wan 2.1 VACE、Wan 2.2 Fun Control、VACE-Fun、LTX-2.5 IC-LoRA Union、H3-Fun-Controlnet-Union、SolarRenderer；Yedp Action Director、Blockout、Pallaidium | [VACE 官方](https://github.com/ali-vilab/VACE/blob/main/UserGuide.md)、[VideoX-Fun](https://github.com/aigc-apps/VideoX-Fun)、[LTX IC-LoRA 文档](https://docs.ltx.io/open-source-model/usage-guides/ic-lo-ra)、[Yedp](https://github.com/yedp123/ComfyUI-Yedp-Action-Director)；闭源只有 Kling 4.0 收深度图视频 | 官方文档强；2026 年社区实测少，多数人已转去 A |
| F | **v2v 转绘 / 编辑** | 把白模视频当「待编辑视频」，让模型重绘；可贴几张转写实的关键帧定外观 | 源视频 + 关键帧 + 强度设置 | Luma Ray 3.2 Modify、Runway Aleph 2.0、Wan 2.7 videoedit、Kling O1 restyle、Gemini Omni edit | [Luma 官方](https://lumalabs.ai/learning-center/articles/ray-3-2-video-to-video)（直接谈 pre-vis 和 Blocking）、[Runway 官方](https://help.runwayml.com/hc/en-us/articles/52150503729171) | 中偏弱（官方说得清楚；没找到用白模做的完整社区案例） |
| G | **只借机位** | 3D 里只做相机路径（场景可以很空），渲一段飞行视频当运镜参考；人物和动作靠首帧和文字 | 运镜参考视频 | Krea Seedance Studio、Kling O1「Reference Video for Camera Movements」、Marble Record | [Krea 文档](https://www.krea.ai/docs/user-guide/features/seedance-studio)、[Dan Kieft](https://www.youtube.com/watch?v=miIDu04N7_4)、[Kling O1 指南](https://kling.ai/quickstart/klingai-video-o1-user-guide) | 中（已做成产品功能；个人案例一两个） |
| H | **白模不喂模型，只用来算事实写提示词** | 程序摆好人和机位，算出每镜谁在画面左 / 右、谁挡谁、景别，抄进提示词；白模图只给人看 | 文字（由几何算出来的站位描述） | 任意模型；nana-whitebox、VLM-Generation-Harness 的 `project.report()` | [娜乌斯嘉AI](https://www.bilibili.com/video/BV1aTWm6jEqW)、[7ohnson](https://github.com/7ohnson/VLM-Generation-Harness) | 弱到中（一个人的对照 + 一个工具；但成本最低） |
| I | **真人 / 现成视频 → 3D 白模 → 重新运镜** | 从视频里恢复人体网格和动作，导进 Blender 换机位，渲白模再当参考视频 | 白模 mp4（动作来自真人） | SAM 3D Body + Blender + MiniMax H3；Motion Previs Studio | [有趣的80后程序员](https://www.bilibili.com/video/BV188tE6kEVL) | 弱（单人演示） |

---

## 1. 做法：每种接法的步骤

### A. 粗白模视频当参考视频

**步骤（多人一致）**

1. 把剧本拆成三堆。7ohnson 的说法最清楚：「空间事实 → 白模（能用坐标写下来的）；外观事实 → 资产图（写不成坐标、但能拍下来的）；表演事实 → prompt」（[README](https://github.com/7ohnson/VLM-Generation-Harness)）。
2. Blender 里用几何体搭场景、摆人、放相机，时间轴上排镜头和切点。现在普遍让 agent 写 bpy 脚本或走 Blender MCP（TanLuAI、DeepWhite、Dan Kieft、JSFILMZ、sorenxet 都是）。
3. 人先看一遍白模，不对就改几何。这一步不花视频积分。DeepWhite：一版场景 10–20 分钟，白模视频约半小时，全程 50 分钟到 1 小时（[视频](https://www.bilibili.com/video/BV1xBWv6qEC7)）。
4. 渲 playblast：和成片同画幅、同帧率、同长度，画面里不带任何叠加物。
5. 准备参考图（人物、场景、道具），各管各的。
6. 提示词：先声明白模的职责和映射，再写内容。
7. 成片和白模左右并排对着看。

**提示词怎么写：官方原话**

- Seedance 2.5【官方】：「文本中写明希望参考白模视频中的什么元素。示例 1：白模中没有光影变化，只希望参考运镜和运动 → 『参考 [视频 1] 的运镜、动作...』」「如果叠加输入了参考图，需写明参考图和白模的对应关系。示例：『将 [图片 1] 中穿灰色衣服的男人对应 [视频 1] 中的红色模型、[视频 2] 中的红发少女替换 [视频 1] 中的绿色模型 2』」（[提示词指南](https://www.volcengine.com/docs/82379/2607689)，我核对过原页）。
- Seedance 2.5 官方粗粒度示例（30 秒、含切镜）：「以白模参考视频 <video1> 作为整支视频唯一的运镜、镜头节奏、景别变化、主体运动轨迹和镜头调度参考……白模视频仅作为运镜、镜头运动和角色动画参考，不参考画面内容。」（同上）
- Seedance 官方提示词 skill（sd25-pe）【官方】：「粗粒度白模……每个几何体必须单独映射到最终主体或道具。」「白模视频作为生成参考，不因为它是视频就自动成为编辑母版。」模板：「@视频1是粗粒度白模参考，仅提供<动作路径、主体站位、机位、运镜、切镜……>，不采用其中的白模外观、材质和场景。」（sd25-pe 0.1.1「白模参考与渲染」；下载地址见 video-film-maker 的 `refs/practical/prompt-skills/overview.md`）。含义：白模走「参考生视频」，提示词里不要出现「编辑视频」这类词，否则会被路由成视频编辑，画幅和时长被锁死。
- Wan 3.0【官方】动作参考的写法：「参考图 1、图 2 的人物角色，仅参考视频 1 的视频动作……参考视频只用于动作控制，不继承其人物外观。最终画面正常彩色，人物稳定……」（[Prompt 指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)，我核对过原页）。它特意写了「最终画面正常彩色」。
- Kling 4.0【官方】只有一句：「Video references: Up to 5 videos, with a combined duration of up to 30 seconds. Videos can guide performance, movement, camera direction, and narrative pacing. White-model and depth-map videos are also supported.」（[官方博客 2026-09-30](https://kling.ai/blog/kling-4-ai-video-model)）

**提示词怎么写：实际在用的写法**

- ComfyUI 官方 Haunted Subway 工作流（一段 21 秒白模 + 4 张参考图 → Seedance 2.5）：「`video_1` — 21-second 3D blockout video: This is the definitive reference for all first-person POV camera movement, viewing angles, shot order, action beats, lighting blackouts, character positions, spatial continuity, reveal timing, final framing, and total duration.」「Treat the blockout as the animation foundation and this prompt as a visual and performance enhancement.」分工表里 `video_1` 不许拿的是「Its gray placeholder look」（[Comfy-Org/workflows](https://github.com/Comfy-Org/workflows)）。
- scenario skill（针对 Seedance 类）：开头把白模说成排练录像，「The reference video is rehearsal footage: stand-ins walked the scene so camera, timing and movement could be locked… Take from the video only the camera path and framing, the timing of every action, and each element's screen position, path, ground contact and scale. No shape, proportion, silhouette or surface in the video belongs in the final frame.」之后不再出现 box、cone、mannequin 这类词（[scenario-labs/skills](https://github.com/scenario-labs/skills)）。
- TanLuAI（X 长文，39 万次浏览，带完整提示词）：「视频中唯一的浅青色长方体代表女主……三个深灰色长方体代表三名男性特工。严格参考视频的摄影机运动、景别、切镜时间、人物整体位置、空间关系与弹体路径。**几何人物只表示位置和移动方向，不提供肢体动作参考。**重新生成自然的奔跑、起跳、探身张望、转身……不迁移方块滑行、僵硬姿态或机械摆动。」负面词里写「白模方块、几何人形、刚性滑行、机器人跑步、塑料皮肤」（[长文](https://x.com/TanLuAI/status/2099124935285461329)）。
- 鱼摆摆喂（B 站 26 万播放，UpDream 合作）：「视频1为白模预演参考，仅控制人物站位、摄像机位置、切镜时间和运动轨迹；图片1定义场景布局；人物参考定义角色外观；最终视频不出现白模网格和预演台界面。」并强调「既然白模已经负责了人物路线、机位和运镜，正文里就不能再重复写一套完全不同的镜头运动，否则 AI 会同时接收到两套指令」（[视频](https://www.bilibili.com/video/BV19gtc6aEQY)）【宣传 + 经验】。
- 7ohnson 的冲突规则：「位置与朝向听白模的 · 长相与光听资产图的 · 其余听 prompt 的」，并要求每张资产图都声明「只取什么、不取什么」（[prompt 规范](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/03-prompt-spec.md)）。
- 墨江鸭鸭（Kling 4.0 对 Seedance 的白模对比，简介里给了全文）：「发生冲突时，镜头运动以白模视频为准，材质以实拍为准，植物外观以 AI 图片为准。」「不要复制灰色材质、几何叶片、规则排列的枝条或空白窗外。」（[视频](https://www.bilibili.com/video/BV1cHn16EEw4)）
- GrandVisionsAI：「Use @Video1 for overall character blocking, action timing, movement paths, spatial relationships and camera motion. The knight, dragon, mountains and buildings in @Video1 are previs references for staging and scale; rebuild their appearance completely in @Image1's exact style.」（[帖子](https://x.com/GrandVisionsAI/status/2096993565599490465) 楼下自回）

**多镜头怎么做（两种，都有人用）**

- 一段白模里直接含多个镜头和切点，一次生成。ComfyUI Haunted Subway 是 21 秒多镜头加黑场；TanLuAI 22 秒 11 个分镜、20 多个人物一次生成（[帖子](https://x.com/TanLuAI/status/2099456658988830842)）；adilinthewild「six people through four cuts with zero seat swaps. Every seat was locked in Blender first. The boxes are the actors.」（[帖子](https://x.com/adilinthewild/status/2093662540119281877)）。7ohnson 量过切点：16 秒 7 镜 6 次硬切，成片切点最大偏差 0.07 秒，没有多余切点（[实测记录](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/04-model-notes.md)）【实测】。
- 同一个 3D 场景里每个机位各录一段，分别生成再剪。aiwarts：「每个机位都可以单独导出一段运镜视频，这样在一个空间内录制的不同机位，空间一致性肯定是很稳定的」（[长文](https://x.com/aiwarts/status/2089710688151191773)）【宣传 + 经验】。

**谁说了不同的话**

- 评论区的反对意见（单人）：「建白模 tokens，然后视频生视频要翻倍，特别是 Seedance 2.5，完了即便如此你以为控的住了？最后动作还是要落实到你的提示词里面……不如把提示词写扎实。」（[DeepWhite 视频](https://www.bilibili.com/video/BV1xBWv6qEC7) 评论，戈登-泽罗）
- ponyodong（单人）：「白模能动，不代表人物会演。跑步、回头、逗小妖，想要灵动，还是得有好的表演参考。先拿最难的 5 秒试，顺了再做 15 秒。」（[帖子](https://x.com/ponyodong/status/2097864677682475069)）

### B. 细白模「上色」重渲染

- Wan 3.0【官方】把它列为任务「白模参考 / 渲染｜提示词 + 白模视频｜写实化重渲染的视频」。做法：「上传纯白 clay render 白模视频作为唯一蓝本，仅将材质、颜色、纹理替换为真实世界质感，其余画面逐帧保持不动。」官方示例提示词分四段：绝对保持不变（镜头轨迹、剪辑点、物体位置、角色动作，「一帧不增删、一秒不错位」）、写实化转换（逐件写真实材质）、光影（「完全沿用白模视频的灯光方向与投影」）、禁止清单（[Prompt 指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide)）。
- Seedance 2.5【官方】细粒度：「服务于建模完整，重点解决重渲染的场景，给『白模上色』获得更好更丰富的渲染效果。」示例：「将视频 1 进行白模渲染，无 bgm，只生成环境音和动作音。渲染要求：背景为……」（[提示词指南](https://www.volcengine.com/docs/82379/2607689)）。
- 即梦官方 Clay Renderer 插件（Blender、Maya）：面板里选相机和帧范围 → Render → Upload to Dreamina，网页自动把白模视频挂成参考输入。官方界定：「It works with a clay render video rather than treating the Blender project itself as the video-generation input.」（[Dreamina 页面](https://dreamina.capcut.com/seedance/seedance-2-5-blender-model-workflow)）
- 这条路的前提是 3D 里已经有像样的模型和动画，等于「拿视频模型当渲染器」。对我们这种只想管走位和机位的用法，官方自己建议走粗粒度（见第 4 节）。

### C. 转写实的首帧 + 白模视频

- LTX-2.5 Layout-to-Render【官方模型卡】：「Give it a grey clay viewport, or a blocky playblast of simple shapes, from Blender, Unreal, or a similar 3D tool, carrying the camera move and the objects. Give it a first frame that sets the art direction. It returns a video that moves like the layout and looks like that first frame.」「Take the first frame of the clay animation and give it to any image model to generate the visual you want… Do not use the grey clay frame itself.」「A grey clay frame used as the first frame produces a grey result.」（[模型卡](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Layout-To-Render)）
- flick.art 三步（Flick 平台驻场导演写的【宣传 + 经验】）：Blender 出视频和第 1 帧 → Nano Banana 转写实，提示词「Use the provided image as the composition and pose reference. Keep composition a 100% exactly match of the provided sketch. Keep camera position 100% unchanged. Keep framing 100% unchanged.」→ Seedance 里转好的帧当 start frame、Blender 视频当 video reference，提示词只写「Reference the character's actions and camera language from @Video.」（[文章](https://flick.art/blog/blender-ai-filmmaking)）
- Polypro：「The greybox gives you the camera. The style frame gives you the look.」（[帖子](https://x.com/Polypro_io/status/2114796010476314631)，浏览量很小）
- 时光之刃（Seedance 2.0，B 站 2.3 万播放）【经验】：按白模首帧生成一张写实参考图 + 人物图 + 白模视频一起给。**首帧看不到的地方会被乱编**，他的修法是：先生成一条，从成片里把不满意的那一帧截出来，标注后局部修图，再当第二张「参考帧」传回去，「基本上这两张图就把整个摄像机所能覆盖的位置都能看得到了」。场景前后不重合时，直接按两个机位各生一张。抽卡主要落在生图上（「每次才一毛钱」），视频 2–3 次能过（[视频](https://www.bilibili.com/video/BV1z3NJ6NEDM)）。
- Luma Ray 3.2【官方】：「You can export a few frames from the source, edit them… then feed them back into Ray 3.2 at the same original source-frame indexes. Ray 3.2 uses those anchors to interpolate the look across the rest of the shot.」最多 64 张关键帧（[学习中心](https://lumalabs.ai/learning-center/articles/ray-3-2-video-to-video)）。
- Runway Aleph 2.0【官方】：「Edit one frame and Aleph 2.0 modifies the rest of your video to match.」（[Prompting Guide](https://help.runwayml.com/hc/en-us/articles/52150503729171)）官方没有白模例子，这是按功能推出来的接法。
- **反对意见**（scenario skill）：「A single restyled frame of the shot carries its own composition and shapes into the video; panels at angles the clip never uses transfer identity without a layout to copy.」它改用 2×2 风格板（四格都是片子里不会出现的角度）来传外观（[handoff.md](https://github.com/scenario-labs/skills)）。
- **接口限制**：Wan 3.0、MiniMax H3 的首帧和参考视频不能同时用（见第 2 节）。在这两家上，「转写实的那一帧」只能当普通参考图给，不保证是第一帧。

### D. 只用白模静帧

- LibTV 导演台就是这么设计的：「通过截图的方式，将角色人物、场景道具等在空间场景中的信息，转化成更具体的"参考图片"」，运镜靠「布置多个机位的方式，来手动模拟镜头的运动轨迹」（[测评](https://www.sohu.com/a/1030583709_122571656)）。
- Blockout 应用给没有参考视频的模型配的档：Veo 3.1「Use the first-frame still as the image input; describe the camera move in the prompt.」Kling 2.x「Use first-frame and last-frame stills as start/end frames」；图像模型用「机位点静帧 + 俯视走位图」当构图参考（[profiles.ts](https://github.com/wassermanproductions/blockout)）。
- Runway【官方】能直接上传 .glb，转到想要的角度截一张当参考图或首帧，「Rigged and animated models won't upload, so for a rigged character export a static .glb for each pose you need.」（[帮助中心](https://help.runwayml.com/hc/en-us/articles/57074952895635)）
- Mixar（厂商博客【宣传】）把相机路径拆成几张静帧交出去：「Camera path: Where the lens starts, ends and travels, communicated as stills from along it.」「a handful of well-spaced poses communicates a move better than nine near-identical frames. Start, one or two mid-points and end covers most of them.」（[文章](https://www.mixar.app/blog/blender-blockout-to-video)）
- 评论区有人问能不能只做静态白模出首中尾关键帧，DeepWhite 回：「动态大的用关键帧容易卡顿。对于文戏比较好。」（[评论](https://www.bilibili.com/video/BV1xBWv6qEC7)）【经验，单人】
- Seedance【官方】对宫格和关键帧的说法：「宫格图并不会严格对齐分镜内容……如需严格按照分镜图生成时，推荐使用多关键帧参考方式。」「prompt 需要在第一句写明『以图片 x 至图片 x 的顺序作为关键帧』。」

### E. 深度 / 姿态 / 线稿控制视频（开源）

- VACE【官方】：`src_video` 可以是「condition videos (Depth, Pose, etc.)」；控制类型有 `depth`、`flow`、`gray`、`pose`、`scribble`、`layout_bbox`、`layout_track`；外观用 `src_ref_images`（「Salient object segmentation can be performed to keep the background white.」）；约 5 秒 81 帧，「we recommend to generate 5s video clips one by one, while using `firstclip` video extension task to keep the temporal consistency.」（[UserGuide](https://github.com/ali-vilab/VACE/blob/main/UserGuide.md)）。Blender 可以直接渲深度通道，不用再估深度（这句是推论，官方没提 Blender）。
- Wan 2.2 Fun Control / VACE-Fun【官方】：「supporting various control conditions such as Canny, Depth, Pose, MLSD, etc., and trajectory control」；另有 Control-Camera 权重吃相机轨迹（[VideoX-Fun](https://github.com/aigc-apps/VideoX-Fun)）。
- LTX-2.5 IC-LoRA【官方】点名 Blender：「Depth Maps｜Tools: Depthcrafter；Blender/3D software - For synthetic depth renders」「Use consistent depth range across all frames」「Soft depth guidance: Set `attention_strength` to 0.6 for depth IC-LoRA to get approximate spatial structure while allowing the model more creative freedom」（[IC-LoRA 文档](https://docs.ltx.io/open-source-model/usage-guides/ic-lo-ra)）。
- 出通道的现成工具：Blockout 导出包里有 `1A_depth.mp4`、`1A_normal.mp4` 和接好线的 ComfyUI 工作流（Wan / LTX 档）；Yedp Action Director 一次烘焙 OpenPose、深度、Canny、法线、灰模、Alpha、带贴图七种；Pallaidium 在 Blender 视频编辑器里加了 Mist / Depth Pass（详见 [notes/tools_notes.md](notes/tools_notes.md) 第 3、4 节）。
- 实测对比（单人，对照）：娜乌斯嘉AI 同一段提示词下比了「方块简易白模、精细白模、深度图」三种参考，「三条成片几乎一模一样，画面长什么样全看场景图，白模只传过去了一件事：镜头怎么走、走多快」（[视频](https://www.bilibili.com/video/BV1aTWm6jEqW)；用的哪个模型字幕里没说）。TanLuAI 也提到在流程里「增加了深度视频的应用」，没给对比（[帖子](https://x.com/TanLuAI/status/2099853992289575199)）。
- 这条路 2025 年是主流，2026 年在社区里基本被 A 取代：CozyClay 的判断是「None of the top hosted APIs (Seedance, Kling, Veo 3.1, Runway Act-Two, MiniMax) documents a depth or pose control-video input.」（[指南](https://cozyclay.org/greybox-to-video/)；Kling 4.0 之后这句已不完全成立）。B 站和 X 上我没搜到 2026 年用 Blender 深度图接 VACE 做叙事短片的实操帖。

### F. v2v 转绘 / 编辑

- Luma Ray 3.2 Modify【官方】是唯一把「运镜、形状、肢体」拆成独立开关的：Motion 滑杆低档「mostly locks onto your camera move」；Structure 滑杆管形状贴合度；「Blocking is the broader pose mode (think block-out or pre-vis level) that captures only the general back-and-forth of a body rather than every limb. It's useful when your performance is a rough stand-in and you'd rather the model generate natural motion than follow your rough puppeteering exactly.」不想把人偶体型带进成片：「Turn Bodies off when you want to change the body type itself.」源视频最长 20 秒（[学习中心](https://lumalabs.ai/learning-center/articles/ray-3-2-video-to-video)）。
- Luma 发布文【官方】：「evolve low-poly footage into cinematic realism」「Whether you're working on previs, pitch decks, or final renders…」（[Introducing Modify Video](https://lumalabs.ai/news/introducing-modify-video)）
- Runway Aleph 2.0 / Edit Studio【官方】：输入 2–30 秒、480p–1080p、24–30 fps、切点不超过 10 个；先在一张关键帧上把改动做对，再铺到整段。
- Wan 2.7 videoedit、Kling O1（「Change [@Video] to the style of [@Image1]」）、Gemini Omni（上传 ≤15 秒视频对话式编辑）也能这么接，官方都没有白模例子。Scenario 的 Blender 插件把 playblast 交给「Seedance, Minimax, Runway Aleph, Gemini, Grok and other video-to-video models」（[README](https://github.com/scenario-labs/blender-plugin)）。
- 没找到有人晒「白模 → Aleph / Luma Modify」的完整短片流程。

### G. 只借机位

- Krea Seedance Studio【官方文档】：在 3D 里打相机关键帧（位置、朝向、焦距、时间、缓动），1–10 秒，「Use video renders the flythrough, adds it to the project feed, and attaches it as a video reference for your next generation.」（[文档](https://www.krea.ai/docs/user-guide/features/seedance-studio)）
- Dan Kieft（YouTube 14 万播放）的顺序是反的：先用图像模型出首帧，把首帧给 Claude + Blender MCP 让它照着搭 3D 场景和相机运动，渲出的视频在提示词开头只加一句「video one as a camera movement reference only」（[视频](https://www.youtube.com/watch?v=miIDu04N7_4) 文字稿）。
- Kling O1【官方】模板：「Take [@Image] as the start frame. Generate a new video following the camera movement of the [@video]」（[指南](https://kling.ai/quickstart/klingai-video-o1-user-guide)）。
- 一个坑（单人实测）：背景空的时候，模型分不清是镜头在绕还是人在转。「人工智能在读这个动作视频的时候，其实它是分不出来这个是镜头的运动还是人物的运动」，在提示词里明确「运动是由镜头的动作产生的」之后才对；要镜头从三个人中间穿过去，也得写明「穿过去」，否则它只在外围绕（[有趣的80后程序员](https://www.bilibili.com/video/BV188tE6kEVL)）。

### H. 白模不喂模型，只用来算事实

- 娜乌斯嘉AI 的结论：「白模最大的作用其实不是帮视频模型，而是帮写提示词的 AI……多人戏最容易错的就是我把谁在左、谁在右写反了。所以现在的做法是先让程序把人和机位摆好，算出每个镜头谁在左、谁在右、谁挡住了谁，四个人几十个机位，测过左右一次都没写错。」每镜出一张图拼成预演，配试读台词，「还能顺便听出来哪句台词在这个镜头里说不完」。只有长镜头、复杂运镜才做视频白模（[视频](https://www.bilibili.com/video/BV1aTWm6jEqW)；工具 [nana-whitebox](https://github.com/nawusijia/nana-whitebox)，MIT，README 写明它出的白模图「是给写提示词的人看的……不用挂给视频模型当参考图」）。
- 7ohnson 同样把几何算出来的东西抄进提示词：「`project.report()` 会算出每个元素在画面的归一化坐标、占幅比例、距离，直接抄进 prompt 当空间描述——比人手写可靠。」还用脚本核对分镜里写的左右、景别和白模算出来的是否一致（[铁律 6](https://github.com/7ohnson/VLM-Generation-Harness/blob/main/docs/02-ironclad-rules.md)）。
- aiwarts 的反例说明为什么文字会错：同一条提示词，纯文字直出的「拍摄方向和参考白模的拍摄方向是完全相反的，人物的位置关系也是相反的」（[长文](https://x.com/aiwarts/status/2089710688151191773)）。

### I. 真人 / 现成视频 → 3D 白模 → 重新运镜

- 有趣的80后程序员：ComfyUI 里用 SAM 3D Body 从视频恢复人体网格和逐帧动作（多人要用 SAM 3.1 分开跟踪，每个人单独导出 FBX，否则三个人叠在一起），导进 Blender 画一条相机样条线，渲白模，连同人物参考图给 MiniMax H3 参考生成（[视频](https://www.bilibili.com/video/BV188tE6kEVL)）【经验，单人】。
- 时光之刃也提到：「像一些比较简单的动作，比如人物的走位，或者是正常人能做到的一些姿势，可以真人去表演、去模拟」，做不到的动作再用 Blender（[视频](https://www.bilibili.com/video/BV1z3NJ6NEDM)）。
- LibTV 测评里的背景：《牡丹记》团队当时「只能先用真人演一遍后，再将内容喂给模型」（[测评](https://www.sohu.com/a/1030583709_122571656)）。
- Seedance 2.0【官方】自己用过反方向：续写画质劣化时「将原始视频通过 Seedance 2.0 转为白模视频，再作为续写输入素材」（[2.0 提示词指南](https://www.volcengine.com/docs/82379/2222480)）。

---

## 2. 各视频模型吃什么

完整的逐模型引语、出处编号（表里的 [W3-1] 等）和输入规格在 [notes/models_notes.md](notes/models_notes.md)。这里放矩阵和最要紧的几句。图例：有 = 官方明写；无 = 官方明写不支持或功能清单里没有；不明 = 没查到官方说法。

| 模型（文档日期） | 文生 | 首帧 | 首尾帧 | 主体参考图 | 参考视频·动作 | 参考视频·运镜 | 深度 / 姿态 / 线稿 | v2v 转绘 | 官方提到白模 / previz |
|---|---|---|---|---|---|---|---|---|---|
| **Wan 3.0**（百炼，2026-11） | 有 | 有 | 有（尾帧须配首帧） | 有，≤10 张 | 有 | 有 | 无专门接口 | 有（视频编辑、白模重渲染） | **有**：「白模参考 / 渲染」 |
| Wan 2.7（百炼） | 有 | 有 | 有 | 有，图 + 视频 ≤5，**可叠首帧** | 有 | 有 | 无 | 有 | 无 |
| Wan 2.1 VACE（开源） | 有 | 有 | 有 | 有 | 有（pose） | 间接（depth / flow） | **有**：depth、pose、gray、scribble、flow、layout | 有 | 无 |
| Wan 2.2 Fun Control / VACE-Fun（开源） | 有 | 有 | 有 | 有 | 有（pose） | 有（Control-Camera） | **有**：Canny、Depth、Pose、MLSD、轨迹 | 有 | 无 |
| Wan 2.2 Animate | — | — | — | 一张角色图 | 有 | 替换模式沿用原视频 | 内部用骨骼 + 脸 | 替换人物 | 无 |
| **Seedance 2.5**（方舟，2026-11-16） | 有 | 有 | 有 | 有，≤30 张 | 有 | 有 | 无专门接口 | 有（视频编辑、白模上色） | **有**：「白模参考/渲染」，分粗 / 细 |
| Seedance 2.0 | 有 | 有 | 有 | 有，≤9 张 | 有 | 有 | 无 | 有 | 间接 |
| **Kling 4.0**（2026-10） | 有 | 有 | 有，≤10 个关键帧 | 有，≤7 个主体 | 有 | 有 | **有：深度图视频、白模视频**；姿态不明 | 有 | **有**：一句话 |
| Kling O1 / 3.0 Omni | 有 | 有 | 有 | 有 | 有 | 有 | 不明 | 有 | 无 |
| Kling Motion Control | — | 人物图 | — | — | 有，3–30 秒，单人单镜头 | 有（Matches Video 档） | — | — | 「certain stylized humanoid… can be recognized」 |
| Veo 3.1 | 有 | 有 | 有 | 有，≤3 张且只能 8 秒 | 无 | 无 | 无 | 无 | 无 |
| Gemini Omni Flash 1.2 | 有 | 有 | 有 | 有，≤6 张 | 无（参考视频是保外观用的） | 无 | 无 | 有，≤15 秒 | 无 |
| Runway Gen-4.5 | 有 | 有 | 无 | 无 | 无 | 无 | 无 | 无 | .glb 截图可当首帧 |
| Runway Aleph 2.0 | — | — | 改一帧带全段 | 参考图 | 沿用源视频 | 沿用源视频 | 无 | **有**，2–30 秒 | 无 |
| **Luma Ray 3.2 Modify** | 无 | — | 关键帧 ≤64 | 走关键帧 | 有 | 有 | **有**：Motion / Structure 滑杆，Poses / Blocking 开关 | **有**，≤20 秒 | **有**：占位物、3D 物体、pre-vis 级 Blocking |
| MiniMax H3（Hailuo 3.0） | 有 | 有 | 有 | 有，≤9 张 | 有 | 有 | 官方接口无；开源有 Fun-Controlnet-Union | 有 | 无 |
| Hailuo 02 / 2.3 | 有 | 有 | 有（仅 02） | 单张人脸 | 无 | 无 | 无 | 无 | 无（有 15 种 `[指令]` 运镜） |
| Higgsfield | 取决于底层模型 | 同左 | Cinema Studio 有 | 同左 | 同左 | 同左 | 无 | 同左 | Blender 插件、3D Jutsu |
| LTX-2.5（开源） | 有 | 有 | 不明 | 不明 | 有（pose） | 间接（depth） | **有**：depth、canny、pose、稀疏轨迹 | 有 | **有**：Layout-to-Render；深度来源列了 Blender |
| Moonvalley Marey | 不明 | 不明 | 不明 | 不明 | 有 | 有 | 不明 | 不明 | 无 |
| Vidu Q2–Q4 | 有 | 有 | 有 | 有，≤7 张 | 不明 | 不明 | 无 | 不明 | 无 |
| HappyHorse 1.1 | 有 | 有 | 无 | 有 | 无 | 无 | 无 | 1.0-video-edit | 无 |
| Sora 2 | 2026-09-24 已停【转述】 | | | | | | | | |

**最要紧的官方原话**

- Wan 3.0 互斥：「reference_xx/file/link 类型和 first_frame/last_frame 类型互斥，不能在同一请求中混用。」参考视频上限：「reference_video：参考视频。最多5段，总时长不大于15秒。」「帧率：≥16 fps」「有视频输入时，输入+输出总时长≤30秒。」（[API 参考](https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference)、[使用指南](https://help.aliyun.com/zh/model-studio/wan3-video-generation-guide)）
- Wan 3.0 同一段参考视频当「主体」还是当「运动」由提示词定：「把参考视频的动作、运镜、特效当成时序信号迁移到新角色或新场景，节奏照搬，主体、环境自由换。」
- Wan 2.7 的参考生视频可以叠首帧（3.0 不行）：「多主体参考+首帧控制……在主体参考基础上加入首帧控制，让画面构图和内容走向更加可控。」（[参考生视频](https://help.aliyun.com/zh/model-studio/video-to-video-guide)）
- Seedance 2.5 输入视频：「非视频编辑任务：单个视频时长 [2, 30] s……总时长不超过 30 s」「帧率（FPS）：[24, 60]」，最多 10 个；「不支持直接上传含有真人人脸的参考图/视频」（[教程](https://www.volcengine.com/docs/82379/2607688)）。
- Seedance「只借动作、不继承外观」【官方 skill】：「生成任务不得默认继承参考视频中的人物身份、服装或完整场景。」「@视频1用于<动作、运镜或节奏>，不采用<容易误带的身份、服装或场景>。」
- Seedance 首帧 + 参考：`first_frame` 是单独的任务；官方绕法是「全模态生视频可通过提示词指定参考图片作为首帧/尾帧……若需严格保障首尾帧和指定图片一致，优先使用图生视频-首尾帧」。
- MiniMax H3 互斥：「图生视频与多模态参考生视频互斥：content 中出现 `reference_image` / `reference_video` / `reference_audio` 任一 role，就不能再出现 `first_frame` / `last_frame`」（[接口文档](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create)）。
- Kling Motion Control 对动作视频：「Real human actions are recommended, while certain stylized humanoid or humanoid body proportions can be recognized.」「For motion reference with two or more characters, the motion of the character occupying the largest portion of the frame will be used」「Please avoid cuts, shot changes, or camera movements」（[指南](https://kling.ai/quickstart/motion-control-user-guide)）。它一次只驱动一个人，不适合多人走位。
- Gemini Omni 的参考视频不是动作参考：「Reference videos work best for visual likenesses」（[文档](https://ai.google.dev/gemini-api/docs/omni)）。Veo 3.1 在 Flow 的支持表里明写「Unsupported: Video to Video editing」。所以 Google 这边白模只能走首帧 / 首尾帧。
- Runway 对 3D 截图：「The rendered view carries the object's shape, proportions and angle, not its lighting. Describe the lighting in your prompt or add a style reference so the result doesn't look like a plain render.」
- Luma 对占位物：「If you drop a placeholder object into a scene… give it shading or a gradient — a flat, single-color blob gives weaker motion control than a shaded one. 3D objects work naturally here, because their lighting creates gradients on its own (even rough lighting helps).」

**首帧和参考视频能不能同时用**

| 能 | 不能 |
|---|---|
| Wan 2.7 参考生视频（首帧 + 参考图 / 视频 ≤5）；Kling O1 / 3.0 Omni / 4.0（@Image 当首帧，再 @Video 借运镜）；Seedance 2.x（提示词里写「@图片N作为首帧。」，不保证严格一致）；Luma Ray 3.2（关键帧贴在源视频帧号上）；LTX Layout-to-Render（首帧 + 布局视频是标准用法） | Wan 3.0；MiniMax H3（官方接口和 Runway 平台上都不行） |

Scenario 插件文档的说法更宽：「Some models (Seedance 2.5, 2.0 Fast and 2.0 Mini, Minimax H3 and Wan 3.0) can't take a first frame together with the clip; for them, the image guides the opening look instead」（[用户指南](https://blender.scenario.com/)）。Seedance 这一条和官方「提示词指定首帧」的绕法并不矛盾：接口上确实不能同传。

**渲白模时照这个规格出**

| 模型 | 参考视频时长 | 帧率 | 分辨率 / 大小 | 其他 |
|---|---|---|---|---|
| Wan 3.0 | 单个 1–15 秒，合计 ≤15 秒，≤5 段；输入 + 输出 ≤30 秒 | ≥16 fps | 单边 240–4096，≤100 MB | mp4 / mov |
| Seedance 2.5 | 单个 2–30 秒，合计 ≤30 秒，≤10 个 | 24–60 fps | 480p–4K，≤200 MB | 不能有真人脸 |
| Kling 4.0 | ≤5 段，合计 ≤30 秒 | 不明 | 不明 | |
| MiniMax H3 | 单段 2–15 秒，合计 ≤15 秒，≤3 段 | 不明 | 边长 256–5760，≤50 MB | 开源版帧数走 17k+5 的格子 |
| Luma Ray 3.2 | ≤20 秒，输出等长 | 24 fps 才能到上限【转述】 | 不明 | 关键帧 ≤64 |
| Runway Aleph 2.0 | 2–30 秒 | 24–30 fps | 480p–1080p | ≤10 个切点 |
| VACE | 约 5 秒（81 帧） | 16 fps | 480p / 720p | 灰 127 = 待生成区域 |
| LTX-2.5 | 帧数 8k+1 | 24–25 fps | 宽高被 64 整除 | |

**把白模图转写实的图像模型**（官方对「保持构图」的说法，详见 notes 第 10 节）

- Qwen-Image-Edit 2509 / 2511 是唯一官方明写原生吃深度图的：「Native Support for ControlNet: Including depth maps, edge maps, keypoint maps, and more.」（[模型卡](https://modelscope.cn/models/Qwen/Qwen-Image-Edit-2509)）
- Nano Banana 有「草图变成品」模板：「Turn this rough [medium] sketch of a [subject] into a [style description] photo. Keep the [specific features] from the sketch but add [new details/materials].」（[文档](https://ai.google.dev/gemini-api/docs/image-generation)）
- gpt-image：「For edits, say "change only X" and list the details to preserve, such as identity, geometry, layout, lighting, or labels.」
- FLUX 3 Image 有框选布局（每个框写里面是什么）。Seedream 5.5 没提线稿、深度或白模。

**和 video-film-maker 的笔记对不上的一处**：video-film-maker 的 `refs/practical/models.md` 写 Seedance 2.5 没有参考视频。火山方舟官方文档写有（最多 10 个、合计 ≤30 秒）。video-film-maker 记的应是经第三方网关的情况，不是模型本身。

---

## 3. 翻车点和对策

每行：现象 → 谁遇到 / 谁说的 → 给出过的办法。多人一致的标「多人」，只有一个来源的标「单人」。

### 3.1 白模的样子被带进成片

| 现象 | 来源 | 对策 |
|---|---|---|
| 灰模材质、方块、胶囊出现在成片里 | 多人。Wan 3.0 官方负向清单直接点名：「禁止出现残留的白模区域、局部未上色的纯白物体、材质丢失的灰模块……塑料玩具与 CG 假质感」；7ohnson：「白模里当占位用的两个深色方块，成片里变成了两个方盒子摆件」 | ① 提示词声明不采用白模外观（Seedance 模板「不采用其中的白模外观、材质和场景」；ComfyUI 分工表「Its gray placeholder look」）；② 负面词点名（TanLuAI「白模方块、几何人形、刚性滑行、机器人跑步、塑料皮肤」；scenario「No blocky placeholder geometry, no mannequin figures, no untextured surfaces.」）；③ 小道具不给造型，只当位置标记（7ohnson 铁律 3）；④ 负面里写具体的反面：「禁止把家具做成方盒子：柜台要有真实的石材体量与边缘倒角」（7ohnson） |
| 提示词里说了替身的形状，反而被原样渲出来 | 单人（scenario，针对 Seedance）：「A prompt that names the proxies' shapes… anchors the model on those shapes and it renders them as they are.」LTX 模型卡同向：「Do not write "clay," "3D," or "Unreal."」 | Seedance 类：开头说一次「排练录像」，之后不提几何词。**相反做法也有人用且没翻车**：TanLuAI、ai-muninn、Blockout 都在提示词里直接写「浅青色长方体」「RED TALL CAPSULE」「grey figures」。看起来 H3 类必须说，Seedance 上两种都有人成功，没人对比过 |
| 白模的光被抄走：平光成片也是平光，「死白的窗、发暗的天花」 | 单人实测（7ohnson） | 提示词里写死「白模是无方向的平光，那只是图纸，光完全按【光】这一段和空镜来」；Runway 官方同向：「Describe the lighting in your prompt or add a style reference so the result doesn't look like a plain render.」反过来，想让模型照白模的光就明说（Seedance 官方示例 2「参考 [视频 1] 的光影变化」；Wan 3.0 细白模示例「完全沿用白模视频的灯光方向与投影」） |
| 叠加物漏进画面：轨迹线、坐标轴、相机视锥、选中框、文字牌、描边、烧在角上的镜号 | 多人。Seedance 官方：「不含【轨迹线】【坐标线】【相机 cone】等干扰信息的视频，否则容易泄露到生成后的视频中」；CozyClay：「A blue selection box on the ground plane can come back as a blue crate.」；7ohnson：「烧字是里面最糟的一个」 | 给模型的那一版什么都不叠。要给人看的标注，另渲一版（7ohnson 的「审片版 / 送模版」；Blockout 的标签「often you want them burned into reference stills but not the motion video」）；htc911 的工具默认隐藏轮廓线，「这样视频模型只会学习运镜和布局，不会学到线稿的画风」 |
| 白模里有带贴图的成品模型，它的造型被抄进成片 | 单人（7ohnson）：「灰模里出现一个 PBR 沙发，送模版就会把那个沙发的造型抄进成片」；CozyClay 同向：「A textured render or a photo… The model tries to keep the wood grain and the shirt too」 | 资产统一换成无贴图灰材质；关掉 Blender MCP 里自动拉 Poly Haven、Sketchfab 成品模型的功能 |
| 颜色被读成衣服颜色或材质 | 两个来源。scenario（H3 Max 实测）：「The model reads a hue as a material hint」；7ohnson：橙色人形「它完全可能理解成这人穿橙色」；htc911 的工具为此留了「统一浅灰」选项 | 见 4.3 颜色之争 |
| 参考图上的品牌字、图案漏进成片 | 单人实测（7ohnson）：纸袋上的字母压印「被当成了这个品牌的墙面纹理」 | 「禁令无效，要靠物理回避」：把那块从参考图里裁掉；屏幕在白模里转开 25 度 |

### 3.2 人偶的动作和比例被带进成片

| 现象 | 来源 | 对策 |
|---|---|---|
| 人偶做了迈腿 / 程序化走路，成片里的人走得僵、滑步、齐步 | 多人，含对照。scenario Sky Islands 实验：Seedance 2.5 上 13 部件关节人偶「came back upright with short walk-like strides even with a running clause in the prompt, while capsules came back running」；娜乌斯嘉AI：「给小人做了迈腿的动画，结果成片里的人走路特别僵硬，把腿的动画去掉，只让它平移，成片里的人反而走得自然了」；DeepWhite：「人物模型很精致……人物位置关系是对的，但是动作非常的机械」；Seedance 官方：「避免包含【四肢/翅膀】等涉及精细运动的元素；如已包含，需补全其动作序列，以防止渲染结果出现四肢僵化」；ComfyUI 官方短片：「If your blockout includes some movement but it's still fairly stiff or limited, the AI may preserve that stiffness」 | 去掉四肢，只平移；或给完整的真动画（动捕、动作库）。提示词补一句：TanLuAI「几何人物只表示位置和移动方向，不提供肢体动作参考」；scenario 步态句「each foot planted before the other lifts… Their feet never slide, glide or float.」；Luma 用 Blocking 档代替 Poses |
| 走得太快、起停太突然，成片里的人「瞬移」 | 单人对照（娜乌斯嘉AI）：「走的僵不僵，跟人偶长什么样关系不大，关键是白模里的人走得太快了，起步跟停下都太突然了」「白模不对的地方，模型就照着学」 | 按真人速度走，起步和停下加缓动；镜头也加缓入缓出（DeepWhite 让 agent「在镜头中增加一个缓入缓出……最后也要一个合理的镜头停顿，让每个人物都能看清楚」）。TanLuAI 的另一个办法：「运镜节奏过快不用理，可以等渲染完成以后再进行变速处理（前提该段没有台词的声音）」 |
| 站着不动被整体平移，模型读不出「在走」 | 单人（7ohnson 铁律 11）：「站着不动被平移过去在白模里一眼假，模型也读不出她在走」 | 他用迈步姿势的静态假人平移。**和上两行矛盾**，见 4.1 |
| 白模能走位，但人物不会「演」 | 单人（ponyodong）：「白模能动，不代表人物会演」 | 表演写进提示词，或另给表演参考；先拿最难的 5 秒试 |
| 人偶的体型、比例被照搬 | 官方（Wan 3.0）：「原白模的卡通圆润造型在写实化后保留其体块轮廓与比例」；Kling Motion Control：「ensuring the proportions match those in the video for optimal results」；ai-muninn 实测身高差被保住但缩小了 | 用真实比例的人偶和真实尺寸的场景（CozyClay：「Scale matters more than detail: doors at 2 m, a car at 4.5 m long.」）；Luma 可以关 Bodies；别用 Q 版比例的资产（见 assets.md） |
| 精确数值被「软化」：两人都往画面中间靠，身高差缩小，原地小转身没跟 | 单人实测（ai-muninn，H3 本地版） | 没有给出办法；他的结论是全景管走位、近一点的景别管脸 |

### 3.3 机位、空间、时间

| 现象 | 来源 | 对策 |
|---|---|---|
| 分不清是镜头在动还是人在动 | 单人实测（有趣的80后程序员，H3） | 提示词明确「运动由镜头产生」；我的补充：场景里放地面和不对称地标（ai-muninn 规则「At least one asymmetric landmark in the scene」），空墙加等距竖肋当刻度尺（7ohnson 铁律 12：「这不是装饰，是刻度尺」） |
| 镜头要穿过人群或物体，成片只在外围绕 | 单人实测（同上） | 提示词逐段写穿过的路径和前景经过的东西 |
| 提示词又写了一套运镜，和白模打架 | 两个来源（鱼摆摆喂；CozyClay「提示词里不要再用文字描述一遍机位」）【经验】 | 运镜只在白模里出现一次，提示词只声明继承范围 |
| 长片段后半段漂：丢人、自己编特写 | 实测（scenario）：「in one audit of 28 renders, 10 to 15 s clips kept the camera and layout, 20 to 30 s clips drifted (lost figures, invented close-ups). Several short captures beat one long one.」 | 10–15 秒一段 |
| 长镜头里模型自己加切点 | 实测（7ohnson）：一条 28 秒、含 7.5 秒长镜的片子「漏 3 个切点、自己加了 4 个」；「某一镜超过 6 秒 → 模型自己在中间加了一刀」 | 拆短，或在硬约束里点名不许切。Gemini Omni 官方也说它默认多镜头，要写「In a single continuous shot / No scene cuts」 |
| 白模和输出长度不一致，结尾没东西可跟或整条错位 | 多人。ComfyUI 排错表：「The timing drifts from the blockout｜Check that Duration equals the blockout's length.」；ai-muninn：「A 120-frame blockout became 107 usable frames, so the last frames of the shot had no blocking to follow.」；7ohnson：「`--dur` 和白模时长不一致 → 整条时间轴都会错位」 | 白模帧数、帧率和输出严格一致，按模型的帧数格子渲；切片按镜头边界自动取，不手填 |
| 参考图和白模场景对不上，场景错乱 | 单人（DeepWhite 的失败案例）：先有参考图再建模，「既要满足白模视频的构图要求，又要满足参考图的要求……就会导致场景的错乱」「一定要让你的参考图和你的场景模型保持一致」 | 场景图和白模出自同一个布局：要么照场景图建白模（UpDream、htc911 的工具能从一张图估出白模），要么从白模机位出场景图 |
| 参考视频里的场景顶掉了参考图里的场景 | 单人实测（302.AI，Wan 3.0，参考视频是实拍不是白模）：「Wan3.0 仅第一层画面贴合了参考图的房屋布局，第二层画面出现明显 bug，骤变为参考视频中的房间」（[评测](https://302.ai/blog/302-ai-benchmark-lab-review-on-wan-3-0-video/)） | 没给办法。对白模的含义：白模背景本来是空的，这个风险小，但提示词仍要写「场景按图 N」 |
| 首帧看不到的区域被乱编（镜头转过去多一扇窗、结构变了） | 单人（时光之刃） | 从成片里截出不对的那一帧，修好当第二张参考帧；或给一张反打方向的场景图（TanLuAI：多给一张「反打镜头的场景图，更好的限制视频的场景一致性」） |
| 相机被墙挡住、主体出画、头被挡 | 多人（B 站[「GPT-6 操作 Blender 白模预演」](https://www.bilibili.com/video/BV1x7Yx6YEM6)：「第三个机位被墙体挡住，调整相机位置和焦距，主体才重新进入画面」；scenario 检查项；7ohnson 铁律 2、5） | 渲之前程序检查：主体占幅、遮挡（按三维垂距、横竖分开量）、穿模、脚着地；每镜首、中、末帧出图给人看；俯视平面图带机位视锥（7ohnson 铁律 13） |
| 全景里脸只有几十像素，糊 | 单人实测（ai-muninn） | 「wide shots for blocking, medium shots for faces」，脸要紧的镜头另搭近一点的白模 |

### 3.4 多人

| 现象 | 来源 | 对策 |
|---|---|---|
| 身份互换、座位互换 | 多人都在防。Wan 3.0 官方示例：「两人各自的外观锁定各自的参考图，不要混淆、不要互换服装发色」 | ① 每个几何体单独映射到角色（Seedance 官方 skill）；② 颜色或特征指认（见 4.3）；③ 在白模里锁死座位：adilinthewild 六人四次切镜没有换座，ai-muninn 两人中途换位也照做 |
| 相似的角色里，最高的那个抢了领头位置 | 单人对照（scenario，Seedance 2.5，纯胶囊档） | 给每个胶囊加两三个标志性特征（护目镜、兜帽、手里的东西） |
| 人偶太小，模型认不出谁是谁，画面里多出不一样的人 | 单人（DeepWhite）：「白模人偶太小了，导致视频模型没有准确识别到每一个人的位置关系，所以……出现了多个不一样的人物」。搜索摘要里另有「主体占画面高度一成、位移半个身高」的下限【转述，原仓库打不开】 | 人偶在画面里要够大；人多的全景拆镜 |
| 松散的小方块靠近人物被读成多出来的人 | 单人（scenario）：「loose limb blocks as extra people」 | 人偶旁边不放零碎小块 |
| 两个东西交叉经过时动作丢失 | 官方（Luma）：「Overlapping movement drops out.」 | 没给办法；避免让两人在画面里交叉时做关键动作 |
| 多张不同真人脸的参考图放一条提示词，脸混在一起 | 单人实测（7ohnson，Seedance 2.5） | 「多人镜头要么只挂一张脸 + 文字描述其他人，要么拆条」 |
| 写提示词时把左右写反、正反打越轴 | 单人（娜乌斯嘉AI） | 左右由程序从几何算出来；相邻镜头自动查越轴 |

### 3.5 手和道具

| 现象 | 来源 | 对策 |
|---|---|---|
| 道具坐标硬填，手和道具隔着几十厘米「对空气划手机」 | 单人实测（7ohnson 铁律 7） | 建完人体后读手的世界坐标再放道具，姿势一改自动对上 |
| 道具特写镜头里只有道具没有手，成片是「灰底上一个红方块」 | 单人实测（7ohnson） | 「插镜里必须有手」，把角色的手摆到道具上 |
| 道具提前动了、换手了 | 单人实测（7ohnson） | 时序约束放进硬约束前三条并写触发条件（「只有在支付提示音响过之后……这个移动全片只发生一次」）；白模里道具在那一镜之前固定不动 |
| 够不着、手部接触不对 | CozyClay 把「collisions, foot slide, reach and hand contact」做成导出前的自动检查 | 导出前查；7ohnson：手够不到桌面时「不是改姿势，是把椅面抬高」 |
| 另一头的做法：人偶干脆不要手 | Higgsfield 3D Jutsu 官方示例：「The character has NO arms and NO hands」；ai-muninn：「No fingers, no props.」；TanLuAI 的对话案例里几何人物「只用于控制位置、朝向和手部目标」 | 接触交给提示词写（搜索摘要里有人主张写「发力来源、接触点、物体反馈和收尾状态」【转述】） |

手和道具这一项**没有共识也没有对照**：一派在白模里把手摆到位，一派不要手、靠文字。

### 3.6 流程和成本

- 输入审核：「A bare gray mannequin playblast was refused by a provider's input screen, and re-encoding did not help; saturated identity colors, or a strong color tint over the whole clip, passed.」（scenario，单人）Seedance 2.5 官方不收真人脸的图和视频，白模本身不触发。
- 参考视频通道更贵：DeepWhite「将白模视频当做参考去生成视频的时候，它本身的成本就要涨 20%」；7ohnson 量的是 28.2 对 26 积分每秒（约贵 8%，2026-08 的数）。两个数对不上，平台和时间不同。
- 搭白模的时间：DeepWhite 50 分钟到 1 小时；TanLuAI「每生成一段 20 秒的建模视频，消耗的额度仅在 10% 左右」（Codex 每 5 小时额度）；Dan Kieft 5–10 分钟一个场景。
- 抽卡次数的一个旁证：时光之刃说，他看到的那条「极简场景出高质量视频」的原作者「抽了 16 次，得到两条」，提示词没公开（[视频](https://www.bilibili.com/video/BV1z3NJ6NEDM)）。
- 用视觉模型比「转风格帧」和「白模帧」时要说明两者本来就该不同，否则它把成功判成失败（scenario）。
- 参考图不要用成片抽帧：「模型输出本身偏软……把它喂回去当参考，模型会把这套渲染指纹当成目标质感」（7ohnson，单人）。

---

## 4. 白模该做成什么样

### 4.1 人偶要多细

**有同条件对照的四个来源**

| 来源 | 比了什么 | 结果 | 局限 |
|---|---|---|---|
| scenario skill「Sky Islands」（2026-10，[cast.md](https://github.com/scenario-labs/skills)） | 同一场景（五个孩子跑过索桥，4 镜 12 秒）用胶囊、带特征胶囊、13 部件关节人偶各搭一遍，三个模型各跑 | Seedance 2.5：关节人偶回来是直挺挺的小碎步，胶囊和带特征胶囊真的在跑；带特征的还保住了五个人的身份和先后顺序。H3 Max、LTX 2.3：三种差别不大 | 原文注明「One take per cell: an indication, not a measurement」 |
| GrandVisionsAI（X，326 赞，[帖子](https://x.com/GrandVisionsAI/status/2096993565599490465)） | 同一提示词，极简白模对「更多细节 + 动画」 | 「barebones won. The more detail you put into the previs, the more literally Seedance follows it.」 | 只看到成片对比视频的文字说明，没看到跑了几次 |
| 娜乌斯嘉AI（B 站，[视频](https://www.bilibili.com/video/BV1aTWm6jEqW)） | ① 方块白模、精细白模、深度图；② 迈腿动画对只平移；③ 十字小人、圆柱、保龄球、蛋形、胶囊 | ① 三条成片几乎一样；精细的只多一个好处：场景图里拍不到的东西（门口一盆绿植）只有它放对了边。② 去掉腿反而自然。③ 形状关系不大，速度和缓动才是关键 | 花了 6000 多积分，每组跑了几次没说；模型没说 |
| ComfyUI 官方短片（[YouTube](https://www.youtube.com/watch?v=2BCnIRyVWIk)） | 不是实验，是官方经验总结 | 两条正路：极简形状（动作靠提示词和参考图）或做足的细动画；「What you generally want to avoid is something in between.」 | 没给数据 |

**官方说法**

- Seedance 2.5【官方】：「简单建模（粗粒度）参考效果较好，建议仅用简单几何体拼接表示人物/物体/动物等」「白模视频主体建议仅保留躯体」。
- Wan 3.0【官方】的示例走另一头：带完整人物动作的细白模逐帧上色，要求「角色的骨相轮廓、发型体块、身材比例、服装剪裁与全部动作、走路节奏、蹲下伸手与推门的时机，必须与白模视频完全一致」。Wan 3.0 官方没有谈粗白模当动作参考该多细。
- Luma【官方】：粗的替身用 Blocking，要逐肢体跟随用 Poses。

**实际在用的人偶**

| 谁 | 人偶 | 模型 |
|---|---|---|
| DeepWhite | 「一个圆球加一个圆柱体」 | Seedance 2.5 |
| TanLuAI | 长方体；小贴士「使用立方体挪动代替有肢体的建模」 | Seedance 2.5 |
| 娜乌斯嘉AI | 「大胶囊，正面贴一块白色面罩，白色朝向哪边，脸就朝向哪边」 | 未说明 |
| ai-muninn | 高胶囊（2.4 m）和矮方块（1.6 m），「No fingers, no props」 | MiniMax H3 本地 |
| scenario skill | 默认带两三个特征的彩色胶囊；远处和群演用纯胶囊 | Seedance 2.5 |
| Higgsfield 3D Jutsu 官方示例 | 灰色替身，故意没有手臂 | Seedance 2.5 |
| 鱼摆摆喂 | 「人物走动的话，最好改成简单的圆柱体」 | Seedance 2.5 |
| GeekCatX | 「方块、圆柱 + 一个 Mixamo 人偶」（[@GeekCatX](https://x.com/GeekCatX) 2026-09-08，帖子链接没取到） | Seedance 2.5 |
| Blockout 应用 | 带关节的胶囊假人 + 算出来的步态 | 多家 |
| 7ohnson | Rigify 骨架上摆胶囊的假人，有鼻锥和肩板，摆静态姿势 | Seedance 2.5 |

**矛盾**

- 7ohnson（单人实测）反对裸圆柱：「圆柱堆起来认不出是人，更看不出面朝哪——实测模型直接让人物转脸对镜头，人物关系全错。」他要求「人体代理必须有朝向和四肢」，并认为不迈步的平移「模型也读不出她在走」。其余来源（官方 + 两个对照 + 多个个人）都说别带四肢。
- 能对上的部分：两边都同意**朝向必须看得出来**。娜乌斯嘉的面罩、scenario 的特征和「a nose block and a hair cap」、7ohnson 的鼻锥肩板，解决的是同一件事。分歧只在要不要四肢。
- 7ohnson 的假人是摆好姿势的静态假人，不带逐帧的腿部动画，和 scenario 实验里翻车的「程序化迈步」不是同一种东西。静态带姿势的假人对比无肢体胶囊，没人做过。

**什么时候才上带骨骼的假人**（scenario，单人）：「A `mannequin` is the choice when the limb motion itself must come from the blockout (a dance, a fight beat, a specific gesture) and the model copies limbs well. Give it real animation then: a rigged mannequin walked by procedural keys is still a procedural walk.」

### 4.2 朝向标记

- 人：胶囊正面贴白色面罩（娜乌斯嘉）；鼻子块 + 头发帽（scenario `detailed` 档）；鼻锥 + 肩板（7ohnson）。
- 车：车头浅色灯块和格栅、车尾暗红；没标的车会倒着开（scenario：「an unmarked car driving backward」）。
- 单个方块：「red front face, black back, green sides and top」（scenario）。
- 椅子：按「坐的人面朝哪」来放靠背（7ohnson）。

### 4.3 要不要上颜色区分角色（各家相反，没有对照）

| 主张 | 谁 | 原话 |
|---|---|---|
| 上色，提示词按颜色指认 | Seedance 官方示例；scenario；TanLuAI；DeepWhite；htc911；鱼摆摆喂；ComfyBlockout；BudgetPixel | 官方：「[视频 1] 中的红色模型……绿色模型 2」；scenario：「An all-gray playblast has lost identity.」；DeepWhite：「要求在素材中说明每一个人物所对应在白模视频中的人偶的颜色」；htc911：「多人戏里建议每个角色用不同的颜色，之后写提示词时就能用红色人物、白色人物来指代」 |
| 上色，但颜色是给人看的 | ai-muninn | 「The red and blue are for you, not the model. The model learns who is who from the prompt」 |
| 给模型的那版不上色 | 7ohnson；CozyClay；LTX 模型卡的例子；Wan 3.0 官方示例（纯白 clay） | 7ohnson：「语义配色对人有意义，是因为我们知道图例；模型手上没有图例」；CozyClay：「Keep the figure grey so it invents the person instead of preserving a mannequin.」 |

补充事实：

- 7ohnson 自己注明「『灰的更好』这一半是推理，不是 A/B 实测。实测过的只有『灰的这条能用』」。他的提示词模板里又写着「白模里橙色的人形是主角，蓝色的人形是配角」，和 README 说的「送模版无颜色」对不上。
- scenario 的折中（单人实测）：颜色要落在角色真穿的东西上，「a hero's color only to something the hero really wears」；只当标记用的颜色「came back as a bare capsule」；黑、白、灰、棕不当身份色；场景不用鲜艳原色（「they read as toys and leak」）。
- 搜索摘要里另有「人偶用中性灰、饱和度压到 0.3 以内」的说法【转述，原仓库打不开，没核对】。
- Luma 官方：Structure「does not notice color at all」，Motion 看的是明暗梯度。
- 全灰假人的 playblast 被某家输入审核拒过，上了饱和色才过（scenario）。

### 4.4 场景要多细

多人一致：**细节可以糙，体积、遮挡、尺度要准**。

- 娜乌斯嘉：「细节可以粗糙，体积和遮挡要准。场景里到底有什么、多大、谁挡住了谁，这些对了就够了。」
- Blockout：「The fidelity target is unambiguous, not beautiful.」
- scenario：「Ambiguity ruins the pass; crudeness does not: a bent lamppost comes back as a snake.」
- CozyClay：「Scale matters more than detail」；Mixar：门的高度错了成片就「reads as wrong… in a way nobody can name」。
- Mixar：要有地面和地平线，「Objects floating in a void generate as objects floating in a void.」
- 7ohnson：要看穿的地方必须是真的洞（Workbench 没有透明，玻璃就是一堵墙）；空墙加等距竖肋；小道具不给造型；「渲出来是一片平灰的时候，先怀疑几何把主体吃了，再怀疑机位」。
- ai-muninn：至少一个不对称的地标。
- htc911 的工具推荐的「引导视频」风格：「规则的物体概括成盒体、棱柱和圆柱，不规则的物体切成剪影景片」。
- 精细场景的唯一实测好处：场景参考图拍不到的东西，只有精细白模能把它放对位置（娜乌斯嘉）。

### 4.5 渲染成什么风格

- **平涂 clay、无描边、无文字、无 gizmo**：多人一致（Seedance 官方、CozyClay、7ohnson、htc911）。
- **带不带明暗**：有分歧。7ohnson 主张无方向平光（明暗会被抄走），层次靠材质明度差，给了一组阶梯：`SCRN 0.88 > WALL 0.74 > RELIEF 0.66 > WOOD 0.60 > DARK 0.52 > FLOOR 0.44 > EXTRA 0.36 > PROP 0.26 > BODY 0.18`，并提醒两个明度相同的东西在灰模里会糊成一片。Luma 官方相反：占位物要有明暗梯度，平涂单色块控制力弱。Blockout：「Generators read lighting direction and time-of-day from the reference. Keep it simple but explicit」，只给几个预设加一个主光方向。scenario：场景灰度 0.32–0.55，一盏灯，暗背景。
- **灰模、深度图、线稿哪个更听话**：只有娜乌斯嘉比过方块、精细、深度图，结果几乎一样。没找到线稿对灰模的对比。htc911 的工具能出「经典白模、纯白线稿、深色蓝图」三种样式，没说哪种效果好。Seedance 官方对宫格分镜推荐「火柴人/线稿」，那是静态分镜图，不是参考视频。
- **两份渲染**（7ohnson，单人）：同一份几何渲两遍，审片版（描边 + 语义配色 + 镜号）给人，送模版（平光灰）给模型；几何一致所以在审片版上确认位置有效，但明度不一致，要另看一眼送模版。

### 4.6 规格

- 和成片同画幅、同帧率、同长度；Seedance 要 ≥24 fps，Wan 3.0 ≥16 fps。
- 分辨率：htc911「建议长边 1280，也就是 720P」；Scenario 插件捕获 1280×720；JSFILMZ 用 1080p。
- 时长：CozyClay 建议 3–5 秒；htc911 3–15 秒；scenario 10–15 秒；单镜不超过 6 秒左右（7ohnson）。
- 人偶在画面里要够大（DeepWhite 的翻车）。

### 4.7 把上面合起来的一个默认配置（这一小节是我的归纳，不是任何一家的原话）

- 人偶：真实身高的胶囊或圆柱加球头，带明显的正面标记（面罩或鼻子块），不带四肢；按真人速度平移，起停有缓动。要特定肢体动作的镜头才换带骨骼的假人配动作库。
- 多人：每人一个标记，同时在提示词里按画面位置和标记双重指认；标记用颜色还是特征，要在自己的模型上测。
- 场景：真实尺寸的盒子和简模，有地面、墙和至少一个不对称地标；灰度分开，平光或一盏弱主光。
- 导出：两版，给模型的那版不叠任何东西；帧数对齐模型的格子；每段 ≤15 秒、每镜 ≤6 秒。
- 提示词：开头声明白模只提供走位、朝向、机位、运镜、切点，不提供外观、光和肢体动作；逐个映射；写冲突规则；负面点名白模感。

---

## 5. 工具和资产

### 5.1 专做这件事的产品、插件和技能

逐项的说明、许可、更新日期、原话见 [notes/tools_notes.md](notes/tools_notes.md)。下表只列和我们最相关的。

| 名称 | 是什么 | 交给模型的东西 | 许可 / 状态 | 对我们 |
|---|---|---|---|---|
| [scenario-labs/skills](https://github.com/scenario-labs/skills) 的 `scenario-blender-blockout` | 给 agent 的 Blender 白模 skill，纯 bpy、可无头跑 | 带身份色的 playblast + 交接单（色标、剪辑表、角色表）+ 2×2 风格板 | MIT，2026-11-16 更新，3,855 星 | 最值得读：人偶四档、对比实验、提示词写法、检查项 |
| [7ohnson/VLM-Generation-Harness](https://github.com/7ohnson/VLM-Generation-Harness) | Blender 白模 harness：`scene.py` 无头渲染、遮挡和占幅计算、切点核验、提示词自检 | 平光灰模 mp4 + 由几何算出的站位文字 | MIT，2026-08-11，19 星 | 15 条「铁律」和排错表都是花钱换来的；`verify_cuts.py` 的切点核验可以照做 |
| [Comfy-Org/workflows](https://github.com/Comfy-Org/workflows) | ComfyUI 官方的白模 → Seedance 2.5 工作流（Haunted Subway、Halloween） | 白模 mp4 + 参考图，带完整提示词和素材 | GPL-3.0，2026-10-29 | 可下载对照的完整例子 |
| [Blockout](https://github.com/wassermanproductions/blockout) | 开源桌面预演应用 | 参考视频 + 深度 + 法线 + 机位静帧 + 俯视走位图 + 按模型写的提示词 + ComfyUI 工作流 | Apache-2.0，2026-08 后没更新 | 导出包结构、按模型的 profile |
| [CozyClay](https://github.com/HaD0Yun/CozyClay) | 浏览器白模预演，带 MCP 和命令行 | 首尾帧 + 白模片段 + 机位 + 提示词；深度、法线 | AGPL-3.0，2026-11-17 | 导出规范、动作质检；代码不能并入 |
| [nana-whitebox](https://github.com/nawusijia/nana-whitebox) | 网页站位工具：俯视图摆人和机位，自动算左右、越轴、台词时长 | 站位文字（给提示词）；白模图只给人看 | MIT，2026-11-09，10 星 | 做法 H 的现成实现 |
| 即梦 Clay Renderer 插件 | Blender / Maya 官方插件，一键把白模渲染传到即梦 | 白模参考视频 | 随账号；要手点 | 证明 Seedance 官方把白模当正路 |
| 即梦短剧工作室 3D 导演台、[UpDream 预演台](https://www.bilibili.com/video/BV19gtc6aEQY)、LibTV 导演台、Higgsfield 3D Jutsu、Krea Seedance Studio、Intangible | 平台内置的 3D 片场：摆人形白模、机位、路径，录成参考视频（LibTV 只出截图） | 白模视频或截图 | 订阅；只能人手点 | 产品形态参考。UpDream 能从 1–3 张场景图估出白模场景【宣传】 |
| htc911「3D 导演台」桌面软件（[B 站](https://www.bilibili.com/video/BV16axj61EcN)，标题称免费开源，网盘分发） | 一张场景图用本地深度模型估出白模；人偶带 IK、23 个内置动作、能导 Mixamo FBX；运镜预设；可接 LLM 当「AI 导演」 | 粘土风引导视频，默认去轮廓线、保留角色颜色 | 没看到仓库和许可 | 导出选项的设计（去线稿、颜色可切浅灰）值得参考 |
| [Yedp Action Director](https://github.com/yedp123/ComfyUI-Yedp-Action-Director) | ComfyUI 里的 3D 视口节点 | OpenPose、深度、Canny、法线、灰模、Alpha、带贴图 7 种序列 | MIT，2026-11-13 | 走做法 E 时的出通道工具 |
| LTX-2.5 Layout-to-Render、SolarRenderer（H3） | 开放权重的「布局视频 + 首帧 → 成片」 | 灰模 playblast + 写实首帧 | 权重各有社区许可 | 本地可跑的做法 C |
| MCP for Blender、Blender Lab MCP、[EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills) | 让 agent 操作 Blender 的通道和技能包 | 不直接出信号 | MIT / 官方实验项目 | 交互调试时用；生产用无头脚本（7ohnson：「生产回路是 headless 的。MCP 是探索期和排查期的东西」「live 会话不是真相，`scene.py` 才是」） |
| Three.js 自己写（[cellinlab](https://x.com/cellinlab/status/2108867779021750318)、[ComfyUI-CodeVideo-ThreeJS](https://github.com/slmonker/ComfyUI-CodeVideo-ThreeJS)）、DaVinci Resolve 的 Fusion（[steftranquillin](https://x.com/steftranquillin/status/2117005090422710731)） | 不用 Blender 的白模来源 | 白模视频 | — | 说明白模来源不挑工具，任何能渲几何体和相机的都行 |
| 传统预演工具 Previs Pro、ShotPro、FrameForge、Storyboarder | 3D 分镜 | 只有 Previs Pro 接了 AI（在 3D 构图帧上做风格转换） | 多数多年没大更新 | 用处不大 |

谁能被 agent 脚本驱动：无头 Blender + bpy（scenario skill、7ohnson、ai-muninn 都这么跑）、ComfyUI API、LTX / SolarRenderer 命令行、CozyClay 命令行。平台内置的导演台和 ComfyUI 里的 3D 视口节点都要人在前端点。

### 5.2 资产

全表、许可证原句和核对过的页面见 [assets.md](assets.md)。要点：

- **可直接打包（CC0）**：Quaternius Universal Animation Library 1 / 2（自带一个关节假人 Mannequin）和 Universal Base Characters、Kenney、KayKit 免费版、The Base Mesh（1254 个真实尺寸无贴图网格）、Poly Haven、ambientCG、Blender Human Base Meshes、Blender 自带的 8 张 HDRI、MPFB 生成的人体。CMU Mocap 不是 CC0 但官网写明可再分发。
- **有坑**：Quaternius 2026-08-28 起有新许可证 QAL，禁止再分发，按包生效，我们要的几包页面仍标 CC0（FAQ 没同步）；Mixamo 不许单独分发动作文件，FAQ 写明不对中国区账号开放；Anderson Rohr 的日常动捕包最适合对戏但禁止再分发；Bandai Namco、LAFAN1、AMASS、SFU 不可商用。
- **和第 4 节的关系**：对照实验说粗白模不要四肢，所以动作库只在「肢体动作必须由白模决定」的镜头才用得上（打斗的一招、坐下起身的时机、特定手势）；家具和场景用 The Base Mesh 这类无贴图、真实尺寸的模型，正合「体积和遮挡准、细节糙」的要求。带贴图的写实资产（Poly Haven 模型、Quaternius 基础人体）进白模前要统一换成灰材质。

---

## 6. 互相矛盾的说法（汇总）

| 问题 | 说法 A | 说法 B | 有没有对照 |
|---|---|---|---|
| 人偶要不要四肢 | 不要：Seedance 官方、scenario 实验、GrandVisionsAI、娜乌斯嘉、DeepWhite、TanLuAI、Higgsfield 示例 | 要：7ohnson（裸圆柱认不出朝向和「在走」）；Wan 3.0 官方示例是完整人物；Blockout 用带关节假人 | 程序化迈步对胶囊：有（Seedance 2.5，单次）。静态带姿势假人对胶囊：没有 |
| 人偶上不上色 | 上：Seedance 官方示例、scenario、TanLuAI、DeepWhite、htc911 | 不上：7ohnson（自称是推理）、CozyClay、Wan 3.0 示例 | 没有 |
| 提示词里说不说替身的形状和颜色 | 不说：scenario（Seedance 类）、LTX 模型卡 | 说：Seedance 官方示例、TanLuAI、ai-muninn、Blockout、DeepWhite | 没有 |
| 外观用什么锁 | 白模第 1 帧转写实当首帧：LTX 模型卡、flick.art、Polypro、时光之刃 | 单张转风格帧会把构图和形状带进去，用 2×2 风格板或普通角色 / 场景参考图：scenario、ComfyUI 官方工作流、TanLuAI | 没有 |
| 白模带不带光 | 平光，不给方向：7ohnson | 带明暗梯度：Luma 官方；简单明确的主光：Blockout；细白模带完整光影：Wan 3.0、Seedance 示例 2 | 没有（Luma 说的是它自己的 Motion 控制） |
| 白模要多细 | 粗：Seedance 官方、多数社区 | 细：Wan 3.0 官方示例、Seedance 细粒度（用于已建好模的重渲染） | 娜乌斯嘉：方块、精细、深度图几乎一样 |
| 手和道具接触 | 白模里把手摆到位：7ohnson、CozyClay | 人偶不要手，接触靠文字：Higgsfield 示例、ai-muninn | 没有 |
| 参考视频通道贵多少 | 约 20%：DeepWhite | 约 8%（28.2 对 26 积分每秒）：7ohnson | 平台和时间不同 |
| 白模值不值 | 值：多数 | 「不如把提示词写扎实」：DeepWhite 评论区；简单镜头不值：DeepWhite、鱼摆摆喂、aiwarts、娜乌斯嘉、Mixar 都说过 | 娜乌斯嘉：原地转和正反打有没有白模一样；楼梯连接二楼有白模明显好；有一轮没白模的反而更好（白模本身走得太快） |
| 参考视频是什么 | 动作、运镜参考：Seedance、Wan、Kling、H3 | 保外观用：Gemini Omni 官方 | 官方定义不同 |
| 「完整 3D 数据」 | Intangible 自称传给模型的是完整 3D 场景数据 | 没有任何模型接口吃 3D 场景；CozyClay 明说参考视频是「pixel channel」 | 厂商说法，未证实 |

---

## 7. 对我们最值得先试的接法

（这一节是我的判断，依据都在上面。）

1. **做法 A 在 Wan 3.0 上的最小测试**。一段 ≤15 秒、两三个胶囊人偶、两三次切镜的白模当 `reference_video`，人物图当 `reference_image`，提示词照官方写法（「参考视频只用于……不继承其外观；最终画面正常彩色」）加逐个映射。先测四件事（照 7ohnson 的清单）：切点偏差、有没有灰模污染、人有没有换位、参考图和白模冲突时听谁的。Wan 3.0 的白模路线没有任何社区实测，这一步省不掉。
2. **人偶粒度和上色，各做一次对照**。同一场景、同一提示词：胶囊带面罩对带姿势的假人；全灰对身份色。Seedance 2.5 上的结论不一定搬得到 Wan 3.0（scenario 的实验里三个模型的反应就不一样）。
3. **做法 H 先落地**。不管模型吃不吃白模，先让脚本从几何算出每镜「谁在画面左、谁在右、谁挡谁、景别」，写进提示词，并查越轴。成本最低，对现有流程没有侵入。
4. **做法 D 当退路**。Wan 3.0 的首帧和参考互斥：要严格锁第一帧构图的镜头，用白模机位图转写实当首帧 / 首尾帧，运镜写文字；要锁运动的镜头走 A。Seedance 2.5 那边可以用提示词把参考图指定为首帧。
5. **做法 B 只在已有像样 3D 动画时用**。Wan 3.0 官方示例就是这种，适合「把预演当成片的骨架逐帧上色」，不适合只想管走位的粗白模。

---

## 8. 没查成的和局限

- **X**：帖子按公开页面读，**回复串大多没读到**，只读到 GrandVisionsAI 楼下两条。@GeekCatX、@rewind02、@dreamina_ai（2026-09-18）、@ridark_eth 四条只在搜索结果里读到被截断的正文，没取到帖子链接。
- **B 站**：搜索 6 次（其中 1 次 TLS 握手超时，换词再搜成功），没有风控提示。字幕读了 9 条，另 1 条没有字幕只读了简介；评论读了 1 条视频的 25 条。两套 3 小时以上的白模课程（BV1Pj4u6qEvN、BV1BGsF6hEQS）和 ReelFork 的 44 分钟课没看。
- **YouTube**：读到 2 条文字稿（ComfyUI 官方短片、Dan Kieft），第 3 条取字幕时返回 429，就没再试。JSFILMZ、Mira AI 等几条教程只有标题。
- **WebFetch 工具**对多数域名报域名校验失败，全程用 curl 读正文。
- **搜索结果里给出但打不开的两个仓库**：`mcanozkulekci/blender-unreal-comfyui-workflows`、`Wanrd0Geri/seedance-previz`，GitHub 上都是 404，引用到的地方都标了「转述」，没当证据用。
- **证据偏向**：社区实测几乎全在 Seedance 2.5 上；Wan 3.0、Kling 4.0 的白模输入只有官方文档；做法 E、F 在 2026 年没找到完整的社区短片案例。大量帖子和视频是平台合作稿（即梦、UpDream、Higgsfield、WaveSpeed、Flick、Mixar），已标【宣传】。
- 所有对照实验都是单次或少量生成，作者自己也这么注明；没有一个给出多次采样的统计。
- 我没有生成任何图片或视频，以上结论都没有在我们自己的模型上验证过。

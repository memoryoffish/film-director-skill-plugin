# 各视频模型吃什么（官方文档核对）

> 底稿说明：调研时的逐项笔记，结论汇总在 [../research.md](../research.md)。

核对日期：2026-11-17。只记官方文档、官方帮助中心、官方 GitHub README 里**亲眼看到**的原文；没看到官方原文、只在第三方看到的标「转述」。引语保留原文。格子里「有 / 无 / 不明」后面的编号对应每节的出处。

> 和 video-film-maker 的 `refs/practical/models.md` 对不上的地方：
> 1. models.md 写 Seedance 2.5「没有参考视频」。火山方舟官方文档写的是**有**（`reference_video`，2.5 最多 10 个、总时长 ≤ 30 秒，还专门有「白模参考/渲染」一节）。models.md 记的应是经第三方网关的情况，不是模型本身。
> 2. wan3-notes.md 写参考图「≤ 10 张」「首帧/尾帧不能和参考图、参考视频同时用」，和官方一致；官方另写参考视频「最多 5 段，总时长不大于 15 秒」、输入 + 输出总时长 ≤ 30 秒。

---

## 0. 支持矩阵（一眼看）

图例：有 = 官方文档明写；无 = 官方文档明写不支持，或官方功能清单里没有；不明 = 没查到官方说法。

| 模型（文档版本/日期） | 文生 | 首帧 | 首尾帧 | 主体参考图 | 参考视频·动作 | 参考视频·运镜 | 深度/姿态/线稿等结构控制 | v2v 转绘（restyle/modify） | 显式相机参数 | 官方提到白模/previz |
|---|---|---|---|---|---|---|---|---|---|---|
| **Wan 3.0**（百炼，2026-11） | 有 [W3-1] | 有 [W3-1] | 有；尾帧须配首帧 [W3-2] | 有，≤10 张 [W3-2] | 有 [W3-3] | 有 [W3-3] | 无专门接口；用白模视频、火柴人分镜图代替 [W3-3] | 有：视频编辑、白模重渲染 [W3-1][W3-3] | 无 | **有**：「白模参考/渲染」任务 [W3-3] |
| Wan 2.7（百炼） | 有 | 有 [W27-1] | 有 [W27-1] | 有，图+视频 ≤5，**可叠首帧** [W27-2] | 有（videoedit 复刻动作）[W27-3] | 有（复刻运镜）[W27-3] | 无 | 有 [W27-3] | 无 | 无 |
| Wan 2.1 VACE（开源） | 有 | 有 | 有（也可只给尾帧）[VACE-2] | 有 [VACE-2] | 有（pose）[VACE-2] | 间接（depth / flow） | **有**：depth、pose、gray、scribble、flow、layout [VACE-2] | 有（V2V / MV2V）[VACE-2] | 无 | 无（没提） |
| Wan 2.2 Fun Control / Camera、VACE-Fun（开源） | 有 | 有（InP） | 有（InP）[FUN-1] | 有（VACE-Fun）[FUN-1] | 有（pose） | 有（Control-Camera）[FUN-1] | **有**：Canny、Depth、Pose、MLSD、轨迹 [FUN-1] | 有 | 有（相机轨迹权重）[FUN-1] | 无 |
| Wan 2.2 Animate | 不适用 | 不适用 | 不适用 | 一张角色图 [W22-1] | 有 [W22-1] | 替换模式沿用原视频 | 内部用骨骼 + 脸 [W22-1] | 替换人物 [W22-1] | 无 | 无 |
| **Seedance 2.5**（方舟，2026-11-16） | 有 [SD25-1] | 有 [SD25-1] | 有 [SD25-1] | 有，≤30 张 [SD25-1] | 有 [SD25-2] | 有 [SD25-2] | 无专门接口；用白模视频、线稿宫格、关键帧代替 [SD25-2] | 有：视频编辑、细粒度白模上色 [SD25-1][SD25-2] | 无 | **有**：「白模参考/渲染」，分粗/细 [SD25-2] |
| Seedance 2.0 | 有 | 有 | 有 [SD20-1] | 有，≤9 张 [SD20-1] | 有 [SD20-2] | 有 [SD20-2] | 无 | 有 [SD20-1] | 无 | 间接：续写前先转白模 [SD20-2] |
| **Kling 4.0**（2026-10） | 有 [K4-1] | 有 | 有，≤10 个关键帧 [K4-1] | 有，≤7 个主体 [K4-1] | 有 [K4-1] | 有 [K4-1] | **有：深度图视频、白模视频**；图里收线框/分镜；姿态不明 [K4-1] | 有 [K4-1] | 无 | **有**：一句话 [K4-1] |
| Kling O1 / 3.0 Omni | 有 [KO1] | 有 [KO1] | 有；不能只给尾帧 [KO1] | 有，≤7（带视频时 ≤4）[K3O] | 有 [KO1] | 有 [KO1] | 不明 | 有（换角度、restyle）[KO1] | 无 | 无 |
| Kling Motion Control 2.6 / 3.0 | 不适用 | 人物图 | 不适用 | 人脸 Element（3.0）[KMC] | 有，3–30 秒 [KMC] | 有（Matches Video 档）[KMC] | 不适用 | 不适用 | Matches Image 档用提示词写运镜 [KMC] | 无；「stylized humanoid……can be recognized」[KMC] |
| Veo 3.1 | 有 [G-3] | 有 [G-3] | 有 [G-3] | 有，≤3 张且只能 8 秒 [G-3] | 无 | 无 | 无 | 无 [G-4] | 无 | 无 |
| Gemini Omni Flash 1.2（Flow） | 有 [G-2] | 有 [G-2] | 有，3–10 秒 [G-2] | 有，≤6 张 [G-2] | 无（参考视频是保外观用的）[G-2] | 无 | 无 | 有，≤15 秒 [G-2] | 无 | 无 |
| Runway Gen-4.5 | 有 [R-3] | 有 [R-3] | 无（另有 Animate Frames 应用）[R-7] | 无 [R-3] | 无 | 无 | 无 | 无 | 无 | .glb 截图可当首帧 [R-5] |
| Runway Aleph 2.0（Edit Studio） | 不适用 | 不适用 | 改一帧带全段 [R-1] | 参考图 [R-2] | 沿用源视频 | 沿用源视频 | 无 | **有**，2–30 秒 [R-2] | 无 | 无 |
| Runway Act-Two | 不适用 | 不适用 | 不适用 | 角色图或角色视频 [R-6] | 有 [R-6] | 角色视频自带 [R-6] | 不适用 | 不适用 | 无 | 无 |
| **Luma Ray 3.2 Modify** | 无 [L-1] | 不适用 | 关键帧 ≤64，贴在源帧号上 [L-1] | 走关键帧 | 有 [L-1] | 有 [L-1] | **有**：Motion / Structure 滑杆，Poses / Blocking 开关 [L-1] | **有**，≤20 秒 [L-1] | 无 | **有**：占位物、3D 物体、pre-vis 级 Blocking [L-1] |
| Luma Ray2 Modify（旧 API） | 不适用 | first_frame 可选 [L-2] | 不适用 | 不适用 | 有 | 有 | adhere / flex / reimagine 各 3 档 [L-2] | 有 [L-2] | 无 | 发布文提 previs、low-poly [L-3] |
| MiniMax H3（Hailuo 3.0） | 有 [M-1] | 有 [M-1] | 有；也可只给尾帧 [M-2] | 有，≤9 张 [M-1] | 有 [M-1] | 有 [M-1] | 官方接口无；开源侧有 Fun-Controlnet-Union [FUN-1] | 有（文档只一句）[M-1] | 无 | 无 |
| Hailuo 02 / 2.3（旧 V1） | 有 | 有 | 有（仅 02）[M-4] | S2V-01，单张人脸 [M-4] | 无 | 无 | 无 | 无 | **有**：15 种 `[指令]` 运镜 [M-4] | 无 |
| Higgsfield | 取决于所选底层模型 [H-1] | 同左 | Cinema Studio 有首尾帧 [H-1] | 同左 | 同左 | 同左 | 无 | 同左 | 预设项：机身、镜头、焦段、光圈、运镜名 [H-1] | 无；有「图 → 3D 场景挑机位」[H-1] |
| LTX-2.5（开源） | 有 | 有 | 不明 | 不明 | 有（pose）[LTX-1] | 间接（depth） | **有**：depth、canny、pose、稀疏轨迹 [LTX-1] | 有（IC-LoRA v2v）[LTX-1] | 无 | **有**：深度图来源列了 Blender [LTX-1] |
| Moonvalley Marey | 不明 | 不明 | 不明 | 不明 | 有 [MV-1] | 有 [MV-1] | 不明 | 不明 | 单图转 3D 后控相机 [MV-1] | 无 |
| Vidu（Q2–Q4） | 有 | 有 | 有 [V-1] | 有，≤7 张 [V-1] | 不明 | 不明 | 无 | 不明 | 无 | 无 |
| Pika 2.5 | 有 | 有 | 有，2–5 张 [P-1] | 不明 | 不明 | 不明 | 无 | 不明 | 无 | 无 |
| HunyuanVideo 1.5（开源） | 有 [HY-1] | 有 [HY-1] | 无 | 无 | 无 | 无 | 无 | 无 | 无 | 无 |
| HappyHorse 1.1（百炼） | 有 [W3-4] | 有 [W3-4] | 无 | 有（参考图）[W3-4] | 无 | 无 | 无 | 1.0-video-edit [W3-4] | 无 | 无 |
| Sora 2 | 已于 2026-09-24 停止（转述） | | | | | | | | | |

---

## 1. Wan（阿里）

### 1.1 Wan 3.0（`wan3.0-video` / `wan3.0-video-prime`，百炼文档 2026-11-11～11-14 更新）

出处：
- [W3-1] 使用指南《万相3.0-视频生成》https://help.aliyun.com/zh/model-studio/wan3-video-generation-guide （页面 lastModified 2026-11-14）
- [W3-2] API 参考 https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference （2026-10-15）
- [W3-3] Prompt 指南 https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide （2026-11-11）
- [W3-4] 选型页《视频生成与编辑》https://help.aliyun.com/zh/model-studio/video-generate-edit-model/

**矩阵行**：文生 有；首帧 有；首尾帧 有（尾帧必须配首帧）；主体参考图 有（≤10 张）；参考视频·动作 有；参考视频·运镜 有；深度/姿态/线稿 **无专门接口**（没有 control 类型的输入，只有 `reference_video`，靠提示词说「参考什么」；白模视频、火柴人分镜图是官方给的替代）；v2v 转绘 有（视频编辑：风格转换、增删改；「白模参考/渲染」）；显式相机参数 无（运镜靠文字或参考视频）。

**官方原话**

- 能力总述 [W3-1]：「wan3.0系列是All-in-One视频生成模型……单次生成时长最长30秒、输出帧率30fps，并原生输出台词、BGM和音效，单次支持最多20个多模态素材参考（图片、视频、音频、文档、网页），支持首帧/首尾帧控制和视频编辑与延长。」
- 路由 [W3-1]：「模型根据 input.media 中的 type 字段和提示词意图自动路由。」「每种任务类型仅支持传入下表中对应的 type 值，不同任务类型的 type 不可混用。例如，首尾帧模式仅支持 first_frame 和 last_frame，不可同时传入 reference_audio 等其他类型。」
- 首尾帧 [W3-1]：「通过 first_frame/last_frame 严格指定视频首帧或尾帧图像，像素级还原参考画面。」[W3-2]：「first_frame：首帧图像。最多1张，严格作为视频第一帧。last_frame：尾帧图像。最多1张，严格作为视频最后一帧。」
- **互斥** [W3-1][W3-2]：「reference_xx/file/link 类型和 first_frame/last_frame 类型互斥，不能在同一请求中混用。」报错原文：「The two modes are mutually exclusive. Do not pass reference_xx and first_frame/last_frame at the same time.」「reference_image/reference_video/reference_audio 之间可自由组合。」
- 参考视频的上限 [W3-2]：「reference_video：参考视频。最多5段，总时长不大于15秒。」视频限制：「格式：mp4、mov。时长：单个[1, 15]秒，总时长不大于15秒。帧率：≥16 fps。分辨率：单边[240, 4096]像素。长宽比：不超过8:1。单文件大小：不超过100MB。」[W3-1]：「有视频输入时，输入+输出总时长≤30秒。」
- 参考图 [W3-2]：「reference_image：参考图像。最多10张。」「分辨率：单边[240, 8000]像素。」「PNG（不支持透明通道）」
- 参考视频能参考什么 [W3-1]：「运镜/动作参考：传入参考视频，复刻其运镜方式或动作编排。」[W3-3] 任务类型表：「运动参考｜提示词 + 含动作 / 表情 / 运镜 / 特效的参考视频｜复刻参考运动信息的新视频」；「主体参考｜提示词 + 人 / 物 / 场景 / 虚拟角色的参考图或视频｜保留参考主体外观 / 声音的新视频」。
- **同一段参考视频是当「主体」还是当「运动」，由提示词决定** [W3-3]「视频时序迁移」：「把参考视频的动作、运镜、特效当成时序信号迁移到新角色或新场景，节奏照搬，主体、环境自由换。」写法表：「只借运动/运镜｜参考视频的运镜方式，场景改为一杯咖啡放在天台咖啡桌上」「只借动作｜视频1中的滑板男人替换为图1中的女人，滑板动作、轨迹和场景保持不变」。
- **「只参考动作、不继承外观」的官方写法** [W3-3]（打斗案例提示词）：「参考图1、图2的人物角色，仅参考视频1的视频动作……人物复刻参考视频中的全部动作、姿态、节奏和停顿，动作顺序、幅度、速度和发生时机保持一致……**参考视频只用于动作控制，不继承其人物外观。**最终画面正常彩色，人物稳定……两人各自的外观锁定各自的参考图，不要混淆、不要互换服装发色。」（注意它还特意写了「最终画面正常彩色」。）
- 视频编辑 [W3-1]：「传入参考视频，通过自然语言指令对视频进行精准编辑，未指定修改的部分保持不变。」「提示词中需包含编辑意图关键词（如"编辑视频""去掉""替换""改成"等）。」「ratio 建议设为 adaptive，duration 建议设为 -1（自动保持原视频宽高比和时长）。」
- 故事板 [W3-3]：「上传九宫格 / 火柴人分镜图作为剧情梗概……在提示词起始处说明故事板仅用于分镜指导，例如 使用故事板作为分镜指导，禁止将故事板作为单张图像生成视频，避免模型将整张宫格图当作单帧素材。」任务表另有「关键帧参考｜提示词 + 多张关键帧图｜对齐关键帧顺序的视频」。

**对白模 / previz 的直接说法**（[W3-3]「白模参考/渲染」一节，官方把它列为一种任务：「白模参考 / 渲染｜提示词 + 白模视频｜写实化重渲染的视频」）

- 「上传纯白 clay render 白模视频作为唯一蓝本，仅将材质、颜色、纹理替换为真实世界质感，其余画面逐帧保持不动。」
- 「明确锁定项：声明"除材质与颜色外一律不改"，并将镜头轨迹、剪辑点、物体位置、角色动作等列为"绝对保持不变"，反复强调"不许新增、不许删减、不许移动""一帧不增删、一秒不错位"。」
- 「强调真实感：通过 玻璃真实折射、树皮透光叶脉、皮肤次表面散射 等光学细节，让生成画面更具真实质感。」
- 官方示例提示词（节选）：「以视频1（我上传的纯白 clay render 白模动画）作为唯一蓝本，做一次写实化重渲染：把画面里所有还是纯白哑光素模的物体与角色，全部替换成真实世界的材质与颜色……除了材质与颜色之外什么都不许改。」「【绝对保持不变·最高优先级】镜头运动轨迹、每一次推拉摇移与环绕的速度和方向、景别切换的时刻、剪辑点、画面比例、总时长、构图与透视，全部与参考视频逐帧一致……场景里每一件物体的位置、朝向、大小比例、数量与相互遮挡关系完全照搬……阳光方向、投影角度与长度、每一帧的明暗分布照搬原片。」「【光影】完全沿用白模视频的灯光方向与投影……原白模的所有 AO 暗角保留为带环境色溢色的通透暗部，暗部有颜色与细节，不许压成死黑」
- 官方负向清单直接点了白模的翻车点：「禁止出现残留的白模区域、局部未上色的纯白物体、材质丢失的灰模块与贴图错位；禁止出现卡通、动漫、插画、塑料玩具与 CG 假质感；禁止出现欧美白人脸、混血脸……；禁止出现线框网格线、坐标轴、操作界面与任何 UI 元素」。还写了「原白模的卡通圆润造型在写实化后保留其体块轮廓与比例」（即：白模的体型比例会被照搬，人偶比例要自己先做对）。

### 1.2 Wan 2.7（`wan2.7-*`，百炼）

出处：
- [W27-1] 图生视频 https://help.aliyun.com/zh/model-studio/wan-image-to-video-guide
- [W27-2] 参考生视频 https://help.aliyun.com/zh/model-studio/video-to-video-guide
- [W27-3] 视频编辑 https://help.aliyun.com/zh/model-studio/wan-video-editing-guide

**矩阵行**：文生 有；首帧 有；首尾帧 有；主体参考图 有（图+视频 ≤5）；参考视频·动作 有（`wan2.7-videoedit` 的「复刻动作」）；参考视频·运镜 有（「复刻运镜」）；结构控制 无专门接口；v2v 转绘 有（指令编辑、改风格）；显式相机参数 无。

- 图生视频 [W27-1]：「支持 首帧生视频、首尾帧生视频、视频续写（首视频片段续写/首视频片段+尾帧续写） 三大任务。」「首视频片段+尾帧续写：设置type为first_clip和last_frame，在续写首视频的同时控制视频结束状态与尾帧一致。」「仅支持以下特定的素材组合，传入其他组合将报错。」
- **2.7 的参考生视频可以叠首帧**（3.0 反而互斥）[W27-2]：「多主体参考+首帧控制……在主体参考基础上加入首帧控制，让画面构图和内容走向更加可控。」「首帧图像最多1张，参考图像和参考视频至少传入1个，参考图像 + 参考视频 ≤ 5。」「首帧无需在提示词中引用。」
- 视频编辑 [W27-3]：「万相视频编辑模型支持对输入视频进行内容增删改、背景替换、风格转换、动作/特效/运镜复刻等编辑操作」「复刻动作/运镜/特效：复刻参考视频的动作序列、运镜轨迹与视觉特效，生成动态特征一致的视频。」示例：「复刻运镜｜参考原视频运镜方式，镜头快速移动，场景更改为在颁奖典礼上，参考图片中的女人在走红毯。」「修改风格｜将整个画面转变为真人电影风格」。输入：「视频数量：必传，有且仅有1个。」「图像数量：可选，最多4张。」
- 选型页 [W3-4]：「如果需要进行特效复刻、运镜复刻，推荐使用wan2.7-videoedit。」
- 2.7 参考生视频里的参考视频很短 [W27-2]（计费说明）：「输入视频计费时长：上限 5 秒。单个视频截断上限 = 5秒 ÷ 输入参考视频数量」（1 个 5 秒、2 个各 2.5 秒……）。官方只在计费里写了「截断」，没明说模型是否只看这几秒；这条路的参考视频是当「主体」用的，不是长段运镜参考。
- Wan 2.5 / 2.6：百炼文档里仍列着 `wan2.6-t2v`、`wan2.6-i2v(-flash)`、`wan2.6-r2v(-flash)`、`wan2.5-t2v-preview`、`wan2.5-i2v-preview`（出现在 [W27-1][W27-2] 的模型与计费表里），这次没读它们的专页；2.6 的参考生视频同样有「5 秒 ÷ 参考素材总数」的截断规则。旧的 `wan2.1-vace-plus`（百炼托管的 VACE，「视频编辑｜720P。最长5秒」）还在 [W3-4]；官方 FAQ [W27-3]：「视频编辑2.1需指定function参数，侧重掩码局部编辑、画面扩展等功能。推荐优先选用视频编辑 2.7。」

### 1.3 Wan 2.2 Animate / Fun Control / Fun Camera、Wan 2.1 VACE（开源，本地或 ComfyUI）

出处：
- [VACE-1] VACE README https://github.com/ali-vilab/VACE （ICCV 2025；Wan2.1-VACE-1.3B / 14B，2025-05-14 发布）
- [VACE-2] VACE UserGuide https://github.com/ali-vilab/VACE/blob/main/UserGuide.md
- [W22-1] Wan2.2 README https://github.com/Wan-Video/Wan2.2
- [FUN-1] VideoX-Fun README https://github.com/aigc-apps/VideoX-Fun
- [W3-4] 百炼选型页（wan2.2-animate-move / animate-mix）

**矩阵行（VACE）**：文生 有；首帧 有（frameref firstframe）；首尾帧 有（firstlastframe，也支持只给尾帧 lastframe、首尾片段 clipref）；主体参考图 有（R2V，`src_ref_images`，组合任务里「不超过三张」）；参考视频·动作 有（pose 控制 = Animate Anything）；参考视频·运镜 无专门项（靠 depth/flow 控制视频间接带过来）；**结构控制 有：depth、flow、gray、pose、scribble、layout_bbox、layout_track**；v2v 有（V2V / MV2V）；显式相机参数 无。

- 任务定义 [VACE-2]：「Video Generation: No video input……including **T2V** and **R2V**」「Video Editing: With video input. Modifying input video at the pixel level globally or locally, including **V2V** (Video-to-Video Editing) and **MV2V** (Masked Video-to-Video Editing).」「Composition Task: ……**Reference Anything** (Face R2V + Object R2V), **Move Anything**(Frame R2V + Layout V2V), **Animate Anything**(R2V + Pose V2V), **Swap Anything**(R2V + Inpainting MV2V), and **Expand Anything**」
- 输入怎么喂 [VACE-2]：「`src_video`: The video to be edited for input into the model, such as condition videos (Depth, Pose, etc.) or in/outpainting input video. **Gray areas**(values equal to 127) represent missing video part. In first-frame R2V task, the first frame are reference frame while subsequent frames are left gray.」「`src_mask`: ……**White areas** represent the parts to be generated, while **black areas** represent the parts to be retained.」「`src_ref_images`: Reference images of R2V. Salient object segmentation can be performed to keep the background white.」「Use descriptive prompt instead of instructions.」
- 控制类型表 [VACE-2]：control 子任务 = `depth`（DepthVideoAnnotator）、`flow`（FlowVisAnnotator）、`gray`（GrayVideoAnnotator）、`pose`（PoseBodyFaceVideoAnnotator）、`scribble`（ScribbleVideoAnnotator）、`layout_bbox`（两个框，「Move linearly from the first box to the second box」）、`layout_track`。extension 子任务 = `firstframe` / `lastframe` / `firstlastframe` / `firstclip` / `lastclip` / `firstlastclip`。
- 限制 [VACE-2]：「Super long video will be trimmed or uniformly sampled into around 5 seconds.」「we recommend to generate 5s video clips one by one, while using `firstclip` video extension task to keep the temporal consistency.」规格 [VACE-1]：Wan2.1-VACE-14B「~ 81 x 720 x 1280」、1.3B「~ 81 x 480 x 832」。
- 对白模的含义（我的推论，非官方原话）：Blender 可以直接渲出深度通道和灰度图当 `src_video`，不必再用 annotator 估深度；`gray` 控制本身就是「给灰度视频上色」。官方没有提 Blender / previz。

**Wan 2.2 Animate** [W22-1]：「Wan-Animate takes a video and a character image as input, and generates a video in either "animation" or "replacement" mode. 1. animation mode: The model generates a video of the character image that mimics the human motion in the input video. 2. replacement mode: The model replaces the character image with the input video.」预处理后给的是 `src_pose.mp4` + `src_face.mp4`（骨骼 + 脸）。百炼 [W3-4]：「将参考视频中的动作迁移到静态图片中的人物上，推荐使用wan2.2-animate-move。背景保持不变。」「将视频中的人物替换为图片中的人物，推荐使用wan2.2-animate-mix。」Wan2.2-S2V 还有 `--pose_video`：「enables pose-driven generation, allowing the model to follow specific pose sequences while generating videos synchronized with audio input.」

**Wan 2.2 Fun Control / Camera、VACE-Fun** [FUN-1]：
- 「Wan2.2-Fun-A14B-Control：Wan2.2-Fun-14B video control weights, supporting various control conditions such as Canny, Depth, Pose, MLSD, etc., and trajectory control. Supports multi-resolution (512, 768, 1024) video prediction at 81 frames, trained at 16 frames per second」
- 「Wan2.2-Fun-A14B-Control-Camera：Wan2.2-Fun-14B camera lens control weights.」（相机轨迹控制；README 致谢 CameraCtrl）
- 「Wan2.2-VACE-Fun-A14B：Control weights for Wan2.2 trained using the VACE scheme……supporting various control conditions such as Canny, Depth, Pose, MLSD, trajectory control, etc. It supports video generation by specifying the subject.」
- 「`control_video` is the control video extracted using operators such as Canny, Pose, or Depth.」
- 同一仓库现在还列了 MiniMax-H3 的开源权重和「MiniMax-H3-Fun-Controlnet-Union……supports multiple control conditions and trajectory control」（见 §5）。

---

## 2. Seedance 2.x（字节 / 火山方舟）

出处（火山方舟文档，均为 2026-11-16 更新）：
- [SD25-1] 《Doubao Seedance 2.5 系列教程》https://www.volcengine.com/docs/82379/2607688
- [SD25-2] 《Doubao Seedance 2.5 系列提示词指南》https://www.volcengine.com/docs/82379/2607689
- [SD25-3] 官方提示词 skill sd25-pe 0.1.1（下载地址和各节位置见 [video-film-maker 的 prompt-skills/overview.md](../../../../video-film-maker/refs/practical/prompt-skills/overview.md)）
- [SD20-1] 《Doubao Seedance 2.0 系列教程》https://www.volcengine.com/docs/82379/2291680
- [SD20-2] 《Doubao Seedance 2.0 系列提示词指南》https://www.volcengine.com/docs/82379/2222480
- [SD-0] 《视频生成教程》https://www.volcengine.com/docs/82379/2298881

**矩阵行（2.5）**：文生 有；首帧 有；首尾帧 有；主体参考图 有（30 张 / flash 10 张）；参考视频·动作 有；参考视频·运镜 有；深度/姿态/线稿 **无专门接口**（官方替代：白模视频、火柴人/线稿宫格分镜、关键帧参考）；v2v 转绘 有（视频编辑；细粒度白模「白模上色」）；显式相机参数 无。
**矩阵行（2.0）**：同上，上限 9 图 + 3 视频 + 3 音频；没有「白模参考/渲染」这个官方任务名，但参考视频的动作/运镜参考是有的。

**官方原话**

- 2.5 的任务划分 [SD25-1]：「任务类型包括文生视频、首帧/首尾帧生视频，以及全模态参考生视频任务；其中全模态参考生视频任务根据提示词意图进一步分为参考生视频、视频编辑和视频延长 3 类子任务。」
- 上限 [SD25-1]：「参考图片数量上限由 9 张增至 30 张（Seedance 2.5）/ 10 张（Seedance 2.5 flash）」「参考音频、视频数量上限由 3 个增至 10 个（Seedance 2.5）/ 5 个（Seedance 2.5 flash）」「参考音频、视频总时长由 15 秒增至 30 秒」「生成视频时长上限由 15 秒延长至 30 秒」。
- 输入视频要求 [SD25-1]：「视频格式：mp4、mov」「分辨率：480p、720p、1080p、4K」「非视频编辑任务：单个视频时长 [2, 30] s。视频编辑任务：单个视频时长 [4, 30] s。总时长：所有视频总时长不超过 30 s。」「宽高比（宽/高）：[0.4, 2.5]」「大小：单个视频不超过 200 MB。」「帧率（FPS）：[24, 60]」（白模视频要按 ≥24 fps 渲）。
- 首尾帧 [SD25-1]：「首帧/首尾帧生视频｜content.role 设置为 first_frame / last_frame｜ratio 必须为 adaptive；模型自动保持输出视频宽高比和 `first_frame` 指定的首帧图片一致」。
- 视频编辑的硬限制 [SD25-1]：「视频编辑｜……ratio 必须为 adaptive、duration 必须为 -1；模型根据提示词意图选定待编辑视频，并自动保持输出视频宽高比、时长和待编辑视频一致；参考视频时长必须为 4-30 秒」「提示词中需包含至少一个关键词：编辑视频、增加/加上、删除/去掉、修改/替换/改成。」可用 `omni_reference_task_type` = `auto` / `edit` / `extend` 显式指定；判错会报 `InvalidParameter.TaskTypeMismatch`。
- **首帧 + 参考能不能同时用**：接口层面 `first_frame/last_frame` 是单独的任务类型；官方给的绕法 [SD20-1]：「进阶用法：全模态生视频可通过提示词指定参考图片作为首帧/尾帧，间接实现"首尾帧+全模态参考"效果。若需严格保障首尾帧和指定图片一致，优先使用图生视频-首尾帧（配置 role 为 first_frame/last_frame）。」[SD25-3]：「关键帧图片仍作为普通参考图输入，只在 Prompt 中逐张指定职责。」「固定首帧时必须单独写出 `@图片N作为首帧。`……不得弱化为"仅作为首帧参考""参考开场构图"」。
- 参考视频能参考什么 [SD20-1]：「可继承参考图片的角色形象、视觉风格、画面构图；参考视频的主体内容、运镜方式、动作表现、整体风格；以及参考音频的音色、音乐旋律、对话内容等核心信息。」[SD25-2] 能力表：「运动参考 - 参考图/视频的运动/动态信息｜动作/表情/运镜/创意/特效等运动参考；运动+主体参考」。
- **「只借动作/运镜、不继承外观」** [SD25-3]：「参考视频没有说明职责时，从动作、运镜、节奏、场景和声音中选择与任务有关的维度。**生成任务不得默认继承参考视频中的人物身份、服装或完整场景。**」模板：「@视频1用于<动作、运镜或节奏>，不采用<容易误带的身份、服装或场景>。」「@视频1用于<人物A>的<动作或运镜>，不采用视频中的人物和场景。」[SD25-1]：「明确素材职责：使用 @图片1、@视频1、@音频1 指代参考素材，说明每份素材具体提供什么（如外貌、动作、音色），以及不采用什么。」
- 素材别给满 [SD20-2]：「推荐配置（总计 4-5 个素材）：角色图 1-2 张（面部特写 / 全身）+ 场景图 1 张 + 运镜视频 1 段 + 音频 1 段。」「不建议用满素材上限，过多素材会导致模型难以判断特征优先级」。
- 真人脸 [SD25-1]：「Seedance 2.5 系列不支持直接上传含有真人人脸的参考图/视频。」（白模人偶没有真人脸，不触发这一条。）
- 宫格分镜 [SD25-2]：「多宫格目前更适用于 15 个以下分镜；推荐火柴人/线稿分镜，不推荐在分镜图上写过多文字」「宫格图并不会严格对齐分镜内容，视频会有一定自主性发挥，如需严格按照分镜图生成时，推荐使用多关键帧参考方式。」关键帧参考：「prompt 需要在第一句写明『以图片 x 至图片 x 的顺序作为关键帧』。」

**对白模 / previz 的直接说法**（2.5 官方把「白模参考/渲染」列为新增参考能力，[SD25-2]）

- 能力表：「白模参考/渲染 - 输入粗粒度或者细粒度白模视频参考其动态信息、进行渲染｜白模参考；白模参考+主体参考；白模参考+主体参考+场景参考」。
- **粗细怎么选**（官方 FAQ 表）：「白模参考，建议粗粒度还是细粒度｜**简单建模（粗粒度）参考效果较好，建议仅用简单几何体拼接表示人物/物体/动物等**」。
- 粗粒度：「支持输入含有运动、运镜、动线和光照等动态/时序信息的白模视频进行渲染；还支持叠加输入主体、场景和道具等参考图控制渲染效果。」「当前版本对于简单建模的参考效果较好」。
- **四肢** ：「白模视频主体建议仅保留躯体，避免包含【四肢/翅膀】等涉及精细运动的元素；如已包含，需补全其动作序列，以防止渲染结果出现四肢僵化。」
- 细粒度：「服务于建模完整，重点解决重渲染的场景，给『白模上色』获得更好更丰富的渲染效果。」「尽量提供完整且清晰的细粒度白模视频，不含【轨迹线】【坐标线】【相机 cone】等干扰信息的视频，否则容易泄露到生成后的视频中。」
- 提示词怎么写：「文本中写明希望参考白模视频中的什么元素。示例 1：白模中没有光影变化，只希望参考运镜和运动 → 『参考 [视频 1] 的运镜、动作...』；示例 2：白模有光影变化且需要参考 → 『参考 [视频 1] 的光影变化和...』」「如果叠加输入了参考图，需写明参考图和白模的对应关系。示例：『将 [图片 1] 中穿灰色衣服的男人对应 [视频 1] 中的**红色模型**、[视频 2] 中的红发少女替换 [视频 1] 中的**绿色模型 2**』」（官方示例就是**用颜色区分白模里的角色**）。「输入了白模视频，也建议在 Prompt 中详细描述希望生成的视频内容……注意文本描述需要和白模内容相吻合；对于没有叠加参考图/视频的白模主体，详细描述主体外表/特征效果更佳。」
- 官方粗粒度示例（30 秒、含切镜）：「以白模参考视频 <video1> 作为整支视频唯一的运镜、镜头节奏、景别变化、主体运动轨迹和镜头调度参考，严格保持白模视频的镜头顺序、机位变化、运动方式和节奏，不改变镜头结构，不新增镜头，不改变主体运动逻辑。结合各阶段关键帧参考图……」「整体要求：所有画面均参考对应关键帧，**白模视频仅作为运镜、镜头运动和角色动画参考，不参考画面内容。**」（做法 = 一段白模视频 + 每个时间段一张关键帧图。）
- 官方细粒度示例：「将视频 1 进行白模渲染，无 bgm，只生成环境音和动作音。渲染要求：背景为……」另有「高难度白模预演：复杂 3D 白模的结构与镜头调度逐帧承接，渲染出成片质感。」
- sd25-pe 的归纳 [SD25-3]：「粗粒度白模：简单几何体主要提供动作路径、运动方向、主体站位、进出场、机位、运镜、切镜、光影变化、声音节奏或空间关系。**每个几何体必须单独映射到最终主体或道具。**」「细粒度白模：主体、道具或场景结构已经完整，主要用于更换人物形象、材质、颜色、场景或视觉风格。」「白模视频作为生成参考，不因为它是视频就自动成为编辑母版。」（即：白模走「参考生视频」，不要写「编辑视频」这类词，否则会被路由成视频编辑、锁死画幅和时长。）模板：「@视频1是粗粒度白模参考，仅提供<动作路径、主体站位、机位、运镜、切镜……>，不采用其中的白模外观、材质和场景。@视频1中的<白模主体A>对应<主体A>。」
- 2.0 文档里另一处用到白模 [SD20-2]「视频延长画质劣化」：「将原始视频通过 Seedance 2.0 转为白模视频，再作为续写输入素材。参考提示词：将视频转为白色 3D 模型，人物统一为纯白 3D 模型，无色彩、无纹理、无阴影，纯白背景，结构稳定、运动流畅。」（官方自己把白模当成不带画质包袱的结构载体。）

---

## 3. Kling（快手可灵）

出处（官方 kling.ai）：
- [K4-1] 官方博客《Inside Kling 4.0: A Complete Guide to AI Video Creation》2026-09-30 https://kling.ai/blog/kling-4-ai-video-model （写明「The full model is coming in October 2026」；发布说明页 https://kling.ai/release-notes/Kling_4 是脚本渲染，没抓到正文）
- [KO1] 《KLING VIDEO O1 User Guide》2025-12-15 https://kling.ai/quickstart/klingai-video-o1-user-guide
- [K3O] 《Kling VIDEO 3.0 Omni Model User Guide》https://kling.ai/quickstart/klingai-video-3-omni-model-user-guide
- [K3] 《Kling VIDEO 3.0 Model User Guide》https://kling.ai/quickstart/klingai-video-3-model-user-guide
- [KMC] 《Motion Control》用户指南 2026-03-05 https://kling.ai/quickstart/motion-control-user-guide

**矩阵行（Kling 4.0）**：文生 有；首帧 有；首尾帧 有（多关键帧，最多 10 个）；主体参考 有（Elements / 最多 7 个主体）；参考视频·动作 有；参考视频·运镜 有；**深度图视频 / 白模视频 有（官方原话「White-model and depth-map videos are also supported」）**；姿态/线稿：图像参考里明写接受 wireframes、storyboards，姿态骨骼视频没提（不明）；v2v 有（编辑、restyle）；显式相机参数 无（4.0 博客没提；Motion Control 的「Matches Image」档可用提示词写运镜）。
**矩阵行（O1 / 3.0 Omni）**：文生 有；首帧 有；首尾帧 有（「Generation with only an end frame is not supported for now.」）；主体参考 有；参考视频·动作 有；参考视频·运镜 有；结构控制 不明（没提）；v2v 有（Transformation、Video Restyle）；显式相机参数 无。
**矩阵行（Motion Control 2.6 / 3.0）**：只做「一张人物图 + 一段动作视频」；动作 有；运镜 有（Matches Video 档连运镜一起照搬）；其余不适用。

**官方原话**

- Kling 4.0 参考上限 [K4-1]：「Kling 4.0 supports up to 15 combined reference assets in a single generation, including: **Image references**: Up to 10 images, including subject images, character turnarounds, image grids, storyboards, and wireframes. These can define character appearance, product details, composition, lighting, and visual style. **Video references**: Up to 5 videos, with a combined duration of up to 30 seconds. Videos can guide performance, movement, camera direction, and narrative pacing. **White-model and depth-map videos are also supported.** **Subject references**: Up to 7 subjects, including up to 3 video-based subjects.」
- 分工 [K4-1]：「Each reference should have a specific purpose: Character reference: Face, clothing, identity. …… Scene reference: Layout and atmosphere. Style reference: Lighting, color, visual treatment. Video reference: Motion, camera movement, pacing.」「Use a reference video to guide pacing, shot composition, and camera movement, then introduce your own characters, products, or other assets」
- 关键帧与时长 [K4-1]：「Kling 4.0 supports up to 10 flexible keyframes, allowing you to define important visual states at different points on the timeline.」「native video generation from 3 to 30 seconds」。编辑：「The full model supports up to five video inputs in an editing task, including one primary video, with a combined duration of up to 30 seconds.」
- previs 的直接说法 [K4-1] 用例表：「Pre-production｜Turn storyboards and visual references into concept videos and scene previews.｜Previsualization, concept development」（它说的是「用 Kling 做预演」，不是「拿预演当输入」；拿白模当输入的只有上面那一句。）
- O1 的视频参考 [KO1]：「You can upload a 3-10s video as a reference to generate the previous/next shot within the same context. Or with text, images, or elements, create a completely new scene referencing actions or camera movements in the video.」模板：「Reference Video for Camera Movements：Take [@Image] as the start frame. Generate a new video following the camera movement of the [@video]」；「Reference Video for Actions：Animate the character in [@Image 1] with the same motion as the character in the [@Video]」；「Generate Next Shot：Based on [@Video], generate the next shot: [describe shot content]」。
- O1 的 v2v [KO1]：「Changing Angle or Composition：Generate [another angle/composition, e.g, close-up, wide shot] in [@Video]」「Video Restyle：Change [@Video] to [Style words……] style」「Change [@Video] to the style of [@Image1]」。
- O1 / 3.0 Omni 的数量 [KO1][K3O]：「Supports uploading 1–7 reference images or elements in the input area.」「When a video is provided, a total of up to 4 images/elements can be uploaded. If no video is provided, up to 7 images/elements can be uploaded.」3.0 时长：「In VIDEO 3.0 and 3.0 Omni……increasing the single-generation duration to 15 seconds.」
- Motion Control [KMC]：「By default, the video will be generated through "Character Orientation Matches Video", and the character's movements, expressions, camera movements, and orientation will follow the motion reference. Other details can be controlled via prompts.」「When you choose "Character Orientation Matches Image"……the character's movements and expressions will follow the motion reference, and the orientation will align with the character orientation in the reference image. Camera movements and other elements can be customised through prompts.」
- Motion Control 对动作视频的要求 [KMC]（和白模人偶直接相关）：「**Real human actions are recommended, while certain stylized humanoid or humanoid body proportions can be recognized.**」「Add the character image, ensuring the proportions match those in the video for optimal results.」「Match the character's full-body/half-body in the image reference with the full-body/half-body in the motion reference.」「Upload a single character motion reference. For motion reference with two or more characters, the motion of the character occupying the largest portion of the frame will be used for generation.」「The action video must be a single continuous shot……Please avoid cuts, shot changes, or camera movements; otherwise, the video may be truncated.」「The supported duration for uploaded action videos is 3–30 seconds, and the generated video duration will match the length of the uploaded video.」「The short edge must be at least 340px, and the long edge must not exceed 3850px.」

---

## 4. Google：Veo 3.1 与 Gemini Omni Flash（Flow）

出处：
- [G-1] Gemini API《Video generation》https://ai.google.dev/gemini-api/docs/video （现在只剩一页导航：推荐 Omni，Veo 3.1 Preview 已下线）
- [G-2] Gemini API《Generate and edit videos with Gemini Omni Flash》https://ai.google.dev/gemini-api/docs/omni
- [G-3] Gemini API《Veo》https://ai.google.dev/gemini-api/docs/veo
- [G-4] Flow 帮助《Learn about Google Flow models & supported features》https://support.google.com/flow/answer/16352836
- [G-5] Flow 帮助《Create videos in Google Flow》https://support.google.com/flow/answer/16353334 ；《Edit videos & build scenes》https://support.google.com/flow/answer/16935718

**现状**：[G-1]「The Veo 3.1 Preview in the Gemini API has been shut down.」（2026-10-22）「migrate to Gemini Omni Flash (`gemini-omni-1.2-flash`) or the GA models available through the Gemini Enterprise Agent Platform」。Flow [G-4]：「You can use a range of Google Flow features powered by Omni Flash 1.2 or Veo 3.1 Lite.」「On December 5, 2026, Veo 3.1 Fast, Veo 3.1 Quality, and Omni Flash 1.1 will be retired.」「On November 5, 2026, Veo Extend was retired.」

**矩阵行（Veo 3.1）**：文生 有；首帧 有；首尾帧 有；主体参考图 有（≤3 张，必须 8 秒）；参考视频·动作 无；参考视频·运镜 无；结构控制 无；v2v 无（Flow 表里明写 Veo 3.1 各档「Unsupported: Video to Video editing」）；显式相机参数 无（API 没有；Flow 的 camera 是编辑模式）。
**矩阵行（Gemini Omni Flash 1.2）**：文生 有；首帧 有；首尾帧 有（3–10 秒）；主体参考图 有（≤6 张）；参考视频 有，但**官方说是用来保外观的**，不是动作/运镜参考；结构控制 无；v2v 有（上传 ≤15 秒视频对话式编辑）；显式相机参数 无。

**官方原话**

- Veo 3.1 [G-3]：「**Frame-specific generation**: Generate a video by specifying the first and last frames.」「**Image-based direction**: Use up to three reference images to guide the content of your generated video.」「Provide images of a person, character, or product to preserve the subject's appearance in the output video.」参数表：「`durationSeconds`……Must be "8" when using extension, reference images or with 1080p and 4k resolutions」。延长：「Use Veo 3.1 to extend videos that you previously generated with Veo by 7 seconds and up to 20 times.」「Gemini API only supports video extensions for Veo-generated videos.」（不能拿自己的白模视频去延长。）
- Flow 的支持表 [G-4]：Veo 3.1 Lite：「Frames to Video: First」「Frames to Video: First and last」「Ingredients/References to Video：8s videos only」「Unsupported features in Veo 3.1 - Lite：Video to Video editing；Extend videos」。Omni Flash 1.2：「Text to Video / Frames to Video / Ingredients/References to Video / Video to Video editing……3 to 15s video length」（有订阅）。
- Flow 参考图的建议 [G-5]：「For the best results, provide subject or product references on a plain or segmented background.」「Make sure location and style references don't contain extra subjects, unless that is your creative intent.」
- Omni Flash [G-2]：「Omni processes text, image, and video inputs to generate synchronized video and native audio up to 15 seconds long.」「using up to 6 reference images to keep characters and objects consistent across shots」（「up to 3 images per character for up to 2 characters」）。
- **Omni 的参考视频不是动作参考** [G-2] Limitations：「**Reference videos work best for visual likenesses** (any audio in a reference video is ignored) and are only supported when generating a new video, not when editing or extending an existing video.」「Videos from 11 to 15 seconds support 1 reference video (up to 3 seconds long), while videos from 3 to 10 seconds support up to 3 reference videos (up to 3 seconds each).」「Referencing or reasoning across multiple videos is not supported.」
- Omni 的编辑 [G-2]：「Upload your videos (up to 15 seconds long) using the Files API to edit them with Gemini Omni Flash.」「Uploaded and model-generated input videos for editing must be 15 seconds or less.」提示词建议：「When editing a specific aspect of the video, include "Keep everything else the same" to maintain visual consistency.」首尾帧：「First and last frame interpolation……supports videos from 3 to 10 seconds.」默认多镜头：「By default Omni Flash will try to create a video with a few different shots.」要单镜头得写「In a single continuous shot / No scene cuts」。
- 白模/previz：Google 这几页都**没有**提 3D、白模、深度、姿态。Omni 的 `task` 取值只有 `text_to_video / image_to_video / reference_to_video / edit / extend`。白模只能走两条：渲染图当首帧/首尾帧；或把白模视频当「待编辑视频」让它重绘（官方没给这种用法的例子，效果不明）。

---

## 5. Runway

出处（官方帮助中心 help.runwayml.com，走 Zendesk 接口读的正文）：
- [R-1] 《Aleph 2.0 Prompting Guide》2026-06-30 https://help.runwayml.com/hc/en-us/articles/52150503729171
- [R-2] 《Creating with Edit Studio》2026-08-24 https://help.runwayml.com/hc/en-us/articles/51683104370451
- [R-3] 《Creating with Gen-4.5》2026-08-13 https://help.runwayml.com/hc/en-us/articles/46974685288467
- [R-4] 《Using reference media to guide your generations》2026-11-03 https://help.runwayml.com/hc/en-us/articles/52963720640275
- [R-5] 《Using 3D models in Runway》2026-11-03 https://help.runwayml.com/hc/en-us/articles/57074952895635
- [R-6] 《Performance Capture with Act-Two》2026-10-22 https://help.runwayml.com/hc/en-us/articles/42311337895827
- [R-7] 《Creating with video to video on Gen-3 Alpha and Turbo》2026-11-16 https://help.runwayml.com/hc/en-us/articles/33350169138323
- [R-8] 《Creating with Gen-4 Video》2026-10-28 https://help.runwayml.com/hc/en-us/articles/37327109429011
- [R-9] 《Creating with Minimax H3》2026-11-01 https://help.runwayml.com/hc/en-us/articles/54046029551379 （Runway 平台上的第三方模型）

**矩阵行（Gen-4.5）**：文生 有；首帧 有；首尾帧 无（「Keyframes – Animate Frames app」另算）；主体参考图 无（Gen-4.5 只收文字和一张图；References 是 Gen-4 Image 的功能）；参考视频 无；结构控制 无；v2v 无；显式相机参数 无（Gen-3 的 Camera Control 已随 Gen-3 下线）。
**矩阵行（Aleph 2.0 / Edit Studio）**：纯 v2v 编辑模型。输入视频 2–30 秒；保留原视频的运动、构图，改你要改的。动作/运镜 = 原视频自带（等于「全继承」）；结构控制 无专门接口。
**矩阵行（Act-Two）**：表演视频 → 驱动角色图或角色视频（动作 有；用角色视频时运镜来自角色视频）。

**官方原话**

- Gen-4.5 [R-3]：「Gen-4.5 currently offers Text to Video and Image to Video control, with support for additional inputs coming soon.」规格：2–10 秒，720p，24/25 fps。
- Gen-3 的 v2v、Camera Control、Keyframes 已下线 [R-7]：「This feature is no longer available. Gen-3 Alpha was retired on July 8, 2026, and Gen-3 Alpha Turbo was retired on July 30, 2026. The following replacements are available now: Text to Video – Gen-4.5；Image to Video – Gen-4.5；Keyframes – Animate Frames app；Video to Video – Edit Studio Aleph 2.0」
- Aleph 2.0 是什么 [R-1]：「Aleph 2.0 is Runway's in-context video editing model. **Edit one frame and Aleph 2.0 modifies the rest of your video to match** — changing only what you ask for while preserving everything else: background, lighting, and surrounding details.」「Effective prompts typically include two key elements: An action verb……(such as add, remove, change, replace, re-light, and re-style)；A description of your desired transformation」「Restyle：Apply a new visual style to your footage — whether that's a film look, an art style, or a distinct aesthetic.」
- Edit Studio 的流程和限制 [R-2]：「Single edit generates an image based on a selected keyframe still from your video. Use this mode when you want precise control over how the edit looks before it's applied across the video.」「Keyframes are optimized to maintain the composition.」「In addition to your text prompt, you may also include a reference image to guide characters, products, objects, or styles.」关键帧可用 Nano Banana Pro / GPT Image 2 / Gen-4 Image 生成。上传视频要求：「Be longer than 2s, shorter than 30s」「Be between 480p and 1080p」「Use between 24fps and 30fps」「Contain ≤ 10 cuts/shot changes」。「Extra motion is a text prompt that accompanies keyframe edits. It's useful when your edit requires specific motion that wouldn't happen on its own or doesn't exist in the original video.」
  - 对白模的含义（我的推论）：Aleph 2.0 的「改一帧、整段跟着改」正好是「白模视频 + 一张转写实的关键帧」的接法；官方没有白模例子。旧版 Aleph（Gen-4 Aleph）的「generate new angles」等说法这次没在官方页面看到原文，第三方说它已在 2026-07-30 从 API 下线（转述，fuser.studio / flami.pro）。
- **Runway 直接吃 3D 模型（.glb）当参考图/首帧** [R-5][R-4]：「You can add a 3D model wherever you'd add a reference image. It shows up as a picture of the model from one angle」「In Tool mode, add a 3D model wherever you'd add a reference image. Turn the model to the angle you want and snap an image of it. That image goes in the reference slot, and the generation uses it like any other reference.」「Select the Reference slot for images, or the first frame slot for video」「Choose a view: Default, 3/4, Front, Left, Right, Back, Top or Bottom. For an exact angle, drag the model into position, scroll to zoom and select Capture current view.」
  - **官方对「灰模质感被带进成片」的说法** [R-5]：「**The rendered view carries the object's shape, proportions and angle, not its lighting. Describe the lighting in your prompt or add a style reference so the result doesn't look like a plain render.**」
  - 限制 [R-5]：「Only .glb files, exported as a single file with embedded textures.」「**Rigged and animated models won't upload, so for a rigged character export a static .glb for each pose you need.**」它是单个物体的转台视角，不是场景和机位编排。
- Act-Two [R-6]：「By providing a driving performance of someone acting out a scene and a character reference (image or video), Act-Two transfers the movement to your character」「Using a character video will use the camera, character, and environmental motion within the video in the completed generation. Using a character image will automatically add camera and environmental motion.」「Feature a single character in the video」，最长 30 秒。
- Gen-4 Video [R-8]：「The input image establishes the visual starting point of the entire generative process and acts as the first frame of your output video.」5 或 10 秒。

---

## 6. Luma（Ray 3.2 / Ray 3.14 Modify / Ray2 Modify）

出处：
- [L-1] Luma Learning Center《Ray 3.2 Video to Video》2026-05-27 https://lumalabs.ai/learning-center/articles/ray-3-2-video-to-video
- [L-2] Luma API 文档《Modify Video》（Ray2 / Ray Flash 2，页面注明「Updated 4 months ago」，并提示新 API 在 Luma Agents API）https://docs.lumalabs.ai/docs/modify-video
- [L-3] 官方新闻《Introducing Modify Video》https://lumalabs.ai/news/introducing-modify-video

**矩阵行（Ray 3.2 Modify）**：纯 v2v。文生 无；首帧/首尾帧 不适用（它用「关键帧」= 贴在源视频某一帧上的改好的图，最多 64 张）；主体参考 走关键帧；参考视频·动作 有（Motion / Bodies+Poses）；参考视频·运镜 有（Motion 低档主要锁运镜）；**结构控制 有（官方把 Motion、Structure、Poses/Blocking 做成可调的滑杆和开关，等于内置的深度/姿态控制，不用自己喂控制图）**；v2v 有；显式相机参数 无。
（Ray 3 系列的文生/图生/首尾帧生成这次没读到官方页，Luma Agents API 文档站 docs.agents.lumalabs.ai 当时打不开，记「不明」。）

**官方原话**

- 定位 [L-1]：「Ray 3.2 is not a text-to-video model. It is not an image-to-video animator. It is not an extender. Ray 3.2 starts with a source video and returns a re-imagined version of that same clip: same duration, new look, new material, new environment」「Instead of starting from a blank prompt, you begin with real motion, real framing, real edits, and real timing.」用途里写了「turn rough source material into a more finished visual direction」。
- 三个输入 [L-1]：「Source video (Required)；Keyframes (Optional with prompt)；Prompt (Optional with keyframes)」「the output duration always matches the source duration, up to a maximum of 20 seconds. There is no duration parameter.」
- **关键帧 = 把白模帧先转写实再贴回去** [L-1]：「You can export a few frames from the source, edit them with 3rd party software like Photoshop or Nuke, or edit them directly in Luma with any image editing model like Uni-1, Nano Banana, GPT Image, then feed them back into Ray 3.2 at the same original source-frame indexes. Ray 3.2 uses those anchors to interpolate the look across the rest of the shot.」「Ray 3.2 supports up to 64 keyframes at arbitrary source-frame indexes.」「with this system — especially when you're using multiple keyframes — your settings often matter more than your prompt.」
- 提示词写终态，不写命令、不写时间 [L-1]：「Your prompt should describe the target end state. Do not write commands. Do not describe the transformation process. Do not describe what happens over time.」「Avoid "no," "not," "without"……Negation can bias the model toward the thing you are trying to exclude.」收尾句：「Preserve all other elements including subject identity, pose, and lighting.」风格迁移模板：「[Scene description] rendered as [target style]. Preserve composition and motion.」
- **Motion 滑杆（1–9）** [L-1]：「Low (around 1) — broad strokes……In practice it mostly locks onto your camera move……Ideal when you want the camera nailed but want freedom in how things move within the frame.」「High (around 9) — dense capture.」「Overlapping movement drops out. When two moving things cross or pass in front of each other, that overlapping movement tends to be lost.」「Closeness preserves detail. A subject that fills more of the frame and moves less holds its movement far better than something small and fast.」
- **对占位物/3D 物体的直接说法** [L-1]：「**It loves gradients. Motion responds to gradients of color and light rather than flat shapes. If you drop a placeholder object into a scene (a stand-in for a creature or prop), give it shading or a gradient — a flat, single-color blob gives weaker motion control than a shaded one. 3D objects work naturally here, because their lighting creates gradients on its own (even rough lighting helps).**」
- **Structure 滑杆（1–9，越大越贴原片）** [L-1]：「Low (around 1–3) — very soft and loose. The model works from soft blobs: a rough sense of where things sit in the frame relative to one another, with little read on the camera.」「High (around 8) — tight on the subject……anything more than a few feet back drops away」「Top (around 9) — whole-frame hold. The model holds onto every shape, angle, and edge across the entire frame」「Override it with keyframes. Even at the top setting you can fight the hold in specific areas with keyframes.」「The system does not notice color at all」（说的是 Structure 不看颜色）。
- **Poses 与 Blocking**（Blocking 这一档官方直接叫 pre-vis 级）[L-1]：「Poses gives you the full performance. It carries every actual movement」「**Blocking is for looser motion blocking. Blocking is the broader pose mode (think block-out or pre-vis level) that captures only the general back-and-forth of a body rather than every limb. It's useful when your performance is a rough stand-in and you'd rather the model generate natural motion than follow your rough puppeteering exactly.**」「Poses-only is powerful. With just Bodies + Poses on (Motion and Structure off), the model focuses purely on the person you're driving……it's quite good at inferring the camera move from how a body moves.」「Cramped spaces. You don't drag in walls, furniture, or other clutter as noise — only the body.」
- Bodies / Faces [L-1]：「Bodies locks the overall body: silhouette, build, proportions」「Turn Bodies off when you want to change the body type itself.」（人偶比例不想带进成片就关 Bodies。）「Turn Faces off when……you are replacing the character entirely……keeping Faces on can fight the swap and pull the old face back into the result.」
- 组合建议 [L-1]：「"I need the camera nailed but the character can be loose" suggests low Motion (around 1) for a strong camera lock plus low Structure (1–2) to keep the character free」「Push Motion to keep the motion and keep Structure low, and you can — for example — keep a camera move and a performance while giving a character an entirely new silhouette.」
- 旧档位怎么对应 [L-1]：「Structure is the old Adherence scale, reversed.」「Reimagine 2 ≈ Motion off, Structure off, Bodies + Poses, Face on.」「Bodies + Poses with Structure at the top is close to the old Adhere (maximum adherence); Structure around 1 lands closest to Reimagine 3.」
- Ray2 Modify 的三档 [L-2]：「a) Adhere — The output adheres very closely to the source video. This is ideal for subtle enhancements, minor retexturing, or applying a light stylistic filter」「b) Flex — The output flexibly adheres somewhat to the shapes, characters, and details of the source video.」「c) Reimagine — The output adheres much more loosely to the source video. This setting is best for fundamentally changing the world and style to something entirely new, even transforming the characters or objects into completely different forms.」参数：`mode: adhere_1…3, flex_1…3, reimagine_1…3`；「first_frame.url: optional (but preferred) provide the first frame of the modified video (to guide it)」；ray-2 最长 10 秒、ray-flash-2 15 秒、100 MB。
- 发布文里对 previs / 低模的说法 [L-3]：「Transform the look of a scene while keeping its motion and framing intact. Turn a garage into a spaceship, shift from day to night, or **evolve low-poly footage into cinematic realism**.」「Extract full-body, facial, or lip-sync motion from any video clip and drive new characters, props, or camera-blocked paths in perfect sync.」「Whether you're working on previs, pitch decks, or final renders, you'll never have to start from scratch again.」
- 矛盾（转述，未核对）：第三方 prompt-architects.com 说 Luma 自己的材料里关键帧上限有 16 和 64 两种说法；我读到的官方学习中心文章写的是 64。

---

## 7. Hailuo / MiniMax

出处（MiniMax 开放平台，中文站）：
- [M-1] 《视频生成》（MiniMax-H3）https://platform.minimaxi.com/docs/guides/video-generation
- [M-2] 《创建视频生成任务》V2 接口 https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create
- [M-3] 《H3亮点功能示例》https://platform.minimaxi.com/docs/guides/video-prompt
- [M-4] 旧 V1 接口：文生视频 https://platform.minimaxi.com/docs/api-reference/video-generation-t2v 、首尾帧 …/video-generation-fl2v 、主体参考 …/video-generation-s2v
- [R-9] Runway 帮助中心《Creating with Minimax H3》（Runway 的说法，供对照）

**矩阵行（MiniMax-H3，即 Hailuo 3.0）**：文生 有；首帧 有；首尾帧 有（还支持只给尾帧）；主体参考图 有（≤9）；参考视频·动作 有；参考视频·运镜 有（官方表：「参考角色、动作、镜头、风格、声音或剪辑节奏」）；结构控制 官方接口无（开源侧有 VideoX-Fun 的 MiniMax-H3-Fun-Controlnet-Union，见 §1.3 [FUN-1]）；v2v 有（文档称可「视频编辑」，没给独立规则）；显式相机参数 无（旧模型有运镜指令）。
**矩阵行（Hailuo 02 / 2.3，V1 接口）**：文生 有；首帧 有；首尾帧 有（仅 Hailuo-02）；主体参考 有（S2V-01，仅一张人脸图）；参考视频 无；结构控制 无；v2v 无；**显式运镜指令 有（15 种 `[指令]`）**。

**官方原话**

- H3 的三种生成方式 [M-1]：「文生视频｜Prompt」「图生视频｜Prompt + 首帧图片和/或尾帧图片｜控制视频的开始或结束画面」「全能参考生成｜Prompt + 参考图片、视频或音频｜参考角色、动作、镜头、风格、声音或剪辑节奏」。输出 768P / 2K，4～15 秒。
- 输入条件 [M-1]：「首/尾帧入口：图片：0、1、2 张」「全能参考入口：图片：≤ 9 张……视频：≤ 3 段；单段时长 [2, 15] 秒；总时长 ≤ 15 秒……音频：≤ 3 段……混合输入的总上限是 12 个文件」「视频单个 50 MB」。
- **互斥** [M-2]：「**图生视频与多模态参考生视频互斥**：content 中出现 `reference_image` / `reference_video` / `reference_audio` 任一 role，就不能再出现 `first_frame` / `last_frame`（反之亦然），二者不可混用。」支持「图生视频-尾帧：`text` + 1 张 `image_url`（`role=last_frame`）」。
- 示例提示词 [M-1]：「人物参考视频1的动作，表演街舞，人物参考图1 图2」。[M-3]：「图2作为固定人物参考……图1作为镜头分镜与节奏参考。」
- Runway 对 H3 的描述 [R-9]（第三方平台的官方帮助页）：「Video references — add up to 3 videos to guide motion, camera movement, or scene structure; combine with image references to replace a character in the reference video while preserving the original camera motion」「Note: Keyframes cannot be combined with reference inputs.」
- 旧模型的运镜指令 [M-4]：「对于 `MiniMax-Hailuo-2.3`、`MiniMax-Hailuo-02` 和 `*-Director` 系列模型，支持使用 `[指令]` 语法进行运镜控制……支持 15 种运镜指令：左右移: [左移], [右移]；左右摇: [左摇], [右摇]；推拉: [推进], [拉远]；升降: [上升], [下降]；上下摇: [上摇], [下摇]；变焦: [变焦推近], [变焦拉远]；其他: [晃动], [跟随], [固定]」。首尾帧：「模型名称。可用值：`MiniMax-Hailuo-02`。」主体参考：「主体类型，当前仅支持 `character` (人物面部)」「目前仅支持单张图片」。
- 白模/previz：MiniMax 这几页**没有**提白模、深度、姿态。

---

## 8. Higgsfield

出处（官方博客）：
- [H-1] 《Cinema Studio 2.0》2026-02-17 https://higgsfield.ai/blog/cinema-studio-guide
- [H-2] 《How to Make Cinematic AI Videos (Full Guide)》（Cinema Studio 3.5 / 4.0）https://higgsfield.ai/blog/cinema-studio-3.5-full-tutorial
- [H-3] 《The Most Reliable AI Video Generators in 2026》https://higgsfield.ai/blog/most-reliable-ai-video-generators-2026 （只下载了，没细读）

- **它是聚合平台 + 自家的「导演面板」**。官网导航里列的视频模型 [H-1]：Seedance 2.5、Seedance 2.0、Kling 3.0、Kling 4.0、Veo 3.1、WAN 2.6、Grok Imagine 1.5、Gemini Omni Flash、MiniMax H3；图像模型：Nano Banana、Flux 2、Seedream 5、GPT Image 2.6 / 2、Ideogram 4.5。所以「支持哪种控制」取决于选的底层模型，矩阵不单列。
- Cinema Studio 自己加的控制 [H-1]：「True Optical Simulation: Full control over the rig build (camera settings). Select specific camera sensors, choose your lens glass (e.g. Cooke), and set your focal length (8mm to 50mm).」「Deterministic Motion Control: Select specific camera movements (Pan Right, Tilt Up, Zoom In) to choreograph exactly how the shot evolves.」「Start & End Frame Precision……You can upload specific Start and End frames」「Aperture Control」。这些是**预设项**（机身、镜头、焦段、光圈、运镜名），不是真正的相机外参。
- 「Hero Frame First」[H-1]：「by perfecting your still image before you animate, you ensure that lighting, composition, and character details are locked in.」
- **3D Scene**（从一张图进入可走动的 3D 场景再挑机位）[H-1]：「You can now enter your image as a 3D Scene and explore it spatially: move within the environment, adjust perspective, and refine composition directly without leaving the scene.」「You will enter the 3D scene space, where you can move the image across the three axes and choose the key frame you want.」（是「图 → 3D → 换机位截图」，不是导入自己的 Blender 场景。）
- 限制 [H-1]：「6-shot maximum；1–12 seconds per shot；1080p」「End frame becomes unavailable when characters are used in: Auto multi-shot mode / Manual multi-shot mode」。
- 白模/previz：没有提导入 3D 白模或参考视频做 blocking 的说法（[H-2] 里只出现一句创作者建议「learn lenses, lighting, blocking and editing」）。

---

## 9. 顺带几家

**LTX-2 / LTX-2.5（Lightricks，开源）** —— 有结构控制，官方点名 Blender
- 出处：[LTX-1]《IC-LoRA》使用指南 https://docs.ltx.io/open-source-model/usage-guides/ic-lo-ra ；文档索引 https://docs.ltx.io/llms.txt （Union Control、Motion Control 各有专页，没细读）。
- 「IC-LoRAs (In-Context LoRAs) are specialized adapters for LTX that condition video generation on a reference input, like an existing video clip or a control signal like a depth map.」「Control-type IC-LoRAs (Union Control, Motion Control) require an extracted control signal — a depth map, pose skeleton, edge map, or motion trajectory. The quality of these signals directly impacts results.」索引页：「Union Control IC-LoRA：Guide LTX-2.5 video generation with depth, canny, or pose extracted from a reference video」「Motion Control IC-LoRA：Direct object motion……with sparse motion tracks you draw」。
- **深度图来源，官方原话**：「Depth Maps｜Tools: Depthcrafter；**Blender/3D software - For synthetic depth renders**」「Use consistent depth range across all frames；Ensure smooth temporal transitions (avoid flickering)；Match resolution to target generation resolution」。姿态：「Format: Typically 17-18 keypoints for body skeleton rendered as visual overlay」。
- 强度：「`attention_strength` — Global strength scalar (0.0 to 1.0)」「Soft depth guidance: Set `attention_strength` to 0.6 for depth IC-LoRA to get approximate spatial structure while allowing the model more creative freedom」「Foreground-only pose control: Use a spatial `attention_mask` that's 1.0 on the character region and 0.0 on the background」；控制太死时「Reduce `attention_strength` to 0.5-0.8」。参考片段「25 fps is standard for most adapters」。提示词只写画面风格、别提控制类型（转述，搜索摘要）。
- 矩阵行：文生 有；首帧 有；首尾帧/关键帧 不明；主体参考 不明；参考视频·动作 有（pose）；运镜 间接（depth）；结构控制 **有（depth / canny / pose / 稀疏轨迹）**；v2v 有（IC-LoRA v2v、retake）；显式相机参数 无。

**Moonvalley Marey** —— 官网四个控制
- 出处：[MV-1] 官网首页 https://www.moonvalley.com/ （docs.moonvalley.com 打不开）。
- 「POSE TRANSFER：Use reference images or performance inputs to guide timing and intent, then apply it to any subject」「CAMERA CONTROL：Create cinematic camera moves using just a single image. Marey transforms any 2D scene into a 3D environment so you can direct the camera as if you're on set.」「MOTION TRANSFER：Pull motion from any reference video and apply it to new subjects or scenes. Marey keeps the timing and energy intact while giving you the freedom to change everything else.」「TRAJECTORY CONTROL：……Just draw a trajectory for any element」。
- 矩阵行：动作参考 有；运镜参考 有（Motion Transfer）+ 单图 3D 相机控制；结构控制 不明；其余不明。输入规格没查到官方页。

**Vidu（生数）**
- 出处：[V-1] 开放平台文档 https://platform.vidu.com/docs/reference-to-video （页面是脚本渲染，只从页面数据里读到零散字段）。
- 读到的官方字段：「Reference to Video：Create videos that align with reference subjects—like characters, objects, and environments—using the world's first Multi-Entity Consistency feature.」「Start End to Video：Create dynamic videos using just the first and last frame images」「You can upload up to 7 reference images」「resolutions of first and last frames should be similar (ratio between 0.8-1.25)」。模型选项里有 Vidu Q4 Preview、Q2 Pro、Q2、Q1。
- 转述（搜索摘要，未核对原文）：q2-pro 的参考可含 2 个视频主体；Q4 Preview 参考图到 15 张；首尾帧是独立接口 `start-end2video`，没看到和参考同用。
- 矩阵行：文生 有；首帧 有；首尾帧 有；主体参考 有（≤7）；参考视频动作/运镜 不明；结构控制 无；v2v 不明。

**Pika**
- 出处：[P-1] 官网 FAQ https://pika.art/faq 。
- 「Open Pikaframes and add two to five still images in the order you want them to appear. Choose the timing and describe how you'd like one frame to turn into the next. Pika generates the motion between them.」（Pika 2.5；即多关键帧插值。）
- 矩阵行：首帧 有；首尾帧/多关键帧 有（2–5 张）；其余不明。

**Sora 2（OpenAI）** —— 已停
- 转述（搜索摘要，没读到 OpenAI 原页）：视频生成指南上的弃用横幅把 Videos API 和所有 Sora 2 模型的终止日期定在 2026-09-24；`input_reference` 是首帧图；characters 用短参考视频建角色。现在不用考虑。

**HunyuanVideo 1.5（腾讯，开源）**
- 出处：[HY-1] README https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5 。只有 T2V 和 I2V（`--image_path`「Path to reference image (enables i2v mode)」）；README 提到衍生的 OmniWeaving（多模态组合）。官方没有深度/姿态控制。
- 矩阵行：文生 有；首帧 有；其余 无/不明。

**HappyHorse 1.x（百炼）**
- 出处：[W3-4] 百炼选型页。`happyhorse-1.1-t2v`（文生）、`-i2v`（首帧）、`-r2v`（参考图像生视频），3–15 秒；`happyhorse-1.0-video-edit`（「通过文本指令对已有视频进行风格转换、元素替换等编辑操作」，720P/1080P，3–15 秒）。没有首尾帧、参考视频（和 models.md 一致）。

---

## 10. 把白模图转写实常用的图像模型（官方对「保持构图/位置」的说法）

| 模型 | 官方怎么说 | 出处 |
|---|---|---|
| **Nano Banana 2.1 / Pro（Gemini 图像）** | 有专门的「草图变成品」模板：「Upload a rough sketch or drawing and ask the model to refine it into a finished image.」「Turn this rough [medium] sketch of a [subject] into a [style description] photo. Keep the [specific features] from the sketch but add [new details/materials].」风格迁移模板：「Preserve the original composition but render it with [description of stylistic elements].」局部编辑：「Keep everything else in the image exactly the same, preserving the original style, lighting, and composition.」参考图上限：「mix up to 14 reference images」（2.1：10 张物体 + 4 张人物；Pro：6 物体 + 5 人物 + 3 风格）。「Control the Camera: Use photographic and cinematic language」。没有深度/姿态输入。Nano Banana 2.1 还支持视频当输入出图（「Video-to-image generation」）。 | [NB-1] https://ai.google.dev/gemini-api/docs/image-generation |
| **Qwen-Image-Edit 2509 / 2511** | 2509：「**Native Support for ControlNet**: Including depth maps, edge maps, keypoint maps, and more.」「multi-image input also supports commonly used ControlNet keypoint maps—for example, changing a person's pose」「native support for commonly used ControlNet image conditions, such as keypoint control and sketches」。2511：「mitigate image drift, improved character consistency, integrated LoRA capabilities……strengthened geometric reasoning ability」「generating new viewpoints can now be done directly with the base model」「Improved Multi-Person Consistency」。另：VideoX-Fun 有「Qwen-Image-2512-Fun-Controlnet-Union……Canny, Depth, Pose, MLSD, Scribble」[FUN-1]。**这是唯一官方明写原生吃深度图的图像编辑模型。** | [Q-1] https://modelscope.cn/models/Qwen/Qwen-Image-Edit-2509 ；[Q-2] https://modelscope.cn/models/Qwen/Qwen-Image-Edit-2511 |
| **FLUX.2 / FLUX 3 Image / FLUX.1 Kontext（BFL）** | FLUX.2：「Reference multiple images simultaneously - up to 8 via API, up to 10 in the playground.」「Replace people with animals while keeping proportions perfect.」FLUX 3 Image 有**框选布局**：「Tell FLUX 3 where each element goes. Draw a box, describe what belongs in it, and the model composes the image around your layout.」「Every box is `[top, left, bottom, right]` in integers from 0 to 1000」；编辑写法：「Keep everything else in the image — composition, other elements, lighting, background — exactly unchanged.」Kontext 官方现在写「For new projects, we recommend FLUX.2」。API 文档里没有深度/canny 控制页。 | [B-1] https://docs.bfl.ml/flux_2/flux2_image_editing ；[B-2] https://docs.bfl.ml/flux_3/flux3_image_bounding_boxes ；[B-3] https://docs.bfl.ml/flux_3/flux3_image_layout ；[B-4] https://docs.bfl.ml/kontext/kontext_image_editing |
| **Seedream 5.5（火山）** | 「支持文生图、单图生图和多参考图生图，并进一步增强多轮编辑一致性」「最多输入 10 张参考图」「增强多轮编辑中主体特征、构图和未编辑区域的一致性。每轮编辑时，将上一轮生成结果作为输入，并通过提示词明确本轮需要修改和保持不变的内容。」示例：「保持人物身份、面部特征、视线、发型……姿态、蓝色背景、构图和画面风格不变。」没提线稿/深度/白模。 | [S-1] https://www.volcengine.com/docs/82379/2833740 |
| **gpt-image 2.6（OpenAI）** | 「For edits, say "change only X" and list the details to preserve, such as identity, geometry, layout, lighting, or labels.」「For precise local edits, also identify saturation, contrast, arrows, camera angle, and surrounding objects that must remain unchanged.」「Assign roles to references. Identify each input by number and purpose」；`markup`：「On edits, upload a transparent PNG overlay with the same pixel dimensions as the first input image.」人物：「Describe body framing, relative scale, gaze, and interaction with objects.」没有深度/姿态输入；没提 3D 渲染当输入。 | [O-1] https://developers.openai.com/api/docs/guides/image-prompting?model=gpt-image-2.6 |
| **Runway 的 3D 参考** | 见 §5：.glb 转台截图当参考图/首帧；「The rendered view carries the object's shape, proportions and angle, not its lighting. Describe the lighting in your prompt or add a style reference so the result doesn't look like a plain render.」 | [R-5] |

---

## 11. 跨家汇总：官方文档里和「白模该怎么做」「白模会怎么翻车」直接相关的话

（每条都是上面各节里的官方原话，这里只归类。）

**哪几家把白模 / 3D / previz 写进了官方文档**
- **Seedance 2.5**：正式任务「白模参考/渲染」，分粗粒度、细粒度两种 [SD25-2][SD25-3]。
- **Wan 3.0**：正式任务「白模参考 / 渲染｜提示词 + 白模视频｜写实化重渲染的视频」[W3-3]。
- **Kling 4.0**：一句「White-model and depth-map videos are also supported.」[K4-1]。
- **Luma Ray 3.2**：占位物要有明暗、「3D objects work naturally here」、Blocking =「block-out or pre-vis level」[L-1]；发布文「evolve low-poly footage into cinematic realism」[L-3]。
- **LTX-2.5**：深度图工具列了「Blender/3D software - For synthetic depth renders」[LTX-1]。
- **Runway**：能传 .glb，但只当「某个角度的参考图/首帧」[R-5]。
- 没提的：Google（Veo / Omni）、MiniMax H3、Higgsfield、Vidu、Pika、Hunyuan、HappyHorse。

**白模做多细**
- Seedance 2.5：「简单建模（粗粒度）参考效果较好，建议仅用简单几何体拼接表示人物/物体/动物等」；「白模视频主体建议仅保留躯体，避免包含【四肢/翅膀】等涉及精细运动的元素；如已包含，需补全其动作序列，以防止渲染结果出现四肢僵化。」细粒度用于「建模完整，重点解决重渲染」。
- Wan 3.0 的官方示例走的是另一头：细的 clay render + 「除了材质与颜色之外什么都不许改」，并说明「原白模的卡通圆润造型在写实化后保留其体块轮廓与比例」。
- Luma：粗的替身表演用 Blocking，让模型自己补自然动作；要逐肢体跟随用 Poses。
- Kling Motion Control：动作视频「Real human actions are recommended, while certain stylized humanoid or humanoid body proportions can be recognized.」人物图与动作视频的比例、全身/半身要对上。
- → 两种思路并存，没有哪家做过并排对比：Seedance 官方明说粗的更好；Wan 给的是细白模逐帧上色的例子。

**要不要上颜色区分角色**
- Seedance 2.5 官方示例直接用颜色指认：「将 [图片 1] 中穿灰色衣服的男人对应 [视频 1] 中的红色模型、[视频 2] 中的红发少女替换 [视频 1] 中的绿色模型 2」；sd25-pe：「每个几何体必须单独映射到最终主体或道具。」
- Wan 3.0 的示例是「纯白 clay render」，没有分色；多人例子靠参考图各自锁外观并写「不要混淆、不要互换服装发色」。
- Luma：Motion 看明暗梯度，「a flat, single-color blob gives weaker motion control than a shaded one」；Structure「does not notice color at all」。

**渲染里不能带的东西**
- Seedance 2.5：「不含【轨迹线】【坐标线】【相机 cone】等干扰信息的视频，否则容易泄露到生成后的视频中。」
- Wan 3.0 负向清单：「禁止出现线框网格线、坐标轴、操作界面与任何 UI 元素」。
- Runway Aleph 2.0：输入视频的切镜数有上限（「Contain ≤ 10 cuts/shot changes」）；Kling Motion Control 的动作视频必须单镜头。

**灰模质感带进成片**
- Runway：「The rendered view carries the object's shape, proportions and angle, not its lighting. Describe the lighting in your prompt or add a style reference so the result doesn't look like a plain render.」
- Wan 3.0：负向里写「禁止出现残留的白模区域、局部未上色的纯白物体、材质丢失的灰模块……塑料玩具与 CG 假质感」；动作参考的例子里要写「最终画面正常彩色」。
- Seedance 2.5 模板：「不采用其中的白模外观、材质和场景」「不采用原有灰模材质、空白背景和制作标记」。
- Luma：贴写实关键帧（最多 64 张）来定外观；提示词写终态并正面描述。

**参考视频把机位锁死 / 想只借一部分**
- Seedance / Wan 3.0 / Kling 4.0 / MiniMax H3 都是「用提示词说明这段视频只提供什么」；Seedance 明写「生成任务不得默认继承参考视频中的人物身份、服装或完整场景」并要求写「不采用什么」。
- Luma 是唯一把「运镜 / 形状 / 肢体」拆成独立滑杆的：Motion≈1 只锁运镜；Poses-only 只带人不带场景。
- Kling Motion Control：「Matches Video」连运镜一起照搬；「Matches Image」运镜改由提示词写。
- Gemini Omni 相反：参考视频「work best for visual likenesses」，不是动作参考。

**首帧/首尾帧和参考能不能同用**
- 不能：Wan 3.0（互斥）、MiniMax H3（互斥）、Runway 平台上的 H3（「Keyframes cannot be combined with reference inputs」）。
- 能：Wan 2.7 参考生视频（首帧 + 参考图/视频 ≤5）；Kling O1/3.0 Omni/4.0（一个输入框里 @Image 当首帧，再 @Video 借运镜）；Seedance 2.x 用提示词把某张参考图指定为首帧/尾帧（「@图片N作为首帧。」），严格一致才用 first_frame 接口。
- Luma Ray 3.2：关键帧就是贴在源视频帧号上的图，天然和源视频同用。

**多人**
- Kling Motion Control：动作视频里有多人时「the motion of the character occupying the largest portion of the frame will be used」，一次只驱动一人。
- Runway Act-Two：「Feature a single character in the video」。
- Luma：「Overlapping movement drops out. When two moving things cross or pass in front of each other, that overlapping movement tends to be lost.」
- Seedance 2.5：靠「每个几何体单独映射」+ 颜色指认；Wan 3.0：「两人各自的外观锁定各自的参考图，不要混淆、不要互换服装发色」。
- Gemini Omni：参考图「up to 3 images per character for up to 2 characters」。

**输入视频规格（渲白模时照这个出）**
| 模型 | 时长 | 帧率 | 分辨率 / 大小 | 其他 |
|---|---|---|---|---|
| Wan 3.0 | 单个 1–15 秒，合计 ≤15 秒，≤5 段；输入+输出 ≤30 秒 | ≥16 fps | 单边 240–4096，≤100 MB | mp4 / mov |
| Seedance 2.5 | 单个 2–30 秒（编辑 4–30 秒），合计 ≤30 秒，≤10 个 | 24–60 fps | 480p–4K，≤200 MB，宽高比 0.4–2.5 | 不能有真人脸 |
| Kling 4.0 | ≤5 段，合计 ≤30 秒 | 不明 | 不明 | |
| Kling Motion Control | 3–30 秒，单镜头 | 不明 | 短边 ≥340，长边 ≤3850 | 一个人 |
| Runway Aleph 2.0 | 2–30 秒 | 24–30 fps | 480p–1080p | ≤10 个切点 |
| Luma Ray 3.2 | ≤20 秒，输出等长 | 不明 | 不明 | 关键帧 ≤64 |
| Gemini Omni | 编辑 ≤15 秒；参考视频每段 ≤3 秒 | 不明 | 不明 | |
| MiniMax H3 | 单段 2–15 秒，合计 ≤15 秒，≤3 段 | 不明 | 边长 256–5760，≤50 MB | H.264 / H.265 |
| VACE（开源） | 约 5 秒（81 帧） | 16 fps 训练 | 480p / 720p | 灰 127 = 待生成 |
| LTX-2.5 IC-LoRA | 不明 | 25 fps 为准 | 控制图分辨率对齐输出 | |

---

## 12. 官方说法里互相对不上的地方

1. **Kling Motion Control 同一页**：一边写动作视频要「Avoid cuts and camera movements in the motion reference」，一边写默认档「the character's movements, expressions, camera movements, and orientation will follow the motion reference」。读法：带运镜的参考视频能用（运镜会被照搬），但官方不推荐，可能被截断。
2. **Wan 2.7 与 3.0**：2.7 的参考生视频可以叠首帧（「多主体参考+首帧控制」）；3.0 明确互斥。选型页却把 3.0 列为首尾帧和参考的首选。要「首帧 + 参考」只能回 2.7，或在 3.0 里把那一帧当普通参考图。
3. **白模粗细**：Seedance 2.5 官方说粗的好、别带四肢；Wan 3.0 官方示例是带完整人物动作的细白模逐帧上色。两家没有共同结论。
4. **参考视频是什么**：Seedance / Wan / Kling / H3 把参考视频当动作、运镜参考；Gemini Omni 官方说它「work best for visual likenesses」。同名功能，含义相反。
5. **Seedance 首帧 + 参考**：接口上 first_frame 是独立任务；官方又给了「提示词里把参考图指定为首帧」的绕法，并承认后者不保证严格一致。
6. **Luma 关键帧数**：官方学习中心写 64；第三方转述 Luma 另有页面写 16（未核对）。
7. **video-film-maker 的笔记 vs 官方**：`refs/practical/models.md` 写 Seedance 2.5 没有参考视频；官方有（见文首）。

## 13. 没查成的

- Kling 4.0 发布说明页（kling.ai/release-notes/Kling_4）和 Vidu 文档是脚本渲染，只拿到博客和零散字段；Kling 4.0 白模/深度图怎么喂（要不要在提示词里声明、深度图的格式）官方只有一句话。
- Luma Ray 3 / 3.14 的生成侧（首尾帧、角色参考）和 Luma Agents API 文档站当时连不上。
- Moonvalley 文档站、Pika 文档、Sora 官方页没读到原文。
- WebFetch 工具对多数域名报「Unable to verify if domain is safe」，全程改用 curl（国外站走代理，中途断过几分钟）。所以引语都是我从页面正文里直接摘的，不是小模型摘要。

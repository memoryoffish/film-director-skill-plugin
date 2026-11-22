# 表演的出处摘录（2026-11-16 调研）

[表演](../../../stages/3-generation/acting.md) 引的原文。下面标「原文」的，都是对照下载下来的页面核对过的；标「转述」的是转述，没有逐字核对。

## Wan 3.0 官方

- 提示词指南：https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide
  - 原文，任务类型表：「运动参考 | 提示词 + 含动作 / 表情 / 运镜 / 特效的参考视频 | 复刻参考运动信息的新视频」；「视频时序迁移：把参考视频的动作、运镜、特效当成时序信号迁移到新角色或新场景，节奏照搬，主体、环境自由换。」
  - 动作参考的范例（打斗），要点：人物的长相、发型、体型和服装照参考图，全程一致；只取参考视频 1 的动作，顺序、幅度、速度、停顿和发生时机照它，它的人物外观不带进来（原文见指南的运动参考范例）。
  - 原文，打斗范例的总则：「全片是一条不中断的连贯格斗链，每一镜的结束姿势就是下一镜的起始姿势，人物站位、重心朝向、受力方向必须延续，不得瞬移、不得凭空换位……先破坏对手重心，再借其惯性方向施加杠杆」。
  - 原文，追逐范例：「【角色动作逻辑】女子的优势是轻、快、反应敏捷、擅长借环境和变线；男子的优势是力量、预判、压迫感……争夺不是胡乱撕扯，而是围绕光球展开的"抓、挡、卸力、换手、借力、转身、闪避、反制"。」
  - 原文，短剧范例：「动作要像随手插进来的日常，不要慢动作亮相、不要摆造型。」
  - 原文，口型范例：「【口型与神态】……说话时伴随自然的眨眼、轻微的头部点动和呼吸感，面部微表情需与台词中的关怀、回忆情绪完美契合。」
  - 原文，综合范例：「将军形象参考图1，面部神态参考图2」。
- 使用指南：https://help.aliyun.com/zh/model-studio/wan3-video-generation-guide
  - 原文：「运镜/动作参考：传入参考视频，复刻其运镜方式或动作编排」；「音频参考：传入音乐或语音，生成与节拍/语调同步的舞蹈、口型动画」。
  - 原文，视线范例：「面部朝向画面左侧斜前方画外导演方向」。
- API：https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference （media 里 reference_image、reference_video、reference_audio 可以组合）。

## 论文

- EmoTrace-Bench（arXiv 2610.15452，2026-10，中国传媒大学和快手 Kling 团队）：https://arxiv.org/abs/2610.15452
  - 原文，表 E.4，Wan-3.0 的「情绪和强度都对」：
    - 只写情绪词 81；只写脸 50，只写身体 47，脸和身体 66；
    - 脸写成变化 69；只写场景 25，场景加反应 75；只写事件 31，事件加反应 84；
    - 用氛围写 31，用镜头术语写 12。
  - 原文，表里的 X2（原因和反应同框），Wan-3.0：6.7，12 个模型里几乎最低。
  - 原文，摘要：明确写出人物的情绪反应，比只写事件或场景跟得更好；多加情绪线索、多用镜头语言，不一定更好。

## 别家官方指南

- Sora 2：https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide.md
  - 原文：「Each shot should have one clear camera move and one clear subject action. Actions work best when described in beats or counts」；「Actor takes four steps to the window, pauses, and pulls the curtain in the final second」；「stitching together two 4 second clips in editing instead of generating a single 8 second clip」。
- Kling：https://kling.ai/blog/kling-ai-motion-prompts-guide
  - 原文：「Describe the hand path, facial expression, timing, body orientation, and who receives the gesture」；「Multi-Shot structure to separate setup, action, and reaction」。
- Runway Gen-4 提示词指南（help.runwayml.com）：转述，写具体动作，不写抽象情绪（「The man extends his arm to shake hands, then nods politely」）；只用正面写法。
- Kling Motion Control、Runway Act-Two、Luma Ray3 Modify：转述，都要求表演视频一镜到底、人物清楚、脸看得见、机位尽量不动。

## 从业者（单一来源，转述）

- Flick（引 Jaime Yao）：打斗每一招写接触、力、反应、下一招：https://flick.art/blog/how-to-choreograph-a-fight-scene-with-ai
- seedance2pro：两人互打一条生成最不可靠，拆成出招、受击、回应三条再剪：https://seedance2pro.io/blog/seedance-2-fight-scene-guide
- FlashBoards：库里肖夫剪法；声音也算「第二个镜头」：https://flashboards.yaroflasher.com/learn/editing/kuleshov-effect/
- Michael Lanham：平静的脸、他看到的东西、回到同一张脸：https://micheallanham.substack.com/p/writing-the-edit-the-new-ai-filmmaking

## 同一账号下的后备模型（转述）

- wan2.2-animate-move（把参考视频的动作和表情迁到一张人物图上）、wan2.2-animate-mix（替换视频里的主角，保留场景和光）：https://help.aliyun.com/zh/model-studio/wan-animate-move-api 、https://help.aliyun.com/zh/model-studio/wan-animate-mix-api

## 待实测的三种做法

从 [表演](../../../stages/3-generation/acting.md) 挪来，都还没在片子里试过。

- **真人表演驱动**：拍一段真人表演当参考视频，人物的样子用参考图锁住，模型照着演（Wan 3.0 官方的「运动参考 / 动作参考」）。
  - 官方写法：「参考图1、图2的人物角色，仅参考视频1的视频动作……人物复刻参考视频中的全部动作、姿态、节奏和停顿……参考视频只用于动作控制，不继承其人物外观。」
  - 表演视频一镜到底、人看得清、机位不动、脸看得见（别家同类工具的共同要求）。
  - `scripts/wan.py` 已经能传参考视频，换写法就行。要查：参考图的背景和姿势会被照搬（实测过）；参考视频里有真人脸会不会被审核拦（没测）。
  - 后备：同一账号的 wan2.2-animate（move 把动作迁到人物图上，mix 替换视频里的主角）。
- **表情先做成图**（图像模型见 [gpt-image](../../practical/gpt-image.md)）：首帧平静、尾帧是要的表情，同机位、同姿势，只改脸，用首尾帧生成。两张差别要小，差别大了中间会偷偷叠化。也可以在参考图里单放一张「神态参考」，但脸可能锁在那个表情上。
- **参考音频带语气**：真人读台词、读出停顿和情绪，录音当参考音频，写「用音频1的音色说：『……』」。`scripts/wan.py` 现在不传音频，要先补上。

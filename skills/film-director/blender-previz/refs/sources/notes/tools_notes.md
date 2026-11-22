# 工具：3D 预演 / 白模 → AI 出片的产品、插件和节点

> 底稿说明：调研时的逐项笔记，结论汇总在 [../research.md](../research.md)。

调研日期 2026-11-17。只查了网页、GitHub、官方文档和一条 YouTube 文字稿；没碰 B 站和 X（X 帖子只记了链接，见文末）。

标注约定：
- 没标的 = 我读到了原页面 / 原 README / 原文档。
- 「转述」= 只看到搜索摘要或别人的引用，没看到原文。
- 「最近更新」GitHub 项目取 `gh api` 查到的最后一次 push 日期和最新 release；今天往前两个月是 2026-09-17，早于它的标「偏旧」。
- 星数是 2026-11-17 查的。

---

## 0. 速览表

| 工具 | 类型 | 交给模型的信号 | 接哪些模型 | 许可 / 价格 | 最近更新 | agent 能不能脚本驱动 | 对我们 |
|---|---|---|---|---|---|---|---|
| scenario-labs/skills 里的 `scenario-blender-blockout` | 给 agent 用的 Blender 白模 skill（bpy 脚本 + 规范 + 实测结论） | 白模 playblast（带身份色）+ 交接单（色标、剪辑表、角色表）+ 风格板 | Seedance 2.5、MiniMax H3 Max、LTX 2.3（都实测过） | MIT；出片那一步走 Scenario 付费 | 2026-11-16，3,855 星 | 能，无头 Blender 直接跑 | **最值得照抄**：人偶四档、身份色、检查项、提示词写法都有实测 |
| Blockout（wassermanproductions） | 桌面白模预演应用 | 参考视频 + 深度视频 + 法线视频 + 每个机位点的静帧 + 俯视走位图 + 按模型写的提示词 + ComfyUI 工作流 | Seedance 2.0、Veo 3.1、Kling 2.x、LTX 2.3、Wan 2.2；图像模型 4 个 | Apache-2.0，免费 | push 2026-08-05，release 2026-07-11（偏旧），196 星 | 能，自带 MCP（33 个工具），但应用要开着 | 导出包结构和「按模型的 profile」值得照做 |
| CozyClay | 浏览器白模预演（开源） | 首尾帧 + 白模片段 + 机位 + 提示词；深度、法线、OTIO | Seedance / Kling / Veo 为主 | AGPL-3.0，免费 | 2026-11-17，v3.2.2（11-07），1,917 星 | 能，`npx cozyclay mcp` 和 `cclay live` 命令行 | 导出规范（纯平、无叠加物）和动作质检值得参考；AGPL 不能把代码并进我们的东西 |
| 即梦 Clay Renderer 插件（官方） | Blender（转述：也有 Maya）插件 | 白模渲染视频，一键传到即梦当参考视频 | Seedance 2.5 | 插件随账号给；出片按积分 | 2026-09 初已有（官方页注明 09-04 核对过文档） | 不能，要手点 + 网页 | 说明 Seedance 官方就把「白模视频当参考」当正路 |
| 即梦短剧工作室 3D 导演台 | 平台内置 3D 片场 | 白模动态参考（人形白模 + 摄影机起止点） | Seedance 2.5 | 订阅 + 积分；搭建和预演不耗视频算力 | 2026-10-26 上线（转述） | 不能 | 产品形态参考 |
| LibTV 3D 导演台 | 画布里的 3D 节点 | 机位视角截图（当参考图）；多机位截图模拟运镜 | 画布里的模型（文中提 Seedance 2.0） | 订阅 | 2026-06 初上线 | 不能 | 只出静帧，不出参考视频 |
| Higgsfield for Blender + 3D Jutsu | Blender 插件 + 浏览器 3D 工作台 | 灰模预演视频当参考；视口直接出片 | Seedance 2.5（插件 Video 页），站内其他模型 | 插件免费，生成扣站内积分 | 插件 2026-08-25 发布（转述），官方博客 2026-10-28 | 半能：MCP Bridge 连 Claude 等，云端推理 | 流程参考；封闭、绑积分 |
| Scenario for Blender | Blender 插件（开源） | 视口/相机 playblast 当参考视频；首帧；风格图；文字→灰模布局 | Seedance、MiniMax、Runway Aleph、Gemini、Grok 等 v2v | GPL-3.0；生成扣 Scenario 积分 | 2026-11-13，v0.13.1（11-12），1,038 星，标「Experimental」 | 能，本地 MCP + 无头入口 | 文档里有一句关键限制（首帧和参考片段不能同用，见 4.6） |
| Krea Seedance Studio | 网页工作台 | 3D 机位路径渲染 → 当视频参考 | Seedance 2.5 / 2 系列 | Krea 订阅 | 文档在线，上线日期没查到 | 不能 | 只管机位，不管人物走位 |
| Intangible | 浏览器 3D 画布 | 厂商称「把整个 3D 场景数据交给模型」（未证实） | Luma、Kling、Seedance、Wan、Omni、Veo | 免费 150 积分；$25/月起（年付） | 博客 2026-10-26 | 有 MCP（转述，v0.1.0，2026-08-10 登记） | 人手摆场景的备选 |
| ArtCraft | 桌面 AI 创作 IDE（开源） | 3D 舞台构图、摆姿势的人偶 → 出图/出片 | 自带 62 个模型目录（Seedance 到 2.0、Kling 到 3.0、Veo 3.1…） | MIT 或 Apache-2.0 | 2026-11-17，v0.41.1（11-07），41,341 星 | 没看到无头接口 | 人手工具；模型目录偏旧一代 |
| World Labs Marble | 生成 3D 世界 + 走机位录像 | 机位飞行视频（mp4） | 自己不出片，录像拿去别家当参考 | 订阅 | Marble 1.1（2026-04，转述） | 录像只在网页，API 不出视频（转述） | 场景一致性备选；不出人物 |
| LTX-2.5 Layout-to-Render IC-LoRA | 开放权重控制 LoRA | 灰模 playblast（管机位和物体位置）+ 转好风格的首帧（管外观） | LTX-2.5-22B | LTX-2.x community licence，权重要申请 | 2026-10-22 | 能，ComfyUI 工作流和 Python 命令行 | 本地可跑的「白模 → 成片」正路之一 |
| SolarRenderer | 开放权重，4 步出片 | 结构视频（灰模、语义图、骨架、深度、人体网格、铅笔分镜）+ 可选首帧 | MiniMax-H3 | 代码 Apache-2.0，权重 MiniMax H3 Community License | 2026-10-30，396 星 | 能，`scripts/render.py` | 本地 H3 路线的备选 |
| Yedp Action Director | ComfyUI 节点（3D 视口） | 7 种通道：OpenPose、深度、Canny、法线、灰模着色、Alpha、带贴图 | 任何吃 ControlNet 的工作流（README 原话）；接 Wan VACE 这类控制视频是我的推断 | MIT | 2026-11-13，V9.3，387 星 | 场景存在工作流 JSON 里，但烘焙在浏览器前端做 | 走「深度 / 姿态控制」路线时最省事的出通道工具 |
| ComfyUI 原生 Load3D | 内置节点 | image、mask、normal、lineart、camera_info、recording_video | 下游任意 | 随 ComfyUI | 随核心更新（没查具体日期） | 录像要在前端操作 | 轻量；没有独立深度输出口 |
| MCP for Blender / Blender Lab MCP | 让 agent 操作开着的 Blender | 不直接出信号，是搭场景的通道 | — | MIT / 官方实验项目 | 2026-11-15（34,765 星）/ v1.0.3 2026-09-11（转述） | 能 | 我们用无头 bpy 就够，交互调试时可用 |
| EL4CTEO/blender-skills | 28 个 Blender agent skill | 不直接出信号 | — | MIT | 2026-11-13，1,807 星 | 能 | 建模、绑定、动作重定向、渲染的现成脚本 |

---

## 1. 专门产品：摆 3D 场景 → 交给图像/视频模型

### 1.1 scenario-labs/skills：`scenario-blender-blockout`（给 agent 的白模 skill）

- 链接：https://github.com/scenario-labs/skills （目录 `skills/dcc/blender/scenario-blender-blockout/`：`SKILL.md`、`references/{cast,handoff,levels,contract,audits,examples,plugin}.md`、`scripts/bx_blockout.py`、`bx_kits.py`、4 个示例场景脚本）
- 是什么：Scenario 公司开源的 agent skill，专门讲「文字或参考图 → Blender 白模 → playblast 当视频模型的参考片段」。搭场景、相机、走位、检查是纯 bpy，可以无头跑；只有最后出片那一步走 Scenario 的付费接口。
- 许可 MIT；3,855 星；最后 push 2026-11-16。针对 Blender 5.2。
- 输出四样：场景、锁定的相机时间线、playblast、交接单（hand-off sheet）。
- 对我们：和我们要做的事几乎一样（agent 写 Blender 脚本搭白模再交给视频模型）。可以直接读它的脚本和规范；它的出片步骤我们换成自己的 Wan 3.0 / Seedance 调用。它的实测只覆盖 Seedance 2.5、H3 Max、LTX 2.3，没有 Wan 3.0 和 Kling。

它给的结论都带原文，下面是最要紧的几条（都是我读到的原文）：

**白模对什么有发言权**
> "the blockout has full authority over motion and layout and none over look. Ambiguity ruins the pass; crudeness does not: a bent lamppost comes back as a snake, loose limb blocks as extra people, an unmarked car driving backward."

**人偶四档（`cast.md`）**

| 档 | 是什么 | 模型照抄什么 | 模型自己编什么 |
|---|---|---|---|
| `capsule` | 带圆球头的彩色胶囊，没有四肢；走路时加一点上下起伏和左右摆 | 位置、身高、速度、朝向 | 身体、四肢、步态、衣服 |
| `featured` | 胶囊 + 两三个标志性特征（护目镜、兜帽、手里的灯笼），各自上色 | 上面那些 + 谁是谁 | 身体、四肢、步态 |
| `jointed` | 13 个刚性彩色部件，脚会踩地迈步 | 上面那些 + 四肢的时间和姿势 | 表面、脸、衣服 |
| `mannequin` | 蒙皮到骨架的灰色假人，躯干上身份色 | 同上 | 表面、脸、衣服 |

按模型选哪档（原表）：

| 视频模型 | 主角 | 群演 |
|---|---|---|
| 紧跟参考片段动作的参考视频模型（Seedance 2.5） | `featured` 胶囊；人物离得远时用 `capsule` | `capsule` |
| 把每个替身当真东西读的 3D-to-video 模型（H3 Max） | `jointed` 或 `featured`；近景要检查前后顺序 | `capsule`、`jointed` |
| 只吃一张图的 render-to-real 模型（LTX 2.3） | 都行，首帧带身份 | `capsule` |

原因（原文）：
> "a reference-video model follows the clip's motion closely, limbs included. In our film work a rigged walk loop came back as sliding feet; in the test below, stepped jointed runners came back upright with short walk-like strides even with a running clause in the prompt, while capsules came back running."

什么时候才用带骨骼的假人：
> "A `mannequin` is the choice when the limb motion itself must come from the blockout (a dance, a fight beat, a specific gesture) and the model copies limbs well. Give it real animation then: a rigged mannequin walked by procedural keys is still a procedural walk."

**对比实验（Sky Islands，2026-10）**：同一个场景（五个孩子跑过索桥，4 个镜头，12 秒）用四种人偶各搭一遍，风格图、角色表、提示词都一样。原文注明「One take per cell: an indication, not a measurement」。

| 模型 | `jointed` | `capsule` | `featured` |
|---|---|---|---|
| Seedance 2.5，12 s | 身体直挺，小碎步，几乎齐步；加了步态句也一样 | 真的在跑（前倾、抬膝、双脚离地、各有节奏） | 同样在跑，并且 5 个人的身份和先后顺序跨 4 个切点都保住 |
| Seedance 2.5，身份 | 保住 | 跟拍镜头里最高的那个占了领头的位置 | 护目镜、围巾、背包、兜帽、手杖都在对的位置 |
| H3 Max 768P | 5 个跑着的孩子，顺序保住 | 一样，没有胶囊形状残留 | 一样，构图比参考更紧 |
| LTX 2.3 720p | 跑着的孩子；有一个背了别人的包 | 身份保住 | 身份保住 |

结论原文：
> "on Seedance the stand-in decides the gait, and features decide whether identities hold with several similar characters; on H3 Max and LTX the style changes little and the usual checks apply."

**颜色（`SKILL.md`、`contract.md`、`levels.md`）**
- 每个主角一个饱和色（红、蓝、绿、黄、紫、青），群演中灰，场景灰度 0.32–0.55，一盏灯，暗背景。原文："An all-gray playblast has lost identity."
- 黑、白、灰、棕不能当身份色（和灰场景分不开）。
- 场景不用鲜艳原色："the set never uses bright primaries (they read as toys and leak)"。
- H3 Max 上试过三套场景配色（按类别给淡色、每类一种灰、接近真实材质的颜色），原文："The model reads a hue as a material hint, so give a hue only where its real-world reading is right, and a hero's color only to something the hero really wears"。
- 颜色只当「标记」不够，要落到衣服上："a color named as a marker only came back as a bare capsule"。
- 朝向：车头用浅色灯块和格栅、车尾暗红；单个方块要标朝向时「red front face, black back, green sides and top」。

**提示词写法（`handoff.md`，针对 Seedance 这类参考视频模型）**
1. 开头把参考视频说成排练录像：
   > "The reference video is rehearsal footage: stand-ins walked the scene so camera, timing and movement could be locked. The final shot replaces every stand-in with the real cast and set. Take from the video only the camera path and framing, the timing of every action, and each element's screen position, path, ground contact and scale. No shape, proportion, silhouette or surface in the video belongs in the final frame."
2. 之后不再出现几何词（box、cone、proxy、mannequin、blockout）。原因：
   > "A prompt that names the proxies' shapes ("the box figure becomes", "each cone is") anchors the model on those shapes and it renders them as they are."
3. 胶囊人例外，只说一次它「不是什么」：
   > "In @video1 each character is a colored capsule stand-in with a ball for a head and no arms or legs: it only marks where that person is, their height, their pace and which way they move. They are real people with natural human motion."
4. 步态句："each foot planted before the other lifts … Their feet never slide, glide or float."
5. 结尾排除句："No blocky placeholder geometry, no mannequin figures, no untextured surfaces."
6. H3 Max 这类模型反过来，要给「替换表」，按形状和颜色说每类替身是什么（"open booths with posts and sloped canopies are food stalls"）。

**风格不用「转好风格的首帧」，用 2×2 风格板**
> "A single restyled frame of the shot carries its own composition and shapes into the video; panels at angles the clip never uses transfer identity without a layout to copy."

**实测到的限制（`handoff.md`「Tested limits」）**
- > "in one audit of 28 renders, 10 to 15 s clips kept the camera and layout, 20 to 30 s clips drifted (lost figures, invented close-ups). Several short captures beat one long one."
- > "A bare gray mannequin playblast was refused by a provider's input screen, and re-encoding did not help; saturated identity colors, or a strong color tint over the whole clip, passed."
- 挑哪一帧去转风格按内容挑，第 1 帧常常是空镜。
- 用视觉模型比对「转风格帧」和「白模帧」时要说明两者本来就该不同，否则它把成功的判成失败。

**检查项**：帧数和分辨率、切点、主体是否在画内、头有没有被挡、离相机太近、穿模、脚和轮子着地、手持抖动幅度；然后每个镜头的首、中、末帧渲一张图人眼看。验收时把 playblast 和成片左右并排（给了 ffmpeg 命令）。

**常见读错**（原文摘）：松散的小方块靠近人物会被读成多出来的人；没标车头的车倒着开；不透明车厢里的人消失；切点那一帧上打关键帧会让动作停住；最后几秒会漂。

### 1.2 Blockout（wassermanproductions/blockout）

- 链接：https://github.com/wassermanproductions/blockout
- 是什么：开源桌面应用（Electron，macOS / Windows），自称「Previs for AI-native filmmaking」。三步：STAGE（放场景和人）、SHOOT（给人和相机打「mark」走位）、DELIVER（按目标模型导出）。
- 许可 Apache-2.0（要保留 NOTICE 署名）；196 星；最后 push 2026-08-05，release `v5.0.0-desktop.1` 2026-07-11，偏旧。
- 定位原文：
  > "It is deliberately **not** a 3D art tool. Grey-box mannequins and vehicles at real-world scale, real lens math, and choreography tools are the whole product. The fidelity target is *unambiguous, not beautiful.*"
  > "A capsule-limbed mannequin that clearly walks from the door to the window, shot on a clearly-35mm dolly move, beats a photorealistic render that took a day."（`docs/DESIGN.md`）
- 导出包（README 原样）：
  ```
  1A_reference.mp4      # the motion reference (deterministic render)
  1A_depth.mp4          # depth pass for ComfyUI control workflows
  1A_normal.mp4         # optional normal pass
  stills/               # frame at every camera mark + first/last + top-down blocking diagram
  prompt.txt            # generated from your actual blocking, tailored per generator
  comfyui-workflow.json # pre-wired depth-conditioning workflow (Wan/LTX profiles)
  metadata.json         # machine-readable marks/lenses/timings
  ```
  另有整场 animatic、contact sheet、给 Blender 的 `.glb`（带动画相机）。
- 按模型的 profile（`src/engine/profiles.ts`，我读了源码）：

  | 模型 | 时长上限 | fps | 吃参考的顺序（`refModes`） | 给用户的提示（`attachHint`） |
  |---|---|---|---|---|
  | Seedance 2.0 | 10 s | 24 | referenceVideo → firstFrame | "Attach the reference MP4 as the motion/video reference and the first-frame still as the image reference." |
  | Veo 3.1 | 8 s | 24 | firstFrame → referenceVideo | "Use the first-frame still as the image input; describe the camera move in the prompt." |
  | Kling 2.x | 10 s | 24 | firstFrame → lastFrame → referenceVideo | "Use first-frame and last-frame stills as start/end frames; the reference video guides motion where supported." |
  | LTX 2.3 | 10 s | 24 | depthVideo → referenceVideo → firstFrame | "Use the depth-pass MP4 as a depth/structure conditioning video (ComfyUI workflow included in the export)." |
  | Wan 2.2 | 8 s | 16 | depthVideo → referenceVideo → firstFrame | "Use the depth or reference video as VACE/control input in ComfyUI (workflow included in the export)." |
  | GPT Image 2 / Nano Banana / Ideogram / Krea 2 | — | — | stills | 用机位点静帧 + 俯视走位图当构图参考 |

  模型版本停在 2026 年年中那一代（没有 Seedance 2.5、Wan 3.0、Kling 4）。
- 自动写的提示词里，吃参考视频的模型统一加这一句（`src/engine/prompt.ts`）：
  > "Use the attached video strictly as a motion reference: match the character blocking and movement, and the camera blocking, movement, and tracking, exactly as shown. The grey figures are placeholders — replace them with the real subjects and world while keeping every move the same."
  注意这句直接说了「grey figures」，和 1.1 里「提示词不要出现几何词」的说法不一致（见 6.3）。
- 标身份的做法（`DESIGN.md` 3.2）：每个东西可以挂标签 = 飘在头顶的文字牌 + 模型本身染色，例子「Label the man "THIEF" (red), the woman "COP" (blue)」。导出时标签有三档：On / Stills only / Off。
  > "often you want them burned into reference stills but not the motion video."
- 光：
  > "Generators read lighting direction and time-of-day from the reference. Keep it simple but explicit"
  所以只给几个预设（Day / Golden hour / Night / Interior warm / Interior cool / Club）加一个主光方向。
- 人偶：代码生成的「articulated capsule mannequins」，Mixamo 兼容骨架，步态是算出来的（"a walk cycle is math, not mocap"）。194 个角色动作、33 条物体路径、39 个经典运镜。
- 资产全是代码生成的灰模，没有外部资产许可问题。
- agent：自带 MCP，33 个工具（`get_state`、`add_entity`、`spawn_choreography`、`apply_camera_move`、`screenshot`…），应用必须开着；`claude mcp add blockout -- node …/blockout-mcp.mjs`。导出是确定性的（同一工程每次逐字节一致）。
- 同作者配套：Motion Previs Studio（https://github.com/wassermanproductions/motion-previs-studio ，Apache-2.0，386 星，push 2026-07-20）反过来做：从一段参考视频里抽姿态、深度、相机运动、遮罩，导出 OpenPose BODY_25 骨架视频和逐帧关键点 JSON，再送进 Blockout 当底图。
- 有没有人晒流程：没找到独立的成片案例。
- 对我们：导出包结构、按模型 profile、标签「只烧进静帧」、俯视走位图这几样可以照做。应用本身是人手工具，更新偏旧。

### 1.3 CozyClay（HaD0Yun/CozyClay，NomaDamas 出品）

- 链接：https://github.com/HaD0Yun/CozyClay ，站点 https://cozyclay.org
- 是什么：浏览器里的开源白模预演，`npx cozyclay` 一条命令起，不要 GPU。Stage（搭景、放人）→ Move（描述动作，agent 写动作规格，浏览器里的确定性编译器逐帧烘焙）→ Shoot（时间线、轨道、镜头）→ Export。
- 许可 AGPL-3.0-or-later；1,917 星；push 2026-11-17；v3.2.2（2026-11-07）。只支持 Chromium。
- 导出：
  > "Keyframe pack (first and last frame, greybox clip, camera, prompt), mp4, depth and normal passes, contact sheet, OTIO cut list."
- 人偶两种：
  > "Add rigged characters, or capsule stand-ins when nobody needs to move a limb."
- 动作质检：
  > "QA checks collisions, foot slide, reach and hand contact before you see it."
- agent：三个入口，应用内 Agent 面板、MCP（`npx -y cozyclay mcp`）、终端（`cclay live status --wait`，JSON 进出）。
- 它的指南页给了几条导出规范（https://cozyclay.org/greybox-to-video/ 和 /seedance-camera-control/，2026-09 更新）：
  > "Keep the export flat: no outlines, no gizmos, no grid, no text overlays. Anything drawn on the frame is something the model may try to keep. A blue selection box on the ground plane can come back as a blue crate."
  > "A textured render or a photo does the opposite. The model tries to keep the wood grain and the shirt too … Grey is not a limitation of the workflow. Grey is the point."
  > "Keep the figure grey so it invents the person instead of preserving a mannequin."
  > "Scale matters more than detail: doors at 2 m, a car at 4.5 m long."
  参考片段 3–5 秒、和成片同画幅、平涂；提示词里不要再用文字描述一遍机位。
- 它对各模型的说法（它引的官方原话我没去官方页核对，算转述）：Seedance 2.5 产品页 "Provides advanced capabilities such as white-model control and green-screen editing…"；Kling Motion Control "Avoid cuts, camera movement, etc.; otherwise, the video may be trimmed."；以及它自己的判断 "None of the top hosted APIs (Seedance, Kling, Veo 3.1, Runway Act-Two, MiniMax) documents a depth or pose control-video input."
- 自述短板：只支持 Chromium；不做写实渲染和布光；很新。
- 对我们：agent 可驱动、在维护。但我们已经有 Blender，主要价值是导出规范和动作质检的思路。AGPL，代码不能并入。

### 1.4 即梦 / Dreamina：Clay Renderer 插件和短剧工作室 3D 导演台

**Clay Renderer 插件（官方）**
- 链接：https://dreamina.capcut.com/seedance/seedance-2-5-blender-model-workflow ，https://dreamina.capcut.com/resource/gpt-6-astra-review （后者有安装步骤，注明依据官方文档、2026-09-04 核对）。官方使用指南在飞书 `bytedance.larkoffice.com/wiki/TrbCwqIZFiblb0kqshZccJ4mndd`（转述，没打开）。
- 是什么：Blender 插件，名字在插件列表里叫「Seedance 2.5 Clay Render & Upload」。N 面板 Dreamina 页签里选来源 Camera（设相机、分辨率、帧范围、保存位置 → Render → Upload to Dreamina）或 Local File。传完即梦网页自动打开，白模视频已经挂成参考输入。
- 官方对它的界定：
  > "It works with a clay render video rather than treating the Blender project itself as the video-generation input."
  > "The documented plugin sends reference video; it does not establish direct FBX, OBJ, GLB, or .blend import, automatic synchronization back into Blender, or a replacement for a physically accurate renderer."
- 官方给的示例提示词：
  > "Use the reference video for camera movement and the positions of the major objects. Turn the blockout into a softly lit architectural concept with pale stone, warm wood, and morning light. Keep the camera path and avoid adding extra buildings."
- 转述：也支持 Maya；中文圈叫「即梦 AI 白模渲染插件」；参考素材上限 30 图、10 视频、10 音频，共 50 个，参考视频合计 30 秒；有第三方示例提示词专门写了「不要白色材质、占位脸、无贴图背景、临时灯光」。
- 对我们：插件只是省掉「导出再上传」，要手点。价值在于确认 Seedance 2.5 官方把白模视频当参考输入。

**即梦短剧工作室 3D 导演台**（爱范儿实测 https://www.ifanr.com/1686343 ，2026-10-29）
- > 「3D 导演台允许创作者先在三维空间中调整角色站位、朝向、道具、机位与运动轨迹。」
- 实测做法：
  > 「先搭一个简单大厅，放入两个人形白模。一个在前，一个站到后方高处，再给摄影机设置起点和终点。它就能作为动态参考放进视频节点，把灰色大厅和人形模型替换成原创服装、石殿、天窗和人物。」
- 「导演台的搭建与预演过程本身不消耗视频生成算力。」另有「智能预演」把多个分镜串起来低成本走一遍。
- 转述：2026-10-26 上线；有道具库、动作库、运镜库；外部模型通过 Blender 白模插件进来；可编辑三维场景靠 720° 全景参考和深度视频。掘金一篇对比文（2026-11-15，像推广稿）说它有「图片生成白模」，抖音官方话题页用的名字是「重制转绘白模」，两者是不是一回事没法确认。

### 1.5 LibTV 3D 导演台（哩布哩布）

- 来源：搜狐转载的短剧新圈测评 https://www.sohu.com/a/1030583709_122571656 （2026-06-01）。没找到官方文档。
- 是什么：LibTV 无限画布里的一个「导演台」节点，进去是三维空间，默认一个机位、一个人物模型；可以上传全景图或让 AI 生成全景当背景，放人物模型、几何模型、群众模型，布多个摄影机（位置、角度、FOV）。有「导演视角」和「机位视角」。
- 交给模型的东西是截图：
  > 「通过截图的方式，将角色人物、场景道具等在空间场景中的信息，转化成更具体的"参考图片"，通过一键发送至画布的方式…」
- 运镜靠多机位截图模拟：
  > 「通过布置多个机位的方式，来手动模拟镜头的运动轨迹，通过连续的场景信息，来让 AI 理解镜头的运动变化。」
- 文中提到一个背景：《牡丹记》团队当时没有这类工具，「只能先用真人演一遍后，再将内容喂给模型」。
- 对我们：它只出静帧参考，不出参考视频，比 1.1–1.4 弱一档。

### 1.6 Higgsfield：Blender 插件和 3D Jutsu

- 链接：https://higgsfield.ai/blog/higgsfield-blender-plugin （2026-10-28），https://higgsfield.ai/blog/higgsfield-3d-jutsu （2026-09-05）
- **Higgsfield for Blender**：7 个页签（Scene Builder、3D Model、Character Animation、Image、Video、Camera、Asset）。Scene Builder 用文字生成真的 Blender 几何体；Video 页「Generate video from your viewport with Seedance 2.5」；Camera 页用手机当虚拟摄影机。要 Blender 5.1+、Windows 或 macOS、Higgsfield 账号，推理在云端。可以通过「Blender Bridge」（`https://bridge.higgsfield.ai/mcp`）让 Claude 等操作打开的场景。发布日 2026-08-25（转述）。
- **3D Jutsu**：浏览器里的 3D 工作台，agent 用灰色替身搭场景，Export 把相机时间线渲成视频当参考。官方四步：灰模预演 → 导出预演视频 → 另外生成人物图和场景图 → 同一个对话里把三者合起来。
  > "The previz provides a reference for the intended camera path, framing, and character behavior, and grey proxies become the real location, wardrobe, and performance."
- 一个值得注意的细节：官方示例里预演人物故意没有手臂：
  > "The character has NO arms and NO hands: none rendered, nothing at the shoulders."
  并且「An invisible camera target is placed separately from the head so the head is always in frame as the camera moves」。
- 素材库：GLB 资产和 Mixamo 角色；导出 MP4、静帧、GLB。
- 有人晒流程（都转述，X 帖没打开）：JSFILMZ「Claude Desktop 通过 Higgsfield MCP 连 Blender → Claude 生成灰模 → 调机位 → 1080p playblast 当 Seedance 2.5 动作参考」；ai-muninn 的作者说是看了这个插件才去做本地版（见 5.4）。
- 对我们：封闭、绑积分。流程和我们一致，可当对照。

### 1.7 Scenario for Blender（scenario-labs/blender-plugin）

- 链接：https://github.com/scenario-labs/blender-plugin ，用户指南 https://blender.scenario.com/
- 是什么：开源 Blender 扩展（Blender 5.0+，README 标「Experimental」），把 Scenario 的图像、视频、3D、PBR、音频生成放进侧栏。和我们相关的三个页签：
  - **Render Video**：
    > "A playblast of your timeline, rendered as a finished clip by a video model that takes a reference video."
    模型列的是「Seedance, Minimax, Runway Aleph, Gemini, Grok and other video-to-video models」。捕获是无声 1280×720。
  - **Blockout**：把文字或参考图变成彩色基本体的灰模布局（收费）。
  - **Camera path planner**：围绕一个静止中心做一个镜头的相机路径。
- 许可 GPL-3.0；1,038 星；push 2026-11-13；v0.13.1（2026-11-12）。安装免费，生成扣 Scenario 的 CU。
- agent：本地 MCP（默认 `http://127.0.0.1:9876/mcp`），有无头入口；`execute_python` 要用户手动开。
- 对我们：插件本身绑 Scenario 计费。用户指南里有一句限制很有用，放在 4.6。

### 1.8 Krea Seedance Studio

- 链接：https://www.krea.ai/docs/user-guide/features/seedance-studio
- 「Control the camera in 3D」四步（官方文档）：
  > "2. Describe the scene, upload a reference, or sketch a layout. The scene agent can build and revise a simple 3D scene for you. 3. Add camera keyframes, then adjust their position, aim, focal length, timing, and easing. Preview the path and set a duration from 1 to 10 seconds. 4. Click Use video to attach the rendered camera path to your Studio prompt, or Export to download it."
  > "Use video renders the flythrough, adds it to the project feed, and attaches it as a video reference for your next generation."
- 只有桌面端；另有镜头设置（焦距 8–100 mm、光圈 f/1.4–f/11）。参考上限转述：Seedance 2.5 共 50 个（30 图），Seedance 2 系列 12 个（9 图）。
- 对我们：只解决机位路径，不解决人物走位。说明「3D 机位飞行视频当 Seedance 视频参考」已经被做成产品功能。

### 1.9 Intangible

- 链接：https://www.intangible.ai/ ，对比文 https://www.intangible.ai/blog/blender-higgsfield-vs-intangible （2026-10-26，厂商自己写的）
- 是什么：浏览器 3D 画布，摆物体、人、环境、相机，再选模型渲染。能导入 GLB、GLTF、DAE、FBX、OBJ、PLY 和高斯泼溅；「Materials are stripped on import, and animation clips do not import」。导出 GLTF/GLB（带动画）、静态 USD、视频和图片；不支持 FBX 导出。
- 接的模型：Luma、Kling、Seedance、Wan、Omni、Veo；后台自动把提示词改成各家的写法。
- 核心卖点是厂商说法，没有独立验证：
  > "A Blender-to-AI workflow passes a flat 2D render of the 3D scene, while Intangible passes the full 3D data of the scene."
  它自己也承认「Some drift between renders is still possible」。
- 价格（该文）：Free $0（150 一次性积分）；Explorer $25/月、Business $50/月（都是年付）。BudgetPixel 写「paid plans from $35 a month」，应是月付价。
- 转述：2025 年年中公测，创始团队来自 Apple、Pixar、Netflix、Google、Unity；VP Land 早期评测说网页慢、渲染靠 Kling；MCP 服务 v0.1.0 于 2026-08-10 登记。
- 对我们：人手摆场景的工具；「完整 3D 数据」到底怎么传给模型没有公开说明。

### 1.10 ArtCraft（storytold/artcraft）

- 链接：https://github.com/storytold/artcraft ，下载 https://getartcraft.com/ （注意组织名是 `storytold`，不是 storyteller-ai）
- 是什么：开源桌面应用（Rust + Tauri），自称「the IDE for interactive AI image and video creation」，「Compose in 2D, stage scenes in 3D」。README 列的 3D 相关功能：3D Image Compositing、Image to 3D Mesh、Character Posing（「Pose characters and set your camera before generating the final shot」）、Scene Blocking with Kitbashing、Character Identity Transfer（「Use a posed mannequin to guide the placement and pose of your character」）。
- 许可 MIT 或 Apache-2.0 任选（商标保留）；41,341 星；push 2026-11-17；v0.41.1（2026-11-07）。
- 模型目录 62 个，但偏旧一代（Seedance 到 2.0，Kling 到 3.0，Veo 到 3.1）；接了 World Labs Marble。
- 没看到无头或 MCP 接口。主要是「摆好构图 → 出图 → 图生视频」，不是参考视频路线。
- 对我们：人手工具，可以看它的人偶和 kitbash 资产怎么设计。

### 1.11 World Labs Marble

- 链接：https://docs.worldlabs.ai/marble/create/studio-tools/record
- Record 功能：在生成的 3D 世界里打相机关键帧、时间线调节奏、Enhance 后下载 mp4。官方提醒：
  > "Currently the trajectory does not persist. You WILL lose the keyframes when you leave the page."
- 只导出视频，不导出相机轨迹数据。转述：录像只在网页端，World API 只给泼溅和网格；网格可导到 Unreal、Blender；Marble 1.1 是 2026-04。没找到「Marble 录像 → Veo / Runway」的成文流程。
- 对我们：解决「同一场戏不同机位场景一致」的另一条路（先有一个 3D 世界，再从里面取机位），但里面没有人物。

### 1.12 其他平台和产品（简记）

| 名称 | 链接 | 要点 | 证据 |
|---|---|---|---|
| BudgetPixel Previs | https://budgetpixel.com/learn/best-ai-previs-tools （2026-10-27，厂商自己的横评） | 一句话生成「clay 3D」预演：按真实尺寸的场景、「your characters as coloured figures with their paths」、相机；Seedance 2.5 拿这段预演当相机、走位、时间的参考。单镜头 4–15 秒，最多 6 个角色 | 读了原文 |
| Flick | https://flick.art/blog/blender-ai-filmmaking （2026-06） | 平台的「Omni Reference」：Blender 片段当视频参考 + Nano Banana 转好的首帧，交给 Seedance；Kling O3 也支持。流程原文见 5.3 | 读了原文 |
| LTX Studio | 同 BudgetPixel 横评 | 站内有相机运动和关键帧，没有 3D 预演这一步 | 转述 |
| Higgsfield Cinema Studio | 同上 | 30 多个运镜预设，没有先看 3D 的步骤 | 转述 |
| Martini（martini.film） | https://www.martini.film/ | 「Step Into Set」一张图约十分钟变成可走动的 3D 环境，人物变人体网格；高斯泼溅上的相机运动工具；有 Blender 导入相机和 MCP；演示用 Kling 2.0 出片 | 转述（官网是纯 JS，没读到正文） |
| Lightcraft Spark Story | https://docs.lightcraft.pro/faq/faq | 浏览器预演（剧本 + 泼溅扫描 + 3D 资产 + iPhone 手持机位），自己不生成视频；$29.95/月 beta；导出说法有出入（FAQ 说 QR 到 Jetset 和 USDZ，别处说 mp4） | 转述 |
| Autodesk Flow Studio | https://www.autodesk.com/campaigns/flow-studio | 2026-08 加了 3D Editor 和多模型 Canvas；导出 MP4、USD、FBX，带相机数据 | 转述 |
| Cuebric | — | 分层深度（2.5D 视差），不是可走动的 3D，没有相机路径导出 | 转述 |
| TapNow | — | 有「3D 片场」「智能预演」「导演台」「Multi Angle」「世界模型」等说法；v2.18.13（2026-09-24）；没找到官方文档 | 转述 |
| Playbook 3D | https://github.com/playbook3d/playbook3d-comfyui-nodes | ComfyUI 节点包最后更新 2025-03-25，21 星，看起来停了；Gumroad 上有「Wan 2.2 Graybox to Rendered Sequence」（Wan 2.2 Fun Control + Flux Kontext depth LoRA） | 元数据我查的，其余转述 |
| video-lab（sbobyn） | https://github.com/sbobyn/video-lab | 本地 Three.js 预演 + ComfyUI；模型表里把「Video from the blockout clip」分成 Seedance 2.5 edit、Kling O1 edit、Wan VACE 1.3B（白模视频当 control frames）；MIT；3 星，2026-11-09 | 读了 README，个人项目 |
| greybox-studio | https://github.com/amirpashasdh/greybox-studio | 浏览器摆白模，导出深度、姿态、遮罩给 ComfyUI；0 星，作者说端到端没测完 | 只看了元数据 |
| Runway / Luma / Kling 自身 | — | 没找到内置 3D 场景或白模编辑器；Runway 自己的 AI previs 指南承认逐帧精确的镜头、走位、时间控制还得靠 Unreal 或 Blender 预演 | 转述 |

---

## 2. 传统 3D 分镜 / 预演工具（有没有 AI 出口）

| 工具 | 能导出什么 | AI 出口 | 现状 | 证据 |
|---|---|---|---|---|
| Previs Pro（Mac / iPad / iPhone） | MP4（带时间线音频）、FCP7 XML | 有：内置 AI 图像和视频生成，「the AI runs on top of frames you composed in 3D — a styling pass over the spatial work」；press kit 列 Wan 2.1、Veo 3.1 Fast、Kling V3（转述） | 3.6.0（2026-10）；$119.99/年或 $359.99 买断，有水印免费档 | 读了 wiki.previspro.com/compare（厂商自己写的） |
| ShotPro（iOS） | .mov 最高 4K | 无 | 最后一次实质功能更新 2020-07 | 同上（竞品说法） |
| FrameForge | 分镜图、视频；深度导出没查到 | 无 | 主版本 v4 是 2019-12；$498.95 | 同上（竞品说法） |
| Storyboarder（Wonder Unit） | 分镜图、导出到 Premiere / FCP / Avid；Shot Generator 可摆 3D 人偶出参考图 | 无 | GitHub 最后 push 2024-03-17，基本停了；3,960 星 | 元数据我查的 |
| set.a.light 3D | 布光图、分镜 | 无 | 付费，有试用 | 转述 |
| Cine Tracer | 截图 / 录屏 | 无（手动截） | Steam 付费 | 转述 |
| Unreal Engine（Sequencer / Movie Render Graph / Metahuman） | 任意通道（beauty、深度、法线、对象 ID）、相机 FBX/USD | 无内置；灰模 playblast 一样可以当参考视频（LTX 模型卡、ComfyUI 官方 README 都把 Unreal 和 Blender 并列） | 活跃 | scenario-labs/skills 里有 Unreal Sequencer skill（转述） |

小结：传统工具里只有 Previs Pro 接了 AI，而且是「在 3D 构图的帧上做风格转换」。其余都要手动导出视频或截图。FrameForge、ShotPro、Storyboarder 都多年没大更新。

---

## 3. Blender 插件和桥

### 3.1 ComfyUI ↔ Blender

| 名称 | 链接 | 能做什么 | 许可 | 最近更新 | 备注 |
|---|---|---|---|---|---|
| ComfyUI-BlenderAI-node（AIGODLIKE） | https://github.com/AIGODLIKE/ComfyUI-BlenderAI-node | 在 Blender 里跑整张 ComfyUI 图，视口或相机当实时输入；深度合成、骨骼摆姿 | GPL-3.0 | push 2025-11-28，release v2.0.0 2025-07-25，**偏旧**（近一年没动），1,594 星 | flick.art 2026-06 的指南还在推荐它 |
| Pallaidium（tin2tin） | https://github.com/tin2tin/Pallaidium | Blender 视频编辑器（VSE）里的生成工作台；SCENE 条（3D 场景）可以直接当参考；2026-07-10 加「3D output type — Mist / Depth Pass」（复制场景、挂 EEVEE Mist 合成通道，生成深度条）；2026-06-27 加「LTX-2.3 3DREAL — video + reference image control」（当前条渲成 control_video，另选一张图当第 0 帧外观参考）；有 ComfyUI、fal.ai 远程适配器，支持 Seedance reference-to-video | GPL-3.0 | push 2026-11-14，1,556 星，更新很勤 | 唯一把「3D 场景条 → 深度 / 参考 → 视频模型」做在 Blender 内部的活跃插件 |
| AI Render（benrugg） | https://github.com/benrugg/AI-Render | Stable Diffusion 渲染，图像为主 | MIT | push 2025-12-28，偏旧，1,234 星 | 对视频没用 |
| Dream Textures | https://github.com/carson-katri/dream-textures | SD 贴图、深度转图 | GPL-3.0 | push 2026-09-17（刚好两个月），8,250 星 | 对视频没用 |
| comfyui-blender-temporal | https://github.com/ismael-joffroy-chandoutis/comfyui-blender-temporal | 把 Blender 的 EXR 深度/法线通道转成 ControlNet 时序条件 | 许可不明 | 2026-07-19，0 星 | 只看了元数据 |
| RunComfy「Blender to ComfyUI AI Renderer 2.0」 | https://www.runcomfy.com/comfyui-workflows/blender-to-comfyui-ai-renderer-2-0-workflow-cinematic-video-output | 现成工作流：Blender 的深度、轮廓、姿态通道 → Wan 2.1 VACE 14B | — | 约 8 个月前 | 转述 |

### 3.2 让 agent 搭场景

| 名称 | 链接 | 要点 | 证据 |
|---|---|---|---|
| MCP for Blender（原 blender-mcp，ahujasid） | https://github.com/ahujasid/mcp-for-blender | 社区版，「Community plugin to control Blender 3D with any LLM of your choice. Not affiliated with the official Blender Foundation.」MIT，34,765 星，push 2026-11-15。2026-09-16 为避免和官方混淆改名（转述） | 元数据我查的 |
| Blender Lab MCP（官方） | https://projects.blender.org/lab/blender_mcp ，https://www.blender.org/lab/mcp-server/ | Blender 基金会实验项目；插件 + 独立 server（stdio + TCP）；v1.0.0 2026-04-27，v1.0.3 2026-09-11，9 月 29 日还有提交；要 Blender 5.1+；26 个工具，一半是无头 `*_for_cli` 版本 | 转述（blender.org 返回 403，没读到） |
| EL4CTEO/blender-skills | https://github.com/EL4CTEO/blender-skills | 28 个 agent skill（建模、绑定、动作重定向、渲染、批处理、QA…），Blender 5.2 LTS+，「Without one [MCP], agents run Blender in the background」。MIT，1,807 星，push 2026-11-13 | 读了 README |
| scenario-labs/skills | 见 1.1 | 另有 `scenario-blender-previs-storyboard`（给导演和剪辑看的 animatic）、`scenario-blender-animation`、`scenario-blender-expert` | 读了 blockout 那个 |

### 3.3 分镜 / 镜头管理插件

- Ubisoft Shot Manager（https://github.com/ubisoft/shotmanager ）：给 Blender 加「镜头」实体和序列编辑。GPL-3.0，219 星，最后 push 2023-08-23，**停更**。
- Storypencil：Blender 自带的 Grease Pencil 分镜插件，二维为主，没有 AI 出口（凭已有知识，没重新核对）。
- 在 scenario 的 skill 里，多机位切换用的是 Blender 原生的时间线 marker 绑相机（`B.bind_cuts`），不需要插件。

### 3.4 一次渲出 depth / normal / canny / OpenPose 的 rig 和脚本

- **toyxyz「Character bones that look like Openpose for blender」**：https://toyxyz.gumroad.com/l/ciojz 。一个摆好姿势的 rig 一次渲出深度、Canny、OpenPose、法线、分割。flick.art 称它是「community-standard rig」。转述：Gumroad 页标题到 Ver_99（Depth+Canny+Landmark+MediaPipeFace+finger+CameraPose），X 上的卡片显示 Ver_101；$0+；当年要求 Blender 3.5+。Gumroad 我这边连不上，没看到页面和许可。
- **Yedp Action Director 的做法**（见 4.2）：在 Mixamo 骨架上挂一个名字含 `pose` / `openpose` 的网格当 OpenPose 火柴人，另挂 `depth` / `depth_f` 网格当男女体型的深度体，渲不同通道时切换显示。这个命名约定可以直接搬到 Blender 里自己做。
- **Blender 自己就能出**：深度用 Z 通道或 Mist 通道，法线用 Normal 通道，线稿用 Freestyle / Line Art，Workbench 引擎出平涂。Pallaidium 的「Mist / Depth Pass」就是这么做的。
- Motion Previs Studio（见 1.2）是反方向：从真实视频里抽 OpenPose BODY_25 骨架视频、深度、相机运动。

### 3.5 Blender 相机轨迹 → 视频模型的相机参数

- 没找到现成的「Blender 相机 → Wan Fun Camera / ReCamMaster / Uni3C 轨迹」专用插件。
- 最接近的在 ComfyUI 这头：**ComfyUI-CameraReference3D**（https://github.com/lovemachine100/ComfyUI-CameraReference3D ，MIT，3 星，2026-07-02）。它的 Camera Trajectory Export 节点能把任意轨迹导成三种格式（README 原文）：
  > "One trajectory → Wan Fun-Camera Plücker embedding (`WanCameraImageToVideo.camera_conditions`), AnimateDiff-Evolved `CAMERACTRL_POSES`, extrinsics JSON."
  其中 `extrinsics_json` 是「Full c2w matrices + hfov/fps/fmul」，注明用途之一是「Blender round-trips」。所以自己写一个 bpy 脚本把相机逐帧 c2w 矩阵导成这个 JSON 是可行的（我的推断，没有试）。项目很小，证据弱。
- **phazei/ComfyUI-Camera-Path**（Apache-2.0，8 星，2026-09-25）：按相机路径用 MoGe 渲一段参考视频，有自己的 JSON 路径格式。只看了元数据。
- Uni3C（kijai/ComfyUI-WanVideoWrapper，6,818 星，push 2026-11-13）吃的是参考视频里的相机运动，所以 Blender 渲一段相机运动的视频就能当输入，不需要轨迹文件（转述 + 我的推断）。
- Blockout 应用会导出带动画相机的 `.glb`；Yedp 能从 `yedp_cams` 目录读 Maya / Blender 导出的 FBX 相机。
- 2026 年的主流做法已经不是导相机参数，而是直接把白模视频当参考（Seedance 2.5、H3、Wan 3.0 hosted、LTX IC-LoRA、Krea、即梦都是这样）。

### 3.6 其他

- **Blender 面部捕捉栈**（thereelstack 2026-11-13 转述一条 X 帖）：MCP for Blender + MediaPipe（52 个 blendshape）+ BlendArMocap（https://github.com/cgtinker/BlendArMocap ，GPL-3.0，1,098 星，push 2025-12-01，偏旧）+ Rhubarb Lip Sync。和白模关系不大。
- **fSpy**：flick.art 提到可以把 Blender 相机对到一张已有的生成图上（反向匹配机位）。

---

## 4. ComfyUI 里直接摆 3D 的节点

### 4.1 原生 Load3D（Load 3D & Animation）

- 文档：https://docs.comfy.org/built-in-nodes/Load3D
- 支持 `.gltf`、`.glb`、`.obj`、`.fbx`、`.stl`。输出口（文档表格）：`image`、`mask`、`normal`、`lineart`（`edge_threshold` 可调）、`camera_info`（LOAD3D_CAMERA）、`recording_video`（「Recorded video (only when recording exists)」）。
- 材质模式：Original、Normal、Wireframe、Lineart。可设 FOV、相机类型、全局光强、背景色或背景图。
- 录像：
  > "Video recording: Allows you to record current 3D view operations as video, allows import, and can be output as recording_video to subsequent nodes"
- 没有单独的深度输出口（第三方文档说深度是材质模式之一，官方页上我没看到）。录像要在前端手动操作。

### 4.2 Yedp Action Director（yedp123/ComfyUI-Yedp-Action-Director）

- 链接：https://github.com/yedp123/ComfyUI-Yedp-Action-Director ；MIT；387 星；push 2026-11-13；V9.3。另有独立桌面版（Windows）。
- 是什么：ComfyUI 里的 3D 视口节点，最多 16 个角色，给角色排 MoCap 动画序列（自动交叉淡化），导入 3D 环境和高斯泼溅，做相机动画，一次烘焙 7 种通道。
- 核心是 Mixamo 兼容骨架：
  > "At its core, this engine is built around a Mixamo-compatible rig."
  读 `.fbx`、`.glb`、`.bvh`。
- 7 个输出（README 表）：

  | 输出 | 说明 | 用途 |
  |---|---|---|
  | POSE_BATCH | 平涂无光的身体部位颜色，含面部关键点 | ControlNet OpenPose |
  | DEPTH_BATCH | 灰度距离图（白近黑远），Near/Far 手动设 | ControlNet Depth |
  | CANNY_BATCH | 黑色网格 + 白色边缘光 | ControlNet Canny / Lineart |
  | NORMAL_BATCH | 相对相机的 RGB 法线 | ControlNet NormalMap |
  | SHADED_BATCH | 带光照的灰模 | 预览或 img2img 风格参考 |
  | ALPHA_BATCH | 黑底白色的角色和道具 | 遮罩、合成 |
  | TEXTURED_BATCH | 带原材质的 RGB | 最终预览 |

- 男女体型：角色卡上有 M / F 开关，「instantly swaps the underlying depth mesh of the character」，同一段骨骼动画换体型。
- 相机：内部打起止关键帧，或者导入 FBX 相机「Maya/Blender Override」。
- 配套节点：**Yedp Blockout**（基本体 + 资产库搭场景，可开关「human silhouette」比例参照，烘焙 Textured / Shaded / Depth / Normal，导出 GLB）；**Yedp Mocap Surgeon**（从视频里用 MediaPipe 抽动作、手修、导出 Mixamo 兼容 GLB）。Blockout 节点里部分模型是 Tim Steer（thebasemesh.com）的 CC0 模型。
- 场景状态存在工作流 JSON 里。烘焙是点视口里的「BAKE V9.3」按钮，前端 Three.js 渲染（「The frontend libraries (Three.js and MediaPipe) are loaded dynamically」），所以纯 API 无头调用大概率不行（我的推断）。
- 对我们：要走「深度 / 姿态控制视频 + Wan VACE」这条路时，它是现成的出通道工具；它的通道设计（尤其 OpenPose 火柴人直接从 3D 骨架出、带面部关键点）可以照着在 Blender 里做。

### 4.3 ComfyBlockout（spiritform/comfyblockout）

- 链接：https://github.com/spiritform/comfyblockout ；没有许可文件；9 星；push 2026-07-02（偏旧）。另有独立版 ComfyBlockoutApp（MIT，2026-10-21，0 星）。
- 三个输出：`image`（首帧）、`video`（录的 mp4，接 Seedance `video_1`、Wan 动作参考、LTX）、`prompt`。
- 值得记的一个设计：基本体自动按 12 色命名调色板上色，
  > "so each block reads as "the **red** cube is the car driving down the street" when prompting"
- 相机关键帧和每个物体的关键帧分轨；录制走 `canvas.captureStream()` → ffmpeg。
- 对我们：小项目，许可不明。「按颜色在提示词里点名」的思路和 1.1、5.4 一致。

### 4.4 Qwen 多角度 / 3D 相机控制节点

- **ComfyUI-qwenmultiangle**（https://github.com/jtydhr88/ComfyUI-qwenmultiangle ，MIT，1,464 星，push 2026-09-13）：Three.js 视口里拖相机，输出一串格式化提示词给 Qwen-Image-Edit 的多角度 LoRA。转述：提示词形如 `<sks> front view eye-level shot medium shot`；方位 0–360°，俯仰 −30° 到 60°；配 fal 的 `Qwen-Image-Edit-2511-Multiple-Angles-LoRA`；comfy.org 有现成工作流。
- 用途是「一张图换角度」（做定妆多视角、换机位首帧），不是摆场景。

### 4.5 3D OpenPose 编辑器

- ZhUyU1997/open-pose-editor（https://github.com/ZhUyU1997/open-pose-editor ，MIT，966 星）：网页 3D 火柴人，可出深度、法线、canny。最后 push 2024-02-25，**停更**。
- comfy.icu 上列的 FK 3D Openpose Editor、Hina 3D Pose Editor：摆人偶出骨架、深度、法线、canny 四张对齐的图（转述，没找到仓库）。
- 这些都是单帧工具，做视频用 4.2。

### 4.6 和「首帧能不能跟参考片段同用」有关的一句官方说明

Scenario for Blender 用户指南（https://blender.scenario.com/ ）：
> "Some models (Seedance 2.5, 2.0 Fast and 2.0 Mini, Minimax H3 and Wan 3.0) can't take a first frame together with the clip; for them, the image guides the opening look instead, and the form says so."

这和我们 `refs/models.md` 里记的「Seedance 首帧和参考图不能一起用」对得上，并且把 Wan 3.0 和 H3 也列进去了。各家官方文档怎么写，见 research.md 第 2 节。

---

## 5. 姿势参考类网页工具

| 工具 | 能导出 | 许可 / 价格 | 证据 |
|---|---|---|---|
| PoseMy.Art（https://posemy.art/ ） | 官网原文：「Open Pose, Depth, Canny, Normals and Regular images」；2400+ 动捕动画；可导出摆好姿势的人物和场景为 OBJ | 专有。OBJ 导出注明「For base only. Commercial use requires significant alteration.」；导出的 OpenPose / 深度图有没有同样限制，官网首页没写。转述：Pro $15/月、$150/年或 $99.99 买断，OpenPose 导出在免费档；有人嫌它的 canny 线太粗、带阴影 | 读了官网首页 |
| Magic Poser | 没查到 OpenPose / 深度导出 | iOS / Android / 网页，免费 + Pro | 转述 |
| DesignDoll | 没查到深度导出 | Windows，免费版 + 买断 Pro | 转述 |
| poseify（fideliskaruri/poseify） | 开源的 PoseMy.Art 仿制品 | 0 星；仓库里有 33 个属于 PoseMy.Art 的模型文件，不在它的许可范围内 | 元数据 + 转述 |

小结：这类工具只适合人手摆单帧，给不了动作序列，资产也不能再分发。我们用 Blender 自己出就行。

---

## 6. 对比和建议

### 6.1 谁能被 agent 用命令行 / 脚本驱动

**可以无头或半无头：**
- 无头 Blender + `scenario-blender-blockout` 的脚本（纯 bpy，MIT）。它明确写了无头路径：每个阶段载入上一个 `.blend`、检查、扩展、另存。
- `EL4CTEO/blender-skills`（MIT）：没有 MCP 时 agent 在后台跑 Blender。
- LTX-2.5 Layout-to-Render（ComfyUI 工作流 JSON 或 Python 命令行）；SolarRenderer（`scripts/render.py`）；ai-muninn 给的 H3 Ref2VA API 格式工作流（可以直接 POST 到 ComfyUI `/prompt`）。
- CozyClay：`npx cozyclay mcp`、`cclay live`（JSON 进出），但要开着 Chromium。
- Blockout：MCP 33 个工具，但应用（Electron）要开着。
- Scenario 插件本地 MCP、Higgsfield Blender Bridge、MCP for Blender、Blender Lab MCP：都要一个开着的 Blender 界面。

**只能人手点：**
- 即梦 Clay Renderer（插件面板 + 网页）、即梦短剧工作室、LibTV 导演台、Krea Seedance Studio、Higgsfield 3D Jutsu（浏览器里和它的 agent 对话）、Intangible（有 MCP 的说法是转述）、TapNow、Previs Pro、Marble Record、PoseMy.Art。
- ComfyUI 里的 Yedp、Load3D、ComfyBlockout：场景能存进工作流，但烘焙 / 录像在浏览器前端做。

对我们的含义：我们本来就是 agent 写 bpy 脚本，不需要再套一层应用。要拿的是别人的规范、脚本和实测结论，主要来源是 1.1。

### 6.2 谁的设计值得照着做

1. **人偶做几档、按模型选**（scenario skill，1.1）：默认用带两三个特征的彩色胶囊；只有动作本身必须由白模决定（舞蹈、打斗的一招、特定手势）才上带骨骼的假人，而且要给真动画。Seedance 2.5 上带腿的替身会把僵硬步态原样带回来。
2. **身份色**（scenario skill）：每个主角一个饱和色，颜色要对应到这个人真穿的衣服；群演和场景用中灰；黑白灰棕不当身份色；场景别用鲜艳原色。
3. **朝向和车头**（scenario skill）：车头浅色灯块 + 格栅、车尾暗红；单个方块红前、黑后、绿侧。人物朝向沿行进方向；`detailed` 档的人偶加「a nose block and a hair cap」。
4. **导出包**（Blockout，1.2）：参考视频、深度视频、可选法线视频、每个机位点的静帧 + 首尾帧 + 俯视走位图、按模型写的提示词、机器可读的元数据。标签（文字牌）只烧进静帧，不烧进动作视频。
5. **按模型的 profile**（Blockout）：每个模型记时长上限、分辨率、fps、吃参考的顺序、提示词里的「照做」句。换模型是改配置。
6. **导出要干净**（CozyClay，1.3）：不带描边、gizmo、地面网格、选中高亮、帧计数、文字叠加；画幅和成片一致。
7. **交接单**（scenario skill）：色标表（哪个颜色 → 哪个角色 → 哪张参考图）、剪辑表（精确到毫秒）、角色表、哪些东西在白模里有 / 只在文字里有、每个慢动作的状态用文字写明、冲突时以视频为准。
8. **检查项和并排验收**（scenario skill）：主体在画内、头不被挡、不穿模、脚着地、切点；成片和 playblast 左右并排看。
9. **动作质检**（CozyClay）：碰撞、滑步、够不够得着、手部接触，在导出前就查。
10. **多通道一次出**（Yedp，4.2）：OpenPose（带脸）、深度、canny、法线、灰模、alpha、带贴图；男女体型的深度体切换。走控制视频路线时照这个出。
11. **帧数和尺寸对齐模型的格子**（LTX 模型卡：8k+1 帧、宽高被 64 整除、24 fps；ai-muninn：H3 是 17k+5 帧，白模帧数要和输出帧数一样，否则结尾没有参考可跟）。
12. **片段要短**（scenario skill）：10–15 秒保得住机位和布局，20–30 秒会漂。

### 6.3 互相矛盾或有出入的说法

| 问题 | 说法 A | 说法 B |
|---|---|---|
| 人偶上不上色 | CozyClay：「Grey is the point」「Keep the figure grey so it invents the person instead of preserving a mannequin」；LTX 模型卡的例子也是 grey clay | scenario skill：「An all-gray playblast has lost identity」，主角必须上饱和色，并且全灰假人的 playblast 被某家的输入审核拒过；ai-muninn 用红胶囊、蓝方块；ComfyBlockout 自动给基本体上 12 色；BudgetPixel Previs 用「coloured figures」；Blockout 灰模 + 可选染色标签 |
| 颜色是给谁看的 | ai-muninn：「The red and blue are for you, not the model. The model learns who is who from the prompt」 | scenario skill：颜色是「load-bearing」，提示词靠颜色把替身对到角色；并且模型会把色相读成材质提示，所以颜色要落在真穿的衣服上 |
| 提示词里要不要说替身的形状 | scenario skill（Seedance 类）：不要出现几何词，说了反而会被原样渲出来；LTX 模型卡：「Do not write "clay," "3D," or "Unreal."」 | Blockout 自动提示词：「The grey figures are placeholders — replace them…」；ai-muninn（H3）：直接写「the RED TALL CAPSULE」「the BLUE SHORT BOX」并禁止画出替身；scenario skill 自己对 H3 Max 也用按形状和颜色的「替换表」。看起来是分模型：Seedance 类不说，H3 类要说 |
| 外观用什么锁 | flick.art、LTX 模型卡：把白模第 1 帧拿去图像模型转成成片样子，当首帧 | scenario skill：单张转风格帧会把它的构图和形状带进视频，改用 2×2 风格板；并且 Seedance 2.5、H3、Wan 3.0 不能同时吃首帧和参考片段（4.6） |
| 人偶要多细 | ComfyUI 官方：要么极简、要么动作做足，别停在中间（见 7.2） | Blockout：带关节的胶囊假人 + 算出来的步态，正好是「中间」那种；按 scenario 的测试，这种在 Seedance 2.5 上会回来僵硬步态 |
| 「完整 3D 数据」 | Intangible：自己传的是完整 3D 场景数据，Blender 路线只传 2D 渲染 | 没有任何模型接口文档支持「吃 3D 场景」；CozyClay 明说参考是「pixel channel」；VP Land 早期评测说它靠 Kling 渲染（转述） |
| comfy.org 那个链接 | thereelstack 说 @ComfyUI 10-16 发的「Blender blockout → Seedance 2.5」工作流在 `comfy.org/workflows/3ddb7afa1aa4-3ddb7afa1aa4/` | 我打开这个地址看到的是「Seedance 2.5: FLF2V」（首尾帧），不是参考视频工作流。真正的白模工作流在 Comfy-Org/workflows 仓库（见 7.1）。那条 X 帖这里没读 |

---

## 7. 顺带发现（工具以外的，原话都在）

### 7.1 ComfyUI 官方的白模 → Seedance 2.5 工作流（Comfy-Org/workflows）

- 仓库：https://github.com/Comfy-Org/workflows （GPL-3.0，96 星，push 2026-10-29）。两个白模驱动的例子：`shared/haunted-subway`（21 秒第一人称恐怖短片，一段白模视频 + 4 张参考图）和 `shared/halloween-sd`（18 秒竖屏动画，白模 + 7 张参考图）。仓库里带白模 mp4、参考图和工作流 JSON，可以下来对照。
- 做法：一个 `ByteDance2ReferenceNodeV2` 节点吃 4 张图 + 1 段视频。README 的分工表（原文）：

  | 槽 | 模型从它拿什么 | 不许拿什么 |
  |---|---|---|
  | `image_1`（人物三视图） | 第一人称角色的衣服、手、手镯、手表、随身听 | 她的脸，或把三视图的版式当成一个镜头 |
  | `image_2`、`image_3` | 1985 年地铁车厢、座椅、灯、涂鸦、乘客 | |
  | `image_4` | 老妇人的脸、头发、开衫、裙子、手包、空眼眶 | |
  | `video_1`（21 秒白模） | "Camera path, head turns, shot order, blackouts, her positions, timing, and length" | "Its gray placeholder look" |

- 提示词结构（Subject / Action / Spoken language lock / Camera / Style / Constraints and negatives），全文约 2.8 万字符。关键句（工作流 JSON 里的原文）：
  > "`video_1` — 21-second 3D blockout video: This is the definitive reference for all first-person POV camera movement, viewing angles, shot order, action beats, lighting blackouts, character positions, spatial continuity, reveal timing, final framing, and total duration. Match the existing animation and pacing exactly."
  > "The supplied 21-second `video_1` 3D blockout is the absolute authority for all animation, action timing, character placement, first-person camera movement, blackouts, and scene transitions."
  > "Treat the blockout as the animation foundation and this prompt as a visual and performance enhancement."
  > "Important: `image_1` is a character and wardrobe reference, NOT a camera-framing reference."
- 排错表里两条：
  > "The timing drifts from the blockout | Check that **Duration** equals the blockout's length."
  > "Use your own scene | Block the scene in Blender, Unreal, or any 3D tool. Render a gray pass at the length you want, and swap it into `video_1`. Set **Duration** to match."
- 设置：720p、16:9、21 秒、带声音。一段白模里含多个镜头和黑场，一次生成。

### 7.2 ComfyUI 官方短片：白模该多细

YouTube「What do AI video models like Seedance 2.5 and MiniMax H3 pick up from a 3D blockout」（ComfyUI 官方频道，2026-11-13，81 秒，5,732 次播放），https://www.youtube.com/watch?v=2BCnIRyVWIk 。自动字幕原文：
> "there are two main approaches. The first is using simple shapes to establish your scene and composition. Here, you're relying more on your prompt and reference images to guide the action. This gives the AI more freedom to interpret movement. You don't necessarily need to animate someone riding a bike or even include the bike in your blockout. You can simply describe that action in your prompt. The second approach is using detailed animations with precise movements and timing. This gives the model a much stronger motion reference … What you generally want to avoid is something in between. If your blockout includes some movement but it's still fairly stiff or limited, the AI may preserve that stiffness instead of adding the natural motion you're hoping for."

这和 1.1 里 Seedance 2.5 的对比实验结论一致（两个独立来源）。

### 7.3 LTX-2.5 Layout-to-Render IC-LoRA 模型卡

https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Layout-To-Render （建于 2026-09-22，最后修改 2026-10-22；权重要申请；LTX-2.x community licence）。原文：
> "Give it a grey clay viewport, or a blocky playblast of simple shapes, from Blender, Unreal, or a similar 3D tool, carrying the camera move and the objects. Give it a first frame that sets the art direction. It returns a video that moves like the layout and looks like that first frame."
> "A detailed clay render is not required."
> "Take the first frame of the clay animation and give it to any image model to generate the visual you want. … Do not use the grey clay frame itself."
> "If the video ignores the art direction, the first frame is not the picture you want. A grey clay frame used as the first frame produces a grey result."
> "Prompting: One or two sentences describing the finished shot. Match the first frame. Do not write "clay," "3D," or "Unreal.""
> "Keyframes: The first frame is the normal recipe. Add a mid frame and a last frame when the picture should hold through the shot."
> "Resolution & frames: Width and height divisible by 64. 1920×1088 is a known good size. Frame count snaps to 8×k+1. … Prefer a 24 fps layout clip."

上一代是 fal 的 `LTX-2.3-3DREAL-LoRA`（https://huggingface.co/fal/LTX-2.3-3DREAL-LoRA ，托管端点 `fal-ai/ltx-2.3-quality/render-to-real`，吃 `video_url` + 可选 `image_url`，提示词里要留触发词 3DREAL）。这部分是转述，HF 页面我这边没连上。

### 7.4 flick.art 的三步流程（2026-06，Flick 平台的驻场导演 Jaime Yao 写的，带产品宣传）

https://flick.art/blog/blender-ai-filmmaking
1. Blender 里做角色动作和相机运动，导出视频和第 1 帧。「basic shapes are enough」「even cubes as stand ins for characters」「Too much detail can confuse the model」。
2. 用 Nano Banana 把第 1 帧转成成片样子，提示词：
   > "Use the provided image as the composition and pose reference. Keep composition a 100% exactly match of the provided sketch. Keep camera position 100% unchanged. Keep framing 100% unchanged. Make sure character pose stays a 100% match to the provided sketch."
3. Omni Reference 选 Seedance，转好的帧当 start frame，Blender 视频当 video reference，提示词只写：
   > "Reference the character's actions and camera language from @Video."
它还列了五种 Blender 控制方式的对照表（动作参考、渲染通道、首帧控制、灰模 + 角色 rig、3D 场景当虚拟布景），并说本地路线用 toyxyz 的 OpenPose rig + ComfyUI-BlenderAI-node + Wan 2.2 VACE。文中「Seedance and Kling O3 both support Omni Reference and follow a Blender motion reference well」。

### 7.5 ai-muninn：Blender 白模 → 本地 MiniMax-H3 Ref2VA（2026-10-12，个人博客，每个测试只跑了一次）

https://ai-muninn.com/en/blog/blender-blocking-h3-ref2va-rtx5090
- 做法：让 Claude 写 Blender 脚本，红色高胶囊（2.4 m）和蓝色矮方块（1.6 m）代表两个人，左后方放一个不对称的地标（3 个方块搭的拱门），慢推镜头；864×480、24 fps、124 帧；`blender -b` 无头渲 PNG 再 ffmpeg 合成。白模接 `ref_videos`，两张人物全身图接 `ref_images`。
- 规则（原文）：
  > "Stand-ins are only capsules and boxes. No fingers, no props."
  > "At least one asymmetric landmark in the scene"
  > "Same frame count as your output, on the 17k+5 grid that H3 frame counts follow."
  > "The red and blue are for you, not the model. The model learns who is who from the prompt in step 4."
- 提示词（原文节选）：
  > "<Subject 1> is the tall adult woman from <Picture 1>. … Her screen position and walking path come from the RED TALL CAPSULE in <Video 1>."
  > "<Video 1> supplies camera movement, relative spatial positions, blocking, motion timing and foreground occlusion for both subjects. The colored primitives are spatial guides only and must be replaced completely by the two realistic people."
- 结果：两人身份没互换；5 个抽样帧左右顺序都对；中途换位照做；前后遮挡顺序对；矮的还是矮。
- 翻车和对策：
  > "Exact values get softened. Both people drifted toward the center of the frame. The height gap shrank somewhat … And the man's small in-place turn wasn't followed at all."
  > "A 120-frame blockout became 107 usable frames, so the last frames of the shot had no blocking to follow. Render the blockout at exactly the output frame count, on the grid."
  全景里脸只有几十像素宽、糊：「wide shots for blocking, medium shots for faces」（另搭一个腰部以上的近一点的白模，头宽从 48–69 px 到 135–156 px）。
  > "none of my clips had a capsule, a box, or grey material. The model does get every frame of the blockout clip, though, so the prompt still has to tell it to leave out the stand-ins."

### 7.6 thereelstack 2026-10-26 汇总里点到的其他案例（都没打开原帖 / 原片，转述）

- Polypro：Blender MCP 搭灰模 → Nano Banana 2.1 做风格帧 → Seedance 2.5 用预演当动作参考，三个镜头同样时间（X 帖 + YouTube 短片 https://www.youtube.com/watch?v=2TAG2w46NiQ ，9 秒，128 次播放）。
- Veerapatra Jinanavin《Making of TEA BREAK | Blender Layout → AI Animation (Seedance 2.5)》https://www.youtube.com/watch?v=JUoBkcXhIe0 （2026-10-26，240 秒，142 次播放；字幕只有片中对白，没有讲解）。
- Layer《Grey blockout to finished game shot with Kling 4 in Layer》https://www.youtube.com/watch?v=IFiPSc798QE （2026-10-26，31 秒，876 次播放）。
- VP Land 2026-11-10 报道 ComfyUI 的一个演示：Blender 里一座红色悬索桥的白模驱动相机运动，卡着音乐节拍，Seedance 2.5 出片；回复里有人说「The previz workflow is the best for consistency」。

---

## 8. 没查成的和要补看的

**没读到原文的**（都已在正文标转述）：
- Gumroad（toyxyz rig）：直连和代理都连不上。
- blender.org/lab/mcp-server：返回 403。
- huggingface.co/fal/LTX-2.3-3DREAL-LoRA：代理当时不通。
- seadanse.com 那篇「7 步」：返回 403。
- martini.film：纯 JS 页面，没渲染出正文。
- 即梦 Clay Renderer 的飞书官方指南：没打开。
- YouTube：4 条里有 1 条（PolyPro 短片）拿字幕时返回 429，就没再试；其余 3 条拿到了元数据，只有 ComfyUI 那条字幕有内容。

**X 帖（没看，只从网页上抄到链接）：**
- @ComfyUI：`x.com/ComfyUI/status/2111110239714165176`（10-16，Blender blockout → Seedance 2.5）、`…/2115089830585704602`（Haunted Subway）、`…/2113682376815779899`（Halloween SD）、`…/2121308924800647349`（推进画里的转场）
- @higgsfield：`x.com/higgsfield/status/2092255768770920506`（Blender 插件发布）、`x.com/higgsfield_ai/status/2095141451583963229`
- @JSFILMZ0412：`x.com/JSFILMZ0412/status/2093663876692754713`（Claude + Higgsfield MCP + Blender → Seedance 2.5）
- @Polypro_io：`x.com/Polypro_io/status/2114796010476314631`；@Scenario_gg：`x.com/Scenario_gg/status/2114723471217557720`
- @ltx_io：`x.com/ltx_io/status/2110703638599569793`（Layout-to-Render 演示）
- @AIStackLabX：`x.com/AIStackLabX/status/2096631495712751753`（Astra → Blender → Clay Renderer → 即梦）
- @aiwarts：`x.com/aiwarts/status/2061795427830112262`（LibTV 导演台）
- @aiaicreate：`x.com/aiaicreate/status/2027027040113713637`（Yedp 大更新）

**B 站（网页搜索里冒出来的，我没打开）：**
- `BV1x7Yx6YEM6`「GPT-6操作Blender白模预演，辅助Seedance 2.5精准生成视频｜完整流程与成片对照」
- `BV1FdMk65EqW`「Blender+Seedance 2.5，让你的AI视频生成更可控【Blender Talk】」

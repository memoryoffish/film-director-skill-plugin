# 两家官方的提示词优化 skill（出处和各节位置）

| skill | 版本 | 用于 | 出处 | 取回 |
|---|---|---|---|---|
| wan3-pe | 0.2.0 | Wan 3.0 | 阿里云百炼《万相 3.0 视频生成提示词指南》https://help.aliyun.com/zh/model-studio/wan3-video-generation-prompt-guide 页内「下载 Skill」：https://g-adoc.alcasset.com/media/maas_docs/sfm-cn/common/files/6a4b3c2d1e0f9f66.zip（sha256 见下面「怎么取回」） | 2026-11-11（2026-11-22 核对过地址和 sha256） |
| sd25-pe | 0.1.1 | Seedance 2.5 | 火山方舟《Doubao Seedance 2.5 提示词指南》https://docs.volcengine.com/docs/82379/2607689 ；清单 https://arkdocs.tos-cn-beijing.volces.com/skills/.well-known/agent-skills/index.json ，包 https://arkdocs.tos-cn-beijing.volces.com/skills/artifacts/video-generation/sd25-pe/0.1.1/sd25-pe-0.1.1.zip（sha256 见下面「怎么取回」，和清单里的 digest 一致） | 2026-11-11（2026-11-22 核对过地址和 sha256） |

这两个 skill 只拿来参考怎么写提示词。全文是阿里云和火山方舟发布的，没有放进这个仓库；要读就照下面「怎么取回」下载到本目录；下面的行号对应表里的版本，官方出了新版就按节名找。官方用法：`/wan3-pe 提示词`、`/sd25-pe 提示词`；sd25-pe 开头有「触发前的自升级」（联网查新版），下面记的是 0.1.1。

## 怎么取回

下载、核对、解到本目录（`<film-director 的目录>/video-film-maker/refs/practical/prompt-skills/`），解完是 `wan3-pe/SKILL.md` 和 `sd25-pe/SKILL.md`：

```bash
cd <film-director 的目录>/video-film-maker/refs/practical/prompt-skills
curl -fLo wan3-pe.zip https://g-adoc.alcasset.com/media/maas_docs/sfm-cn/common/files/6a4b3c2d1e0f9f66.zip
curl -fLo sd25-pe.zip https://arkdocs.tos-cn-beijing.volces.com/skills/artifacts/video-generation/sd25-pe/0.1.1/sd25-pe-0.1.1.zip
shasum -a 256 wan3-pe.zip sd25-pe.zip        # Linux 上用 sha256sum
unzip -o wan3-pe.zip wan3-pe/SKILL.md        # 这个包里是 wan3-pe/ 文件夹
unzip -o sd25-pe.zip SKILL.md -d sd25-pe     # 这个包里 SKILL.md 在最外层
shasum -a 256 wan3-pe/SKILL.md sd25-pe/SKILL.md
```

| 文件 | sha256 |
|---|---|
| `wan3-pe.zip`（0.2.0） | `370cfe7376d7953a62adc5ed3df12a2017f7b89c0ce51ba2841f8047c42dd439` |
| `sd25-pe.zip`（0.1.1） | `de823de6dc053ad463a3a5ccd2b1a59bf65f06515ebd5badc12a351d59269f85` |
| `wan3-pe/SKILL.md`（346 行） | `c7b22d8bf902131b3c399a7c5519c158e9ebf7582a76b7e8ef6567a018ee3649` |
| `sd25-pe/SKILL.md`（996 行） | `ee04557ba9a1c9f5517b574e24fc73d0022b22254373074db4c11f3d0635ea57` |

- sha256 对不上，说明官方换了包：照样能用，但下面的行号不再准，按节名找（比如 `grep -n '视频延长模板' sd25-pe/SKILL.md`）。
- 下载回来的包和解出来的文件只在本机用，不提交进仓库（本 skill 的 `.gitignore` 已经排除了它们）。
- 取不到（离线、地址失效）时，照 [adapt.md](../../../stages/3-generation/adapt.md) 里自己写的两家骨架写，被点名的那一节就跳过。

## 和哪一步有关

- **续写**（[extension.md](../../../transitions/extension.md)）：wan3-pe「视频区间入片」「案例 B：完整视频首段 + 向后续写」；sd25-pe「视频延长模板」（向后、向前延长）。
- **首帧 / 尾帧接龙、过渡段**（[bridge.md](../../../transitions/bridge.md)、[tail-frame.md](../../../transitions/tail-frame.md)）：wan3-pe「整图入片」；sd25-pe「关键帧锚点」（首帧加参考、首尾帧加参考、多关键帧顺序）。
- **参考图锁人物**（[references.md](../../../stages/2-casting/references.md)）：wan3-pe「第三步：分配素材职责」「编号规则」；sd25-pe「主体设定和分场景调用」「建立素材职责和主体映射」。
- **分镜表、一部片的时间线**（[shot-unit.md](../../../stages/3-generation/shot-unit.md)、[movie.md](../../../transitions/movie.md)）：sd25-pe「长视频与时间段」；两者的镜头时间戳写法（「镜头N xx-xx秒」）。
- **运镜和声音**（[prompts.md](../../../stages/3-generation/prompts.md)）：wan3-pe 五段请求结构里的【运镜与核心约束】【音频风格】；sd25-pe「专业摄影表达」「声音、台词和文字」。
- **台词和音色**（[dialogue.md](../../../stages/3-generation/dialogue.md)）：wan3-pe「台词与音色」「音频入片」；sd25-pe「声音、台词和文字」，改已有片子的声音看「声音编辑」。

和我们写法不同的地方：两家都主张「只写用户要的、不滥加约束」，画幅、时长、分辨率交给接口参数；我们在接缝要用的那几秒的提示词里会写「no cuts / no dissolves」「no music」，因为实测 Wan 会自己切镜、加配乐（见 [wan3-notes.md](../wan3-notes.md)、[own-cuts.md](../../../stages/3-generation/own-cuts.md)）。

## 各节的行号

下载回来以后，别的文件点名哪一节，就按节名找到它，照下面的行号只读那一节（Read 带 offset、limit），不要整篇打开。

wan3-pe 0.2.0 的 `SKILL.md`（346 行）：

- 「技能定位」27–37、「触发与不触发」38–55、「硬性约束」56–69
- 「素材输入情形」70–95：「无素材的纯文字请求」74–77、「引用素材但当前不可得」78–83、「素材可读时」84–87、「数量与上限」88–91、「编号规则」92–95
- 「整理流程」96–188：「第一步：锁定故事合同」98–117、「第二步：读懂素材」118–143、「第三步：分配素材职责」144–171、「第四步：把握映射确定性」172–184、「第五步：落模板并净化」185–188
- 「请求模板」189–265：「五段请求结构」191–232、「整图入片」233–241、「视频区间入片」242–250、「音频入片」251–258、「台词与音色」259–265
- 「交付约定」266–273、「交付前核对」274–292
- 「端到端示例」293–339：「案例 A：急诊室抢救（形象参考 + 音色参考）」295–319、「案例 B：完整视频首段 + 向后续写」320–339
- 「运行环境适配」340–346

sd25-pe 0.1.1 的 `SKILL.md`（996 行）：

- 「触发前的自升级」28–44、「目的」45–50、「适用场景」51–67、「不可违反的原则」68–81
- 「输入状态」82–120：「纯文生视频」86–89、「需要参考但未提供素材」90–97、「素材可读取」98–101、「当前 Agent 无法读取」102–107、「素材规格预检」108–120
- 「核心工作流」121–327：「1. 解析用户目标」123–152、「2. 编译小说和长文本」153–163、「3. 盘点和理解素材」164–199、「4. 建立素材职责和主体映射」200–244、「5. 处理映射置信度」245–259、「6. 选择唯一主任务」260–310、「7. 应用任务参数规则」311–321、「8. 套用模板并净化」322–327
- 「视频生成模板」328–401：「基础生成」330–351、「带参考素材的生成」352–401
- 「多素材组织」402–497：「类型分组」414–434、「主体设定和分场景调用」435–457、「空间与站位」458–497
- 「长视频与时间段」498–543：「目标时长覆盖」524–543
- 「视频编辑模板」544–636：「声音编辑」614–636
- 「视频延长模板」637–698：「向后延长」647–676、「向前延长」677–698
- 「关键帧锚点」699–818：「首帧加其他参考」707–718、「首帧、尾帧加其他参考」719–749、「多关键帧顺序控制」750–767、「宫格分镜与故事板」768–784、「白模参考与渲染」785–818
- 「情绪、摄影与声音」819–903：「情绪与可观察表现」821–846、「专业摄影表达」847–864、「声音、台词和文字」865–883、「产品与实体流程」884–903
- 「输出合同」904–957：「默认交付」908–915、「素材引用保真」916–921、「输入与参数提示」922–929、「必须说明的能力边界」930–937、「完整输入到输出示例」938–957
- 「最终自检」958–989、「Compatibility And Runtime Notes」990–996

两家的「镜头N xx-xx秒」写法：wan3-pe 第 202 行（「五段请求结构」里）；sd25-pe 第 532–540 行（「目标时长覆盖」里）。

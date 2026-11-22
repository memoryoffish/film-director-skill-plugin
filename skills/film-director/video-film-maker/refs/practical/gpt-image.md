# gpt-image：要一张做准的图时用

一句话：定妆参考图、关键时刻的那一帧、表情的首尾帧、画面上要读清的字，这些要做准的图可以先用 OpenAI 的 gpt-image 画出来，再交给视频模型；画质默认 `high`；用之前问用户。

照官方图像提示词指南整理（[原文](https://developers.openai.com/api/docs/guides/image-prompting?model=gpt-image-2.6)，Markdown 版在同一地址加 `.md`；2026-11-16 查）。带白模的片子里，每镜的关键帧就是用它照白模静帧和定妆图画的（见 [关键帧](../../stages/2-casting/keyframes.md)）。

## 什么时候用

- 定妆：人物、道具、场景的参考图（见 [参考图](../../stages/2-casting/references.md)）。
- 关键时刻那一帧先做成图，再当首帧或尾帧（见 [关键时刻](../../stages/1-storyboard/key-moment.md)）。
- 表情的首尾帧（见 [表演](../../stages/3-generation/acting.md)「待实测」）。
- 画面上要读得清的字、二维动画的画风基准图。

## 用之前问用户

和 [预算](../../stages/common/budget.md) 一起问，用户的答复只对这一部片有效；没人回答时见 [规矩](../../stages/common/rules.md)「没人回答时」：

- 用不用。调 gpt-image 的脚本是 blender-previz 的 [scripts/gimg.py](../../../blender-previz/scripts/gimg.py)（OpenAI 官方 Images 接口，key 只从环境变量 `OPENAI_API_KEY` 读，用法见 [blender-previz 的 refs/gpt-image.md](../../../blender-previz/refs/gpt-image.md)），所以要问有没有可用的 key。装了同一个仓库里的 film-crew 插件时，出图也可以交给它的 backends（同样从 `OPENAI_API_KEY` 读 key）。
- 用哪个模型：`gpt-image-2.6-sunburst` 细节和编辑更准，`gpt-image-2.6-flare` 更快。
- 画质：**默认 `high`**；要省钱或要快，问过用户再降。
- 大概几张、多少钱：按 token 计费，标准队列每百万个图像 token 输入 $8、输出 $30，批量减半；一张多少看尺寸和画质，用官方的[计算器](https://developers.openai.com/api/docs/guides/image-generation#calculating-costs)估（[价格页](https://developers.openai.com/api/docs/pricing)）。

## 参数（官方）

| 参数 | 用法 |
|---|---|
| `model` | `gpt-image-2.6-sunburst` 或 `gpt-image-2.6-flare` |
| `quality` | `auto` / `low` / `medium` / `high` / `xhigh` / `max`；我们默认 `high` |
| `complexity` | 出图前规划多少：`low` / `medium` / `high`，不写就是 `high` |
| `size` | `1024x1024`、`1536x1024`、`1024x1536` 或自定（两边都是 16 的倍数，画幅 1:3 到 3:1）；16:9 的画用 `1536x864` |
| `background` | `auto` / `opaque` / `transparent` |
| `output_format` | `png` / `jpeg` / `webp`（生成还能出 `svg`、`gif`） |
| `markup` | 编辑时上传和第一张输入图一样大的透明 PNG，在上面标要改的地方 |

编辑时不写 `input_fidelity`。比较画质时固定 `complexity`，比较 `complexity` 时固定画质，一次只改一样。

## 写法（官方 8 条）

1. **先说结果**：主体、用途、构图、画幅、位置约束；复杂的分成场景、主体、细节、约束几段。
2. **格式随意**：短句、段落、类 JSON 都行，挑最好读、好改的。
3. **写看得见的细节**：材质、光、颜色、媒介；要写实就明说「photorealistic」。镜头参数只当外观提示；宽画面、暗光、雨夜、霓虹要写尺度、氛围和颜色，不靠情绪词。
4. **人和动作**：取景范围、相对大小、视线、手怎么拿东西（「全身，脚也在画里」「看着打开的书」）。
5. **字**：要的字放引号里，写清位置和字体，少见的词逐字拼出来；写明不要别的字，生成后查拼写和清晰度。
6. **编辑分清改和不改**：「只改 X」，列出要保持的（身份、形状、布局、光、标签），排除水印、多余的字和 logo。
7. **参考图分角色**：按编号写每张是干什么的（人物、画风、衣服、背景），怎么组合。
8. **一次改一样**：上一张当下一次编辑的输入，每次重复要保持的东西；出图偏离了要求，就把关键约束再写一遍。

**人物一致**（官方例子）：先做一张角色设定图（外貌、比例、衣服、气质，干净背景，不要字），后面每张都带上它，并重复「同样的衣服、五官、比例、配色」「不要重新设计角色」。

## 生成后查

- 字读得清，和要求的一样。
- 身份、形状、参考图里的细节没变。
- 编辑只改了要改的地方。

## 局限

- 画出来的图会和输入不一致：一部 38 镜的片，事后一镜一张放大了看，26 张关键帧的背景或站位不对。画完照 [关键帧](../../stages/2-casting/keyframes.md)「出图后检查」看。
- 给 Seedance 用的图不能有写实人脸，会被拒（见 [models.md](models.md)）；动画风格的可以。
- 一张图多少钱要用计算器估，计费按 token，不是按张。

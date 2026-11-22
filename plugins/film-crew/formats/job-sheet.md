# 任务单

一句话：一个 JSON 文件就是一次生成请求，要一段视频或一组图；写单子的人只写要什么，交给后端（[../backends](../backends/overview.md)）去调模型。

## 规矩

1. **一个文件一次请求。** `name` 是这次请求的名字，后端用它给产物和记录起名（`<name>.mp4`、`<name>.png`、`<name>.json`）。同一个名字只对应一次请求：要重来或换参数，就换个名字。
2. **字段就是拍片 skill 现在写的任务文件里那些。** skill 今天写出来的任务文件，不用改就是合法的任务单，包括已经给 Seedance 改写过的（`"resolution": "720p"`、没有 `seed`、提示词里写 `@图片N`）和出图的单子（`name, prompt, images, size, n, model, quality`）。
3. **相对路径相对项目目录。** 首帧、尾帧、参考图、参考视频、输入图写相对路径时，相对的是运行命令时所在的项目目录（单子一般放在 `<项目>/jobs/`、`<项目>/jobs_img/`，路径从 `<项目>/` 算起，例如 `keys/k_s01.png`）；写绝对路径就照用。
4. **`model` 写要哪个模型，别的不管。** 这个模型收不收这种喂法、几秒、几张参考图，这里不定，看后端的能力卡（`../backends/cards/`）。
5. **照平常写就行，给哪家改写是后端的事。** 写成 `"720P"`、带 `seed`、提示词里叫 `图1`，再加 `"model": "seedance-2.5"`，后端会改成 Seedance 要的样子；已经改写过的单子，后端原样用（改写做两遍和做一遍一样，后端的测试里查了这一条）。

## 字段

两种单子都有：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | 字符串 | 是 | 这次请求的名字，不带 `/` |
| `prompt` | 字符串 | 是 | 提示词，不能空 |
| `model` | 字符串 | 否 | 要哪个模型；不写就用后端的默认模型 |
| `kind` | `"video"` / `"image"` | 否 | 一般不用写，见下一节 |

视频单子：

| 字段 | 类型 | 说明 |
|---|---|---|
| `duration` | 整数 | 秒数 |
| `resolution` | 字符串 | `"720P"` 这类；`"720p"` 也行 |
| `ratio` | 字符串 | 画幅，`"16:9"` 这类 |
| `audio` | 布尔 | 要不要声音 |
| `prompt_extend` | 布尔 | 让模型扩写提示词 |
| `seed` | 整数 | 种子 |
| `first_frame` | 路径 | 首帧。写成 `"@NAME"` 是用前一个任务 NAME 的官方尾帧（那个任务要写 `return_last_frame`） |
| `last_frame` | 路径 | 尾帧，要和 `first_frame` 一起 |
| `reference_images` | 路径列表 | 参考图，按顺序就是提示词里的图1、图2…… |
| `reference_video` | 路径 | 参考视频（提示词里的视频1），可以和参考图一起 |
| `return_last_frame` | 布尔 | 要模型交回官方尾帧，给下一段当首帧 |

图片单子：

| 字段 | 类型 | 说明 |
|---|---|---|
| `images` | 路径列表 | 输入图，第一张是提示词里的 Image 1；不写就是只凭文字出图 |
| `size` | `"宽x高"` | 例如 `"1536x864"` |
| `n` | 整数 ≥ 1 | 出几张 |
| `quality` | 字符串 | 例如 `"high"` |

没列在这里的字段不收。不写的字段由后端用自己的默认值（能力卡里写着）。

## 视频还是图片

1. 写了 `kind` 就照 `kind`。
2. 没写：`model` 以 `gpt-image` 开头，或者有 `images`、`size`、`n`、`quality` 任何一个，就是图片。
3. 其余都是视频。

所以只有 `name` 和 `prompt` 的单子是视频；要只凭文字出图，写上 `size` 或 `"kind": "image"`。

## 喂法

只看有哪些媒体字段：

| 有的字段 | 喂法 |
|---|---|
| 都没有 | 文生（t2v） |
| `first_frame` | 首帧（first_frame） |
| `first_frame` + `last_frame` | 首尾帧（first_last） |
| `reference_images` | 参考图（refs） |
| `reference_video`（可以再带 `reference_images`） | 参考视频（ref_video） |
| 图片单子有 `images` / 没有 | 改图（edit）/ 文生图（t2i） |

一张单子只有一种喂法：只有 `last_frame` 不行；首帧、尾帧不和参考图、参考视频写在一起。

## 检查

```
python3 check_job.py SHEET.json [...] [--root 项目目录]
```

查格式：必填字段、类型、一张单子一种喂法、有没有不认识的字段；给了 `--root` 再查文件在不在。不查某个模型收不收。有问题逐条打印，退出码 1。代码里用 `check(sheet, root)`，返回问题列表，空列表就是没问题。

## 例子

[examples/jobs/](examples/jobs/overview.md)：每种喂法一张，两张图片单，一张照平常写、交给 Seedance 的单子。

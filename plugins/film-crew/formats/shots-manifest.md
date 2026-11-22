# 镜头清单

一句话：一部片一个 JSON，写这部片每一镜「用了什么、出了什么」；ComfyUI（`../comfyui/scripts/shots2comfy.py`）和网页查看器（`../viewer`）都只读它。拍片的运行目录由 [read_run.py](read_run.py) 读成清单；别的流程没有这种运行目录，自己照格式写一份也行。

## 怎么用

1. **从运行目录读**：`python3 read_run.py CONFIG.json --out DIR [--films k1,k2]`，一部片写一个 `DIR/<key>.shots.json`。
   CONFIG：`{"films": [{"key", "run", "film", "previz", "flag"}]}`，路径相对 CONFIG 所在的目录，可以用 `~`；`film`、`previz` 不写就是 `<run>/film.mp4`、`<run>/previz.mp4`。页面的设置（`title`、`compact`、`view` 这些）写在里面也不碍事，这里不读。
2. **查格式**：`python3 check_manifest.py DIR/*.shots.json`，有问题打出来、退出码 1。只看清单本身，不读里面写的文件。
3. **交给查看器**：ComfyUI 是 `../comfyui/scripts/shots2comfy.py DIR/*.shots.json …`；网页是 `../viewer/scripts/console.py DIR/*.shots.json OUT_DIR …`。

## 规矩

1. **图的路径相对 `root`**；任务文件里写的是绝对路径，就照写绝对路径。
2. **名字用 skill 自己的**：镜头名、任务名照原样；关键帧、出图任务的名字是图的文件名去掉扩展名（`k_S3`）。人说「S3 的首帧」，说的就是这些名字。
3. **前一半是 ComfyUI 用的几项**，格式和 `shots2comfy.py` 开头写的一样，不变。**后一半是另加的几项**，都可以没有，只有网页查看器用；`shots2comfy.py` 不认识的字段一律不看，加了也不改它出的工作流。
4. **只写事实**：这部片、这一镜是什么样的。转出来的媒体文件叫什么、多大、摆在页面哪里，是查看器自己的事，不写进来。
5. **认不出来的不写，或者写 null**（比如为什么重抽，运行目录里没有记录，`why` 写 null），不猜。

## ComfyUI 用的几项

一部片：

| 字段 | 是什么 |
|---|---|
| `film` | 片的 key：ComfyUI 里的文件夹名、文件名都用它，不带 `/` |
| `title` | 片名，可以不写 |
| `root` | 放图的目录（运行目录） |
| `video` | 成片 mp4 |
| `shots` | 每一镜一条，按时间排 |

每一镜：

| 字段 | 是什么 |
|---|---|
| `name`、`what` | 镜头名、拍什么 |
| `t0`、`t1` | 这一镜在成片里的起止（秒） |
| `video` | 这一镜的视频是怎么生成的；一条生成切成几镜时，几镜写同一条。没有视频任务的镜头不写 |
| `keyframes` | 视频直接用的图里，这一镜自己出的关键帧：`{路径: {prompt, size, inputs, takes}}`，`inputs` 依次是出图的图1、图2……，重画过的 `takes` 写 `[[名字, true, 用没用上], …]` |
| `images` | 这一镜里其余每一张现成的图：`{路径: {kind, title, short}}`。`kind`：`wm` 白模静帧、`ref` 参考图、`key` 别的镜头的关键帧或基准画面、`img` 其他；`title` 是 ComfyUI 里这张图的节点标题 |

`video`：

| 字段 | 是什么 |
|---|---|
| `name` | 任务名 |
| `feed` | 喂法：`T2V` 文生、`I2V` 首帧、`FLF2V` 首尾帧、`R2V` 参考图 |
| `first`、`last`、`refs`、`ref_video` | 这种喂法用到的才写：I2V 写 `first`，FLF2V 写 `first`、`last`，R2V 写 `refs`（一列）和参考视频 `ref_video` |
| `model`、`prompt`、`duration`、`seed`、`resolution`、`ratio`、`audio` | 生成用的参数（ComfyUI 视频节点上显示的；没写的用默认值） |
| `takes` | 每一次生成 `[名字, 成没成, 用没用上]`；只有一次可以不写 |
| `shots` | 这条生成切成了哪几镜；只有这一镜可以不写 |

```
{"film": "zz_demo", "title": "接口演示", "root": "<运行目录>", "video": "<成片 mp4>",
 "shots": [{
   "name": "S3", "what": "她把杯子放到桌上", "t0": 8.0, "t1": 12.0,
   "video": {"name": "v3r", "feed": "I2V", "first": "keys/k_S3.png",
             "model": "Wan 3.0", "prompt": "…", "duration": 5, "seed": 0, "resolution": "720P", "ratio": "16:9", "audio": true,
             "takes": [["v3", true, false], ["v3r", true, true]], "shots": ["S3"]},
   "keyframes": {"keys/k_S3.png": {"prompt": "…", "size": "1536x864",
                                   "inputs": ["wm/S3_a.png", "keys/k_base.png", "refs/girl_front.png"], "takes": []}},
   "images": {"wm/S3_a.png": {"kind": "wm", "title": "白模 · S3 开头"},
              "keys/k_base.png": {"kind": "key", "title": "基准画面 · k_base"},
              "refs/girl_front.png": {"kind": "ref", "title": "参考图 · girl_front", "short": "girl_front"}}}]}
```

`keyframes` 里的每一张都得是视频直接用的图（`first`、`last` 或 `refs` 里的一张），ComfyUI 那边按它在视频节点上的口写标题。

## 网页查看器另加的几项

都可以没有，只有网页查看器用。没有时页面少那一块：没有 `previz` 就不放预演，没有 `pictures` 图下面只写文件名，没有 `attempts` 就不显示重抽的明细。

一部片：

| 字段 | 是什么 |
|---|---|
| `genre` | 类型 |
| `model` | 全片用的模型，一句话（`Wan 3.0（720P，带声音）；关键帧 gpt-image`）。任务里没写模型时，节点图取它括号、分号前那段 |
| `previz` | 全片的白模预演视频；没有就不写 |
| `flag` | 有问题的地方：`{t: 秒, shots: [镜头名], note: 一句话}`，页面打开就停在这一镜 |
| `recon` | 镜头表是重建的：一句话写从哪重建的 |
| `plan`、`seconds` | `plan: true`：还没开拍，没有成片；`seconds` 是镜头表写的片长（开拍了的片子看成片本身，不写） |
| `roles` | 每张参考图是谁：`{"girl": "女孩，全身"}`，键是文件名去掉扩展名 |
| `pictures` | 用到的每一张图（下面一张表） |
| `image_jobs` | 每一个出图任务（下面一张表） |

每一镜：

| 字段 | 是什么 |
|---|---|
| `feed_note` | 镜头表里这一镜怎么喂的那句原话（`关键帧当首帧（v3r）`） |
| `stills` | `[首, 尾]`，这一镜的白模静帧：先在白模目录里（含子目录）按镜头名找（`<镜>_a.png`、`_b.png`），找不到用这一镜的关键帧出图时用的那张白模；没有写 null |
| `named_stills` | `[首, 尾]`，白模目录最上层按镜头名放的那两张，喂没喂进去都写；找「有白模、没喂进去」的镜头用 |
| `own_ref` | 一条生成切成几镜、参考图里放着各镜的画面时，哪一张是这一镜的（参考图的下标，从 0 起） |

每一镜的 `video` 里：

| 字段 | 是什么 |
|---|---|
| `sent` | 任务文件原样，只去掉 `prompt`（在 `video.prompt`）：发出去的 `first_frame`、`last_frame`、`reference_images`、`video` / `reference_video` 和每个参数。不管喂法，任务里有什么写什么（参考图生视频也给了首帧，就都在） |
| `status` | 这一次生成的结果：`ok`、`failed`，或结果记录里写的状态（小写）；没有记录不写 |
| `attempts` | 同一镜生成过的每一次，按时间排：`{name, used, status, error, seed, diff, was, why}`。`diff` 是和用上的那次比哪几项输入不一样（只换了 `seed` 就是换种子重抽），`was` 是改了的图原来是哪张，`why` 为什么重抽（没有记录写 null）。只生成过一次不写 |

`pictures`，键是图的路径：

| 字段 | 是什么 |
|---|---|
| `label` | 这张图是什么，一句话：`参考图 girl_front`、`白模 S3_a`、`关键帧 k_S3（S3 首帧 等）` |
| `made_by` | 出这张图的出图任务（`image_jobs` 里的名字）；找不到出图记录不写 |
| `keyframe` | `true`：这部片出的关键帧，节点图沿着它往上追 |
| `still` | 白模静帧是哪一镜的哪一头：`[镜头名, "a" 首 / "b" 尾]` |
| `note` | 白模静帧的站位描述 |

`image_jobs`，键是出图任务名：

| 字段 | 是什么 |
|---|---|
| `prompt` | 出图提示词 |
| `inputs` | 喂给出图模型的图，依次是图1、图2…… |
| `size` | 出图尺寸，记录里写了才有 |
| `ok` | 出图成没成；关键帧目录里的出图记录才有 |
| `attempts` | 重画的几版，格式和 `video.attempts` 一样；只画过一次不写 |

## 从运行目录读出来时，两份事实宽窄不一样

运行目录里没有现成的事实，下面这几样是从文件名、目录认出来的，ComfyUI 用的几项和另加的几项各有各的认法，`read_run.py` 两套都写。自己照格式写清单时，直接写事实，两边写成一样的就行。

| 事 | ComfyUI 用的几项 | 另加的几项 |
|---|---|---|
| 哪张图是关键帧 | 放在 `keys/`、有出图记录（`keys/` 或 `jobs_img/`），且是这一镜自己的 | `made_by`：按名字找得到出图记录（还找 `imgjobs/`、图旁边）；`keyframe`：放在 `keys/`、记录在 `keys/` 或 `jobs_img/` |
| 重抽归到哪一镜 | 名字后缀 `r`、`b`、`_tN`、`_vN`、`_B` 去掉一次；按结果记录里的先后排 | 同样的后缀一层层去掉；按生成时间排，带 `diff`、`was` |
| 一次生成的结果 | `takes` 里 `true` / `false` / `null`（不认识的状态） | `status`：`ok`、`failed` 或原来的状态 |
| 白模静帧 | `images` 里 `kind: "wm"`，只写喂进去的 | `stills`（含子目录、找不到用关键帧的）、`named_stills`（最上层、按名字） |

一镜用哪条视频任务，两边是同一个：这一镜的 `job`、`clip`、`source`、`src`、`feed`、`name` 里第一个是任务名的词，都没有再查剪辑表 `edl.json`。

## 例子

- [examples/manifest/demo.shots.json](examples/manifest/demo.shots.json)：手写的四镜，另加的几项都填了。

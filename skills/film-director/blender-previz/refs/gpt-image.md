# 白模转关键帧：图像模型怎么调

图像模型用 `gpt-image-2.6-sunburst`，画质设 `high`。思路和经验在 [stages/3-feed/keyframes.md](../stages/3-feed/keyframes.md)，这一篇讲怎么调用。

## 调用

```
python3 scripts/gimg.py --out keys jobs_img/k_s1.json jobs_img/k_s2.json
```

任务文件，一个任务一个 json：

```json
{"name": "k_s1", "size": "1536x864", "images": ["wm/s1_a.png", "refs/ajie.png", "refs/xz.png"],
 "prompt": "Turn Image 1 into a photorealistic film still, 16:9. …"}
```

- `images` 里的第一张就是提示词里的「图1」，后面的依次往下数；不写 `images` 就是只凭文字出图（定妆图、道具图、场景图）。
- 脚本输出 `keys/<name>.png` 和 `keys/<name>.json`；已经出好的会跳过，要重画就删掉它的那个 json。一次并行出 4 张，一张约 25–45 秒；实际出来的图是 1672×941，不是任务里写的尺寸（这几个数和下一条的报错码都是 2026-11 实测时的，换了接口先重看）。
- 服务端偶尔报 502、524、499 或断开连接：脚本会自己重试两次，先隔 20 秒、再隔 40 秒；两次都失败的记在它的 json 里，同一批再跑一遍，就只补失败的那几张。
- 请求发到 OpenAI 官方 Images 接口：带输入图的发到 `/v1/images/edits`，纯文字的发到 `/v1/images/generations`。地址读环境变量 `OPENAI_BASE_URL`（默认 `https://api.openai.com/v1`），key 只读环境变量 `OPENAI_API_KEY`，在进程里读、不打印；型号默认 `gpt-image-2.6-sunburst`（[官方型号页](https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst)），用环境变量 `OPENAI_IMAGE_MODEL` 或任务里的 `"model"` 换。
- 装了同一个仓库里的 film-crew 插件的话，出图也可以交给它的 backends（先用 `request` 看要发的请求再发），任务单格式一样。
- 提示词用英文写（官方指南的例子都是英文）；官方指南：<https://developers.openai.com/api/docs/guides/image-prompting?model=gpt-image-2.6>。

## 提示词骨架

主帧（输入图依次是白模、人物图、道具图）：

```
Turn Image 1 into a photorealistic film still, 16:9.

Image 1 is a 3D blocking render (white model). Use it only as the layout guide: keep its camera position, lens, perspective and framing exactly,
and keep every person and object at the same place, size, facing direction and pose. Do not move, add or remove anyone or anything.
Walls, floor, door and furniture stay where they are in Image 1.

Who is who:
- The blue mannequin on the left is <NAME>: the <person> from Image 2 (<face, hair, clothes>). He is <seen from behind / in profile facing right …>, <doing what>.
- The red mannequin on the right is <NAME>: … from Image 3 …
- The green box is the <prop> from Image 4 (<what it looks like>). <Which way it faces.>

Scene: <the place; what each coloured block in the white model stands for; what state things are in>.

<Mood of the moment.> Look: photorealistic cinema frame, 35mm film, fine grain, natural colours, <light>.

The mannequins and boxes in Image 1 are only position markers: do not draw any mannequin, flat plastic white-model shading, square chest plates,
subtitles or watermark. Nobody looks at the camera.
```

派生帧（输入图依次是这一镜的白模、主帧、这一镜需要的人物图）：

```
Image 2 is a film still: <one sentence>. Image 1 is a 3D blocking render (white model) of <the next shot in the same place, from a new camera position … /
the same shot three seconds later, same camera>. Draw <this new shot / that later moment> as a photorealistic film still, 16:9.

Keep from Image 2: the same <place: walls, floor, door, landmarks>, the same <props>, the same people and clothes, the same light and film look.

Framing, positions and poses exactly as in Image 1: <shot size>. The blue mannequin on the LEFT is <NAME> (<the person from Image 3>), <pose, facing>.
The red mannequin on the RIGHT is … <What is behind them. What cannot be seen from this side.>

<the same "only position markers" paragraph>
```

二维动画：把提示词里的 `photorealistic film still` 和 `Look:` 那一行换成画风描述（例如 `a frame from a hand-drawn 2D anime film, clean line art, cel shading, painted backgrounds`）；主帧多带一张画风基准图，提示词里写 `Match the drawing style of Image N`。

## 实测的脾气（和白模有关的）

下面是六个案例、一百多张关键帧里见到的；对应的做法写在 [stages/3-feed/keyframes.md](../stages/3-feed/keyframes.md)，各片的具体数字在 [examples/](../examples/overview.md)。

- 拍片时顺手看，机位、站位、左右多半第一次就对上，贴地、俯拍、过肩、反打都跟得上，出错多在状态、尺度和小东西上；但事后把一部 38 镜的片一镜一张放大了再看，26 张的背景或站位没照白模，所以每张都要和白模并排专门看。
- 照搬人偶的姿势：白模里两臂平伸，关键帧就是 T 字；两个人偶坐姿一样，画出来的两人也一样。
- 人在画面里看得清、又不大时，会被画大（人占画面高：白模 6% → 9.5%，37% → 51%，12% → 17%）；只剩一个光点时（4%）大小是对的。提示词里写百分比没用，拿画面里的东西当尺子写比例好一些（9.5% → 7.8%）。
- 从主帧派生的帧会把主帧里的东西带回来（片尾桌上又出现了已经给出去的橡皮）。
- 输入图里有别的人时，他的配件会串到这一镜的人身上（老师的圆眼镜到了学生脸上）。
- 定妆图上人身上挂着的小道具会再画一份（腰上一支手电，手里又一支）。
- 主帧是大远景时，小占位物在里面只有几个像素，从它派生的几个机位把这样东西各画成各的样子（实心大圆盘 / 带辐条的小手轮）。
- 白模里涂成醒目色的道具，偶尔会被照着那个颜色画（17 张里 1 张把白橡皮画成黄的）。
- 方块家具会被画成方墩（实心方块椅子 → 木墩加靠背）。
- 写了「门开 85 度」也可能画成开过 90 度：出图后对着白模看门扇的角度。

# 03 节点包：回放，以后生成

一句话：六个节点用 ComfyUI 的新接口（`comfy_api.latest`）写，再带一段前端脚本：节点上只露这一步要看的，图和成片由前端直接从运行目录取，打开就有图、视频自己播；回放不调接口，跑一遍把这一镜的关键帧和视频留在 output 里（人接手要用的，见 [06-handover.md](06-handover.md)）；生成模式以后用同一套口接我们的工具。

## 推荐

- **按片名找文件，不认识任何 skill 的目录**：参数里只写 `film`（片的 key）和 `name` / `file`；root（下面叫运行目录）、成片的绝对路径、每张关键帧的文件，记在节点包目录的 `filmkit_runs.json`（`scripts/shots2comfy.py` 照清单写；也能用环境变量 `FILMKIT_RUNS` 指到别处）。工作流里没有服务器路径。
- **视频按喂法分节点**：FilmKitT2V / I2V / FLF2V / R2V 共用一套参数和回放，只是口不同；一个工厂函数生成四个类。看节点名就知道喂法。视频节点是输出节点，也是一镜的终点：不另放「成片这一镜」，同一个画面不摆两遍。
- **口按用了几张来**：关键帧的图、参考图生视频的参考图用 `io.Autogrow`（`TemplatePrefix(..., prefix="image")`），口名 `images.image0`、`images.image1`……，接满一个前端自动多出一个空口；执行时收到 `{名字: 图}` 的字典。
- **前端脚本 `web/filmkit.js` 管显示**（节点一打开就这样，不用先跑）：
  1. 藏参数：标 `advanced=True` 的（film、file、name、执行方式、size、seed、resolution、ratio、audio、t0、t1）设成 `hidden`，连带 seed 后面前端自动加的控件。前端 1.59 的经典画布不管 advanced 标记，所以自己藏；设置里开了 Always show advanced widgets 就不藏。
  2. 口：自动增减的口改成中文名（图1、参考图1）；打开存好的工作流时，没接线的可选口（自动增减留的那个空口、没用上的参考视频）用 `removeInput` 收起来。新拖出来的节点不动，不然没法接线。
  3. 图：FilmKit 图、关键帧各加一个自己的控件，里面是一个 `<img>`，地址 `/filmkit/file?film=&rel=`，高度正好是图的高度。
  4. 视频：视频节点加一个 `<video>`，地址 `/filmkit/film?film=`（整部成片，浏览器按字节范围取），定位到 t0，放到 t1 跳回 t0，静音、循环、带控件。
  5. 提示词框：字号 12，固定高度（关键帧 112、视频 132），往下滚看全。
  6. 摆进窗口：载入 shots2comfy 出的工作流（`extra.filmkit`）后，把整镜缩放、平移到画布上没被挡住的那一块（避开左边栏、顶上的工具条，不让节点压在小地图下面），最大 100%。只在头一回打开时摆（存下来的视图还等于 `extra.filmkit.view`）；自己挪过再切回来就不动。
  7. 这些工作流的线画成直的、拐点画小、线中间不画圆点（只改画布，不动用户的设置；切到别的工作流照用户的设置画）。
  8. 跑过以后节点不变样：节点上已经有画面了，前端自带的预览不再加一份。经典画布的预览挂在 `onDrawBackground` 上，在这个节点上换成空函数；Vue 节点看 `node.hideOutputImages`（自带的 Painter、ImageCrop 也这么关）。
  9. 人在回放的节点上改了提示词、模型、时长，弹一句「这是回放，改了也不会重新生成」（一个节点一次）。多行的提示词框打字时不走控件的 callback，要在输入框上听 `input`。
- **两个只读接口**：`/filmkit/file`（运行目录里的图片、视频）、`/filmkit/film`（登记的成片）。只认登记过的片；路径跑出运行目录、后缀不是图片视频的一律 404。
- **回放读什么、交出什么**：FilmKitImage 读 `file`；FilmKitKeyframe 读登记表里这张关键帧的文件（登记表里没有这一栏时，按 `keys/<name>.png` 找；前端脚本显示时用工作流里记的 `properties.filmkit.file`）；视频节点从成片里裁出 t0–t1，交给下游的就是留下的那个文件。
- **留什么**：ComfyUI 里节点回的每一份东西（`ui`）都算一件「产出」，进历史记录、进 Assets 面板。只回这一镜自己产出的两样，存法和 SaveImage / SaveVideo 一样（文件里带着这一次的工作流，拖回 ComfyUI 就能打开这一镜）：
  - 关键帧：`output/filmkit__<片>__<关键帧名>.png`（像素原样，只多写一段工作流）；
  - 这一镜的视频：`output/filmkit__<片>__<镜头名>.mp4`（按镜头名叫：一条生成切成几镜时每镜各是一段）。
  喂进去的图不是这一镜产出的，FilmKitImage 不回；要是每个节点都回预览，跑一镜面板里会多出好几张中间图。
- **文件已经在就不重写**：源头没变（关键帧没重画；成片没重剪、这一镜的长度没变）就不动。
- **资产系统开着时只写文件，不回 `ui`**：ComfyUI 跑完以后会自己扫一遍 output，把节点写了但没报的文件登记上，开着的面板自己多出卡片（离上一次扫不到 10 秒时，等满 10 秒）。这样登记的资产不挂在某一次 Run 上：一个文件一张卡片，按文件时间排；「Open as workflow」读的是文件里带的工作流，重启以后照样打得开。回了 `ui` 的话卡片挂在那一次 Run 上，有两个毛病：前端只去问那次 Run 的记录（重启就没了，不会退回去读文件，点了没反应）；同一个文件每回一次多一张卡片（资产系统不合并）。
- **资产系统没开（`args.disable_assets`）时照回**：那种模式下面板只列这次启动以后回过 `ui` 的。
- **源头没变就不重跑**：`fingerprint_inputs` 返回（源文件的修改时间，留下的那件在不在），和 LoadImage 看文件一个道理。运行目录里的图重画了、成片重剪了、留在 output 里的那件被删了，再跑才重读、重留。生成模式照常按参数走缓存，免得重复花钱。
- **生成模式（还没做）**：FilmKitKeyframe 把接进来的图存成 PNG、写一张出图的任务单交给后端（`../backends`）；视频节点把首帧、尾帧、参考图存好、写一张视频任务单，交给后端提交并等它取回。出图、生成视频用的 key 不一定在跑 ComfyUI 的那台机器上，要先定节点怎么把任务交给那台机器。那时一次生成留一件产出（新出的那一条），和人自己跑一样。

## 伪代码

```
FilmKitImage.execute(film, file):        读 登记表[film].run/file → IMAGE
FilmKitKeyframe.execute(images{…}, prompt, size, film, name, mode):
    replay: 源 = keys/name.png；留 = output/filmkit__film__name.png
            留不在或比源旧 → 写（PNG 里带工作流）
            → IMAGE；没开资产系统才回 ui = 留
FilmKit<喂法>.execute(口…, model, prompt, duration, seed, …, film, name, mode, t0, t1, shot):
    replay: 留 = output/filmkit__film__shot.mp4
            留不在、比成片旧、或长度和 t1 − t0 差 0.2 秒以上 → 成片.as_trimmed(t0, t1 − t0).save_to(留，带工作流)
            → VIDEO（留下的那个文件）；没开资产系统才回 ui = 留
fingerprint_inputs = (源文件的修改时间, 留在不在)        # generate 时 = mode

前端脚本
  loadedGraphNode(节点): 收起空口；藏 advanced 参数；口改中文名；提示词框定高；
                         图节点加 <img>（/filmkit/file），视频节点加 <video>（/filmkit/film，在 t0–t1 里循环）；
                         有了自己的画面 → 关掉前端自带的预览；提示词、模型、时长被改 → 提示一句「这是回放」
  afterConfigureGraph(): 是我们的工作流 → 线画直、拐点画小；头一回打开 → 摆进看得见的那块
      看得见的那块 = 画布 − 左边栏（.side-tool-bar-container、.side-bar-panel）− 顶上（.workflow-tabs-container、.actionbar）
      scale = min(1, 宽 / 框宽, 高 / 框高)；有节点压在小地图（.minimap-main-container）下面就再乘 0.95，直到不压
```

## 踩过的坑

- **软链不行**：ComfyUI 0.46 校验文件路径两边都取 realpath，input、output 里指到外面的软链一律当成不存在（「Invalid image file」）。所以留下的东西只能是真文件。
- **留在子目录里的文件插不成节点**：资产系统开着时，前端 1.59 把 Assets 卡片插成 LoadImage / LoadVideo 只取文件名，丢掉子目录（`filmkit/片/k_S22.png` 变成 `k_S22.png [output]`）。留下的文件放 output 最上层，片名写进文件名。
- **回了 `ui` 的卡片，重启后点不回工作流**：只在第一次落地时回一次 `ui`，卡片一镜一张、叠着关键帧和视频，看着整齐；但重启 ComfyUI 以后右键 Open as workflow 没反应（`/api/jobs/<号>` 404，前端不再去读文件）。所以资产系统开着就不回。
- **回了 `ui` 节点就多一份预览**：经典画布给有产出的节点自动加预览控件（最少 220 高），节点被撑高、画面出现两遍。有自己画面的节点要把它关掉（见上面第 8 条）。
- **种子控件**：叫 seed 的 INT 参数，前端自动在后面加一个 control_after_generate 控件，工作流里要给它占一格（`"fixed"`）；藏 seed 时要连它一起藏。
- **advanced 标记前端不认**：1.59 的经典画布照样显示，只把字调淡；要自己藏。
- **前端自带的图片预览最少占 220 高**（给 `node.imgs` 赋值就走它）：小图节点被撑到 246 高，排好的位置全叠在一起。所以用自己的控件（`addDOMWidget`，`getMinHeight` = `getMaxHeight` = 画面高 + 2×边距，`serialize: false`，`margin` 6）。`<img>` 设 `pointer-events: none`，点在图上照样能拖节点、滚轮缩放。
- **带控件的节点最窄 210**（LiteGraph 的 140×1.5），工作流里写 200 也会被撑到 210。
- **控件之间不留缝**：口一行 20，第一个控件从 20×口数+6 开始，节点底下留 8。照这个算节点高度，前端打开后一个像素都不改。
- **视频循环别用 timeupdate**：一秒只来四次，会多放出下一镜的几帧；用 `requestVideoFrameCallback` 每帧看一眼。
- **前端脚本**：模块里写 `WEB_DIRECTORY = "./web"` 就行，新接口的节点包也认。改 js 不用重启 ComfyUI（刷新页面就行），改 Python 要重启。

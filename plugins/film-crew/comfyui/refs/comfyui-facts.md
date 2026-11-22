# ComfyUI：对接时用到的事实

都是 2026-11-19 查的；版本变了先重查。

## 官方自己的白模片：图里只有「喂 + 生成」

- [Comfy-Org/workflows](https://github.com/Comfy-Org/workflows) 的 Haunted Subway（21 秒恐怖短片，Seedance 2.5）：整张图 7 个节点，4 个 LoadImage + 1 个 LoadVideo（21 秒的 3D 白模视频）→ 1 个 `ByteDance2ReferenceNodeV2` → SaveVideo。白模在 Blender 里做好、提示词写好（每张参考图管什么、不许管什么），才放进图里。同仓库还有 Halloween SD（白模 + 7 张参考图）。
- 这说明：ComfyUI 的图擅长的是最后一段；前面的判断（搭白模、分配参考、写提示词）在图外面。这也是我们只把「算」做成节点的理由。

## 工作流文件格式（UI 格式，0.4 版）

- 顶层：`id, revision, last_node_id, last_link_id, nodes, links, groups, config, extra, version`（前端 1.59.6 自己存时还多 `floatingLinks`、`definitions`）。
- 节点：`id, type, pos, size, flags, order, mode, inputs, outputs, properties, widgets_values, title`；前端 1.59.6 存的 `inputs` 里每个参数也占一项（带 `widget: {name}`），官方仓库里的文件只写了连线的口，两种都能打开。
- 连线：`[连线号, 起点节点, 起点口, 终点节点, 终点口, 类型]`；组：`{id, title, bounding: [x, y, w, h], color, flags}`。
- 前端 1.59.6 里新建的 SaveVideo，`widgets_values` 是 `["video/ComfyUI", "auto", "auto", "auto"]`；Note 是 `[文本]`。

## Partner 节点（原来叫 API 节点）

- Seedance 2.5、Wan 3.0、Kling、MiniMax 等都有官方 Partner 节点，[2026-08 起有 Seedance 2.5](https://blog.comfy.org/p/seedance-25-is-now-available-via)；[价格表](https://docs.comfy.org/tutorials/partner-nodes/pricing)。
- 本地 ComfyUI 跑 Partner 节点也要登录 Comfy 账号、扣 Comfy Credits，任务经 Comfy 转给模型方；不能填我们自己的 key。
- 同一个工作流里互不依赖的 Partner 节点会[自动并行](https://support.comfy.org/articles/5762992921-partner-nodes-concurrency)；本地 ComfyUI 的队列一次跑一个工作流。
- 11-12 的版本加了 `--disable-partner-nodes`（[更新日志](https://docs.comfy.org/changelog)）。

## 让 agent 开 ComfyUI

- [Comfy MCP](https://docs.comfy.org/agent-tools/mcp)（2026-06 公测）：本地版 `pip install comfy-mcp`，默认连 `127.0.0.1:8188`，工具有 run_workflow（API 格式或 UI 导出都收）、fetch_outputs、validate_workflow、search_templates；云版连 Comfy Cloud。
- [Comfy Agent](https://docs.comfy.org/agent-tools/in-app-agent)（2026-10）：ComfyUI 里自带的聊天助手，能贴 SKILL.md 当个人 skill；只在 Comfy Cloud 上，本地版还没出，用 Comfy Credits。我们的 skill 是几百个文件加脚本加 Blender，贴不进去。
- 这里没用 MCP：核对和回放直接用前端（`app.graphToPrompt`、`app.api.queuePrompt`），见 [methods/05-check.md](../methods/05-check.md)。

## 循环和条件

- [2026-09-15 起有原生循环](https://comfyui-wiki.com/en/news/2026-09-15-comfyui-workflow-loops)（Start Loop / End Loop，按次数、区间或列表转，带一个传递值）；没看到能按条件提前停。「看一眼片子决定重不重抽」这种判断本来就不在节点里。

## 3D：以后放白模用

- [Load 3D & Animation](https://docs.comfy.org/built-in-nodes/Load3D) 是核心节点：读 gltf/glb/obj/fbx/stl，节点里就是一个能转、能缩放、能播动画的 3D 查看器，输出相机参数。白模导成 GLB 就能放进来；我们的人偶动画导出后能不能播还没试。
- 社区的 Blender 桥：[blender-in-comfyui](https://github.com/JayLyu/blender-in-comfyui)（节点里无界面调 Blender 渲图，要 `--allow-subprocess`）、[ComfyUI-Blender](https://github.com/alexisrolland/ComfyUI-Blender)（反过来，在 Blender 里跑 ComfyUI 工作流）。

## 版本里的几处行为（实测，0.46.0 / 前端 1.59.6）

- 路径校验两边都取 realpath：input、temp 里指到外面的软链一律当成不存在。
- 前端拿 LoadImage / LoadVideo 的值去对下拉列表（只列 input 最上层），对不上报 Missing Inputs、不让跑。
- 缓存按输入的签名；同样的输入在另一个工作流里直接用缓存，前端收不到那个节点的预览。
- 输入标 `advanced=True`，经典画布照样显示（只把字调淡）；前端有个设置 `Comfy.Node.AlwaysShowAdvancedWidgets`（默认关），但不管经典画布。要藏得自己在前端脚本里设 `widget.hidden = true`。
- `io.Autogrow`（`TemplatePrefix(input, prefix, min, max)`）的口名是 `<输入名>.<前缀><序号>`，序号从 0 起，比如 `images.image0`；接满一个自动多一个空口，执行时收到字典。
- 新接口的节点包也能带前端脚本：模块里写 `WEB_DIRECTORY = "./web"`；也能挂自己的接口：`PromptServer.instance.routes.get(...)`。
- 前端脚本里给节点设 `node.imgs = [Image]`，经典画布就把它当预览画出来，不用先跑。
- 每个自定义节点头上默认挂一个来源标签（包名），设置 `Comfy.NodeBadge.NodeSourceBadgeMode` 设成 `None` 就不显示。
- 前端会在叫 seed 的 INT 参数后面自动加 control_after_generate，默认 randomize。
- **节点回的每一份预览都是一件产出**：`io.NodeOutput(..., ui=...)` 里的图、视频进历史记录（`/history`），左边栏 Assets 的 Generated 里一次运行一张卡片、几件叠在一起；temp 里的预览也算。不是输出节点的节点回了 `ui` 也算。历史记录在内存里，重启就清。
- **给 `node.imgs` 赋值走前端自带的图片预览，最少占 220 高**（`$$canvas-image-preview` 控件）：节点比这矮会被前端撑高。要小图就自己 `node.addDOMWidget(名字, 类型, 元素, {serialize: false, margin, getMinHeight, getMaxHeight})`，元素实际高度 = 控件高度 − 2×margin（margin 默认 10）。
- **带控件的节点最窄 210**（LiteGraph `NODE_WIDTH` 140 × 1.5）。口一行 20；第一个控件从 20×口数+6 开始；普通控件（下拉、数字）一行 24，控件之间不留缝；多行文本框是自己伸缩的，`widget.options.getMinHeight / getMaxHeight` 能把它定死。
- **画布铺满整个窗口，侧栏盖在它上面**：左边图标栏 56 宽（`.side-tool-bar-container`），点开一个面板再加 312（`.side-bar-panel`）；顶上标签栏 38 高（`.workflow-tabs-container`），工具条到 82（`.actionbar`）；右下角小地图 253×200（`.minimap-main-container`）。1600×900、侧栏开着时看得见的是 1208×798。
- **前端的「适应窗口」**（`Comfy.Canvas.FitView`）按整块画布算，不管侧栏，而且只用到 0.75 的地方。工作流里存了 `extra.ds`（`{scale, offset}`）的，打开时照它摆（设置 `Comfy.EnableWorkflowViewRestore` 默认开）；屏幕坐标 = (图上坐标 + offset) × scale。
- **字什么时候不画**：字号 × 缩放小于 `LiteGraph.Canvas.MinFontSizeForLOD`（默认 8）就不画节点上的字，实测缩放 0.6 上下。
- **拐点（reroute）是自带的**，不用装节点。0.4 版格式里写在 `extra.reroutes`：`{id, pos, linkIds, parentId?}`，一串拐点靠 `parentId` 从目标往来源连；`extra.linkExtensions`：`{id: 线号, parentId: 这根线最后经过的拐点}`。几根线可以共用一串拐点，到最后一个再分开。拐点的圆点半径是 `LiteGraph.Reroute.radius`（默认 10）。
- **线的画法是全局设置** `Comfy.LinkRenderMode`（0 折线、1 直线、2 曲线，默认 2），画布上是 `app.canvas.links_render_mode`。曲线模式下拐点的切线方向取前后两段的平均，横着穿过一列时会往一边鼓 20 多像素；直线模式拐点之间就是直线。线中间的小圆点是 `app.canvas.linkMarkerShape`（设置 `Comfy.Graph.LinkMarkers`）。
- **分组框**：`groups` 里一项 `{id, title, bounding: [x, y, 宽, 高], color, font_size, flags}`。标题用框的颜色画，缩得再小也画；颜色太深标题就看不见。
- **`app.loadGraphData` 之后**前端先按 `extra.ds` 摆视图，再调扩展的 `afterConfigureGraph`；想自己摆，等两帧再动。切回一个已经开着的标签页也会再走一遍，这时 `extra.ds` 是那个标签页上次的视图。
- **前端刷新后会接着打开上次开着的工作流**。里面有在放的视频时网络一直不空闲，自动化脚本别等 networkidle。
- **Workflows 面板**只列文件名（不带 `.json`），按名字排；名字放不下时，选中的那一行自己滚动着显示。文件名可以有中文、空格、全角标点。
- 一个 `<video>` 直接放 50 MB 的成片里的 4 秒：先取开头 2 MB（文件头），再从这一镜的位置往后取，12 秒里一共约 13 MB（浏览器会往后多缓冲）。`web.FileResponse` 自己支持按字节范围取。切到别的工作流时节点的 `onRemoved` 会被调，在里面把视频停掉、清掉地址。

## Assets 面板和资产系统（0.46.0 / 前端 1.59.6，2026-11-19 读代码加实测）

- **面板从哪读**（前端 `assetsStore`）：
  - 没开资产系统（默认）：Generated = `/api/jobs` 里跑完、带预览的任务，一个任务一张卡片（封面是第一件 output 类型的产出）；Imported = `/internal/files/input`，只列 input **最上层**的文件。历史在内存里，重启后 Generated 是空的，人自己的产出也一样。
  - 开了资产系统（`--enable-assets`，Windows 整合包默认开；`/api/features` 里 `assets: true`）：两栏都读库（`/api/assets?tags_any=output,temp` / `input`，再加 `tags_none=missing`）。启动时扫 models、input、output（含子目录），库在 `user/comfyui.db`，重启后还在。同一个任务的几件叠成一张卡片，封面是这个任务最后出的那件（我们这里是视频）；没有任务号的（扫出来的）一件一张。标了 `missing` 的不显示。
- **面板一次只加载最近 100 件**（`/api/assets?limit=100&sort=created_at`），往下滚才加载更多；上面的搜索框只在已经加载出来的里面找。往 input 里放两百多张图，早先扫进去的那十几张就滚不到、搜不到。
- **卡片上能干什么**（右键）：Inspect asset、Insert as node in workflow（图 → LoadImage，视频 → LoadVideo，值是 `文件名 [output]`，input 里的不带后缀）、Download、Open as workflow in new tab、Export workflow、Copy job ID、Delete。
- **Open as workflow** 读的是这次任务带的工作流，或者文件里写的（PNG 的文本块、mp4 的元数据）。所以存文件时照 SaveImage / SaveVideo 的做法把 `extra_pnginfo`、`prompt` 写进去（节点定义里要 `hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo]`），扫出来的、没有任务号的文件也点得回它的工作流。
- **子目录的坑**：开着资产系统时，前端把卡片插成节点用的是 `user_metadata.subfolder`（扫出来的、跑出来的都是空），服务器给的 `loader_path`（带子目录）只拿来取缩略图。`output/filmkit/片/k_S22.png` 插出来是 `k_S22.png [output]`，读不到（跑出来的、扫出来的两种卡片都试过）。照同一段代码，自带的 SaveVideo 默认存进 `video/` 的文件也会这样（没单独试）。要让人插得成，文件放最上层。
- **同一个文件的几次产出不合并**（`asset_enrichment.py` 里写明了）：每个回了这份文件的任务各记一笔，面板里各一张卡片。走缓存的那次，输出节点缓存下来的 `ui` 会原样再报一遍。
- **挂在任务上的卡片，重启后点不回工作流**：前端（`extractWorkflowFromAsset`）见资产带任务号就只问 `/api/jobs/<号>`，问不到就算了，不会退回去读文件。任务记录在内存里，重启就没，所以人自己用 SaveImage 存的图重启后也点不回。不带任务号的资产才去取文件、读里面的工作流（PNG、mp4 都试过）。
- **ComfyUI 跑完以后自己扫一遍 output**（`main.py` 里 `asset_manager.queue_output_scan()`，注释写的是「找节点没申报的产出」）：节点写了文件但没回 `ui`，也会登记进库，不带任务号，`created_at` 用的是文件的修改时间（面板就按它从新到旧排）。同一个路径原来挂在任务上的那条会被标成 `missing`。
  - 这遍扫描挂在跑完以后的内存清理上，清理最多 10 秒一次：离上一次超过 10 秒，跑完马上扫；不到 10 秒，等到满 10 秒。370 个文件扫一遍 0.01～0.2 秒。
  - 面板开着会自己多出卡片，不用刷新：实测跑完后 0.6 秒出现；紧接着再跑一次，5.8 秒。
- **每次打开或刷新页面也全扫一遍**：前端取 `/object_info` 时，服务器把 models、input、output 扫一遍（386 个文件 0.22 秒）。拷进 input 的图，人下一次打开页面就列出来了。
- **删掉一条资产记录是记死的**：`DELETE /api/assets/<id>` 只删记录、不删文件，之后再扫也不会把这个文件登记回来。想让一批文件重新登记，只能停掉 ComfyUI、删 `user/comfyui.db*` 再起（启动时全扫一遍）。
- **原地重写的文件，跑完那遍扫描不认**：那遍只登记新路径，已经登记过的路径直接跳过（日志里 `created=0 enriched=0`），记录里还是旧的大小和时间，卡片不动。有人打开或刷新页面时的全扫才重新登记：一条新记录（时间是登记的那一刻），排到最上面，旧的那条不再显示，不会出两张。`/api/view`、我们的 `/filmkit/file` 都带 ETag 和 Last-Modified，文件变了浏览器会取新的。
- **文件删了，记录变成 `missing`**：下一遍扫描把它标成 missing，卡片就没了，不用去删记录。撤掉放进去的东西就这么做。
- **预览节点的图也进 Generated**：资产系统开着时面板列的是 output 和 temp 两种标签。自己做试验接了 PreviewImage，跑完要把那批 temp 记录和 `temp/` 里的文件清掉。
- **产出怎么进库**：节点回 `ui` 的那一刻按路径登记、记上任务号；节点没报、直接写进 output 的，跑完那遍扫描会登记；别的时候放进目录的文件（比如拷进 input 的）要等下一次扫（启动时、有人打开页面时，或 `POST /api/assets/seed`，body `{"roots": ["input"]}`，加 `?wait=true` 等它扫完）。列表接口 `/api/assets` 一次最多 500 条，翻页用返回的 `next_cursor` 填 `after`；`name_contains` 按文件名找；`/api/assets/seed/status` 看扫描在不在跑。
- **不开浏览器排队跑一镜**：`POST /prompt`，body `{"prompt": {"<节点号>": {"class_type", "inputs", "_meta": {"title"}}}, "extra_data": {"extra_pnginfo": {"workflow": <UI 格式的工作流>}}}`，再 `GET /history/<prompt_id>` 等结果。
  - `inputs` 里参数按名字给，线写 `["<来源节点号>", 第几个出口]`；能自动增减的口叫 `images.image0`、`refs.ref0`……；没接线的可选口不写；前端自己加的那一格（seed 后面的 control_after_generate）不发。
  - `extra_pnginfo.workflow` 就是节点里 `io.Hidden.extra_pnginfo` 拿到的那份，照 SaveImage 的做法写进文件，卡片的 Open as workflow 打开的就是它。
  - 照这个拼出来的和前端 `app.graphToPrompt()` 转出来的，四种喂法逐个对过，都相同。
  - 服务器上常设着 `http_proxy`，发给 127.0.0.1 的请求也会被送去代理；用不带代理的 opener。
- **有自己画面的节点怎么不让前端再加预览**：经典画布的预览挂在节点原型的 `onDrawBackground` 上（`updatePreviews`），在节点实例上换成空函数；Vue 节点看 `node.hideOutputImages = true`（自带的 Painter、ImageCropV2、ImageCompositor 就这么关）。经典画布那条路不看 `hideOutputImages`。
- **多行文本框打字不走 `widget.callback`**：要知道人改了，在 `widget.element`（textarea）上听 `input`。提示用 `app.extensionManager.toast.add({severity, summary, detail, life})`。
- **打开工作流不会被标成已修改**：前端脚本在 `loadedGraphNode` 里收口、在 `afterConfigureGraph` 以后改视图，`activeWorkflow.isModified` 都还是 false。
- **人存工作流**（Ctrl+S / `Comfy.SaveWorkflow`）是整份重写到原路径；`extra` 里不认识的键（我们的 `extra.filmkit`）原样留着。
- **裁视频**：`VideoFromFile(path).as_trimmed(t0, 时长).save_to(...)` 带了起止就一定重新编码（按帧裁，准）；不带起止、容器和编码都不变时是直接拷流。一镜（一张 1672×941 的关键帧 + 1280×720 的 4 秒）头一回跑 2.6～4.4 秒，文件已经在以后 0.1～1.2 秒。

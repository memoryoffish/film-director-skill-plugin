# scripts

| 脚本 | 在哪跑 | 做什么 |
|---|---|---|
| [shots2comfy.py](shots2comfy.py) | 有 ComfyUI、读得到图和成片的服务器 | **给拍片 skill 的接口**：收镜头清单，登记；每镜写一个 ComfyUI 工作流（排好位置和走线，文件名带上拍什么）；跨镜头用的参考图、基准画面拷进 input（Assets 的 Imported）；把每镜排队跑一遍，关键帧和视频留在 output（Generated）；写回执。人存过的工作流不盖，挪成「镜头名（人改过）…」并报出来；`--prune` 只删没人动过的旧工作流和 input、output 里用不到的 `filmkit__` 文件。不认识任何 skill 的目录。 |
| [check_in_comfy.py](check_in_comfy.py) | 能开到 ComfyUI 网页的地方（本机经隧道） | 这一块自己的验收：在真前端里先点开左边栏，再逐个打开工作流，核对节点类型、连线、参数；打开时看得全不全、线有没有从节点背后过、有没有空口、图和视频出来没有；`--run` 再点一遍回放，看该留的在不在、Assets 面板里有没有它的卡片、多留了没有、节点变样没有；`--shots` 截打开时的样子。有问题退出码 1。 |

拍片运行目录怎么变成清单：[../formats/read_run.py](../../formats/read_run.py)。手写清单的例子：[../formats/examples/manifest/demo.shots.json](../../formats/examples/manifest/demo.shots.json)。

```bash
# 服务器上：把清单交给 ComfyUI。COMFYUI_DIR 说 ComfyUI 在哪；地址不是 127.0.0.1:8188 再设 COMFYUI_URL
export COMFYUI_DIR=<ComfyUI 目录>
python3 scripts/shots2comfy.py <清单.json…> [--shots S22] [--prune] [--index <回执>] [--no-run]

# 本机：经隧道核对、回放、截图（要装了 playwright 的 Python）。文件名带空格和中文，整个加引号
<装了 playwright 的 python> scripts/check_in_comfy.py "filmkit/zz_demo/S3 她把杯子放到桌上.json" --run --shots /tmp/comfy-shots
```

- `shots2comfy.py` 只用标准库，系统 Python 就能跑；写登记表要对节点包目录有写权限。清单的格式写在它开头，讲法在 [methods/00-interface.md](../methods/00-interface.md)。
- 回执（`--index`，默认 `<comfy>/user/filmkit_index.json`）里每镜有工作流文件名、喂法、节点数、打开时的缩放、跑一遍会留在 output 里的文件名（`kept`）、这一次跑成了没有（`run`）。全量验收就照它列的文件名跑。
- `check_in_comfy.py` 的工作流参数可以是 ComfyUI 用户目录里的路径（`user/default/workflows/` 下面），也可以是本机的 json 文件（比如网页上导出的）。

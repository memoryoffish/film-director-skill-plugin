# 00 接口：skill 交一份清单，ComfyUI 这一头照着放

一句话：拍片的 skill 和 ComfyUI 之间只有一份「镜头清单」和一条命令。skill 不用知道 ComfyUI 的任何事，ComfyUI 这一头也不认识 skill 的目录；人在 ComfyUI 里看和拿，要调整就告诉 agent，agent 改完把清单再交一次。

## 推荐

**两边各管各的**：

| 谁 | 管什么 | 不碰什么 |
|---|---|---|
| 拍片的 skill（video-film-maker、blender-previz 等） | 怎么拍；每一镜用了什么、出了什么；人说要调整时怎么改 | 不写任何 ComfyUI 的东西（节点、工作流、往哪放） |
| ComfyUI 这一头（本目录） | 节点包、一镜怎么摆、文件放哪、留哪些资产、在真前端里验收 | 不认识任何 skill 的目录结构；不调生成接口；不动 skill 的文件 |
| 中间 | 清单（skill 写）、`scripts/shots2comfy.py`（这里给的命令）、回执（命令写回来） | |

- **清单里写什么**：一部片一个 json。片：`film`（key）、`title`、`root`（放图的目录）、`video`（成片）。每一镜：`name`、`what`（拍什么）、`t0`、`t1`（在成片里的起止），再加三样：
  - `video`：这一镜的视频怎么生成的——喂法 `feed`（T2V / I2V / FLF2V / R2V）、它直接用的图（`first`、`last`、`refs`）、模型、提示词、时长、生成了几次（`takes`）；
  - `keyframes`：视频直接用的图里，这一镜自己出的关键帧——提示词、用到的图（`inputs`）、重画了几次；
  - `images`：其余每张现成的图是什么——`kind`（wm 白模静帧 / ref 参考图 / key 别的镜头的关键帧 / img 其他）和节点标题 `title`。

  完整格式在 [scripts/shots2comfy.py](../scripts/shots2comfy.py) 开头和 [../formats/shots-manifest.md](../../formats/shots-manifest.md)；手写的例子是 [../formats/examples/manifest/demo.shots.json](../../formats/examples/manifest/demo.shots.json)，写完可以用 `../formats/check_manifest.py` 查一遍。
- **还没有视频任务的镜头**（清单里那一镜不写 `video`）：不出工作流，命令最后把这几镜列出来；别的镜头照常。
- **清单里写什么，ComfyUI 里就是什么**：「每镜只放必要的」由写清单的那一边定——别的镜头的关键帧写成一张图（标题说它是谁的），不往上追；没喂进去的白模、全片预演不写。
- **一条命令**：`shots2comfy.py <清单…>`。登记、出工作流、把跨镜头的图放进 input、把每一镜排队跑一遍（回放，只读文件），关键帧和视频就留在 Assets 面板里了。只发几镜用 `--shots`。ComfyUI 在哪由环境变量 `COMFYUI_DIR`、`COMFYUI_URL` 定，skill 不用管。
- **回执**：命令跑完写一份 json（`--index`）：每镜的工作流文件、喂法、节点数、打开时的缩放、留下的文件名、这一次跑成了没有。agent 拿它告诉人去哪看。
- **名字是 skill 起的**：清单里的镜头名、关键帧名、任务名原样显示在 ComfyUI 里（工作流名 `S3 她把杯子放到桌上`、节点标题 `首帧 · k_S3`、卡片名 `filmkit__<片>__k_S3`）。人说「S3 的首帧手不对」，说的就是 skill 自己的名字，agent 不用懂 ComfyUI 就知道是哪张。
- **人不在 ComfyUI 里改**：要调整，人告诉 agent 哪一镜、哪张图；agent 用 skill 自己的工具改（重画关键帧、重抽、重剪），把清单再交一次（`--shots` 那几镜）。ComfyUI 这一头不生成、不读人在工作流里改了什么。保底的两样留着：在回放节点上改参数，前端提示一句「这是回放」；人存过的工作流不盖。
- **运行目录由 `../formats/read_run.py` 读成清单**：拍片 skill 还不会自己出清单，[../formats/read_run.py](../../formats/read_run.py) 替它把运行目录读成清单，再交给这里。别的流程照格式直接写清单。
- **撤掉一部片**：删掉放进去的文件（`workflows/filmkit/<片>/`、input 和 output 里的 `filmkit__<片>__*`），登记表里去掉这部片；下一遍扫描卡片就没了。不要去删资产记录：删过的记录是记死的，同名文件以后再放进来也不出卡片。

## 伪代码

```
skill（或替它干活的桥）:
    清单 = {film, title, root, video, shots: [{name, what, t0, t1, video, keyframes, images}]}
    shots2comfy 清单 [--shots 改过的那几镜]        # 回执里看每镜跑成了没有

shots2comfy:
    登记：film → root、成片、关键帧名 → 文件
    for 镜: 建图 → 摆 → 写工作流（人改过的那份挪开）
    跨镜头用的图 → input（Imported）
    for 镜（倒着排）: 排队跑一遍 → 节点包把这一镜的关键帧、视频留在 output（Generated）；已经在、没变的不重写
    回执：每镜 {file, feed, nodes, scale, kept, run}

人: 在 ComfyUI 里看、拿；要调整 → 告诉 agent「哪一镜、哪张图、怎么改」
agent: 用 skill 的工具改文件 → 清单再交一次 → 告诉人去看
```

## 实测（ComfyUI 0.46.0）

- **手写清单**（图放在自己的目录里，不是拍片 skill 的结构）：首帧生视频、文生视频各一镜，一条命令放进去，在真前端里都过检查。
- **调整一轮**：换掉首帧那张图、清单里改一句提示词，`--shots A1` 再交，0.8 秒。重新打开页面：这一镜的关键帧节点是新图、新提示词；Generated 里这张关键帧排到最上面，旧卡片没了；视频没变，不重写。
- **排队的格式**：命令自己拼的（`api_prompt()`）和前端转出来的，逐镜相同。
- **再交一次**：文件都在时带 `--prune` 再交，什么都不删、不重写。
- **撤掉一部片**：删文件、扫一遍，这部片的卡片都没了，别的片的不受影响。

## 局限

- `../formats/read_run.py` 靠文件名和目录认东西（重抽按后缀归到同一镜、关键帧按名字认是哪一镜的）。skill 自己出清单就不用猜。
- 清单里的 root、成片要是跑 ComfyUI 的那台机器上读得到的路径。
- 改过的文件，卡片要等有人打开或刷新一次页面才换成新的（那时 ComfyUI 才重新登记它）。

# formats：两份交接文件的格式

一句话：拍片的方法、调模型的后端、给人看的查看器，三样之间只靠两份文件来往；这里是这两份文件的格式，和把拍片运行目录读成镜头清单的脚本。路径都相对本目录。只用 Python 标准库。

## 两份文件

| 文件 | 写什么 | 谁写 | 谁读 | 格式 |
|---|---|---|---|---|
| 任务单 | 一次生成要什么：提示词、用到的图和视频、几秒、多大、想用哪个模型 | 拍片的 agent（拍片 skill 写的任务文件不用改就是） | 后端 [../backends](../backends/overview.md) | [job-sheet.md](job-sheet.md) |
| 镜头清单 | 一部片每一镜用了什么、出了什么 | [read_run.py](read_run.py) 从运行目录读出来；别的流程自己照格式写也行 | 查看器：[../comfyui](../comfyui/overview.md)、[../viewer](../viewer/overview.md) | [shots-manifest.md](shots-manifest.md) |

1. **格式跟着拍片时本来就有的文件定。** 任务单的字段就是拍片时写的任务文件里那些；镜头清单由这边读拍完留下的运行目录得到。
2. **格式里只写事实。** 哪个模型收什么，在后端的能力卡里；图在页面上怎么摆，是查看器的事。
3. **运行目录只在一处读。** 认识运行目录长什么样的代码只有 `read_run.py`。文件的放法换了，只改它。

## 怎么用

```bash
# 查任务单（--root 给了项目目录，再查单子里写的文件在不在）
python3 check_job.py <项目>/jobs/*.json <项目>/jobs_img/*.json --root <项目>

# 运行目录 → 镜头清单（CONFIG 里写每部片的运行目录、成片、预演）
python3 read_run.py CONFIG.json --out manifests/

# 查镜头清单
python3 check_manifest.py manifests/*.shots.json
```

查出问题时逐条打印，退出码 1。检查只看格式，不看某个模型收不收、图画得对不对。

清单读出来以后交给谁：ComfyUI 是 `../comfyui/scripts/shots2comfy.py`，网页是 `../viewer/scripts/console.py`。任务单交给 `../backends/scripts/filmgen.py`。

## 运行目录里要有什么

`read_run.py` 读的文件列在它开头的说明里，都只读。拍片时本来就会留下的：`jobs/`（视频任务）、`keys/`（关键帧和出图记录）、`wm/`（白模静帧）、`refs/`（参考图）、`clips/`（每一次生成的结果）。

**镜头表 `meta.json` 要另外写一份**，放在运行目录里。拍完以后照分镜和剪辑结果写：每一镜叫什么、在成片里从第几秒到第几秒、拍的是什么、用的是哪条视频任务。

```json
{"title": "片名", "genre": "类型", "model": "用的视频模型",
 "shots": [{"name": "S1", "t0": 0.0, "t1": 4.0, "what": "这一镜拍什么", "job": "v1"},
           {"name": "S2", "t0": 4.0, "t1": 8.0, "what": "…", "job": "v2"}]}
```

- `job` 写这一镜用的视频任务名（`jobs/` 里那份文件的 `name`）；一条生成切成两镜时，两镜写同一个名字。
- 还没开拍、只想先看分镜时写 `"plan": true` 和 `"seconds"`（片长）。

## 文件

| 在哪 | 是什么 |
|---|---|
| [job-sheet.md](job-sheet.md)、[check_job.py](check_job.py) | 任务单的格式和检查 |
| [shots-manifest.md](shots-manifest.md)、[check_manifest.py](check_manifest.py) | 镜头清单的格式和检查 |
| [read_run.py](read_run.py) | 运行目录 → 镜头清单 |
| [examples/](examples/overview.md) | 手写的任务单和镜头清单 |

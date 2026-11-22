# film-crew

[English](README.en.md) · **中文**

写代码的 agent 拍片时，[film-director](../../skills/film-director) 这个 skill 管方法：怎么计划、怎么拍、怎么剪。film-crew 管方法以外的事：调视频和图像模型，拍的时候让人看到进度，拍完让人看到每一镜喂进去了什么、出来了什么。

一步装完。不装 skill 也能用：只要按下面两份交接文件的格式写，别的流程也能接进来。

## 里面有什么

| 部分 | 做什么 | 先读 |
| --- | --- | --- |
| `backends/` | 收一张任务单（一份 JSON，写一次生成要什么），去调这个模型的官方接口。`request` 只把要发的请求原样打印出来，什么都不发。每个模型有一张能力卡：收什么输入、单条几秒、几张参考图、多少钱。 | [backends/overview.md](backends/overview.md) |
| `viewer/` | 把一部片的运行目录做成网页。拍片进行中是进度页：每一次生成都能直接播，顶上写已经花的时间和钱。剪完以后是展示台（每一镜的输入和它在成片里的那几秒并排放）和节点图（每一镜谁喂给了谁）。 | [viewer/overview.md](viewer/overview.md) |
| `comfyui/` | 每一镜在 ComfyUI 里打开成一份工作流：用到的图 → 这一镜的关键帧 → 一个视频节点，节点上播这一镜。只回放。关键帧、片段、参考图留在 Assets 面板里，人可以拿去接着用。 | [comfyui/overview.md](comfyui/overview.md) |
| `formats/` | 两份交接文件的格式和检查脚本，以及把运行目录读成镜头清单的脚本。 | [formats/overview.md](formats/overview.md) |

四个部分之间只靠两份文件来往：

- **任务单**：一次生成要什么（提示词、图、几秒、多大、哪个模型）。agent 写，`backends/` 读。
- **镜头清单**：一部片每一镜用了什么、出了什么。`formats/read_run.py` 从运行目录读出来，`viewer/` 和 `comfyui/` 读它。

agent 从 [SKILL.md](SKILL.md) 读起。给 agent 读的文件（`SKILL.md` 和各部分的 `overview.md`）是中文写的。

## 安装

**Claude Code：**

```bash
claude plugin install film-crew --marketplace memoryoffish/film-director-skill-plugin
```

这条命令会先把仓库登记成插件市场（还没登记的话），再安装。你的 Claude Code 不认 `--marketplace` 时，先跑 `claude plugin marketplace add memoryoffish/film-director-skill-plugin`，再跑 `claude plugin install film-crew@film-director`。

**其他 agent。** 把 `plugins/film-crew` 拷贝或软链接到 agent 的 skills 目录，比如 `~/.claude/skills/`、`~/.agents/skills/`。

**需要什么。** Python 3.10+ 和 ffmpeg。展示台另要 Pillow。`comfyui/` 要你自己装好的 ComfyUI。把任务送到另一台机器上跑（`send`）要 ssh，那台机器上要有 tmux。

**key。** 每个适配从环境变量读自己的 key，不打印、不保存。仓库里不带任何 key。`request` 不设 key 也能用。

| 模型 | 官方接口 | key |
| --- | --- | --- |
| Wan 3.0、HappyHorse 1.1 | 阿里云百炼（DashScope） | `DASHSCOPE_API_KEY` |
| Seedance 2.5、Seedance 2.0 | 火山方舟 | `ARK_API_KEY` |
| MiniMax H3-Max | MiniMax | `MINIMAX_API_KEY` |
| gpt-image 2.6 | OpenAI Images | `OPENAI_API_KEY` |

默认地址是各家的官方地址。要换地域或站点，设 `DASHSCOPE_BASE_URL`、`ARK_BASE_URL`、`MINIMAX_BASE_URL`、`OPENAI_BASE_URL`。

## 怎么用

`<crew>` 是本目录，`<project>` 是拍这部片的目录。

1. **开拍时起进度页**，放在 tmux 里一直跑：

   ```bash
   python3 <crew>/viewer/scripts/progress.py <页面目录> --jobs <project>/clips \
       --prices <crew>/backends/cards/prices.json --every 60
   ```

2. **生成。** 每一次生成写一张任务单，放进 `<project>/jobs/`（视频）或 `<project>/jobs_img/`（图）。先看会发什么，再跑：

   ```bash
   cd <project>
   python3 <crew>/backends/scripts/filmgen.py request jobs/v01.json   # 打印会发出去的请求
   python3 <crew>/backends/scripts/filmgen.py run jobs/v01.json       # 片段放进 clips/
   ```

3. **剪完以后写一份镜头表** `meta.json`，放在运行目录里：每一镜叫什么、在成片里从第几秒到第几秒、出自哪张任务单。拍片的 skill 不会自己写这份文件。格式在 [formats/overview.md](formats/overview.md)。然后把运行目录读成清单：

   ```bash
   python3 <crew>/formats/read_run.py films.json --out manifests/
   python3 <crew>/formats/check_manifest.py manifests/*.shots.json
   ```

4. **给人看。**

   ```bash
   python3 <crew>/viewer/scripts/console.py manifests/*.shots.json site/           # 网页：展示台
   python3 <crew>/comfyui/scripts/shots2comfy.py manifests/*.shots.json --comfy <ComfyUI 目录>
   ```

   网页上的节点图是照 `shots2comfy.py` 写出来的工作流文件画的。要节点图，先跑 `shots2comfy.py`，再给 `console.py` 加上 `--workflows <ComfyUI 目录>/user/default/workflows/filmkit`。

每一步的参数、要装什么、做完查什么，在那一部分的 `overview.md` 里。

## 哪些真跑过

| 部分 | 现状 |
| --- | --- |
| backends：Wan 3.0 | 用真 key 走官方接口跑过（2026-11-22）。 |
| backends：gpt-image 2.6 | 经一个兼容 OpenAI 接口的网关跑过（2026-11-22）。没有直接对 api.openai.com 跑过。 |
| backends：HappyHorse 1.1、Seedance 2.5 / 2.0、MiniMax H3-Max | 照官方文档写成，请求格式离线核对过。还没有用真 key 经这几个适配跑过。 |
| viewer | 离线测试通过。页面在桌面窗口和手机宽度下都看过。 |
| comfyui | 在真的 ComfyUI 0.46.0、前端 1.59.6 上核对过。前端换了版本，要重跑检查脚本。 |
| formats | 检查脚本在 `formats/examples/` 的例子上都通过。 |

## 局限

- 查看器和 ComfyUI 都要镜头表 `meta.json`，这份文件得剪完以后另写。
- 镜头清单是按文件名从运行目录里读出来的。哪些是重抽、哪张关键帧属于哪一镜，都这样认。
- `comfyui/` 只回放。在里面改了提示词再点 Run，不会重新生成。要调整某一镜，告诉 agent。
- 后端只发本地文件。火山方舟的参考视频只收公网链接，所以带参考视频的单子，方舟适配会拒。

## 许可证

[Apache-2.0](../../LICENSE)。

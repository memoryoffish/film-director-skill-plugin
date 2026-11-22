# tests

不联网、不开浏览器、不要 ffmpeg。在 `viewer/` 下跑：`python3 -B -m unittest discover -s tests`（`-B`：不在 `../formats` 里留 `__pycache__`）。
`test_read_run.py`、`test_check_manifest.py`、`test_console.py` 要 `../formats` 在旁边，`test_console.py` 还要 Pillow；缺了就跳过。

| 文件 | 测什么 |
|---|---|
| [synth_run.py](synth_run.py) | 造一个八镜的小运行目录（纯色 PNG + 任务文件 + 出图记录 + 结果记录），读法里的分支都走到：白模在子目录、找不到白模用关键帧的、出图记录在 `jobs_img/` / `imgjobs/` / 图旁边、绝对路径、只在剪辑表里的任务、一条生成切成两镜、参考图生视频也给了首帧、重抽重画、没有任务的镜头。`python3 synth_run.py <目录>` 单独造一份 |
| [test_read_run.py](test_read_run.py) | `read_run.py` 读它：格式查得过；`sent` 留着喂法去掉的首帧；`stills` 和 `named_stills` 各按各的找；`own_ref`；`pictures` 的说明、`made_by`、`keyframe`、白模站位；`attempts` 的次序、结果、`diff`、`was`；ComfyUI 用的几项照旧 |
| [test_check_manifest.py](test_check_manifest.py) | 手写的例子查得过，去掉另加的几项也查得过；十几种写错的各报出来 |
| [test_console.py](test_console.py) | `console.py` 从清单出数据（标成还没开拍，不抽帧）：每一镜的首帧、参考图说明、白模、参数；`keys` 的次序；节点图实体表；从文件读工作流（人改过的那份不用）；缺工作流、没给 `--workflows`；精简时的白模尾帧 |
| [test_progress.py](test_progress.py) | `progress.py`：给了价格表写花费（原价、折扣价、估价），没给只写时间；重抽几次、视频链接、用了几分钟 |
| [test_styles.py](test_styles.py) | 风格：不加 `--style` 页面里什么都不多；加了以后 `<main>` 里的内容照旧；`styles/` 下每份 CSS 的每条规则都在自己的名字底下、动画名带前缀，每份 JS 登记在自己的名字和部分上；没有的风格或部分直接停 |

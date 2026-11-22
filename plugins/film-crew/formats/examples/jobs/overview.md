# examples/jobs：手写的任务单

每种喂法一张，两张图片单，一张交给 Seedance 的。项目目录就是这个文件夹：单子里的路径从这里算起（`media/…`）。

| 文件 | 种类 | 喂法 | 看点 |
|---|---|---|---|
| [t2v.json](t2v.json) | 视频 | 文生 | 没有媒体字段 |
| [first_frame.json](first_frame.json) | 视频 | 首帧 | `first_frame` |
| [first_last.json](first_last.json) | 视频 | 首尾帧 | `first_frame` + `last_frame` |
| [refs.json](refs.json) | 视频 | 参考图 | 提示词里的图1、图2 就是 `reference_images` 的顺序 |
| [ref_video.json](ref_video.json) | 视频 | 参考视频 | `reference_video` 再带一张参考图 |
| [seedance_plain.json](seedance_plain.json) | 视频 | 参考图 | 照平常写（`720P`、`seed`、`图N`），只加了 `"model": "seedance-2.5"`；后端会改写 |
| [image_edit.json](image_edit.json) | 图片 | 改图 | `images` 第一张是 Image 1 |
| [image_t2i.json](image_t2i.json) | 图片 | 文生图 | 写全了 `model`、`quality`、`size`、`n` |
| [media/](media/overview.md) | | | 单子用到的小图和一段 2 秒的小视频 |

检查（在 `formats/` 里）：

```
python3 check_job.py examples/jobs/*.json --root examples/jobs
```

看后端会发什么（在这个文件夹里，不发送、不上传）：

```
python3 ../../../backends/scripts/filmgen.py request *.json
```

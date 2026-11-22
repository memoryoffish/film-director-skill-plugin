# 手写的镜头清单

[demo.shots.json](demo.shots.json)：四镜，ComfyUI 用的几项和网页查看器另加的几项都写了，格式见 [shots-manifest.md](../../shots-manifest.md)。

| 镜 | 喂法 | 写了什么 |
|---|---|---|
| A1 她把杯子放到桌上 | 首帧生视频 | 首帧是这一镜自己出的关键帧（`made_by: one_first`，重画过一次）；生成 3 次，第 1 次报错；白模静帧带站位描述；片头的 `flag` 指着它 |
| A2 只有提示词的一镜 | 文生视频 | 只有提示词和 `sent` |
| A3、A4 | 参考图生视频，一条 `u1` 切成两镜 | 参考图第 2、3 张是两镜各自的画面（`own_ref` 1、2） |

`root` 是 `/srv/films/zz_demo`，图不在仓库里；拿去试的时候换成自己放图的目录。

```bash
python3 ../../check_manifest.py demo.shots.json                                       # 格式查得过
python3 ../../../comfyui/scripts/shots2comfy.py demo.shots.json --comfy <目录> --no-run     # 出 4 份工作流（图找不到时按 16:9 排）
```

`<目录>` 里要先有 `custom_nodes/comfyui_filmkit/` 和 `input/` 两个文件夹（登记表、参考图写在那里），可以是空的；`--no-run` 只放文件，不碰正在跑的 ComfyUI。

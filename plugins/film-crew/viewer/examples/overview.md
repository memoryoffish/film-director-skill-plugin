# examples：从运行目录到页面，一遍命令

`<W>` 是放输出的目录，命令在 `viewer/` 下跑。配置 `films.json` 写每部片的运行目录、成片、预演，和想让页面打开就停在的那一处：

```json
{"films": [{"key": "demo", "run": "<运行目录>", "film": "<成片 mp4>", "previz": "<白模预演 mp4，可以没有>",
            "flag": {"t": 9.5, "shots": ["S3"], "note": "这一处要看什么，一句话"}}]}
```

```bash
# 运行目录 → 镜头清单，查一遍格式
python3 ../formats/read_run.py films.json --out <W>/manifests
python3 ../formats/check_manifest.py <W>/manifests/*.shots.json

# 要节点图：出工作流。这里放进一个空的替身目录，不碰正在跑的 ComfyUI
#（要它在 ComfyUI 里能打开，--comfy 指真的 ComfyUI 目录）
mkdir -p <W>/comfy/custom_nodes/comfyui_filmkit <W>/comfy/input
python3 ../comfyui/scripts/shots2comfy.py <W>/manifests/*.shots.json --comfy <W>/comfy --no-run

# 做页面：清单的次序就是页面上片子的次序。默认带转码，起一次等它跑完，别重复起
python3 scripts/console.py <W>/manifests/*.shots.json <W>/site \
    --workflows <W>/comfy/user/default/workflows/filmkit --title <页面标题> --view graph

# 看：起一个只听本机的静态服务，开 http://127.0.0.1:8797/
cd <W>/site && python3 -m http.server 8797 --bind 127.0.0.1
```

页面在另一台机器上做的，本机用 `ssh -N -L 8797:127.0.0.1:8797 <主机>` 转过来看。

没有运行目录时：手写的镜头清单在 `../formats/examples/manifest/`；`tests/synth_run.py <目录>` 造一个八镜的假运行目录（没有成片）。

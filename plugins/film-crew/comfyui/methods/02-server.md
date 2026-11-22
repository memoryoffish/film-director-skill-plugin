# 02 在服务器上起 ComfyUI

一句话：放在运行目录所在的机器上，代码和 Python 环境放本地盘，CPU 模式，tmux 里常驻，本机开一条 ssh 隧道看。

## 推荐

- **放哪台**：运行目录、成片在哪就放哪。回放要读这些文件；视频裁剪、转码也是重活，不放本机。
- **放哪块盘**：代码和虚拟环境放本地盘（比如 `/tmp/comfyui`），不放网络盘：Python 导入几千个小文件，网络盘上慢。代价是容器重建后要重装（几分钟）。
- **环境**：`python3 -m venv --system-site-packages`，复用系统里已有的 torch，只装缺的十来个包；PyPI 走镜像。
- **CPU 模式**：`--cpu`。我们的节点只读文件、裁视频，不碰显卡，也就不和训练抢卡。
- **带资产系统启动**：`--enable-assets`。input、output 里的文件启动时扫进库，Assets 面板按库列：重启以后我们留下的关键帧、视频、参考图都还在。不带时 Generated 只列这次启动以后跑出来的，一重启就空（Windows 整合包默认是开的）。
- **只听本机**：`--listen 127.0.0.1`，本机 `ssh -N -L 8188:127.0.0.1:8188 <服务器>` 转过来，浏览器开 `http://127.0.0.1:8188`。
- **常驻**：服务器上 tmux 会话（比如叫 `comfy`），日志 `tee -a` 到文件；本机的隧道也放 tmux（`comfy-tunnel`）。改了节点包要重启：`tmux respawn-pane -k -t comfy:server "<启动命令>"`。

## 伪代码

```
git -c http.proxy=<服务器上的代理> clone --depth 1 https://github.com/Comfy-Org/ComfyUI
python3 -m venv --system-site-packages venv
venv/bin/pip install -i <PyPI 镜像> -r ComfyUI/requirements.txt      # torch 已有就跳过
ln -s <本目录>/nodes/comfyui_filmkit ComfyUI/custom_nodes/comfyui_filmkit
tmux new -d -s comfy "cd ComfyUI && ../venv/bin/python main.py --cpu --listen 127.0.0.1 --port 8188 --disable-auto-launch --enable-assets | tee -a comfy.log"
等 /system_stats 返回 200
本机：tmux new -d -s comfy-tunnel "ssh -N -o ControlMaster=no -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -L 127.0.0.1:8188:127.0.0.1:8188 <服务器>"
```

## 实测

- 服务器直连 GitHub 不通时，clone 走机器上的 HTTP 代理（`git -c http.proxy=<代理>`）；PyPI 慢或不通时换就近的镜像（`pip install -i <镜像>`）。
- 系统 Python 已经带着 torch、torchvision、av 时，要装的只有 torchsde、SQLAlchemy、alembic、kornia、spandrel、comfy-kitchen、comfy-aimdo、simpleeval 和前端三件（frontend 1.59.6、workflow-templates、embedded-docs）。装完一次约两分钟，torch 不会重下。
- 冷启动约 30 秒（`/system_stats` 第 9～10 次轮询，每次 3 秒）。
- 隧道要单独一条连接（`ControlMaster=no`）：复用的主连接坏了时会拒开新会话，隧道跟着挂。
- 资产系统：启动时扫 217 个文件用了 2.4 秒；库在 `ComfyUI/user/comfyui.db`。启动以后才拷进 input 的文件要再扫一次才列得出来：有人打开或刷新一次页面就会扫；脚本里用 `curl -X POST 127.0.0.1:8188/api/assets/seed -d '{"roots":["input"]}'`。前端 1.59 不认识服务器发的 `assets.seed.*` 消息，控制台里会有几行「Unknown message type」，不碍事。

## 局限

- `/tmp` 在容器的根文件系统上，容器重建就没了；重装照上面几步。
- 只开了本机访问；要给别人看，得另想办法（别直接 `--listen 0.0.0.0`）。

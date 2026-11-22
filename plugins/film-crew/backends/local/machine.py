"""Where the backends run and which addresses they call, read from environment variables.

No key is in this file or anywhere in this folder: each adapter reads its vendor's key in process from the environment
variable that vendor's docs name (DASHSCOPE_API_KEY, ARK_API_KEY, MINIMAX_API_KEY, OPENAI_API_KEY) and never prints or
writes it. The addresses below are the official defaults; set the variable next to one to call another region or site.
"""
import os

# send: the machine that runs a project's video jobs (an ssh host), the folder there that holds the projects (relative to
# the remote home: REMOTE/<project>), one tmux session per project, and the python it runs. HOST and REMOTE have no
# default: send stops with a message when they are not set.
HOST = os.environ.get("FILM_SEND_HOST", "")
REMOTE = os.environ.get("FILM_SEND_REMOTE", "")
SESSION = os.environ.get("FILM_SEND_SESSION", "film_{project}")
REMOTE_PYTHON = os.environ.get("FILM_SEND_PYTHON", "python3 -I")   # -I keeps the project folder off sys.path

# how many jobs of one backend run at once
WORKERS = {"bailian": 4, "ark_video": 2, "minimax_video": 2, "openai_image": 4}

# Alibaba Cloud Model Studio (DashScope), Beijing. The docs recommend the workspace address
# https://<WorkspaceId>.cn-beijing.maas.aliyuncs.com/api/v1 (shown in the console); the DashScope address still serves.
DASHSCOPE_BASE = os.environ.get("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
# Volcengine Ark, cn-beijing
ARK_BASE = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
# MiniMax, China site; an account on the international site uses https://api.minimax.io
MINIMAX_BASE = os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.cn")
# OpenAI
IMAGE_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

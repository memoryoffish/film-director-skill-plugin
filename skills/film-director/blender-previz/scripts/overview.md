# scripts：工具

| 脚本 | 做什么 |
|---|---|
| [blocking.py](blocking.py) | 白模工具：用 Python 写场景，出静帧、预演、平面图、站位描述；查越轴、出画、遮挡、视线、间距、每镜首尾的变化 |
| [gimg.py](gimg.py) | 图像模型出图（OpenAI 官方 Images 接口）：白模转关键帧（带输入图）、定妆图（纯文字）。服务端报错自动重试两次。见 [refs/gpt-image.md](../refs/gpt-image.md) |
| [jobs.py](jobs.py) | 视频任务和提示词模板：分镜单元（`unit_job`）、单镜参考图 / 参考视频（`ref_job`）、单镜首帧（`shot_job`）、给图派活的几句话（`wm_guide`、`key_guide`、`video_guide`、`still_guide`）；给 `model="seedance-2.5"` 时改写成 Seedance 的任务 |
| [cut.py](cut.py) | 处理生成出来的成片：量切点、按镜头表把单元拆成一镜一镜、按整帧裁和拼、抽帧拼图、按时间密抽、「白模 \| 关键帧 \| 成片」三栏对照、找撞击声 |

## 环境

- Blender 当 Python 模块用，不开界面：`python3 -m venv .venv && .venv/bin/pip install bpy==5.3.0 pillow numpy`（Python 3.13）。
- 要装 ffmpeg（macOS 上用 Homebrew 装的 ffmpeg 不在 PATH 里时，先 `export PATH=/opt/homebrew/bin:$PATH`）。
- 在一台 Mac 上实测，渲 1280×720 的一帧约半秒（默认 32 次采样）；`previz(samples=8)` 快约三倍，画质当参考视频、做对照都够用。GPU 服务器上（EEVEE 用一张 GPU）默认每秒约渲 3 帧，`samples=8` 只快一半；长片的预演怎么渲，见下面速查里的「长片的预演」。
- 只有 CPU、或者在软件 GL 上（没有显卡的服务器、容器）EEVEE 一渲就崩时，建好 `Stage` 以后改用 Cycles 的 CPU 渲染：`st.scene.render.engine = "CYCLES"; st.scene.cycles.device = "CPU"; st.scene.cycles.samples = 16`。这时 `previz(samples=…)`、`clip(samples=…)` 改的是 EEVEE 的采样，不起作用，采样数改 `st.scene.cycles.samples`；Cycles 在 CPU 上慢，先用 `still()` 出一帧看时间和样子再渲整段。这一条在这里没有实测过。
- 平面图 `plan()` 的标签要一个中文字体：先读环境变量 `BLOCKING_FONT`，没设就在 macOS、Linux 的常见位置找；都找不到时，固定的字（机位、门往哪开、底下的标题行）换成英文。人名、门通向哪里照你起的名字画，没有中文字体的机器上这些名字也起英文的，不然是方块。
- `blocking.py`，和 `cut.py` 里拼图的命令，要用上面那个装了 bpy 和 Pillow 的 Python 跑；`jobs.py`、`gimg.py` 用系统 Python 就行。
- 要自己加网格时，`import bmesh`、`from mathutils import …` 要写在 `from blocking import …` 之后：这两个模块是 bpy 带的，blocking 载入 bpy 以后才导入得了。
- 几个渲染同时跑时，停自己的那个要按进程号停（`kill <PID>`），别按名字杀（`pkill -f scene.py` 会把别人的渲染也杀掉）。
- 测试：`python3 -m pytest -q -p no:cacheprovider tests/`（`blocking.py` 的测试要用上面那个带 bpy 的 Python；它不在那个路径时，把环境变量 `BLENDER_PY` 设成它的路径）。

## 一个项目的目录

```
<项目>/
  scene.py          # 场景：from blocking import Stage …
  wm/               # 白模静帧 <镜头>_a.png（首帧）、_b.png（尾帧）、平面图、预演
  refs/             # 人物、道具参考图
  keys/             # 关键帧
  jobs/*.json       # 视频任务；里面的图片路径相对项目目录
  clips/            # 取回的成片和每条任务的状态文件
  cut/              # 裁好的镜头和成片
```

视频任务用 video-film-maker 的 `scripts/wan.py` 送（官方 DashScope 接口，key 从环境变量 `DASHSCOPE_API_KEY` 读）。任务字段是同一套（`name`、`duration`、`resolution`、`ratio`、`audio`、`prompt_extend`、`seed`、`prompt`、`first_frame`、`last_frame`、`reference_images`、`reference_video`），`jobs.py` 写出来的任务不用改。不同的是交法：这边一个任务一个文件，`wan.py` 的批量入口 `occut.py gen` 吃的是一个任务列表文件。所以在项目目录里先把 `jobs/` 下要送的任务拼成一个列表，再送（任务里的图片路径相对项目目录，要在项目目录里跑）：

```
cd <项目>
python3 -c 'import glob, json; json.dump([json.load(open(f)) for f in sorted(glob.glob("jobs/*.json"))], open("jobs_list.json", "w"), ensure_ascii=False, indent=1)'
python3 <video-film-maker>/scripts/occut.py gen jobs_list.json clips --workers 2
```

成片和每个任务的状态文件（`clips/<name>.mp4`、`clips/<name>.json`）一条条落到 `clips/`；已经下载好的任务再送时跳过，中途断了再跑一遍同一条命令，按状态文件里的任务号接着等。引用的文件还不存在的任务（比如预演还在渲）会报错，先别把它拼进列表。要重拍、换种子或改了提示词，把任务换个名字另存：同名任务参数变了，`wan.py` 会报错、不重发。`wan.py` 只送 Wan 3.0 和 HappyHorse 1.1；`model="seedance-2.5"` 的任务它不收，这个 skill 不带调 Seedance 的脚本。装了同一个仓库里的 film-crew 插件的话，视频任务也可以交给它的 backends（先用 `request` 看要发的请求再发），任务单格式一样，一个任务一个文件直接交。

## blocking.py 速查

单位是米和秒。方向用从上往下看的罗盘角：0 = +Y（北），90 = +X（东），180 = −Y，270 = −X。人的 `facing` 除了角度，也可以写一个点 `(x, y)`，或另一个人、一件东西的名字（面朝它）。位置写两个数 `(x, y)` 时，放在那一点的地面上；写三个数时，第三个数就是高度。两个动画关键帧之间是匀速的；`walk` 和 `camera_move` 自己打很多个动画关键帧，做出缓起缓停。`walk` 按速度配步频，`strike`、`sit_down` 按像样的节拍打动画关键帧，`timeline()` 列出每一步、每个姿势落在第几秒、每段走路走多快：自己看预演、对成片时用。要喂给视频模型的预演用替身版：`Stage(…, stand_ins=True)` 把同一个脚本里的人全换成没有四肢的替身（见 [预演当参考视频](../stages/3-feed/ref-video.md)）。

```python
import sys
SKILL = "<blender-previz 的目录>"                                       # 这个 skill 的目录
sys.path.insert(0, SKILL + "/scripts")
from blocking import Stage, POSES, Capsule, key

st = Stage(fps=30)                                   # 帧率和成片一致（Wan 3.0 是 30，Seedance 24）；stand_ins=True：所有人换成胶囊替身，渲要喂的那版预演
# ---- 场地
st.floor(0, 0, 4, 5)                                 # x0, y0, x1, y1；z= 抬高（楼上、平台）
st.floor(0, 5, 4, 8, name="屋里")
st.wall((0, 5), (4, 5), doors=[(1.0, 0.9, 2.0), (3.0, 0.9, 2.0)])   # a 点到 b 点；doors = [(离 a 多远, 宽, 高)…] 开门洞（一个时也可写 door=(…)）
st.wall((0, 0), (0, 5), windows=[(2.5, 1.2, 1.2, 0.9)])            # windows = [(离 a 多远, 宽, 高, 窗台高)…]：开洞，装窗框和中梃
st.wall((4, 0), (4, 5))
st.wall((0, 8), (4, 8), height=5.6, windows=[(2, 0.8, 0.9, 0.9), (2, 0.8, 0.9, 3.7)])   # 同一竖列上下几扇（每层一扇；门上开窗也行）：离 a 一样远，窗台高从墙底量
d = st.door("门", hinge=(0.55, 5), heading=90, into=(1, 6), into_name="屋里")   # 合页点、关着时门扇伸向哪边、门往哪一侧开；先建地板再建门，楼上的门把 hinge 写成 (x, y, z)
d.open(0.0, 0); d.open(1.0, 0); d.open(2.0, 80)      # 往 into 那一侧开到 80 度；d.set(秒, 带正负号的角度) 也行
d.attach("福字", (0.012, 0.3, 0.3), (0.031, 0.45, 1.3), "red")      # 挂在门扇上、跟着门转的东西；第三组数的正号 = heading 右手那一面
st.ceiling(0, 0, 4, 5, z=2.8)                        # 天花板 + 一组无影补光（light=False 不要灯；energy= 每盏的瓦数）
st.stairs("楼梯", at=(3.4, 0.4), heading=0, steps=4) # 往 heading 方向上行；返回顶端的点。默认实心；solid=False 只有一层 0.15 米厚的梯段板、底下空着（楼梯间里上面那段，底下要放机位、走人）
st.box("柜子", (0.8, 0.4, 1.8), (3.5, 4.7))           # (宽, 深, 高), 底面中心；color=、heading=；ground=False 表示人不踩它
st.cylinder("柱子", 0.12, 2.8, (0.4, 0.4));  st.ball("灯", 0.15, (2, 2, 2.4), color="yellow")
sofa = st.sofa("沙发", (2, 3), heading=180);  st.table("桌", (2, 1.5));  st.stool("凳", (1, 1))
st.chair("椅子", (3.4, 3.6), heading=270)              # 座面 + 四条腿 + 靠背；heading = 坐的人面朝哪
st.asset("床", SKILL + "/assets/kaykit-furniture/bed_single_A.gltf", (1.0, 7.0), heading=180, length=2.0)   # 现成模型，统一涂成一个颜色
# ---- 人
a = st.person("阿杰", "blue", at=(1, 2), facing=0, height=1.83, marks=("glasses",))          # 带关节的人偶
b = st.person("小周", "red", at=(2.8, 2.2), facing="阿杰", height=1.66, marks=("hair_long",))
c = st.person("胶囊", "yellow", at=(2.5, 0.6), facing=0, kind="capsule", marks=("cap_back",)) # 胶囊替身
a.place(1.0, (1, 4.4), pose="stand", hands={"r": d.lock_point(side=-1)})   # 第 1 秒：在哪、朝哪、什么姿势；右手够到门锁
a.walk(1.0, 3.0, (1.0, 6.0))                         # 1–3 秒走过去，缓起缓停，沿地面（会上台阶）；步频按速度配，摆幅跟着步长
a.strike(3.8)                                        # 3.8 秒右直拳打直：前 0.35 秒蓄力、前 0.15 秒上步，停 0.08 秒，0.2 秒收回成架势
b.place(0.5, (2.8, 2.2), pose="sit", seat=0.40)      # 坐在 0.40 米高的东西上；同一个坐姿的下一个动画关键帧不用再写 seat
b.place(1.5, (2.8, 2.2), pose="sit", feet={"l": (2.4, 1.6, 0.05)}, head_turn=-30)   # 左脚伸出去够一个点；单个关节角（度）
c.walk(0.0, 3.0, (2.5, 3.0), ease=False)             # 匀速走：镜头开始和结束时人都在走
c.place(3.0, (2.5, 3.0), pose="crouch")              # 胶囊只会变矮：low=0.6 或 Capsule.LOW["名字"] = 0.6 给自己的姿势
e = st.person("小林", "purple", at=(3.6, 2.4), facing=0)
e.walk(0.0, 1.5, (3.3, 3.1), cadence=1.5)            # 自己定步频（每秒几步）；stride_s=0.5 是旧写法（每步几秒，摆幅不变）
e.sit_down(3.2, "椅子")                               # 3.2 秒坐定：前 1.3 秒一步跨到椅子前、转身，停一下，屈膝前倾，落座，再坐直
st.key(sofa, 2.0, at=(2, 3.4), heading=180)          # 道具的动画关键帧
# ---- 机位
st.camera("全景", (2, -1.2, 1.6), (2, 5, 1.0), lens=24)             # 位置、看向的点、焦距
st.camera_key("全景", 3.0, (2, 0.2, 1.6), (2, 5, 1.0))             # 匀速移到这里
st.camera("门口", (1.8, 3.6, 1.5), (0.8, 5.5, 1.1), lens=28)
st.camera_move("门口", 1.5, 3.0, (1.6, 4.2, 1.5), (0.8, 5.8, 1.1))  # 缓起缓停地移过去
st.camera("顶", (2, 3, 6.5), (2, 3, 0), lens=24, hide=["ceiling", "wall_top0", "门_lintel"], roll=90)   # 这一镜藏掉天花板、门上那截墙；画面上方朝西
# ---- 看和算
shots = [("s1", "全景", 0.0, 1.5), ("s2", "门口", 1.5, 3.0), ("s3", "顶", 0.0, 1.0)]
notes = st.stills(shots, "wm", last={"s1", "s2"})    # wm/s1_a.png（首帧）；last 里的镜头再出 s1_b.png（尾帧）；返回每镜的站位描述
print(st.describe("全景", 0.0, props=["福字"]))       # 「阿杰在画面左侧，全身入画，占画面高 66%，背对镜头」；门的合页在哪边、往哪开；props 里点名的东西在画面哪里
print(st.order("全景", 0.0))                          # 画面里从左到右的人名（整个人被挡住的不算）
print(st.flips(shots))                               # [(前一镜, 后一镜, 原来的左右顺序, 现在的)]：哪两镜之间人换了边
print(st.changes(shots))                             # 每镜开头和结尾哪里变了（左右、朝向、进出画、门、道具）：这些镜头要出尾帧
print(st.sees("小周", "阿杰", t=0.0))                  # 小周的眼睛到阿杰的头之间挡着什么；[] = 看得见
print(st.sees("全景", ("阿杰", "chest"), t=2.0))       # 也可以从机位看、看身上某处，或看一件东西的名字
print(st.gap("阿杰", "小周", t=0.0))                   # 两人胸口之间的地面距离（米）
tl = st.timeline()                                   # 每个人：走了哪几段（速度、步频、步长）、每次换脚、每个姿势、出拳和坐下落在第几秒
print(tl["people"]["小林"]["events"], tl["warnings"])  # warnings：步频不在每秒 1.4–1.8 步的走路
for line in st.check_bodies():                       # 人偶做不做得到：关节超出范围、手够不着或伸到背后、头和胸穿进家具墙门、两人叠在一起
    print(line)                                      # 【要改】的都改
st.pose_sheet("wm/poses.png")                        # 每人每个姿势正面、右侧各一张小图拼成一张，逐张看，每张写一句
print(st.ground(1.0, 5.0))                           # 这个点的地面高度（门洞里也是地面）
print(a.point("hand_r"))                             # 身上某处的世界坐标："mouth"、"lap"、"hand_l"、"hand_r"
st.plan("wm/plan.png", t=2.0)                        # 这一刻的俯视图；region=(x0, y0, x1, y1) 只画一块，大场景用
st.plan("wm/plan_s2.png", t=1.5, cams=["门口"])       # 只画点名的机位：一镜一张（这一镜的机位、开头那一刻的人）
st.previz(shots[:2], "wm/previz.mp4", samples=8)     # 按切点拼好的预演，每镜都重渲；同目录留下 pv_<镜头>.mp4（全是胶囊时 pv_<镜头>_capsule.mp4）
st.previz(shots[:2], "wm/previz.mp4", only=["s2"], samples=8)       # 重渲 s2，再补上还没有文件的镜头，其余用已有的文件
st.previz(shots, "wm/previz.mp4", missing=True)      # 只渲还没有文件的镜头，再拼：停了以后接着渲，或分进程渲完以后拼（长片见下）
st.retime(1.25)                                      # 整条时间线快 1.25 倍：所有动画关键帧的秒数除以 1.25，之后出图、出预演的镜头表也要跟着除；放在打完所有帧之后
st.save("wm/scene.blend")
```

- 现成的姿势（`POSES`）：stand、walk_a、walk_b、sit、sit_floor、crouch、carry、lift_low、push、hands_on_hips、high_five、arms_out；打斗和坐下：guard、guard2（同一个架势略有不同的两版，交替打动画关键帧，做出一点起伏）、punch_r（右直拳打直）、duck（矮身躲拳）、body_punch（右拳打肚子）、hurt_b、hurt_b2（弓身、两臂护着肚子的两版，往后退的时候交替打）、sit_mid（坐到一半：屈膝、上身前倾）。hands_on_hips 摆不成真的叉腰：人偶的大臂不会自己转，两条前臂会平端在身前；要叉腰的镜头，白模里只给位置，叉腰写在文字里。要别的姿势，直接给关节角，或往 `POSES` 里加一条（可带 `"seat"`：坐的东西多高；`"low"`：胶囊替身缩到站着时的几成高）。
- 走路的步频：`walk` 既不给 `cadence` 也不给 `stride_s` 时，步频 = 速度 ÷ 0.8 米，限制在每秒 1.4–1.8 步之间（每秒 1.3 米约 1.6 步）；比每秒 1.1 米慢时，步频停在 1.4、步子变短；原地踏步也是 1.4，摆幅降到原来的四分之一。髋和肩的摆角按 步长 ÷ 0.65 米 缩放（`walk_a`、`walk_b` 两个姿势画的是 0.65 米的步子）；你自己给的关节角优先。给 `stride_s`（每步几秒）是旧写法：照旧把整段均分成一步一步，摆幅不变。胶囊替身没有脚，接受这两个参数但不用。
- `strike(t, step=0.5, pose="punch_r")`：人从 t − 0.35 秒时站的地方，朝自己面朝的方向上步出拳（step 是上步的米数）；挨打的人不会自己反应，要另外给他打反应姿势（duck、hurt_b / hurt_b2）并让他退开。`sit_down(t, 椅子)` 只认 `chair()` 搭的椅子：调它之前，先让人走到椅子旁边、离座面前沿半米左右（不走到椅子上），在 t − 1.7 秒前走到；椅子要从桌边拉开，座面前留出站的地方。这两个函数对胶囊替身也能用（胶囊只会变高变矮）。
- `timeline()` 报的时刻，是动画关键帧实际落在的那一帧；它报的换脚是两腿交错的那一刻（相邻的 walk_a 和 walk_b 两个动画关键帧的正中间），拿成片对步子时就数这个。调过 `retime()` 以后，它报的时刻已经换算好了。
- `check_bodies(step=0.25)` 每 0.25 秒和每个姿势的动画关键帧查一次，两个关键帧之间插出来的也查。关节范围在 `ROM`：肘 -5–155°、膝 -5–165°，肩往前抬 -65–180°（再往后就是胳膊往后反折），大腿往前抬 -30–135°、左右转 ±45°，上身扭转 ±60°，转头 ±80°，低头 70°、抬头 75°。上身前倾和胳膊侧抬不查：人偶躺不下也趴不下，场景里拿前倾去凑；胳膊往前抬起以后，侧抬就成了大臂自己转。`hands=`、`feet=` 的目标点超出胳膊（腿）伸直的长度 5 厘米以上，或者在背后，反解照样把胳膊拉过去、不报错，所以由它来报（连着几个动画关键帧的合成一段）。头、胸穿进家具墙门，两个人叠在一起，也报。脚离地、插进地里几厘米和膝盖贴着抬着的沙发不查。胶囊替身不查。`pose_sheet()` 默认每次打姿势出一组，一段走路只出第一步；`people=`、`times=` 只出点名的。
- 关节（`JOINTS`）和各自正值的方向：lean（上身前倾）、twist（上身向自己的左边转）、head_turn（头向自己的左边转）、head_nod（低头）、shoulder_l/r（手臂往前抬；负数往后摆）、abduct_l/r（手臂往身体外侧举）、elbow_l/r（弯肘）、hip_l/r（大腿往前抬）、hipturn_l/r（大腿向左右摆）、knee_l/r（弯膝）。
- 颜色名：red、blue、green、yellow、purple、orange、white、black、maroon、grey、door、wall、floor、prop、hair 等，也可以直接给 `(r, g, b)`。
- 人的标记 `marks`：glasses、cap、cap_back、hair_curly、hair_long、shorts。胶囊替身认得其中的 glasses、cap、cap_back、hair_curly、hair_long。
- 坐：`pose="sit"` 默认座高 0.45 米，别的高度给 `seat=`；坐在地上用 `sit_floor`。座高跟着人的身材一起缩放，所以放大的巨人也坐得到地上。人要站在家具上，位置里写上 `z`。
- 胶囊替身没有四肢：`pose` 只让它变矮，`hands`、`feet` 不起作用。
- 人整个被挡住时（头、胸、腰都被挡），`describe` 写「在 X 后面，画面里看不见」，`order`、`flips` 不算他。
- `describe` 报的【要改】：头出画、镜头贴着或钻进了什么东西，都附上离镜头多远；故意拍局部的特写可以不理。镜头整个在实心的东西里（墙、柜子、默认实心的楼梯）时，它写「镜头在 X 里面」，这时画面里只有那样东西的内壁，一定要挪机位。「腰被挡住」（坐在桌子后面）只是说明。【留意】：人只占画面高不到一成时，它提醒你出图后量一下。
- 门的高度：`hinge` 只写两个数时，门立在建门那一刻合页下面最高的东西上。如果地板在门之后才建，或者合页正好落在地板边上、两块地板的接缝上（bpy 5.3 在接缝上查不到地板），门都会掉到 0 米。所以工具在第一次出静帧、`describe`、`plan`、`clip` 之前会再查一次门的高度：门洞两侧各 0.25 米处，脚下没有一样能站的东西和门一样高，或者那里上下不止一层地板，就报错，并写出该改成的 `hinge=(x, y, z)`。楼上、平台上的门直接写三个数。
- 自己用 `ob.keyframe_insert(...)` 打的动画关键帧，出图前会被改成匀速；新写的代码用 `key(ob, "location", 帧号)`。
- 拍到中途要补一个镜头：把它排在时间线最后（比如 40–44 秒），在镜头表里放到它该在的位置；`stills`、`previz` 都按镜头表的顺序出，不管时间线上谁先谁后。
- 长片的预演（几千帧）：
  - 草稿：`samples=8, scale=0.5`，只渲四分之一的像素，渲完每镜的片子再放大回原尺寸，画面软一点，看节奏、看机位够用。草稿尺寸的预演没当参考视频试过；要喂给视频模型的那几镜按原尺寸渲（`only=[…]`）。
  - 分进程：开 n 个进程，各跑一遍场景脚本，第 k 个进程调 `st.previz(shots, "wm/previz.mp4", samples=8, scale=0.5, part=(k, n))`（k = 0…n−1；它只渲镜头表里第 k、k+n、k+2n… 镜，不拼接）；都跑完以后再调一次 `st.previz(shots, "wm/previz.mp4", missing=True)`，把各镜拼起来；中途停掉的进程没渲完的镜头，这一步会补渲。
  - 一镜要渲完、编码完，才会出现 `pv_<镜头>.mp4`，所以渲到一半停了，直接用 `missing=True` 接着渲；`only`、`missing` 都不给时，每镜都重渲。
  - 多快（GPU 服务器，EEVEE 用一张 GPU；每种设置渲 288 帧）：默认（32 次采样、原尺寸）每秒约 3 帧；`samples=8` 约 4.4 帧；`samples=8, scale=0.5` 约 6.8 帧；再分两个进程，合起来约 12 帧。一部 5 分钟的片（9000 帧）分别约 50、34、22、13 分钟。采样降到 8 以下几乎不再快（4 次采样：原尺寸 4.6 帧、半尺寸 6.7 帧）：每帧约 0.2 秒是固定的，场景求值只占 2 毫秒，帧图写在网络盘还是内存里差不多。每个进程占显存约 1.2 GB，进程数按卡上空着的显存定。

## cut.py 速查

```
python3 scripts/cut.py cuts CLIP [0.12]                     # 片子里的硬切点（秒）；默认门槛 0.2，两镜都暗时用 0.12
python3 scripts/cut.py strip OUT.jpg CLIP [步长 0.1] [起] [止]   # 按固定间隔密抽、每格写着秒数和帧号，最后一帧一定在：找碰上的那一帧、片尾跳帧
python3 scripts/cut.py trio OUT.jpg WM KEY CLIP [WM KEY CLIP …]  # 每镜一行：白模 | 关键帧 | 成片头、中、尾
python3 scripts/cut.py pairs OUT.jpg A1 B1 [A2 B2 …]        # 两两并排（白模 | 关键帧）
python3 scripts/cut.py sheet OUT.jpg "0.5,2,3.4" CLIP …     # 每条一行，按给的秒数抽帧；写 "5" 就均匀抽 5 帧
python3 scripts/cut.py onsets CLIP                          # 最尖的几声（撞击、关门）在第几秒，和画面里碰上的那一帧对
python3 scripts/cut.py frame CLIP 3.6 OUT.png
```

在 Python 里还能直接调：`piece(src, t0, 长度, dst)` 按源片的帧率裁出整帧（声音裁到和画面一样长，两头各 30 毫秒淡入淡出）；`tail(src, 长度, dst)` 取片子最后一段；`join(片段, dst)` 画面和声音分开拼，拼多少段，总长都不会比各段加起来长；`split_unit(src, 每镜时长, lo=0.2)` 量出片子里实际的切点，和镜头表上该切的时刻一一对上，给出该在哪里裁。

## jobs.py 速查

```python
from jobs import unit_job, ref_job, shot_job, wm_guide, key_guide, video_guide, still_guide, save
refs, names = ["refs/ajie.png", "refs/xz.png"], ["阿杰", "小周"]
blocks = ["风格：写实的电影画面。", "人物：…", "场景：…", "声音：…"]
legend = "蓝色人偶就是阿杰，红色人偶就是小周"
u = unit_job("U1_K", [(0, 3.5, "全景，固定机位", "…"), (3.5, 6.1, "中景", "…")], blocks, names, refs,
             key_guide(3, 2), seed=1, duration=7, extra_refs=["keys/k_s1_a.png", "keys/k_s2_a.png"])   # 分镜单元 + 每镜一张关键帧
r = ref_job("s3_VC", "全景，机位缓慢后退。两人并排朝镜头走。", blocks, names, refs,
            video_guide(1, legend) + still_guide(3, legend), seed=2, duration=5, extra_refs=["wm/s3_a.png"], video="wm/pv_s3_capsule.mp4")
f = shot_job("s5_FL", "近景，固定机位。他的右手把钥匙插进锁孔，拧开，把门往屋里推开。", "声音：钥匙的咔哒声。",
             "keys/k_s5_a.png", seed=3, duration=4, last_frame="keys/k_s5_b.png")                  # 首帧 + 尾帧
s = shot_job("s5_FL_sd", "…", "声音：…", "keys/k_s5_a.png", seed=3, duration=4, last_frame="keys/k_s5_b.png", model="seedance-2.5")
for j in (u, r, f, s):
    save(j, "jobs")
```

## 和第一版不一样的地方

旧场景脚本（examples 里各片的 `scene.py`）照样跑得通；下面这些会让画面或输出和第一版不一样：

1. **动画关键帧之间真的匀速了。** 第一版在 bpy 5.3 里插出来的实际是缓起缓停（文档里说的是线性）：所以 `camera_key` 两点之间的镜头、门的开合、`place` 与 `place` 之间的画面都会和第一版不一样。正好落在动画关键帧上的那一帧不变；`walk`、`camera_move` 照旧缓起缓停。
2. **墙不再算地面。** `ground()` 只量地板、台阶和 `ground=True` 的方块；人走过门洞不再飞上门楣，`door()` 写在 `wall()` 后面，门也立在地上。
3. `box`、`sofa`、`table`、`stool`、`stairs` 的位置可以写两个数（第一版报错）。
4. **坐着的座高不会悄悄复位**：同一个坐姿的下一个动画关键帧沿用上一次的 `seat`。座高和身材一起缩放：普通身高的人偶座高只差几毫米，放大的人偶不再悬空。
5. 带关节的人偶现在也画 `hair_long`（旧脚本里自己加过头发的，会出现两块头发）；胶囊替身的帽子多了帽檐，也认 `glasses` 了。
6. `describe()` 多了「占画面高」、门的开向和开合、被整个挡住的人；警告里带上离镜头的距离；「画面中间」的左右边界对称（0.42–0.58 都算中间）。`order()`、`flips()` 不再算整个被挡住的人。
7. `previz()` 全是胶囊替身时，每镜的文件叫 `pv_<镜头>_capsule.mp4`（后缀可以用 `tag=` 自己定）；每镜渲完会删掉 PNG 帧目录（要保留就用 `clip(keep_frames=True)`）。
8. `plan()` 画的是那一刻的位置，不画人头顶以上的东西；比二十来米大的场地自动缩小比例。
9. `cut.py` 裁出来的片段，帧率和源片一样（第一版一律 30），按整帧裁；`join()` 拼出来的成片不再每个接缝多十几毫秒。
10. `gimg.py` 服务端报错自动重试。
11. `jobs.py`：只有一个镜头时 `wm_guide`、`key_guide`、`video_guide` 的说法改成单镜的（不再说「依次是镜头1…」）；`shot_job` 的尾帧和首帧是同一个文件时报错。
12. **`walk` 的步频跟着速度走。** 没给 `stride_s` 的 `walk` 不再每 0.5 秒一步（不管多快都是每秒 2 步）：步频按速度配、限制在每秒 1.4–1.8 步之间，髋和肩的摆角跟着步长缩放，每一步的位置按它实际落在的那一帧算。examples 里这些走路会变：fight-sock 的大刘、suspense-maoyan 的林夏（四段）、romance-lastbus 的阿远，步子更少、更大，换脚的时刻不同；走路中间的静帧和预演会变，走到地方以后不变。给了 `stride_s` 的照旧（同一个场景的动画关键帧逐个比过，一样）；胶囊替身的 `walk` 不变。
13. 新加的：`POSES` 里打斗和坐下的八个姿势；`strike()`、`sit_down()`、`timeline()`、`retime()`；`Stage(stand_ins=True)`；`chair()` 记下座高给 `sit_down` 用。旧脚本自己往 `POSES` 里加过同名姿势的（fight-sock 的 guard、duck），照旧用自己的。
14. `door()` 只写 (x, y) 的门出图前要核对高度（见上面「门的高度」）：门落在地面高度、地板却在楼上的旧脚本会在第一次出图时报错。`describe` 多了「镜头在 X 里面」。examples 里各片的输出不变（逐镜比过）。
15. 新加的：`check_bodies()`、`pose_sheet()`、`Person.angles()`（读出这一帧的关节角）、`Person.reach_gap()`、`ROM`。`cut.py strip` 在没有 `-fps_mode` 的老 ffmpeg（5.1 以前）上改用 `-vsync`。

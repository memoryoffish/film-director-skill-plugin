"""《十分之一》白模：一个场景（荒原 + 巨船 + 机库 + 巨人），一条时间线，11 个机位（第二版加了 s6b）。单位：米、秒。

    PY=<装了 bpy 的 python>
    $PY scene.py                    每镜首帧（和要用的尾帧）白模图、平面图、站位和尺度 -> wm/
    $PY scene.py --clips            再出整片预演 wm/previz.mp4 和每镜 wm/pv_<镜头>.mp4
    $PY scene.py --detail 0         最粗的一档（一个方块当船）出 s1、s3 的静帧 -> wm/d0/（对比搭多细才够）
    $PY scene.py --capsule s2 s3    人换成胶囊替身，只出这几镜的预演 -> wm/cap/pv_<镜头>.mp4（当参考视频用）

方向：X 朝东，Y 朝北。船的南侧面在 Y=0，荒原在 Y<0，人从南往北走。机库在船里（Y 0–70），巨人背靠北墙坐着。
"""
import json, math, sys
from pathlib import Path

SKILL = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, SKILL + "/scripts")
from blocking import COLORS, POSES, Person, Stage, _box, _mesh   # noqa: E402  (blocking imports bpy first)
import bmesh, bpy                                           # noqa: E402
from mathutils import Matrix, Vector                        # noqa: E402

HERE = Path(__file__).resolve().parent
COLORS.update(hull=(0.60, 0.60, 0.58), hull2=(0.50, 0.51, 0.52), gate=(0.30, 0.34, 0.42), sand=(0.52, 0.47, 0.38), ring=(0.90, 0.40, 0.05),
              giant=(0.82, 0.82, 0.78), giant2=(0.62, 0.62, 0.60), deck=(0.33, 0.34, 0.36), crate=(0.42, 0.30, 0.20))

# 跪坐（blocking 里没有这个姿势）：坐在脚后跟上，上身前倾，手好往下够；膝盖不往前顶，挡不住手
POSES["kneel"] = {"hip_r": 40, "knee_r": 150, "hip_l": 40, "knee_l": 150, "lean": 30, "shoulder_r": 60, "elbow_r": 75}

# 镜头表：名字、机位、开始、结束（秒）
# 第二版在 s6 和 s7 之间补了 s6b（她走到那几根「圆木」跟前查看的全景）。它排在成片的这个位置；在白模的时间线上放在最后（40–44 秒），前面各镜的时间不用动
SHOTS = [("s1", "c1", 0.0, 4.0), ("s2", "c2", 4.0, 7.5), ("s3", "c3", 7.5, 12.0), ("s4", "c4", 12.0, 16.0), ("s5", "c5", 16.0, 19.5),
         ("s6", "c6", 19.5, 23.0), ("s6b", "c6b", 40.0, 44.0), ("s7", "c7", 23.0, 26.0), ("s8", "c8", 26.0, 28.5), ("s9", "c9", 28.5, 32.5),
         ("s10", "c10", 32.5, 37.5)]
LAST = {"s2", "s3", "s4", "s5", "s6b", "s7", "s8", "s9", "s10"}   # 运镜的镜头再出尾帧（首尾帧用）
HATCH_X, GIANT_H = 6.0, 16.0              # 小舱门中心的 X；巨人站直的身高
HANG = (-45.0, 45.0, 70.0, 40.0)          # 机库：西墙 X、东墙 X、北墙 Y、顶高
C1 = (-125.0, -205.0, 1.7)                # s1 机位
S1_A, S1_B = (-87.0, -146.0), (-84.3, -141.8)     # s1 里她从哪走到哪（在机位到小舱门的连线上，离机位 70 米）
LAMP_W = 2500.0                          # 机库里每盏灯的瓦数


# ---------------------------------------------------------------- blocking.py 里没有的几样
def hcyl(st, name, r, length, at, heading=90.0, color="hull", cone=1.0, segs=32):
    """横放的圆柱：轴线沿 heading，at 是圆柱中心 (x, y, z)。cone = 远端半径 / 近端半径。"""
    def build(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r * cone, depth=length)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"), verts=bm.verts)
    ob = st._add(name, _mesh(name, build), color, loc=at)
    ob.rotation_euler = (0, 0, -math.radians(heading))
    st.items.append({"kind": "box", "name": name, "size": (2 * r, length, 2 * r), "at": (at[0], at[1], at[2] - r), "heading": heading, "color": color})
    return ob


def dune(st, name, size, at, color="sand", clip_y=-1.0):
    """压扁的球当沙堆；size = 三个半轴，at = (x, y)。北边在 clip_y 处切平（贴着船壳，不钻进机库）。"""
    def build(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=14, radius=1.0)
        yl = (clip_y - at[1]) / size[1]
        if yl < 1:
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, yl, 0), plane_no=(0, 1, 0), clear_outer=True)
    ob = st._add(name, _mesh(name, build, True), color, loc=(at[0], at[1], 0))
    ob.scale = size
    return ob


def lamp(st, name, at, watts, soft=3.0):
    """机库里的点光源（有顶的室内，太阳照不进来）。"""
    li = bpy.data.lights.new(name, "POINT")
    li.energy, li.shadow_soft_size = watts, soft
    ob = bpy.data.objects.new(name, li)
    ob.location = at
    st.scene.collection.objects.link(ob)
    return ob


def suit_up(st, p, pack="grey", torch=False):
    """给人偶加头盔（白球 + 正面的黑面罩）、背包；torch=True 再加右手里的黄色手电。只为看得出是宇航员、哪边是正面。"""
    add = lambda n, mesh, col, parent: p._keep(st._add(f"{p.name}_{n}", mesh, col, parent))
    add("helmet", _mesh("helmet", lambda bm: (bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=0.155),
                                              bmesh.ops.translate(bm, vec=(0, 0.0, 0.2), verts=bm.verts)), True), "white", p.j["neck"])
    add("visor", _mesh("visor", lambda bm: _box(bm, (0.2, 0.08, 0.13), (0, 0.125, 0.21))), "black", p.j["neck"])
    add("pack", _mesh("pack", lambda bm: _box(bm, (0.34, 0.17, 0.48), (0, -0.2, 0.26))), pack, p.j["spine"])
    if torch:
        return add("torch", _mesh("torch", lambda bm: _box(bm, (0.05, 0.22, 0.05), (0, 0.07, -0.33))), "yellow", p.j["elbow_r"])


def wheel(st, door, x=0.1, r=0.22):
    """小舱门朝外那一面的手轮（黄色圆盘），跟着门扇转。"""
    def build(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=r, radius2=r, depth=0.06)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(x, door.width / 2, door.lock), verts=bm.verts)
    return st._add("hatch_wheel", _mesh("hatch_wheel", build), "yellow", parent=door.root)


def stride(p, t0, t1, a, b, facing=None, **joints):
    """匀速走（镜头一开始人就在走、切走时还在走）：blocking 的 walk() 自带缓起缓停，用在这里人会在镜头里起步和停下。"""
    n = max(2, round((t1 - t0) / 0.5))
    for i in range(n + 1):
        k = i / n
        p.place(t0 + (t1 - t0) * k, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), facing if facing is not None else b,
                "walk_a" if i % 2 == 0 else "walk_b", **joints)


# ---------------------------------------------------------------- 场景
def build(detail=1, capsule=False):
    st = Stage(fps=30)
    eps = 1 / st.fps
    st.floor(-420, -520, 420, 0, color="sand", name="plain")

    if detail == 0:           # 最粗：一个方块当船，一块深色板当机库大门，一块小板当小舱门
        st.box("hull", (300, 70, 56), (0, 35, 0), color="hull", ground=False)
        st.box("gate", (44, 0.6, 34), (0, -0.3, 0), color="gate", ground=False)
        st.box("hatch", (1.1, 0.3, 2.1), (HATCH_X, -0.75, 0), color="door", ground=False)
        hatch = None
    else:
        ship(st)
        hangar(st)
        hatch = st.door("hatch", hinge=(HATCH_X - 0.55, -0.1), heading=90, width=1.1, height=2.1, lock=1.1, frame=False, color="door")
        wheel(st, hatch)

    # ---- 人：林，蓝色人偶，1.68 米，头盔 + 背包
    lin = st.person("林", "blue", at=S1_A, facing=S1_B, height=1.68, kind="capsule" if capsule else "jointed")
    torch = None if capsule else suit_up(st, lin, torch=True)
    # s1 大远景：她在荒原上朝船走（匀速）
    stride(lin, 0.0, 4.0 - eps, S1_A, S1_B)
    # s2 跟拍：离船 60 米，接着走
    stride(lin, 4.0, 7.5 - eps, (4.5, -62), (4.5, -57.6))
    # s3 走到小舱门前，停下，抬头
    stride(lin, 7.5, 9.9, (HATCH_X + 0.1, -5.2), (HATCH_X + 0.1, -2.3))
    lin.place(10.4, (HATCH_X + 0.1, -2.0), 0, "stand")
    lin.place(11.3, (HATCH_X + 0.1, -2.0), 0, "stand", head_nod=-32, lean=-6)
    lin.place(12.0 - eps, (HATCH_X + 0.1, -2.0), 0, "stand", head_nod=-32, lean=-6)
    if detail and not capsule:
        wc = (HATCH_X, -0.3, 1.1)                          # 手轮中心（朝外那一面）
        grip = {"l": (wc[0] - 0.2, wc[1], wc[2]), "r": (wc[0] + 0.2, wc[1], wc[2])}
        # s4 小舱门：双手扳手轮，扳不动，整个人压上去，松了
        at4 = (HATCH_X, -0.78)
        lin.place(12.0, at4, 0, "stand", hands=grip, lean=8)
        lin.place(13.2, at4, 0, "stand", hands=grip, lean=22, hip_l=30, knee_l=38, hip_r=-18, knee_r=8)
        lin.place(14.6, at4, 0, "stand", hands=grip, lean=28, hip_l=34, knee_l=42, hip_r=-22, knee_r=10)
        lin.place(15.2, (at4[0], at4[1] + 0.1), 0, "stand", lean=14, shoulder_l=60, shoulder_r=60, elbow_l=30, elbow_r=30)
        lin.place(16.0 - eps, (at4[0], at4[1] + 0.1), 0, "stand", lean=8, shoulder_r=70, elbow_r=25)
        for t, ang in ((0, 0), (14.6, 0), (15.2, 14), (16.0 - eps, 22), (16.0, 50), (17.3, 88), (37.5, 88)):
            hatch.set(t, ang)
        # s5 从机库里往外看：她左手推开门跨进来，右手举起手电
        lin.place(16.0, (HATCH_X + 0.2, -0.4), 0, "stand", shoulder_l=75, elbow_l=20, lean=8)
        lin.place(17.3, (HATCH_X + 0.25, 0.9), 0, "walk_a", shoulder_l=40, elbow_l=30)
        lin.place(18.2, (HATCH_X + 0.3, 1.9), 0, "stand")
        lin.place(19.0, (HATCH_X + 0.3, 1.9), 0, "stand", shoulder_r=62, elbow_r=28, head_turn=-18)
        lin.place(19.5 - eps, (HATCH_X + 0.3, 1.9), 0, "stand", shoulder_r=62, elbow_r=28, head_turn=18)
        # s6 机库高处俯拍：她举着手电往深处走
        stride(lin, 19.5, 23.0 - eps, (HATCH_X, 9.0), (HATCH_X - 0.4, 13.4), shoulder_r=58, elbow_r=30)
        # s7–s10 在巨人的左手边
        g, tip = giant(st)                                                    # tip = 巨人左手最靠东那根手指的指尖顶面
        st.tip, st.head = tuple(tip), tuple(g.j["neck"].matrix_world @ Vector((0, 0, 0.2)))
        near = (tip.x + 0.42, tip.y - 0.3)                                   # 她蹲的位置：指尖的东南侧，伸手够得着
        touch = (tip.x, tip.y + 0.06, tip.z + 0.05)                           # 她的左手（靠镜头这一侧）按在指尖上，右手举着手电
        crouch = dict(pose="kneel", head_nod=-8)
        lin.place(23.0, near, (tip.x, tip.y), **crouch)
        lin.place(23.0, near, (tip.x, tip.y), hands={"l": (touch[0] + 0.1, touch[1] - 0.1, touch[2] + 0.26)}, **crouch)
        lin.place(24.4, near, (tip.x, tip.y), hands={"l": touch}, **crouch)
        lin.place(26.0 - eps, near, (tip.x, tip.y), hands={"l": touch}, **crouch)
        # s8 她的脸：先低头看手，再慢慢抬头
        crouch = dict(pose="kneel")
        lin.place(26.0, near, (tip.x, tip.y), hands={"l": touch}, head_nod=-8, **crouch)
        lin.place(27.2, near, (tip.x, tip.y), hands={"l": touch}, head_nod=-34, head_turn=-20, **crouch)
        lin.place(28.5 - eps, near, (tip.x, tip.y), hands={"l": touch}, head_nod=-62, head_turn=-30, **crouch)
        st.scene.frame_set(st.frame(26.0))
        st.face = tuple(lin.landmarks()["head"])                              # s8 开头她的头在哪（架机位用）
        # s9 她站起来退一步，手电往上举
        back = (near[0] + 0.5, near[1] - 0.8)
        up = dict(pose="stand", head_nod=-40, lean=-8)
        lin.place(28.5, near, st.head, shoulder_r=60, elbow_r=30, **up)
        lin.place(30.0, back, st.head, shoulder_r=95, elbow_r=20, **up)
        lin.place(32.5 - eps, back, st.head, shoulder_r=125, elbow_r=12, **up)
        # s10 全景：她站在巨人手边，仰着头
        lin.place(32.5, back, st.head, shoulder_r=125, elbow_r=12, **up)
        lin.place(37.5, back, st.head, shoulder_r=125, elbow_r=12, **up)
        # s6b（成片里在 s6 和 s7 之间）：她举着手电走到那几根「圆木」跟前，停在一米多外，手电往下照，低头看；凑近一步，跪坐下来（就是 s7 开头的位置）
        a0, a1, a2 = (near[0] + 0.55, near[1] - 2.7), (near[0] + 0.2, near[1] - 1.3), (near[0] + 0.05, near[1] - 0.45)
        look = (tip.x - 0.2, tip.y + 0.1)
        stride(lin, 40.0, 41.0, a0, a1, shoulder_r=52, elbow_r=35)
        lin.place(41.5, a1, look, "stand", shoulder_r=42, elbow_r=30, head_nod=22, lean=8)
        lin.place(42.3, a1, look, "stand", shoulder_r=42, elbow_r=30, head_nod=26, head_turn=-14, lean=14)
        lin.place(43.0, a2, look, "walk_a", shoulder_r=40, elbow_r=30, head_nod=26, lean=16)
        lin.place(43.7, near, (tip.x, tip.y), "kneel", head_nod=8)
        lin.place(44.0 - eps, near, (tip.x, tip.y), hands={"l": (touch[0] + 0.1, touch[1] - 0.1, touch[2] + 0.26)}, pose="kneel", head_nod=8)
        st.near = near
        if torch:                                                             # 手电：进机库以后才拿在手上
            for t, k in ((0, 0.001), (16.0 - eps, 0.001), (16.0, 1.0)):
                torch.scale = (k, k, k)
                torch.keyframe_insert("scale", frame=st.frame(t))
    if detail == 0 and torch:                                                 # 粗的一档只有外景，手电不出现
        torch.scale = (0.001, 0.001, 0.001)
    cameras(st, detail and not capsule)
    return st


def ship(st):
    """船：南侧面在 Y=0。下层船体 300 × 70 × 40（空心，里面是机库），上层 236 × 46 × 16，舰桥塔、尾部三个推进器、肋条。
    南侧面正中是机库大门（44 × 34，两扇），门上一个 18 米的橙色圆环；大门右扇脚下是小舱门（1.1 × 2.1）。"""
    H = 40.0
    st.wall((-150, 0), (-22, 0), height=H, thickness=2.0, color="hull", name="south_w")
    st.wall((22, 0), (150, 0), height=H, thickness=2.0, color="hull", name="south_e")
    st.box("south_top", (44, 2.0, H - 34), (0, 0, 34), color="hull", ground=False)
    st.wall((-22, 0), (22, 0), height=34, thickness=0.4, color="gate", name="gate", door=(22 + HATCH_X, 1.1, 2.1))     # 大门，脚下开小舱门洞
    st.wall((-150, 70), (150, 70), height=H, thickness=2.0, color="hull", name="north")
    st.wall((-150, 0), (-150, 70), height=H, thickness=2.0, color="hull", name="west")
    st.wall((150, 0), (150, 70), height=H, thickness=2.0, color="hull", name="east")
    st.box("roof", (300, 72, 1.5), (0, 35, H), color="hull", ground=False)
    st.box("upper", (236, 46, 16), (-6, 40, H + 1.5), color="hull2", ground=False)
    st.box("bridge", (26, 24, 26), (-92, 40, H + 17.5), color="hull2", ground=False)
    st.box("bridge_win", (22, 0.6, 3.0), (-92, 27.8, H + 36), color="black", ground=False)
    st.box("mast", (2.4, 2.4, 34), (-70, 44, H + 17.5), color="hull2", ground=False)
    for i, x in enumerate((30, 62, 94)):                         # 上层甲板上三个横放的大罐
        hcyl(st, f"tank{i}", 9, 40, (x, 40, H + 17.5 + 8), 0, "hull")
    for i in range(3):                                           # 船头（西端）一级一级收窄
        st.box(f"nose{i}", (70 - 18 * (i + 1), 22, H - 9 * (i + 1)), (-161 - 22 * i, 35, 0), color="hull", ground=False)
    for i, y in enumerate((13, 35, 57)):                         # 船尾（东端）三个推进器
        hcyl(st, f"engine{i}", 13, 34, (167, y, 20), 90, "hull2")
        hcyl(st, f"nozzle{i}", 13, 14, (191, y, 20), 90, "black", cone=1.25)
    for i, x in enumerate(range(-140, 141, 20)):                 # 南侧面的竖肋，每 20 米一根
        if abs(x) > 30:
            st.box(f"rib{i}", (2.4, 1.6, H), (x, -1.4, 0), color="hull2", ground=False)
    for sx in (-1, 1):
        st.box(f"band{sx}", (123, 1.2, 1.6), (sx * 88.5, -1.3, 19), color="hull2", ground=False)      # 半腰的横梁（大门两侧）
        st.box(f"jamb{sx}", (5, 3.4, 38), (sx * 24.5, -1.3, 0), color="hull2", ground=False)         # 大门的门框
        st.cylinder(f"piston{sx}", 2.6, 30, (sx * 31, -4.5), color="hull2")                          # 门框外的液压柱
        st.box(f"foot{sx}", (8, 8, 1.2), (sx * 31, -4.5, 0), color="hull2", ground=False)
    st.box("lintel", (54, 3.4, 5), (0, -1.3, 34), color="hull2", ground=False)
    st.box("seam", (0.5, 0.2, 34), (0, -0.3, 0), color="black", ground=False)         # 两扇门中间的缝
    hcyl(st, "ring", 9.0, 0.3, (0, -0.35, 19.5), 0, "ring", segs=48)                  # 门上的橙色圆环：橙色圆盘 + 门色的小圆盘
    hcyl(st, "ring_in", 6.6, 0.3, (0, -0.45, 19.5), 0, "gate", segs=48)
    st.box("seam2", (0.5, 0.2, 13.2), (0, -0.62, 12.9), color="black", ground=False)
    # ---- 小舱门周围：给人当尺子的东西
    st.box("sill", (2.6, 1.6, 0.1), (HATCH_X, -1.0, 0), color="hull2")
    st.box("hframe_top", (1.6, 0.12, 0.25), (HATCH_X, -0.26, 2.1), color="hull2", ground=False)
    for sx in (-1, 1):
        st.box(f"hframe{sx}", (0.25, 0.12, 2.1), (HATCH_X + sx * 0.68, -0.26, 0), color="hull2", ground=False)
        st.box(f"ladder{sx}", (0.06, 0.06, 26), (HATCH_X + 5 + sx * 0.25, -0.5, 0), color="yellow", ground=False)   # 检修梯，在小舱门东边 5 米
    for i in range(64):
        st.box(f"rung{i}", (0.5, 0.04, 0.04), (HATCH_X + 5, -0.5, 0.4 + 0.4 * i), color="yellow", ground=False)
    for i, (x, y) in enumerate(((3.4, -0.9), (2.7, -1.15), (3.1, -1.8))):               # 三个旧油桶，在小舱门西边
        st.cylinder(f"barrel{i}", 0.3, 0.9, (x, y), color="crate")
    st.box("rover", (1.9, 4.4, 1.0), (-9.5, -9, 0.45), heading=62, color="crate", ground=False)        # 一辆废弃的勘探车
    st.box("rover_cab", (1.7, 1.6, 0.9), (-10.2, -9.4, 1.45), heading=62, color="crate", ground=False)
    for i, (dx, dy) in enumerate(((-1.6, 0.2), (1.2, 1.7), (-0.2, -1.9), (2.6, -0.4))):
        hcyl(st, f"wheel{i}", 0.55, 0.4, (-9.5 + dx, -9 + dy, 0.55), 152, "black", segs=16)
    for i, (sz, at) in enumerate((((30, 12, 5), (-70, -9)), ((24, 10, 3.5), (66, -8)), ((16, 8, 2.0), (-16, -7.5)), ((40, 14, 7), (120, -10)), ((34, 12, 6), (-128, -9)),
                                  ((14, 7, 1.6), (36, -6)))):
        dune(st, f"dune{i}", sz, at)                             # 堆在船脚下的沙


def hangar(st):
    """机库：船肚子里 90 × 70 × 40 的空腔，地面是甲板；东西两面墙各有一排立柱，西墙 13 米高处一条检修走道，几个集装箱当尺子。"""
    x0, x1, y1, top = HANG
    st.floor(x0, 0.2, x1, y1 - 1, color="deck", name="deck")
    st.wall((x0, 0), (x0, y1), height=top, thickness=1.0, color="hull2", name="hang_w")
    st.wall((x1, 0), (x1, y1), height=top, thickness=1.0, color="hull2", name="hang_e")
    for i, y in enumerate(range(10, 70, 12)):
        for sx, x in ((-1, x0 + 1.2), (1, x1 - 1.2)):
            st.box(f"col{sx}{i}", (1.6, 1.6, top), (x, y, 0), color="hull", ground=False)
        st.box(f"beam{i}", (x1 - x0, 1.6, 2.0), (0, y, top - 2.0), color="hull", ground=False)
    st.box("walk", (2.4, 62, 0.25), (x0 + 2.2, 34, 13.0), color="hull", ground=False)
    st.box("walk_rail", (0.08, 62, 0.08), (x0 + 3.4, 34, 14.1), color="yellow", ground=False)
    for i, (x, y, hd, n) in enumerate(((-30, 12, 0, 2), (-27, 12, 0, 1), (30, 16, 90, 1), (-13, 60, 90, 1), (-30, 50, 0, 1))):
        for k in range(n):                                       # 集装箱 12.2 × 2.4 × 2.6
            st.box(f"crate{i}_{k}", (2.44, 12.2, 2.6), (x, y, 2.6 * k), heading=hd, color="crate", ground=False)
    st.box("stripe", (0.3, 52, 0.02), (HATCH_X, 27, 0.0), color="yellow", ground=False)      # 从小舱门往里的一条黄色地标线
    for i, (x, y, z) in enumerate(((16, 50, 14), (-14, 46, 12), (10, 14, 10))):
        lamp(st, f"lamp{i}", (x, y, z), LAMP_W, soft=3.0)


def giant(st):
    """巨人：和林同一款宇航服，站直 16 米（林的 9.5 倍），背靠机库北墙坐在甲板上，腿朝南伸直，头垂着、偏向左手。
    左臂垂在身侧，左手平放在甲板上、手指朝南：人偶自带的手是一块竖着的板，这里换成平放的手套（手掌 + 四根手指 + 拇指）。
    返回 (人偶, 食指指尖顶面的点)。"""
    y1 = HANG[2]
    g = Person(st, "巨人", "giant", GIANT_H, 1.0, (), legs="giant2", plate="ring")
    suit_up(st, g, pack="giant2")
    k = GIANT_H / 1.80
    at, seat = (0.0, y1 - 3.3, 0.0), 0.085 * (k - 1)            # blocking 的坐姿按真人算坐高，放大的人偶要自己把骨盆抬到位
    g.place(0.0, at, 180, "sit_floor", seat=seat, lean=10, head_nod=30, head_turn=24, hip_l=84, hip_r=84, knee_l=4, knee_r=4,
            shoulder_l=14, abduct_l=7, elbow_l=0, shoulder_r=14, abduct_r=7, elbow_r=0)
    bpy.data.objects["巨人_hand_l"].scale = (0.001, 0.001, 0.001)
    bpy.context.view_layer.update()
    w = g.j["elbow_l"].matrix_world @ Vector((0, 0, -0.27))     # 手腕
    y0 = w.y + 0.25                                              # 手套后缘
    st.box("glove_palm", (0.86, 0.62, 0.34), (w.x, y0 - 0.31, 0), color="giant", ground=False)
    for i in range(4):                                           # 四根手指，每根 0.19 宽、0.62 长：和她的小臂差不多粗
        st.box(f"glove_f{i}", (0.19, 0.62 - 0.05 * abs(i - 1.5), 0.2), (w.x - 0.33 + 0.22 * i, y0 - 0.62 - (0.62 - 0.05 * abs(i - 1.5)) / 2, 0), color="giant", ground=False)
    st.box("glove_thumb", (0.2, 0.5, 0.2), (w.x - 0.55, y0 - 0.55, 0), heading=215, color="giant", ground=False)
    st.box("glove_cuff", (0.9, 0.16, 0.5), (w.x, y0 + 0.02, 0), color="ring", ground=False)      # 手套口的橙色环
    return g, Vector((w.x - 0.33 + 0.22 * 3, y0 - 1.24 + 0.1, 0.2))                                # 最东边那根手指的指尖顶面


def cameras(st, full):
    cam = lambda *a, **k: setattr(st.camera(*a, **k).data, "clip_end", 5000.0)
    tx = HATCH_X
    cam("c1", C1, (4, 0, 22), lens=50)                                     # 大远景：荒原上很低的机位，斜着看船的南侧面，人是画面底下的一个小点
    st.camera_move("c1", 0.0, 4.0, tuple(a + (b - a) * 0.02 for a, b in zip(C1, (tx, 0, 1.7))), (4, 0, 22))      # 极慢的推近（6 米）
    cam("c2", (5.9, -67.5, 1.5), (3.5, 0, 11), lens=24)                    # 跟拍：在她右后方 5.5 米，跟着她往前走，船压满画面
    st.camera_key("c2", 4.0, (5.9, -67.5, 1.5), (3.5, 0, 11))
    st.camera_key("c2", 7.5, (5.9, -63.1, 1.5), (3.5, 0, 11))
    cam("c3", (tx + 6.5, -11.0, 1.3), (tx - 0.5, 0, 2.2), lens=24)         # 升起：从她右后方的低机位，升到 11.5 米、退到 29 米外
    st.camera_key("c3", 7.5, (tx + 6.5, -11.0, 1.3), (tx - 0.5, 0, 2.2))
    st.camera_move("c3", 8.2, 12.0, (tx + 10, -29.0, 11.5), (tx - 3, 0, 9.5))
    cam("c4", (tx + 2.9, -1.2, 1.35), (tx + 0.05, -0.45, 1.2), lens=40)     # 小舱门：她右侧的平视中景，门在画面右边
    cam("c5", (tx + 1.9, 5.6, 1.25), (tx + 0.15, 0, 1.15), lens=30)        # 反打：从机库里隔着黑看小舱门
    cam("c6", (-41.2, 36, 14.6), (tx - 1, 9, 0.5), lens=28)                # 机库高处（检修走道上）俯拍
    if full:
        t = Vector(st.tip)
        # 全景查看：机位在巨人两腿之间、左膝的上方 2 米，朝东略往下看。左膝顶面 1.05 米，再低就被它挡住；再偏北，手掌和小臂就进画了（一眼看出是手）。
        # 画面里只有四根手指的前半截（左下角）、她（从右边走进来）和空甲板；手指在左、她在右，和 s7 同一边
        cam("c6b", (0.0, 63.2, 2.05), (3.3, 63.33, 0.7), lens=28)
        cam("c7", (t.x - 0.62, t.y - 1.05, 0.72), (t.x - 0.03, t.y + 0.05, 0.24), lens=40)       # 大特写：巨人的指尖和她的手
        cam("c8", (t.x - 1.0, t.y + 0.1, 0.55), (st.face[0], st.face[1], st.face[2] - 0.08), lens=50)         # 她的脸：从巨人的手和大腿之间往东看
        c9 = (t.x + 3.2, t.y - 3.3, 0.5)
        cam("c9", c9, (t.x + 0.6, t.y - 0.4, 1.6), lens=20)                                     # 她身后的低机位，往上摇到巨人的头盔
        st.camera_key("c9", 28.5, c9, (t.x + 0.6, t.y - 0.4, 1.6))
        st.camera_move("c9", 29.0, 32.3, c9, (st.head[0] + 0.6, st.head[1], st.head[2] - 1.2))
        cam("c10", (17.5, 45.5, 2.4), (1.2, 64, 4.4), lens=35)                 # 全景：整个巨人和她
        st.camera_key("c10", 32.5, (17.5, 45.5, 2.4), (1.2, 64, 4.4))
        st.camera_move("c10", 33.0, 37.5, (22.5, 40.0, 4.6), (1.2, 64, 4.4))  # 缓慢后拉、升高


# ---------------------------------------------------------------- 大场景的平面图（blocking 的 plan() 按房间尺度画：110 像素/米，人是 0.22 米的圆）
def plan_big(st, path, t, region, px_per_m, title=""):
    from PIL import Image, ImageDraw, ImageFont
    from blocking import heading_vec
    st.scene.frame_set(st.frame(t))
    bpy.context.view_layer.update()
    x0, y0, x1, y1 = region
    px = lambda v: ((v[0] - x0) * px_per_m, (y1 - v[1]) * px_per_m)
    img = Image.new("RGB", (int((x1 - x0) * px_per_m), int((y1 - y0) * px_per_m) + 26), (245, 245, 245))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 14)
    rgb = lambda col: tuple(int(255 * min(1, v ** (1 / 2.2))) for v in (COLORS[col] if isinstance(col, str) else col))
    order = {"floor": 0, "step": 1, "wall": 2}
    skip = ("roof", "upper", "tank", "beam", "bridge", "mast", "walk", "south_top", "lintel", "ring", "seam", "band")
    for it in sorted((i for i in st.items if i["kind"] != "door" and not i["name"].startswith(skip)), key=lambda i: order.get(i["kind"], 3)):
        w, dp = it["size"][0], it["size"][1]
        f, r, c = heading_vec(it["heading"]), heading_vec(it["heading"] + 90), Vector((it["at"][0], it["at"][1], 0))
        d.polygon([px(c + r * sx * w / 2 + f * sy * dp / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))],
                  fill=(232, 228, 220) if it["kind"] == "floor" else (70, 70, 70) if it["kind"] == "wall" else rgb(it["color"]), outline=(120, 120, 120))
    for p in st.people.values():
        c = p.root.matrix_world.translation
        cx, cy = px(c)
        r = max(5, 0.25 * px_per_m)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(p.color), outline=(0, 0, 0))
        tip = px(c + p.forward() * max(0.6, 12 / px_per_m))
        d.line([(cx, cy), tip], fill=(0, 0, 0), width=3)
        d.text((cx + r + 3, cy - 8), p.name, fill=(0, 0, 0), font=font)
    if hasattr(st, "head") and y0 < HANG[2] - 3 < y1:              # 巨人：躯干、两条腿、左手（不在 st.people 里，自己画）
        gy = HANG[2] - 3.3
        for box in ((-2.2, gy - 1.2, 2.2, gy + 1.6), (-1.6, gy - 8.6, -0.1, gy - 1.2), (0.1, gy - 8.6, 1.6, gy - 1.2), (st.tip[0] - 1.0, st.tip[1] - 0.1, st.tip[0] + 0.2, st.tip[1] + 1.3)):
            d.rectangle([*px((box[0], box[3])), *px((box[2], box[1]))], fill=(225, 225, 215), outline=(60, 60, 60))
        d.text(px((-9.5, gy + 1.0)), "巨人", fill=(0, 0, 0), font=font)
    for name, c in st.cams.items():
        ob = c["obj"]
        pos = ob.matrix_world.translation
        if not (x0 <= pos.x <= x1 and y0 <= pos.y <= y1):
            continue
        fw = ob.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        fw.z = 0
        fw.normalize()
        half, side = math.atan(18 / ob.data.lens), Vector((fw.y, -fw.x, 0))
        for sgn in (-1, 1):
            d.line([px(pos), px(pos + (fw * math.cos(half) + side * sgn * math.sin(half)) * (60 / px_per_m))], fill=(200, 60, 0), width=2)
        cx, cy = px(pos)
        d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(200, 60, 0))
        d.text((cx + 7, cy + 4), name, fill=(200, 60, 0), font=font)
    step = 50 if px_per_m < 4 else 10 if px_per_m < 20 else 1
    for gx in range(math.ceil(x0 / step) * step, int(x1) + 1, step):
        d.line([px((gx, y0)), px((gx, y0 + 6 / px_per_m))], fill=(90, 90, 90))
        d.text((px((gx, y0))[0] + 2, img.height - 44), str(gx), fill=(90, 90, 90), font=font)
    d.text((6, img.height - 22), f"{title}  北(+Y)朝上，刻度每 {step} 米，t = {t:.1f} s", fill=(60, 60, 60), font=font)
    img.save(path)


def scale_note(st, cam, t):
    """这一镜里尺度怎么读：人占画面多高、离镜头多远。"""
    r = st.report(cam, t)
    lin = next(p for p in r["people"] if p["name"] == "林")
    return {"t": t, "lin_height_in_frame": lin["body_height_in_frame"], "lin_px_720": round(lin["body_height_in_frame"] * 720), "lin_distance_m": lin["distance_m"],
            "lin_shot": lin["shot"], "cam_height_m": r["height_m"], "pitch_deg": r["pitch_deg"], "lens_mm": r["lens_mm"]}


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--detail" in args:                                   # 粗的一档，只看外景两镜
        st = build(detail=int(args[args.index("--detail") + 1]))
        st.stills([s for s in SHOTS if s[0] in ("s1", "s3")], HERE / "wm/d0", last={"s3"})
        sys.exit()
    if "--capsule" in args:                                  # 胶囊替身的预演（参考视频用）
        st = build(capsule=True)
        st.scene.eevee.taa_render_samples = 8                # 预演不用 32 次采样：一帧从 3.5 秒降到 1 秒左右
        want = args[args.index("--capsule") + 1:]
        (HERE / "wm/cap").mkdir(parents=True, exist_ok=True)
        for name, cam, t0, t1 in SHOTS:
            if name in want:
                st.clip(cam, HERE / f"wm/cap/pv_{name}.mp4", t0, t1)
        sys.exit()
    st = build()
    only = [a for a in args if a.startswith("s")]
    shots = [s for s in SHOTS if not only or s[0] in only]
    notes = st.stills(shots, HERE / "wm", last=LAST)
    scale = {}
    for name, cam, t0, t1 in shots:
        scale[name] = scale_note(st, cam, t0)
        print(f"== {name} {t0}–{t1}s", json.dumps(scale[name], ensure_ascii=False), "\n" + notes[name])
        if name in LAST:
            scale[name + "_end"] = scale_note(st, cam, t1 - 2 / st.fps)
            print("   尾帧", json.dumps(scale[name + "_end"], ensure_ascii=False))
    if not only:
        json.dump({"notes": notes, "scale": scale}, open(HERE / "wm/notes.json", "w"), ensure_ascii=False, indent=1)
        plan_big(st, HERE / "wm/plan_site.png", 0.0, (-260, -270, 230, 90), 2.2, "全场：荒原、船、机位 c1 c2")
        plan_big(st, HERE / "wm/plan_gate.png", 12.0, (-40, -30, 45, 12), 14, "大门脚下：小舱门、检修梯、油桶、勘探车，机位 c3 c4 c5")
        plan_big(st, HERE / "wm/plan_hangar.png", 32.5, (-50, -4, 50, 74), 9, "机库：小舱门在下，巨人靠北墙，机位 c5–c10")
        print("flips:", st.flips(SHOTS))
        st.save(str(HERE / "wm/scene.blend"))
    if "--clips" in args:
        st.scene.eevee.taa_render_samples = 8
        st.previz(shots, HERE / ("wm/previz.mp4" if not only else "wm/previz_part.mp4"))

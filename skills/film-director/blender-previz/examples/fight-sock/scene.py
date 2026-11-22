"""《一只袜子》的白模：深夜自助洗衣店，一个场景、一条时间线、14 个镜头。

    PY=<装了 bpy 的 python>
    $PY scene.py stills            # wm/<镜头>_a.png（首帧）、_b.png（尾帧）、plan_*.png、wm/notes.json（describe、flips）
    $PY scene.py still s04 7.6 x   # 任意时刻的一张：wm/x.png
    $PY scene.py previz            # wm/previz.mp4 + wm/pv_<镜头>.mp4
    $PY scene.py unit R1 s04 s05 s06      # wm/pv_R1.mp4：几镜拼成一个单元的预演
    KIND=capsule $PY scene.py unit R1c s04 s05 s06   # 同上，人换成胶囊替身
    NEUTRAL=1 $PY scene.py still s04 7.0 s04n_a      # 不摆出招姿势（只有站位和朝向）的对照版

单位米、秒。北(+Y)是洗衣机墙，机位都在两人连线的南侧：大刘永远在画左，小满永远在画右。
"""
import math
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from blocking import Stage, POSES, Capsule, _mesh, _box  # noqa: E402  (it imports bpy, which must come before bmesh / mathutils)
import bmesh  # noqa: E402
from mathutils import Matrix  # noqa: E402

HERE = Path(__file__).parent
KIND = os.environ.get("KIND", "jointed")
NEUTRAL = bool(os.environ.get("NEUTRAL"))      # 只给站位，不摆出招的姿势

# ---------- 这场戏用到的姿势（skill 自带的只有站、坐、蹲、推……）
POSES.update({
    "guard":   {"shoulder_l": 55, "shoulder_r": 50, "elbow_l": 120, "elbow_r": 125, "hip_l": 20, "knee_l": 24, "hip_r": -14, "knee_r": 18, "lean": 8},
    "tense":   {"shoulder_l": 12, "shoulder_r": 12, "elbow_l": 35, "elbow_r": 35, "hip_l": 10, "knee_l": 12, "hip_r": -6, "knee_r": 8, "lean": 4},
    "load":    {"lean": 62, "hip_l": 28, "hip_r": 28, "knee_l": 48, "knee_r": 48, "head_nod": -20, "shoulder_l": 70, "shoulder_r": 70, "elbow_l": 15, "elbow_r": 15},
    "kick":    {"hip_r": 58, "knee_r": 12, "hip_l": -6, "knee_l": 10, "lean": -10, "shoulder_l": 30, "shoulder_r": -28, "elbow_l": 30, "elbow_r": 20},
    "windup":  {"twist": -55, "abduct_r": 70, "shoulder_r": -35, "elbow_r": 100, "shoulder_l": 55, "elbow_l": 110, "hip_l": 22, "knee_l": 26, "hip_r": -16, "knee_r": 20, "lean": 8},
    "hook":    {"twist": 60, "lean": 18, "shoulder_l": 20, "elbow_l": 105, "abduct_l": 15, "hip_l": 26, "knee_l": 34, "hip_r": -22, "knee_r": 16},
    "duck":    {"hip_l": 78, "hip_r": 70, "knee_l": 112, "knee_r": 104, "lean": 34, "shoulder_l": 62, "shoulder_r": 62, "elbow_l": 132, "elbow_r": 132, "head_nod": -12},
    "drive":   {"lean": 22, "hip_l": 38, "knee_l": 42, "hip_r": -20, "knee_r": 14, "shoulder_r": 20, "elbow_r": 95, "head_nod": -10},
    "hit":     {"lean": 50, "shoulder_l": 4, "shoulder_r": 4, "elbow_l": 100, "elbow_r": 100, "abduct_l": -8, "abduct_r": -8, "hip_l": 14, "hip_r": 14, "knee_l": 30, "knee_r": 30, "head_nod": 18},
    "lunge":   {"lean": 24, "hip_l": 34, "knee_l": 36, "hip_r": -22, "knee_r": 16, "shoulder_l": 70, "shoulder_r": 70, "elbow_l": 30, "elbow_r": 30},
    "pinned":  {"lean": -10, "hip_l": 8, "knee_l": 14, "hip_r": 8, "knee_r": 14, "shoulder_l": 40, "shoulder_r": 40, "elbow_l": 110, "elbow_r": 110, "head_nod": -8},
    "cocked":  {"twist": -40, "abduct_r": 68, "shoulder_r": -30, "elbow_r": 105, "hip_l": 24, "knee_l": 28, "hip_r": -16, "knee_r": 18, "lean": 12},
    "punch":   {"twist": 35, "lean": 20, "hip_l": 28, "knee_l": 32, "hip_r": -20, "knee_r": 14},
    "hurt":    {"lean": 22, "shoulder_r": 62, "elbow_r": 112, "shoulder_l": 58, "elbow_l": 100, "abduct_l": -12, "head_nod": 18, "hip_l": 10, "hip_r": 10, "knee_l": 20, "knee_r": 20},
    "grab":    {"lean": 14, "hip_l": 26, "knee_l": 30, "hip_r": -16, "knee_r": 14, "shoulder_l": 70, "shoulder_r": 70, "elbow_l": 40, "elbow_r": 40},
    "thrown":  {"lean": -14, "abduct_l": 72, "abduct_r": 30, "elbow_l": 35, "elbow_r": 70, "shoulder_r": 25, "hip_l": 16, "knee_l": 22, "hip_r": -8, "knee_r": 16, "head_nod": -14},
    "slump":   {"hip_l": 82, "hip_r": 70, "knee_l": 28, "knee_r": 8, "shoulder_l": 12, "shoulder_r": 12, "elbow_l": 28, "elbow_r": 28, "lean": -4, "head_nod": 22, "seat": 0.0},
    "pant":    {"lean": 42, "shoulder_l": 48, "shoulder_r": 48, "elbow_l": 12, "elbow_r": 12, "hip_l": 18, "hip_r": 18, "knee_l": 30, "knee_r": 30, "head_nod": -18},
    "sit_knees": {"hip_l": 112, "hip_r": 112, "knee_l": 118, "knee_r": 118, "shoulder_l": 55, "shoulder_r": 55, "elbow_l": 20, "elbow_r": 20, "lean": 6, "head_nod": 6, "seat": 0.0},
})

# 胶囊替身只认 skill 自带的 sit / crouch…：这场戏自己加的姿势也让它变矮
Capsule.LOW.update({"duck": 0.6, "load": 0.68, "hit": 0.8, "pant": 0.76, "slump": 0.5, "sit_knees": 0.5})

MACH_Y = 4.4                                   # 洗衣机墙的正面
COLS = [1.8 + 0.6 * i for i in range(9)]       # 9 列机器的中心 x：第 5 列 4.2（被打裂的烘干机）、第 6 列 4.8（她的洗衣机）、第 8 列 6.0（她被按上去的地方）
GLASS = (0.10, 0.12, 0.16)
T = {}                                         # 镜头名 -> (机位, 开始, 结束)


def disc(st, name, radius, at, axis="y", color=GLASS, depth=0.04):
    """A short cylinder whose flat face looks along the y axis (a round machine door) or the x axis (the same door standing open)."""
    def build(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=radius, radius2=radius, depth=depth)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X" if axis == "y" else "Y"), verts=bm.verts)
    return st._add(name, _mesh(name, build), color, loc=at)


def ponytail(st, p):
    """blocking.py 的带关节人偶没有 hair_long（只有胶囊替身有）：自己在头后面加一个发髻和一条马尾。"""
    if not hasattr(p, "j"):
        return
    hair = (0.05, 0.04, 0.04)
    for n, size, off in (("cap", (0.2, 0.2, 0.1), (0, -0.02, 0.27)), ("knot", (0.09, 0.09, 0.09), (0, -0.13, 0.25)), ("tail", (0.07, 0.07, 0.3), (0, -0.17, 0.08))):
        p.objs.add(st._add(f"{p.name}_{n}", _mesh(n, lambda bm, s=size, o=off: _box(bm, s, o)), hair, p.j["neck"]))


def hold(p, t0, t1, at, facing=None, pose=None, hands=None, **joints):
    """Same state from t0 until one frame before t1 (the next shot's first frame can then jump)."""
    p.place(t0, at, facing, pose, hands=hands, **joints)
    p.place(t1 - 1 / 30, at, facing, pose, hands=hands, **joints)


def build():
    st = Stage(fps=30)
    # ---------- 场地：8 × 5 米的自助洗衣店
    st.floor(0, 0, 8, 5)
    st.wall((0, 5), (8, 5))                                            # 北墙：洗衣机靠着它
    st.wall((0, 0), (0, 5), door=(1.2, 0.9, 2.05))                     # 西墙：靠南是玻璃店门
    st.door("店门", hinge=(0, 0.75), heading=0, width=0.9, color=(0.55, 0.70, 0.80), lock=0)
    st.wall((8, 0), (8, 5))                                            # 东墙
    st.wall((0, 0), (8, 0), color=(0.55, 0.70, 0.80))                  # 南墙：临街的玻璃橱窗（机位都在屋里，背对它）
    for i, x in enumerate(COLS):                                       # 下层洗衣机、上层烘干机，各一个圆门
        st.box(f"洗衣机{i + 1}", (0.58, 0.6, 0.88), (x, MACH_Y + 0.3, 0), color="white", ground=False)
        st.box(f"烘干机{i + 1}", (0.58, 0.6, 0.88), (x, MACH_Y + 0.3, 0.9), color="white", ground=False)
        st.box(f"面板{i + 1}", (0.5, 0.03, 0.1), (x, MACH_Y - 0.015, 0.76), color="grey", ground=False)
        if i != 5:
            disc(st, f"洗衣机门{i + 1}", 0.19, (x, MACH_Y - 0.02, 0.42))
        disc(st, f"烘干机门{i + 1}", 0.2, (x, MACH_Y - 0.02, 1.34))
    disc(st, "滚筒6", 0.17, (COLS[5], MACH_Y - 0.01, 0.42), color=(0.02, 0.02, 0.02), depth=0.02)    # 她那台洗衣机：门开着，看得见黑的滚筒口
    wdoor = disc(st, "洗衣机门6", 0.19, (COLS[5] + 0.21, MACH_Y - 0.2, 0.42), axis="x")               # 门扇朝外开着（合页在右）
    st.box("兑币机", (0.7, 0.45, 1.75), (0.75, 4.78, 0), color="orange", ground=False)                 # 西北角的兑币机：认方向用
    st.table("叠衣台", (7.55, 2.7, 0), heading=90, size=(1.7, 0.7, 0.86))
    st.cylinder("洗衣液1", 0.06, 0.28, (7.6, 3.2, 0.86), color="purple")
    st.cylinder("洗衣液2", 0.06, 0.24, (7.45, 2.9, 0.86), color="orange")
    basket = st.box("洗衣篮", (0.52, 0.38, 0.3), (4.2, 3.5, 0), color=(0.20, 0.65, 0.35), ground=False)
    sock = st.box("红袜子", (0.09, 0.22, 0.03), (4.2, 3.5, 0.3), heading=40, color="red", ground=False)
    cl = [st.box(f"衣服{i}", (0.34, 0.28, 0.04), (4.2, 3.5, 0.26), heading=30 * i, color=c, ground=False)
          for i, c in enumerate(((0.85, 0.85, 0.9), (0.75, 0.8, 0.95), (0.95, 0.85, 0.8)))]
    pile = st.box("烘干机里的衣服", (0.42, 0.36, 0.22), (COLS[4], MACH_Y + 0.3, 1.2), color=(0.9, 0.86, 0.8), ground=False)   # 第 5 列烘干机里的一堆衣服，最后掉到他头上

    # ---------- 人：身份色（蓝、黄），身高体型差得很大
    liu = st.person("大刘", "blue", at=(2.15, 2.6), facing=60, height=1.90, build=1.22, kind=KIND)
    man = st.person("小满", "yellow", at=(4.8, 3.9), facing=0, height=1.62, build=0.9, legs="black", kind=KIND,
                    marks=("hair_long",))
    ponytail(st, man)
    N = NEUTRAL

    def shot(name, cam, t0, t1):
        T[name] = (cam, t0, t1)

    door6 = (COLS[5], MACH_Y - 0.03, 0.45)
    dryer5 = (4.42, MACH_Y - 0.05, 1.42)             # 他的拳头砸在第 5 列烘干机的玻璃门上
    panel8 = (5.72, MACH_Y - 0.05, 1.48)             # 第二拳砸在她耳边的白铁皮上

    # ---------- s01 0–3.5 全景：她弯腰往洗衣机里放衣服，他从左边走进来，停在篮子旁
    shot("s01", "开场", 0.0, 3.5)
    hold(man, 0.0, 5.0, (4.8, 3.86), 0, "load", hands={"l": door6, "r": door6})
    liu.walk(0.0, 2.7, (3.72, 3.62))
    liu.place(3.4, (3.72, 3.62), 100, "stand", head_nod=20)
    # ---------- s02 3.5–5.0 贴地：他一脚把洗衣篮踢飞，衣服撒了一地，红袜子落在她脚边
    shot("s02", "贴地", 3.5, 5.0)
    liu.place(3.5, (3.72, 3.62), 105, "stand", head_nod=20)
    liu.place(3.85, (3.72, 3.62), 105, "kick")
    liu.place(4.3, (3.72, 3.62), 100, "stand")
    for ob, a, b, hd in ((basket, (4.2, 3.5, 0), (6.45, 2.95, 0), 75), (sock, (4.2, 3.5, 0.3), (4.98, 3.52, 0), 115),
                         (cl[0], (4.2, 3.5, 0.26), (5.15, 3.2, 0), 20), (cl[1], (4.2, 3.5, 0.26), (5.7, 3.35, 0), 70), (cl[2], (4.2, 3.5, 0.26), (6.05, 2.75, 0), 130)):
        st.key(ob, 3.85, at=a, heading=0)
        st.key(ob, 4.6, at=b, heading=hd)
    # ---------- s03 5.0–7.0 她的近景：低头看见脚边的袜子，再抬眼看他
    shot("s03", "她近景", 5.0, 7.0)
    liu.place(5.0, (3.82, 3.8), 88, "stand")
    man.place(5.0, (4.62, 3.9), 268, "tense", head_nod=28)
    man.place(5.9, (4.62, 3.9), 268, "tense", head_nod=28)
    man.place(6.4, (4.62, 3.9), 268, "tense", head_nod=-6)
    hold(man, 6.4, 7.0, (4.62, 3.9), 268, "tense", head_nod=-6)
    hold(liu, 5.0, 7.0, (3.82, 3.8), 88, "stand")
    # ---------- s04 7.0–8.8 侧面双人：他抡右拳，她往下一蹲，拳头从她头顶过去砸在烘干机门上
    shot("s04", "侧面", 7.0, 8.8)
    liu.place(7.0, (3.86, 3.86), 86, "tense" if N else "windup")
    man.place(7.0, (4.58, 3.92), 268, "tense" if N else "guard")
    liu.place(7.25, (3.86, 3.86), 86, "tense" if N else "windup")
    man.place(7.3, (4.58, 3.92), 268, "tense" if N else "guard")
    liu.place(7.6, (4.06, 3.9), 80, "hook", hands={"r": dryer5})
    man.place(7.6, (4.74, 3.78), 262, "duck")
    hold(liu, 7.6, 10.3, (4.06, 3.9), 80, "hook", hands={"r": dryer5})
    hold(man, 7.6, 10.25, (4.74, 3.78), 262, "duck")
    # ---------- s05 8.8–10.0 特写：拳头砸在烘干机的圆玻璃门上，玻璃裂成蛛网
    shot("s05", "烘干机特写", 8.8, 10.0)
    # ---------- s06 10.0–12.0 侧面近一点：她从下面起来，一拳顶进他肚子，他弯下腰退了两步
    shot("s06", "侧面近", 10.0, 12.0)
    man.place(10.6, (4.5, 3.86), 268, "guard", hands={"l": (4.2, 3.86, 1.12)})
    liu.place(10.6, (4.06, 3.9), 86, "hit")
    liu.place(11.3, (3.2, 3.84), 86, "hit", lean=36)
    man.place(11.2, (4.52, 3.88), 268, "guard")
    hold(liu, 11.3, 12.0, (3.2, 3.84), 86, "hit", lean=36)
    hold(man, 11.2, 12.25, (4.52, 3.88), 268, "guard")
    # ---------- s07 12.0–14.5 斜侧全景：他吼着扑上来揪住她的卫衣，顶着她往右退，把她后背撞在洗衣机墙上
    shot("s07", "斜侧", 12.0, 14.5)
    liu.place(12.0, (3.2, 3.84), 86, "tense" if N else "lunge")
    liu.place(12.6, (4.02, 3.84), 84, "grab", hands={"l": (4.42, 3.9, 1.22), "r": (4.42, 3.82, 1.22)})
    man.place(12.6, (4.55, 3.88), 266, "pinned")
    liu.place(13.5, (5.48, 3.62), 52, "drive", hands={"l": (5.86, 3.94, 1.26)})
    man.place(13.5, (6.0, 4.08), 232, "pinned")
    hold(liu, 13.5, 14.5, (5.48, 3.62), 52, "drive", hands={"l": (5.86, 3.94, 1.26)})
    hold(man, 13.5, 16.9, (6.0, 4.08), 232, "pinned")
    # ---------- s08 14.5–16.5 过他右肩：她被小臂压在机器上，他把右拳收到耳边
    shot("s08", "过肩", 14.5, 16.5)
    hold(liu, 14.5, 16.9, (5.48, 3.62), 52, "cocked", hands={"l": (5.86, 3.94, 1.26)})
    # ---------- s09 16.5–18.0 特写（升格）：她猛一偏头，拳头砸在她耳边的白铁皮上，砸出一个坑
    shot("s09", "耳边特写", 16.5, 18.0)
    liu.place(17.2, (5.52, 3.66), 46, "punch", hands={"r": panel8, "l": (5.9, 3.96, 1.26)})
    man.place(17.2, (6.1, 4.08), 236, "pinned", head_turn=28, twist=16)
    hold(liu, 17.2, 18.0, (5.52, 3.66), 46, "punch", hands={"r": panel8, "l": (5.9, 3.96, 1.26)})
    hold(man, 17.2, 19.8, (6.1, 4.08), 236, "pinned", head_turn=28, twist=16)
    # ---------- s10 18.0–19.5 他的近景：疼得缩回手直甩
    shot("s10", "他近景", 18.0, 19.5)
    hold(liu, 18.0, 19.8, (5.34, 3.52), 122, "hurt")
    # ---------- s11 19.5–22.0 侧面全景：她揪住他的皮夹克一拧身，借劲把他甩到洗衣机上，后背撞上去
    shot("s11", "侧面全", 19.5, 22.0)
    man.place(20.15, (5.72, 3.74), 240, "grab", hands={"l": (5.46, 3.5, 1.36), "r": (5.44, 3.6, 1.36)})
    liu.place(20.15, (5.34, 3.52), 122, "hurt")
    man.place(20.9, (5.9, 3.3), 290, "tense" if N else "lunge")
    liu.place(20.9, (4.24, 4.02), 176, "tense" if N else "thrown")
    hold(liu, 20.9, 22.4, (4.24, 4.02), 176, "tense" if N else "thrown")
    hold(man, 20.9, 22.0, (5.9, 3.3), 290, "tense" if N else "lunge")
    # ---------- s12 22.0–24.5 他的中景：顺着机器滑坐到地上，头顶裂了的烘干机门弹开，一堆衣服掉在他头上
    shot("s12", "他中景", 22.0, 24.5)
    hold(man, 22.0, 24.5, (5.9, 3.3), 286, "pant")
    liu.place(23.3, (4.24, 3.98), 178, "slump")
    hold(liu, 23.3, 30.9, (4.24, 3.98), 178, "slump")
    st.key(pile, 23.5, at=(COLS[4], MACH_Y + 0.3, 1.2))
    st.key(pile, 23.9, at=(4.24, 4.0, 1.02))
    # ---------- s13 24.5–27.2 贴着她那台洗衣机的低机位：她捡起地上的红袜子扔进滚筒，把圆门拍上，按启动；坐在旁边的他被关门声吓得一缩
    shot("s13", "洗衣机近", 24.5, 27.2)
    sock_at = (4.98, 3.52, 0.02)
    hold(man, 24.5, 25.0, (5.4, 3.62), 272, "crouch", hands={"r": sock_at})
    man.place(25.7, (5.3, 3.82), 292, "crouch", hands={"r": door6})
    man.place(26.3, (5.3, 3.82), 292, "crouch", hands={"r": (COLS[5] + 0.15, MACH_Y - 0.08, 0.5)})
    man.place(26.8, (5.3, 3.82), 292, "crouch", hands={"r": (COLS[5] + 0.12, MACH_Y - 0.03, 0.78)})
    man.place(27.2 - 1 / 30, (5.3, 3.82), 292, "crouch", hands={"r": (COLS[5] + 0.12, MACH_Y - 0.03, 0.78)})
    st.key(sock, 25.0, at=sock_at)
    st.key(sock, 25.7, at=(COLS[5], MACH_Y - 0.1, 0.45))
    st.key(sock, 25.9, at=(COLS[5], MACH_Y + 0.15, 0.4))
    st.key(wdoor, 26.0, at=(COLS[5] + 0.21, MACH_Y - 0.2, 0.42))
    st.key(wdoor, 26.3, at=(COLS[5] + 0.02, MACH_Y - 0.04, 0.42))
    # ---------- s14 27.2–31.0 全景（正对机器墙）：她转过身，靠着机器在他右边滑坐下来；两人中间的滚筒转起来
    shot("s14", "全景", 27.2, 31.0)
    man.place(27.2, (5.3, 3.82), 292, "crouch", hands={"r": (COLS[5] + 0.12, MACH_Y - 0.03, 0.78)})
    man.place(27.7, (5.3, 3.82), 292, "crouch")
    man.place(28.4, (5.5, 3.98), 180, "crouch")
    man.place(29.2, (5.5, 4.0), 180, "sit_knees")
    man.place(31.0, (5.5, 4.0), 180, "sit_knees")
    liu.place(31.0, (4.24, 3.98), 178, "slump")

    # ---------- 机位：全在两人连线的南侧
    st.camera("开场", (1.2, 1.2, 1.3), (4.8, 4.0, 1.0), lens=24)
    st.camera("全景", (4.6, 0.45, 1.2), (4.6, 4.4, 0.95), lens=24)
    st.camera("贴地", (5.75, 2.55, 0.16), (4.0, 3.75, 0.32), lens=24)
    st.camera("她近景", (3.9, 2.4, 1.48), (4.47, 3.9, 1.4), lens=50)
    st.camera("侧面", (4.3, 1.15, 1.38), (4.3, 4.4, 1.22), lens=35)
    st.camera("烘干机特写", (5.0, 3.3, 1.5), (4.4, 4.4, 1.4), lens=40)
    st.camera("侧面近", (4.05, 1.7, 1.2), (4.1, 4.4, 1.2), lens=40)
    st.camera("斜侧", (6.9, 1.2, 1.3), (5.3, 4.2, 1.15), lens=28)
    st.camera("过肩", (6.25, 2.5, 1.5), (5.85, 4.1, 1.45), lens=35)
    st.camera("耳边特写", (6.35, 2.9, 1.5), (5.9, 4.3, 1.48), lens=60)
    st.camera("他近景", (6.3, 2.5, 1.55), (5.4, 3.52, 1.55), lens=45)
    st.camera("侧面全", (5.4, 0.8, 1.3), (4.95, 4.2, 1.1), lens=28)
    st.camera("他中景", (4.9, 2.0, 0.7), (4.2, 4.3, 1.04), lens=26)
    st.camera("洗衣机近", (4.75, 2.0, 0.5), (4.8, 4.4, 0.64), lens=28)
    shots = [(n, c, a, b) for n, (c, a, b) in T.items()]
    return st, shots


LAST = {"s01", "s03", "s04", "s06", "s07", "s09", "s11", "s12", "s13", "s14"}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    st, shots = build()
    wm = HERE / "wm"
    wm.mkdir(exist_ok=True)
    if cmd == "stills":
        notes = st.stills(shots, wm, last=LAST)
        for t, n in ((0.0, "0"), (7.0, "7"), (13.6, "13"), (22.0, "22"), (30.9, "31")):
            st.plan(wm / f"plan_{n}.png", t=t, title="一只袜子")
        notes["flips"] = st.flips(shots)
        notes["order"] = {n: st.order(c, a) for n, c, a, b in shots}
        (wm / "notes.json").write_text(json.dumps(notes, ensure_ascii=False, indent=1))
        for k, v in notes.items():
            print("==", k, "\n", v)
    elif cmd == "still":
        name, t, out = sys.argv[2], float(sys.argv[3]), sys.argv[4]
        st.still(T[name][0], wm / f"{out}.png", t)
        print(st.describe(T[name][0], t))
    elif cmd == "previz":
        st.previz(shots, wm / "previz.mp4")
    elif cmd == "unit":
        st.previz([s for s in shots if s[0] in sys.argv[3:]], wm / f"pv_{sys.argv[2]}.mp4")
    elif cmd == "blend":
        st.save(str(wm / "scene.blend"))

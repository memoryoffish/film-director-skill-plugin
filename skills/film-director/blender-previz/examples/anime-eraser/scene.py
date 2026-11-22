"""《橡皮》白模：一间教室、一条时间线、12 个机位。

python scene.py              每镜首帧（和要用的尾帧）白模图、平面图、站位描述、越轴检查
python scene.py --previz     再渲染整片预演 wm/previz.mp4（24 fps，和成片同帧率）
镜头时长默认用下面的 DUR；目录里有 durations.json（{"s01": 3.1, …}）时用它的（成片剪完后按实际时长重出预演）。
"""
import json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from blocking import Stage, _box, _mesh  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "wm"
# 镜头表：名字、机位、时长（秒）
DUR = [("s01", "c01", 3.2), ("s02", "c02", 3.4), ("s03", "c03", 3.2), ("s04", "c04", 3.0), ("s05", "c05", 2.4), ("s06", "c06", 2.6),
       ("s07", "c07", 3.6), ("s08", "c08", 2.0), ("s09", "c09", 2.8), ("s10", "c10", 2.0), ("s11", "c11", 2.8), ("s12", "c12", 3.6)]
LAST = {"s04", "s07", "s08", "s11", "s12"}                 # 这几镜再出尾帧
if (HERE / "durations.json").exists():
    _d = json.loads((HERE / "durations.json").read_text())
    DUR = [(n, c, float(_d.get(n, d))) for n, c, d in DUR]
SHOTS, T, _t = [], {}, 0.0
for _n, _c, _dd in DUR:
    SHOTS.append((_n, _c, round(_t, 4), round(_t + _dd, 4)))
    T[_n] = (_t, _dd)
    _t += _dd

WOOD, STEEL, PAPER = (0.62, 0.45, 0.25), (0.33, 0.35, 0.38), (0.95, 0.95, 0.90)
COLS, ROWS = [1.2, 2.7, 4.2, 5.7], [5.3, 4.2, 3.1, 2.0]     # 4 列（x，从窗到走廊）× 4 排（y，从讲台往后）
SEAT = 0.42
HIDE = (0.4, 0.4, -5.0)                                       # 暂时不用的道具放到地板下面
GIRL_DESK, BOY_DESK = (COLS[2], ROWS[0]), (COLS[1], ROWS[2])  # 小满：第 1 排第 3 列；小野：第 3 排第 2 列
GIRL_AT, BOY_AT = (GIRL_DESK[0], GIRL_DESK[1] - 0.42), (BOY_DESK[0], BOY_DESK[1] - 0.42)
AISLE = 3.45                                                  # 两人之间那条过道的中线，正对讲桌
STOP = (3.62, 4.42)                                           # 橡皮停下的地方：过道里，离小满的椅子还差一截


def desk(st, name, x, y):
    st.box(f"{name}_top", (0.62, 0.42, 0.03), (x, y, 0.69), color=WOOD, ground=False)
    st.box(f"{name}_shelf", (0.56, 0.36, 0.02), (x, y, 0.56), color=STEEL, ground=False)
    for sx in (-1, 1):
        for sy in (-1, 1):
            st.box(f"{name}_leg{sx}{sy}", (0.03, 0.03, 0.69), (x + sx * 0.28, y + sy * 0.18, 0), color=STEEL, ground=False)


def chair(st, name, x, y):
    """椅面中心在 (x, y)，靠背在南边（人朝北坐）。"""
    st.box(f"{name}_seat", (0.40, 0.38, 0.03), (x, y, SEAT - 0.03), color=WOOD, ground=False)
    st.box(f"{name}_back", (0.40, 0.03, 0.22), (x, y - 0.19, 0.58), color=WOOD, ground=False)
    for sx in (-1, 1):
        st.box(f"{name}_fl{sx}", (0.025, 0.025, SEAT - 0.03), (x + sx * 0.18, y + 0.17, 0), color=STEEL, ground=False)
        st.box(f"{name}_bl{sx}", (0.025, 0.025, 0.80), (x + sx * 0.18, y - 0.19, 0), color=STEEL, ground=False)


def leg_to(p, t, side, target):
    """让一只脚够到一个点（blocking.py 的腿只能前后摆，这里给髋关节加一个绕竖轴的转角，膝盖按两段骨头算）。先 place() 再调。"""
    import bpy
    bpy.context.view_layer.update()
    hip, knee = p.j[f"hip_{side}"], p.j[f"knee_{side}"]
    from mathutils import Vector
    d = p.pelvis.matrix_world.inverted() @ Vector(target) - hip.location          # 模型单位（1.80 米的人偶）
    l1, l2 = 0.43, 0.49
    r, dn = min(d.length, l1 + l2 - 1e-3), d.normalized()
    alpha = math.acos(max(-1, min(1, (l1 * l1 + r * r - l2 * l2) / (2 * l1 * r))))
    gamma = math.acos(max(-1, min(1, (l1 * l1 + l2 * l2 - r * r) / (2 * l1 * l2))))
    hip.rotation_euler = (math.acos(max(-1, min(1, -dn.z))) + alpha, 0, math.atan2(-dn.x, dn.y))
    knee.rotation_euler = (-(math.pi - gamma), 0, 0)
    f = p.stage.frame(t)
    hip.keyframe_insert("rotation_euler", frame=f)
    knee.keyframe_insert("rotation_euler", frame=f)


def build():
    st = Stage(fps=24)
    eps = 1 / st.fps
    at = lambda shot, dt: T[shot][0] + (min(dt, T[shot][1] - eps) if dt >= 0 else T[shot][1] + dt)   # 镜头内的时刻；负数从镜头结尾往回数

    # ---- 教室：北墙是黑板和讲桌，西墙一排窗，东墙是走廊（前后两扇门），南墙是储物柜和布告栏
    W, D = 7.2, 8.6
    st.floor(0, 0, W, D)
    st.wall((0, 0), (0, D), height=3.0, name="west")
    st.wall((0, D), (W, D), height=3.0, name="north")
    st.wall((W, 0), (W, D), height=3.0, name="east")
    st.wall((0, 0), (W, 0), height=3.0, name="south")
    for i, y in enumerate((1.7, 4.3, 6.9)):                                          # 西墙三扇大窗（浅蓝色块）
        st.box(f"window{i}", (0.03, 2.0, 1.5), (0.08, y, 0.95), color=(0.55, 0.78, 0.98), ground=False)
    st.box("blackboard", (3.8, 0.04, 1.25), (AISLE, D - 0.09, 0.9), color=(0.05, 0.22, 0.14), ground=False)
    st.box("clock", (0.32, 0.04, 0.32), (AISLE, D - 0.09, 2.35), color="white", ground=False)
    for i, y in enumerate((1.1, 7.6)):                                               # 东墙前后两扇推拉门（棕色块）
        st.box(f"door{i}", (0.04, 1.0, 2.0), (W - 0.09, y, 0), color="door", ground=False)
    st.box("lockers", (4.4, 0.42, 0.9), (3.4, 0.28, 0), color=(0.55, 0.50, 0.42), ground=False)
    st.box("board", (2.4, 0.03, 1.0), (3.4, 0.08, 1.25), color=(0.25, 0.42, 0.30), ground=False)
    st.box("teacher_desk", (1.3, 0.6, 0.76), (AISLE, 7.2, 0), color=(0.40, 0.27, 0.16), ground=False)
    chair(st, "teacher_chair", AISLE, 7.86)
    for c, x in enumerate(COLS):
        for r, y in enumerate(ROWS):
            desk(st, f"desk{r}{c}", x, y)
            chair(st, f"chair{r}{c}", x, y - 0.42)
    for n, (x, y) in (("paper_g", GIRL_DESK), ("paper_b", BOY_DESK)):
        st.box(n, (0.21, 0.30, 0.006), (x - 0.02, y - 0.02, 0.72), color=PAPER, ground=False)

    girl = st.person("小满", "red", at=GIRL_AT, facing=0, height=1.58, build=0.92)
    boy = st.person("小野", "blue", at=BOY_AT, facing=0, height=1.72)
    teacher = st.person("老师", "purple", at=(AISLE, 7.86), facing=180, height=1.70, build=1.12, marks=("glasses",))
    bob = st._add("小满_hair", _mesh("bob", lambda bm: _box(bm, (0.235, 0.13, 0.24), (0, -0.06, 0.20))), (0.06, 0.05, 0.05), girl.j["neck"])   # 齐下巴的短发
    girl.objs.add(bob)
    sock = st._add("小满_sock", _mesh("sock", lambda bm: _box(bm, (0.105, 0.27, 0.08), (0, 0.07, -0.455))), "white", girl.j["knee_l"])   # 左脚只穿着白袜子（s07 起）
    girl.objs.add(sock)

    def show(ob, t, on):
        ob.scale = (1, 1, 1) if on else (0.001, 0.001, 0.001)
        ob.keyframe_insert("scale", frame=st.frame(t))

    show(sock, 0, False)

    # ---- 道具
    NEWS_Z = 0.84
    news = st.box("newspaper", (0.62, 0.015, 0.52), (AISLE, 7.54, NEWS_Z), color=(0.86, 0.86, 0.82), ground=False)
    eraser = st.box("eraser", (0.07, 0.04, 0.025), (*STOP, 0), color="yellow", ground=False)
    SHOE = (4.07, 5.22, 0)
    shoe = st.box("shoe", (0.09, 0.24, 0.07), SHOE, heading=25, color="white", ground=False)       # 小满脱在桌子底下的那只鞋
    sheet = st.box("sheet_up", (0.30, 0.012, 0.38), HIDE, color=PAPER, ground=False)               # 结尾小野竖起来挡脸的卷子
    for ob in (news, eraser, shoe, sheet):                                                         # 让平面图画它们当时的位置
        next(it for it in st.items if it["name"] == ob.name)["obj"] = ob
    st.key(shoe, 0, at=HIDE); st.key(sheet, 0, at=HIDE)

    def T_(t):   # 老师：坐在讲桌后面，两手举着报纸
        teacher.place(t, (AISLE, 7.86), 180, "sit", seat=SEAT, hands={"l": (AISLE + 0.29, 7.56, 1.08), "r": (AISLE - 0.29, 7.56, 1.08)}, head_nod=8)

    def G(t, nod=22, turn=0, twist=0, lean=16, rh=(0.12, -0.10), lh=(-0.15, -0.07), lap=False):
        """小满：坐着，手在桌上（rh / lh 是相对桌心的偏移），或两手放在腿上（lap）。"""
        gx, gy = GIRL_DESK
        hands = ({"l": (gx - 0.05, gy - 0.26, 0.62), "r": (gx + 0.05, gy - 0.26, 0.62)} if lap else
                 {"r": (gx + rh[0], gy + rh[1], 0.74), "l": (gx + lh[0], gy + lh[1], 0.74)})
        girl.place(t, GIRL_AT, 0, "sit", seat=SEAT, hands=hands, lean=lean, head_nod=nod, head_turn=turn, twist=twist)

    def B(t, nod=22, turn=0, lean=16, rh=(0.12, -0.10), lh=(-0.15, -0.07)):
        bx, by = BOY_DESK
        boy.place(t, BOY_AT, 0, "sit", seat=SEAT, hands={"r": (bx + rh[0], by + rh[1], 0.74), "l": (bx + lh[0], by + lh[1], 0.74)}, lean=lean, head_nod=nod, head_turn=turn)

    def B_down(t, nod=-25, turn=0, hand=(3.2, 3.02, 0.06)):
        """小野侧着身子探进过道，右手垂到地面（人偶只能往前弯腰，所以整个人转向过道再弯下去）。"""
        boy.place(t, (BOY_AT[0] + 0.10, BOY_AT[1] + 0.04), 90, "sit", seat=SEAT, lean=62, head_nod=nod, head_turn=turn, hands={"r": hand}, shoulder_l=20, elbow_l=70)

    # ---- s01 全景：三个人各在各的位置，两个学生埋头写
    T_(0)
    G(at("s01", 0)); B(at("s01", 0))
    st.key(eraser, 0, at=(BOY_DESK[0] + 0.2, BOY_DESK[1] + 0.08, 0.72))
    # ---- s02 小满：写错了，没有橡皮，用手指蹭；后景的小野抬头看她
    G(at("s02", 0)); G(at("s02", 0.6), nod=12)
    for i, dx in enumerate((0.0, 0.07, 0.0, 0.07, 0.0)):
        G(at("s02", 1.0 + 0.25 * i), nod=28, rh=(0.02 + dx, -0.06))
    G(at("s02", 2.7), nod=4, lean=6, rh=(0.02, -0.06))
    B(at("s02", 0)); B(at("s02", 1.2)); B(at("s02", 1.8), nod=0, turn=-28, lean=8)
    # ---- s03 小野：看她、瞄一眼老师、低头在橡皮上画，侧身探下去
    B(at("s03", 0), nod=0, turn=-28, lean=8); B(at("s03", 0.7), nod=0, turn=-28, lean=8)
    B(at("s03", 1.1), nod=-4, turn=-6, lean=8)
    er = (BOY_DESK[0] + 0.06, BOY_DESK[1] - 0.06)
    st.key(eraser, at("s03", 1.2), at=(BOY_DESK[0] + 0.2, BOY_DESK[1] + 0.08, 0.72))
    st.key(eraser, at("s03", 1.6), at=(*er, 0.74))
    B(at("s03", 1.6), nod=34, lean=22, rh=(0.10, -0.06), lh=(0.02, -0.06)); B(at("s03", 2.5), nod=34, lean=22, rh=(0.10, -0.06), lh=(0.02, -0.06))
    st.key(eraser, at("s03", 2.5), at=(*er, 0.74))
    B_down(at("s03", -eps), nod=-10)
    st.key(eraser, at("s03", -eps), at=(3.22, 3.04, 0.03))
    G(at("s03", 0), nod=4, lean=6, rh=(0.02, -0.06)); G(at("s03", 1.0))
    # ---- s04 地面机位：橡皮顺着过道滑出去，越滑越慢，停在过道中间
    B_down(at("s04", 0), nod=-20); B_down(at("s04", -eps), nod=-28)
    a0, a1 = (3.33, 3.66), STOP                                                      # 第一帧橡皮已经在画面左下角，正往前滑
    st.key(eraser, at("s04", 0) - eps, at=(3.22, 3.04, 0.03))
    for k in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):                                         # 减速滑行
        e = 1 - (1 - k) ** 2
        st.key(eraser, at("s04", 1.3 * k), at=(a0[0] + (a1[0] - a0[0]) * e, a0[1] + (a1[1] - a0[1]) * e, 0))
    G(at("s04", 0))
    # ---- s05 俯拍：两人都僵住盯着地上的橡皮，再一起看向讲台
    B_down(at("s05", 0), nod=-28); B_down(at("s05", 1.2), nod=-28); B_down(at("s05", 1.6), nod=-34, turn=55)
    G(at("s05", 0), nod=30, turn=70, twist=45, lean=4, lh=(-0.22, -0.16)); G(at("s05", 1.2), nod=30, turn=70, twist=45, lean=4, lh=(-0.22, -0.16))
    G(at("s05", 1.6), nod=-4, turn=14, lean=4)
    # ---- s06 老师翻报纸、咳一声；前景的小满坐得笔直
    G(at("s06", 0), nod=-2, turn=10, lean=2); G(at("s06", -eps), nod=-2, turn=10, lean=2)
    for dt, z in ((0, 0), (0.8, 0), (1.2, 0.06), (1.6, 0)):
        st.key(news, at("s06", dt), at=(AISLE, 7.54, NEWS_Z + z))
    B(at("s06", 0)); B(at("s06", -eps))
    # ---- s07 地面机位：小满的脚从鞋里退出来，伸直了够到橡皮，勾回椅子底下
    gx, gy = GIRL_AT
    seat_at = (gx - 0.12, gy - 0.02)                                                 # 往椅子左前角滑下去一点
    back = (3.90, 4.95)                                                              # 橡皮被勾回来的地方：椅子左边，手垂下去够得着

    def G_foot(t, foot):
        girl.place(t, seat_at, 322, "sit", seat=SEAT - 0.04, lean=-12, twist=-40, head_nod=24, head_turn=40, shoulder_l=35, elbow_l=70, shoulder_r=35, elbow_r=70)
        leg_to(girl, t, "l", foot)

    G(at("s07", 0), nod=24, turn=55, twist=30, lean=4); G(at("s07", 0.5), nod=24, turn=55, twist=30, lean=4)
    st.key(shoe, at("s07", 0) - eps, at=HIDE); st.key(shoe, at("s07", 0), at=SHOE)           # 这一镜起左脚已经从鞋里退出来
    show(sock, at("s07", 0) - eps, False); show(sock, at("s07", 0), True)
    G_foot(at("s07", 1.0), (3.86, 4.74, 0.10)); G_foot(at("s07", 1.7), (STOP[0] + 0.04, STOP[1] + 0.03, 0.04)); G_foot(at("s07", 2.0), (STOP[0] + 0.04, STOP[1] + 0.03, 0.04))
    G_foot(at("s07", 3.1), (back[0] + 0.04, back[1] + 0.03, 0.04)); G_foot(at("s07", -eps), (back[0] + 0.04, back[1] + 0.03, 0.04))
    st.key(eraser, at("s07", 2.0), at=(*STOP, 0)); st.key(eraser, at("s07", 3.1), at=(*back, 0)); st.key(eraser, at("s07", -eps), at=(*back, 0))
    # ---- s08 老师把报纸放低，眼睛从镜片上面往外看
    for dt, z in ((0, 0), (0.5, 0), (0.9, -0.26), (2.0, -0.26)):
        st.key(news, at("s08", dt), at=(AISLE, 7.54, NEWS_Z + z))
    for dt, hz in ((0, 1.08), (0.5, 1.08), (0.9, 0.82), (2.0, 0.82)):
        teacher.place(at("s08", dt), (AISLE, 7.86), 180, "sit", seat=SEAT, hands={"l": (AISLE + 0.29, 7.56, hz), "r": (AISLE - 0.29, 7.56, hz)}, head_nod=14 if hz < 1 else 8)
    # ---- s09 从讲桌看过去：两个人都坐得端端正正在写，过道里躺着一只鞋
    G(at("s09", 0)); B(at("s09", 0)); G(at("s09", -eps)); B(at("s09", -eps))
    st.key(eraser, at("s09", 0) - eps, at=(*back, 0)); st.key(eraser, at("s09", 0), at=(GIRL_DESK[0], GIRL_DESK[1] - 0.26, 0.64))
    # ---- s10 大特写：桌子底下摊开手心，橡皮上画着笑脸
    st.key(news, at("s10", 0) - eps, at=(AISLE, 7.54, NEWS_Z - 0.26)); st.key(news, at("s10", 0), at=(AISLE, 7.54, NEWS_Z))
    T_(at("s10", 0))
    palm = (3.93, 5.02, 0.50)
    for dt in (0, -eps):
        girl.place(at("s10", dt), GIRL_AT, 0, "sit", seat=SEAT, hands={"l": palm, "r": (GIRL_DESK[0] + 0.12, GIRL_DESK[1] - 0.10, 0.74)}, lean=8, head_nod=30, head_turn=50)
    st.key(eraser, at("s10", 0) - eps, at=(GIRL_DESK[0], GIRL_DESK[1] - 0.26, 0.64)); st.key(eraser, at("s10", 0), at=(palm[0], palm[1] + 0.03, palm[2] + 0.045)); st.key(eraser, at("s10", -eps), at=(palm[0], palm[1] + 0.03, palm[2] + 0.045))
    st.key(eraser, at("s11", 0), at=(GIRL_DESK[0], GIRL_DESK[1] - 0.26, 0.64))
    # ---- s11 小满侧脸：看着橡皮笑了，回头
    G(at("s11", 0), nod=42, lean=12, lap=True); G(at("s11", 1.5), nod=30, lean=10, lap=True); G(at("s11", -eps), nod=6, turn=75, twist=40, lean=4, lap=True)
    # ---- s12 越过小满的肩往后看：小野竖起卷子挡住脸，从卷子旁边伸出大拇指
    bx, by = BOY_AT
    st.key(sheet, at("s12", 0) - eps, at=HIDE); st.key(sheet, at("s12", 0), at=(bx + 0.17, by + 0.30, 0.95), heading=42); st.key(sheet, at("s12", -eps), at=(bx + 0.17, by + 0.30, 0.95), heading=42)
    for dt, up in ((0, 0), (1.3, 0), (1.9, 1), (3.6, 1)):
        hands = {"l": (bx + 0.03, by + 0.36, 1.08), "r": (bx + 0.42, by + 0.10, 1.28) if up else (bx + 0.30, by + 0.24, 1.08)}
        boy.place(at("s12", dt), BOY_AT, 0, "sit", seat=SEAT, hands=hands, lean=6, head_nod=10)
    G(at("s12", 0), nod=6, turn=75, twist=40, lean=4, lap=True); G(at("s12", -eps), nod=6, turn=75, twist=40, lean=4, lap=True)

    # ---- 机位：除了正对过道的几个，都在两人连线靠走廊的一侧（小野在画面左，小满在画面右，讲台在右）
    st.camera("c01", (6.7, 1.6, 2.5), (3.25, 4.5, 0.6), lens=22)           # 全景：教室后面靠走廊的角上，高机位
    st.camera("c02", (5.55, 5.62, 1.18), (3.8, 4.68, 0.90), lens=35)        # 小满中近景，后景左边是小野和窗
    st.camera("c03", (4.15, 4.05, 1.10), (2.78, 2.86, 0.98), lens=45)      # 小野中近景
    st.camera("c04", (3.45, 3.25, 0.08), (3.5, 6.8, 0.5), lens=22)         # 贴地：顺着过道往讲桌看
    st.camera("c05", (3.3, 0.55, 2.95), (3.55, 5.65, 0.0), lens=24)           # 俯拍：小野、橡皮、小满、讲桌
    st.camera("c06", (4.15, 3.95, 1.32), (3.45, 7.7, 1.05), lens=45)           # 越过小满的肩看老师
    st.camera("c07", (2.95, 3.82, 0.12), (3.86, 4.70, 0.22), lens=32)      # 贴地：橡皮在前，小满的脚和椅子在后
    st.camera("c08", (3.45, 5.75, 1.25), (3.45, 7.8, 1.17), lens=60)       # 老师正面近景
    st.camera("c09", (3.45, 7.42, 1.42), (3.5, 3.6, 0.5), lens=24)         # 老师的视线：从讲桌上方看全班
    st.camera("c10", (3.5, 4.62, 0.82), (3.93, 5.03, 0.54), lens=70)       # 大特写：腿上的手心和橡皮
    st.camera("c11", (5.35, 5.22, 1.0), (4.2, 4.98, 0.98), lens=40)       # 小满侧面近景
    st.camera("c12", (5.3, 5.6, 1.25), (2.95, 3.05, 1.0), lens=55)          # 越过小满的肩往后看小野
    return st


if __name__ == "__main__":
    st = build()
    notes = st.stills(SHOTS, OUT, last=LAST)
    for name, cam, t0, _t1 in SHOTS:
        print(name, f"{t0:.2f}", "从左到右：" + "、".join(st.order(cam, t0)), "\n" + notes[name])
    for k in sorted(notes):
        if k.endswith("_end"):
            print(k, "\n" + notes[k])
    st.plan(OUT / "plan.png", 0.0, scale=90, title="《橡皮》教室")
    st.plan(OUT / "plan_s05.png", T["s05"][0], scale=90, title="s05 橡皮停在过道里")
    for a, b, was, now in st.flips(SHOTS):
        print(f"{a} → {b}：左右换了（{'、'.join(was)} → {'、'.join(now)}），{b} 的提示词要写明新的左右")
    json.dump({"shots": SHOTS, "notes": notes}, open(OUT / "notes.json", "w"), ensure_ascii=False, indent=1)
    st.save(str(OUT / "scene.blend"))
    if "--previz" in sys.argv:
        st.previz(SHOTS, OUT / "previz.mp4")

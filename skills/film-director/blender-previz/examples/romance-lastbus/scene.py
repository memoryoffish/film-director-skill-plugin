"""《末班》白模：夜里的公交站，一张长椅，两个人。一个场景、一条时间线、9 个机位。

    PY=<装了 bpy 的 python>
    $PY scene.py              每镜首帧（和要用的尾帧）白模图、平面图、站位描述、两人间距、越轴检查 -> wm/
    $PY scene.py --previz     再渲染整部片的白模预演 wm/previz.mp4（和成片同样的镜头顺序和时长）
    $PY scene.py --clip s6    只渲染一个镜头的预演 wm/pv_s6.mp4（当参考视频用）；加 --capsule 换成胶囊替身

方向：长椅沿东西方向（X 轴），两人面朝南（-Y，朝马路）坐着；机位都在马路这一侧（y < 0.2），所以小夏永远在画面左边、阿远在右边。
公交车从东边（画面右边）来，往西（画面左边）开走。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from blocking import Stage, _box, _mesh  # noqa: E402

HERE = Path(__file__).parent
WM = HERE / "wm"
FAR = (30.0, 30.0)
SW = 0.15                      # 人行道比路面高
SEAT = SW + 0.45               # 椅面离路面
BY = 0.22                      # 坐着的人的 y

# 镜头表：名字、机位、开始、结束（秒）。成片按这张表剪。
SHOTS = [("s1", "wide", 0.0, 3.5), ("s2", "her", 3.5, 6.0), ("s3", "him", 6.0, 9.0), ("s4", "can", 9.0, 11.5), ("s5", "her", 11.5, 15.0),
         ("s6", "two", 15.0, 19.0), ("s7", "hands", 19.0, 21.5), ("s8", "faces", 21.5, 26.5), ("s9", "ots_her", 26.5, 30.0),
         ("s10", "ots_him", 30.0, 33.0), ("s11", "wide", 33.0, 37.0)]
LAST = {"s1", "s4", "s6", "s7"}      # 这几镜再出尾帧
XH0, XY0 = -0.58, 0.62         # 开场：小夏、阿远各坐一头（中心相距 1.20 米）
XH1 = 0.08                     # s6 小夏挪过来以后（中心相距 0.54 米，肩和肩之间约一个手掌）
XH2, XY2 = 0.12, 0.55          # s8 起：肩挨着肩（中心相距 0.43 米）


def add_hair(st, p, length=0.30):
    """blocking.py 的带关节人偶没有 hair_long（只有胶囊替身有）：在头后面加一块垂到肩的头发。"""
    if not hasattr(p, "j"):
        return
    ob = st._add(f"{p.name}_hairlong", _mesh("hairlong", lambda bm: _box(bm, (0.25, 0.10, length), (0, -0.075, 0.27 - length / 2))), (0.16, 0.09, 0.05), p.j["neck"])
    p._keep(ob)


def build(kind="jointed"):
    st = Stage(fps=30)
    eps = 1 / st.fps
    # ---- 场地：马路（南）、路缘、人行道、候车亭（长椅、背板、灯箱、顶棚、立柱）、站牌、后面的一排卷帘门
    st.floor(-8, -8, 8, -1.3, z=0.0, color=(0.16, 0.16, 0.18), name="road")
    st.floor(-8, -1.3, 8, 4.2, z=SW, color=(0.40, 0.40, 0.40), name="sidewalk")
    st.box("curb", (16, 0.16, SW), (0, -1.3, 0), color=(0.62, 0.62, 0.60), ground=False)
    st.box("bench_seat", (1.9, 0.45, 0.06), (0, 0.175, SEAT - 0.06), color=(0.45, 0.30, 0.16), ground=False)      # 木条长椅，没有靠背
    for i, x in enumerate((-0.8, 0.8)):
        st.box(f"bench_leg{i}", (0.06, 0.40, 0.39), (x, 0.175, SW), color="black", ground=False)
    st.box("shelter_back", (3.8, 0.05, 2.15), (0, 0.86, SW), color=(0.22, 0.25, 0.30), ground=False)             # 候车亭背板
    st.box("lightbox", (1.25, 0.08, 1.55), (0, 0.80, SW + 0.42), color=(0.97, 0.97, 0.92), ground=False)          # 发白光的空灯箱，正在长椅中段后面
    st.box("roof", (4.0, 1.5, 0.08), (0, 0.30, SW + 2.25), color=(0.22, 0.25, 0.30), ground=False)
    for i, x in enumerate((-1.9, 1.9)):
        st.cylinder(f"post{i}", 0.04, 2.25, (x, 0.86, SW), color=(0.22, 0.25, 0.30))
    st.cylinder("sign_pole", 0.035, 2.25, (2.75, -0.75, SW), color=(0.6, 0.6, 0.6))                                # 站牌
    st.box("sign", (0.5, 0.04, 0.5), (2.75, -0.75, SW + 1.72), color="orange", ground=False)
    st.wall((-8, 3.8), (8, 3.8), height=3.2, z=SW, color=(0.34, 0.34, 0.37), name="shops")                      # 关了门的店面

    # ---- 道具：便利店袋子、两罐热饮、末班车
    bag = st.box("bag", (0.24, 0.14, 0.22), (*FAR, 0), color="white", ground=False)
    can_her = st.cylinder("can_her", 0.033, 0.12, (*FAR, 0), color="yellow")
    can_him = st.cylinder("can_him", 0.033, 0.12, (*FAR, 0), color="yellow")
    bus = st.box("bus", (2.5, 10.0, 3.0), (60, -3.0, 0), heading=270, color=(0.75, 0.78, 0.80), ground=False)
    tail = [st.box(f"bus_tail{i}", (0.25, 0.05, 0.18), (60, -3.0, 0), heading=270, color="red", ground=False) for i in range(2)]
    for it in st.items:                       # 会动的道具记下物体，平面图才按当前时刻的位置画（blocking.py 的 box 只记初始位置）
        if it["name"] in ("bag", "can_her", "can_him", "bus"):
            it["obj"] = {"bag": bag, "can_her": can_her, "can_him": can_him, "bus": bus}[it["name"]]

    xia = st.person("小夏", "red", at=(XH0, BY), facing=180, pose="sit", height=1.62, build=0.92, marks=("hair_curly",), kind=kind)
    add_hair(st, xia)
    yuan = st.person("阿远", "blue", at=(2.6, -0.3), facing=270, height=1.80, build=0.95, marks=("glasses",), kind=kind)

    def sit(p, t, x, hands=None, **j):
        p.place(t, (x, BY), 180, "sit", hands=hands, **j)

    # ================= s1 0–3.5 全景：小夏坐在左头低头看手机；阿远从右边走进来，看她一眼，在最右头坐下
    sit(xia, 0.0, XH0, head_nod=18)
    sit(xia, 3.5, XH0, head_nod=18)
    yuan.walk(0.0, 1.6, (XY0, -0.3))
    yuan.place(2.0, (XY0, -0.12), 180, "stand")
    sit(yuan, 2.7, XY0)
    sit(yuan, 6.0, XY0)
    for t, at in ((0.0, (2.6, -0.55, 0.85)), (1.6, (XY0, -0.55, 0.85)), (2.0, (XY0 + 0.1, -0.35, 0.85)), (2.7, (0.86, 0.14, SEAT)), (37.0, (0.86, 0.14, SEAT))):
        st.key(bag, t, at=at)                                                    # 袋子先拎在手里，坐下后放在他右手边的椅面上
    # ================= s2 3.5–6.0 她的近景：眼睛往他那边溜一下，又收回来
    sit(xia, 4.2, XH0, head_nod=18)
    sit(xia, 4.8, XH0, head_turn=42, head_nod=5)
    sit(xia, 5.3, XH0, head_turn=42, head_nod=5)
    sit(xia, 5.9, XH0, head_nod=18)
    # ================= s3 6.0–9.0 他的近景：偷看她一眼，低头，从袋子里摸出一罐热饮攥在手里
    sit(yuan, 6.5, XY0)
    sit(yuan, 7.0, XY0, head_turn=-42)
    sit(yuan, 7.5, XY0, head_turn=-42)
    sit(yuan, 8.1, XY0, head_nod=28)
    sit(yuan, 9.0, XY0, head_nod=28)
    lap = lambda p: tuple(p.point("lap"))
    st.scene.frame_set(st.frame(9.0))
    hl = lap(yuan)
    st.key(can_him, 8.2 - eps, at=(*FAR, 0))
    st.key(can_him, 8.2, at=(hl[0], hl[1], hl[2]))                               # 他自己那罐：一直在他腿上
    st.key(can_him, 37.0, at=(hl[0] - (XY0 - XY2), hl[1], hl[2]))
    # ================= s4 9.0–11.5 特写：他的手把另一罐放到两人中间的椅面上，往她那边推过去
    c0, c1 = (0.26, 0.10, SEAT), (0.00, 0.10, SEAT)
    grab = lambda c: (c[0] + 0.03, c[1] - 0.02, c[2] + 0.10)
    sit(yuan, 9.0, XY0, head_nod=20, hands={"r": grab((0.42, 0.0, SEAT + 0.1))})
    sit(yuan, 9.8, XY0, head_nod=20, lean=8, hands={"r": grab(c0)})
    sit(yuan, 10.2, XY0, head_nod=20, lean=8, hands={"r": grab(c0)})
    sit(yuan, 11.0, XY0, head_nod=20, lean=16, twist=-25, hands={"r": grab(c1)})
    sit(yuan, 11.5 - eps, XY0, head_nod=10, lean=6, hands={"r": grab((0.30, 0.02, SEAT + 0.12))})
    sit(yuan, 11.5, XY0)
    for t, at in ((9.0 - eps, (*FAR, 0)), (9.0, (0.42, 0.0, SEAT + 0.1)), (9.8, c0), (10.2, c0), (11.0, c1), (13.4, c1)):
        st.key(can_her, t, at=at)
    # ================= s5 11.5–15.0 她的近景：低头看见那罐，摘下一只耳机，抬头看他，把罐子拿起来
    sit(xia, 11.5, XH0, head_turn=25, head_nod=30)
    sit(xia, 12.4, XH0, head_turn=25, head_nod=30)
    sit(xia, 13.4, XH0, head_turn=52, head_nod=0)
    st.scene.frame_set(st.frame(13.4))
    sit(xia, 14.2, XH0, head_turn=52, head_nod=0)
    sit(xia, 15.0, XH0, head_turn=30)
    hx = lap(xia)
    st.key(can_her, 14.2, at=hx)                                                 # 罐子到了她手里（腿上）
    st.key(can_her, 15.5, at=hx)
    # ================= s6 15.0–19.0 正面双人：她捧着罐子往他这边挪过来，停在一个手掌之外；他僵着看前面
    sit(yuan, 15.0, XY0)
    sit(yuan, 19.0, XY0, head_nod=6)
    sit(xia, 15.5, XH0, head_turn=30)
    for i in range(1, 5):                                                        # 2 秒挪 0.66 米，缓起缓停
        k = i / 4
        e = k * k * (3 - 2 * k)
        sit(xia, 15.5 + 2.0 * k, XH0 + (XH1 - XH0) * e, head_turn=30 * (1 - k))
    st.key(can_her, 17.5, at=(hx[0] + (XH1 - XH0), hx[1], hx[2]))
    sit(xia, 18.2, XH1)
    hold = (0.36, -0.04, SW + 0.92)                                              # 两人中间、胸口高：耳机在这里交到他手上
    sit(xia, 19.0 - eps, XH1, head_turn=35, hands={"l": hold})
    # ================= s7 19.0–21.5 特写：她的手递过来一只耳机，他的手接，指尖碰了一下
    sit(xia, 19.0, XH1, head_turn=35, hands={"l": hold})
    sit(xia, 21.5 - eps, XH1, head_turn=35, hands={"l": hold})
    sit(yuan, 19.0 + eps, XY0, head_turn=-20, head_nod=15, hands={"r": (0.50, -0.10, SW + 0.80)})
    sit(yuan, 20.3, XY0, head_turn=-20, head_nod=15, hands={"r": (hold[0] + 0.05, hold[1], hold[2])})
    sit(yuan, 21.5 - eps, XY0, head_turn=-20, head_nod=15, hands={"r": (hold[0] + 0.05, hold[1], hold[2])})
    # ================= s8 21.5–26.5 两张脸：肩挨着肩，一人一只耳机；他偷看她一眼；车从画右（东）来，两人一起转头看过去，谁都没起身；他转回来低头说「下一班吧」
    # （第一版是「两人抬眼看镜头这边的车」，拍出来成了盯着镜头；改成看画右，白模也跟着改）
    for p, x in ((xia, XH2), (yuan, XY2)):
        sit(p, 21.5, x, head_nod=12)
        sit(p, 22.2, x, head_nod=12)
    st.key(can_her, 21.5, at=(hx[0] + (XH2 - XH0), hx[1], hx[2]))
    st.key(can_her, 37.0, at=(hx[0] + (XH2 - XH0), hx[1], hx[2]))
    st.key(can_him, 21.5 - eps, at=hl)
    st.key(can_him, 21.5, at=(hl[0] - (XY0 - XY2), hl[1], hl[2]))
    sit(yuan, 22.6, XY2, head_turn=-38)
    sit(yuan, 23.0, XY2, head_turn=-38)
    sit(yuan, 23.4, XY2, head_nod=12)
    sit(xia, 23.6, XH2, head_nod=12)
    for p, x in ((xia, XH2), (yuan, XY2)):          # 一起往东（画右）看
        sit(p, 24.3, x, head_turn=55)
        sit(p, 25.3, x, head_turn=55)
    sit(yuan, 25.8, XY2, head_nod=22)
    sit(yuan, 26.5 - eps, XY2, head_nod=22)
    sit(xia, 26.5 - eps, XH2, head_turn=40)
    # ================= s9 26.5–30.0 越过他的肩拍她：她转过头看着他，「这是末班车。」
    sit(yuan, 26.5, XY2, head_nod=22)
    sit(yuan, 30.0, XY2, head_nod=22)
    sit(xia, 26.5, XH2, head_turn=20)
    sit(xia, 27.3, XH2, head_turn=58)
    sit(xia, 33.0, XH2, head_turn=58)
    # ================= s10 30.0–33.0 越过她的肩拍他：他转过来，对上她的眼睛，绷不住笑了，低头
    sit(yuan, 30.0 + eps, XY2, head_turn=-20, head_nod=10)
    sit(yuan, 30.8, XY2, head_turn=-58)
    sit(yuan, 32.2, XY2, head_turn=-58)
    sit(yuan, 33.0 - eps, XY2, head_turn=-40, head_nod=22)
    # ================= s11 33.0–37.0 全景：末班车的车尾从画面左边开出去，两个人还并排坐在长椅中间
    for p, x in ((xia, XH2), (yuan, XY2)):
        sit(p, 33.0, x)
        sit(p, 37.0, x)
    for ob, dx, dy, dz in ((bus, 0, 0, 0), (tail[0], 5.02, 0.9, 0.9), (tail[1], 5.02, -0.9, 0.9)):   # 车尾在车身东端
        for t, x in ((33.0 - eps, 60.0), (33.0, -6.6), (35.2, -18.0), (37.0, -40.0)):
            st.key(ob, t, at=(x + dx, -3.0 + dy, dz))

    # ---- 机位：都在马路这一侧
    st.camera("wide", (0.0, -6.6, 1.35), (0.0, 0.3, 1.15), lens=40)            # 马路对面，平视，全景
    st.camera("her", (0.75, -1.9, 1.38), (-0.42, BY, 1.30), lens=60)            # 她的近景：机位靠他这一侧，她看他就是看画面右
    st.camera("him", (-0.75, -1.9, 1.42), (0.46, BY, 1.36), lens=60)            # 他的近景：机位靠她这一侧，他看她就是看画面左
    st.camera("can", (0.02, -0.85, 1.25), (0.02, 0.10, SEAT + 0.05), lens=36)   # 俯拍两人中间的椅面
    st.camera("two", (0.05, -3.3, 1.30), (0.05, BY, 1.08), lens=45)             # 正面双人，膝盖以上
    st.camera("hands", (0.36, -1.05, 1.28), (0.36, -0.04, SW + 0.90), lens=58)    # 两人中间的手
    st.camera("faces", (0.33, -2.3, 1.38), (0.33, BY, 1.34), lens=70)           # 两张脸
    st.camera("ots_her", (1.15, -0.95, 1.42), (0.30, BY, 1.36), lens=75)        # 越过他的右肩拍她
    st.camera("ots_him", (-0.48, -0.95, 1.42), (0.36, BY, 1.38), lens=75)       # 越过她的左肩拍他
    return st, xia, yuan


def plan(st, path, t, title):
    """平面图：先把此刻放在远处（没出场）的道具拿掉，不然图幅被撑到几十米。"""
    st.scene.frame_set(st.frame(t))
    keep = st.items
    st.items = [it for it in keep if not (it.get("obj") is not None and abs(it["obj"].matrix_world.translation.x) > 9) and not it["name"].startswith("bus_tail")]
    st.plan(path, t=t, title=title, scale=150, margin=0.4)
    st.items = keep


def gap(xia, yuan, st, t):
    st.scene.frame_set(st.frame(t))
    a, b = xia.landmarks()["chest"], yuan.landmarks()["chest"]
    return round(((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5, 2)


if __name__ == "__main__":
    args = sys.argv[1:]
    kind = "capsule" if "--capsule" in args else "jointed"
    st, xia, yuan = build(kind)
    WM.mkdir(exist_ok=True)
    if "--clip" in args:
        name = args[args.index("--clip") + 1]
        _n, cam, t0, t1 = next(s for s in SHOTS if s[0] == name)
        print(st.clip(cam, WM / f"pv_{name}{'_cap' if kind == 'capsule' else ''}.mp4", t0, t1))
    elif "--previz" in args:
        print(st.previz(SHOTS, WM / "previz.mp4"))
    else:
        notes = st.stills(SHOTS, WM, last=LAST)
        plan(st, WM / "plan_t3.png", 3.4, "s1 末：各坐一头（相距 1.20 米）")
        plan(st, WM / "plan_t18.png", 18.0, "s6 末：她挪过来（0.54 米）")
        plan(st, WM / "plan_t25.png", 25.0, "s8：肩挨肩（0.43 米）")
        notes["_flips"] = st.flips(SHOTS)
        notes["_gap_m"] = {n: [gap(xia, yuan, st, t0), gap(xia, yuan, st, t1 - 1 / 30)] for n, _c, t0, t1 in SHOTS}
        notes["_order"] = {n: st.order(c, t0) for n, c, t0, _t1 in SHOTS}
        (WM / "notes.json").write_text(json.dumps(notes, ensure_ascii=False, indent=1))
        for k, v in notes.items():
            print(f"--- {k}\n{v}")
        st.save(str(WM / "scene.blend"))

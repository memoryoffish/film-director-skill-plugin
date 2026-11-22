"""《猫眼》白模：一条 11 米长的走廊、尽头一扇门、门里一间屋。一个场景、一条时间线、8 个机位、10 个镜头。

python scene.py              每镜首帧和尾帧白模图（wm/<镜头>_a.png、_b.png）、平面图、站位描述、越轴检查、视线检查
python scene.py --clips      再渲染整段预演 wm/previz.mp4 和每镜一条 wm/pv_<镜头>.mp4（机器空闲时约 10 分钟）
python scene.py --clips pov1 in     只重渲这几镜的 wm/pv_<镜头>.mp4
成片用的那条 previz.mp4（猫眼三镜带遮罩、结尾黑场）由 post.py 拿 wm/pv_<镜头>.mp4 拼。
python scene.py --dolly      只渲染「wide」这一镜的跟拍预演（胶囊替身），给参考视频那种喂法用：wm/pv_dolly.mp4
python scene.py --unit U2 eye,top,in     这几镜的胶囊替身预演，按切点拼好：wm/pv_U2_capsule.mp4

坐标（米）：走廊沿 +Y（北）走，宽 1.7（x 0…1.7），从 y=0（楼梯口）到 y=11（尽头的墙，林夏家的门在墙正中）。
楼梯口平台在 y<0；门里的屋子在 y>11，比走廊宽，门扇往屋里开、合页在西边，开到底时门扇和西墙之间有一个 1.3 米宽的角落。
"""
import json, math, sys
from pathlib import Path

SKILL = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, SKILL + "/scripts")
from blocking import Stage, _mesh, _box          # noqa: E402
import bpy                                       # noqa: E402
from mathutils import Vector                     # noqa: E402

HERE = Path(__file__).resolve().parent
WM = HERE / "wm"
W, L, H = 1.7, 11.0, 2.8                         # 走廊宽、长、层高
DOOR_Y = L                                       # 尽头那面墙
PEEP = (0.85, DOOR_Y, 1.55)                      # 猫眼
DOOR_OPEN = 78                                   # 门开到多少度停住。85 度时从 in 的机位看门扇只剩一条线（第一版成片里门画成了两扇），78 度看得见一窄条门的里面
IN_END = (1.1, 11.48)                           # 她进门后站住的地方：刚过门槛，门扇东边
FAR = (30.0, 30.0)
# 镜头表：名字、机位、开始、结束（秒）——成片的顺序和时长
SHOTS = [("pov1", "pov", 0.0, 5.0), ("wide", "wide", 5.0, 9.0), ("stop", "stop", 9.0, 12.5), ("gap", "gap", 12.5, 15.0),
         ("pov2", "pov", 15.0, 18.0), ("keys", "keys", 18.0, 21.0), ("pov3", "pov", 21.0, 24.0), ("eye", "eye", 24.0, 27.0),
         ("top", "top", 27.0, 31.0), ("in", "in", 31.0, 31.0 + 157 / 30)]    # 第二版：in 在手碰到开关的那一帧切黑，157 帧
LEAD = 1.5                                       # pov1 开头先看 1.5 秒空走廊，她才从楼梯口出来
T = {n: (a, b) for n, _c, a, b in SHOTS}


def wall_doors(st, a, b, doors, name, **kw):
    """A wall from a to b with several door openings: doors = [(distance from a to the door centre, width, height), …] in order.
    (blocking.wall only cuts one opening, so the wall is laid as one piece per door.)"""
    a, b = Vector((*a, 0)), Vector((*b, 0))
    u, length = (b - a).normalized(), (b - a).length
    cuts = [0.0] + [(doors[i][0] + doors[i + 1][0]) / 2 for i in range(len(doors) - 1)] + [length]
    for i, (c, w, h) in enumerate(doors):
        p, q = a + u * cuts[i], a + u * cuts[i + 1]
        st.wall((p.x, p.y), (q.x, q.y), name=f"{name}{i}", door=(c - cuts[i], w, h), **kw)


def fill_light(st, at, energy=40):
    """A shadowless lamp: with a ceiling on, the sun and the sky do not reach the corridor."""
    light = bpy.data.lights.new("fill", "POINT")
    light.energy, light.use_shadow, light.shadow_soft_size = energy, False, 0.5
    ob = bpy.data.objects.new("fill", light)
    ob.location = at
    st.scene.collection.objects.link(ob)


def hide_during(st, ob, t0, t1):
    """Leave an object out of the render between t0 and t1 (the ceiling, for the top shot)."""
    for f, v in ((1, False), (st.frame(t0) - 1, False), (st.frame(t0), True), (st.frame(t1) - 1, True), (st.frame(t1), False)):
        ob.hide_render = v
        ob.keyframe_insert("hide_render", frame=f)


def on_leaf(st, door, name, size, local, color):
    """A block fixed on a door leaf (it swings with the door). local = (out of the leaf: + is the face to the right of the door's
    heading, along the leaf from the hinge, height)."""
    return st._add(name, _mesh(name, lambda bm: _box(bm, size, local)), color, parent=door.root)


def sees(st, eye, target, ignore=()):
    """Is there a clear line from eye to target (world points)? Returns (True, None) or (False, name of what is in the way)."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    eye, target = Vector(eye), Vector(target)
    d = target - eye
    origin = eye.copy()
    for _ in range(20):
        hit, loc, _n, _i, ob, _m = st.scene.ray_cast(dg, origin, d.normalized(), distance=(target - origin).length - 0.02)
        if not hit:
            return True, None
        if ob.original.hide_render or any(ob.original in p.objs for p in ignore):
            origin = loc + d.normalized() * 1e-3
            continue
        return False, ob.name
    return True, None


def walk_flat(p, t0, t1, to, facing=None, end_pose="stand", z=0.0, stride_s=0.5, **joints):
    """blocking.Person.walk with the floor height given: inside a doorway ground() returns the top of the wall piece above the
    door, so walk() would lift the person onto the lintel for the keyframe that falls inside the wall thickness."""
    st = p.stage
    st.scene.frame_set(st.frame(t0))
    bpy.context.view_layer.update()
    a, b = p.root.matrix_world.translation.copy(), Vector((to[0], to[1], 0))
    head = facing if facing is not None else (b.x, b.y)
    n = max(1, round((t1 - t0) / stride_s))
    for i in range(n + 1):
        k = i / n
        q = a.lerp(b, k * k * (3 - 2 * k) if n > 3 else k)
        p.place(t0 + (t1 - t0) * k, (q.x, q.y, z), head if i == 0 or facing is not None else None,
                end_pose if i == n else ("walk_a" if i % 2 == 0 else "walk_b"), **joints)


def build(kind="jointed", dolly=False):
    st = Stage(fps=30)
    eps = 1 / st.fps
    # ---------------- 场地
    st.floor(-1.6, -2.4, W, 0, name="landing")                      # 楼梯口平台（楼梯在西边画外，没搭）
    st.floor(0, 0, W, L, name="corridor")
    st.floor(-0.9, L, 2.9, 14.6, name="room")
    wall_doors(st, (0, 0), (0, L), [(2.2, 0.85, 2.0), (5.6, 0.85, 2.0), (9.0, 0.85, 2.0)], "west")       # 401 403 405
    wall_doors(st, (W, -2.4), (W, L), [(3.9 + 2.4, 0.85, 2.0), (7.3 + 2.4, 0.85, 2.0)], "east")          # 402 404
    st.wall((-1.6, -2.4), (W, -2.4), name="landing_s")
    st.wall((-1.6, 0), (0, 0), name="landing_n")
    st.wall((-0.9, L), (2.9, L), thickness=0.2, door=(0.85 + 0.9, 0.9, 2.0), name="end")                  # 尽头的墙，正中是林夏家的门
    st.wall((-0.9, L), (-0.9, 14.6), name="room_w")
    st.wall((2.9, L), (2.9, 14.6), name="room_e")
    st.wall((-0.9, 14.6), (2.9, 14.6), name="room_n")
    ceil_a = st.box("ceil_corridor", (W + 1.6, L + 2.4, 0.1), ((W - 1.6) / 2, (L - 2.4) / 2, H), color="wall", ground=False)
    ceil_b = st.box("ceil_room", (3.8, 3.6, 0.1), (1.0, L + 1.8, H), color="wall", ground=False)
    st.box("solid_w", (0.84, 2.9, H), (-0.48, 9.45, 0), color=(0.03, 0.03, 0.03), ground=False)   # 正俯拍里走廊西墙外面：实心的黑（剖开的墙体），不画邻居家
    for y in (-1.2, 1.5, 4.0, 6.5, 9.0, 10.6):
        fill_light(st, (0.85, y, 2.3), 14)
    for at in ((0.4, 12.3, 2.3), (1.6, 13.4, 2.3), (-0.4, 11.6, 2.2)):
        fill_light(st, at, 12)
    # 两边的门：都关着
    for n, x, y in (("d401", 0, 2.2), ("d403", 0, 5.6), ("d405", 0, 9.0), ("d402", W, 3.9), ("d404", W, 7.3)):
        st.door(n, hinge=(x, y - 0.425), heading=0, lock=1.0)
    # 尽头的门：合页在西边门框，往屋里开；外面贴着红色福字，福字上方是猫眼
    door = st.door("door", hinge=(0.4, DOOR_Y), heading=90, width=0.9)
    on_leaf(st, door, "fu", (0.012, 0.34, 0.34), (0.031, 0.45, 1.28), "red")
    for sd in (-1, 1):
        on_leaf(st, door, f"peephole{sd}", (0.02, 0.04, 0.04), (sd * 0.03, 0.45, PEEP[2]), "yellow")
    for t, ang in ((0, 0), (T["in"][0] + 0.4, 0), (T["in"][0] + 1.9, DOOR_OPEN), (T["in"][1], DOOR_OPEN)):
        door.set(t, ang)
    for ob in (ceil_a, ceil_b, bpy.data.objects["end_top"], bpy.data.objects["door_lintel"]):   # 正俯拍：掀掉天花板和门上方那截墙，才看得见门扇
        hide_during(st, ob, *T["top"])
    st.box("doormat", (0.7, 0.42, 0.015), (0.85, 10.68, 0), color="maroon", ground=False)
    st.box("switch", (0.09, 0.02, 0.09), (1.55, DOOR_Y + 0.115, 1.3), color="white", ground=False)          # 屋里门东边墙上的开关
    # 认地方用的东西
    st.box("bike", (0.5, 1.7, 1.0), (W - 0.31, 5.6, 0), color="purple", ground=False)                       # 东墙边靠着的自行车
    st.box("hydrant", (0.2, 0.6, 0.8), (0.11, 3.9, 0.6), color="red", ground=False)                         # 西墙上的消火栓箱
    st.box("exit_sign", (0.5, 0.05, 0.2), (0.85, 0.0, 2.42), color="green", ground=False)                   # 走廊口吊着的绿色安全出口灯
    st.box("window", (1.1, 0.03, 1.1), (0.85, -2.33, 1.0), color=(0.55, 0.75, 0.95), ground=False)          # 楼梯间南墙的窗
    st.box("room_window", (1.4, 0.03, 1.2), (1.0, 14.53, 0.9), color=(0.55, 0.75, 0.95), ground=False)      # 屋里北墙的窗
    for i, y in enumerate((0.8, 4.4, 8.0)):
        st.ball(f"bulb{i}", 0.07, (0.85, y, 2.6), color="yellow")                                           # 三盏吊着的灯泡
    # 405 门缝下的一条光，光里两只脚的影子
    st.box("gap_light", (0.32, 0.8, 0.008), (0.19, 9.0, 0.0), color="yellow", ground=False)
    for i, y in enumerate((8.9, 9.12)):
        st.box(f"gap_shadow{i}", (0.2, 0.1, 0.01), (0.14, y, 0.0), color="black", ground=False)

    # ---------------- 人
    xia = st.person("林夏", "blue", at=(-1.2, -1.75), facing=90, height=1.63, kind=kind)
    man = st.person("男人", "red", at=(0.85, 11.4), facing=180, height=1.78, build=1.08, kind=kind)
    lock = door.lock_point(side=1)
    # pov1：她从楼梯口（西边画外）走上平台，转过来面朝走廊站住
    xia.place(LEAD + 0.4, (-1.2, -1.75), 90, "stand")
    xia.walk(LEAD + 0.4, LEAD + 2.2, (0.85, -1.1))
    xia.place(LEAD + 2.7, (0.85, -1.1), 0, "stand")
    xia.place(T["pov1"][1] - eps, (0.85, -1.1), 0, "stand")
    # wide：背对镜头沿走廊往里走
    xia.place(T["wide"][0], (0.95, 0.8), 0, "stand")
    xia.walk(T["wide"][0], T["wide"][1] - eps, (0.95, 5.0))
    # stop：走到 405 门前停下，头转向左前方的 405
    xia.place(T["stop"][0], (0.95, 6.4), 0, "walk_a")
    xia.walk(T["stop"][0], T["stop"][0] + 1.8, (0.95, 8.3))
    xia.place(T["stop"][0] + 2.4, (0.95, 8.3), 0, "stand", head_turn=55)
    xia.place(T["pov2"][0] + 0.3, (0.95, 8.3), 0, "stand", head_turn=55)
    # pov2：快步往自己家门走，边走边回头看 405
    xia.walk(T["pov2"][0] + 0.3, T["pov2"][1] - 0.2, (0.95, 9.75), head_turn=80, twist=25)
    xia.place(T["pov2"][1] - eps, (0.95, 9.75), 0, "stand", head_turn=80, twist=25)
    # keys：站在门前，右手拿钥匙够门锁，低头
    at_door = (0.95, 10.48)
    xia.place(T["keys"][0], at_door, 0, "stand", head_nod=24, hands={"r": (lock[0] - 0.02, lock[1] - 0.2, lock[2] + 0.12)})
    xia.place(T["keys"][0] + 1.8, at_door, 0, "stand", head_nod=24, hands={"r": lock})
    xia.place(T["keys"][1] - eps, at_door, 0, "stand", head_nod=24, hands={"r": lock})
    # pov3：钥匙插着，她回头越过左肩看 405，再转回来低头看锁
    xia.place(T["pov3"][0], at_door, 0, "stand", head_turn=75, twist=35, hands={"r": lock})
    xia.place(T["pov3"][0] + 1.4, at_door, 0, "stand", head_turn=75, twist=35, hands={"r": lock})
    xia.place(T["pov3"][0] + 2.2, at_door, 0, "stand", head_nod=24, hands={"r": lock})
    xia.place(T["in"][0] + 0.9, at_door, 0, "stand", head_nod=24, hands={"r": lock})
    # in：门开了，她跨进门里一步，回头朝走廊看一眼，再侧过身去够门边墙上的开关（第二版：侧面对镜头，不再背对镜头）
    xia.place(T["in"][0] + 1.5, at_door, 0, "stand")
    walk_flat(xia, T["in"][0] + 1.5, T["in"][0] + 3.0, IN_END)
    xia.place(T["in"][0] + 3.7, (*IN_END, 0), 0, "stand", head_turn=75, twist=35)                    # 回头朝走廊看一眼
    reach = dict(head_turn=-25, hands={"r": (1.55, DOOR_Y + 0.14, 1.3)})                              # 侧身朝东（画面左），右手够门边墙上的开关
    xia.place(T["in"][0] + 4.7, (*IN_END, 0), 100, "stand", **reach)
    xia.place(T["in"][1], (*IN_END, 0), 100, "stand", **reach)

    # 男人：一直贴在门里，眼睛对着猫眼，两只手撑在门上
    peeping = dict(lean=20, head_nod=-12, hands={"l": (1.12, DOOR_Y + 0.13, 1.45), "r": (0.58, DOOR_Y + 0.13, 1.45)})
    for t in (0, T["eye"][0] + 1.6):
        man.place(t, (0.85, 11.4, 0), 180, "stand", **peeping)
    # eye：门外钥匙一响，他把脸从猫眼上移开，往后退半步
    man.place(T["eye"][1] - 0.3, (0.85, 11.6, 0), 180, "stand")
    man.place(T["top"][0] + 0.6, (0.85, 11.6, 0), 180, "stand")
    # top：他面朝门，侧着挪进门扇开到底时挡得住的那个角落
    walk_flat(man, T["top"][0] + 0.6, T["top"][1] - 0.8, (-0.28, 11.52), facing=(0.9, 11.2))
    man.place(T["top"][1] - 0.3, (-0.28, 11.52, 0), 90, "stand")
    man.place(T["in"][1], (-0.28, 11.52, 0), 90, "stand")

    # ---------------- 机位
    st.camera("pov", (PEEP[0], DOOR_Y - 0.1, 1.53), (0.85, 0.0, 1.3), lens=14)          # 猫眼的视线：贴着门外侧，沿走廊往楼梯口看
    st.camera("wide", (0.5, -1.7, 1.5), (0.9, DOOR_Y, 1.2), lens=28)                    # 楼梯口平台上，她身后，顺着走廊看到尽头的门
    st.camera("stop", (1.25, 10.85, 1.45), (0.55, 8.4, 1.3), lens=35)                   # 走廊里迎着她拍，405 的门在画面右边
    st.camera("gap", (1.42, 9.55, 0.16), (0.0, 8.97, 0.1), lens=40)                     # 贴地，拍 405 的门缝
    st.camera("keys", (1.6, 9.75, 1.3), (1.05, DOOR_Y, 1.08), lens=40)                # 她右后方，拍手、钥匙、门锁
    st.camera("eye", (2.0, 11.55, 1.6), (0.8, 11.28, 1.52), lens=45)                   # 屋里，男人的侧脸和门
    top = st.camera("top", (0.4, DOOR_Y + 0.15, 7.5), (0.4, DOOR_Y + 0.15, 0.0), lens=62)             # 正俯拍，掀掉天花板：门外是她，门里是他
    top.rotation_euler = (0, 0, math.radians(90))                                        # 画面右边是北（屋里），左边是走廊
    top.keyframe_insert("rotation_euler", frame=1)
    st.camera("in", (0.62, 14.3, 1.1), (0.5, DOOR_Y, 1.15), lens=28)                    # 屋里，正对着门：门扇把画面分成两半
    if dolly:                                                                            # wide 的跟拍版：镜头跟着她往走廊里推
        st.camera("dolly", (0.5, -1.7, 1.5), (0.9, DOOR_Y, 1.2), lens=28)
        st.camera_move("dolly", T["wide"][0], T["wide"][1], (0.6, 1.3, 1.45), (0.9, DOOR_Y, 1.2))
    return st, xia, man, door


def eyelines(st, xia, man):
    """这场戏靠视线成立的几件事，从白模里量出来。"""
    out = []
    t = T["pov3"][0] + 0.5
    st.scene.frame_set(st.frame(t))
    head = xia.landmarks()["head"]
    d = (Vector(PEEP) - head).length
    out.append(f"pov3（{t:.1f}s）：她的头离猫眼 {d:.2f} 米")
    ok, what = sees(st, head, man.landmarks()["head"], ignore=(xia, man))
    out.append(f"  她看不看得见门里的男人：{'看得见' if ok else '看不见，被 ' + what + ' 挡住'}")
    for name, tt in (("pov1 结尾", T["pov1"][1] - 0.1), ("pov2 开头", T["pov2"][0]), ("pov2 结尾", T["pov2"][1] - 0.1), ("pov3", T["pov3"][0])):
        st.scene.frame_set(st.frame(tt))
        h = xia.landmarks()["head"]
        ok, what = sees(st, (PEEP[0], DOOR_Y - 0.1, PEEP[2]), h, ignore=(xia,))
        out.append(f"{name}：从猫眼到她 {(h - Vector(PEEP)).length:.1f} 米，{'看得见' if ok else '被 ' + str(what) + ' 挡住'}")
    # 405 的门缝：从猫眼看不看得见（它在侧墙上，猫眼只能顺着走廊看）
    ok, what = sees(st, (PEEP[0], DOOR_Y - 0.1, PEEP[2]), (0.19, 9.0, 0.02))
    out.append(f"从猫眼看 405 门缝下的光：{'看得见' if ok else '被 ' + str(what) + ' 挡住'}")
    # 结尾：门开到底，她站在屋里，看不看得见角落里的男人
    tt = T["in"][1] - 0.2
    st.scene.frame_set(st.frame(tt))
    for part in ("head", "chest"):
        ok, what = sees(st, xia.landmarks()["head"], man.landmarks()[part], ignore=(xia, man))
        out.append(f"in 结尾：她的眼睛到男人的{part}：{'看得见' if ok else '看不见，被 ' + what + ' 挡住'}")
    ok, what = sees(st, st.cams["in"]["obj"].matrix_world.translation, man.landmarks()["head"], ignore=(man,))
    out.append(f"in 结尾：镜头到男人的头：{'看得见' if ok else '被 ' + str(what) + ' 挡住'}")
    return out


if __name__ == "__main__":
    if "--dolly" in sys.argv:
        st, *_ = build(kind="capsule", dolly=True)
        st.clip("dolly", WM / "pv_dolly.mp4", *T["wide"])
        sys.exit()
    if "--unit" in sys.argv:                       # --unit U2 eye,top,in：这几镜的胶囊替身预演，按切点拼好
        name, names = sys.argv[sys.argv.index("--unit") + 1], sys.argv[sys.argv.index("--unit") + 2].split(",")
        st, *_ = build(kind="capsule")
        (WM / "capsule").mkdir(exist_ok=True)
        out = st.previz([s for s in SHOTS if s[0] in names], WM / "capsule" / f"pv_{name}.mp4")
        out.replace(WM / f"pv_{name}_capsule.mp4")
        sys.exit()
    st, xia, man, door = build()
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    shots = [s for s in SHOTS if not only or s[0] in only]
    notes = st.stills(shots, WM, last={s[0] for s in shots})
    for name, cam, t0, _t1 in shots:
        print(f"== {name}  从左到右：" + "、".join(st.order(cam, t0)) + "\n" + notes[name] + "\n  结尾：" + notes[name + "_end"].replace("\n", "\n  "))
    for a, b, was, now in st.flips(SHOTS):
        print(f"{a} → {b}：左右换了（{'、'.join(was)} → {'、'.join(now)}）")
    lines = eyelines(st, xia, man)
    print("\n".join(lines))
    if not only:
        st.items = [it for it in st.items if not it["name"].startswith("ceil")]      # plan() 会把天花板画在所有东西上面
        for t, tag in ((LEAD + 1.0, "0_arrive"), (T["stop"][0] + 2.5, "1_at405"), (T["pov3"][0] + 0.5, "2_atdoor"), (T["in"][1] - 0.5, "3_inside")):
            st.plan(WM / f"plan_{tag}.png", t, title=f"《猫眼》 {tag}")
        json.dump({"notes": notes, "eyelines": lines}, open(WM / "notes.json", "w"), ensure_ascii=False, indent=1)
        st.save(str(WM / "scene.blend"))
    if "--clips" in sys.argv:
        if only:                                   # 只重渲点名的几镜：wm/pv_<镜头>.mp4
            for name, cam, t0, t1 in shots:
                st.clip(cam, WM / f"pv_{name}.mp4", t0, t1)
        else:
            st.previz(SHOTS, WM / "previz.mp4")

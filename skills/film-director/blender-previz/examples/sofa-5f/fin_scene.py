"""《沙发》五楼到结尾（旧版 5-1 … 6-2，9 个镜头 33.8 秒）在一个白模里走一遍：一套布景、一条时间线、9 个机位。

python fin_scene.py            每个镜头的首帧（和要用的尾帧）白模图、平面图、布局说明
python fin_scene.py --clips    再渲染整段预演 previz.mp4（约 10 分钟）
"""
import json, math, sys
sys.path.insert(0, ".")
from pathlib import Path

from blocking import Stage

OUT = Path("out/fin")
RISE, RUN, STEPS = 0.165, 0.27, 9
Y0, Z0 = -RUN * STEPS, -RISE * STEPS
FAR = (9.0, 9.0)                                   # 不在这场戏里的人和东西先放到这里
# 镜头表：名字、机位、开始、结束（秒）
SHOTS = [("s51", "c51", 0.0, 3.5), ("s52", "c52", 3.5, 6.1), ("s53", "c53", 6.1, 9.6), ("s54", "c54", 9.6, 13.0), ("s55", "c55", 13.0, 15.4),
         ("s56", "c56", 15.4, 17.95), ("s57", "c57", 17.95, 21.2), ("s61", "c61", 21.2, 26.4), ("s62", "c62", 26.4, 33.8)]
LAST = {"s51", "s53"}                              # 这两个镜头还要尾帧（给首尾帧用）


def build():
    st = Stage(fps=30)
    eps = 1 / st.fps
    # ---- 布景：五楼平台（门在北墙正中）、楼梯从南边上来占西半边、栏杆在东半边、楼梯间南墙有窗，门里是空屋
    st.floor(0, 0, 2.4, 3.2)
    st.floor(-1.0, 3.2, 3.4, 6.5, name="room")
    st.floor(0, Y0 - 1.6, 2.4, Y0, z=Z0, name="lower")
    st.stairs("stairs", (0.6, Y0, Z0), 0, STEPS, RISE, RUN, 1.1)
    st.wall((0, Y0 - 1.6), (0, 3.2), height=2.8 - Z0, z=Z0, name="west")
    st.wall((2.4, Y0 - 1.6), (2.4, 3.2), height=2.8 - Z0, z=Z0, name="east")
    st.wall((0, Y0 - 1.6), (2.4, Y0 - 1.6), height=2.8 - Z0, z=Z0, name="south")
    st.wall((0, 3.2), (2.4, 3.2), door=(1.2, 0.85, 2.0), name="north")
    for n, a, b in (("room_s1", (-1.0, 3.2), (0, 3.2)), ("room_s2", (2.4, 3.2), (3.4, 3.2)), ("room_w", (-1.0, 3.2), (-1.0, 6.5)), ("room_e", (3.4, 3.2), (3.4, 6.5))):
        st.wall(a, b, name=n)
    st.box("rail", (1.2, 0.05, 0.05), (1.8, 0.0, 0.95), color="red", ground=False)
    for i in range(7):
        st.box(f"post{i}", (0.03, 0.03, 0.95), (1.22 + i * 0.193, 0.0, 0), color="red", ground=False)
    st.box("num5", (0.02, 0.42, 0.6), (0.07, 2.25, 1.35), color="red", ground=False)                          # 西墙上的红色「5」
    st.box("window", (0.9, 0.02, 0.8), (1.2, Y0 - 1.6 + 0.07, 0.9), color=(0.55, 0.75, 0.95), ground=False)   # 楼梯间南墙的窗
    door = st.door("door", hinge=(0.775, 3.2), heading=90)                                                    # 合页在西侧门框，往屋里开
    for t, ang in ((8.5, 0), (9.6 - 3 * eps, 90), (21.2 - eps, 90), (21.2, 0), (33.8, 0)):
        door.set(t, ang)

    # ---- 沙发：5-1 里被推到门前，之后一直横在门前（坐面朝楼梯这边，靠背贴着门所在的墙）
    sofa = st.sofa("沙发", (1.2, 1.55, 0), heading=180)
    for t, y in ((0, 1.55), (0.2, 1.55), (3.0, 2.66), (33.8, 2.66)):
        st.key(sofa, t, (1.2, y, 0))

    spec = {"阿杰": dict(color="blue", height=1.84, build=0.95, marks=("glasses",)),
            "小周": dict(color="red", height=1.66, build=1.14, marks=("cap_back", "shorts"), legs="black"),
            "大妈": dict(color="maroon", height=1.58, build=1.18, marks=("hair_curly",), legs="black")}
    a, z, m = (st.person(n, at=FAR, **spec[n]) for n in ("阿杰", "小周", "大妈"))

    # ---- 5-1 两人弓着腰把沙发推到门前，手按在沙发前沿
    for p, x in ((a, 0.5), (z, 1.9)):
        keys = [(0, 0.62, "push"), (0.2, 0.62, "push")] + [(0.2 + 0.4 * i, 0.62 + 1.11 * i / 7, "walk_a" if i % 2 else "walk_b") for i in range(1, 8)]
        keys += [(3.5 - eps, 1.73, "push")]
        for t, y, pose in keys:
            st.scene.frame_set(st.frame(t))
            edge = sofa.location.y - 0.42
            legs = {} if pose != "push" else dict(hip_l=38, knee_l=42, hip_r=-20, knee_r=10)
            p.place(t, (x, y), 0, "stand" if pose == "push" else pose, hands={"l": (x - 0.16, edge, 0.5), "r": (x + 0.16, edge, 0.5)}, lean=46, head_nod=-18, **legs)
    # ---- 5-2 直起腰，面对面，隔着半步击掌（靠镜头这一侧的手在两人中间碰上）
    clap = (1.2, 1.74, 1.62)
    for p, x, face, hand in ((a, 0.74, 90, "r"), (z, 1.66, 270, "l")):
        nod = -6 if p is z else 6
        for t, up in ((3.5, 0), (4.2, 0), (4.8, 1), (5.0, 1), (5.6, 0), (6.1 - eps, 0)):
            p.place(t, (x, 1.85), face, "stand", hands={hand: clap} if up else None, head_nod=nod)
    # ---- 5-3 阿杰一条腿跪在沙发坐面上，探身越过靠背，钥匙插进门锁，把门往里推开；小周在后面看着
    kneel = dict(hip_l=8, hip_r=8, knee_l=98, knee_r=98, lean=26, head_nod=12, shoulder_l=25, elbow_l=40)
    lock = door.lock_point()
    for t, pt in ((6.1, (lock[0] + 0.06, lock[1] - 0.15, lock[2] + 0.08)), (7.0, lock), (8.5, lock), (9.6 - eps, (1.48, 3.3, 1.0))):
        a.place(t, (1.4, 2.5, 0.42), 0, "stand", hands={"r": pt}, **kneel)
    z.place(6.1, (1.9, 1.75), facing=(1.5, 3.2), pose="stand")
    z.place(9.6 - eps, (1.9, 1.75), pose="stand")
    # ---- 5-4 … 5-7 门开了，两人并排站在沙发后面：看门、低头看沙发、再抬头、发呆
    for p, x in ((a, 0.85), (z, 1.55)):
        for t, nod in ((9.6, 0), (15.9, 0), (16.6, 34), (17.2, 34), (17.8, 0), (21.2 - eps, 0)):
            p.place(t, (x, 1.8), facing=0, pose="stand", head_nod=nod)
    # ---- 6-1 屋里：两人背靠着关上的门坐在地板上吃外卖（从屋里往门拍，阿杰在画面左）
    for p, x in ((a, 1.5), (z, 0.9)):
        box = st.box(f"饭盒_{p.name}", (0.19, 0.14, 0.05), (*FAR, 0), color="white", ground=False)
        for t, at in ((21.2 - eps, (*FAR, 0)), (21.2, (x - 0.06, 3.86, 0.26)), (26.4 - eps, (x - 0.06, 3.86, 0.26)), (26.4, (*FAR, 0))):
            st.key(box, t, at)
        base = dict(lean=-6, hip_l=84, hip_r=84, knee_l=6, knee_r=6)
        n, t = 0, 21.2
        while t < 26.4 + 0.65:
            tt, k = min(t, 26.4 - eps), (n + (p is z)) % 2
            p.place(tt, (x, 3.46, 0), 0, "sit_floor", head_nod=16 - 12 * k, **base)                       # 先摆好身子，才知道嘴在哪
            p.place(tt, (x, 3.46, 0), 0, "sit_floor", head_nod=16 - 12 * k, **base,
                    hands={"l": (x - 0.06, 3.84, 0.34), "r": tuple(p.point("mouth")) if k else (x + 0.04, 3.84, 0.4)})
            t, n = t + 0.65, n + 1
        p.place(26.4, FAR, facing=0, pose="stand")
    # ---- 6-2 门外：大妈坐在堵门的沙发正中间剥毛豆
    bowl = st.box("碗", (0.16, 0.16, 0.07), (*FAR, 0), color="white", ground=False)
    for t, at in ((26.4 - eps, (*FAR, 0)), (26.4, (1.2, 2.3, 0.56)), (33.8, (1.2, 2.3, 0.56))):
        st.key(bowl, t, at)
    m.place(26.4 - eps, FAR, facing=180, pose="stand")
    n, t = 0, 26.4
    while t <= 33.8:
        k = n % 2
        m.place(t, (1.2, 2.62), facing=180, pose="sit", seat=0.42, head_nod=24, shoulder_l=12, shoulder_r=12, abduct_l=-8, abduct_r=-8, elbow_l=62 + 10 * k, elbow_r=72 - 10 * k)
        t, n = t + 0.5, n + 1

    # ---- 机位
    st.camera("c51", (1.95, -1.9, 2.05), (1.1, 2.6, 0.7), lens=27)         # 全景：从楼梯口上方越过栏杆往门拍
    st.camera("c52", (1.2, -0.6, 1.45), (1.2, 1.85, 1.42), lens=34)        # 中景：两人侧面相对
    st.camera("c53", (2.05, 2.3, 1.4), (1.52, 3.17, 0.98), lens=45)        # 近景：门锁和手
    st.camera("c54", (1.2, -1.5, 1.6), (1.2, 3.2, 0.95), lens=30)          # 全景：从两人身后正对着门
    st.camera("c55", (1.15, 1.95, 1.45), (0.52, 3.15, 0.72), lens=45)      # 特写：扶手顶在门框外的墙上
    st.camera("c56", (1.2, 4.55, 1.35), (1.2, 1.8, 1.05), lens=30)         # 中景：从屋里隔着门框正面拍两人，沙发靠背横在门洞下半截
    st.camera("c57", (1.2, 3.3, 1.62), (1.2, 1.8, 1.6), lens=40)           # 近景：两张脸并排
    st.camera("c61", (1.2, 6.3, 0.95), (1.2, 3.3, 0.45), lens=30)          # 屋里：机位偏低，正对门的里面
    st.camera("c62", (1.2, -1.0, 1.3), (1.2, 3.2, 0.85), lens=32)          # 全景：正对关着的门
    return st


if __name__ == "__main__":
    st = build()
    notes = st.stills(SHOTS, OUT, last=LAST)
    for name, cam, t0, _t1 in SHOTS:
        print(name, "从左到右：" + "、".join(st.order(cam, t0)), "\n" + notes[name])
        st.plan(OUT / f"{name}_plan.png", t0, title=name)
    for a, b, was, now in st.flips(SHOTS):
        print(f"{a} → {b}：左右换了（{'、'.join(was)} → {'、'.join(now)}），{b} 的提示词要写明新的左右")
    json.dump(notes, open(OUT / "notes.json", "w"), ensure_ascii=False, indent=1)
    st.save(str(OUT / "fin.blend"))
    if "--clips" in sys.argv:
        st.previz(SHOTS, OUT / "previz.mp4")

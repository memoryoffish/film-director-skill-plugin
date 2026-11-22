"""Fidelity experiment: three test shots, each built with jointed mannequins, capsule stand-ins or all-grey mannequins.

    $BLENDER_PY scene.py stills            # first / last stills, plans, notes, ground-truth tracks
    $BLENDER_PY scene.py previz s1:j s1:c  # previz clips of the named shot:figure pairs
    $BLENDER_PY scene.py strip s2:j        # a strip of previz frames to look at
    $BLENDER_PY scene.py round2            # ground truth + first still of the round-2 variants

Round 2 (does the film follow the mannequin's rhythm): s1c14 / s1c17 / s1c24 = the corridor walk at 1.4 / 1.7 / 2.4 steps a second,
s1x125 / s1x080 = the whole corridor shot 1.25 / 0.8 times as fast, s2e13 / s2e23 = the fight keyed with fast strikes, punch out at
1.3 s / 2.3 s, s3e = the room with the walk ending in front of the chair and a keyed sit-down. Previz: scene.py previz s1c14:j …

Shots: s1 corridor walk + camera backing away, s2 one beat of a fight (side, fixed camera), s3 enter, cross the room, sit (pan).
Figures: j = jointed (identity colours), c = capsule (identity colours), jg = jointed, all grey.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

SKILL = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, SKILL + "/scripts")
from blocking import Capsule, POSES, Stage  # noqa: E402

HERE = Path(__file__).resolve().parent
WM = HERE / "wm"
FPS = 30
DUR = {"s1": 5.0, "s2": 5.0, "s3": 6.0, "s3b": 6.0}
CAM = {"s1": "跟拍", "s2": "侧面", "s3": "摇", "s3b": "摇"}

# ---- poses the tool does not have (fight) and what they mean for a capsule (only its height)
POSES.update({
    "guard": {"shoulder_l": 58, "shoulder_r": 48, "elbow_l": 118, "elbow_r": 125, "hip_l": 20, "knee_l": 22, "hip_r": -14, "knee_r": 20, "lean": 8},
    "guard2": {"shoulder_l": 62, "shoulder_r": 44, "elbow_l": 112, "elbow_r": 128, "hip_l": 26, "knee_l": 32, "hip_r": -10, "knee_r": 28, "lean": 10},
    "punch_r": {"shoulder_r": 86, "elbow_r": 4, "shoulder_l": 52, "elbow_l": 125, "twist": 30, "lean": 14, "hip_l": 32, "knee_l": 30, "hip_r": -24, "knee_r": 12},
    "duck": {"lean": 40, "hip_l": 52, "knee_l": 78, "hip_r": 44, "knee_r": 82, "shoulder_l": 60, "shoulder_r": 55, "elbow_l": 125, "elbow_r": 125, "head_nod": -18},
    "body_punch": {"lean": 24, "twist": 28, "shoulder_r": 58, "elbow_r": 38, "shoulder_l": 55, "elbow_l": 125, "hip_l": 36, "knee_l": 42, "hip_r": -16, "knee_r": 22},
    "hurt": {"lean": 36, "shoulder_l": 34, "shoulder_r": 34, "elbow_l": 98, "elbow_r": 98, "hip_l": 22, "knee_l": 32, "hip_r": 10, "knee_r": 30, "head_nod": 22},
    "hurt2": {"lean": 34, "shoulder_l": 34, "shoulder_r": 34, "elbow_l": 98, "elbow_r": 98, "hip_l": -8, "knee_l": 26, "hip_r": 24, "knee_r": 34, "head_nod": 22},
})
POSES.update({     # round 2: doubled over with the forearms against the belly (the round-1 "hurt" holds the forearms out in front)
    "hurt_b": {"lean": 46, "shoulder_l": -6, "shoulder_r": -2, "elbow_l": 112, "elbow_r": 118, "hip_l": 24, "knee_l": 40, "hip_r": 8, "knee_r": 38, "head_nod": 26},
    "hurt_b2": {"lean": 42, "shoulder_l": -2, "shoulder_r": -6, "elbow_l": 116, "elbow_r": 110, "hip_l": -10, "knee_l": 30, "hip_r": 26, "knee_r": 42, "head_nod": 24}})
POSES["sit_mid"] = {"hip_l": 62, "hip_r": 62, "knee_l": 70, "knee_r": 70, "lean": 40, "shoulder_l": 30, "shoulder_r": 30, "elbow_l": 35, "elbow_r": 35}
Capsule.LOW.update({"duck": 0.66, "hurt": 0.84, "hurt2": 0.84})


def cast(st, fig, a_at, a_face, x_at, x_face, a_pose="stand", x_pose="stand"):
    """阿杰: tall, thin, glasses. 小周: a head shorter, stocky, cap worn backwards, shorts."""
    kind = "capsule" if fig == "c" else "jointed"
    grey = fig == "jg"
    a = st.person("阿杰", "grey" if grey else "blue", at=a_at, facing=a_face, pose=a_pose, height=1.83, build=0.94,
                  marks=("glasses",), plate="white", kind=kind)
    x = st.person("小周", "grey" if grey else "red", at=x_at, facing=x_face, pose=x_pose, height=1.66, build=1.14,
                  marks=("cap_back", "shorts"), plate="black" if grey else "white", kind=kind)
    return a, x


def walk_const(p, t0, t1, a, b, T, stride=0.5, phase=0, heads=None, swing=1.0):
    """Walk at constant speed (the shot starts and ends in mid-walk; Stage.walk always eases in and out):
    the person is at `a` at time T[0] and at `b` at T[1]; poses are keyed every `stride` seconds from t0 to t1."""
    i, t = 0, t0
    while t <= t1 + 1e-6:
        k = (t - T[0]) / (T[1] - T[0])
        extra = {"head_turn": heads(t)} if heads and p.__class__.__name__ == "Person" else {}
        if swing != 1.0 and p.__class__.__name__ == "Person":        # walk_a / walk_b with wider or narrower legs and arms (step length)
            f, r = ("l", "r") if (i + phase) % 2 == 0 else ("r", "l")
            extra.update({f"hip_{f}": 28 * swing, f"hip_{r}": -18 * swing, f"shoulder_{f}": -22 * swing, f"shoulder_{r}": 24 * swing})
        p.place(t, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), b if i == 0 else None,
                "walk_a" if (i + phase) % 2 == 0 else "walk_b", **extra)
        i, t = i + 1, t0 + (i + 1) * stride


def linear(st):
    """Make every key linear. blocking.py asks for linear keys through a preference, but in bpy 5.3 keyframe_insert still
    makes Bezier keys: a camera keyed at two times eases in and out instead of moving at constant speed."""
    import bpy
    for act in bpy.data.actions:
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:
                            k.interpolation = "LINEAR"
    return st


def keys(p, facing, rows):
    """rows = [(t, (x, y), pose, {joint: angle}), …]"""
    for i, (t, at, pose, *more) in enumerate(rows):
        extra = more[0] if more and p.__class__.__name__ == "Person" else {}
        p.place(t, at, facing if i == 0 else None, pose, **extra)


# ---------------------------------------------------------------- s1: corridor, two people walk to camera, camera backs away
def s1(fig="j", cad=None, k=1.0):
    """Round 2: cad = steps per second of both walkers at the same 1.3 m/s (the step length follows: legs and arms swing wider
    or narrower); k = the whole shot k times faster (walkers, camera, cadence), which is what speeding up the previz clip does."""
    st = Stage(fps=FPS)
    W, Y0, Y1 = 2.2, -3.0, 19.0
    st.floor(0, Y0, W, Y1)
    st.wall((0, Y0), (0, 0.5))
    for i, yc in enumerate((3.0, 8.0, 13.0)):                       # west wall (screen left): three closed doors
        # the door goes in before its wall: door() asks ground() for the floor height at the hinge, and once the wall is there
        # the ray lands on top of the wall (2.8 m) unless the hinge is exactly on the edge of the opening
        st.door(f"门{i + 1}", hinge=(0, yc - 0.425), heading=0)
        st.wall((0, yc - 2.5), (0, yc + 2.5), door=(2.5, 0.9, 2.0))
    st.wall((0, 15.5), (0, Y1))
    st.wall((W, Y0), (W, Y1))                                        # east wall (screen right): a row of windows
    for i, yc in enumerate((-1.0, 3.0, 7.0, 11.0, 15.0)):
        st.box(f"窗{i + 1}", (1.6, 0.05, 1.3), (W - 0.085, yc, 0.95), heading=90, color=(0.55, 0.75, 0.95), ground=False)
    st.wall((0, Y1), (W, Y1))
    st.box("尽头的门", (1.3, 0.05, 2.05), (W / 2, Y1 - 0.085, 0), color="door", ground=False)
    st.box("天花板", (W + 0.2, Y1 - Y0, 0.1), (W / 2, (Y0 + Y1) / 2, 2.8), color="white", ground=False)

    v = 1.3 * k
    ya, yb, d = 4.5 + 5 * v, 4.5, 3.8                                # round 1: 6.5 m in 5 s = 1.3 m/s
    a, x = cast(st, fig, (0.72, ya), 180, (1.48, ya), 180)
    # round 1: 小周 takes shorter, quicker steps (0.46 s against 0.5 s) and glances at 阿杰 (on his right) around 2.3–3.2 s
    sa, sx, tx = (0.5 / k, 0.46 / k, -0.3 / k) if cad is None else (1 / cad, 1 / cad, -0.6 / cad)
    swing = 1.0 if cad is None else (v / cad) / 0.65                 # walk_a / walk_b as they are fit a 0.65 m step
    walk_const(a, -sa, 5.6, (0.72, ya), (0.72, yb), (0, 5), stride=sa, phase=0, swing=swing)
    walk_const(x, tx, 5.6, (1.48, ya), (1.48, yb), (0, 5), stride=sx, phase=1, swing=swing,
               heads=lambda t: -42 if 2.2 / k <= t <= 3.2 / k else 0)
    st.camera(CAM["s1"], (W / 2, ya - d, 1.35), (W / 2, ya, 1.0), lens=28)
    st.camera_key(CAM["s1"], 5.0, (W / 2, yb - d, 1.35), (W / 2, yb, 1.0))     # backs away at the walkers' speed
    st.camera_key(CAM["s1"], 6.0, (W / 2, yb - d - v, 1.35), (W / 2, yb - v, 1.0))
    st.steps = {"阿杰": {"t0": -sa, "stride": sa}, "小周": {"t0": tx, "stride": sx}}   # pose keys at t0 + i * stride
    return linear(st)


# ---------------------------------------------------------------- s2: car park, side view, punch -> duck -> counter
def s2(fig="j", people=True):
    st = Stage(fps=FPS)
    st.floor(-9, -7, 9, 4)
    st.wall((-9, 4), (9, 4), height=3.0)
    st.box("柱子左", (0.6, 0.6, 3.0), (-3.1, 3.1, 0), color=(0.62, 0.62, 0.62), ground=False)
    st.box("柱子右", (0.6, 0.6, 3.0), (2.5, 3.1, 0), color=(0.62, 0.62, 0.62), ground=False)
    st.box("车身", (4.4, 1.8, 0.8), (5.4, 2.9, 0), color=(0.55, 0.57, 0.62), ground=False)            # a car parked along the back wall, right of the pillar
    st.box("车顶", (2.3, 1.6, 0.5), (5.5, 2.9, 0.8), color=(0.30, 0.33, 0.38), ground=False)
    st.box("天花板", (18, 11, 0.1), (0, -1.5, 3.0), color="white", ground=False)

    st.camera(CAM["s2"], (-0.4, -5.0, 1.35), (-0.4, 0, 1.05), lens=35)
    if not people:
        return st
    a, x = cast(st, fig, (-0.80, 0), 90, (0.80, 0), 270, "guard", "guard")
    keys(a, 90, [(0.0, (-0.80, 0), "guard"), (0.4, (-0.78, 0), "guard2"), (0.8, (-0.80, 0), "guard"),
                 (1.15, (-0.30, 0), "punch_r"), (1.45, (-0.30, 0), "punch_r"), (1.75, (-0.32, 0), "guard"),
                 (2.05, (-0.42, 0), "hurt"), (2.5, (-0.85, 0), "hurt2"), (3.0, (-1.30, 0), "hurt"), (3.4, (-1.55, 0), "hurt2"),
                 (4.2, (-1.60, 0), "guard"), (5.0, (-1.60, 0), "guard2"), (5.4, (-1.60, 0), "guard")])
    keys(x, 270, [(0.0, (0.80, 0), "guard"), (0.4, (0.82, 0), "guard2"), (0.9, (0.80, 0), "guard"),
                  (1.2, (0.72, 0), "duck"), (1.5, (0.45, 0), "duck"), (1.9, (0.28, 0), "body_punch"), (2.15, (0.28, 0), "body_punch"),
                  (2.5, (0.25, 0), "guard"), (3.0, (0.05, 0), "guard2"), (3.6, (-0.35, 0), "guard"), (4.3, (-0.40, 0), "guard2"),
                  (5.0, (-0.40, 0), "guard"), (5.4, (-0.40, 0), "guard2")])
    return linear(st)


def s2e(fig="j", tp=1.3):
    """Round 2: the beat of s2 keyed faster and with wind-ups. 阿杰's straight right is fully out at tp (0.15 s from the loaded
    guard), 小周 is down under it 0.05 s earlier, his body punch lands at tp + 0.55 (0.15 s), 阿杰 folds 0.15 s after that."""
    st = s2(fig, people=False)
    a, x = cast(st, fig, (-0.80, 0), 90, (0.80, 0), 270, "guard", "guard")
    tc = tp + 0.55
    bob = lambda who, x0, t1: [(round(t, 2), (x0 + (0.02 if i % 2 else 0) * (1 if who == "a" else -1), 0), "guard2" if i % 2 else "guard")
                               for i, t in enumerate(t / 100 for t in range(0, int(t1 * 100), 40))]
    keys(a, 90, bob("a", -0.80, tp - 0.45) + [
        (tp - 0.35, (-0.80, 0), "guard", {"twist": -16, "lean": 4}),                  # loads the right hand
        (tp - 0.15, (-0.50, 0), "guard2", {"twist": -20, "lean": 10}),                # steps in, still loaded
        (tp, (-0.30, 0), "punch_r"), (tp + 0.08, (-0.29, 0), "punch_r"),              # out in 0.15 s, held for two frames
        (tp + 0.28, (-0.33, 0), "guard"), (tc - 0.05, (-0.34, 0), "guard2"),
        (tc + 0.15, (-0.45, 0), "hurt_b"), (tc + 0.6, (-0.90, 0), "hurt_b2"), (tc + 1.05, (-1.30, 0), "hurt_b"), (tc + 1.5, (-1.55, 0), "hurt_b2"),
        (tc + 2.3, (-1.60, 0), "guard"), (tc + 2.9, (-1.60, 0), "guard2"), (tc + 3.5, (-1.60, 0), "guard")])
    keys(x, 270, bob("x", 0.80, tp - 0.3) + [
        (tp - 0.25, (0.80, 0), "guard"), (tp - 0.05, (0.70, 0), "duck"), (tp + 0.15, (0.50, 0), "duck"),      # under the punch in 0.2 s
        (tc - 0.15, (0.36, 0), "guard2", {"twist": -22, "lean": 22}),                                        # rises inside, loads
        (tc, (0.28, 0), "body_punch"), (tc + 0.1, (0.28, 0), "body_punch"), (tc + 0.35, (0.26, 0), "guard"),
        (tc + 0.85, (0.05, 0), "guard2"), (tc + 1.45, (-0.35, 0), "guard"), (tc + 2.15, (-0.40, 0), "guard2"),
        (tc + 2.9, (-0.40, 0), "guard"), (tc + 3.5, (-0.40, 0), "guard2")])
    return linear(st)


# ---------------------------------------------------------------- s3: room, enter by the door, cross, sit opposite; camera pans
def s3(fig="j", fixed=False, good=False):
    """fixed=True is the second version of the set, built after the first round of clips: there the flat pale-blue window panel
    came back as a pale-blue board on the wall and the solid box chairs as solid block seats. Now the window is a real hole
    with a frame, and the chairs stand on four legs."""
    st = Stage(fps=FPS)
    st.floor(0, -2.5, 6.2, 4.2)
    d = st.door("门", hinge=(0.775, 4.2), heading=90)                 # before the wall (see s1)
    d.set(0.0, -86)                                                   # open, swung into the room, leaf against the west side
    st.wall((0, -2.5), (0, 4.2), name="西墙")
    st.wall((6.2, -2.5), (6.2, 4.2), name="东墙")
    chair = (0.35, 0.24, 0.15)
    wx = 2.95 if good else 3.15              # round 2: the west chair stands 0.2 m further from the table, so there is room in front of the seat
    if not fixed:
        st.floor(-0.5, 4.2, 6.2, 6.0, name="走廊地面")
        st.wall((0, 4.2), (6.2, 4.2), door=(1.2, 0.9, 2.0))           # north wall, door near its west end
        st.wall((-0.5, 6.0), (6.2, 6.0), name="走廊墙")                # what you see through the open door
        st.box("窗", (1.7, 0.05, 1.25), (4.2, 4.2 - 0.085, 0.95), color=(0.55, 0.75, 0.95), ground=False)
        for n, cx, back in (("椅子西", 3.15, -1), ("椅子东", 4.65, 1)):   # two chairs facing each other across the table
            st.box(n, (0.42, 0.42, 0.45), (cx, 1.9, 0), color=chair, ground=False)
            st.box(n + "靠背", (0.42, 0.05, 0.45), (cx + back * 0.21, 1.9, 0.45), heading=90, color=chair, ground=False)
    else:
        st.floor(-0.5, 4.2, 2.9, 6.0, name="走廊地面")                  # the corridor ends before the window: outside it is open air
        st.wall((-0.5, 6.0), (2.9, 6.0), name="走廊墙")
        st.wall((2.9, 4.2), (2.9, 6.0), name="走廊尽头")
        st.wall((0, 4.2), (3.35, 4.2), door=(1.2, 0.9, 2.0))          # north wall in pieces, leaving a window hole 3.35-5.05 m, 0.95-2.2 m high
        st.box("窗台墙", (1.7, 0.12, 0.95), (4.2, 4.2, 0), color="wall", ground=False)
        st.box("窗上墙", (1.7, 0.12, 0.6), (4.2, 4.2, 2.2), color="wall", ground=False)
        st.wall((5.05, 4.2), (6.2, 4.2))
        frame = (0.93, 0.93, 0.9)
        for n, size, at in (("窗框下", (1.7, 0.16, 0.05), (4.2, 4.2, 0.95)), ("窗框上", (1.7, 0.16, 0.05), (4.2, 4.2, 2.15)),
                            ("窗框左", (0.05, 0.16, 1.25), (3.375, 4.2, 0.95)), ("窗框右", (0.05, 0.16, 1.25), (5.025, 4.2, 0.95)),
                            ("窗棂", (0.04, 0.1, 1.25), (4.2, 4.2, 0.95))):
            st.box(n, size, at, color=frame, ground=False)
        for n, cx, back in (("椅子西", wx, -1), ("椅子东", 4.65, 1)):   # seat on four legs + a back
            st.table(n, (cx, 1.9, 0), size=(0.42, 0.42, 0.45), color=chair)
            st.box(n + "靠背", (0.42, 0.04, 0.42), (cx + back * 0.19, 1.9, 0.47), heading=90, color=chair, ground=False)
    st.table("桌子", (3.9, 1.9, 0), size=(0.8, 0.8, 0.74), color=(0.55, 0.38, 0.22))

    a, x = cast(st, fig, (1.2, 4.4), 180, (4.65, 1.9), 270, "walk_a", "sit")
    walk_const(a, 0.0, 0.9, (1.2, 4.4), (1.2, 3.45), (0, 0.9), stride=0.45, phase=0)
    if not good:
        # 阿杰: in the doorway at 0 s, two steps in, across the room to the side of the empty chair, steps in front of it, sits
        # (round 1: the last leg ends ON the chair, the mannequin and the seat overlap)
        walk_const(a, 0.9, 3.0, (1.2, 3.45), (3.22, 2.45), (0.9, 3.0), stride=0.5, phase=0)
        keys(a, None, [(3.35, (3.2, 2.2), "walk_b"), (3.75, (3.15, 1.9), "stand")])
        a.place(3.75, (3.15, 1.9), 90, "stand")
        a.place(4.6, (3.15, 1.9), 90, "sit")
        a.place(5.3, (3.15, 1.9), 90, "sit", lean=12, elbow_l=75, elbow_r=75)
        a.place(6.2, (3.15, 1.9), 90, "sit", lean=10, elbow_l=70, elbow_r=75)
    else:
        # round 2: across the room to a point beside the gap between seat and table, one step into the gap while turning to the
        # table, a short stop, then hips back and down with the trunk forward, seated at 4.6 s, forearms on the table
        walk_const(a, 0.9, 2.9, (1.2, 3.45), (3.34, 2.5), (0.9, 2.9), stride=0.5, phase=0)
        a.place(3.3, (3.30, 1.92), 135, "walk_b", hip_r=16, hip_l=-10)
        a.place(3.6, (3.30, 1.9), 90, "stand")
        a.place(3.85, (3.30, 1.9), 90, "stand", lean=6, knee_l=8, knee_r=8, hip_l=6, hip_r=6)
        a.place(4.2, (3.14, 1.9), 90, "sit_mid")
        a.place(4.6, (wx + 0.04, 1.9), 90, "sit", lean=16)
        a.place(4.95, (wx + 0.04, 1.9), 90, "sit", lean=2)
        a.place(5.5, (wx + 0.04, 1.9), 90, "sit", lean=14, elbow_l=75, elbow_r=75, shoulder_l=42, shoulder_r=42)
        a.place(6.2, (wx + 0.04, 1.9), 90, "sit", lean=12, elbow_l=70, elbow_r=75, shoulder_l=42, shoulder_r=42)
    # 小周: seated the whole time, watches 阿杰 come in (the door is to his right front), then faces him
    keys(x, 270, [(0.0, (4.65, 1.9), "sit", {"head_turn": -36}), (1.0, (4.65, 1.9), "sit", {"head_turn": -34}),
                  (3.0, (4.65, 1.9), "sit", {"head_turn": -14}), (3.8, (4.65, 1.9), "sit", {"head_turn": 0}),
                  (5.0, (4.65, 1.9), "sit", {"head_turn": 0, "lean": 8}), (6.2, (4.65, 1.9), "sit", {"head_turn": 0, "lean": 8})])
    cam = (2.7, -2.1, 1.4)
    st.camera(CAM["s3"], cam, (1.2, 4.3, 1.1), lens=40)
    st.camera_key(CAM["s3"], 0.35, cam, (1.2, 4.2, 1.1))
    st.camera_move(CAM["s3"], 0.35, 3.9, cam, (3.75, 1.9, 1.05))      # pans right with him, ends on the two at the table
    st.camera_key(CAM["s3"], 6.2, cam, (3.75, 1.9, 1.05))
    return linear(st)


BUILD = {"s1": s1, "s2": s2, "s3": s3, "s3b": lambda fig="j": s3(fig, fixed=True)}
ROUND2 = {"s1c14": lambda fig="j": s1(fig, cad=1.4), "s1c17": lambda fig="j": s1(fig, cad=1.7), "s1c24": lambda fig="j": s1(fig, cad=2.4),
          "s1x125": lambda fig="j": s1(fig, k=1.25), "s1x080": lambda fig="j": s1(fig, k=0.8),
          "s2e13": lambda fig="j": s2e(fig, 1.3), "s2e23": lambda fig="j": s2e(fig, 2.3),
          "s3e": lambda fig="j": s3(fig, fixed=True, good=True)}
ALL = {**BUILD, **ROUND2}
DUR.update({v: DUR[v[:2]] for v in ROUND2})
CAM.update({v: CAM[v[:2]] for v in ROUND2})


def round2(names):
    """Ground truth (where each person is every 0.1 s, when the walk poses are keyed) and the first still of the round-2 variants."""
    for v in names or ROUND2:
        st = ROUND2[v]("j")
        (WM / f"gt_{v}.json").write_text(json.dumps(track(st, v), ensure_ascii=False))
        if hasattr(st, "steps"):
            (WM / f"steps_{v}.json").write_text(json.dumps(st.steps, ensure_ascii=False))
        st.still(CAM[v], WM / f"{v}_j_a.png", 0.0)
        print("round2", v, flush=True)


def track(st, shot):
    """Where each person is in the frame every 0.1 s (x of the chest, top of head, feet; 0–1 from left / top)."""
    out, t = [], 0.0
    while t < DUR[shot] - 1e-6:
        r = st.report(CAM[shot], t)
        out.append({"t": round(t, 2), **{p["name"]: {k: p[k] for k in ("x", "head_y", "feet_y", "shot", "facing", "distance_m")} for p in r["people"]}})
        t += 0.1
    return out


def stills():
    notes = {}
    for shot, build in BUILD.items():
        for fig in ("j", "c", "jg"):
            st = build(fig)
            end = DUR[shot] - 2 / FPS
            st.still(CAM[shot], WM / f"{shot}_{fig}_a.png", 0.0)
            st.still(CAM[shot], WM / f"{shot}_{fig}_b.png", end)
            if fig == "j":
                st.plan(WM / f"plan_{shot}_a.png", t=0.0, title=shot)
                st.plan(WM / f"plan_{shot}_b.png", t=end, title=shot)
                notes[shot] = {"start": st.describe(CAM[shot], 0.0), "mid": st.describe(CAM[shot], DUR[shot] / 2), "end": st.describe(CAM[shot], end),
                               "order_start": st.order(CAM[shot], 0.0), "order_end": st.order(CAM[shot], end)}
                (WM / f"gt_{shot}.json").write_text(json.dumps(track(st, shot), ensure_ascii=False))
                print(shot, "\n" + notes[shot]["start"], "\n--\n" + notes[shot]["mid"], "\n--\n" + notes[shot]["end"], flush=True)
    (WM / "notes.json").write_text(json.dumps(notes, ensure_ascii=False, indent=1))


def previz(pairs):
    for pair in pairs:
        shot, fig = pair.split(":")
        st = ALL[shot](fig)
        out = WM / f"pv_{shot}_{fig}.mp4"
        st.clip(CAM[shot], out, 0.0, DUR[shot])
        shutil.rmtree(out.with_suffix(""), ignore_errors=True)       # the frame folder
        print("previz", out, flush=True)


def strip(pairs, step=0.4):
    from PIL import Image
    for pair in pairs:
        shot, fig = pair.split(":")
        st = ALL[shot](fig)
        frames, t = [], 0.0
        while t < DUR[shot] - 1e-6:
            f = WM / f"_tmp_{shot}_{fig}_{len(frames)}.png"
            st.still(CAM[shot], f, t)
            frames.append(Image.open(f).convert("RGB").resize((480, 270)))
            f.unlink()
            t += step
        cols = 4
        img = Image.new("RGB", (480 * cols, 270 * ((len(frames) + cols - 1) // cols)))
        for i, im in enumerate(frames):
            img.paste(im, ((i % cols) * 480, (i // cols) * 270))
        img.save(WM / f"strip_{shot}_{fig}.jpg", quality=88)
        print("strip", WM / f"strip_{shot}_{fig}.jpg", flush=True)


if __name__ == "__main__":
    WM.mkdir(exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if what == "stills":
        stills()
    elif what == "previz":
        previz(sys.argv[2:])
    elif what == "strip":
        strip(sys.argv[2:])
    elif what == "round2":
        round2(sys.argv[2:])

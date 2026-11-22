"""blocking.py runs inside Blender's Python module: these run a small scene with the bpy venv when it is on this machine."""
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

PY = os.environ.get("BLENDER_PY", str(Path(__file__).resolve().parents[1] / ".venv/bin/python"))
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
pytestmark = pytest.mark.skipif(not Path(PY).exists(), reason="needs a Python with bpy (set BLENDER_PY)")


def run(body):
    code = f"import sys; sys.path.insert(0, {str(SCRIPTS)!r})\nfrom blocking import *\n" + textwrap.dedent(body)
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


def test_wall_spans():
    out = run("""
        print(wall_spans(4, 2.8, [(1.0, 0.9, 0, 2.0), (3.0, 1.0, 0.9, 2.1)]))
        try:
            wall_spans(4, 2.8, [(1.0, 0.9, 0, 2.0), (1.5, 0.9, 0, 2.0)])
        except ValueError:
            print("overlap refused")
    """)
    spans = eval(out.splitlines()[0])
    assert [s[0] for s in spans] == ["full", "top", "full", "sill", "top", "full"]
    assert abs(spans[-1][2] - 3.5) < 1e-9 and "overlap refused" in out


def test_wall_openings_above_each_other():
    out = run("""
        r = lambda spans: [(k, i, *(round(v, 2) for v in rest)) for k, i, *rest in spans]
        print(r(wall_spans(2.4, 9.0, [(1.2, 0.8, 1.9, 2.8), (1.2, 0.8, 4.7, 5.6), (1.2, 0.8, 7.5, 8.4)])))   # a window on every storey
        print(r(wall_spans(2.4, 6.0, [(1.2, 1.2, 0.0, 2.1), (1.2, 0.6, 3.5, 4.2)])))                        # a door, a narrower window over it
        try:
            wall_spans(2.4, 6.0, [(1.2, 1.2, 0.0, 2.1), (1.2, 0.6, 2.0, 2.7)])
        except ValueError as e:
            print("refused:", e)
        st = Stage(fps=30)
        st.wall((0, 0), (2.4, 0), height=6.0, door=(1.2, 1.2, 2.1), windows=[(1.2, 0.6, 0.7, 3.5)], name="w")
        print(sorted(o.name for o in bpy.data.objects if o.name.startswith("w_") and "_win" not in o.name))
    """).splitlines()
    assert eval(out[0]) == [("full", 0, 0.0, 0.8, 0.0, 9.0), ("sill", 0, 0.8, 1.6, 0.0, 1.9), ("top", 0, 0.8, 1.6, 2.8, 4.7),
                            ("top", 1, 0.8, 1.6, 5.6, 7.5), ("top", 2, 0.8, 1.6, 8.4, 9.0), ("full", 1, 1.6, 2.4, 0.0, 9.0)]
    assert eval(out[1]) == [("full", 0, 0.0, 0.6, 0.0, 6.0), ("top", 1, 0.6, 0.9, 2.1, 6.0), ("top", 1, 0.9, 1.5, 2.1, 3.5),
                            ("top", 0, 0.9, 1.5, 4.2, 6.0), ("top", 1, 1.5, 1.8, 2.1, 6.0), ("full", 1, 1.8, 2.4, 0.0, 6.0)]
    assert out[2] == "refused: openings 1 and 0 overlap"
    assert eval(out[3]) == ["w_s0", "w_s1", "w_top0", "w_top1", "w_top1_2", "w_top1_3"]     # one name each: hide=["w_top1"] covers all three


def test_ground_doors_boxes_and_linear_keys():
    out = run("""
        st = Stage(fps=30)
        st.floor(0, 0, 4, 5); st.floor(0, 5, 4, 8, name="room")
        st.wall((0, 5), (4, 5), doors=[(1.0, 0.9, 2.0), (3.0, 0.9, 2.0)])
        d = st.door("门", hinge=(0.55, 5), heading=90, into=(1, 6), into_name="屋里")
        st.box("柜子", (0.8, 0.4, 1.8), (3.5, 4.7)); st.table("桌", (2, 1.5)); st.stool("凳", (1, 1)); st.sofa("沙发", (2, 3), heading=180)
        st.chair("椅", (3.2, 1.5), heading=270)
        a = st.person("阿杰", "blue", at=(1, 2), facing=0, marks=("hair_long",))
        a.walk(0.0, 2.0, (1.0, 6.0), ease=False)
        b = st.person("小周", "red", at=(3, 2.5), facing=0)
        b.place(0.5, (3, 2.5), pose="sit", seat=0.40); b.place(1.0, (3, 2.5), pose="sit")
        d.open(0.0, 0); d.open(2.0, 80)
        st.camera("c", (2, -1, 1.5), (2, 5, 1.0)); st.camera_key("c", 2.0, (2, 1, 1.5), (2, 5, 1.0))
        st.at_time(1.0)
        print(round(st.ground(1.0, 5.0), 3), round(d.root.location.z, 3))
        print(round(st.cams["c"]["obj"].location.y, 3), round(a.root.location.y, 3))
        print(round(b.pelvis.location.z * b.root.scale.z - 0.085 * b.root.scale.z, 3))
        print(round(d.angle(), 1), d.sign)
        print(st.describe("c", 1.0))
    """).splitlines()
    assert out[0] == "0.0 0.0"                      # the doorway is floor, not the top of the wall; the door stands on the floor
    assert out[1] == "0.0 4.0"                      # camera and walk move at constant speed
    assert out[2] == "0.4"                          # the seat height stays when the next key does not repeat it
    assert out[3] == "40.0 1"                       # opening into the room is a positive swing for this door
    assert any("门扇往离镜头远的那边开（往屋里开），现在开着约 40 度" in l for l in out)


def test_door_height_can_be_given_with_the_hinge():
    out = run("""
        st = Stage(fps=30)
        st.floor(0, 0, 4, 5)
        up = st.door("楼上门", hinge=(1.0, 2.0, 2.9), heading=90, into=(1.5, 3))      # its floor is built after it
        st.floor(0, 0, 4, 5, z=2.9, name="upper")
        down = st.door("楼下门", hinge=(3.0, 2.0, 0.0), heading=90, into=(3.5, 3))    # two floors above each other: say which
        auto = st.door("自动", hinge=(2.0, 2.0), heading=90, into=(2.5, 3))
        st.at_time(0.0)
        print(round(up.root.location.z, 3), round(down.root.location.z, 3), round(auto.root.location.z, 3))
        jamb = next(i for i in st.items if i["name"] == "楼上门_jamb_a")
        print(round(jamb["at"][2], 3), round(up.hinge[2], 3))
    """).splitlines()
    assert out[0] == "2.9 0.0 2.9"                  # two numbers: the highest floor built so far under the hinge
    assert out[1] == "2.9 2.9"                      # the frame and the leaf stand at the same height


def test_looked_up_door_height_is_checked_before_output():
    out = run("""
        def attempt(build):
            st = Stage(fps=30)
            build(st)
            st.camera("c", (2, -2, 1.6), (2, 3, 1.0))
            try:
                st.describe("c", 0.0)
                print("ok", round(st.doors[0].root.location.z, 2))
            except ValueError as e:
                print("refused:", e)
        attempt(lambda st: (st.door("门", hinge=(1.0, 5.0), heading=90), st.floor(0, 0, 4, 5, z=2.9), st.floor(0, 5, 4, 8, z=2.9)))
        attempt(lambda st: (st.floor(0, 0, 4, 5.05, z=2.9), st.floor(0, 5, 4, 8, z=2.9), st.door("门", hinge=(1.0, 5.0), heading=90)))
        attempt(lambda st: (st.floor(0, 0, 4, 8), st.floor(0, 0, 4, 8, z=2.9, name="upper"), st.door("门", hinge=(1.0, 5.0), heading=90)))
        attempt(lambda st: (st.floor(0, 0, 4, 8), st.floor(0, 0, 4, 8, z=2.9, name="upper"), st.door("门", hinge=(1.0, 5.0, 0.0), heading=90)))
        attempt(lambda st: (st.floor(0, 0, 4, 5), st.floor(0, 5, 4, 8, z=0.3, name="raised"), st.door("门", hinge=(1.0, 5.0), heading=90)))
        attempt(lambda st: (st.floor(0, 0, 4, 4.9), st.box("sill", (1.2, 0.6, 0.1), (1.425, 4.5)), st.door("门", hinge=(1.0, 5.0), heading=90)))
        attempt(lambda st: (st.floor(0, 0, 4, 5, z=2.9), st.floor(0, 5, 4, 8, z=2.9), st.door("门", hinge=(1.0, 5.0), heading=90)))
    """).splitlines()
    assert out[0] == ("refused: door 门 stands at 0.00 m, the height found under its hinge when it was built, but the floor beside the "
                      "doorway is at 2.9 m: the floor was built after the door, or the hinge sits on the very edge of the floor where the "
                      "look-up misses it. Give the height: hinge=(1, 5, 2.9)")                     # floors built after it
    assert out[1] == "ok 2.9"                                                                       # floors first
    assert out[2] == ("refused: door 门: floors at 0, 2.9 m lie above each other at the doorway, so the height looked up under the "
                      "hinge (2.90 m) is a guess. Give the height of the floor this door stands on: hinge=(1, 5, z)")   # which storey?
    assert out[3] == "ok 0.0"                                                                       # z given: not looked up
    assert out[4].startswith("ok")                                                                  # a step up at the doorway is fine
    assert out[5] == "ok 0.0"                                      # a sill plate in front of the door: the floor beside it still counts
    assert out[6] == "ok 2.9" or out[6].endswith("hinge=(1, 5, 2.9)")      # hinge on the seam of two floors: found, or said (bpy 5.3 misses it)


def test_sees_hide_and_hidden_people():
    out = run("""
        st = Stage(fps=30)
        st.floor(0, 0, 4, 5)
        st.ceiling(0, 0, 4, 5, light=False)
        st.box("墙", (3, 0.2, 2.5), (2, 2.5), ground=False)
        a = st.person("甲", "blue", at=(1, 1), facing=0)
        b = st.person("乙", "red", at=(2, 4), facing=180)
        st.camera("前", (2, -1, 1.5), (2, 5, 1.2))
        st.camera("顶", (2, 2.5, 6), (2, 2.5, 0), hide=["ceiling"], roll=90)
        print(st.sees("甲", "乙"))
        print(st.sees("顶", "乙"), st.sees((2, 2.5, 6), "乙"))
        print(st.gap("甲", "乙", 0))
        print(st.order("前", 0))
        print(st.describe("前", 0))
    """).splitlines()
    assert out[0] == "['墙']"
    assert out[1] == "[] ['ceiling']"
    assert out[2] == "3.16"
    assert out[3] == "['甲']"                       # 乙 is wholly behind the wall: not in the left-to-right order
    assert any("乙在墙后面，画面里看不见" in l for l in out)


def test_camera_inside_a_solid_and_open_stairs():
    out = run("""
        for solid in (True, False):
            st = Stage(fps=30)
            st.floor(0, 0, 4, 8)
            st.stairs("梯", (2.0, 1.0, 1.4), 0, 9, solid=solid)            # a flight going up from a landing 1.4 m high
            st.box("柜", (0.8, 0.5, 1.8), (0.6, 6.0), ground=False)
            st.camera("c", (2.0, 2.6, 1.9), (2.0, 6.0, 1.9))               # where step 5 is, 0.5 m above the landing
            st.camera("d", (0.6, 6.0, 1.2), (3.0, 6.0, 1.2))               # in the cabinet
            ob = bpy.data.objects["梯_5"]
            print(solid, round(min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box), 3),
                  [l for l in st.describe("c", 0).splitlines() if "里面" in l])
        print([l for l in st.describe("d", 0).splitlines() if "里面" in l])
    """).splitlines()
    assert out[0] == "True 1.4 ['【要改】镜头在梯_5里面，画面里只有它的内壁：把机位挪出来（楼梯默认是实心的，要把机位放到一段楼梯底下，那段写 stairs(…, solid=False)）']"
    assert out[1] == "False 2.075 []"                # open underneath: step 5 is 0.15 m thick below its tread line, the camera is under it
    assert out[2] == "['【要改】镜头在柜里面，画面里只有它的内壁：把机位挪出来']"


def test_previz_renders_what_is_asked_for(tmp_path):
    out = run(f"""
        import subprocess
        from pathlib import Path
        st = Stage(fps=30)
        st.floor(0, 0, 4, 5)
        st.camera("c", (2, -1, 1.5), (2, 5, 1.0))
        done = []
        def fake(cam, path, t0, t1, samples=None, scale=1.0):         # stands in for the render: a short grey clip
            done.append((Path(path).stem, samples, scale))
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=64x36:r=30:d=0.2", "-pix_fmt", "yuv420p", str(path)], check=True)
        st.clip = fake
        shots = [(n, "c", 0.0, 0.2) for n in ("s1", "s2", "s3", "s4", "s5")]
        out = Path({str(tmp_path)!r}) / "previz.mp4"
        for kw in (dict(part=(0, 2), samples=4, scale=0.5), dict(part=(1, 2), samples=4, scale=0.5), dict(missing=True), dict(only=["s2"]), "rm s4",
                   dict(only=["s2"]), dict()):
            if kw == "rm s4":
                (out.parent / "pv_s4.mp4").unlink()
                continue
            r = st.previz(shots, out, **kw)
            print(r and r.name, done)
            done.clear()
    """).splitlines()
    assert out[0] == "None [('pv_s1', 4, 0.5), ('pv_s3', 4, 0.5), ('pv_s5', 4, 0.5)]"     # process 0 of 2: shots 1, 3, 5, not joined
    assert out[1] == "None [('pv_s2', 4, 0.5), ('pv_s4', 4, 0.5)]"
    assert out[2] == "previz.mp4 []"                                                      # all there: only joined
    assert out[3] == "previz.mp4 [('pv_s2', None, 1.0)]"
    assert out[4] == "previz.mp4 [('pv_s2', None, 1.0), ('pv_s4', None, 1.0)]"            # only= also fills in what is missing
    assert out[5] == "previz.mp4 " + str([(f"pv_s{i}", None, 1.0) for i in range(1, 6)])  # by default every shot again
    assert (tmp_path / "previz.mp4").exists()


def test_plan_draws_the_cameras_asked_for(tmp_path):
    out = run(f"""
        from pathlib import Path
        from PIL import Image
        st = Stage(fps=30)
        st.floor(0, 0, 4, 5)
        st.camera("A", (1, 1, 1.5), (1, 4, 1.0)); st.camera("B", (3, 1, 1.5), (3, 4, 1.0))
        for cams, name in ((None, "all.png"), (["A"], "one.png")):
            p = Path({str(tmp_path)!r}) / name
            st.plan(p, cams=cams, region=(0, 0, 4, 5), scale=50)
            im = Image.open(p).convert("RGB")
            print(im.getpixel((50, 200)), im.getpixel((150, 200)))
    """).splitlines()
    assert out[0] == "(200, 60, 0) (200, 60, 0)"                    # the camera squares of A and B
    assert out[1].startswith("(200, 60, 0) ") and not out[1].endswith("(200, 60, 0)")


def test_feet_and_hands_reach_their_points():
    out = run("""
        from mathutils import Vector
        st = Stage(fps=30)
        st.floor(0, 0, 4, 5)
        g = st.person("小满", "red", at=(2, 2), facing=0, height=1.58)
        target = Vector((1.55, 2.55, 0.05))
        g.place(1.0, (2, 2), 0, "sit", seat=0.42, lean=-12, feet={"l": target}, hands={"r": (2.3, 2.4, 0.74)})
        st.at_time(1.0)
        foot = g.j["knee_l"].matrix_world @ Vector((0, 0.07, -0.455))
        print(round((foot - target).length, 3), round((g.point("hand_r") - Vector((2.3, 2.4, 0.74))).length, 3))
    """).split()
    assert float(out[0]) < 0.08 and float(out[1]) < 0.05


def test_walk_rhythm_strike_sit_and_beats():
    out = run("""
        print(walk_keys(4.0, 5.2))                      # 1.3 m/s: 1.625 steps a second, 0.8 m a step
        print(walk_keys(4.0, 2.0)[1:], walk_keys(4.0, 9.6)[1:])      # slow and fast stay within 1.4–1.8
        print(walk_keys(2.0, 0.0)[1:])                  # on the spot
        print(walk_keys(2.7, 1.87, stride_s=0.5))       # the old way: 5 steps fill the walk, swing as drawn
        print(walk_keys(4.0, 5.2, cadence=1.45)[0])
        print(walk_swing("walk_a", 1.5))
        print(strike_keys(1.3))
        print(sit_keys(4.6, (2.95, 1.9), 90, 0.45))
        print(key_beats([(0.0, "stand"), (0.0, "walk_a"), (0.6, "walk_b"), (1.2, "walk_a"), (1.8, "stand"), (2.5, "stand"), (3.0, "sit")]))
    """).splitlines()
    ks, c, step, swing = eval(out[0])
    assert len(ks) == 7 and abs(c - 1.625) < 1e-9 and abs(step - 0.8) < 1e-9 and abs(swing - 0.8 / 0.65) < 1e-9
    assert abs(ks[1] * 4.0 - 1 / 1.625) < 1e-9 and 0.5 - 1e-6 <= (1 - ks[-1]) * 4.0 * c <= 1.5   # the end pose 0.5–1.5 steps after the last
    slow, fast = eval(out[1].split(") (")[0] + ")"), eval("(" + out[1].split(") (")[1])
    assert slow[0] == 1.4 and fast[0] == 1.8
    assert eval(out[2]) == (1.4, 0.0, 0.25)
    ks, c, step, swing = eval(out[3])
    assert ks == [0.0, 0.2, 0.4, 0.6, 0.8] and swing == 1.0
    assert len(eval(out[4])) == 6
    assert eval(out[5]) == {"hip_l": 42.0, "hip_r": -27.0, "shoulder_l": -33.0, "shoulder_r": 36.0}
    sk = eval(out[6])
    assert [round(k[0], 2) for k in sk] == [0.95, 1.15, 1.3, 1.38, 1.58] and sk[2][1:3] == (0.5, "punch_r")
    st = eval(out[7])
    assert [round(k[0], 2) for k in st] == [3.3, 3.6, 3.85, 4.2, 4.6, 4.95]
    assert [round(k[1][0], 2) for k in st] == [3.3, 3.3, 3.3, 3.14, 2.99, 2.99] and st[1][2] == 90 and st[4][3] == "sit"
    assert eval(out[8]) == ([0.3, 0.9], [(1.8, "stand"), (3.0, "sit")])


def test_walk_cadence_timeline_retime():
    out = run("""
        import json
        from mathutils import Vector
        st = Stage(fps=30)
        st.floor(-3, -2, 6, 8)
        a = st.person("甲", "blue", at=(0, 0), facing=0)
        b = st.person("乙", "red", at=(1.2, 0), facing=0)
        a.walk(0.0, 4.0, (0, 5.2), ease=False)
        b.walk(0.0, 4.0, (1.2, 4.8), ease=False, cadence=1.45)
        c = st.person("丙", "yellow", at=(3, 0), facing=0)
        c.walk(0.0, 2.0, (3, 2.6), stride_s=0.5)                 # the old way: 2 steps a second, flagged
        st.chair("椅", (4.5, 4.0), heading=270)
        d = st.person("丁", "purple", at=(5.0, 2.6), facing=0)
        d.walk(0.0, 1.0, (4.85, 3.4))
        d.sit_down(3.0, "椅")
        e = st.person("戊", "green", at=(-2, 3), facing=90, pose="guard", kind="capsule")
        e.strike(1.3)
        tl = st.timeline()
        print(json.dumps(tl, ensure_ascii=False))
        st.at_time(3.0)
        print(round(d.pelvis.matrix_world.translation.z, 2), round(d.root.location.x, 2))
        st.at_time(1.3)
        print(round(e.root.location.x, 2))
        st.at_time(2.0)
        y2 = a.root.location.y
        st.retime(2.0)
        st.at_time(1.0)
        print(round(a.root.location.y - y2, 4))
        print(json.dumps(st.timeline()["people"]["甲"], ensure_ascii=False))
    """).splitlines()
    import json
    tl = json.loads(out[0])
    p = tl["people"]
    assert len(p["甲"]["changeovers"]) == 6 and len(p["乙"]["changeovers"]) == 5
    assert abs(p["甲"]["changeovers"][1] - p["甲"]["changeovers"][0] - 1 / 1.625) < 0.04
    assert abs(p["乙"]["changeovers"][1] - p["乙"]["changeovers"][0] - 1 / 1.45) < 0.04
    assert p["甲"]["walks"][0]["cadence"] == 1.625 and p["乙"]["walks"][0]["step"] == round(1.2 / 1.45, 3)
    assert len(tl["warnings"]) == 1 and tl["warnings"][0].startswith("丙")
    assert [w for t, w in p["丁"]["events"]] == ["停在椅前", "坐定（椅）"] and ["3.0", "sit"] == [str(x) for x in p["丁"]["poses"][-1]]
    assert p["戊"]["events"] == [[1.3, "打直（punch_r）"]] and p["戊"]["changeovers"] == []
    z, x = map(float, out[1].split())
    assert 0.45 < z < 0.65 and abs(x - 4.46) < 0.01                  # seated on the 0.45 m seat, just in front of its centre
    assert abs(float(out[2]) - (-1.5)) < 0.01                        # the capsule stepped 0.5 m toward where it faces
    assert float(out[3]) == 0.0                                       # twice as fast: where it was at 2 s it now is at 1 s
    q = json.loads(out[4])
    assert abs(q["changeovers"][0] - p["甲"]["changeovers"][0] / 2) < 1e-6 and q["walks"][0]["cadence"] == 3.25


def test_stand_ins_turn_the_same_scene_into_capsules():
    out = run("""
        def scene(stand_ins):
            st = Stage(fps=30, stand_ins=stand_ins)
            st.floor(-3, -2, 6, 8)
            st.chair("椅", (4.5, 4.0), heading=270)
            a = st.person("甲", "blue", at=(0, 0), facing=0, marks=("glasses", "shorts"))
            a.walk(0.0, 4.0, (0, 5.2))
            a.place(5.0, (0, 5.2), pose="stand", hands={"r": (0.3, 5.6, 1.0)}, head_turn=30)
            b = st.person("乙", "red", at=(5.0, 2.6), facing=0)
            b.walk(0.0, 1.0, (4.85, 3.4)); b.sit_down(3.0, "椅"); b.strike(6.0)
            st.at_time(2.0); mid = a.root.location.y
            st.at_time(4.5)
            return type(a).__name__, type(b).__name__, round(a.root.location.y, 3), round(mid, 1), st.timeline()["people"]["甲"]["walks"][0]["speed"]
        print(scene(False)); print(scene(True))
    """).splitlines()
    j, c = eval(out[0]), eval(out[1])
    assert j[:2] == ("Person", "Person") and c[:2] == ("Capsule", "Capsule")       # the same script, everyone a stand-in
    assert j[2] == c[2] == 5.2 and abs(j[3] - c[3]) <= 0.3 and j[4] == c[4]        # same route, arrival and walking speed


def test_check_bodies_and_pose_sheet(tmp_path):
    sheet = tmp_path / "poses.png"
    out = run(f"""
        st = Stage(fps=24)
        st.floor(-5, -5, 5, 5)
        a = st.person("阿杰", "blue", (0, 0), facing=0)
        a.walk(0.0, 2.0, (0, 2.6))
        print("CLEAN", len(st.check_bodies()))
        b = st.person("小周", "red", (2, 0), facing=0)
        b.place(1.0, (2, 0), pose="stand", elbow_r=-30)        # elbow bent the wrong way
        b.place(2.0, (2, 0), pose="stand")
        m = st.person("大妈2", "green", (3, -1), facing=180, pose="sit", seat=0.45)   # sits with her back to a point 1 m behind
        m.place(1.5, (3, -1), pose="sit", hands={{"l": (3.0, 0.05, 1.0)}})
        st.box("crate", (0.6, 0.6, 1.6), (-2, 0), ground=False)
        st.person("大妈", "purple", (-2, 0), facing=0)           # inside the crate
        st.person("影子", "yellow", (0, 2.6), facing=0)          # where 阿杰's walk ends
        for line in st.check_bodies():
            print("L", line)
        print("TILES", len(st.pose_sheet({str(sheet)!r}, people=["小周"])))
    """)
    lines = [l[2:] for l in out.splitlines() if l.startswith("L ")]
    assert "CLEAN 0" in out
    assert any("小周" in l and "右肘弯" in l and "往反方向弯了" in l for l in lines)
    assert not any("离地" in l or "插进地里" in l for l in lines)
    assert any("大妈2 1.50 秒" in l and "左手够不着目标点" in l for l in lines)
    assert any("大妈2 1.50 秒" in l and "左手的目标点在背后" in l for l in lines)
    assert any("大妈2" in l and "左肩往前抬" in l for l in lines)
    assert any("大妈" in l and "穿进了crate" in l for l in lines)       # chest inside the crate
    assert any("阿杰和影子" in l and "叠在一起" in l for l in lines)
    assert not any(l.startswith("【要改】阿杰 ") for l in lines)
    assert "TILES 3" in out and sheet.exists()

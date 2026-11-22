"""White-model blocking for AI video: a set, mannequins, cameras -> stills, a previz, a floor plan and a layout report.

Runs with the Blender Python module (`pip install bpy`), headless. Units are metres and seconds.
Directions are compass degrees seen from above: 0 = +Y (north), 90 = +X (east), 180 = -Y, 270 = -X.
A person's `facing` may also be an (x, y) point or the name of another person / prop to face.
Keys are linear between two keyframes; walk() and camera_move() ease in and out by laying many keys.
walk() steps at a cadence that follows the speed; st.timeline() lists when each step, key pose, strike and sit-down falls.

    st = Stage(fps=30)
    st.floor(0, 0, 4, 5); st.wall((0, 5), (4, 5), doors=[(2.0, 0.9, 2.0)])
    d = st.door("door", hinge=(1.55, 5), heading=90, into=(2, 6), into_name="屋里")   # the leaf swings into the room
    a = st.person("阿杰", "blue", at=(1, 2), facing=0, marks=("glasses",))
    a.place(2.0, (1, 4.5), pose="stand", hands={"r": d.lock_point(side=-1)})   # at 2 s he stands at the door, right hand on the lock
    d.open(2.0, 0); d.open(3.0, 80)                                          # the door swings open between 2 s and 3 s
    st.camera("wide", (2, -1.5, 1.6), (2, 5, 1.0), lens=30)
    shots = [("s1", "wide", 0.0, 3.5)]
    st.stills(shots, "out")            # out/s1_a.png (first frame); st.describe("wide", 0) gives the layout as sentences
    st.previz(shots, "out/previz.mp4")
"""
from __future__ import annotations

import contextlib
import itertools
import math
import os
import shutil
import subprocess
from pathlib import Path

import bpy  # must come before bmesh / mathutils: they live inside the bpy module
import bmesh
from bpy_extras import anim_utils
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector

COLORS = {
    "floor": (0.42, 0.42, 0.42), "wall": (0.78, 0.78, 0.76), "step": (0.55, 0.55, 0.55), "door": (0.30, 0.20, 0.14),
    "frame": (0.22, 0.15, 0.10), "prop": (0.50, 0.50, 0.55), "skin": (0.85, 0.66, 0.52),
    "red": (0.80, 0.10, 0.10), "blue": (0.10, 0.25, 0.80), "green": (0.05, 0.30, 0.15), "yellow": (0.90, 0.70, 0.05),
    "purple": (0.45, 0.15, 0.60), "orange": (0.90, 0.40, 0.05), "white": (0.92, 0.92, 0.92), "black": (0.05, 0.05, 0.05),
    "maroon": (0.45, 0.08, 0.12), "grey": (0.5, 0.5, 0.5), "hair": (0.16, 0.09, 0.05),
}

# Joint angles in degrees. Positive = the natural flexion: lean forward, raise arm forward, bend elbow, lift thigh
# forward, bend knee, nod the head down. abduct = arm away from the body sideways. head_turn positive = to the person's left.
# twist positive = the upper body turns to the person's left. hipturn = the thigh swings about the vertical (positive = to the left).
# A pose may carry "seat" (height of what the person sits on, above the ground they stand on) and "low" (the height a capsule
# stand-in shrinks to, as a share of its standing height).
POSES = {
    "stand": {},
    "walk_a": {"hip_l": 28, "knee_l": 10, "hip_r": -18, "knee_r": 22, "shoulder_l": -22, "shoulder_r": 24, "elbow_l": 15, "elbow_r": 25, "lean": 4},
    "walk_b": {"hip_r": 28, "knee_r": 10, "hip_l": -18, "knee_l": 22, "shoulder_r": -22, "shoulder_l": 24, "elbow_r": 15, "elbow_l": 25, "lean": 4},
    "sit": {"hip_l": 88, "hip_r": 88, "knee_l": 88, "knee_r": 88, "shoulder_l": 25, "shoulder_r": 25, "elbow_l": 55, "elbow_r": 55, "seat": 0.45},
    "sit_floor": {"hip_l": 90, "hip_r": 90, "shoulder_l": 30, "shoulder_r": 30, "elbow_l": 70, "elbow_r": 70, "lean": -8, "seat": 0.0},
    "crouch": {"hip_l": 105, "hip_r": 105, "knee_l": 135, "knee_r": 135, "lean": 30, "shoulder_l": 40, "shoulder_r": 40, "elbow_l": 30, "elbow_r": 30},
    "carry": {"lean": 12, "shoulder_l": 30, "shoulder_r": 30, "elbow_l": 35, "elbow_r": 35, "hip_l": 12, "hip_r": 12, "knee_l": 22, "knee_r": 22},
    "lift_low": {"lean": 55, "shoulder_l": 75, "shoulder_r": 75, "elbow_l": 10, "elbow_r": 10, "hip_l": 35, "hip_r": 35, "knee_l": 65, "knee_r": 65, "head_nod": -20},
    "push": {"lean": 32, "shoulder_l": 95, "shoulder_r": 95, "elbow_l": 25, "elbow_r": 25, "hip_l": 40, "knee_l": 45, "hip_r": -22, "knee_r": 12},
    "hands_on_hips": {"abduct_l": 40, "abduct_r": 40, "elbow_l": 100, "elbow_r": 100, "shoulder_l": -15, "shoulder_r": -15},
    "high_five": {"shoulder_r": 150, "elbow_r": 20},
    "arms_out": {"abduct_l": 80, "abduct_r": 80},
    # A fight beat and a sit-down that a jointed previz carried into the film (examples/fidelity): a guard and its other half
    # (alternate them for a little bounce), a right straight, ducking under it, a right to the body, doubled over with the
    # forearms against the belly (alternate the two while backing off), half-way down to a chair. strike() and sit_down() use them.
    "guard": {"shoulder_l": 58, "shoulder_r": 48, "elbow_l": 118, "elbow_r": 125, "hip_l": 20, "knee_l": 22, "hip_r": -14, "knee_r": 20, "lean": 8},
    "guard2": {"shoulder_l": 62, "shoulder_r": 44, "elbow_l": 112, "elbow_r": 128, "hip_l": 26, "knee_l": 32, "hip_r": -10, "knee_r": 28, "lean": 10},
    "punch_r": {"shoulder_r": 86, "elbow_r": 4, "shoulder_l": 52, "elbow_l": 125, "twist": 30, "lean": 14, "hip_l": 32, "knee_l": 30, "hip_r": -24, "knee_r": 12},
    "duck": {"lean": 40, "hip_l": 52, "knee_l": 78, "hip_r": 44, "knee_r": 82, "shoulder_l": 60, "shoulder_r": 55, "elbow_l": 125, "elbow_r": 125, "head_nod": -18, "low": 0.66},
    "body_punch": {"lean": 24, "twist": 28, "shoulder_r": 58, "elbow_r": 38, "shoulder_l": 55, "elbow_l": 125, "hip_l": 36, "knee_l": 42, "hip_r": -16, "knee_r": 22},
    "hurt_b": {"lean": 46, "shoulder_l": -6, "shoulder_r": -2, "elbow_l": 112, "elbow_r": 118, "hip_l": 24, "knee_l": 40, "hip_r": 8, "knee_r": 38, "head_nod": 26, "low": 0.84},
    "hurt_b2": {"lean": 42, "shoulder_l": -2, "shoulder_r": -6, "elbow_l": 116, "elbow_r": 110, "hip_l": -10, "knee_l": 30, "hip_r": 26, "knee_r": 42, "head_nod": 24, "low": 0.84},
    "sit_mid": {"hip_l": 62, "hip_r": 62, "knee_l": 70, "knee_r": 70, "lean": 40, "shoulder_l": 30, "shoulder_r": 30, "elbow_l": 35, "elbow_r": 35, "low": 0.86},
}
JOINTS = ("lean", "twist", "head_turn", "head_nod", "shoulder_l", "shoulder_r", "abduct_l", "abduct_r", "elbow_l", "elbow_r",
          "hip_l", "hip_r", "hipturn_l", "hipturn_r", "knee_l", "knee_r")
# How far a person's joints go, in the angles above (degrees; a few degrees of slack on the straight side of elbows and knees).
# A mannequin outside these ranges is in a pose no body can take: Stage.check_bodies() flags it.
# lean and abduct are not checked: a mannequin cannot lie down or lie on its front, so scenes tip the trunk with lean to do
# it; and once the arm is raised forward, abduct turns the upper arm about itself rather than pulling it in.
ROM = {"twist": (-60, 60), "head_turn": (-80, 80), "head_nod": (-75, 70), "shoulder": (-65, 180),
       "elbow": (-5, 155), "hip": (-30, 135), "hipturn": (-45, 45), "knee": (-5, 165)}
JOINT_ZH = {"lean": "上身前倾（负数是后仰）", "twist": "上身扭转", "head_turn": "转头", "head_nod": "低头（负数是抬头）",
            "shoulder": "肩往前抬（负数是往后摆）", "abduct": "胳膊往外侧抬（负数是往里收）", "elbow": "肘弯", "hip": "大腿往前抬（负数是往后摆）",
            "hipturn": "大腿左右转", "knee": "膝弯"}


def heading_vec(deg: float) -> Vector:
    r = math.radians(deg)
    return Vector((math.sin(r), math.cos(r), 0.0))


def wall_spans(length, height, openings):
    """Split a wall into pieces around its openings. openings = [(centre along the wall, width, bottom, top), …]; openings that
    overlap along the wall stand above each other in one column (a window on every storey, a door with windows over it).
    Returns [(kind, index, start, end, bottom, top)] with kind "full" (a whole-height piece), "sill" (under an opening)
    or "top" (over an opening, up to the next opening above it or the top of the wall); index is the opening's number for
    sill / top and the piece's number for full. Where openings of different widths stand above each other, an opening's
    sill / top comes in one piece for each stretch of the wall with the same openings above each other."""
    ops = sorted(openings)
    edge = lambda i: (ops[i][0] - ops[i][1] / 2, ops[i][0] + ops[i][1] / 2)
    cols = []                                                    # [start, end, openings] of each column
    for i in sorted(range(len(ops)), key=lambda i: edge(i)[0]):
        lo, hi = edge(i)
        if lo < -1e-6 or hi > length + 1e-6:
            raise ValueError(f"opening {i} ({lo:.2f}–{hi:.2f} m) runs past the end of the wall")
        if cols and lo < cols[-1][1] - 1e-6:
            cols[-1][1] = max(cols[-1][1], hi)
            cols[-1][2].append(i)
        else:
            cols.append([lo, hi, [i]])
    out, s, nfull = [], 0.0, 0
    for lo, hi, idx in cols:
        if lo > s + 1e-6:
            out.append(("full", nfull, s, lo, 0.0, height))
            nfull += 1
        xs = sorted({x for i in idx for x in edge(i)})
        for a, b in zip(xs, xs[1:]):
            if b - a < 1e-6:
                continue
            z, below = 0.0, None
            for z0, z1, i in sorted((ops[i][2], ops[i][3], i) for i in idx if edge(i)[0] < b - 1e-6 and edge(i)[1] > a + 1e-6):
                if z0 < z - 1e-6:
                    raise ValueError(f"openings {below} and {i} overlap")
                if z0 > z + 1e-6:
                    out.append(("sill", i, a, b, z, z0) if below is None else ("top", below, a, b, z, z0))
                z, below = z1, i
            if z < height - 1e-6:
                out.append(("top", below, a, b, z, height))
        s = hi
    if s < length - 1e-6:
        out.append(("full", nfull, s, length, 0.0, height))
    return out


CADENCE = (1.4, 1.8)     # steps a second that read as a natural walk at 1.2–1.4 m/s; 2.0 already looks clipped (examples/fidelity)
STEP_M = 0.8             # the step length the default cadence aims at: 1.3 m/s -> 1.63 steps a second
SWING_M = 0.65           # the step length walk_a / walk_b are drawn for; hips and shoulders swing in proportion to the real step


def walk_keys(duration, distance, cadence=None, stride_s=None):
    """How a walk of `distance` metres in `duration` seconds is stepped. Returns (ks, cadence, step, swing):
    ks = where the walk poses (walk_a, walk_b, …) are keyed, as shares of the duration (the end pose follows at 1.0);
    cadence = steps a second as keyed; step = metres a step; swing = how far hips and shoulders swing against walk_a / walk_b as drawn.
    cadence given: one step every 1 / cadence s from the start; the end pose comes 0.5–1.5 steps after the last walk pose.
    Neither given: cadence = speed / 0.8 m, kept within 1.4–1.8. Below 1.1 m/s it stays at 1.4 and the steps get shorter; on the
    spot (distance 0) it still steps at 1.4, with the swing at its floor of 0.25 (feet shuffle, arms barely move).
    stride_s given (the old way): about one step every stride_s seconds, fitted so the steps fill the walk exactly; swing stays
    as drawn, so an old scene that passes stride_s looks as it did."""
    if stride_s is not None:
        n = max(1, round(duration / stride_s))
        return [i / n for i in range(n)], n / duration, distance / n, 1.0
    c = cadence or min(CADENCE[1], max(CADENCE[0], distance / duration / STEP_M))
    n = max(1, math.floor(c * duration - 0.5 + 1e-6) + 1)
    step = distance / duration / c
    return [i / (c * duration) for i in range(n)], c, step, max(0.25, step / SWING_M)


def walk_swing(pose, swing):
    """The hip and shoulder angles of a walk pose scaled by `swing` (knees, elbows and lean stay)."""
    return {k: v * swing for k, v in POSES[pose].items() if k.startswith(("hip_", "shoulder_"))}


def strike_keys(t, step=0.5, pose="punch_r"):
    """A fast right-hand strike fully out at time t: [(time, metres moved toward where the striker faces, pose, joints), …].
    Loads from 0.35 s before (the upper body turns back), steps in 0.15 s before, out in 0.15 s, held 0.08 s, back to guard in
    0.2 s. Keyed like this in a jointed previz, the film's punch landed within about 0.2 s of t (examples/fidelity)."""
    return [(t - 0.35, 0.0, "guard", {"twist": -16, "lean": 4}),
            (t - 0.15, 0.6 * step, "guard2", {"twist": -20, "lean": 10}),
            (t, step, pose, {}),
            (t + 0.08, step + 0.01, pose, {}),
            (t + 0.28, step - 0.03, "guard", {})]


def sit_keys(t, seat_at, heading, seat=0.45):
    """Sitting down on a chair, seated at time t: [(time, (x, y), facing or None, pose, joints), …]. seat_at = centre of the seat,
    heading = the way the sitter will face. One step in front of the seat at t - 1.3 (the facing is filled in by sit_down: half-way
    round), back to the chair at t - 1.0, knees give at t - 0.75, hips back and down with the trunk forward at t - 0.4, seated at t
    (still leaning forward), upright at t + 0.35."""
    fx, fy = math.sin(math.radians(heading)), math.cos(math.radians(heading))
    at = lambda d: (seat_at[0] + fx * d, seat_at[1] + fy * d)
    return [(t - 1.3, at(0.35), None, "walk_b", {"hip_r": 16, "hip_l": -10}),
            (t - 1.0, at(0.35), heading, "stand", {}),
            (t - 0.75, at(0.35), None, "stand", {"lean": 6, "knee_l": 8, "knee_r": 8, "hip_l": 6, "hip_r": 6}),
            (t - 0.4, at(0.19), None, "sit_mid", {}),
            (t, at(0.04), None, "sit", {"seat": seat, "lean": 16}),
            (t + 0.35, at(0.04), None, "sit", {"seat": seat, "lean": 2})]          # a capsule needs the seat on every key


def key_beats(keys):
    """From one person's pose keys [(time, pose), …] in any order (a later key at the same time wins): the changeovers of the
    feet (half-way between a walk_a and a walk_b key next to each other: the moment the legs pass) and the key poses (each time
    the pose changes, walk poses left out). Returns (changeovers, poses)."""
    ks = sorted(dict(keys).items())
    walk = {"walk_a", "walk_b"}
    changes = [round((a + b) / 2, 3) for (a, pa), (b, pb) in zip(ks, ks[1:]) if {pa, pb} == walk]
    poses = [(round(t, 3), p) for i, (t, p) in enumerate(ks) if p not in walk and (i == 0 or ks[i - 1][1] != p)]
    return changes, poses


def _mesh(name, build, smooth=False):
    me, bm = bpy.data.meshes.new(name), bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return me


def _box(bm, size, offset=(0, 0, 0)):
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=offset, verts=bm.verts)


def _limb(bm, r_top, r_bottom, length, squash=1.0):
    """Tapered tube hanging from the origin down -Z, with a ball at the joint."""
    bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=r_bottom, radius2=r_top, depth=length)
    bmesh.ops.translate(bm, vec=(0, 0, -length / 2), verts=bm.verts)
    ball = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=r_top * 1.08)["verts"]
    if squash != 1.0:
        bmesh.ops.scale(bm, vec=(1, squash, 1), verts=bm.verts)
    return ball


def _linear_key(ob, path, f):
    """Make the key just inserted on ob.path at frame f linear (bpy 5.3 gives keys inserted from Python Bezier ease)."""
    cb = anim_utils.animdata_get_channelbag_for_assigned_slot(ob.animation_data)
    for fc in cb.fcurves if cb else ():
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - f) < 0.5 and kp.interpolation == "BEZIER":
                    kp.interpolation = "LINEAR"


def key(ob, path, f):
    """keyframe_insert with a linear key. Use it in your own scene code instead of ob.keyframe_insert."""
    ob.keyframe_insert(path, frame=f)
    _linear_key(ob, path, f)


PLAN_FONTS = ("/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
              "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")


def plan_font():
    """A Chinese font file for the plan labels: $BLOCKING_FONT, else the first of PLAN_FONTS that exists; None when none does."""
    return next((fp for fp in (os.environ.get("BLOCKING_FONT"), *PLAN_FONTS) if fp and Path(fp).exists()), None)


class Stage:
    def __init__(self, fps: int = 24, size=(1280, 720), stand_ins: bool = False):
        """stand_ins=True: every person() is a capsule stand-in whatever its kind. Run the same scene script once more with it
        to render the previz that goes to the video model as a reference video (jointed mannequins are for looking and stills)."""
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = s = bpy.context.scene
        self.fps, self.size, self.stand_ins = fps, size, stand_ins
        s.render.engine = "BLENDER_EEVEE"
        s.render.resolution_x, s.render.resolution_y = size
        s.render.resolution_percentage = 100
        s.render.fps = fps
        s.render.image_settings.file_format = "PNG"
        s.view_settings.view_transform = "Standard"
        s.eevee.taa_render_samples = 32
        world = bpy.data.worlds.new("world")
        s.world = world
        world.use_nodes = True
        bg = world.node_tree.nodes["Background"]
        bg.inputs[0].default_value, bg.inputs[1].default_value = (0.80, 0.80, 0.80, 1), 0.9
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
        sun.data.energy, sun.data.angle = 2.2, math.radians(12)
        sun.rotation_euler = (math.radians(48), 0, math.radians(35))
        s.collection.objects.link(sun)
        self.mats, self.set_objs, self.items, self.people, self.cams, self.doors = {}, [], [], {}, {}, []
        self._checked = None                                  # how many ground objects there were when the doors were last checked

    # ---------- basics
    def mat(self, color):
        rgb = COLORS[color] if isinstance(color, str) else tuple(color)
        if rgb not in self.mats:
            m = bpy.data.materials.new(f"m{len(self.mats)}")
            m.use_nodes = True
            b = m.node_tree.nodes["Principled BSDF"]
            b.inputs["Base Color"].default_value = (*rgb, 1)
            b.inputs["Roughness"].default_value = 0.9
            if "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = 0.1
            m.diffuse_color = (*rgb, 1)
            self.mats[rgb] = m
        return self.mats[rgb]

    def _add(self, name, mesh, color, parent=None, loc=(0, 0, 0)):
        ob = bpy.data.objects.new(name, mesh)
        if mesh is not None:
            ob.data.materials.append(self.mat(color))
        ob.parent, ob.location = parent, loc
        self.scene.collection.objects.link(ob)
        return ob

    def _at3(self, at):
        return tuple(at) if len(at) == 3 else (at[0], at[1], self.ground(*at))

    def frame(self, t: float) -> int:
        return int(round(t * self.fps)) + 1

    def at_time(self, t: float):
        self.scene.frame_set(self.frame(t))
        bpy.context.view_layer.update()

    def linear(self):
        """Make every Bezier key in the scene linear (keys your own code inserted with ob.keyframe_insert). Called before every output."""
        for act in bpy.data.actions:
            for layer in act.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            for kp in fc.keyframe_points:
                                if kp.interpolation == "BEZIER":
                                    kp.interpolation = "LINEAR"

    def ground(self, x: float, y: float, top: float = 20.0) -> float:
        """Height of what people walk on (floors, steps, boxes made with ground=True) under the point (x, y).
        Walls, door frames, ceilings and furniture are not ground: a seated pose gives the seat height above the floor;
        to stand on furniture pass z."""
        zs = [z for z, _ob in self._hits(x, y, top)]
        return round(max(zs), 4) if zs else 0.0

    def _hits(self, x, y, top=20.0):
        """[(height, object)] for every ground object under (x, y): floors above each other give one each."""
        bpy.context.view_layer.update()
        out = []
        for ob in self.set_objs:                     # each ground object on its own: a wall standing on the floor cannot hide it
            mi = ob.matrix_world.inverted()
            hit, loc, _n, _i = ob.ray_cast(mi @ Vector((x, y, top)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
            if hit:
                out.append(((ob.matrix_world @ loc).z, ob))
        return out

    def _check_doors(self):
        """Doors standing on a looked-up height (hinge given as (x, y)), held against the set as it is now. Raises ValueError
        when nothing one stands on a step either side of the doorway is at the door's height (the floor was built after the
        door, or the look-up missed a hinge on the very edge of the floor), or when floors lie above each other there (which
        storey?). Runs before every still, clip, report and plan, again whenever ground has been added since."""
        if self._checked == len(self.set_objs):
            return
        self._checked = len(self.set_objs)
        floors = {it["obj"] for it in self.items if it["kind"] == "floor"}
        for d in self.doors:
            if not d.looked_up:
                continue
            f, z = heading_vec(d.heading), d.hinge[2]
            mid, side = Vector(d.hinge) + f * (d.width / 2), Vector((-f.y, f.x, 0))
            found, levels = set(), set()
            for k in (-0.25, 0.25):
                hits = self._hits(*(mid + side * k).xy)
                found |= {round(h, 2) for h, _ob in hits}
                fl = {round(h, 2) for h, ob in hits if ob in floors}
                if len(fl) > 1:
                    levels |= fl
            xy = f"{d.hinge[0]:g}, {d.hinge[1]:g}"
            if levels:
                raise ValueError(f"door {d.name}: floors at {', '.join(f'{v:g}' for v in sorted(levels))} m lie above each other at the "
                                 f"doorway, so the height looked up under the hinge ({z:.2f} m) is a guess. Give the height of the floor "
                                 f"this door stands on: hinge=({xy}, z)")
            if found and all(abs(z - h) > 0.02 for h in found):
                raise ValueError(f"door {d.name} stands at {z:.2f} m, the height found under its hinge when it was built, but the floor "
                                 f"beside the doorway is at {' / '.join(f'{h:g}' for h in sorted(found))} m: the floor was built after the "
                                 f"door, or the hinge sits on the very edge of the floor where the look-up misses it. Give the height: "
                                 f"hinge=({xy}, {f'{min(found):g}' if len(found) == 1 else 'z'})")

    def _item(self, kind, name, size, at, heading, color, ob):
        self.items.append({"kind": kind, "name": name, "size": size, "at": tuple(at), "heading": heading, "color": color, "obj": ob})

    # ---------- the set
    def box(self, name, size, at, heading=0.0, color="prop", ground=True, kind="box"):
        """A box of size (width across, depth along heading, height); `at` is the centre of its bottom face, (x, y) or (x, y, z):
        two numbers put it on the ground there."""
        at = self._at3(at)
        ob = self._add(name, _mesh(name, lambda bm: _box(bm, size, (0, 0, size[2] / 2))), color, loc=at)
        ob.rotation_euler = (0, 0, -math.radians(heading))
        if ground:
            self.set_objs.append(ob)
        self._item(kind, name, size, at, heading, color, ob)
        return ob

    def cylinder(self, name, radius, height, at, color="prop", ground=False, cone=1.0):
        """An upright cylinder (pillar, round table top, barrel, lamp post); `at` is the centre of its bottom. cone = top radius / bottom radius."""
        at = self._at3(at)
        ob = self._add(name, _mesh(name, lambda bm: (bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=radius, radius2=radius * cone, depth=height),
                                                     bmesh.ops.translate(bm, vec=(0, 0, height / 2), verts=bm.verts)), smooth=False), color, loc=at)
        if ground:
            self.set_objs.append(ob)
        self._item("box", name, (radius * 2, radius * 2, height), at, 0.0, color, ob)
        return ob

    def ball(self, name, radius, at, color="prop"):
        """A sphere; `at` is its centre (x, y, z)."""
        ob = self._add(name, _mesh(name, lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius), smooth=True), color, loc=at)
        self._item("box", name, (radius * 2, radius * 2, radius * 2), (at[0], at[1], at[2] - radius), 0.0, color, ob)
        return ob

    def asset(self, name, path, at, heading=0.0, height=None, length=None, color="prop", front=0.0):
        """Bring in a model file (.glb/.gltf, .obj, .fbx, .stl) as one plain-coloured object standing on `at`.
        Give its real `height` or its `length` (the longer side of its footprint) in metres: models come in any unit.
        front = the compass direction the model's own front points to inside the file (try 0, 90, 180, 270 and look at the plan)."""
        before = set(bpy.data.objects)
        ext = Path(path).suffix.lower()
        if ext in (".glb", ".gltf"):
            bpy.ops.import_scene.gltf(filepath=str(path))
        elif ext == ".obj":
            bpy.ops.wm.obj_import(filepath=str(path))
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=str(path))
        elif ext == ".stl":
            bpy.ops.wm.stl_import(filepath=str(path))
        else:
            raise ValueError(f"asset: cannot read {ext} files")
        new = [o for o in bpy.data.objects if o not in before]
        meshes = [o for o in new if o.type == "MESH"]
        bpy.context.view_layer.update()
        me, bm = bpy.data.meshes.new(name), bmesh.new()
        for o in meshes:                                   # bake every part into one mesh in world space
            tmp = o.data.copy()
            tmp.transform(o.matrix_world)
            bm.from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        xs, ys, zs = [v.co.x for v in bm.verts], [v.co.y for v in bm.verts], [v.co.z for v in bm.verts]
        w, d, h = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
        k = height / h if height else length / max(w, d) if length else 1.0
        bmesh.ops.translate(bm, vec=(-(max(xs) + min(xs)) / 2, -(max(ys) + min(ys)) / 2, -min(zs)), verts=bm.verts)
        bmesh.ops.scale(bm, vec=(k, k, k), verts=bm.verts)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(front), 3, "Z"), verts=bm.verts)
        for f in bm.faces:
            f.material_index = 0
        bm.to_mesh(me)
        bm.free()
        at = self._at3(at)
        ob = self._add(name, me, color, loc=at)
        ob.rotation_euler = (0, 0, -math.radians(heading))
        size = (d * k, w * k, h * k) if round(front / 90) % 2 else (w * k, d * k, h * k)
        self._item("box", name, size, at, heading, color, ob)
        return ob

    def floor(self, x0, y0, x1, y1, z=0.0, color="floor", name="floor"):
        return self.box(name, (abs(x1 - x0), abs(y1 - y0), 0.1), ((x0 + x1) / 2, (y0 + y1) / 2, z - 0.1), color=color, kind="floor")

    def ceiling(self, x0, y0, x1, y1, z=2.8, light=True, energy=20.0, spacing=2.5, color="wall", name="ceiling"):
        """A ceiling slab at height z over the rectangle, and (light=True) a grid of soft shadowless lamps under it.
        With a ceiling the sun no longer reaches inside: without lamps walls, floor and ceiling come out the same flat grey.
        energy = watts per lamp (a few tens for a corridor or a room; thousands for a hall tens of metres high).
        Hide it in a shot that looks down from above: camera(..., hide=["ceiling"])."""
        ob = self.box(name, (abs(x1 - x0), abs(y1 - y0), 0.1), ((x0 + x1) / 2, (y0 + y1) / 2, z), color=color, ground=False, kind="ceiling")
        if light:
            nx, ny = max(1, round(abs(x1 - x0) / spacing)), max(1, round(abs(y1 - y0) / spacing))
            for i in range(nx):
                for j in range(ny):
                    self.fill_light((x0 + (x1 - x0) * (i + 0.5) / nx, y0 + (y1 - y0) * (j + 0.5) / ny, z - 0.45), energy, name=f"{name}_lamp")
        return ob

    def fill_light(self, at, energy=20.0, shadow=False, name="fill"):
        """A point lamp at (x, y, z), soft and (by default) without shadows: lights a room without making new dark patches."""
        light = bpy.data.lights.new(name, "POINT")
        light.energy, light.use_shadow, light.shadow_soft_size = energy, shadow, 0.5
        ob = bpy.data.objects.new(name, light)
        ob.location = at
        self.scene.collection.objects.link(ob)
        return ob

    def wall(self, a, b, height=2.8, thickness=0.12, z=0.0, color="wall", name="wall", door=None, doors=(), windows=()):
        """A wall from point a to point b (x, y). Openings are measured from a:
        door = (distance from a to the door centre, width, height) cuts one opening; doors = [(…), (…)] cuts several;
        windows = [(distance from a to the centre, width, height, sill height), …] cuts window holes and puts a frame with a
        middle bar in each (window()). Openings may stand above each other at the same distance from a: one tall wall with a
        window on every storey (sill heights measured from z), or a door with windows over it. A door opening still needs
        door() for its leaf and frame. Returns the wall pieces."""
        a, b = Vector((*a, 0)), Vector((*b, 0))
        d = b - a
        length, heading = d.length, math.degrees(math.atan2(d.x, d.y))
        u = d.normalized()
        ds = ([door] if door else []) + list(doors)
        ops = [(c, w, 0.0, h) for c, w, h in ds] + [(c, w, s, s + h) for c, w, h, s in windows]
        one = len(ops) == 1
        pieces, names = [], []
        for kind, i, s0, s1, z0, z1 in wall_spans(length, height, ops):
            n = (name if not ops else f"{name}_{'ab'[i] if one else 's' + str(i)}" if kind == "full" else
                 f"{name}_{kind}" if one else f"{name}_{kind}{i}")
            names.append(n)
            if names.count(n) > 1:                  # the piece over a wide opening goes on beside a narrower one above it
                n += f"_{names.count(n)}"
            mid = a + u * (s0 + s1) / 2
            pieces.append(self.box(n, (thickness, s1 - s0, z1 - z0), (mid.x, mid.y, z + z0), heading, color, ground=False, kind="wall"))
        for i, (c, w, h) in enumerate(ds):
            self.items.append({"kind": "door", "name": f"{name}_door" if len(ds) == 1 else f"{name}_door{i}",
                               "at": tuple(a + u * c), "heading": heading, "width": w})
        for i, (c, w, h, s) in enumerate(windows):
            p = a + u * c
            self.window(f"{name}_win" if len(windows) == 1 else f"{name}_win{i}", (p.x, p.y, z), heading, w, h, s, depth=thickness + 0.04)
        return pieces

    def window(self, name, at, heading, width=1.2, height=1.2, sill=0.9, depth=0.16, bar=0.06, mullion=True, color="frame"):
        """A window frame (two jambs, head, sill, and a middle bar) standing in a wall hole. at = (x, y[, z]) on the wall line
        at floor level; heading = the direction the wall runs. wall(windows=[…]) cuts the hole and calls this."""
        at = self._at3(at)
        c, u = Vector(at), heading_vec(heading)
        parts = [("jamb_a", -width / 2 + bar / 2, sill, (depth, bar, height)), ("jamb_b", width / 2 - bar / 2, sill, (depth, bar, height)),
                 ("sill", 0.0, sill, (depth, width, bar)), ("head", 0.0, sill + height - bar, (depth, width, bar))]
        if mullion:
            parts.append(("mullion", 0.0, sill, (depth * 0.7, bar * 0.7, height)))
        for n, along, z0, size in parts:
            p = c + u * along
            self.box(f"{name}_{n}", size, (p.x, p.y, c.z + z0), heading, color, ground=False, kind="window")

    def stairs(self, name, at, heading, steps, rise=0.165, run=0.27, width=1.1, color="step", solid=True):
        """Steps going up along `heading`; `at` is the centre of the foot of the first step. Returns the top point.
        solid=True: each step is a block down to the height of `at`, the flight a solid wedge (a flight standing on the floor).
        solid=False: a flight 0.15 m thick under the steps, open underneath like a flight above a landing or above another
        flight: a camera or a person fits under it."""
        f, p = heading_vec(heading), Vector(self._at3(at))
        for i in range(steps):
            c = p + f * (run * (i + 0.5))
            z0 = 0.0 if solid else max(0.0, rise * i - 0.15)
            self.box(f"{name}_{i}", (width, run, rise * (i + 1) - z0), (c.x, c.y, p.z + z0), heading, color, kind="step")
        return tuple(p + f * (run * steps) + Vector((0, 0, rise * steps)))

    def sofa(self, name, at, heading, length=2.0, depth=0.88, seat=0.42, back=0.82, arm=0.62, color="green"):
        """A three-seat sofa; it faces `heading` (the side you sit from). `at` is the centre of its footprint."""
        at = self._at3(at)
        root = self._add(name, None, color, loc=at)
        root.rotation_euler = (0, 0, -math.radians(heading))
        aw, bd = 0.22, 0.24
        parts = [((length - 2 * aw, depth - bd, seat), (0, bd / 2, seat / 2)), ((length, bd, back), (0, -depth / 2 + bd / 2, back / 2)),
                 ((aw, depth, arm), (-length / 2 + aw / 2, 0, arm / 2)), ((aw, depth, arm), (length / 2 - aw / 2, 0, arm / 2))]
        base = COLORS[color] if isinstance(color, str) else tuple(color)
        for i, (size, off) in enumerate(parts):   # seat a little lighter than back and arms, so the shape reads from any side
            shade = tuple(min(1.0, v * (1.5 if i == 0 else 1.0) + (0.04 if i == 0 else 0)) for v in base)
            self._add(f"{name}_{i}", _mesh(f"{name}_{i}", lambda bm, s=size, o=off: _box(bm, s, o)), shade, parent=root)
        self._item("sofa", name, (length, depth, back), at, heading, color, root)
        return root

    def table(self, name, at, heading=0.0, size=(1.0, 0.7, 0.74), color="prop"):
        """A table: top (width across, depth along heading) on four legs; `at` is the centre of its footprint on the floor."""
        w, d, h = size
        at = self._at3(at)
        root = self._add(name, None, color, loc=at)
        root.rotation_euler = (0, 0, -math.radians(heading))
        self._add(f"{name}_top", _mesh(f"{name}_top", lambda bm: _box(bm, (w, d, 0.04), (0, 0, h - 0.02))), color, parent=root)
        for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
            self._add(f"{name}_leg{i}", _mesh(f"{name}_leg{i}", lambda bm, sx=sx, sy=sy: _box(bm, (0.05, 0.05, h - 0.04), (sx * (w / 2 - 0.06), sy * (d / 2 - 0.06), (h - 0.04) / 2))), color, parent=root)
        self._item("sofa", name, (w, d, h), at, heading, color, root)
        return root

    def chair(self, name, at, heading=0.0, seat=0.45, size=(0.44, 0.42), back=0.86, color="prop"):
        """A chair: seat, four legs and a backrest; it faces `heading` (the way the sitter looks). `at` is the centre of the seat
        on the floor. Sit someone on it with place(…, pose="sit", seat=<seat>) at a point just in front of it, not on it."""
        w, d = size
        at = self._at3(at)
        root = self._add(name, None, color, loc=at)
        root.rotation_euler = (0, 0, -math.radians(heading))
        parts = [("seat", (w, d, 0.04), (0, 0, seat - 0.02))]
        for i, (sx, sy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):            # the two back legs run up into the backrest
            top = seat - 0.04 if sy > 0 else back
            parts.append((f"leg{i}", (0.035, 0.035, top), (sx * (w / 2 - 0.03), sy * (d / 2 - 0.03), top / 2)))
        parts.append(("back", (w, 0.03, 0.24), (0, -d / 2 + 0.03, back - 0.12)))
        for n, s, o in parts:
            self._add(f"{name}_{n}", _mesh(f"{name}_{n}", lambda bm, s=s, o=o: _box(bm, s, o)), color, parent=root)
        self._item("chair", name, (w, d, back), at, heading, color, root)
        self.items[-1]["seat"] = seat
        return root

    def stool(self, name, at, size=(0.34, 0.34, 0.45), color="prop"):
        return self.box(name, size, at, color=color, ground=False, kind="box")

    def key(self, ob, t, at=None, heading=None):
        """Keyframe a prop (anything box(), sofa(), table() … returned) at time t: where it is and which way it faces."""
        f = self.frame(t)
        if at is not None:
            ob.location = at if len(at) == 3 else (*at, ob.location.z)
            key(ob, "location", f)
        if heading is not None:
            ob.rotation_euler = (ob.rotation_euler.x, ob.rotation_euler.y, -math.radians(heading))
            key(ob, "rotation_euler", f)
        return ob

    def door(self, name, hinge, heading, width=0.85, height=2.0, lock=1.0, frame=True, color="door", into=None, into_name=""):
        """A door leaf in a wall opening. `hinge` is the hinge point, (x, y) or (x, y, z); the closed leaf runs from there along `heading`.
        Two numbers stand the door on the highest floor already built under that point: build the floor before the door.
        With floors above each other (an upper storey, a landing) give z, the height of the floor the door stands on.
        A looked-up height is checked again at the first still, clip, describe or plan: ValueError when the floor beside the
        doorway is at another height by then, or when floors lie above each other there.
        into = any point (x, y) on the side the leaf swings into (a point inside the room for a door that opens inward);
        into_name = what that side is called in describe() ("屋里", "楼道"). Then door.open(t, degrees) swings it that way.
        door.set(t, angle) keys a signed angle instead: positive swings the leaf to the left of `heading` (counter-clockwise from above).
        Set the hinge side and the swing side when you build the set: from the hinge you know which jamb, from `into` which room."""
        looked_up = len(hinge) == 2
        hinge = self._at3(hinge)
        f, z = heading_vec(heading), hinge[2]
        if frame:                                                     # dark jambs and lintel so the opening reads from any side
            for n, k in (("jamb_a", -0.035), ("jamb_b", width + 0.035)):
                c = Vector((hinge[0], hinge[1], 0)) + f * k
                self.box(f"{name}_{n}", (0.18, 0.07, height), (c.x, c.y, z), heading, "frame", ground=False)
            c = Vector((hinge[0], hinge[1], 0)) + f * (width / 2)
            self.box(f"{name}_lintel", (0.18, width + 0.14, 0.07), (c.x, c.y, z + height), heading, "frame", ground=False)
        root = self._add(name, None, color, loc=(hinge[0], hinge[1], z))
        root.rotation_euler = (0, 0, -math.radians(heading))
        self._add(f"{name}_leaf", _mesh("leaf", lambda bm: _box(bm, (0.05, width, height), (0, width / 2, height / 2))), color, parent=root)
        if lock:
            for side in (-1, 1):                                      # a lock plate on both faces, near the free edge
                self._add(f"{name}_lock{side}", _mesh("lock", lambda bm, sd=side: _box(bm, (0.03, 0.07, 0.16), (sd * 0.035, width - 0.07, lock))), "yellow", parent=root)
        sign = None
        if into is not None:
            left = Vector((-f.y, f.x, 0))
            sign = 1 if (Vector((into[0] - hinge[0], into[1] - hinge[1], 0))).dot(left) > 0 else -1
        d = Door(self, name, root, (hinge[0], hinge[1], z), heading, width, height, lock or 1.0, sign, into_name)
        d.looked_up = looked_up
        d.set(0.0, 0.0)
        self.doors.append(d)
        return d

    def stills(self, shots, folder, last=()):
        """One white-model still per shot at its first frame: <folder>/<shot>_a.png; shots named in `last` also get <shot>_b.png near the end.
        shots = [(name, camera, t0, t1), …]. Returns {shot: layout sentences}."""
        folder, notes = Path(folder), {}
        folder.mkdir(parents=True, exist_ok=True)
        for name, cam, t0, t1 in shots:
            self.still(cam, folder / f"{name}_a.png", t0)
            notes[name] = self.describe(cam, t0)
            if name in last:
                self.still(cam, folder / f"{name}_b.png", t1 - 2 / self.fps)
                notes[name + "_end"] = self.describe(cam, t1 - 2 / self.fps)
        return notes

    def previz(self, shots, path, only=None, samples=None, tag=None, scale=1.0, missing=False, part=None):
        """Render every shot from its camera and join them into one clip, cut exactly at the shot boundaries.
        Each shot is also left as pv_<shot>[_<tag>].mp4 next to it; tag defaults to "capsule" when everyone is a capsule stand-in,
        so a capsule previz does not overwrite the jointed one.
        Which shots are rendered: by default all of them, again; missing=True only those whose file is not there yet (go on after
        a stop; join after part=); only = [names] those named, and the missing ones.
        samples = render samples (default 32; 8 is enough for a reference video). scale = share of the frame size to render at
        (0.5 renders a quarter of the pixels; the clips are scaled back up to full size, softer).
        part = (k, n): render only shots k, k + n, k + 2n, … of the list and do not join. Run n processes with k = 0 … n-1,
        then one more call with missing=True joins. Returns the joined clip's path (None with part)."""
        path = Path(path)
        tag = ("capsule" if self.people and all(isinstance(p, Capsule) for p in self.people.values()) else "") if tag is None else tag
        parts = []
        for i, (name, cam, t0, t1) in enumerate(shots):
            p = path.parent / f"pv_{name}{'_' + tag if tag else ''}.mp4"
            parts.append(p)
            if part and i % part[1] != part[0]:
                continue
            if not p.exists() or (only is None and not missing) or (only is not None and name in only):
                self.clip(cam, p, t0, t1, samples=samples, scale=scale)
        if part:
            return None
        lst = path.with_suffix(".txt")
        lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                        "-r", str(self.fps), "-movflags", "+faststart", str(path)], check=True)
        lst.unlink()
        return path

    def order(self, cam, t=0.0):
        """Names of the people seen in frame, from screen left to screen right (someone wholly hidden behind something is left out)."""
        return [p["name"] for p in self.report(cam, t)["people"] if p["shot"] != "不在画面里" and not p["hidden"]]

    def flips(self, shots):
        """Cuts where people swap sides: for each shot, compared with the last earlier shot that had two or more people in frame,
        the people who are in both and whose left-right order is reversed (the camera crossed their line). A reverse shot does this
        on purpose; the prompt of the later shot must then say the new order. Returns [(earlier, later, order before, order now)]."""
        out, prev = [], None
        for name, cam, t0, _t1 in shots:
            cur = self.order(cam, t0)
            if len(cur) < 2:
                continue
            if prev:
                both = [n for n in prev[1] if n in cur]
                if len(both) > 1 and [n for n in cur if n in both] == both[::-1]:
                    out.append((prev[0], name, both, [n for n in cur if n in both]))
            prev = (name, cur)
        return out

    def changes(self, shots):
        """What changes between the first and the last frame of each shot: who swaps sides, who turns, who comes into or leaves
        the frame, a door that opens or closes, a prop that moves. Shots listed here usually need a last frame too
        (stills(last=…) and a first + last frame feed). Returns {shot: [sentences]} for the shots where something changes."""
        out = {}
        for name, cam, t0, t1 in shots:
            a, b = self.report(cam, t0), self.report(cam, t1 - 2 / self.fps)
            lines = []
            seen = lambda r: [p["name"] for p in r["people"] if p["shot"] != "不在画面里" and not p["hidden"]]
            if len(seen(a)) > 1 and seen(a) != seen(b) and set(seen(a)) == set(seen(b)):
                lines.append(f"左右：{'、'.join(seen(a))} → {'、'.join(seen(b))}")
            pa, pb = {p["name"]: p for p in a["people"]}, {p["name"]: p for p in b["people"]}
            show = lambda p: "画面里看不见" if p["shot"] == "不在画面里" or p["hidden"] else p["facing"]
            for n in pa:
                if show(pa[n]) != show(pb[n]):
                    lines.append(f"{n}：{show(pa[n])} → {show(pb[n])}")
            for da, db in zip(a["doors"], b["doors"]):
                if abs(da["angle"] - db["angle"]) > 20:
                    lines.append(f"{da['name']}：{da['state']} → {db['state']}")
            for it in self.items:
                ob = it.get("obj")
                if ob is None or it["kind"] in ("floor", "wall", "step", "ceiling", "window"):
                    continue
                self.at_time(t0)
                p0, r0 = ob.matrix_world.translation.copy(), ob.matrix_world.to_euler().z
                self.at_time(t1 - 2 / self.fps)
                p1, r1 = ob.matrix_world.translation.copy(), ob.matrix_world.to_euler().z
                turn = abs(math.degrees((r1 - r0 + math.pi) % (2 * math.pi) - math.pi))
                if (p1 - p0).length > 0.15 or turn > 20:
                    lines.append(f"{it['name']}：挪了 {(p1 - p0).length:.2f} 米" + (f"、转了 {turn:.0f} 度" if turn > 20 else ""))
            if lines:
                out[name] = lines
        return out

    def gap(self, a, b, t=None):
        """Distance on the floor between two people's chests (names or the objects person() returned), in metres."""
        if t is not None:
            self.at_time(t)
        pa, pb = (self.people[x] if isinstance(x, str) else x for x in (a, b))
        u, v = pa.landmarks()["chest"], pb.landmarks()["chest"]
        return round(math.hypot(u.x - v.x, u.y - v.y), 2)

    def _point(self, x, role):
        """A world point for sees(): (x, y, z); a person's name (their eyes as the one who looks, their head as the target);
        (person name, part) with part one of head / eyes / chest / pelvis / feet / hand_l / hand_r / mouth / lap;
        a camera name (its lens); or the name of any object (its middle)."""
        if isinstance(x, (tuple, list)) and x and isinstance(x[0], str):
            p = self.people[x[0]]
            lm = p.landmarks()
            return (lm[x[1]] if x[1] in lm else p.point(x[1])), p.objs
        if isinstance(x, str):
            if x in self.people:
                p = self.people[x]
                return p.landmarks()["eyes" if role == "from" else "head"], p.objs
            if x in self.cams:
                return self.cams[x]["obj"].matrix_world.translation.copy(), set()
            ob = bpy.data.objects[x]
            parts = {ob, *ob.children_recursive}
            pts = [o.matrix_world @ Vector(c) for o in parts if o.type == "MESH" for c in o.bound_box] or [ob.matrix_world.translation]
            return sum(pts, Vector()) / len(pts), parts
        return Vector(x), set()

    def sees(self, a, b, t=None, ignore=()):
        """What is in the way between a and b (see _point for what a and b can be), at time t. Returns the names of the things
        the straight line hits, nearest first; an empty list means a sees b. The two people at the ends, things hidden at that
        moment, and the names in `ignore` are not counted. A camera name as `a` also leaves out what that camera hides."""
        if t is not None:
            self.at_time(t)
        bpy.context.view_layer.update()
        with self._hidden(a if isinstance(a, str) and a in self.cams else None):
            pa, skip_a = self._point(a, "from")
            pb, skip_b = self._point(b, "to")
            skip = skip_a | skip_b
            for w in (self.people.get(n) for n in ignore if isinstance(n, str)):
                if w is not None:
                    skip |= w.objs
            names_ignored = {n for n in ignore if isinstance(n, str) and n not in self.people}
            dg = bpy.context.evaluated_depsgraph_get()
            d = pb - pa
            if d.length < 1e-6:
                return []
            u, origin, out = d.normalized(), pa.copy(), []
            for _ in range(60):
                left = (pb - origin).length - 0.02
                if left <= 0:
                    break
                hit, loc, _n, _i, ob, _m = self.scene.ray_cast(dg, origin, u, distance=left)
                if not hit:
                    break
                o = ob.original
                label = self._label(o)
                if o not in skip and not o.hide_render and label not in names_ignored and o.name not in names_ignored and label not in out:
                    out.append(label)
                origin = loc + u * 1e-3
            return out

    def _ray(self, dg, origin, u, distance):
        """The first thing a ray hits within `distance`, passing through things hidden at this moment (hide_render).
        Returns (hit, where, the original object)."""
        origin = origin.copy()
        for _ in range(30):
            hit, loc, _n, _i, ob, _m = self.scene.ray_cast(dg, origin, u, distance=distance)
            if not hit or not ob.original.hide_render:
                return hit, loc, (ob.original if hit else None)
            distance -= (loc - origin).length + 1e-3
            origin = loc + u * 1e-3
            if distance <= 0:
                break
        return False, None, None

    def _inside(self, point):
        """The first solid thing of the set (not a person) that the world point is inside right now, as (object, kind of the
        item it belongs to: "step", "wall", "sofa" …), or None. Things hidden at this moment do not count."""
        body = set().union(*(p.objs for p in self.people.values()))
        kinds = {it["obj"]: it["kind"] for it in self.items if it.get("obj") is not None}
        for ob in self.scene.objects:
            if ob.type != "MESH" or ob.hide_render or ob in body:
                continue
            q = ob.matrix_world.inverted_safe() @ point
            bb = ob.bound_box
            if not all(min(v[k] for v in bb) - 1e-4 <= q[k] <= max(v[k] for v in bb) + 1e-4 for k in range(3)):
                continue
            leaves = 0
            for d in (Vector((0, 0, 1)), Vector((0, 0, -1))):    # from inside a closed mesh a ray leaves through a face turned away
                hit, _loc, n, _i = ob.ray_cast(q, d)
                leaves += bool(hit and n.dot(d) > 0)
            if leaves == 2:
                return ob, kinds.get(ob, kinds.get(ob.parent))
        return None

    def _label(self, ob):
        for p in self.people.values():
            if ob in p.objs:
                return p.name
        for d in self.doors:
            if ob.parent is d.root:
                return d.name
        return ob.name

    def _match(self, names):
        out = set()
        for n in names:
            obs = [n] if isinstance(n, bpy.types.Object) else [o for o in bpy.data.objects if o.name == n or o.name.startswith(n + "_")]
            for o in obs:
                out.add(o)
                out.update(o.children_recursive)
        return out

    @contextlib.contextmanager
    def _hidden(self, cam):
        """While a camera is in use, leave out of the render and of the ray tests the things it was told to hide."""
        obs = self._match(self.cams[cam]["hide"]) if cam and self.cams[cam]["hide"] else set()
        was = [(o, o.hide_render, o.hide_viewport) for o in obs]
        for o in obs:
            o.hide_render = o.hide_viewport = True
        if obs:
            bpy.context.view_layer.update()
        try:
            yield
        finally:
            for o, r, v in was:
                o.hide_render, o.hide_viewport = r, v
            if obs:
                bpy.context.view_layer.update()

    # ---------- people
    def person(self, name, color, at, facing=0.0, pose="stand", height=1.72, build=1.0, marks=(), legs=None, plate="white", kind="jointed", **joints):
        """color = the top; legs = trousers colour (default: a darker shade of the top); marks: glasses, cap, cap_back,
        hair_curly, hair_long, shorts (bare shins). plate = colour of the chest plate that marks the front.
        kind="jointed": a mannequin with limbs you pose (stills, key poses). kind="capsule": a body and a head with a face plate,
        no limbs; it only slides, turns and shrinks (for a previz clip used as a reference video, where stiff limbs would be copied).
        Stage(stand_ins=True) makes everyone a capsule."""
        p = (Capsule if kind == "capsule" or self.stand_ins else Person)(self, name, color, height, build, marks, legs, plate)
        self.people[name] = p
        p.place(0.0, at, facing, pose, **joints)
        return p

    # ---------- cameras
    def camera(self, name, at, look_at, lens=35.0, hide=(), roll=0.0):
        """hide = names of things left out while this camera shoots (a ceiling, the wall over a door, a lintel, for a shot
        from above); a name also covers everything named <name>_…. roll = degrees turned about the line of sight; for a camera
        looking straight down, 0 puts north (+Y) at the top of the frame and 90 puts west there (north on the right)."""
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        cam.data.lens, cam.data.sensor_width, cam.data.clip_start = lens, 36.0, 0.05
        self.scene.collection.objects.link(cam)
        self.cams[name] = {"obj": cam, "keys": [], "hide": list(hide), "roll": roll}
        self.camera_key(name, 0.0, at, look_at)
        return cam

    def camera_key(self, name, t, at, look_at, roll=None):
        """Where the camera is at time t; between two keys it moves at constant speed."""
        c = self.cams[name]
        cam, roll = c["obj"], c["roll"] if roll is None else roll
        cam.location = at
        q = (Vector(look_at) - Vector(at)).to_track_quat("-Z", "Y") @ Quaternion((0, 0, 1), math.radians(roll))
        cam.rotation_euler = q.to_euler("XYZ", cam.rotation_euler)
        f = self.frame(t)
        key(cam, "location", f)
        key(cam, "rotation_euler", f)
        c["keys"].append((t, tuple(at), tuple(look_at)))

    def camera_move(self, name, t0, t1, at, look_at, steps=12):
        """Move the camera from where it is at t0 to (at, look_at) by t1, easing in and out (camera_key alone moves at constant speed)."""
        _, a0, l0 = max((k for k in self.cams[name]["keys"] if k[0] <= t0), key=lambda k: k[0])
        self.camera_key(name, t0, a0, l0)
        for i in range(1, steps + 1):
            k = i / steps
            e = k * k * (3 - 2 * k)
            self.camera_key(name, t0 + (t1 - t0) * k, tuple(a + (b - a) * e for a, b in zip(a0, at)), tuple(a + (b - a) * e for a, b in zip(l0, look_at)))

    # ---------- output
    def still(self, cam, path, t=0.0):
        self.linear()
        self._check_doors()
        self.scene.camera = self.cams[cam]["obj"]
        self.scene.frame_set(self.frame(t))
        self.scene.render.filepath = str(path)
        with self._hidden(cam):
            bpy.ops.render.render(write_still=True)
        return Path(path)

    def clip(self, cam, path, t0=0.0, t1=5.0, crf=16, samples=None, keep_frames=False, scale=1.0):
        """Render [t0, t1) from one camera to an mp4. The PNG frames go to a folder next to it, removed afterwards unless keep_frames.
        scale = share of the frame size to render at; the mp4 is scaled back up to the full size. The mp4 appears only when
        it is complete (an interrupted clip leaves no file, so previz(missing=True) renders it again)."""
        self.linear()
        self._check_doors()
        path = Path(path)
        frames = path.with_suffix("")
        frames.mkdir(parents=True, exist_ok=True)
        s = self.scene
        s.camera, s.frame_start, s.frame_end = self.cams[cam]["obj"], self.frame(t0), self.frame(t1) - 1
        s.render.filepath = str(frames / "f_")
        old, pct = s.eevee.taa_render_samples, s.render.resolution_percentage
        up = ["-vf", f"scale={round(s.render.resolution_x * pct / 200) * 2}:{round(s.render.resolution_y * pct / 200) * 2}"] if scale != 1.0 else []
        if samples:
            s.eevee.taa_render_samples = samples
        s.render.resolution_percentage = max(1, round(pct * scale))
        try:
            with self._hidden(cam):
                bpy.ops.render.render(animation=True)
        finally:
            s.eevee.taa_render_samples, s.render.resolution_percentage = old, pct
        tmp = path.with_suffix(".tmp.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(self.fps), "-start_number", str(s.frame_start), "-i",
                        str(frames / "f_%04d.png"), *up, "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(tmp)], check=True)
        tmp.replace(path)
        if not keep_frames:
            shutil.rmtree(frames, ignore_errors=True)
        return path

    def save(self, path):
        self.linear()
        bpy.ops.wm.save_as_mainfile(filepath=str(path))

    # ---------- timing
    def retime(self, speed):
        """Everything `speed` times as fast (0.8 = slower): every key at time t moves to t / speed — people, cameras, doors,
        props, and what timeline() lists. Call it after the last key. Shot times scale the same way (t0 / speed, t1 / speed); to
        keep a shot as long, key more action (people starting further back). A faster walk also steps faster and reads as a
        brisk walk; for unhurried steps at the same speed give walk() a lower cadence instead."""
        k = 1.0 / speed
        for act in bpy.data.actions:
            for layer in act.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            for kp in fc.keyframe_points:
                                for v in (kp.co, kp.handle_left, kp.handle_right):
                                    v[0] = 1 + (v[0] - 1) * k            # frame(t) = t * fps + 1
                            fc.update()
        for c in self.cams.values():
            c["keys"] = [(t * k, a, look) for t, a, look in c["keys"]]
        for p in self.people.values():
            p.log["keys"] = [(t * k, pose) for t, pose in p.log["keys"]]
            p.log["walks"] = [{**w, "from": w["from"] * k, "to": w["to"] * k, "speed": w["speed"] * speed,
                               "cadence": w["cadence"] and w["cadence"] * speed} for w in p.log["walks"]]
            p.log["events"] = [(t * k, what) for t, what in p.log["events"]]
        return self

    def timeline(self):
        """When things happen in the previz, to hold the film against: for each person the walks (from, to, metres, m/s, steps a
        second, metres a step), every changeover of the feet (the legs pass each other, half-way between a walk_a and a walk_b
        key), every key pose with its time (walk poses left out), and the beats strike() and sit_down() keyed.
        warnings: walks keyed outside 1.4–1.8 steps a second. Times are those of the frames the keys fall on."""
        people, warnings = {}, []
        for p in self.people.values():
            changes, poses = key_beats(p.log["keys"])
            walks = [{k: round(v, 3) if isinstance(v, float) else v for k, v in w.items()} for w in p.log["walks"]]
            people[p.name] = {"walks": walks, "changeovers": changes if isinstance(p, Person) else [], "poses": poses,
                              "events": sorted((round(t, 3), w) for t, w in p.log["events"])}
            for w in walks:
                if w["cadence"] and w["metres"] > 0.05 and not CADENCE[0] - 0.01 <= w["cadence"] <= CADENCE[1] + 0.01:
                    warnings.append(f"{p.name} {w['from']:.2f}–{w['to']:.2f} 秒：每秒 {w['cadence']:.2f} 步、步长 {w['step']:.2f} 米，"
                                    f"不在每秒 {CADENCE[0]}–{CADENCE[1]} 步里（多了步子碎；少的没测过）")
        return {"people": people, "warnings": warnings}

    def _pose_at(self, p, t):
        """The pose a person was last keyed with at or before time t."""
        name = "stand"
        for tk, ps in sorted(dict(p.log["keys"]).items()):
            if tk <= t + 1e-6:
                name = ps
        return name

    def check_bodies(self, step=0.25, t0=0.0, t1=None):
        """Whether the jointed mannequins move like bodies, every `step` seconds and at every pose key from t0 to t1 (default:
        the last pose key). Mainly joints outside what a person can do (ROM: an elbow or knee bent backwards or folded too far,
        an arm swung back over the shoulder, a hip or thigh turned too far, the head turned or bent too far, the waist twisted
        too far, also in between two keys). Also a hand or foot sent (hands=, feet=) more than 5 cm beyond reach or to a point
        behind the back (sitting with the back to a door, the hand cannot pass a bowl through the door a metre behind: the
        person turns round first, or the bowl goes where the hand can get to it), the head or chest inside furniture, walls,
        doors or steps, and two people in the same place. Not checked: feet a few centimetres off or into the floor, knees
        against a sofa being carried, the trunk tipped to lie down. Capsule stand-ins are left out.
        Returns one line per problem and span of time, with the worst value; empty when nothing is found. It only catches
        what can be measured: look at pose_sheet() too."""
        people = [p for p in self.people.values() if isinstance(p, Person)]
        if not people:
            return []
        self.linear()
        if t1 is None:
            t1 = max([t for p in people for t in p.log["posed"]] + [t0])
        times = sorted({round(t0 + i * step, 4) for i in range(int((t1 - t0) / step + 1e-6) + 1)}
                       | {round(t, 4) for p in people for t in p.log["posed"] if t0 - 1e-6 <= t <= t1 + 1e-6})
        found = {}                                       # (who, what) -> [(time, how bad, text)]

        def note(who, what, t, bad, text):
            found.setdefault((who, what), []).append((t, bad, text))

        for t in times:
            self.at_time(t)
            pts = {}
            for p in people:
                for k, v in p.angles().items():
                    base, sd = (k[:-2], k[-1]) if k[-2:] in ("_l", "_r") else (k, "")
                    if base not in ROM:
                        continue
                    lo, hi = ROM[base]
                    if not lo - 0.5 <= v <= hi + 0.5:
                        side = {"l": "左", "r": "右"}.get(sd, "")
                        how = "往反方向弯了" if base in ("elbow", "knee") and v < lo else "超出了人能做到的范围"
                        note(p.name, k, t, max(lo - v, v - hi), f"{side}{JOINT_ZH[base]} {v:.0f}°，{how}（人能做到 {lo}–{hi}°）")
                pts[p.name] = bp = p.body_points()
                for part in ("头", "胸口"):
                    hit = self._inside(bp[part])
                    if hit:
                        note(p.name, f"in-{part}-{hit[0].name}", t, 0, f"{part}穿进了{self._label(hit[0])}")
            for a, b in itertools.combinations(people, 2):
                pa, pb = pts[a.name], pts[b.name]
                dc, dp = (pa["胸口"] - pb["胸口"]).length, (pa["胯"] - pb["胯"]).length
                if min(dc, dp) < 0.3:
                    note(f"{a.name}和{b.name}", "overlap", t, 0.3 - min(dc, dp),
                         f"身体叠在一起（{'胸口' if dc < dp else '胯'}相距 {min(dc, dp) * 100:.0f} 厘米）")
        for p in people:                         # hands and feet sent where the limb cannot get to
            for t, limb, sd, far, behind, length in p.log["reach"]:
                if not t0 - 1e-6 <= t <= t1 + 1e-6:
                    continue
                side = "左" if sd == "l" else "右"
                if far > 0.05:
                    note(p.name, f"far-{limb}{sd}", t, far, f"{side}{limb}够不着目标点，最多差 {far * 100:.0f} 厘米（伸直也只有 {length * 100:.0f} 厘米）")
                if behind > 0:
                    note(p.name, f"behind-{limb}{sd}", t, behind, f"{side}{limb}的目标点在背后，最远 {behind * 100:.0f} 厘米：人得先转过身来，或者把东西放到身前")
        for key in found:                        # reach notes were added after the frame loop: keep each list in time order
            found[key].sort()
        out = []
        for (who, _what), hits in found.items():
            spans, cur = [], [hits[0]]
            for h in hits[1:]:
                if h[0] - cur[-1][0] <= max(step * 1.5, 1.0) + 1e-6:
                    cur.append(h)
                else:
                    spans.append(cur)
                    cur = [h]
            spans.append(cur)
            for s in spans:
                worst = max(s, key=lambda h: h[1])
                when = f"{s[0][0]:.2f} 秒" if len(s) == 1 else f"{s[0][0]:.2f}–{s[-1][0]:.2f} 秒"
                out.append((s[0][0], f"【要改】{who} {when}：{worst[2]}"))
        return [line for _t, line in sorted(out)]

    def pose_sheet(self, path, people=None, times=None, tile=(260, 360), per_row=3):
        """One picture for looking at the jointed mannequins' poses: for each person (default: all jointed ones) and each time
        (default: every time a pose was keyed; a walk shows its first step only), the body alone from the front and from its
        right side, labelled with who, the seconds and the pose. Look at every tile and write one line: what the person is
        doing, and whether a body would be like that (weight over the feet, which way elbows and knees bend, where the hands
        are, two people in the very same pose). check_bodies() catches what can be measured; this is for the rest.
        Returns [(person, time, pose)] in tile order."""
        from PIL import Image, ImageDraw, ImageFont
        path = Path(path)
        tmp = path.parent / f".{path.stem}_tiles"
        tmp.mkdir(parents=True, exist_ok=True)
        entries = []
        for n in people or [n for n, p in self.people.items() if isinstance(p, Person)]:
            p = self.people[n]
            if times is not None:
                ts = sorted(times)
            else:
                ts, prev = [], None
                for tk in sorted({round(t, 4) for t in p.log["posed"]}):
                    ps = self._pose_at(p, tk)
                    if not (ps in ("walk_a", "walk_b") and prev in ("walk_a", "walk_b")):
                        ts.append(tk)
                    prev = ps
            entries += [(n, t, self._pose_at(p, t)) for t in ts]
        s = self.scene
        keep = (s.render.resolution_x, s.render.resolution_y, s.render.filepath, s.camera, s.eevee.taa_render_samples)
        cam = bpy.data.objects.new("_pose_cam", bpy.data.cameras.new("_pose_cam"))
        cam.data.lens, cam.data.sensor_width = 50.0, 36.0
        s.collection.objects.link(cam)
        s.render.resolution_x, s.render.resolution_y = tile
        s.eevee.taa_render_samples = 8
        s.camera = cam
        self.linear()
        files = []
        try:
            for n, t, _ps in entries:
                p = self.people[n]
                others = [o for o in s.objects if o.type == "MESH" and o not in p.objs and not o.hide_render]
                for o in others:
                    o.hide_render = True
                try:
                    self.at_time(t)
                    lm = p.landmarks()
                    mid, f = (lm["head_top"] + lm["feet"]) / 2, p.forward()
                    for view, way in (("front", f), ("side", Vector((f.y, -f.x, 0)))):
                        cam.location = mid + way * 3.4 * p.root.scale.z
                        cam.rotation_euler = (mid - cam.location).to_track_quat("-Z", "Y").to_euler()
                        files.append(tmp / f"{len(files):03d}_{view}.png")
                        s.render.filepath = str(files[-1])
                        bpy.ops.render.render(write_still=True)
                finally:
                    for o in others:
                        o.hide_render = False
        finally:
            s.render.resolution_x, s.render.resolution_y, s.render.filepath, s.camera, s.eevee.taa_render_samples = keep
            bpy.data.objects.remove(cam)
        fp = plan_font()                                                # same font as plan(); none: English labels
        font = ImageFont.truetype(fp, 17) if fp else ImageFont.load_default()
        w, h, lab, gutter = tile[0], tile[1], 28, 14
        rows = max(1, math.ceil(len(entries) / per_row))
        sheet = Image.new("RGB", (per_row * 2 * w + (per_row - 1) * gutter, rows * (h + lab)), "white")
        draw = ImageDraw.Draw(sheet)
        for i, (n, t, ps) in enumerate(entries):
            r, c = divmod(i, per_row)
            x0, y0 = c * (2 * w + gutter), r * (h + lab)
            for k in range(2):
                sheet.paste(Image.open(files[2 * i + k]).convert("RGB"), (x0 + k * w, y0 + lab))
            draw.text((x0 + 6, y0 + 5), f"{n}  {t:.2f} 秒  {ps}   正面 | 右侧" if fp else f"{n}  {t:.2f} s  {ps}   front | right",
                      fill="black", font=font)
        sheet.save(path)
        for fp in files:
            fp.unlink()
        tmp.rmdir()
        return entries

    def _keyed(self, t):
        """The time of the frame a key at time t falls on."""
        return (self.frame(t) - 1) / self.fps

    # ---------- what each camera sees
    def report(self, cam, t=0.0) -> dict:
        self.linear()
        self._check_doors()
        s = self.scene
        s.camera = c = self.cams[cam]["obj"]
        s.frame_set(self.frame(t))
        with self._hidden(cam):
            return self._report(cam, c, t)

    def _report(self, cam, c, t):
        s = self.scene
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        cpos = c.matrix_world.translation
        fwd = c.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        pitch = math.degrees(math.asin(max(-1, min(1, fwd.z))))
        out = {"camera": cam, "t": t, "height_m": round(cpos.z, 2), "pitch_deg": round(pitch, 1), "lens_mm": c.data.lens,
               "angle": "俯拍" if pitch < -12 else "仰拍" if pitch > 12 else "平视", "people": [], "warnings": [], "notes": []}
        near, nearest = [], 9.9                               # something right in front of the lens?
        q = c.matrix_world.to_quaternion()
        for u in (-0.35, -0.17, 0, 0.17, 0.35):
            for v in (-0.2, 0, 0.2):
                hit, loc, ob = self._ray(dg, cpos, (q @ Vector((u, v, -1))).normalized(), 0.35)
                if hit:
                    near.append(self._label(ob))
                    nearest = min(nearest, (loc - cpos).length)
        solid = self._inside(cpos)
        if solid:
            ob, kind = solid
            out["warnings"].append(f"镜头在{self._label(ob)}里面，画面里只有它的内壁：把机位挪出来" +
                                   ("（楼梯默认是实心的，要把机位放到一段楼梯底下，那段写 stairs(…, solid=False)）" if kind == "step" else ""))
        elif len(near) >= 4:
            out["warnings"].append(f"镜头贴着或钻进了{max(set(near), key=near.count)}（离镜头 {nearest:.2f} 米），画面被挡住")
        inside = lambda q: 0 <= q.x <= 1 and 0 <= q.y <= 1 and q.z > 0
        for p in self.people.values():
            pts = p.landmarks()
            uv = {k: world_to_camera_view(s, c, v) for k, v in pts.items()}
            head, feet = uv["head_top"], uv["feet"]
            span = head.y - feet.y
            lo = 0.0 if span <= 0 else max(0.0, (0 - feet.y) / span)       # share of the body cut off at the bottom
            hi = 1.0 if span <= 0 else min(1.0, (1 - feet.y) / span)
            size = ("不在画面里" if not any(inside(q) for q in uv.values()) else
                    "全身" if lo <= 0.04 else "膝盖以上" if lo < 0.38 else "腰以上" if lo < 0.58 else "胸以上" if lo < 0.8 else "头部特写")
            to_cam = (cpos - pts["chest"])
            to_cam.z = 0
            ang = math.degrees(p.forward().xy.angle_signed(to_cam.xy)) if to_cam.length > 1e-6 else 0.0
            a = abs(ang)
            ahead = world_to_camera_view(s, c, pts["chest"] + p.forward() * 0.5)
            side = "画面左" if ahead.x < uv["chest"].x else "画面右"
            facing = ("正对镜头" if a < 25 else f"朝镜头、偏向{side}" if a < 65 else f"侧身朝{side}" if a < 115
                      else f"背朝镜头、偏向{side}" if a < 155 else "背对镜头")
            seen, behind = [], []
            for k in ("head", "chest", "pelvis"):
                d = pts[k] - cpos
                hit, _l, ob = self._ray(dg, cpos, d.normalized(), d.length - 0.12)
                ok = (not hit) or ob in p.objs
                seen.append(ok)
                if not ok:
                    behind.append(self._label(ob))
            hidden = size != "不在画面里" and not any(seen)
            dist = round((pts["chest"] - cpos).length, 2)
            if size != "不在画面里" and not hidden and (hi < 0.9 or not inside(uv["head"])):
                out["warnings"].append(f"{p.name}的头出画了（{size}，离镜头 {dist} 米）")
            frame_h = round(max(0.0, (min(hi, 1) - lo) * span), 3) if pitch > -60 else 0.0     # looking straight down there is no height
            out["people"].append({
                "name": p.name, "color": p.color, "x": round(uv["chest"].x, 2), "head_y": round(1 - head.y, 2), "feet_y": round(1 - feet.y, 2),
                "body_height_in_frame": round(frame_h, 2), "frame_h": frame_h, "shot": size, "facing": facing,
                "distance_m": dist, "pose": p.pose_name, "hidden": hidden, "behind": behind[1] if len(behind) > 1 else behind[0] if behind else "",
                "blocked": [k for k, v in zip(("头", "胸", "腰"), seen) if not v]})
            if size != "不在画面里" and not hidden and 0 < frame_h < 0.10:
                out["notes"].append(f"{p.name}只占画面高 {frame_h * 100:.0f}%：出关键帧时小人常被画大，出图后量一下")
        out["people"].sort(key=lambda r: r["x"])
        right = c.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        out["props"] = []
        for it in self.items:
            if it["kind"] != "sofa":
                continue
            ob = it["obj"]
            mid = ob.matrix_world @ Vector((0, 0, it["size"][2] / 2))
            uv = world_to_camera_view(s, c, mid)
            long_axis = ob.matrix_world.to_quaternion() @ Vector((1, 0, 0))
            front = ob.matrix_world.to_quaternion() @ Vector((0, 1, 0))
            across = abs(long_axis.dot(right))
            toward = front.dot((cpos - mid).normalized())
            out["props"].append({"name": it["name"], "x": round(uv.x, 2), "y": round(1 - uv.y, 2), "distance_m": round((mid - cpos).length, 2),
                                 "lies": "横在画面里（长边左右方向）" if across > 0.8 else "长边朝纵深方向" if across < 0.45 else "斜着",
                                 "front": "正面朝镜头" if toward > 0.6 else "背面朝镜头" if toward < -0.6 else "侧面朝镜头",
                                 "tilt_deg": round(math.degrees(math.asin(max(-1, min(1, long_axis.z)))), 0)})
        out["doors"] = []
        for d in self.doors:
            ang = d.angle()
            h = Vector(d.hinge) + Vector((0, 0, d.height / 2))
            closed_edge = h + heading_vec(d.heading) * d.width
            free = d.root.matrix_world @ Vector((0, d.width, d.height / 2))
            uh, uf, uc = (world_to_camera_view(s, c, v) for v in (h, free, closed_edge))
            swing = d.sign if d.sign is not None else (1 if max(d.angles, key=abs, default=0) >= 0 else -1)
            f = heading_vec(d.heading)
            left = Vector((-f.y, f.x, 0)) * swing
            toward = left.dot(Vector((cpos.x - h.x, cpos.y - h.y, 0))) > 0
            state = "关着" if abs(ang) < 3 else f"开着约 {abs(ang):.0f} 度"
            out["doors"].append({"name": d.name, "angle": abs(ang), "state": state, "in_frame": inside(uh) or inside(uf),
                                 "hinge_side": "左" if uh.x < uc.x else "右", "opens_toward_camera": toward,
                                 "listed": d.sign is not None or any(abs(x) > 1 for x in d.angles)})
        return out

    def describe(self, cam, t=0.0, props=()) -> str:
        """The layout as sentences for a prompt: who is where in the frame, how big, facing which way; doors that open or are
        open (which side the hinge is on, which way the leaf swings); the sofas and tables in view; and the objects named in
        `props` (where they are in the frame, or that they are out of it)."""
        r = self.report(cam, t)
        where = lambda x: "画面最左边" if x < 0.2 else "画面左侧" if x < 0.42 else "画面中间" if x <= 0.58 else "画面右侧" if x <= 0.8 else "画面最右边"
        lines = [f"机位：{r['angle']}，镜头离地 {r['height_m']} 米，{r['lens_mm']:.0f}mm 镜头。"]
        vis = [p for p in r["people"] if p["shot"] != "不在画面里" and not p["hidden"]]
        order = sorted(vis, key=lambda p: p["distance_m"])
        apart = len(order) > 1 and order[-1]["distance_m"] > order[0]["distance_m"] * 1.2
        for p in r["people"]:
            if p["hidden"]:
                lines.append(f"{p['name']}在{p['behind']}后面，画面里看不见。")
                continue
            if p not in vis:
                continue
            depth = "" if not apart else "，离镜头最近" if p is order[0] else "，离镜头最远" if p is order[-1] else ""
            blocked = f"，{'、'.join(p['blocked'])}被挡住" if p["blocked"] else ""
            tall = f"，占画面高 {p['frame_h'] * 100:.0f}%" if p["frame_h"] else ""
            lines.append(f"{p['name']}在{where(p['x'])}{depth}，{p['shot']}入画{tall}，{p['facing']}{blocked}。")
        for q in r["props"]:
            if not (0 <= q["x"] <= 1 and 0 <= q["y"] <= 1):
                continue
            nearer = [p["name"] for p in vis if p["distance_m"] < q["distance_m"] - 0.3]
            farther = [p["name"] for p in vis if p["distance_m"] > q["distance_m"] + 0.3]
            rel = (f"，在{'、'.join(nearer)}的后面（离镜头更远）" if nearer and not farther else
                   f"，在{'、'.join(farther)}的前面（离镜头更近）" if farther and not nearer else
                   f"，在{'、'.join(nearer)}和{'、'.join(farther)}之间" if nearer and farther else "")
            tilt = f"，一头高一头低，斜了约 {abs(q['tilt_deg']):.0f} 度" if abs(q["tilt_deg"]) > 8 else ""
            lines.append(f"{q['name']}在{where(q['x'])}，{q['lies']}，{q['front']}{tilt}{rel}。")
        for d in r["doors"]:
            if d["listed"] and d["in_frame"]:
                dd = next(x for x in self.doors if x.name == d["name"])
                into = f"（往{dd.into_name}开）" if dd.into_name else ""
                lines.append(f"{d['name']}：合页在画面{d['hinge_side']}边，门扇往{'镜头这边' if d['opens_toward_camera'] else '离镜头远的那边'}开{into}，现在{d['state']}。")
        if props:
            s, c = self.scene, self.cams[cam]["obj"]
            with self._hidden(cam):
                for n in props:
                    pt, _ = self._point(n, "to")
                    uv = world_to_camera_view(s, c, pt)
                    if not (0 <= uv.x <= 1 and 0 <= uv.y <= 1 and uv.z > 0):
                        lines.append(f"{n}不在画面里。")
                        continue
                    block = self.sees(cam, n)
                    vert = "上部" if uv.y > 0.66 else "中部" if uv.y > 0.33 else "下部"
                    lines.append(f"{n}在{where(uv.x)}{vert}，离镜头 {uv.z:.1f} 米" + (f"，被{'、'.join(block)}挡住" if block else "") + "。")
        lines += [f"【要改】{w}" for w in r["warnings"]]
        lines += [f"【留意】{w}" for w in r["notes"]]
        return "\n".join(lines)

    # ---------- floor plan (drawn, not rendered)
    def plan(self, path, t=0.0, scale=None, margin=0.8, title="", region=None, cams=None):
        """Top view at time t: floors, walls, furniture and props where they are at that moment, doors with their swing, people
        with the way they face, cameras with their field of view. Things above everyone's head (ceilings, roofs, lintels) are
        left out. region = (x0, y0, x1, y1) to draw only part of a big set; scale = pixels per metre (default: fits ~2400 px).
        cams = names of the cameras to draw (default all); one shot's plan: cams=[its camera], t = its start."""
        from PIL import Image, ImageDraw, ImageFont
        self.linear()
        self._check_doors()
        self.at_time(t)
        tops = [p.landmarks()["head_top"].z for p in self.people.values()]
        ceiling = max(tops) if tops else 2.2
        polys, frame_pts = [], []
        for it in self.items:
            if it["kind"] in ("door", "ceiling"):
                continue
            ob = it.get("obj")
            if ob is not None:
                if ob.type == "MESH":
                    base = min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box)
                else:
                    base = ob.matrix_world.translation.z
                sc = ob.matrix_world.to_scale()
                at, hd = tuple(ob.matrix_world.translation), -math.degrees(ob.matrix_world.to_euler().z)
            else:
                base, sc, at, hd = (it["at"][2] if len(it["at"]) > 2 else 0.0), Vector((1, 1, 1)), it["at"], it["heading"]
            if base > ceiling - 0.02:
                continue
            w, d = it["size"][0] * sc.x, it["size"][1] * sc.y
            f, r = heading_vec(hd), heading_vec(hd + 90)
            c = Vector((at[0], at[1], 0))
            poly = [c + r * sx * w / 2 + f * sy * d / 2 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            polys.append((it, poly, f, c))
            if it["kind"] in ("floor", "wall", "step"):
                frame_pts += poly
        people = [(p, p.root.matrix_world.translation.copy()) for p in self.people.values()]
        cams = [(n, self.cams[n]["obj"]) for n in (self.cams if cams is None else cams)]
        if region:
            x0, y0, x1, y1 = region
        else:
            pts = (frame_pts or [v for q in polys for v in q[1]]) + [v for _p, v in people] + [o.matrix_world.translation.copy() for _n, o in cams]
            x0, x1 = min(p.x for p in pts) - margin, max(p.x for p in pts) + margin
            y0, y1 = min(p.y for p in pts) - margin, max(p.y for p in pts) + margin
        scale = scale or min(110.0, 2400.0 / max(x1 - x0, y1 - y0))
        within = lambda v: x0 <= v.x <= x1 and y0 <= v.y <= y1
        px = lambda v: ((v.x - x0) * scale, (y1 - v.y) * scale)
        img = Image.new("RGB", (int((x1 - x0) * scale), int((y1 - y0) * scale) + 30), (245, 245, 245))
        dr = ImageDraw.Draw(img)
        fp = plan_font()
        zh = fp is not None                                             # no Chinese font: the fixed labels are drawn in English
        font = ImageFont.truetype(fp, 15) if zh else ImageFont.load_default()
        rgb = lambda col: tuple(int(255 * min(1, v ** (1 / 2.2))) for v in (COLORS[col] if isinstance(col, str) else col))
        order = {"floor": 0, "step": 1, "wall": 2, "box": 3, "sofa": 3}
        for it, poly, f, c in sorted(polys, key=lambda q: order.get(q[0]["kind"], 3)):
            fill = {"floor": (225, 225, 225), "step": (205, 205, 205), "wall": (60, 60, 60)}.get(it["kind"], rgb(it["color"]))
            dr.polygon([px(v) for v in poly], fill=fill, outline=(120, 120, 120))
            if it["kind"] in ("sofa", "chair"):
                dr.line([px(c), px(c + f * 0.6)], fill=(255, 255, 255), width=3)
            if it["kind"] == "sofa":
                dr.text(px(c + Vector((0.1, 0.25, 0))), it["name"], fill=(255, 255, 255), font=font)
        for d in self.doors:                                            # the leaf where it is now (thick) and where it is closed (thin)
            h = Vector(d.hinge)
            closed = h + heading_vec(d.heading) * d.width
            now = d.root.matrix_world @ Vector((0, d.width, 0))
            dr.line([px(h), px(closed)], fill=(150, 110, 80), width=1)
            dr.line([px(h), px(now)], fill=rgb("door"), width=5)
            if d.into_name:
                dr.text(px(now), f"往{d.into_name}开" if zh else f"opens into {d.into_name}", fill=(120, 70, 30), font=font)
        rad = max(0.22 * scale, 5)
        for p, c in people:
            if not within(c):
                continue
            cx, cy = px(c)
            dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=rgb(p.color), outline=(0, 0, 0))
            tip = px(c + p.forward() * max(0.55, 14 / scale))
            dr.line([(cx, cy), tip], fill=(0, 0, 0), width=4)
            dr.text((cx + rad + 3, cy - rad - 6), p.name, fill=(0, 0, 0), font=font)
        for name, ob in cams:
            pos = ob.matrix_world.translation
            if not within(pos):
                continue
            fw = ob.matrix_world.to_quaternion() @ Vector((0, 0, -1))
            fw.z = 0
            if fw.length < 1e-6:                                         # looking straight down
                fw = ob.matrix_world.to_quaternion() @ Vector((0, 1, 0))
                fw.z = 0
            fw.normalize()
            half = math.atan(18 / ob.data.lens)
            side = Vector((fw.y, -fw.x, 0))
            for sgn in (-1, 1):
                dr.line([px(pos), px(pos + (fw * math.cos(half) + side * sgn * math.sin(half)) * max(2.2, 60 / scale))], fill=(200, 60, 0), width=2)
            cx, cy = px(pos)
            dr.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(200, 60, 0))
            dr.text((cx + 8, cy + 6), f"机位 {name}" if zh else f"cam {name}", fill=(200, 60, 0), font=font)
        step = 1 if scale >= 20 else 10 if scale >= 4 else 50
        legend = (f"{title}  北(+Y)朝上，刻度每 {step} 米，t = {t:.1f} s" if zh else
                  f"{title}  north (+Y) up, a tick every {step} m, t = {t:.1f} s")
        dr.text((8, img.height - 24), legend, fill=(60, 60, 60), font=font)
        for gx in range(math.ceil(x0 / step) * step, math.floor(x1) + 1, step):
            dr.line([px(Vector((gx, y0, 0))), px(Vector((gx, y0 + 6 / scale, 0)))], fill=(120, 120, 120))
        for gy in range(math.ceil(y0 / step) * step, math.floor(y1) + 1, step):
            dr.line([px(Vector((x0, gy, 0))), px(Vector((x0 + 6 / scale, gy, 0)))], fill=(120, 120, 120))
        img.save(path)
        return Path(path)


class Capsule:
    """A stand-in without limbs: a rounded body, a head, a nose and a face plate that show the front. Same calls as Person;
    joint angles are ignored. A pose only changes its height: LOW below, or the pose's own "low" in POSES, or place(…, low=0.6).
    marks: glasses, cap, cap_back, hair_curly, hair_long."""
    LOW = {"sit": 0.72, "sit_floor": 0.5, "crouch": 0.62, "lie": 0.2}

    def __init__(self, stage, name, color, height, build, marks, legs=None, plate="white"):
        self.stage, self.name, self.color, self.pose_name, self.height = stage, name, color, "stand", height
        self.objs: set = set()
        self.log = {"keys": [], "walks": [], "events": []}       # for Stage.timeline()
        st = stage
        self.root = st._add(name, None, color)
        self.root.scale = (build, build, 1.0)
        self.body = st._add(f"{name}_body", None, color, self.root)
        new = lambda n, mesh, col: self.objs.add(st._add(f"{name}_{n}", mesh, col, self.body)) or None
        h = height
        new("trunk", _mesh("trunk", lambda bm: (bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.2, radius2=0.2, depth=h - 0.42),
                                                bmesh.ops.scale(bm, vec=(1, 0.72, 1), verts=bm.verts),
                                                bmesh.ops.translate(bm, vec=(0, 0, (h - 0.42) / 2), verts=bm.verts)), True), color)
        new("shoulders", _mesh("sh", lambda bm: (bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=0.2),
                                                 bmesh.ops.scale(bm, vec=(1, 0.72, 0.5), verts=bm.verts),
                                                 bmesh.ops.translate(bm, vec=(0, 0, h - 0.42), verts=bm.verts)), True), color)
        new("head", _mesh("head", lambda bm: (bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=12, radius=0.11),
                                              bmesh.ops.scale(bm, vec=(0.9, 1.0, 1.15), verts=bm.verts),
                                              bmesh.ops.translate(bm, vec=(0, 0.01, h - 0.13), verts=bm.verts)), True), "skin")
        new("face", _mesh("face", lambda bm: _box(bm, (0.13, 0.02, 0.11), (0, 0.105, h - 0.125))), plate)
        new("nose", _mesh("nose", lambda bm: _box(bm, (0.03, 0.06, 0.03), (0, 0.13, h - 0.14))), "black")
        new("plate", _mesh("plate", lambda bm: _box(bm, (0.2, 0.02, 0.2), (0, 0.15, h - 0.62))), plate)
        if "cap" in marks or "cap_back" in marks:
            new("cap", _mesh("cap", lambda bm: _box(bm, (0.2, 0.2, 0.05), (0, 0.0, h - 0.02))), "red")
            sign = -1 if "cap_back" in marks else 1
            new("brim", _mesh("brim", lambda bm: _box(bm, (0.15, 0.1, 0.012), (0, sign * 0.14, h - 0.035))), "red")
        if "glasses" in marks:
            new("glasses", _mesh("glasses", lambda bm: _box(bm, (0.17, 0.02, 0.04), (0, 0.118, h - 0.11))), "black")
        if "hair_curly" in marks or "hair_long" in marks:
            new("hair", _mesh("hair", lambda bm: _box(bm, (0.24, 0.1, 0.3 if "hair_long" in marks else 0.16), (0, -0.09, h - (0.3 if "hair_long" in marks else 0.16)))), "hair")

    def forward(self):
        v = self.root.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        v.z = 0
        return v.normalized()

    def landmarks(self):
        bpy.context.view_layer.update()
        mw, top = self.body.matrix_world, self.height
        base = self.root.matrix_world.translation.copy()
        return {"head_top": mw @ Vector((0, 0, top)), "head": mw @ Vector((0, 0, top - 0.13)), "eyes": mw @ Vector((0, 0.1, top - 0.12)),
                "chest": mw @ Vector((0, 0, top - 0.5)), "pelvis": mw @ Vector((0, 0, top * 0.52)), "feet": base}

    def reach(self, side, target, length=0.33):
        return {}

    def point(self, where):
        bpy.context.view_layer.update()
        z = {"mouth": self.height - 0.19, "lap": self.height * 0.5}.get(where, self.height * 0.55)
        return self.body.matrix_world @ Vector((0, 0.2, z))

    _heading = lambda self, facing, at: Person._heading(self, facing, at)

    def place(self, t, at, facing=None, pose=None, hands=None, feet=None, low=None, **joints):
        st, f = self.stage, self.stage.frame(t)
        st.scene.frame_set(f)
        z = at[2] if len(at) > 2 else st.ground(at[0], at[1])
        self.root.location = (at[0], at[1], z)
        if facing is not None:
            bpy.context.view_layer.update()
            new = -math.radians(self._heading(facing, at))
            old = self.root.rotation_euler.z
            self.root.rotation_euler.z = old + (new - old + math.pi) % (2 * math.pi) - math.pi if self.root.animation_data else new
        if pose is not None:
            self.log["keys"].append((st._keyed(t), pose))
        if pose is not None or low is not None:
            self.pose_name = pose or self.pose_name
            k = low if low is not None else self.LOW.get(self.pose_name, POSES.get(self.pose_name, {}).get("low", 1.0))
            self.body.scale = (1, 1, k)
            self.body.location.z = joints.get("seat", 0.0) if self.pose_name == "sit" else 0.0
            key(self.body, "scale", f)
            key(self.body, "location", f)
        key(self.root, "location", f)
        key(self.root, "rotation_euler", f)
        return self

    def walk(self, t0, t1, to, stride_s=None, facing=None, end_pose="stand", ease=True, cadence=None, **joints):
        """Slide in a straight line from where it stands at t0 to `to`, following the ground; eases in and out unless
        ease=False (constant speed, for a shot that starts and ends in mid-walk). It has no feet: stride_s and cadence are
        accepted so the same scene code runs with either kind of figure, and do nothing."""
        st = self.stage
        st.scene.frame_set(st.frame(t0))
        bpy.context.view_layer.update()
        a, b = self.root.matrix_world.translation.copy(), Vector((to[0], to[1], 0))
        head = facing if facing is not None else (b.x, b.y) if (b.xy - a.xy).length > 1e-3 else None
        n = max(2, round((t1 - t0) / 0.25))
        for i in range(n + 1):
            k = i / n
            e = k * k * (3 - 2 * k) if ease else k        # smoothstep: gentle start and stop, as a person walks
            p = a.lerp(b, e)
            self.place(t0 + (t1 - t0) * k, (p.x, p.y), head if i == 0 or facing is not None else None, end_pose if i == n else "stand")
        d = (b.xy - a.xy).length
        self.log["walks"].append({"from": st._keyed(t0), "to": st._keyed(t1), "metres": d, "speed": d / (t1 - t0), "cadence": None, "step": None})
        return self

    strike = lambda self, *a, **k: Person.strike(self, *a, **k)         # only the height changes (duck, hurt_b …)
    sit_down = lambda self, *a, **k: Person.sit_down(self, *a, **k)


class Door:
    def __init__(self, stage, name, root, hinge, heading, width, height, lock, sign=None, into_name=""):
        self.stage, self.name, self.root, self.hinge, self.heading = stage, name, root, hinge, heading
        self.width, self.height, self.lock, self.sign, self.into_name = width, height, lock, sign, into_name
        self.angles = []
        self.looked_up = False            # the height came from ground() (hinge given as (x, y)): Stage._check_doors holds it against the set

    def set(self, t, angle):
        """Key the leaf at time t: 0 = closed, 90 = wide open (positive = to the left of the closed leaf's direction, seen from above)."""
        self.root.rotation_euler = (0, 0, -math.radians(self.heading) + math.radians(angle))
        key(self.root, "rotation_euler", self.stage.frame(t))
        self.angles.append(angle)
        return self

    def open(self, t, degrees):
        """Key the leaf at time t, opened `degrees` toward the side given by door(…, into=…)."""
        if self.sign is None:
            raise ValueError(f"door {self.name}: give door(…, into=(x, y)) to say which way it opens, or use set() with a signed angle")
        return self.set(t, self.sign * degrees)

    def angle(self) -> float:
        """How far the leaf is open right now, in degrees (signed like set())."""
        a = math.degrees(self.root.rotation_euler.z) + self.heading
        return (a + 180) % 360 - 180

    def lock_point(self, side=1, out=0.06):
        """World position just in front of the lock: side=1 on the face to the right of `heading`, side=-1 on the other face."""
        bpy.context.view_layer.update()
        return tuple(self.root.matrix_world @ Vector((side * out, self.width - 0.07, self.lock)))

    def attach(self, name, size, local, color="prop"):
        """A block fixed on the leaf, so it swings with it (a sign, a peephole, a poster). size = (thickness, along the leaf, height);
        local = (out from the leaf's middle: + is the face to the right of the door's heading, along the leaf from the hinge, height)."""
        return self.stage._add(name, _mesh(name, lambda bm: _box(bm, size, local)), color, parent=self.root)


class Person:
    """A jointed mannequin 1.80 m tall before scaling; nose, chest plate and feet show which way it faces."""

    def __init__(self, stage: Stage, name, color, height, build, marks, legs=None, plate="white"):
        self.stage, self.name, self.color, self.pose_name = stage, name, color, "stand"
        self.objs: set = set()
        self.seat_h, self.joints = None, {}
        self.log = {"keys": [], "walks": [], "events": [], "posed": [], "reach": []}   # for timeline(), check_bodies(), pose_sheet()
        st, dark = stage, legs or tuple(v * 0.55 for v in (COLORS[color] if isinstance(color, str) else color))
        shin = "skin" if "shorts" in marks else dark
        new = lambda n, mesh, col, parent, loc=(0, 0, 0): self._keep(st._add(f"{name}_{n}", mesh, col, parent, loc))
        self.root = st._add(name, None, color)
        self.root.scale = (height / 1.80 * build, height / 1.80 * build, height / 1.80)
        self.pelvis = st._add(f"{name}_pelvis", None, color, self.root, (0, 0, 0.92))
        j = self.j = {}
        new("hips", _mesh("hips", lambda bm: (_limb(bm, 0.155, 0.15, 0.16, 0.7), bmesh.ops.translate(bm, vec=(0, 0, 0.1), verts=bm.verts)), True), dark, self.pelvis)
        j["spine"] = st._add(f"{name}_spine", None, color, self.pelvis, (0, 0, 0.08))
        new("torso", _mesh("torso", lambda bm: (bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.15, radius2=0.2, depth=0.46),
                                                bmesh.ops.scale(bm, vec=(1, 0.62, 1), verts=bm.verts),
                                                bmesh.ops.translate(bm, vec=(0, 0, 0.23), verts=bm.verts)), True), color, j["spine"])
        new("plate", _mesh("plate", lambda bm: _box(bm, (0.2, 0.02, 0.2), (0, 0.125, 0.32))), plate, j["spine"])
        j["neck"] = st._add(f"{name}_neck", None, color, j["spine"], (0, 0, 0.48))
        new("neckm", _mesh("neckm", lambda bm: (_limb(bm, 0.05, 0.05, 0.1), bmesh.ops.translate(bm, vec=(0, 0, 0.08), verts=bm.verts)), True), "skin", j["neck"])
        new("head", _mesh("head", lambda bm: (bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=12, radius=0.105),
                                              bmesh.ops.scale(bm, vec=(0.9, 1.0, 1.15), verts=bm.verts),
                                              bmesh.ops.translate(bm, vec=(0, 0.01, 0.2), verts=bm.verts)), True), "skin", j["neck"])
        new("nose", _mesh("nose", lambda bm: (bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.028, radius2=0.004, depth=0.07),
                                              bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"), verts=bm.verts),
                                              bmesh.ops.translate(bm, vec=(0, 0.125, 0.19), verts=bm.verts))), dark, j["neck"])
        for x in (-0.04, 0.04):
            new("eye", _mesh("eye", lambda bm, x=x: _box(bm, (0.028, 0.02, 0.022), (x, 0.098, 0.215))), "black", j["neck"])
        if "cap_back" in marks or "cap" in marks:
            new("cap", _mesh("cap", lambda bm: (bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=10, radius=0.112),
                                                bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.02), plane_no=(0, 0, -1), clear_outer=True),
                                                bmesh.ops.translate(bm, vec=(0, 0.01, 0.235), verts=bm.verts)), True), "red", j["neck"])
            sign = -1 if "cap_back" in marks else 1
            new("brim", _mesh("brim", lambda bm: _box(bm, (0.15, 0.1, 0.012), (0, sign * 0.15, 0.255))), "red", j["neck"])
        if "glasses" in marks:
            new("glasses", _mesh("glasses", lambda bm: _box(bm, (0.17, 0.02, 0.05), (0, 0.105, 0.215))), "black", j["neck"])
        if "hair_curly" in marks:
            new("hair", _mesh("hair", lambda bm: (bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=10, radius=0.125),
                                                  bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0.045, 0), plane_no=(0, 1, -0.9), clear_outer=True),
                                                  bmesh.ops.translate(bm, vec=(0, 0.0, 0.225), verts=bm.verts)), True), "hair", j["neck"])
        if "hair_long" in marks:                                      # hair down to the shoulders, behind the head
            new("hairlong", _mesh("hairlong", lambda bm: (bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=10, radius=0.118),
                                                          bmesh.ops.translate(bm, vec=(0, -0.015, 0.215), verts=bm.verts),
                                                          _box(bm, (0.23, 0.09, 0.30), (0, -0.07, 0.10)))), "hair", j["neck"])
        for sd, x in (("l", -1), ("r", 1)):
            j[f"shoulder_{sd}"] = st._add(f"{name}_sh_{sd}", None, color, j["spine"], (x * 0.215, 0, 0.43))
            new(f"uarm_{sd}", _mesh("uarm", lambda bm: _limb(bm, 0.052, 0.043, 0.29), True), color, j[f"shoulder_{sd}"])
            j[f"elbow_{sd}"] = st._add(f"{name}_el_{sd}", None, color, j[f"shoulder_{sd}"], (0, 0, -0.29))
            new(f"farm_{sd}", _mesh("farm", lambda bm: _limb(bm, 0.043, 0.034, 0.26), True), "skin", j[f"elbow_{sd}"])
            new(f"hand_{sd}", _mesh("hand", lambda bm: _box(bm, (0.035, 0.085, 0.11), (0, 0.01, -0.315))), "skin", j[f"elbow_{sd}"])
            j[f"hip_{sd}"] = st._add(f"{name}_hip_{sd}", None, color, self.pelvis, (x * 0.092, 0, 0))
            new(f"thigh_{sd}", _mesh("thigh", lambda bm: _limb(bm, 0.082, 0.06, 0.43), True), dark, j[f"hip_{sd}"])
            j[f"knee_{sd}"] = st._add(f"{name}_knee_{sd}", None, color, j[f"hip_{sd}"], (0, 0, -0.43))
            new(f"shin_{sd}", _mesh("shin", lambda bm: _limb(bm, 0.06, 0.042, 0.42), True), shin, j[f"knee_{sd}"])
            new(f"foot_{sd}", _mesh("foot", lambda bm: _box(bm, (0.095, 0.26, 0.07), (0, 0.07, -0.455))), "black", j[f"knee_{sd}"])

    def _keep(self, ob):
        self.objs.add(ob)
        return ob

    def forward(self) -> Vector:
        v = self.root.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        v.z = 0
        return v.normalized()

    def landmarks(self) -> dict:
        bpy.context.view_layer.update()
        mw, sp, nk = self.root.matrix_world, self.j["spine"].matrix_world, self.j["neck"].matrix_world
        feet = min(((self.j[f"knee_{s}"].matrix_world @ Vector((0, 0.05, -0.49))) for s in "lr"), key=lambda v: v.z)
        base = mw.translation.copy()
        return {"head_top": nk @ Vector((0, 0, 0.33)), "head": nk @ Vector((0, 0, 0.2)), "eyes": nk @ Vector((0, 0.1, 0.215)),
                "chest": sp @ Vector((0, 0, 0.3)), "pelvis": self.pelvis.matrix_world.translation.copy(),
                "feet": Vector((base.x, base.y, min(feet.z, base.z + 0.02)))}

    def reach(self, side, target, length=0.33) -> dict:
        """Shoulder, abduct and elbow angles that put the hand of that side ("l" / "r") on the world point `target`,
        for the body as it is posed right now: call place() first, then place() again with these angles added."""
        bpy.context.view_layer.update()
        sh = self.j[f"shoulder_{side}"]
        p = self.j["spine"].matrix_world.inverted() @ Vector(target) - sh.location   # target seen from the shoulder, in the torso's axes
        beta = math.atan2(-p.x, -p.z) if p.z <= 0 else math.atan2(p.x, p.z)         # swing the arm plane sideways to contain the target
        down = p.dot(Vector((-math.sin(beta), 0, -math.cos(beta))))
        l1, l2 = 0.29, length
        r = max(abs(l1 - l2) + 1e-3, min(math.hypot(p.y, down), l1 + l2 - 1e-3))
        bend = math.acos(max(-1.0, min(1.0, (r * r - l1 * l1 - l2 * l2) / (2 * l1 * l2))))
        lift = math.atan2(p.y, down) - math.atan2(l2 * math.sin(bend), l1 + l2 * math.cos(bend))
        x = -1 if side == "l" else 1
        return {f"shoulder_{side}": math.degrees(lift), f"abduct_{side}": math.degrees(-x * beta), f"elbow_{side}": math.degrees(bend)}

    def reach_gap(self, side, target, length=0.33, foot=False) -> tuple:
        """How a hand (or foot) target sits against the body as it is posed right now, in metres: (how far beyond reach,
        how far behind the back, reach). reach() and reach_foot() still bend the limb toward a target they cannot get to,
        stretched straight; place(hands=…, feet=…) logs this for check_bodies()."""
        bpy.context.view_layer.update()
        k = self.root.scale.z
        if foot:
            d = self.pelvis.matrix_world.inverted() @ Vector(target) - self.j[f"hip_{side}"].location
            return max(0.0, (d.length - 0.92) * k), 0.0, 0.92 * k
        q = self.j["spine"].matrix_world.inverted() @ Vector(target)
        p = q - self.j[f"shoulder_{side}"].location
        return max(0.0, (p.length - 0.29 - length) * k), max(0.0, (-0.12 - q.y) * k), (0.29 + length) * k

    def reach_foot(self, side, target) -> dict:
        """Hip, hip-turn and knee angles that put the foot of that side on the world point `target` (the leg can swing out
        sideways), for the body as it is posed right now: place() first, then place() again with these angles (feet= does both)."""
        bpy.context.view_layer.update()
        hip = self.j[f"hip_{side}"]
        d = self.pelvis.matrix_world.inverted() @ Vector(target) - hip.location         # target seen from the hip, in the pelvis's axes
        l1, l2 = 0.43, 0.49
        r = max(0.05, min(d.length, l1 + l2 - 1e-3))
        dn = d.normalized()
        alpha = math.acos(max(-1, min(1, (l1 * l1 + r * r - l2 * l2) / (2 * l1 * r))))
        gamma = math.acos(max(-1, min(1, (l1 * l1 + l2 * l2 - r * r) / (2 * l1 * l2))))
        flex = math.acos(max(-1, min(1, -dn.z))) + alpha
        lean = self.joints.get("lean", 0.0)
        return {f"hip_{side}": math.degrees(flex) - lean * 0.45, f"hipturn_{side}": math.degrees(math.atan2(-dn.x, dn.y)),
                f"knee_{side}": math.degrees(math.pi - gamma)}

    def point(self, where) -> Vector:
        """World position of a spot on the body: "mouth", "lap", "hand_l", "hand_r"."""
        bpy.context.view_layer.update()
        if where == "mouth":
            return self.j["neck"].matrix_world @ Vector((0, 0.15, 0.14))
        if where == "lap":
            return self.pelvis.matrix_world @ Vector((0, 0.3, 0.16))
        return self.j[f"elbow_{where[-1]}"].matrix_world @ Vector((0, 0.01, -0.31))

    def angles(self) -> dict:
        """The joint angles (degrees, as in POSES) the mannequin has at the current frame, read back from its rotations:
        between two keys they are what Blender interpolates, not what either key asked for."""
        d, j = math.degrees, self.j
        lean = -d(self.pelvis.rotation_euler.x + j["spine"].rotation_euler.x)
        a = {"lean": lean, "twist": d(self.pelvis.rotation_euler.z + j["spine"].rotation_euler.z),
             "head_nod": lean * 0.5 - d(j["neck"].rotation_euler.x), "head_turn": d(j["neck"].rotation_euler.z)}
        for sd, x in (("l", -1), ("r", 1)):
            a[f"shoulder_{sd}"] = d(j[f"shoulder_{sd}"].rotation_euler.x)
            a[f"abduct_{sd}"] = -d(j[f"shoulder_{sd}"].rotation_euler.y) / x
            a[f"elbow_{sd}"] = d(j[f"elbow_{sd}"].rotation_euler.x)
            a[f"hip_{sd}"] = d(j[f"hip_{sd}"].rotation_euler.x) - lean * 0.45
            a[f"hipturn_{sd}"] = d(j[f"hip_{sd}"].rotation_euler.z)
            a[f"knee_{sd}"] = -d(j[f"knee_{sd}"].rotation_euler.x)
        return {k: (v + 180.0) % 360.0 - 180.0 for k, v in a.items()}

    def body_points(self) -> dict:
        """World points check_bodies() tests against the set and the other people: head, chest, hips, knees, elbows, hands."""
        bpy.context.view_layer.update()
        j = self.j
        pts = {"头": j["neck"].matrix_world @ Vector((0, 0.01, 0.2)), "胸口": j["spine"].matrix_world @ Vector((0, 0, 0.3)),
               "胯": self.pelvis.matrix_world @ Vector((0, 0, 0.1))}
        for sd, zh in (("l", "左"), ("r", "右")):
            pts[f"{zh}膝"] = j[f"knee_{sd}"].matrix_world.translation.copy()
            pts[f"{zh}肘"] = j[f"elbow_{sd}"].matrix_world.translation.copy()
            pts[f"{zh}手"] = self.point(f"hand_{sd}")
        return pts

    def _in_torso(self, point) -> bool:
        """Whether a world point is inside this mannequin's own torso (the flattened cone between hips and shoulders)."""
        q = self.j["spine"].matrix_world.inverted_safe() @ point
        if not 0.02 <= q.z <= 0.44:
            return False
        r = 0.15 + 0.05 * q.z / 0.46
        return (q.x / r) ** 2 + (q.y / (0.62 * r)) ** 2 < 0.8

    def _heading(self, facing, at) -> float:
        if isinstance(facing, (int, float)):
            return float(facing)
        if isinstance(facing, str):
            st = self.stage
            tgt = st.people[facing].root.matrix_world.translation if facing in st.people else bpy.data.objects[facing].matrix_world.translation
        else:
            tgt = Vector((*facing[:2], 0))
        return math.degrees(math.atan2(tgt.x - at[0], tgt.y - at[1]))

    def place(self, t, at, facing=None, pose=None, hands=None, feet=None, **joints):
        """Key the mannequin at time t: where it stands (x, y[, z]; z defaults to the ground there), facing, pose.
        hands = {"l": point, "r": point} moves those hands onto world points (a door lock, the edge of a sofa, a bowl);
        feet = {"l": point} does the same for a foot (a foot stretched out to hook something). A seated pose keeps the seat
        height of the last call until the pose changes or a new seat= is given."""
        if hands or feet:
            self.place(t, at, facing, pose, **joints)
            for sd, pt in (hands or {}).items():
                self.log["reach"].append((self.stage._keyed(t), "手", sd, *self.reach_gap(sd, pt)))
                joints.update(self.reach(sd, pt))
            for sd, pt in (feet or {}).items():
                self.log["reach"].append((self.stage._keyed(t), "脚", sd, *self.reach_gap(sd, pt, foot=True)))
                joints.update(self.reach_foot(sd, pt))
            facing = None
        st, f = self.stage, self.stage.frame(t)
        st.scene.frame_set(f)
        z = at[2] if len(at) > 2 else st.ground(at[0], at[1])
        self.root.location = (at[0], at[1], z)
        if facing is not None:
            bpy.context.view_layer.update()
            new = -math.radians(self._heading(facing, at))
            old = self.root.rotation_euler.z
            self.root.rotation_euler.z = old + (new - old + math.pi) % (2 * math.pi) - math.pi if self.root.animation_data else new
        if pose is not None:
            self.log["keys"].append((st._keyed(t), pose))
        if pose is not None or joints:
            self.log["posed"].append(st._keyed(t))
            if pose is not None and pose != self.pose_name:
                self.seat_h = None
            self.pose_name = pose or self.pose_name
            a = {**POSES[self.pose_name], **joints}
            if "seat" in joints:
                self.seat_h = joints["seat"]
            elif "seat" in a and self.seat_h is not None:
                a["seat"] = self.seat_h
            self.joints = a
            g = lambda k: math.radians(a.get(k, 0.0))
            j = self.j
            self.pelvis.rotation_euler = (-g("lean") * 0.45, 0, g("twist") * 0.4)
            j["spine"].rotation_euler = (-g("lean") * 0.55, 0, g("twist") * 0.6)
            j["neck"].rotation_euler = (-g("head_nod") + g("lean") * 0.5, 0, g("head_turn"))
            for sd, x in (("l", -1), ("r", 1)):
                j[f"shoulder_{sd}"].rotation_euler = (g(f"shoulder_{sd}"), -x * g(f"abduct_{sd}"), 0)
                j[f"elbow_{sd}"].rotation_euler = (g(f"elbow_{sd}"), 0, 0)
                j[f"hip_{sd}"].rotation_euler = (g(f"hip_{sd}") + g("lean") * 0.45, 0, g(f"hipturn_{sd}"))
                j[f"knee_{sd}"].rotation_euler = (-g(f"knee_{sd}"), 0, 0)
            if "seat" in a:                                   # the pelvis sits 0.085 (mannequin units) above the seat
                self.pelvis.location.z = a["seat"] / self.root.scale.z + 0.085
            else:   # drop the pelvis until the lower foot stands on the ground
                self.pelvis.location.z = 0.92
                bpy.context.view_layer.update()
                low = min((j[f"knee_{sd}"].matrix_world @ Vector((0, y, -0.49))).z for sd in "lr" for y in (-0.06, 0.2))
                self.pelvis.location.z = 0.92 - (low - z) / self.root.scale.z
            for ob in (self.pelvis, *j.values()):
                key(ob, "rotation_euler", f)
            key(self.pelvis, "location", f)
        key(self.root, "location", f)
        key(self.root, "rotation_euler", f)
        return self

    def walk(self, t0, t1, to, stride_s=None, facing=None, end_pose="stand", ease=True, cadence=None, **joints):
        """Walk in a straight line from where it stands at t0 to `to`, following the ground; facing defaults to the way it goes.
        Eases in and out unless ease=False (constant speed, for a shot that starts and ends in mid-walk).
        Steps: cadence = steps a second; by default it follows the speed (about 1.6 at 1.3 m/s, kept within 1.4–1.8; see
        walk_keys), and hips and shoulders swing with the step length. A jointed previz used as a reference video hands its steps
        to the film one for one, so this is the film's cadence. stride_s = seconds a step, the old way (swing as drawn).
        Extra joint angles (for example the arms of "carry") are held through the whole walk and win over the swing."""
        st = self.stage
        st.scene.frame_set(st.frame(t0))
        bpy.context.view_layer.update()
        a = self.root.matrix_world.translation.copy()
        b = Vector((to[0], to[1], 0))
        head = facing if facing is not None else (b.x, b.y) if (b.xy - a.xy).length > 1e-3 else None
        d = (b.xy - a.xy).length
        ks, c, step, swing = walk_keys(t1 - t0, d, cadence, stride_s)
        ease = ease and len(ks) > 3                                  # ease in and out: a sudden start or stop comes back as a jump
        f0, f1 = st.frame(t0), st.frame(t1)
        for i, k in enumerate(ks + [1.0]):
            t = t0 + (t1 - t0) * k
            if stride_s is None and f1 > f0:     # where the key's frame falls: steps rarely land on whole frames, keep the speed even
                k = (st.frame(t) - f0) / (f1 - f0)
            p = a.lerp(b, k * k * (3 - 2 * k) if ease else k)
            pose = end_pose if i == len(ks) else ("walk_a" if i % 2 == 0 else "walk_b")
            extra = walk_swing(pose, swing) if pose in ("walk_a", "walk_b") and swing != 1.0 else {}
            self.place(t, (p.x, p.y), head if i == 0 or facing is not None else None, pose, **{**extra, **joints})
        self.log["walks"].append({"from": st._keyed(t0), "to": st._keyed(t1), "metres": d, "speed": d / (t1 - t0), "cadence": c, "step": step})
        return self

    def strike(self, t, step=0.5, pose="punch_r"):
        """A fast right-hand strike, fully out at time t, from wherever the person stands at t - 0.35 toward where they face:
        loads, steps in `step` metres, out, held a moment, back to guard (strike_keys). Key the one who is hit with a reaction
        (duck, hurt_b / hurt_b2) and let them back off, or the two freeze against each other."""
        st = self.stage
        st.at_time(t - 0.35)
        p0, f = self.root.matrix_world.translation.copy(), self.forward()
        for tk, dist, ps, jt in strike_keys(t, step, pose):
            q = p0 + f * dist
            self.place(tk, (q.x, q.y), None, ps, **jt)
        self.log["events"].append((st._keyed(t), f"打直（{pose}）"))
        return self

    def sit_down(self, t, chair, seat=None):
        """Sit down on a chair() (its name or what chair() returned), seated at time t (sit_keys). Walk to a point beside the
        chair first, about half a metre from its front edge and done by t - 1.7, not onto the seat: from there one step in front
        of it while turning, back to the chair, knees give, hips back and down with the trunk forward, seated, upright.
        Pull the chair out from the table so there is room in front of the seat."""
        st = self.stage
        it = next((i for i in st.items if i["kind"] == "chair" and (i["name"] == chair or i["obj"] is chair)), None)
        if it is None:
            raise ValueError(f"sit_down: no chair() called {chair!r}")
        keys = sit_keys(t, it["at"][:2], it["heading"], it["seat"] if seat is None else seat)
        st.at_time(t - 1.3)
        here, f = self.root.matrix_world.translation, self.forward()
        step = Vector((keys[0][1][0] - here.x, keys[0][1][1] - here.y, 0))
        if step.length > 0.1:                         # the step in front of the seat faces half-way between its way and the chair's
            f = step
        now = math.degrees(math.atan2(f.x, f.y))
        half = now + ((it["heading"] - now + 180) % 360 - 180) / 2
        for i, (tk, at, facing, ps, jt) in enumerate(keys):
            self.place(tk, at, half if i == 0 else facing, ps, **jt)
        self.log["events"] += [(st._keyed(t - 1.0), f"停在{it['name']}前"), (st._keyed(t), f"坐定（{it['name']}）")]
        return self

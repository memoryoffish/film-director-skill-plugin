"""Write the image jobs (white model -> realistic keyframe) and the video jobs of the fidelity experiment.

    python3 make_jobs.py img                     # jobs_img/*.json
    python3 make_jobs.py video s1 T S VC VJ      # jobs/<shot>_<feed>_s<seed>.json for the named shot and feeds (default: all)

Feeds (same prompt body inside a shot; only the last sentence and the attachments change):
    T    text + the two character reference images
    S    + the jointed white-model first still as a reference image                      (wm_guide)
    VC   + the capsule previz as the reference video                                     (video_guide)
    VJ   + the jointed previz as the reference video                                     (video_guide, same words as VC)
    VCS  + the capsule previz as the reference video and the jointed first still as a reference image
    KF   realistic keyframe as the first frame, slim prompt (s3: first + last frame = KFL)
    SG   like S with the all-grey still (mannequins told apart by glasses / cap / chest plate / height)
    c14 c17 c24 x125 x080 (s1), e13 e23 (s2), e (s3)   round 2: the jointed previz with another cadence / speed / faster key moves
    VC2  second round, s3 only: the capsule previz of the rebuilt set (window = a real hole with a frame, chairs on legs) and a
         video guide that says what an upright, shrinking capsule does and does not mean (capsule_guide)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, SKILL + "/scripts")
from jobs import save, shot_job, unit_job, video_guide, wm_guide  # noqa: E402

HERE = Path(__file__).resolve().parent
SEEDS = {"s1": (1101, 1102), "s2": (2101, 2102), "s3": (3101, 3102)}
DUR = {"s1": 5, "s2": 5, "s3": 6}
REFS, REF_NAMES = ["refs/ajie.png", "refs/xz.png"], ["阿杰", "小周"]

STYLE = "风格：写实的电影画面，35mm 胶片质感，细腻颗粒，自然的色调；画面里只有下面写到的人。"
# copied from examples/sofa-5f/notes.md
PEOPLE = ("人物：阿杰：二十五六岁的中国男青年，个子很高、偏瘦，短黑发，戴一副方框黑框眼镜，穿一件胸前印着绿色卡通恐龙的灰色短袖T恤、深蓝色牛仔裤、白色运动鞋。 "
          "小周：二十五六岁的中国男青年，比阿杰矮一个头，圆脸，微胖，戴一顶帽檐朝后反扣的红色棒球帽，穿一件白色镶蓝边的宽松篮球背心、黑色运动短裤、黑色运动鞋。")
QUIET = "两人自始至终没说话，嘴都闭着；没有任何人声、没有任何配乐。"

SHOT = {
    "s1": dict(
        cam="全景，两人全身入画；镜头在两人正前方三四米、齐胸高，面对着他们匀速向后退（后退跟拍），和两人始终保持同样的距离",
        pic="阿杰在画面中间偏左、小周在画面中间偏右，两人并排、正对镜头，沿着走廊不紧不慢地朝镜头走来，步子自然，手臂随着步子自然摆动。走到一半，小周侧过头看了阿杰一眼，"
            "又转回去看前面；阿杰一直看着前方。因为镜头在后退，两人在画面里的大小和位置基本不变，画面左边墙上的木门、右边墙上的窗一扇接一扇从画面两边进入画面、向走廊深处退去。",
        scene="场景：一栋老办公楼的走廊，又直又长，约两米宽。画面左边的墙上每隔几米有一扇关着的深棕色木门，画面右边的墙上是一排窗，下午的阳光从窗斜照进来，在水磨石地面上投下一格一格的光；"
              "墙下半截刷着旧绿漆墙裙、上半截是发黄的白墙，白色的天花板上有一排日光灯管，走廊尽头是一扇关着的棕色门。走廊里只有这两个人。",
        sound="声音：现场同期声：走廊里两个人的脚步声和回声、远处窗外的鸟叫。" + QUIET,
        marks="左边墙上的棕色门板是木门，右边墙上的浅蓝色方块是窗，走廊尽头的棕色方块是一扇门",
        slim="全景，镜头在两人正前方，面对着他们匀速向后退（后退跟拍），和两人始终保持同样的距离。左边戴眼镜的高个子和右边戴红帽子的矮个子并排朝镜头走来，步子自然，"
             "手臂随着步子自然摆动；走到一半，右边的人侧过头看了左边的人一眼，又转回去看前面。两人在画面里的大小和位置基本不变，两侧的门和窗不断向走廊深处退去。",
        slim_cam="镜头匀速向后退、始终跟着两人"),
    "s2": dict(
        cam="全景，固定机位，平视，从正侧面拍，两人全身入画",
        pic="阿杰在画面左边、面朝右，小周在画面右边、面朝左，两人相隔一步半，都摆着拳击的架势，盯着对方，脚下轻轻挪动。大约一秒后阿杰先动手：上前一步，右手一记直拳打向小周的头；"
            "小周一矮身，拳头从他头顶擦过去，他顺势贴近，一拳打在阿杰的肚子上；阿杰弓起身，捂着肚子朝画面左边踉跄着退了三四步；小周跟上两步，重新摆好架势盯着他，"
            "阿杰喘着气慢慢直起身，也重新举起拳头。全程阿杰都在小周的左边。",
        scene="场景：夜里空荡荡的地下停车场。水泥地面上画着白色的车位线，后面是一面水泥墙，墙前立着两根灰色的水泥方柱，画面右后方贴着墙停着一辆旧的银灰色轿车；"
              "低矮的水泥天花板上一排日光灯管，冷白的顶光。停车场里只有这两个人。",
        sound="声音：现场同期声：空旷停车场里的回声、鞋底蹭地的声音、出拳的风声、拳头打在身上的一声闷响、粗重的喘气声。" + QUIET,
        marks="后面两根灰色方柱是水泥柱，画面右后方的灰色方块是一辆停着的轿车",
        slim="全景，固定机位，平视，从正侧面拍。左边的高个子和右边的矮个子都摆着拳击的架势，脚下轻轻挪动。大约一秒后左边的人先动手：上前一步，右手一记直拳打向右边的人的头；"
             "右边的人一矮身，拳头从他头顶擦过去，他顺势贴近，一拳打在左边的人的肚子上；左边的人弓起身，捂着肚子朝画面左边踉跄着退了三四步；右边的人跟上两步，重新摆好架势盯着他，"
             "左边的人喘着气慢慢直起身，也重新举起拳头。",
        slim_cam="机位固定"),
    "s3": dict(
        cam="中景，机位的位置不动，镜头跟着阿杰从左向右摇（摇镜）",
        pic="开头镜头对着房间左后方敞开的木门：阿杰从门外走进屋，正对镜头方向走了两步，然后转向画面右边，穿过房间，走向右边窗前的一张小方桌；镜头跟着他向右摇，"
            "桌子和一直坐在桌子右侧椅子上的小周逐渐进入画面，小周面朝左坐着，看着阿杰走过来。阿杰走到桌子左侧的空椅子前，转身坐下，面朝右，和小周隔着桌子面对面；"
            "坐下后他把两只前臂搁在桌上，身体微微前倾。结尾镜头停住：阿杰在画面左边、侧身朝右，小周在画面右边、面朝左，桌子在两人中间。",
        scene="场景：一栋旧办公楼里的小房间，白墙，灰色的水泥地面。后墙左边是一扇向屋里敞开的深棕色木门，门外是走廊；后墙右边是一扇大窗，白天的自然光从窗外照进来。"
              "窗前摆着一张浅色的木头小方桌，桌子左右两侧各有一把深色木椅，面对面。屋里只有这两个人。",
        sound="声音：现场同期声：脚步声、椅子腿蹭地的声音、坐下时椅子的吱呀声、门外走廊里隐约的环境声。" + QUIET,
        marks="棕色的是向屋里敞开的木门，浅蓝色方块是窗，浅棕色的是桌子，两个深棕色方块是椅子",
        slim="中景，机位的位置不动，镜头跟着进门的人从左向右摇。戴眼镜的高个子从门口走进屋，转向画面右边，穿过房间，走到右边窗前的小方桌旁，在桌子左侧的空椅子上坐下，面朝右，"
             "两只前臂搁在桌上；桌子右侧的椅子上一直坐着一个戴红帽子的矮个子，面朝左，看着他走过来、坐下。镜头摇到两人隔着桌子面对面坐着就停住。",
        slim_cam="机位的位置不动、镜头从左向右摇"),
}

WHO = {  # how the prompt points at the mannequins
    "colour_pose": "蓝色人偶的位置、朝向和姿势就是阿杰的，红色人偶的就是小周的",
    "colour_route": "蓝色人偶的位置、朝向和路线就是阿杰的，红色人偶的就是小周的",
    "grey_pose": "两个人偶都是灰色的：个子高、戴黑色眼镜、胸牌是白色的那个，位置、朝向和姿势就是阿杰的；个子矮、戴红色帽子、胸牌是黑色的那个就是小周的",
}


def still_plus_video(legend_route, legend_pose):
    """VCS: the capsule previz as reference video and the jointed first still as reference image 3. Not in jobs.py: written here."""
    return (video_guide(1, legend_route) + "\n" +
            f"图3是这个镜头第一帧的白模站位示意图（和视频1同一个机位、同一时刻，只是人偶带了四肢），只用来定开头每个人的位置、朝向和姿势：{legend_pose}。"
            "不要把人偶、白模的纯色质感、胸前的白牌画进成片；人的样子用前面的人物参考图，场景的样子按文字写的来。")


def capsule_guide(n, legend):
    """video_guide for a capsule previz, second round. Added after the first clips: people stood bolt upright with their feet
    together wherever the capsule stood still, and sat down stiffly where it only shrank."""
    return (f"视频1是这个单元的白模预演（{n} 个镜头，切点和上面的时间表一致），只用来定每个镜头的机位、运镜、构图、站位、走位的路线和先后、切点：{legend}。"
            "替身是一根没有四肢的柱子，只表示人在哪、朝哪、什么时候走到哪，不提供肢体动作：它立得笔直、两脚并在一起只是因为它是柱子，不代表人的站姿——"
            "人的站姿、重心、迈步和手臂按真人在这场戏里自然的样子来；替身变矮表示人蹲下或坐下，怎么蹲、怎么坐按文字写的来。"
            "不要把替身、白模的纯色质感、滑行和僵硬的姿势画进成片；人和东西的样子用参考图，场景和光按文字写的来；最终画面正常彩色。")


R2 = ("c14", "c17", "c24", "x125", "x080", "e13", "e23", "e")     # s1: cadence 1.4 / 1.7 / 2.4, whole shot x1.25 / x0.8; s2: punch at 1.3 / 2.3 s; s3: sit keyed properly


def video(shot, feeds):
    s, out = SHOT[shot], []
    shots = [(0.0, float(DUR[shot]), s["cam"], s["pic"])]
    blocks = [STYLE, PEOPLE, s["scene"], s["sound"]]
    route, pose = WHO["colour_route"] + "；" + s["marks"], WHO["colour_pose"] + "；" + s["marks"]
    g_pose = WHO["grey_pose"] + "；" + s["marks"]
    for seed in SEEDS[shot]:
        for feed in feeds:
            name = f"{shot}_{feed}_s{seed}"
            unit = lambda guide, **kw: unit_job(name, shots, blocks, REF_NAMES, REFS, guide, seed, DUR[shot], **kw)
            if feed == "T":
                job = unit("")
                job["prompt"] = job["prompt"].rstrip("\n")
            elif feed == "S":
                job = unit(wm_guide(3, 1, pose), extra_refs=[f"wm/{shot}_j_a.png"])
            elif feed == "SG":
                job = unit(wm_guide(3, 1, g_pose), extra_refs=[f"wm/{shot}_jg_a.png"])
            elif feed == "VC":
                job = unit(video_guide(1, route), video=f"wm/pv_{shot}_c.mp4")
            elif feed == "VJ":
                job = unit(video_guide(1, route), video=f"wm/pv_{shot}_j.mp4")
            elif feed == "VC2":
                legend = ("蓝色的柱形替身的位置、朝向和路线就是阿杰的，红色的柱形替身的就是小周的；棕色的是向屋里敞开的木门，后墙上带白框的洞是窗，"
                          "浅棕色的是桌子，两把深棕色的是椅子")
                job = unit(capsule_guide(1, legend), video=f"wm/pv_{shot}b_c.mp4")
            elif feed == "VCS":
                job = unit(still_plus_video(route, pose), extra_refs=[f"wm/{shot}_j_a.png"], video=f"wm/pv_{shot}_c.mp4")
            elif feed in ("KF", "KFL"):
                job = shot_job(name, s["slim"], s["sound"], f"keys/k_{shot}_a.png", seed, DUR[shot],
                               last_frame=f"keys/k_{shot}_b.png" if feed == "KFL" else None, camera=s["slim_cam"])
            elif feed in R2:        # round 2: the jointed previz with its rhythm changed; same words as VJ
                marks = "棕色的是向屋里敞开的木门，后墙上带白框的洞是窗，浅棕色的是桌子，两把深棕色的是椅子" if shot == "s3" else s["marks"]
                # s2: the text no longer says when the first punch comes, so that only the previz carries the timing
                sh = [(0.0, float(DUR[shot]), s["cam"], s["pic"].replace("大约一秒后阿杰先动手", "对峙片刻后阿杰先动手"))]
                assert shot != "s2" or "对峙片刻后" in sh[0][3]
                job = unit_job(name, sh, blocks, REF_NAMES, REFS, video_guide(1, WHO["colour_route"] + "；" + marks), seed, DUR[shot],
                               video=f"wm/pv_{shot}{feed}_j.mp4")
            else:
                raise SystemExit(f"unknown feed {feed}")
            job.update(shot=shot, feed=feed)
            save(job, HERE / "jobs")
            out.append(name)
    return out


# ---------------------------------------------------------------- white model -> realistic keyframe (gpt-image)
MARKERS = ("The mannequins and boxes in Image 1 are only position markers: do not draw any mannequin, flat plastic white-model shading, "
           "square chest plates, subtitles or watermark. Nobody looks into the camera lens.")
LAYOUT = ("Image 1 is a 3D blocking render (white model). Use it only as the layout guide: keep its camera position, lens, perspective and framing exactly, "
          "and keep every person and object at the same place, size, facing direction and pose. Do not move, add or remove anyone or anything. "
          "Walls, floor, doors, windows and furniture stay where they are in Image 1.")
AJIE = "the tall, thin young man from Image 2 (same face, short black hair, black square glasses, grey T-shirt with a green cartoon dinosaur on the chest, dark blue jeans, white sneakers)"
XZ = "the shorter, stocky, round-faced young man from Image 3 (red baseball cap worn backwards, white basketball jersey with blue trim, black shorts, black sneakers)"

IMG = {
    "k_s1_a": dict(images=["wm/s1_j_a.png", "refs/ajie.png", "refs/xz.png"], prompt=f"""Turn Image 1 into a photorealistic film still, 16:9.

{LAYOUT}

Who is who:
- The blue mannequin on the left is AJIE: {AJIE}. He walks straight toward the camera, seen from the front, full body, in mid-stride, arms swinging naturally, eyes on the way ahead.
- The red mannequin on the right is XIAOZHOU: {XZ}. He walks beside Ajie toward the camera, seen from the front, full body, in mid-stride.

Scene: a long, straight corridor of an old office building, about two metres wide. On the left wall, closed dark-brown wooden doors (the brown panel in Image 1); on the right wall a row of windows (the pale blue panels) with warm afternoon sunlight slanting in and laying bright patches on the terrazzo floor; old green dado paint on the lower half of the walls, yellowed white above; a white ceiling with a row of fluorescent tubes; at the far end of the corridor a closed brown door. Nobody else is in the corridor.

Look: photorealistic cinema frame, 35mm film, fine grain, natural colours, soft warm afternoon light.

{MARKERS}"""),
    "k_s2_a": dict(images=["wm/s2_j_a.png", "refs/ajie.png", "refs/xz.png"], prompt=f"""Turn Image 1 into a photorealistic film still, 16:9.

{LAYOUT}

Who is who:
- The blue mannequin on the left is AJIE: {AJIE}. He is seen in full profile facing right, full body, in a boxing guard: both fists raised in front of his chin, left foot forward, knees slightly bent, eyes fixed on his opponent.
- The red mannequin on the right is XIAOZHOU: {XZ}. He is seen in full profile facing left, full body, in the same kind of boxing guard, fists up, eyes fixed on Ajie.
The two stand about a step and a half apart, squaring up for a fight.

Scene: an empty underground car park at night. Bare concrete floor with white painted parking-bay lines; behind the two men a concrete back wall with two square grey concrete pillars in front of it (the two grey columns in Image 1); at the far right, behind the right pillar, an old silver-grey sedan parked along the back wall (the grey boxes at the right edge of Image 1), partly out of frame; a low concrete ceiling with a row of fluorescent tubes that give a cold white top light. Nobody else is there.

Look: photorealistic cinema frame, 35mm film, fine grain, cool desaturated colours, hard fluorescent top light.

{MARKERS}"""),
    "k_s3_b": dict(images=["wm/s3_j_b.png", "refs/ajie.png", "refs/xz.png"], prompt=f"""Turn Image 1 into a photorealistic film still, 16:9.

{LAYOUT}

Who is who:
- The blue mannequin on the left is AJIE: {AJIE}. He sits on the left chair, seen in profile facing right, leaning slightly forward with both forearms resting on the table, looking at the man opposite.
- The red mannequin on the right is XIAOZHOU: {XZ}. He sits on the right chair facing left, turned a little toward the camera, forearms on the table, looking at Ajie.
They sit face to face across a small table.

Scene: a small plain room in an old office building: white walls, grey concrete floor. Behind the two men a large window (the pale blue panel in Image 1) lets in soft daylight. The light-brown shape between them is a small square wooden table on four legs; the two dark-brown boxes are plain dark wooden chairs with straight backs. Nobody else is in the room.

Look: photorealistic cinema frame, 35mm film, fine grain, natural colours, soft daylight from the window.

{MARKERS}"""),
    "k_s3_a": dict(images=["wm/s3_j_a.png", "keys/k_s3_b.png", "refs/ajie.png"], prompt="""Image 2 is a film still: two young men sit face to face at a small wooden table by a window in a plain white room. Image 1 is a 3D blocking render (white model) of an earlier moment of the same shot in the same room: the camera stands at the same spot but is turned to the left, toward the door of the room, a few seconds before the man with glasses sits down. Draw that earlier moment as a photorealistic film still, 16:9.

Keep from Image 2: the same room (white walls, grey concrete floor), the same window, the same dark wooden chairs, the same man with glasses and his clothes, the same soft daylight and film look.

Framing, positions and poses exactly as in Image 1:
- The brown frame in the back wall is the open doorway of the room; the brown panel at its left side is the dark-brown wooden door leaf, swung open into the room, with a brass handle. Through the doorway you see a dim corridor with a plain wall.
- The blue mannequin is AJIE: the tall, thin young man from Image 3 and Image 2 (same face, short black hair, black square glasses, grey T-shirt with a green cartoon dinosaur on the chest, dark blue jeans, white sneakers). He is just stepping through the doorway into the room, walking toward the camera, seen from the front, full body, in mid-stride, arms swinging naturally.
- At the right edge of the frame: the back of an empty dark wooden chair (the brown box) and, on the back wall above it, the left part of the window (the pale blue panel).
- The table and the second man are outside the frame to the right: they are not visible in this picture. Ajie is the only person in the frame.

The mannequins and boxes in Image 1 are only position markers: do not draw any mannequin, flat plastic white-model shading, square chest plates, subtitles or watermark. Nobody looks into the camera lens."""),
}


def img():
    (HERE / "jobs_img").mkdir(exist_ok=True)
    for name, j in IMG.items():
        (HERE / "jobs_img" / f"{name}.json").write_text(json.dumps({"name": name, "size": "1536x864", **j}, ensure_ascii=False, indent=1))
    print(len(IMG), "image jobs")


if __name__ == "__main__":
    if sys.argv[1] == "img":
        img()
    else:
        shot, feeds = sys.argv[2], sys.argv[3:] or ["T", "S", "VC", "VJ", "VCS", "KFL" if sys.argv[2] == "s3" else "KF"]
        print("\n".join(video(shot, feeds)))

"""《沙发》五楼到结尾 9 个镜头：gpt-image 关键帧任务（gpt/jobs/f_*.json）和 Wan 任务（server/jobs7/）。

python3 make_fin.py keys      关键帧任务（分 4 批，后一批要用前一批的成图）
python3 make_fin.py video     视频任务：逐镜头首帧（GF / GFL）、单元一次生成（URI 白模图当参考、URV 预演当参考视频、URG 关键帧当参考）
"""
import json, sys
from pathlib import Path
import make_jobs as m

HERE = Path(__file__).resolve().parent
WM, GOUT, REFS = HERE / "out/fin", HERE / "gpt/out", HERE / "server/inputs"
AJ, XZ, AUNT, SOFA = (str(REFS / f"{n}.png") for n in ("ajie", "xz", "aunt", "sofa"))

# ---------------------------------------------------------------- gpt-image keyframes
E_AJ = "AJIE: the tall, thin young man from Image {i} (same face, short black hair, black square glasses, grey T-shirt with a green cartoon dinosaur on the chest, dark blue jeans, white sneakers)"
E_XZ = "XIAOZHOU: the shorter, stocky, round-faced young man from Image {i} (red baseball cap worn backwards, white basketball jersey with blue trim, black shorts, black sneakers)"
E_SOFA = "an old dark-green velvet three-seat sofa with square arms, three seat cushions and short dark wooden legs"
E_LAND = ("the top-floor landing of an old Chinese walk-up apartment building, very narrow. Lower half of the walls painted old green, upper half yellowed white, "
          "bare concrete floor, a few small white paper ads with black text pasted on the walls. The red block on the left wall is a big floor number 5, "
          "hand-painted in red directly on the wall. In the middle of the end wall is the only door: an old dark-brown wooden door in a dark frame, with an old brass lock "
          "on its right side. The red bars are an old iron stair railing painted faded red, at the edge of the landing where the stairs come up.")
E_LOOK = "Look: photorealistic cinema frame, 35mm film, fine grain, natural colours, warm late-afternoon daylight coming from the stairwell window behind the camera."
E_GUIDE = ("Image 1 is a 3D blocking render (white model). Use it only as the layout guide: keep its camera position, lens, perspective and framing exactly, and keep every "
           "person and object at the same place, size, facing direction and pose. Do not move, add or remove anyone or anything. Walls, floor, door, railing and furniture "
           "stay where they are in Image 1.")
E_NO = ("The mannequins and boxes in Image 1 are only position markers: do not draw any mannequin, flat plastic white-model shading, square chest plates, "
        "subtitles or watermark. Nobody looks at the camera.")
E_KEEP = "Keep from Image 2: the same landing (walls, floor, paper ads, the red painted 5, the brown door with its dark frame and brass lock, the faded-red railing), the same sofa, the same people and clothes, the same warm light and film look."

KEYS = {  # name: (batch, images, prompt)
    "s51_a": (0, [WM / "s51_a.png", AJ, XZ, SOFA], f"""Turn Image 1 into a photorealistic film still, 16:9.

{E_GUIDE}

Who is who:
- The blue mannequin on the left is {E_AJ.format(i=2)}. He is seen from behind, bent forward at the waist with one foot ahead, both hands on the front edge of the sofa, pushing it away from the camera toward the door. The dinosaur print is on his chest and cannot be seen from behind; the back of his T-shirt is plain grey.
- The red mannequin on the right is {E_XZ.format(i=3)}. He is also seen from behind, bent forward, both hands on the front edge of the sofa, pushing.
- The green box is the sofa from Image 4 ({E_SOFA}). Its seat faces the camera and its backrest is on the far side, toward the door. It stands in the middle of the landing, not yet at the door.

Scene: {E_LAND} The door is closed. The camera is high, at the top of the stairs, looking over the railing in the foreground.

Both men are sweaty and straining. {E_LOOK}

{E_NO}"""),
    "s51_b": (1, [WM / "s51_b.png", GOUT / "f_s51_a.png"], f"""Image 2 is a film still: two young men push an old dark-green sofa across a narrow apartment landing toward a brown door. Image 1 is a 3D blocking render (white model) of the same shot three seconds later, same camera. Draw that later moment as a photorealistic film still, 16:9.

{E_KEEP} Same camera position and framing as Image 2.

Change only what Image 1 shows: the sofa has been pushed all the way to the end wall, its backrest now touches the wall with the door, and it covers the lower half of the closed door. The two men have followed it and are further from the camera, still bent forward with both hands on the front edge of the sofa: the blue mannequin (left) is the tall man in the grey T-shirt, the red mannequin (right) is the stocky man in the red backwards cap and white jersey. Exactly two people.

{E_NO}"""),
    "s52_a": (1, [WM / "s52_a.png", GOUT / "f_s51_a.png", AJ, XZ], f"""Image 2 is a film still: two young men push an old dark-green sofa across a narrow apartment landing toward a brown door. Image 1 is a 3D blocking render (white model) of the next shot in the same place, a moment later, from a new camera position at chest height. Draw this new shot as a photorealistic film still, 16:9.

{E_KEEP}

Framing, positions and poses exactly as in Image 1: a medium shot from the knees up. The blue mannequin on the LEFT is {E_AJ.format(i=3)}, standing upright in profile, facing right. The red mannequin on the RIGHT is {E_XZ.format(i=4)}, standing upright in profile, facing left, looking up at Ajie. They have just straightened up, are out of breath and sweaty, and look at each other with the beginning of a tired grin; their arms hang at their sides. Behind them the sofa stands right against the end wall, its seat toward the camera, across the bottom of the frame; between the two men we see the closed brown door with its brass lock on the right; the red painted 5 is on the left wall.

{E_NO}"""),
    "s53_a": (1, [WM / "s53_a.png", GOUT / "f_s51_a.png", AJ], f"""Image 2 is a film still of a narrow apartment landing with an old dark-green velvet sofa and a closed dark-brown wooden door. Image 1 is a 3D blocking render (white model) of a close-up in the same place: the camera is now right at the door, a little to the right of it, looking at the door's lock. Draw this close-up as a photorealistic film still, 16:9.

Keep from Image 2: the same old dark-brown door, the same dark door frame, the same yellowed wall, the same dark-green velvet sofa, the same warm light and film look.

Framing exactly as in Image 1:
- The large brown surface is the closed door (worn dark-brown painted wood). The darker vertical strip to its right is the door frame; the pale surface at the far right is the wall.
- The yellow block on the door is an old brass rim lock with a keyhole.
- The green area along the bottom is the top of the sofa's backrest, close to the lens and slightly out of focus.
- The arm coming in from the upper left is the right arm of the young man from Image 3: the short sleeve of his grey T-shirt at the top left, a bare forearm, and his right hand holding a small bunch of keys, the tip of one key just about to enter the keyhole. The skin-coloured shape at the left edge is his left hand resting on top of the sofa's backrest.
His face is not in the frame. Shallow depth of field, focus on the lock and the hand.

Do not draw any mannequin, flat plastic white-model shading, subtitles or watermark."""),
    "s53_b": (2, [WM / "s53_b.png", GOUT / "f_s53_a.png"], """Image 2 is a film still: a close-up of a man's hand putting a key into the brass lock of a closed dark-brown wooden door; the top of a dark-green sofa backrest runs along the bottom of the frame. Image 1 is a 3D blocking render (white model) of the same shot three seconds later, same camera. Draw that later moment as a photorealistic film still, 16:9.

Keep from Image 2: the same camera and framing, the same door frame on the right, the same wall, the same sofa backrest along the bottom, the same arm (grey T-shirt sleeve, bare forearm), the same light and film look.

Change only what Image 1 shows: the door has swung open inward, away from the camera, hinged on its left side. The door leaf (the large brown surface on the left) now stands open at an angle, further away; its brass lock, with the bunch of keys hanging from it, is small near the top centre. Between the edge of the door and the door frame on the right we look into an empty room: an old wooden floor and bare white walls in daylight. The man's right hand has let go of the key and is stretched out near the top of the frame, fingers open, having just pushed the door.

Do not draw any mannequin, flat plastic white-model shading, subtitles or watermark."""),
    "s54_a": (1, [WM / "s54_a.png", GOUT / "f_s51_a.png"], f"""Image 2 is a film still: two young men push an old dark-green sofa across a narrow apartment landing toward a brown door. Image 1 is a 3D blocking render (white model) of a later shot in the same place: the camera now stands centred behind the two men and looks straight at the door. Draw this shot as a photorealistic film still, 16:9.

{E_KEEP}

Framing, positions and poses exactly as in Image 1: a full shot. The door now stands open, swung inward into the flat (its leaf is seen edge-on at the left side of the doorway); through the doorway we see an empty room with a wooden floor and white walls in daylight. The sofa stands right against the end wall across the doorway, its seat toward the camera; the doorway is clearly much narrower than the sofa, so both ends of the sofa stick out well past the door frame. The blue mannequin on the left is the tall man in the grey T-shirt and jeans, the red mannequin on the right is the stocky man in the red backwards cap, white jersey and black shorts: both stand upright side by side in front of the sofa with their backs to the camera, arms hanging, perfectly still, looking at the doorway. The back of the grey T-shirt is plain (no print). The red painted 5 is on the left wall; the faded-red railing is in the foreground at the bottom right.

{E_NO}"""),
    "s55_a": (2, [WM / "s55_a.png", GOUT / "f_s54_a.png"], """Image 2 is a film still of a narrow apartment landing: an old dark-green velvet sofa stands across an open dark-brown wooden doorway that is much narrower than the sofa. Image 1 is a 3D blocking render (white model) of the next shot in the same place: an extreme close-up, camera high, looking down at the left end of the sofa where it meets the wall beside the door. Draw that close-up as a photorealistic film still, 16:9.

Keep from Image 2: the same sofa (worn dark-green velvet, square arm), the same walls (old green lower half, yellowed white upper half), the same dark-brown door frame, the same warm afternoon light and film look.

Framing as in Image 1: the green shape is the sofa's left arm and the top of its backrest, filling the lower part of the frame; the brown vertical strips at the upper right are the left jamb of the door frame and the edge of the open door; the pale surface is the wall beside the door. The point of the picture: the end of the sofa is jammed flat against the wall beside the door frame and sticks out well past the door frame, so it obviously cannot go through. No people in the frame.

Do not draw any mannequin, flat plastic white-model shading, subtitles or watermark."""),
    "s56_a": (2, [WM / "s56_a.png", GOUT / "f_s54_a.png", AJ, XZ], f"""Image 2 is a film still: two young men stand with their backs to the camera in front of an old dark-green sofa that blocks an open doorway on a narrow apartment landing. Image 1 is a 3D blocking render (white model) of the reverse angle of the same moment: the camera is now inside the empty flat, looking out through the open doorway at the two men from the front. Draw that reverse shot as a photorealistic film still, 16:9.

Keep from Image 2: the same two men and their clothes, the same sofa, the same landing (old green lower walls, yellowed white upper walls, small paper ads), the same warm afternoon light and film look.

Framing, positions and poses exactly as in Image 1, a frame within a frame:
- Foreground: the inside of the flat, in shade. The dark vertical strip on the left is the door jamb with a bare white room wall beside it; the large brown surface on the right is the open door leaf, close to the camera.
- Through the doorway: the green band across the bottom of the opening is the BACK of the sofa's backrest (plain dark-green velvet), wider than the doorway so its ends disappear behind the frame on both sides.
- Behind the sofa the two men stand side by side facing the camera, seen from the thighs up. The red mannequin on the LEFT is {E_XZ.format(i=4)}. The blue mannequin on the RIGHT is {E_AJ.format(i=3)}. Both look at the doorway with blank, sweaty faces, mouths closed, arms hanging.
- Behind them: the landing, the faded-red iron railing at waist height, and beyond it the open stairwell with its far wall and a window (the pale blue rectangle) letting in warm daylight. This is the top floor: the stairs only go down, so no steps are visible above the railing.
- The red painted 5 of Image 2 is on the wall that is now on the right-hand side, hidden behind the open door leaf: no painted number is visible anywhere in this shot.

{E_NO}"""),
    "s57_a": (3, [WM / "s57_a.png", GOUT / "f_s56_a.png", AJ, XZ], f"""Image 2 is a film still: seen through an open doorway, two young men stand side by side behind an old dark-green sofa on a narrow apartment landing, facing the camera. Image 1 is a 3D blocking render (white model) of the next shot: a close two-shot of their faces from the doorway. Draw it as a photorealistic film still, 16:9.

Keep from Image 2: the same two men, faces and clothes, the same landing behind them (yellowed walls, faded-red railing, the stairwell wall with a window letting in warm daylight), the same light and film look. No door frame and no painted number on any wall in this shot.

Framing and positions exactly as in Image 1: a close shot from the chest up, the two faces side by side. The red mannequin on the LEFT, lower in the frame, is {E_XZ.format(i=4)}. The blue mannequin on the RIGHT, taller, is {E_AJ.format(i=3)}. Both stare straight ahead, just past the camera, with blank, exhausted faces covered in sweat, mouths closed. The background is out of focus.

{E_NO}"""),
    "s61_a": (0, [WM / "s61_a.png", AJ, XZ], f"""Turn Image 1 into a photorealistic film still, 16:9.

{E_GUIDE}

Who is who:
- The blue mannequin on the LEFT is {E_AJ.format(i=2)}.
- The red mannequin on the RIGHT is {E_XZ.format(i=3)}.
Both sit on the floor side by side, backs against the closed door, legs stretched out toward the camera, shoes nearest the camera. Each holds a white plastic takeout box (the white boxes) on his lap with the left hand and a pair of disposable chopsticks in the right hand. Ajie looks down into his box, picking at the rice; Xiaozhou is lifting a bite to his mouth. Both are sweaty, tired and blank-faced, mouths closed or chewing; they do not look at each other.

Scene: the inside of a just-rented, completely empty flat: old wooden floorboards, bare white walls, no furniture at all. The brown rectangle behind them is the inside of the flat's old dark-brown wooden entrance door in a dark frame, closed; the yellow block is its brass lock. Soft afternoon daylight comes from a window behind the camera. The camera is low, a little below standing waist height.

Look: photorealistic cinema frame, 35mm film, fine grain, natural warm colours.

{E_NO}"""),
    "s62_a": (1, [WM / "s62_a.png", GOUT / "f_s51_a.png", AUNT], f"""Image 2 is a film still: two young men push an old dark-green sofa across a narrow apartment landing toward a brown door. Image 1 is a 3D blocking render (white model) of a later shot in the same place: the camera stands centred on the landing and looks straight at the closed door. Draw this shot as a photorealistic film still, 16:9.

Keep from Image 2: the same landing (walls, floor, paper ads, the red painted 5 on the left wall, the brown door with its dark frame and brass lock, the faded-red railing), the same sofa, the same warm light and film look. The two men are gone.

Framing, positions and poses exactly as in Image 1: a full shot. The sofa stands right against the end wall across the closed door, blocking it, its seat toward the camera; it is almost as wide as the landing. The maroon mannequin is AUNTIE: the woman from Image 3 (about sixty, short permed dark-brown hair, round face, maroon floral short-sleeved blouse, loose black trousers, black cloth shoes). She sits comfortably in the middle of the sofa facing the camera, feet on the floor, head lowered, both hands at a white porcelain bowl of edamame pods on her lap (the small white box), shelling a pod. The faded-red railing is in the foreground at the bottom right. Exactly one person.

{E_NO}"""),
}

# ---------------------------------------------------------------- Wan video jobs
STYLE = "风格：写实的电影画面，35mm 胶片质感，细腻颗粒，自然的暖色调；冷面喜剧的拍法：机位固定、构图端正，人物的表情和停顿清清楚楚；画面里只有下面写到的人。"
PEOPLE = lambda who: "人物：" + " ".join(m.P[n] for n in who)
SOFA_T = m.SOFA
LAND = ("场景：一栋没有电梯的老居民楼的楼道，很窄。墙下半截刷着旧绿漆墙裙、上半截是发黄的白墙，水泥地面，墙上贴着开锁、通下水道的白底黑字小广告；周六下午暖黄的阳光从楼梯间的窗斜照进来。"
        "这里是五楼，也是顶楼：楼梯从下面上来，到这个小平台为止，平台靠楼梯的一边是褪色红漆的铁栏杆；平台尽头那面墙的正中只有一扇旧的深棕色木门，就是他们的家门，门锁在门的右侧，门往屋里开；"
        "左边墙上用红漆刷着很大的楼层号「5」。")
ROOM = "场景二（只在写明的镜头里）：五楼那扇木门的里面，一间刚租下的空屋子，旧木地板，白墙，屋里什么家具都没有，窗外是下午的阳光。"
SOUND = ("声音：像纪录片一样现场录的同期声：老楼道的回声、喘气声、布面摩擦声、远处窗外的鸟叫。所有人自始至终都没说话，嘴都闭着；没有任何人声、没有任何配乐"
         "（没有鼓、弦乐、钢琴、合成器、持续的低音铺底、合唱、哼唱、任何旋律）。安静的时候就让它安静。")
REQ1 = "要求：全片只有这一个镜头，机位固定，不切镜；画面里没有任何字幕、水印；人物不看镜头。"
REQU = "要求：画面里没有任何字幕、水印；除了墙上的楼层号和小广告，没有别的可读文字。人物视线按分镜表写的方向看，不看镜头。"

SHOT = {  # name: (who, seconds to generate, text, extra sound)
    "s51": (["阿杰", "小周"], 4, "全景，固定机位，从楼梯口上方越过红漆栏杆往平台尽头的木门拍。木门关着。阿杰在画面左边、小周在画面右边，都背对镜头，弓着腰，双手按在墨绿色沙发的前沿，一步一步把沙发往门那边推，沙发在水泥地上蹭着往前滑，最后靠背贴上门所在的那面墙，停住。两人浑身是汗。",
            "沙发腿蹭水泥地的闷响、最后靠背撞上墙的一声闷响"),
    "s52": (["阿杰", "小周"], 3, "中景，固定机位，平视。沙发已经横在门前。阿杰在画面左边、面朝右，小周在画面右边、面朝左，两人刚直起腰，喘着气，对视着笑了出来，各举起靠镜头这一侧的手，在两人中间“啪”地击了一下掌，然后手放下。两人身后是沙发和关着的木门。",
            "清脆的一声击掌"),
    "s53": (["阿杰"], 4, "近景，固定机位，拍门锁和阿杰的手。画面下沿是沙发靠背的顶边。阿杰的右手从画面左上方伸进来，把钥匙插进旧木门右侧的黄铜门锁，拧了一下，“咔哒”一声，然后把门往屋里推开：门的合页在左边，门扇向里转开，露出门里的空屋子。画面里只有手和前臂，没有脸。",
            "钥匙串的叮当声、钥匙插进锁孔和拧开门锁的咔哒声、旧门轴的吱呀声"),
    "s54": (["阿杰", "小周"], 4, "全景，固定机位，从两人身后正对着门拍。旧木门已经向屋里敞开，门洞很窄，只有沙发一半宽；墨绿色沙发横在门前，两头都比门框宽出一大截。阿杰在画面左边，小周在画面右边，并排站在沙发跟前，背对镜头，一动不动地看着门，只有喘气时肩膀微微起伏。", ""),
    "s55": ([], 3, "特写，固定机位，俯拍，极近：画面里只有门框的一边和沙发的一头。墨绿色沙发的扶手顶在深棕色门框外面的墙上，比门框宽出一大截，根本进不去。画面里没有人，几乎是静止的，只有阳光里的浮尘在动。", ""),
    "s56": (["阿杰", "小周"], 3, "中景，固定机位，从屋里隔着门框往外拍。门框套着两个人：小周在画面左边，阿杰在画面右边，面朝镜头并排站在沙发后面；沙发的靠背横在门洞下半截。两人看着门框，然后慢慢低头，一起看向身前的沙发，再抬头看门，一句话也没说，嘴闭着，面无表情。", ""),
    "s57": (["阿杰", "小周"], 4, "近景，固定机位，两张脸并排：小周在画面左边，阿杰在画面右边。两人满脸是汗，面无表情地看着前方，一动不动，很久都没说话，只有喘气声；一滴汗从阿杰的下巴滴下来。", ""),
    "s61": (["阿杰", "小周"], 6, "中景，固定机位，机位偏低，在屋里平视拍那扇木门的里面。门关着。阿杰和小周并排坐在地板上，背靠着门，腿朝镜头伸直，阿杰在画面左边，小周在画面右边；两人各用左手端着一盒外卖放在腿上，右手拿筷子扒饭，默默地嚼，谁也不看谁，一句话也不说。",
            "筷子碰塑料饭盒的声音、嚼饭的声音"),
    "s62": (["大妈"], 8, "全景，固定机位，在门外的五楼平台上正对着关着的木门拍。墨绿色沙发横着堵在木门前面，靠背贴着门，从头到尾纹丝不动。大妈舒舒服服地坐在沙发正中间，面朝镜头，腿上放着一个装毛豆的白瓷碗，低头不紧不慢地剥毛豆，把豆子丢进碗里，偶尔往嘴里放一颗，慢慢嚼。除了她的手和嘴，画面里什么都不动。",
            "剥毛豆壳的轻响、豆子落进瓷碗的声音"),
}
LASTF = {"s51", "s53"}
UNITS = {  # name: (shots with cut times, duration, people)
    "U5a": ([("s51", 0.0, 3.5), ("s52", 3.5, 6.1), ("s53", 6.1, 9.6)], 10, ["阿杰", "小周"]),
    "U5b": ([("s54", 0.0, 3.4), ("s55", 3.4, 5.8), ("s56", 5.8, 8.35), ("s57", 8.35, 11.6)], 12, ["阿杰", "小周"]),
    "U6": ([("s61", 0.0, 5.2), ("s62", 5.2, 12.6)], 13, ["阿杰", "小周", "大妈"]),
}
RNAME = {"阿杰": "ajie", "小周": "xz", "大妈": "aunt"}


def sound(extra):
    return SOUND if not extra else SOUND.replace("远处窗外的鸟叫。", f"远处窗外的鸟叫；这个镜头里还有{extra}。")


def shot_prompt(name):
    who, _d, text, extra = SHOT[name]
    scene = ROOM.replace("场景二（只在写明的镜头里）", "场景") if name == "s61" else LAND
    parts = ["镜头：" + text, STYLE]
    if who:
        parts.append(PEOPLE(who))
    if name != "s61":
        parts.append(SOFA_T)
    return "\n".join([*parts, scene, sound(extra), REQ1])


def unit_prompt(u, tail):
    shots, dur, who = UNITS[u]
    end = shots[-1][2]
    head = [f"本单元共 {len(shots)} 个镜头，剧情时长 {end:.2f} 秒；下面所有时间都是成片内的秒数，从 0 开始。成片必须按分镜时间表剪接成这 {len(shots)} 个镜头：相邻镜头交界的秒数就是切点，"
            "切点处机位与景别立即改变；表中没有的切点不要加，表中有的切点不能省，不合并、不调换，只用硬切，没有叠化。",
            f"{end:.2f} 秒之后直到成片结束，延续最后一个镜头的画面与运动，不要切到新镜头。"]
    if u == "U6":
        head.append("镜头1在屋里（场景二），镜头2在门外的五楼平台。")
    for i, (n, a, b) in enumerate(shots):
        text = SHOT[n][2]
        cam, _, pic = text.partition("。")
        head.append(f"镜头{i + 1}｜{a:.2f}–{b:.2f} 秒｜机位与景别：{cam}｜{'开场' if i == 0 else '以“硬切”从上一镜头切入'}\n  画面：{pic}")
    names = [*who, "那张墨绿色沙发"]
    refline = "参考图：" + "，".join(f"图{i + 1}是{n}" for i, n in enumerate(names)) + "。每张图只用来锁住这个人（或这张沙发）的长相、衣服和颜色；不照搬图里的灰色背景、构图、光线、姿势和视线，只用图里的人和沙发。"
    extra = "；".join(SHOT[n][3] for n, *_ in shots if SHOT[n][3])
    body = ["", STYLE, refline, PEOPLE(who), SOFA_T, LAND]
    if u == "U6":
        body.append(ROOM)
    return "\n".join([*head, *body, sound(extra), REQU, tail])


def write(folder, job):
    d = HERE / "server" / folder
    d.mkdir(exist_ok=True)
    (d / f"{job['name']}.json").write_text(json.dumps(job, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "keys":
        (HERE / "gpt/jobs").mkdir(exist_ok=True)
        for name, (batch, images, prompt) in KEYS.items():
            (HERE / "gpt/jobs" / f"f_{name}.json").write_text(json.dumps({"name": f"f_{name}", "batch": batch, "size": "1536x864", "images": [str(p) for p in images],
                                                                           "prompt": prompt}, ensure_ascii=False, indent=1))
        for b in range(4):
            print(b, " ".join(f"jobs/f_{n}.json" for n, v in KEYS.items() if v[0] == b))
    if what == "video":
        base = dict(resolution="720P", ratio="16:9", audio=True, prompt_extend=False)
        dolls = "蓝色人偶的位置、朝向、姿势和动作就是阿杰的，红色人偶的就是小周的，枣红色人偶的就是大妈的，绿色方块就是沙发的位置和方向，棕色的是门，红色栏杆是楼梯口的铁栏杆，墙上的红色方块是楼层号「5」的位置"
        for u, (shots, dur, who) in UNITS.items():
            refs = [f"inputs/{RNAME[n]}.png" for n in who] + ["inputs/sofa.png"]
            k = len(refs)
            idx = "、".join(f"图{k + 1 + i}" for i in range(len(shots)))
            sh = "、".join(f"镜头{i + 1}" for i in range(len(shots)))
            for seed in (9101, 9102):
                if "--urv" not in sys.argv and "--urg" not in sys.argv:
                    tail = (f"{idx}依次是{sh}开头的白模站位示意图，只用来定每个镜头的机位、构图和站位：{dolls}，门、墙、地面的位置和透视也照它。"
                            "不要把人偶、白模的纯色质感、胸前的白牌画进成片；人和沙发的样子用前面几张参考图，场景的样子按文字写的来。")
                    write("jobs7", {"name": f"{u}_URI_s{seed}", "shot": u, "variant": "URI", "seed": seed, "duration": dur, **base, "prompt": unit_prompt(u, tail),
                                    "reference_images": refs + [f"inputs/fin/{n}_a.png" for n, *_ in shots]})
                if "--urv" in sys.argv:
                    tail = (f"视频1是这个单元的白模预演（{len(shots)} 个镜头，切点和上面的时间表一致），只用来定每个镜头的机位、构图、站位、动作的先后和切点：{dolls}。"
                            "不要把人偶、白模的纯色质感、僵硬的姿势画进成片：人按真人自然地动；人和沙发的样子用参考图，场景和光按文字写的来；最终画面正常彩色。")
                    write("jobs8", {"name": f"{u}_URV_s{seed}", "shot": u, "variant": "URV", "seed": seed, "duration": dur, **base, "prompt": unit_prompt(u, tail),
                                    "reference_images": refs, "reference_video": f"inputs/fin/pv_{u}.mp4"})
                if "--urg" in sys.argv:
                    tail = (f"{idx}依次是{sh}开头的画面参考（同一个地方、同样的人和沙发）：每个镜头的机位、景别、构图、每个人的位置和朝向都照对应的那张图；"
                            "人的长相和衣服以前面的人物参考图为准。")
                    write("jobs9", {"name": f"{u}_URG_s{seed}", "shot": u, "variant": "URG", "seed": seed, "duration": dur, **base, "prompt": unit_prompt(u, tail),
                                    "reference_images": refs + [f"img_f/f_{n}_a.png" for n, *_ in shots]})
        if "--gf2" in sys.argv:      # first-frame jobs with a slim prompt: motion + camera + sound only, nothing that is outside the frame
            req = "要求：全片只有这一个镜头，从头到尾机位固定，不切镜、不换角度、不叠化；画面延续首帧的样子（写实的电影画面，35mm 胶片质感）；没有任何字幕、水印；人物不看镜头。"
            for n, (who, dur, text, extra) in SHOT.items():
                for seed in (9301, 9302):
                    job = {"name": f"{n}_{'GFL2' if n in LASTF else 'GF2'}_s{seed}", "shot": n, "variant": "GFL2" if n in LASTF else "GF2", "seed": seed, "duration": dur, **base,
                           "prompt": "\n".join(["镜头：" + text, sound(extra), req]), "first_frame": f"img_f/f_{n}_a.png"}
                    if n in LASTF:
                        job["last_frame"] = f"img_f/f_{n}_b.png"
                    write("jobs11", job)
        if "--gf" in sys.argv:
            for n, (who, dur, _t, _e) in SHOT.items():
                for seed in (9201, 9202):
                    job = {"name": f"{n}_{'GFL' if n in LASTF else 'GF'}_s{seed}", "shot": n, "variant": "GFL" if n in LASTF else "GF", "seed": seed, "duration": dur, **base,
                           "prompt": shot_prompt(n), "first_frame": f"img_f/f_{n}_a.png"}
                    if n in LASTF:
                        job["last_frame"] = f"img_f/f_{n}_b.png"
                    write("jobs10", job)

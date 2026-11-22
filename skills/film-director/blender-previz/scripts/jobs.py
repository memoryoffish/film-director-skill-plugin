"""Prompt and job templates for feeding a white model to a video model. These are the wordings that were tested (see ../examples).

    from jobs import unit_job, shot_job, ref_job, wm_guide, key_guide, video_guide, still_guide

A unit = one generation holding several shots, cut at the times of the shot list. A job is a dict; write it with save(job, "jobs").
Text blocks (style, people, props, scene, sound) are yours: one paragraph each, starting with its label ("风格：…", "人物：…").
People and props that have a reference image get no appearance text: the 参考图 line says who or what each image is.
Jobs are written for Wan 3.0; model="seedance-2.5" rewrites one for Seedance 2.5 (no seed, "720p", images called @图片N, no
reference video).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BASE = dict(resolution="720P", ratio="16:9", audio=True, prompt_extend=False)
REQ_UNIT = "要求：画面里没有任何字幕、水印；除了写明的文字，没有别的可读文字。人物视线按分镜表写的方向看，不看镜头。"
REQ_SHOT = "要求：全片只有这一个镜头，从头到尾{camera}，不切镜、不换角度、不叠化；画面延续首帧的样子；没有任何字幕、水印；人物不看镜头。"
REQ_ONE = "要求：全片只有这一个镜头，从头到尾{camera}，不切镜、不换角度、不叠化；画面里没有任何字幕、水印；除了写明的文字，没有别的可读文字；人物不看镜头。"


def schedule(shots) -> str:
    """shots = [(t0, t1, camera, picture), …] with times inside the unit, starting at 0."""
    n, end = len(shots), shots[-1][1]
    lines = [f"本单元共 {n} 个镜头，剧情时长 {end:.2f} 秒；下面所有时间都是成片内的秒数，从 0 开始。成片必须按分镜时间表剪接成这 {n} 个镜头：相邻镜头交界的秒数就是切点，"
             "切点处机位与景别立即改变；表中没有的切点不要加，表中有的切点不能省，不合并、不调换，只用硬切，没有叠化。",
             f"{end:.2f} 秒之后直到成片结束，延续最后一个镜头的画面与运动，不要切到新镜头。"]
    for i, (a, b, cam, pic) in enumerate(shots):
        lines.append(f"镜头{i + 1}｜{a:.2f}–{b:.2f} 秒｜机位与景别：{cam}｜{'开场' if i == 0 else '以“硬切”从上一镜头切入'}\n  画面：{pic}")
    return "\n".join(lines)


def ref_line(names) -> str:
    """names = what reference images 1..n show, in order: ["阿杰", "小周", "那张墨绿色沙发"]."""
    return ("参考图：" + "，".join(f"图{i + 1}是{n}" for i, n in enumerate(names)) +
            "。每张图只用来锁住这个人（或这件东西）的长相、衣服和颜色；不照搬图里的背景、构图、光线、姿势和视线。")


def wm_guide(first: int, n: int, legend: str) -> str:
    """White-model stills as reference images first..first+n-1, one per shot. legend says what each coloured thing stands for:
    "蓝色人偶的位置、朝向、姿势和动作就是阿杰的，红色人偶的就是小周的，绿色方块就是沙发的位置和方向"."""
    if n == 1:
        return (f"图{first}是这个镜头开头的白模站位示意图，只用来定机位、构图和站位：{legend}，门、墙、地面的位置和透视也照它。"
                "不要把人偶、白模的纯色质感、胸前的白牌画进成片；人和东西的样子用前面几张参考图，场景的样子按文字写的来。")
    idx, sh = "、".join(f"图{first + i}" for i in range(n)), "、".join(f"镜头{i + 1}" for i in range(n))
    return (f"{idx}依次是{sh}开头的白模站位示意图，只用来定每个镜头的机位、构图和站位：{legend}，门、墙、地面的位置和透视也照它。"
            "不要把人偶、白模的纯色质感、胸前的白牌画进成片；人和东西的样子用前面几张参考图，场景的样子按文字写的来。")


def key_guide(first: int, n: int) -> str:
    """Realistic keyframes (white model turned into film stills) as reference images, one per shot."""
    if n == 1:
        return (f"图{first}是这个镜头开头的画面参考（同一个地方、同样的人和东西）：机位、景别、构图、每个人的位置和朝向都照这张图；"
                "人的长相和衣服以前面的人物参考图为准。")
    idx, sh = "、".join(f"图{first + i}" for i in range(n)), "、".join(f"镜头{i + 1}" for i in range(n))
    return (f"{idx}依次是{sh}开头的画面参考（同一个地方、同样的人和东西）：每个镜头的机位、景别、构图、每个人的位置和朝向都照对应的那张图；"
            "人的长相和衣服以前面的人物参考图为准。")


def video_guide(n: int, legend: str) -> str:
    """The unit's (or the one shot's) white-model previz as the reference video."""
    what = "这个镜头的白模预演" if n == 1 else f"这个单元的白模预演（{n} 个镜头，切点和上面的时间表一致）"
    return (f"视频1是{what}，只用来定{'' if n == 1 else '每个镜头的'}机位、运镜、构图、站位、走位的路线和先后{'' if n == 1 else '、切点'}：{legend}。"
            "人偶只表示位置和朝向，不提供肢体动作：不要把人偶、白模的纯色质感、滑行和僵硬的姿势画进成片，人按真人自然地走和动；"
            "人和东西的样子用参考图，场景和光按文字写的来；最终画面正常彩色。")


def still_guide(index: int, legend: str) -> str:
    """With a capsule previz as the reference video: one jointed-mannequin still of the first frame as reference image `index`,
    so the shot does not open with everyone standing like a pillar. legend as in wm_guide."""
    return (f"图{index}是这个镜头第一帧的白模站位示意图（和视频1同一个机位、同一时刻，只是人偶带了四肢），只用来定开头每个人的位置、朝向和姿势：{legend}。"
            "不要把人偶、白模的纯色质感、胸前的白牌画进成片；人的样子用前面的人物参考图，场景的样子按文字写的来。")


def for_model(job: dict, model: str | None) -> dict:
    """Rewrite a Wan 3.0 job for another model. Only Seedance 2.5 differs: no seed, lower-case resolution, image N called @图片N,
    and no reference video."""
    if not model or model.lower().startswith("wan"):
        return job
    if not model.lower().startswith("seedance"):
        raise ValueError(f"no template for model {model}")
    if job.get("reference_video"):
        raise ValueError("Seedance takes no reference video: feed reference images, or a first (and last) frame")
    job = {k: v for k, v in job.items() if k != "seed"}
    job["model"], job["resolution"] = model, job["resolution"].lower()
    job["prompt"] = re.sub(r"图(\d+)", r"@图片\1", job["prompt"])
    return job


def unit_job(name, shots, blocks, ref_names, refs, guide, seed, duration, extra_refs=(), video=None, head=(), model=None):
    """One multi-shot generation. refs = files of the character / prop reference images (same order as ref_names);
    extra_refs = the per-shot stills the guide talks about (they follow refs, so their numbers start at len(refs) + 1);
    video = previz clip for video_guide; head = extra lines after the schedule header (e.g. which shot is in which place)."""
    parts = schedule(shots).split("\n")
    prompt = "\n".join([*parts[:2], *head, *parts[2:], "", blocks[0], ref_line(ref_names), *blocks[1:], REQ_UNIT, guide])
    job = {"name": name, "seed": seed, "duration": duration, **BASE, "prompt": prompt, "reference_images": [*refs, *extra_refs]}
    if video:
        job["reference_video"] = video
    return for_model(job, model)


def ref_job(name, text, blocks, ref_names, refs, guide, seed, duration, extra_refs=(), video=None, camera="机位固定", model=None):
    """One shot from reference images (people and props, then this shot's white-model still or keyframe) and/or a previz clip.
    text = this shot's camera and action ("近景，固定机位。她…"); guide = wm_guide(len(refs)+1, 1, …) or key_guide(len(refs)+1, 1)
    for a still, video_guide(1, …) for a previz clip, and + still_guide(len(refs)+1, …) when a first-frame still goes with it."""
    prompt = "\n".join(["镜头：" + text, "", blocks[0], ref_line(ref_names), *blocks[1:], REQ_ONE.format(camera=camera), guide])
    job = {"name": name, "seed": seed, "duration": duration, **BASE, "prompt": prompt, "reference_images": [*refs, *extra_refs]}
    if video:
        job["reference_video"] = video
    return for_model(job, model)


def shot_job(name, text, sound, first_frame, seed, duration, last_frame=None, camera="机位固定", model=None):
    """One shot from a first frame, and a last frame when the shot has to end in a set state (where someone lands, which way a
    door has opened, which way a head has turned, who has come in). Give the last frame's file explicitly; it must be a
    different picture from the first. The prompt is slim on purpose: what moves, what the camera does, the sound. Nothing
    that is not visible in the frame: describe it and the model cuts or drifts to show it."""
    if last_frame is not None and Path(last_frame) == Path(first_frame):
        raise ValueError(f"{name}: the last frame is the first frame; with nothing to move to, give no last frame")
    job = {"name": name, "seed": seed, "duration": duration, **BASE,
           "prompt": "\n".join(["镜头：" + text, sound, REQ_SHOT.format(camera=camera)]), "first_frame": first_frame}
    if last_frame:
        job["last_frame"] = last_frame
    return for_model(job, model)


def save(job, folder="jobs"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    (Path(folder) / f"{job['name']}.json").write_text(json.dumps(job, ensure_ascii=False, indent=1))
    return job

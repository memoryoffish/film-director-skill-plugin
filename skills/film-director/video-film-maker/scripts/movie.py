#!/usr/bin/env python3
"""Run a movie plan: several Wan calls joined with different transitions (see transitions/movie.md).

    python3 movie.py PLAN.json OUT_DIR

Each call in the plan has a mode (`t2v`, `refs` = reference images of the identity, or `extension` = continue the
last few seconds of an earlier call), a timeline, and how it joins the next call (`seam_out`) and the previous one
(`seam_in`): `occlusion` (both sides covered, blended inside the cover), `color` (both sides filled by one colour,
hard cut) or `extension` (the call repeats its input, cut right after the repeat; when the copy runs slow and stops
matching before the input's end, the source is cut at the last frame the copy still reproduces). After every generation the
seams it takes part in are checked (tail/head covered, colour fill, Wan's own cuts next to a seam); a failing
take is regenerated with the next seed, up to `takes`. Independent calls are generated in parallel.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import occut  # noqa: E402
import wan  # noqa: E402

FILL = 0.80          # share of the frame one colour must cover for a colour cut
DISSOLVE = 6         # frames blended inside an occlusion seam
EXT_MATCH_MIN = 24.0  # dB (480 px wide): the extension seam is cut where Wan's copy reproduces the source this well;
                      # at 24 the jump is about one frame of motion (mean abs diff 8-13), at 20 it pops (17, brighter)
MODES = {"t2v", "refs", "extension"}


def red_fraction(rgb: np.ndarray) -> float:
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return float((((h < 10) | (h > 170)) & (s > 90) & (v > 40)).mean())


def validate(plan: dict) -> None:
    names = []
    for c in plan["calls"]:
        if c.get("mode") not in MODES:
            raise ValueError(f"{c.get('name')}: mode must be one of {sorted(MODES)}")
        if c["mode"] == "extension" and c.get("of") not in names:
            raise ValueError(f"{c['name']}: an extension must continue an earlier call (`of`)")
        if c["mode"] == "refs" and not plan.get("identity_refs"):
            raise ValueError(f"{c['name']}: refs mode needs plan.identity_refs")
        if not 2 <= int(c["duration"]) <= wan.MAX_CLIP_S:
            raise ValueError(f"{c['name']}: duration must be 2-{wan.MAX_CLIP_S} s")
        names.append(c["name"])
    for a, b in zip(plan["calls"], plan["calls"][1:]):
        if a.get("seam_out", {}).get("method") != b.get("seam_in", {}).get("method"):
            raise ValueError(f"{a['name']} -> {b['name']}: seam_out and seam_in disagree")


def color_frames(frames: np.ndarray, rng: range) -> list[int]:
    return [i for i in rng if red_fraction(frames[i]) >= FILL]


def job_for(plan: dict, call: dict, take: int, out_dir: Path, accepted: dict) -> dict:
    job = {**plan.get("defaults", {}), "name": call["name"] if take == 1 else f"{call['name']}_t{take}",
           "duration": int(call["duration"]), "prompt": call["prompt"]}
    if job.get("seed") is not None:
        job["seed"] = int(job["seed"]) + take - 1
    if call["mode"] == "refs":
        job.update(reference_images=plan["identity_refs"], ratio="16:9")
    elif call["mode"] == "extension":
        src = accepted[call["of"]]
        n = occut.frame_count(Path(src["clip"]))
        k = int(round(float(call.get("input_s", 3)) * 30))
        excerpt = out_dir / "inputs" / f"{job['name']}_input.mp4"
        excerpt.parent.mkdir(parents=True, exist_ok=True)
        occut.join([{"clip": src["clip"], "start": n - k, "end": n - 1}], excerpt)
        job.update(reference_video=str(excerpt), ratio="adaptive")
    return job


def check(call: dict, clip: Path, accepted: dict, out_dir: Path, next_input_s: float = 3.0) -> dict:
    """Where this call starts and ends in the film, and what is wrong with it."""
    frames, fps = occut.decode(clip, width=480)
    n, problems = len(frames), []
    start, end = 0, n - 1
    seam_in, seam_out = call.get("seam_in", {}), call.get("seam_out", {})
    src_end = None
    if seam_in.get("method") == "extension":
        src, _ = occut.decode(Path(accepted[call["of"]]["clip"]), width=480)
        limit = int(round((float(call.get("input_s", 3)) + 2) * fps))
        # Wan's copy of the input often runs slow and stops matching before the input's last frame: cut the
        # source at the last frame the copy still reproduces and go on right after it in the copy.
        for src_end in range(len(src) - 1, len(src) - 1 - int(round(float(call.get("input_s", 3)) * fps)), -1):
            k, score = occut.match_frame(src[src_end], frames, limit)
            if score >= EXT_MATCH_MIN:
                break
        else:  # Wan redrew its input instead of copying it: any cut would jump
            src_end, (k, score) = None, occut.match_frame(src[-1], frames, limit)
            problems.append(f"extension does not repeat its input (best match {score} dB at frame {k})")
        start = k + 1
    elif seam_in.get("method") == "occlusion":
        head = occut.head_cover(clip, leak_max=float(call.get("head_leak_max", occut.HEAD_LEAK_MAX)))
        if head:
            start = head[0]
        else:
            problems.append("head not covered")
    elif seam_in.get("method") == "color":
        hits = color_frames(frames, range(0, min(n, int(1.5 * fps))))
        if hits:
            start = hits[-1]  # the last fully red frame, so the reveal follows right after the cut
        else:
            problems.append("head not filled with the colour")
    w0 = seam_out.get("window_s", [call["duration"] - 2, call["duration"]])[0]
    if seam_out.get("method") == "occlusion":
        tail = occut.tail_report(clip, out_dir / "cuts", window_s=max(1.0, n / fps - w0 + 0.5))
        end = tail["cut"]
        if not tail["covered"]:
            problems.append(f"tail not covered (leak {tail['cut_frame']['leak']})")
    elif seam_out.get("method") == "color":
        hits = color_frames(frames, range(max(0, int((w0 - 0.5) * fps)), n))
        if hits:
            end = hits[0]  # the first fully red frame: cut as soon as the colour fills the frame
        else:
            problems.append("tail not filled with the colour")
    # Wan may cut inside a clip; only the seconds a seam relies on must be free of it: the head right after the
    # incoming seam (ramp and dissolve for occlusion), the cover/colour window, or the input the next extension copies.
    head_s = 0.0 if not seam_in else occut.RAMP_S if seam_in.get("method") == "occlusion" else occut.SEAM_GUARD_S
    tail_s = (0.0 if not seam_out else next_input_s if seam_out.get("method") == "extension"
              else max(occut.SEAM_GUARD_S, end / fps - w0))
    own = occut.own_cuts(clip, out_dir / "owncuts", start, end)
    near = occut.seam_cuts(own, head_s, tail_s)
    problems += [f"Wan own cut at frame {c['frame']} next to a seam" for c in near]
    return {"clip": str(clip), "start": start, "end": end, "problems": problems, "src_end": src_end,
            "own_cut_candidates": [c for c in own["candidates"] if c not in near]}


def run_call(plan: dict, call: dict, out_dir: Path, client, accepted: dict, report: dict) -> dict | None:
    for take in range(1, int(plan.get("takes", 1)) + 1):
        job = job_for(plan, call, take, out_dir, accepted)
        state = wan.run_job(job, out_dir / "clips", client)
        clip = out_dir / "clips" / f"{job['name']}.mp4"
        nxt = next((c for c in plan["calls"] if c.get("of") == call["name"] and c["mode"] == "extension"), {})
        res = {**check(call, clip, accepted, out_dir, float(nxt.get("input_s", 3))), "take": take, "task_id": state.get("task_id"),
               "mode": call["mode"]}
        report.setdefault(call["name"], []).append(res)
        wan.log("movie_take", call=call["name"], take=take, start=res["start"], end=res["end"], problems=res["problems"])
        if not res["problems"]:
            return res
    return None


def run(plan: dict, out_dir: Path, client) -> dict:
    validate(plan)
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    accepted, report = {}, {}
    calls = plan["calls"]
    independent = [c for c in calls if c["mode"] != "extension"]
    with ThreadPoolExecutor(max_workers=int(plan.get("workers", 4))) as pool:
        futures = {c["name"]: pool.submit(run_call, plan, c, out_dir, client, accepted, report) for c in independent
                   if c.get("seam_in", {}).get("method") != "extension"}
        for name, f in futures.items():
            accepted[name] = f.result()
    for c in calls:  # extensions (and anything depending on them) in order
        if c["name"] in accepted:
            continue
        if c["mode"] == "extension" and not accepted.get(c["of"]):
            accepted[c["name"]] = None
            continue
        accepted[c["name"]] = run_call(plan, c, out_dir, client, accepted, report)
    result = {"report": report, "accepted": accepted}
    failed = [c["name"] for c in calls if not accepted.get(c["name"])]
    if failed:
        result["stopped"] = f"no acceptable take for {failed}"
    else:
        result["film"] = assemble(plan, accepted, out_dir)
    (out_dir / "movie.json").write_text(json.dumps(result, ensure_ascii=False, indent=1))
    return result


def assemble(plan: dict, accepted: dict, out_dir: Path) -> dict:
    segs, calls = [], plan["calls"]
    for i, c in enumerate(calls):
        a = accepted[c["name"]]
        seg = {"clip": a["clip"], "start": a["start"], "end": a["end"],
               "label": f"第 {i + 1} 次调用 · {c.get('label', c['mode'])} · {c['duration']}s · 共生成 {a['take']} 次"}
        if i and c.get("seam_in", {}).get("method") == "occlusion":
            prev = accepted[calls[i - 1]["name"]]
            seam = occut.seam_report(Path(prev["clip"]), prev["end"], Path(a["clip"]), out_dir / "seams",
                                     b_skip=a["start"], tag=c["name"])
            seg.update(occut.head_ramp(seam), dissolve=int(plan.get("dissolve_frames", DISSOLVE)))
        if i and a.get("src_end") is not None and c.get("of") == calls[i - 1]["name"]:
            segs[-1]["end"] = min(segs[-1]["end"], a["src_end"])  # the source ends where the copy stops matching
        segs.append(seg)
    clean = occut.join([{k: v for k, v in s.items() if k != "label"} for s in segs], out_dir / "film_raw.mp4")
    occut.join(segs, out_dir / "film_raw_labeled.mp4")
    fin = [occut.finish(out_dir / f"film_raw{t}.mp4", out_dir / f"{plan.get('film_name', 'movie')}{t}.mp4",
                        plan.get("target_s"), float(plan.get("fade_in_s", 0)), float(plan.get("fade_out_s", 0)),
                        plan.get("trim_from", "end")) for t in ("", "_labeled")]
    return {"joined": clean, "film": fin[0], "labeled": fin[1]}


if __name__ == "__main__":
    plan_path, out = Path(sys.argv[1]), Path(sys.argv[2])
    print(json.dumps({k: v for k, v in run(json.loads(plan_path.read_text()), out,
                                           wan.Client(wan.read_key())).items() if k != "report"},
                     ensure_ascii=False, indent=1, default=str))

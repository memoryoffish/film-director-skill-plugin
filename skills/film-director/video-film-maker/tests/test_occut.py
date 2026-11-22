"""Offline tests (no network, no billing). Run: python3 -m pytest -q tests/"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import occut  # noqa: E402
import wan  # noqa: E402

RNG = np.random.default_rng(0)
W, H, FPS = 192, 108, 30


def texture(seed: int, w: int = W * 2, h: int = H) -> np.ndarray:
    r = np.random.default_rng(seed).integers(0, 255, (h // 6 + 1, w // 6 + 1, 3), dtype=np.uint8)
    return np.kron(r, np.ones((6, 6, 1), dtype=np.uint8))[:h, :w]


def write_video(path: Path, frames: list[np.ndarray], audio: bool = True) -> Path:
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={len(frames) / FPS}", "-shortest", "-c:a", "aac"]
    cmd += ["-c:v", "libx264", "-qp", "0", "-pix_fmt", "yuv444p", str(path)]
    subprocess.run(cmd, input=np.stack(frames).tobytes(), check=True)
    return path


def panning(seed: int, n: int, step: int) -> list[np.ndarray]:
    """The picture moves left by `step` px per frame (a camera moving right)."""
    tex = texture(seed)
    return [np.ascontiguousarray(tex[:, i * step:i * step + W]) for i in range(n)]


def occluded_clip(path: Path, n_open: int = 40, n_cover: int = 8) -> Path:
    frames = panning(1, n_open, 2) + [np.full((H, W, 3), 20 + (i % 2), np.uint8) for i in range(n_cover)]
    return write_video(path, frames)


# ---------- wan.py ----------

def job(tmp_path: Path, **kw) -> dict:
    return {"name": "x", "prompt": "a shot", "duration": 5, "resolution": "720P", **kw}


@pytest.mark.parametrize("duration", [1, 16, 30])
def test_duration_outside_cap_is_rejected(tmp_path, duration):
    with pytest.raises(ValueError):
        wan.build_payload(job(tmp_path, duration=duration))


def test_text_only_payload_defaults():
    body = wan.build_payload({"name": "x", "prompt": "p", "duration": 15})
    assert body["model"] == "wan3.0-video"  # standard queue by default
    assert "media" not in body["input"]
    assert body["parameters"] == {"resolution": "1080P", "ratio": "16:9", "duration": 15, "audio": True,
                                  "prompt_extend": False, "watermark": False}


def test_first_frame_is_a_file_reference_until_sent(tmp_path):
    img = tmp_path / "f.png"
    img.write_bytes(b"\x89PNG fake")
    body = wan.build_payload(job(tmp_path, first_frame=img, seed=3))
    m = body["input"]["media"][0]
    assert m["type"] == "first_frame" and m["path"] == str(img) and "url" not in m
    assert body["parameters"]["ratio"] == "adaptive" and body["parameters"]["seed"] == 3
    wire = wan.wire_payload(body)
    assert wire["input"]["media"][0]["url"].startswith("data:image/png;base64,")
    assert "path" in body["input"]["media"][0]  # the planned payload is not mutated
    img.write_bytes(b"\x89PNG other")
    with pytest.raises(RuntimeError):
        wan.wire_payload(body)


def test_read_key_parses_export_and_quotes(tmp_path, monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    f = tmp_path / ".env"
    f.write_text("OTHER=1\nexport DASHSCOPE_API_KEY='sk-abc'\n")
    assert wan.read_key([tmp_path / "missing", f]) == "sk-abc"
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-env")
    assert wan.read_key([f]) == "sk-env"


def test_reference_video_is_uploaded_and_cannot_mix_with_frames(tmp_path):
    vid, img = tmp_path / "a.mp4", tmp_path / "f.png"
    vid.write_bytes(b"mp4"); img.write_bytes(b"png")
    with pytest.raises(ValueError):
        wan.build_payload(job(tmp_path, first_frame=img, reference_video=vid))
    body = wan.build_payload(job(tmp_path, reference_video=vid, duration=13))
    with pytest.raises(RuntimeError):
        wan.wire_payload(body)
    wire = wan.wire_payload(body, upload=lambda p: "oss://dashscope-instant/x/" + Path(p).name)
    assert wire["input"]["media"] == [{"type": "reference_video", "url": "oss://dashscope-instant/x/a.mp4"}]


def test_reference_images_keep_their_order_and_exclude_first_frame(tmp_path):
    a, b = tmp_path / "a.png", tmp_path / "b.jpg"
    a.write_bytes(b"png"); b.write_bytes(b"jpg")
    body = wan.build_payload(job(tmp_path, reference_images=[a, b]))
    assert [m["type"] for m in body["input"]["media"]] == ["reference_image"] * 2
    wire = wan.wire_payload(body)
    assert wire["input"]["media"][0]["url"].startswith("data:image/png") and wire["input"]["media"][1]["url"].startswith("data:image/jpeg")
    with pytest.raises(ValueError):
        wan.build_payload(job(tmp_path, reference_images=[a], first_frame=b))


def test_multipart_body_carries_fields_and_file(tmp_path):
    f = tmp_path / "v.mp4"
    f.write_bytes(b"VIDEOBYTES")
    body, ctype = wan.multipart({"key": "dir/v.mp4", "policy": "p"}, "file", f)
    boundary = ctype.split("boundary=")[1]
    assert body.count(f"--{boundary}".encode()) == 4 and body.endswith(f"--{boundary}--\r\n".encode())
    assert b'name="key"\r\n\r\ndir/v.mp4' in body and b'filename="v.mp4"' in body and b"VIDEOBYTES" in body


class FakeClient:
    def __init__(self, video: Path | None = None):
        self.calls, self.video = [], video

    def request(self, method, path, payload=None, oss=False):
        self.calls.append((method, path))
        if method == "POST":
            return {"output": {"task_id": "t1", "task_status": "PENDING"}, "request_id": "r1"}
        return {"output": {"task_status": "SUCCEEDED", "video_url": "u", "usage": {"duration": 2.0}}}

    def download(self, url, dst):
        dst.write_bytes(self.video.read_bytes())


def test_lost_acknowledgement_is_never_replayed(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "x.json").write_text(json.dumps({"name": "x", "payload": wan.build_payload(job(tmp_path)),
                                            "status": "dispatching"}))
    client = FakeClient()
    with pytest.raises(RuntimeError, match="review"):
        wan.run_job(job(tmp_path), out, client)
    assert client.calls == []


def test_run_job_submits_once_then_resumes_by_task_id(tmp_path):
    video = occluded_clip(tmp_path / "v.mp4")
    client = FakeClient(video)
    state = wan.run_job(job(tmp_path), tmp_path / "out", client, poll_s=0)
    assert state["status"] == "DOWNLOADED" and state["task_id"] == "t1"
    assert [c[0] for c in client.calls] == ["POST", "GET"]
    again = FakeClient(video)
    wan.run_job(job(tmp_path), tmp_path / "out", again)
    assert again.calls == []  # already downloaded
    with pytest.raises(RuntimeError, match="new name"):
        wan.run_job(job(tmp_path, prompt="another shot"), tmp_path / "out", again)


# ---------- measures ----------

def test_choose_cut_takes_the_latest_least_informative_covered_frame():
    kb = [5.0, 20, 20, 9, 4, 4, 12]
    lk = [1.0, 30, 30, 5, 40, 3, 2]  # frame 4 compresses best but leaks background
    assert occut.choose_cut(kb, lk, fps=1, window_s=4) == 5
    assert occut.choose_cut(kb, lk, fps=1, window_s=1) == 6
    assert occut.choose_cut(kb, [30.0, 30, 30, 20, 25, 20, 22], fps=1, window_s=4) == 5  # none covered


def test_leak_flags_background_at_one_edge():
    cover = np.full((H, W, 3), 40, np.uint8)
    cover[:, :, 0] = 50  # a dark reddish occluder
    open_edge = cover.copy()
    open_edge[:, : W // 8] = (230, 200, 60)  # bright yellow leaves showing on the left
    assert occut.leak(cover) < 1 < occut.LEAK_MAX < occut.leak(open_edge)


def test_flat_frame_compresses_far_smaller_than_texture():
    flat = occut.frame_info(np.full((H, W, 3), 30, np.uint8))
    busy = occut.frame_info(texture(2)[:, :W])
    assert flat["kb"] < 0.35 * busy["kb"] and flat["std"] < 1 < busy["std"]


@pytest.mark.parametrize("step,sign", [(3, -1), (-3, 1)])
def test_motion_sign_follows_camera_direction(step, sign):
    frames = np.stack(panning(3, 12, abs(step)) if step > 0 else panning(3, 12, 3)[::-1])
    m = occut.motion(frames, FPS)
    assert np.sign(m["dx"]) == sign and abs(m["dx"]) > occut.STILL


def test_still_picture_has_no_motion():
    frames = np.stack([texture(4)[:, :W]] * 10)
    assert abs(occut.motion(frames, FPS)["dx"]) < occut.STILL


def test_scene_score_separates_hard_cut_from_continuous_motion():
    frames = np.stack(panning(5, 10, 2) + panning(6, 10, 2))
    s = occut.scene_scores(frames, FPS)
    assert len(s) == 20
    assert s[10] > occut.HARD_CUT and max(s[1:10] + s[11:]) < occut.HARD_CUT


# ---------- tail / seam / join ----------

def test_tail_finds_the_covered_stretch(tmp_path):
    clip = occluded_clip(tmp_path / "a.mp4", n_cover=20)
    rep = occut.tail_report(clip, tmp_path / "cuts", window_s=1.0)
    assert rep["covered"] and rep["cut"] >= 40 and rep["first_covered_s"] == pytest.approx(40 / FPS, abs=0.04)
    assert Path(rep["cut_png"]).exists() and (tmp_path / "cuts" / "a_tail.png").exists()
    assert rep["motion_into_cut"]["dx"] > -occut.STILL  # it ends on a held cover: nothing moves into the cut


def test_tail_of_open_clip_is_not_covered(tmp_path):
    clip = write_video(tmp_path / "o.mp4", panning(7, 40, 2))
    assert not occut.tail_report(clip, tmp_path / "cuts", 1.0)["covered"]


def test_seam_hard_cut_vs_continued_motion(tmp_path):
    a = write_video(tmp_path / "a.mp4", panning(8, 30, 2))
    b_cont = write_video(tmp_path / "b.mp4", panning(8, 60, 2)[29:])  # B starts on A's last frame
    b_new = write_video(tmp_path / "c.mp4", panning(9, 30, 2))
    cont = occut.seam_report(a, 29, b_cont, tmp_path / "s", b_skip=1)
    hard = occut.seam_report(a, 29, b_new, tmp_path / "s", b_skip=0)
    assert cont["seam_scene_score"] < occut.HARD_CUT < hard["seam_scene_score"]
    assert cont["same_direction"] and cont["speed_ok"] and cont["b_first_vs_a_cut_psnr"] > 40
    assert cont["covered_total_s"] == 0
    ext = write_video(tmp_path / "e.mp4", panning(8, 60, 2)[10:])  # an extension repeating A's frames 10..29
    rep = occut.seam_report(a, 29, ext, tmp_path / "s", b_skip=None)
    assert rep["matched"]["b_index"] == 19 and rep["b_skip"] == 20 and rep["seam_scene_score"] < occut.HARD_CUT
    b_back = write_video(tmp_path / "d.mp4", panning(8, 60, 2)[29:][::-1])
    assert not occut.seam_report(a, 29, b_back, tmp_path / "s")["same_direction"]


def test_seam_counts_the_covered_stretch_on_both_sides(tmp_path):
    a = occluded_clip(tmp_path / "a.mp4", n_open=30, n_cover=6)
    b = write_video(tmp_path / "b.mp4", [np.full((H, W, 3), 20, np.uint8)] * 4 + panning(12, 20, 2))
    rep = occut.seam_report(a, 35, b, tmp_path / "s", b_skip=1)
    assert (rep["covered_a_frames"], rep["covered_b_frames"]) == (6, 3)
    assert rep["covered_total_s"] == pytest.approx(9 / FPS, abs=1e-3)


def test_join_is_frame_exact_and_keeps_audio(tmp_path):
    a = write_video(tmp_path / "a.mp4", [np.full((H, W, 3), 10 * i, np.uint8) for i in range(20)])
    b = write_video(tmp_path / "b.mp4", [np.full((H, W, 3), 200 + 2 * i, np.uint8) for i in range(20)], audio=False)
    rep = occut.join([{"clip": str(a), "start": 0, "end": 14}, {"clip": str(b), "start": 1, "end": 19}],
                     tmp_path / "j.mp4")
    frames, _ = occut.decode(tmp_path / "j.mp4", width=W)
    assert len(frames) == 15 + 19 and rep["info"]["audio"]
    assert abs(float(frames[14].mean()) - 140) < 4 and abs(float(frames[15].mean()) - 202) < 4
    assert rep["duration_s"] == pytest.approx(34 / FPS, abs=1e-3)
    assert rep["info"]["duration"] == pytest.approx(34 / FPS, abs=0.06)


def test_shot_job_names_takes_and_moves_the_seed():
    board = {"defaults": {"resolution": "720P", "seed": 10}}
    shot = {"name": "s2", "prompt": "p", "duration": 12, "end": "occlude"}
    j1 = occut.shot_job(board, shot, 1, "cut.png")
    j3 = occut.shot_job(board, shot, 3, None)
    assert (j1["name"], j1["seed"], j1["first_frame"]) == ("s2", 10, "cut.png") and "end" not in j1
    assert (j3["name"], j3["seed"]) == ("s2_t3", 12) and "first_frame" not in j3


def test_ramp_mapping_is_continuous_and_eases_to_normal_speed():
    k, T = 2.0, 1.2
    assert occut.ramp_source(0.0, k, T) == 0
    assert occut.ramp_source(0.01, k, T) == pytest.approx(0.02, rel=0.02)  # k times fast at the start
    assert occut.ramp_source(T, k, T) == pytest.approx(T * (k + 1) / 2)
    late = occut.ramp_source(3.0, k, T) - occut.ramp_source(2.9, k, T)
    assert late == pytest.approx(0.1)  # back to 1x
    assert occut.ramp_source(0.5, 1.0, T) == 0.5


def test_join_speeds_up_the_head_and_keeps_the_tail_in_sync(tmp_path):
    a = write_video(tmp_path / "a.mp4", [np.full((H, W, 3), 4 * i, np.uint8) for i in range(60)])
    rep = occut.join([{"clip": str(a), "start": 0, "end": 59, "head_speed": 2.0, "ramp_s": 0.5}], tmp_path / "r.mp4")
    frames, _ = occut.decode(tmp_path / "r.mp4", width=W)
    shown = [round(float(f.mean()) / 4) for f in frames]
    assert len(frames) == rep["segments"][0]["frames_out"] == 60 - 8
    assert shown[0] == 0 and shown[1] >= 2 and shown[-1] == 59
    assert all(b >= a for a, b in zip(shown, shown[1:]))
    assert all(b - a == 1 for a, b in zip(shown[30:], shown[31:]))


def test_take_problems_follow_the_checklist():
    tail_ok = {"covered": True, "cut_frame": {"leak": 3.0}}
    tail_bad = {"covered": False, "cut_frame": {"leak": 30.0}}
    seam = lambda a, b: {"motion_into_cut": {"dx": a}, "motion_out_of_cut": {"dx": b}}
    assert occut.take_problems(None, tail_ok) == []
    assert occut.take_problems(None, tail_bad) == ["tail not covered (leak 30.0)"]
    assert occut.take_problems(seam(-0.4, -0.2), None) == []
    assert occut.take_problems(seam(-0.4, 0.2), None) == ["B moves the other way"]
    assert occut.take_problems(seam(-0.4, 0.0), None) == ["B starts still"]
    assert occut.take_problems(seam(0.0, 0.3), None) == []  # A held still into the cut: nothing to match


def test_head_ramp_only_for_slow_starts():
    assert occut.head_ramp(None) == {} and occut.head_ramp({"speed_ratio": 0.9}) == {}
    assert occut.head_ramp({"speed_ratio": 0.5}) == {"head_speed": 2.0, "ramp_s": occut.RAMP_S}
    assert occut.head_ramp({"speed_ratio": 0.2})["head_speed"] == occut.RAMP_MAX


def test_chain_retakes_a_take_that_is_not_covered(tmp_path, monkeypatch):
    open_clip = write_video(tmp_path / "open.mp4", panning(20, 70, 2))
    covered = occluded_clip(tmp_path / "cov.mp4", n_open=50, n_cover=20)
    tail_b = write_video(tmp_path / "b.mp4", [np.full((H, W, 3), 20, np.uint8)] * 3 + panning(21, 60, 2))
    served = {"s1": open_clip, "s1_t2": covered, "s2": tail_b}

    def fake_run_job(job, out_dir, client, poll_s=10.0):
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{job['name']}.mp4").write_bytes(served[job["name"]].read_bytes())
        return {"usage": None, "job": job}

    monkeypatch.setattr(occut.wan, "run_job", fake_run_job)
    monkeypatch.setattr(occut, "own_cuts", lambda *a, **k: {"range": [0, 0], "fps": 30.0, "candidates": []})  # synthetic covers appear in one frame
    board = {"takes": 2, "window_s": 1.0, "defaults": {"seed": 1},
             "shots": [{"name": "s1", "prompt": "a"}, {"name": "s2", "prompt": "b"}]}
    rep = occut.run_chain(board, tmp_path / "out", client=None)
    assert [(e["shot"], e["take"]) for e in rep["shots"]] == [("s1", 1), ("s1", 2), ("s2", 1)]
    assert rep["shots"][0]["problems"] and not rep["shots"][1]["problems"]
    plan = json.loads((tmp_path / "out" / "plan.json").read_text())
    assert plan[0]["clip"].endswith("s1_t2.mp4") and plan[0]["end"] == rep["shots"][1]["tail"]["cut"]
    assert plan[1]["start"] == 1 and Path(rep["film"]["out"]).exists()


def test_finish_can_trim_from_the_start_to_keep_the_ending(tmp_path):
    raw = write_video(tmp_path / "raw.mp4", [np.full((H, W, 3), 4 * i, np.uint8) for i in range(60)])
    rep = occut.finish(raw, tmp_path / "f.mp4", target_s=1.0, fade_in=0, fade_out=0, trim_from="start")
    frames, _ = occut.decode(tmp_path / "f.mp4", width=W)
    assert abs(len(frames) - 30) <= 1 and abs(float(frames[-1].mean()) - 236) < 6


def test_join_dissolve_blends_the_last_and_first_frames(tmp_path):
    a = write_video(tmp_path / "a.mp4", [np.full((H, W, 3), 40, np.uint8)] * 20)
    b = write_video(tmp_path / "b.mp4", [np.full((H, W, 3), 200, np.uint8)] * 20)
    rep = occut.join([{"clip": str(a), "start": 0, "end": 19}, {"clip": str(b), "start": 0, "end": 19, "dissolve": 4}],
                     tmp_path / "d.mp4")
    frames, _ = occut.decode(tmp_path / "d.mp4", width=W)
    levels = [float(f.mean()) for f in frames]
    assert len(frames) == 36 and rep["duration_s"] == pytest.approx(36 / FPS, abs=1e-3)
    assert abs(levels[15] - 40) < 4 and abs(levels[20] - 200) < 4
    assert [round(x) for x in levels[16:20]] == pytest.approx([72, 104, 136, 168], abs=4)  # weights 1/5 … 4/5
    assert rep["segments"][1]["placed_s"] == pytest.approx(16 / FPS, abs=1e-3)


def test_chain_reference_mode_starts_on_b_cover_and_dissolves(tmp_path, monkeypatch):
    a = occluded_clip(tmp_path / "a.mp4", n_open=50, n_cover=20)
    b = write_video(tmp_path / "b.mp4", panning(23, 1, 2) + [np.full((H, W, 3), 25, np.uint8)] * 8
                    + panning(22, 50, 2))
    seen = {}

    def fake_run_job(job, out_dir, client, poll_s=10.0):
        seen[job["name"]] = job
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{job['name']}.mp4").write_bytes(b.read_bytes())
        return {"usage": None}

    monkeypatch.setattr(occut.wan, "run_job", fake_run_job)
    monkeypatch.setattr(occut, "own_cuts", lambda *a, **k: {"range": [0, 0], "fps": 30.0, "candidates": []})
    board = {"takes": 1, "window_s": 1.0, "mode": "refs", "identity_refs": ["r1.png", "r2.png"], "dissolve_frames": 6,
             "shots": [{"name": "s1", "prompt": "a", "use_clip": str(a)}, {"name": "s2", "prompt": "b"}]}
    rep = occut.run_chain(board, tmp_path / "out", client=None)
    assert "s1" not in seen and seen["s2"]["reference_images"] == ["r1.png", "r2.png"]
    assert "first_frame" not in seen["s2"]
    assert rep["shots"][1]["head_cover"][:2] == [1, 2]  # frame 0 is not covered, the run starts at 1
    plan = json.loads((tmp_path / "out" / "plan.json").read_text())
    assert plan[1]["start"] == 1 and plan[1]["dissolve"] == 6


def can_label() -> bool:
    if not Path(occut.LABEL_FONT).exists():
        return False
    filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return " drawtext " in filters


@pytest.mark.skipif(not can_label(), reason="CJK font missing (set OCCUT_FONT) or ffmpeg built without drawtext")
def test_join_labels_mark_each_generation_call(tmp_path):
    a = write_video(tmp_path / "a.mp4", [np.full((H, W, 3), 90, np.uint8)] * 15)
    b = write_video(tmp_path / "b.mp4", [np.full((H, W, 3), 90, np.uint8)] * 15)
    occut.join([{"clip": str(a), "start": 0, "end": 14, "label": "Wan 调用 #1 · 文生 8s"},
                {"clip": str(b), "start": 0, "end": 14, "label": "Wan 调用 #2 · 参考图: 8s"}], tmp_path / "l.mp4")
    frames, _ = occut.decode(tmp_path / "l.mp4", width=W)
    assert len(frames) == 30
    strip = lambda f: f[-1, W // 2].astype(int)
    assert np.abs(strip(frames[5]) - strip(frames[20])).max() > 40  # strip colour changes at the boundary
    assert frames[5][2:12, 2:60].std() > 10 and frames[5][60:80, 80:120].std() < 3  # label only in the corner


def test_own_cuts_flags_a_cut_inside_one_clip_but_not_a_pan(tmp_path):
    pan = write_video(tmp_path / "pan.mp4", panning(30, 60, 2))
    red = [np.full((H, W, 3), (200, 40, 40), np.uint8)] * 30
    blue = [np.full((H, W, 3), (40, 60, 200), np.uint8)] * 30
    cut = write_video(tmp_path / "cut.mp4", red + blue)
    assert occut.own_cuts(pan, tmp_path / "o")["candidates"] == []
    rep = occut.own_cuts(cut, tmp_path / "o")
    assert [c["frame"] for c in rep["candidates"] if c["likely_cut"]] and abs(rep["candidates"][0]["frame"] - 30) <= 3
    assert occut.own_cuts(cut, tmp_path / "o", start=0, end=20)["candidates"] == []  # outside the used range
    assert (tmp_path / "o" / "cut_overview.png").exists()


def test_chain_retakes_when_wan_cut_inside_the_used_range(tmp_path, monkeypatch):
    frames = panning(1, 60, 1) + panning(2, 60, 1) + [np.full((H, W, 3), 20 + (i % 2), np.uint8) for i in range(20)]
    clip = write_video(tmp_path / "a.mp4", frames)  # 140 frames: room for a mid-clip cut away from both seams

    def fake_run_job(job, out_dir, client, poll_s=10.0):
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{job['name']}.mp4").write_bytes(clip.read_bytes())
        return {}

    calls = []

    def fake_own_cuts(c, out, start, end):
        calls.append((start, end))
        end = 139 if end is None else end
        # every take cuts once mid-clip (content, fine); s1's first take also cuts 0.3 s before its tail cut
        cands = [{"frame": 60, "likely_cut": True}] + ([{"frame": end - 9, "likely_cut": True}] if len(calls) == 1 else [])
        return {"range": [start, end], "fps": 30.0, "candidates": cands}

    monkeypatch.setattr(occut.wan, "run_job", fake_run_job)
    monkeypatch.setattr(occut, "own_cuts", fake_own_cuts)
    board = {"takes": 2, "window_s": 1.0, "defaults": {"seed": 1}, "shots": [{"name": "s1", "prompt": "a"}, {"name": "s2", "prompt": "b"}]}
    rep = occut.run_chain(board, tmp_path / "out", client=None)
    s1 = rep["shots"][0]
    assert s1["problems"] == [f"Wan own cut at frame {s1['tail']['cut'] - 9} next to a seam"]
    assert [(e["shot"], e["take"]) for e in rep["shots"][1:]] == [("s1", 2), ("s2", 1)]
    assert not any("frame 60" in p for e in rep["shots"] for p in e["problems"])  # a cut mid-clip is content
    assert calls[0][0] == 0 and calls[0][1] == s1["tail"]["cut"]  # only the used range is checked


def audio_rms(path: Path, t0: float, t1: float) -> float:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", str(path),
                          "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    return float(np.sqrt(np.mean(x * x)))


def test_join_audio_does_not_dip_when_the_first_clip_is_used_to_its_end(tmp_path):
    a = write_video(tmp_path / "a.mp4", panning(50, 45, 2))            # audio ends with the video
    b = write_video(tmp_path / "b.mp4", panning(51, 75, 2))
    plans = occut.audio_seams([{"end": 44}, {"start": 15}], [{"duration": 1.5, "audio": True}] * 2, 30.0, 0.25)
    assert plans == [("pre", 0.25)]
    occut.join([{"clip": str(a), "start": 0, "end": 44}, {"clip": str(b), "start": 15, "end": 74}], tmp_path / "j.mp4")
    seam, steady = audio_rms(tmp_path / "j.mp4", 1.38, 1.62), audio_rms(tmp_path / "j.mp4", 0.6, 1.1)
    assert seam > 0.75 * steady
    assert occut.audio_seams([{"end": 44}, {"start": 0}], [{"duration": 1.5, "audio": True}] * 2, 30.0, 0.25) == [("cut", 0.02)]


def test_seam_cuts_ignores_wan_cuts_away_from_the_seams():
    own = {"range": [0, 299], "fps": 30.0, "candidates": [
        {"frame": 20, "likely_cut": True}, {"frame": 150, "likely_cut": True},
        {"frame": 280, "likely_cut": True}, {"frame": 290, "likely_cut": False}]}
    assert [c["frame"] for c in occut.seam_cuts(own, head_s=1.0, tail_s=2.0)] == [20, 280]
    assert [c["frame"] for c in occut.seam_cuts(own, head_s=0.0, tail_s=0.0)] == []  # a lone clip: cuts are content
    assert [c["frame"] for c in occut.seam_cuts(own, head_s=0.0, tail_s=0.5)] == []


def test_happyhorse_picks_the_model_per_mode_and_drops_unknown_params(tmp_path):
    img = tmp_path / "f.png"; img.write_bytes(b"\x89PNG fake")
    body = wan.build_payload({"name": "x", "prompt": "p", "duration": 5, "model": "happyhorse-1.1", "resolution": "720P"})
    assert body["model"] == "happyhorse-1.1-t2v"
    assert body["parameters"] == {"resolution": "720P", "ratio": "16:9", "duration": 5, "watermark": False}
    body = wan.build_payload(job(tmp_path, first_frame=img, model="happyhorse-1.1"))
    assert body["model"] == "happyhorse-1.1-i2v" and "ratio" not in body["parameters"]
    body = wan.build_payload(job(tmp_path, reference_images=[img], model="happyhorse-1.1", seed=4))
    assert body["model"] == "happyhorse-1.1-r2v" and body["parameters"]["ratio"] == "16:9" and body["parameters"]["seed"] == 4
    with pytest.raises(ValueError):
        wan.build_payload(job(tmp_path, first_frame=img, last_frame=img, model="happyhorse-1.1"))
    with pytest.raises(ValueError):
        wan.build_payload(job(tmp_path, first_frame=img, model="happyhorse-1.1-t2v"))

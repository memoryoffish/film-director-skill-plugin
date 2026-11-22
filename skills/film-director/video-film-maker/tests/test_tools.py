"""Offline tests for the helper tools moved into scripts/ (synthetic video and audio, no network)."""
from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio_probe  # noqa: E402
import camfx  # noqa: E402
import colorfill  # noqa: E402
import env10  # noqa: E402
import glowlen  # noqa: E402
import optical_edit  # noqa: E402
import peaks  # noqa: E402
import track_toss  # noqa: E402
from test_occut import FPS, H, W, panning, write_video  # noqa: E402

SR = 44100


def write_wav(path: Path, x: np.ndarray) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    return path


def silence_then_tone(path: Path) -> Path:
    t = np.arange(SR) / SR
    return write_wav(path, np.concatenate([np.zeros(SR), 0.5 * np.sin(2 * np.pi * 1000 * t)]))


def test_env10_finds_where_a_sound_starts(tmp_path):
    env = dict(env10.envelope(silence_then_tone(tmp_path / "a.wav"), 0.9, 1.1))
    assert env[0.94] < -80 and abs(env[1.04] - (-9.0)) < 0.5  # 0.5 * sine = -9 dBFS RMS


def test_audio_probe_tells_a_tone_from_noise(tmp_path):
    t = np.arange(SR) / SR
    noise = np.random.default_rng(0).standard_normal(SR) * 0.1
    rep = audio_probe.probe(write_wav(tmp_path / "b.wav", np.concatenate([noise, 0.3 * np.sin(2 * np.pi * 1500 * t)])),
                            step=0.5)
    rows = {r["t"]: r for r in rep["rows"]}
    assert rows[0.0]["tonal_db"] < 25 and rows[1.0]["tonal_db"] > 40 and abs(rows[1.0]["peak_hz"] - 1500) < 20


def test_peaks_lists_the_note(tmp_path):
    t = np.arange(SR) / SR
    rows = peaks.peaks(write_wav(tmp_path / "c.wav", 0.3 * np.sin(2 * np.pi * 440 * t)), step=0.5, n=2)
    top = max(rows[0]["peaks"], key=lambda p: p[1])
    assert abs(top[0] - 440) < 10


def solid(rgb: tuple[int, int, int], n: int) -> list[np.ndarray]:
    return [np.full((H, W, 3), rgb, np.uint8) for _ in range(n)]


def test_optical_edit_bloom_lands_where_the_plan_says_and_glowlen_sees_it(tmp_path):
    a = write_video(tmp_path / "a.mp4", solid((60, 60, 70), 30))
    b = write_video(tmp_path / "b.mp4", solid((80, 70, 60), 30))
    seg = [{"clip": str(a), "start": 0, "end": 29}, {"clip": str(b), "start": 0, "end": 29}]
    bloom = {"type": "bloom", "rise": 6, "overlap": 4, "fall": 9, "level": 0.5, "sfx": False}
    for name, tr in (("glow", bloom), ("ref", {"type": "dissolve", "frames": 4})):
        (tmp_path / f"{name}.json").write_text(json.dumps({"segments": seg, "transitions": [tr]}))
        optical_edit.main(str(tmp_path / f"{name}.json"), str(tmp_path / f"{name}.mp4"))
    rep = json.loads((tmp_path / "glow.json").read_text())
    assert rep["frames"] == 56  # 30 + 30 - overlap 4
    mark = rep["transitions"][0]
    assert mark["peak_overlap"] == [26, 29] and mark["glow"] == [20, 38]
    cap = cv2.VideoCapture(str(tmp_path / "glow.mp4"))
    assert (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) == (W, H)
    g = glowlen.glow_length(tmp_path / "glow.mp4", tmp_path / "ref.mp4", 10, 50)
    assert g["frames"] > 6 and 20 <= g["first"] and g["last"] <= 38 and g["peak_lift"] > 0.1


def test_camfx_center_box_skips_a_brighter_ceiling_lamp():
    f = np.full((270, 480, 3), 20, np.uint8)
    cv2.circle(f, (240, 30), 30, (255, 255, 255), -1)   # lamp on the ceiling, the brightest thing
    cv2.circle(f, (240, 160), 25, (170, 170, 170), -1)  # the tunnel exit
    free = camfx.bright_center(f)
    boxed = camfx.bright_center(f, (0.25, 0.3, 0.75, 0.9))
    assert free["y"] < 0.2
    assert abs(boxed["x"] - 0.5) < 0.02 and abs(boxed["y"] - 160 / 270) < 0.03


def test_colorfill_counts_fill_and_flags_a_leaking_edge():
    orange = np.zeros((H, W, 3), np.uint8)
    orange[:] = (20, 140, 240)  # BGR
    full = colorfill.fill_stats(orange)
    assert full["share"] > 0.99 and full["worst_cell_dE"] < 1
    leak = orange.copy()
    leak[: H // 4, W // 2 - 12: W // 2 + 12] = (235, 235, 240)  # white pith at the top edge
    assert colorfill.fill_stats(leak)["worst_cell_dE"] > 12
    red = np.zeros((H, W, 3), np.uint8)
    red[:] = (30, 20, 200)
    assert colorfill.fill_stats(red, hue=(340, 20))["share"] > 0.99 and colorfill.fill_stats(red)["share"] < 0.01
    assert colorfill.runs([3, 4, 5, 9]) == [[3, 5], [9, 9]]


def test_track_toss_ignores_a_still_lookalike_and_finds_the_top(tmp_path):
    frames = []
    for k in range(20):
        f = np.full((H, W, 3), 90, np.uint8)
        cv2.rectangle(f, (5, 5), (25, 25), (240, 160, 40), -1)  # RGB: a still copper-orange pot
        y = 80 - int(60 * np.sin(np.pi * k / 19))              # up and down, top at frame 9-10
        if k:
            cv2.circle(f, (120, y), 8, (240, 170, 50), -1)
        frames.append(f)
    clip = write_video(tmp_path / "toss.mp4", frames, audio=False)
    res = track_toss.track(str(clip), 0, 1, 19)
    top = track_toss.highest(res)
    assert top["i"] in (9, 10) and abs(top["cx"] - 120) < 3
    assert all(d.get("cx", 120) > 60 for d in res)  # never the pot


def test_moved_tools_have_no_hardcoded_home_paths():
    root = Path(__file__).resolve().parents[1] / "scripts"
    moved = ("audio_probe", "env10", "peaks", "refcrop", "optical_edit", "glowlen", "camfx", "colorfill", "track_toss")
    for p in (root / f"{m}.py" for m in moved):
        assert "/mnt/data" not in p.read_text(), p.name

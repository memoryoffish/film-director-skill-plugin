"""Offline tests for the movie runner (no network)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import movie  # noqa: E402
from test_occut import H, W, panning, write_video  # noqa: E402

RED = np.zeros((H, W, 3), np.uint8)
RED[..., 0] = 200
RED[..., 1:] = 20


def test_red_fraction_counts_saturated_red_only():
    assert movie.red_fraction(RED) > 0.99
    assert movie.red_fraction(np.full((H, W, 3), 120, np.uint8)) == 0.0


def plan(**over):
    p = {"identity_refs": ["a.png"], "calls": [
        {"name": "c1", "mode": "refs", "duration": 6, "prompt": "p", "seam_out": {"method": "extension"}},
        {"name": "c2", "mode": "extension", "of": "c1", "duration": 9, "prompt": "p", "seam_in": {"method": "extension"}}]}
    p.update(over)
    return p


def test_validate_rejects_bad_plans():
    movie.validate(plan())
    with pytest.raises(ValueError):
        movie.validate(plan(identity_refs=[]))
    bad = plan()
    bad["calls"][1]["of"] = "c9"
    with pytest.raises(ValueError):
        movie.validate(bad)
    bad = plan()
    bad["calls"][0]["seam_out"] = {"method": "occlusion"}
    with pytest.raises(ValueError, match="disagree"):
        movie.validate(bad)


def test_check_finds_colour_cut_and_extension_start(tmp_path, monkeypatch):
    monkeypatch.setattr(movie.occut, "own_cuts", lambda *a, **k: {"range": [0, 0], "fps": 30.0, "candidates": []})
    a = write_video(tmp_path / "a.mp4", panning(40, 60, 2) + [RED] * 15)          # red fills from frame 60
    b = write_video(tmp_path / "b.mp4", [RED] * 10 + panning(41, 50, 2))          # red until frame 9
    ca = {"name": "a", "mode": "refs", "duration": 2, "seam_out": {"method": "color", "window_s": [1.5, 2.5]}}
    cb = {"name": "b", "mode": "refs", "duration": 2, "seam_in": {"method": "color"}}
    ra, rb = movie.check(ca, a, {}, tmp_path), movie.check(cb, b, {}, tmp_path)
    assert (ra["end"], ra["problems"]) == (60, []) and (rb["start"], rb["problems"]) == (9, [])
    src = write_video(tmp_path / "src.mp4", panning(42, 40, 2))
    ext = write_video(tmp_path / "ext.mp4", panning(42, 70, 2)[10:])               # repeats src frames 10..39
    ce = {"name": "e", "mode": "extension", "of": "s", "duration": 3, "input_s": 1, "seam_in": {"method": "extension"}}
    re_ = movie.check(ce, ext, {"s": {"clip": str(src)}}, tmp_path)
    assert re_["start"] == 30 and re_["problems"] == [] and re_["src_end"] == 39


def test_check_cuts_the_source_where_a_slow_copy_stops_matching(tmp_path, monkeypatch):
    monkeypatch.setattr(movie.occut, "own_cuts", lambda *a, **k: {"range": [0, 0], "fps": 30.0, "candidates": []})
    src = write_video(tmp_path / "src.mp4", panning(42, 40, 2))
    ext = write_video(tmp_path / "ext.mp4", panning(42, 40, 2)[10:30] + panning(43, 40, 2))  # copies src 10..29 only
    ce = {"name": "e", "mode": "extension", "of": "s", "duration": 3, "input_s": 1, "seam_in": {"method": "extension"}}
    re_ = movie.check(ce, ext, {"s": {"clip": str(src)}}, tmp_path)
    assert (re_["src_end"], re_["start"], re_["problems"]) == (29, 20, [])


def test_check_flags_an_extension_that_does_not_repeat_its_input(tmp_path, monkeypatch):
    monkeypatch.setattr(movie.occut, "own_cuts", lambda *a, **k: {"range": [0, 0], "fps": 30.0, "candidates": []})
    src = write_video(tmp_path / "src.mp4", panning(42, 40, 2))
    ext = write_video(tmp_path / "ext.mp4", panning(43, 70, 2))                   # redrawn: never shows src's end
    ce = {"name": "e", "mode": "extension", "of": "s", "duration": 3, "input_s": 1, "seam_in": {"method": "extension"}}
    re_ = movie.check(ce, ext, {"s": {"clip": str(src)}}, tmp_path)
    assert len(re_["problems"]) == 1 and "does not repeat its input" in re_["problems"][0]

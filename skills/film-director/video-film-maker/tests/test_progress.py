"""Offline tests for scripts/progress.py (local job folders, no ssh)."""
import json
import sys
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import progress  # noqa: E402


def job(d: Path, name: str, status: str = "DOWNLOADED", video: bool = True, dur: int = 10) -> None:
    (d / f"{name}.json").write_text(json.dumps({
        "name": name, "status": status, "task_id": "x", "submitted_utc": 1.0,
        "timing": {"submit_time": "2026-11-16 15:00:00.0", "end_time": "2026-11-16 15:03:00.0"},
        "usage": {"duration": dur} if status == "DOWNLOADED" else {},
        "payload": {"parameters": {"resolution": "720P"}}}))
    if video:
        (d / f"{name}.mp4").write_bytes(b"")


def args(tmp: Path, **kw) -> Namespace:
    base = dict(out=str(tmp / "page"), jobs=[str(tmp / "clips")], remote=None, cuts=None, local_cuts=None,
                events=None, story=None, units=None, order=None, title="测试片", estimate_cny=100.0, price="list", every=None)
    base.update(kw)
    return Namespace(**base)


def test_page_has_a_player_per_downloaded_take_and_states(tmp_path):
    clips = tmp_path / "clips"; clips.mkdir(); (tmp_path / "page").mkdir()
    job(clips, "U1_t1"); job(clips, "U1_t2"); job(clips, "U2_t1", status="RUNNING", video=False)
    ev = tmp_path / "ev.jsonl"
    ev.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in [
        {"t": "15:04", "unit": "U1", "take": "U1_t1", "state": "retake", "what": "多了人声"},
        {"t": "15:08", "unit": "U1", "state": "pass", "what": "U1 第 2 次合格"}]))
    html = progress.build(args(tmp_path, events=str(ev))).read_text()
    assert html.count("<video") == 2                      # two downloaded takes, the running one has a placeholder
    assert "生成中" in html and "多了人声" in html
    assert "<span class='ok'>U1</span>" in html           # unit verdict lands on its newest take
    assert "¥12" in html                                  # 20 billed seconds x 0.6


def test_take_state_order_of_precedence():
    j = {"name": "A_t1", "unit": "A", "status": "FAILED"}
    assert progress.take_state(j, []) == "fail"
    j["status"] = "PENDING"
    assert progress.take_state(j, []) == "gen"
    j["status"] = "DOWNLOADED"
    assert progress.take_state(j, []) == "todo"
    assert progress.take_state(j, [{"take": "A_t1", "state": "pass"}]) == "pass"
    assert progress.take_state(j, [{"unit": "A", "state": "pass"}]) == "todo"   # unit verdicts only for the newest take
    j["latest"] = True
    assert progress.take_state(j, [{"unit": "A", "state": "pass"}]) == "pass"


def test_order_and_cuts(tmp_path):
    clips = tmp_path / "clips"; clips.mkdir(); (tmp_path / "page").mkdir()
    job(clips, "B_t1"); job(clips, "A_t1")
    (tmp_path / "cut").mkdir(); (tmp_path / "cut" / "film.mp4").write_bytes(b"")
    html = progress.build(args(tmp_path, order="A,B", local_cuts=[str(tmp_path / "cut" / "*.mp4")])).read_text()
    assert html.index(">A<") < html.index(">B<")
    assert "cut/film.mp4" in html


def test_story_and_unit_descriptions(tmp_path):
    clips = tmp_path / "clips"; clips.mkdir(); (tmp_path / "page").mkdir()
    job(clips, "U1_t1")
    (tmp_path / "story.md").write_text("末班车上，老人把蛋糕给了司机。", encoding="utf-8")
    (tmp_path / "units.json").write_text(json.dumps({"U1": "司机从后视镜看老人"}, ensure_ascii=False), encoding="utf-8")
    html = progress.build(args(tmp_path, story=str(tmp_path / "story.md"), units=str(tmp_path / "units.json"))).read_text()
    assert "老人把蛋糕给了司机" in html and "司机从后视镜看老人" in html

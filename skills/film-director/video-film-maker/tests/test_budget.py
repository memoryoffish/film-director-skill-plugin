"""Offline tests for scripts/budget.py (no network)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import budget  # noqa: E402

DATA = {
    "wan_calls": {"720P/t2v": {"wall_per_output_s": {"p50": 20.0, "p90": 30.0}},
                  "720P/extension": {"wall_per_output_s": {"p50": 30.0, "p90": 40.0}}},
    "wan_price_cny_per_s": {"wan3.0-video": {"list": {"720P": 0.6, "1080P": 1.2}, "discount": {"720P": 0.42, "1080P": 0.84}}},
    "retake_gens_per_call": {"p50": 2.0, "range": [1.0, 5.0]},
    "agent_per_film": {"minutes": {"min": 60, "max": 140}, "usd": {"min": 10, "max": 31}},
    "network": {"dashscope_api_total_s": {"mac": 0.13, "server": 0.08}, "oss_MBps": {"mac_down": 2.0, "server_down": 1.3}},
}


def plan():
    return {"resolution": "720P", "concurrency": 2, "calls": [
        {"name": "a", "duration": 10, "mode": "t2v"},
        {"name": "b", "duration": 10, "mode": "extension", "input_s": 3}]}


def test_estimate_bills_extension_input_and_scales_by_retake():
    e = budget.estimate(plan(), DATA)
    assert e["billed_s_once"] == 23                       # 10 + (10 + 3 input)
    assert e["money_cny"]["typical"] == round(23 * 2.0 * 0.6)
    assert e["money_cny"]["high"] == round(23 * 5.0 * 0.6)
    assert e["wan_minutes"]["typical"] == round((20 * 10 + 30 * 10) * 2.0 / 2 / 60)
    assert budget.estimate(plan(), DATA, "discount")["money_cny"]["unit"] == 0.42


def test_estimate_rejects_unknown_modes_and_asks_the_user():
    bad = plan(); bad["calls"][0]["mode"] = "magic"
    try:
        budget.estimate(bad, DATA)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    text = budget.ask_text(budget.estimate(plan(), DATA), plan())
    assert "可以开始吗" in text and "¥" in text


def test_verdict_thresholds():
    assert budget.verdict(0.1, 0.1) == "正常"
    assert budget.verdict(0.25, 0.1) == "偏慢"
    assert budget.verdict(0.5, 0.1) == "很慢"


def test_actual_sums_billed_seconds_of_downloaded_jobs(tmp_path):
    def state(name, status, billed):
        (tmp_path / f"{name}.json").write_text(json.dumps({"name": name, "task_id": "t-" + name, "status": status,
            "payload": {"parameters": {"resolution": "720P", "duration": 10}}, "usage": {"duration": billed}}))
    state("a", "DOWNLOADED", 10); state("b", "DOWNLOADED", 13); state("c", "FAILED", 10)
    (tmp_path / "notes.json").write_text("{}")
    r = budget.actual([tmp_path], DATA)
    assert (r["jobs"], r["downloaded"], r["billed_s"], r["money_cny"]) == (3, 2, 23, round(23 * 0.6, 1))


def test_actual_uses_each_jobs_model(tmp_path):
    data = dict(DATA); data["wan_price_cny_per_s"] = dict(DATA["wan_price_cny_per_s"], **{"happyhorse-1.1-r2v": {"list": {"720P": 0.9}}})
    for name, model in (("a", "wan3.0-video"), ("b", "happyhorse-1.1-r2v")):
        (tmp_path / f"{name}.json").write_text(json.dumps({"name": name, "task_id": "x", "status": "DOWNLOADED", "usage": {"duration": 10},
                                                          "payload": {"model": model, "parameters": {"resolution": "720P"}}}))
    got = budget.actual([tmp_path], data)
    assert got["billed_s"] == 20 and got["money_cny"] == 15.0      # 10 s x 0.6 + 10 s x 0.9

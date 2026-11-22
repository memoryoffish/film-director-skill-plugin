#!/usr/bin/env python3
"""Time and money budget for a film: estimate before generating, check the network, compare the actual run.

    python3 budget.py estimate PLAN.json [--price list|discount]
    python3 budget.py netcheck [--oss-url URL]
    python3 budget.py actual CLIPS_DIR [CLIPS_DIR ...] [--price list|discount]

PLAN.json: {"resolution": "720P", "model": "wan3.0-video", "concurrency": 3,
            "calls": [{"name": "c1", "duration": 10, "mode": "t2v|first_frame|first_last|refs|extension",
                       "input_s": 3}]}   # input_s only for extension (billed too)
"retake" (generations per call) is optional and normally left out: the default is the measured median in
budget-data.json (about 1.2), and the "high" figure uses the top of the measured range.
Typical values (call times, prices, retake factor, agent time and cost, network) come from
../refs/practical/budget-data.json; see ../refs/practical/budget-data.md. The numbers are for asking the user, not for deciding alone.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "refs" / "practical" / "budget-data.json"
MODES = {"t2v", "first_frame", "first_last", "refs", "extension"}
SLOW, VERY_SLOW = 2.0, 4.0  # network: this many times the typical value


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def unit_price(data: dict, model: str, res: str, price: str) -> float:
    table = data["wan_price_cny_per_s"][model]
    prices = table.get(price, table["list"])
    return prices.get(res, prices.get(res.upper()))


def call_time(data: dict, res: str, mode: str, duration: int) -> tuple[float, float]:
    """Typical and slow wall time of one call: the measured per-call median / p90, scaled by length."""
    res = res.upper()  # only Wan call times are measured; other models use them as a rough guess
    c = data["wan_calls"].get(f"{res}/{mode}") or data["wan_calls"][f"{res}/t2v"]
    per = c["wall_per_output_s"]
    return per["p50"] * duration, per["p90"] * duration


def estimate(plan: dict, data: dict, price: str = "list") -> dict:
    res, model = plan.get("resolution", "720P"), plan.get("model", "wan3.0-video")
    conc = max(1, int(plan.get("concurrency", 3)))
    retake = float(plan.get("retake", data["retake_gens_per_call"]["p50"]))
    retake_max = float(data["retake_gens_per_call"]["range"][1])
    up = unit_price(data, model, res, price)
    billed = t50 = t90 = 0.0
    for c in plan["calls"]:
        if c.get("mode", "t2v") not in MODES:
            raise ValueError(f"{c.get('name')}: mode must be one of {sorted(MODES)}")
        sec = float(c["duration"]) + (float(c.get("input_s", 0)) if c.get("mode") == "extension" else 0.0)
        billed += sec
        a, b = call_time(data, res, c.get("mode", "t2v"), int(c["duration"]))
        t50, t90 = t50 + a, t90 + b
    ag = data["agent_per_film"]
    return {
        "calls": len(plan["calls"]), "billed_s_once": round(billed), "retake": retake,
        "money_cny": {"typical": round(billed * retake * up), "high": round(billed * retake_max * up), "unit": up, "price": price},
        "wan_minutes": {"typical": round(t50 * retake / conc / 60), "slow": round(t90 * retake_max / conc / 60)},
        "agent": {"minutes": [ag["minutes"]["min"], ag["minutes"]["max"]], "usd": [ag["usd"]["min"], ag["usd"]["max"]]},
    }


def ask_text(e: dict, plan: dict) -> str:
    m, w, a = e["money_cny"], e["wan_minutes"], e["agent"]
    return (f"这部片计划 {e['calls']} 次生成调用（{plan.get('resolution', '720P')}），每次都过一遍要生成约 {e['billed_s_once']} 秒。\n"
            f"- 视频花费：按每次调用平均抽 {e['retake']:g} 次，约 ¥{m['typical']}；抽得多时最多约 ¥{m['high']}（单价 ¥{m['unit']}/秒，{'原价' if m['price'] == 'list' else '折扣价'}）。\n"
            f"- 生成时间：约 {w['typical']} 分钟，慢的时候 {w['slow']} 分钟（同时跑 {plan.get('concurrency', 3)} 个）。\n"
            f"- agent 自己：以往一部片 {a['minutes'][0]}–{a['minutes'][1]} 分钟、${a['usd'][0]}–{a['usd'][1]}。\n"
            "可以开始吗？或者给一个时间、花费的上限。")


def verdict(measured: float, typical: float) -> str:
    r = measured / typical if typical else 1.0
    return "很慢" if r >= VERY_SLOW else "偏慢" if r >= SLOW else "正常"


def netcheck(data: dict, oss_url: str | None = None, tries: int = 3) -> dict:
    out = {}
    ts = []
    for _ in range(tries):
        t = time.time()
        try:
            urllib.request.urlopen("https://dashscope.aliyuncs.com/api/v1/tasks/x", timeout=20)
        except urllib.error.HTTPError:
            pass  # 401 is the expected answer; we only time the round trip
        except Exception as e:  # unreachable
            out["api"] = {"error": str(e)}
            break
        ts.append(time.time() - t)
    if ts:
        typ = min(data["network"]["dashscope_api_total_s"].values())
        out["api"] = {"seconds": round(statistics.median(ts), 3), "typical": typ, "verdict": verdict(statistics.median(ts), typ)}
    if oss_url:
        t = time.time()
        n = len(urllib.request.urlopen(oss_url, timeout=120).read())
        mbps = n / 1e6 / max(1e-6, time.time() - t)
        typ = min(v for k, v in data["network"]["oss_MBps"].items() if "down" in k)
        out["oss_download"] = {"MBps": round(mbps, 2), "typical": typ, "verdict": verdict(typ, mbps)}  # speed: slower = bigger ratio
    return out


def actual(dirs: list[Path], data: dict, price: str = "list") -> dict:
    jobs = []
    for d in dirs:
        for f in sorted(Path(d).glob("*.json")):
            try:
                s = json.loads(f.read_text())
            except Exception:
                continue
            if not isinstance(s, dict) or "payload" not in s or not s.get("task_id"):
                continue
            par = s["payload"].get("parameters", {})
            jobs.append({"name": s.get("name", f.stem), "res": par.get("resolution", "720P"), "dur": par.get("duration"),
                         "model": s["payload"].get("model") or "wan3.0-video",
                         "billed": (s.get("usage") or {}).get("duration") if s.get("status") == "DOWNLOADED" else 0,
                         "status": s.get("status")})
    money = sum((j["billed"] or 0) * unit_price(data, j["model"], j["res"], price) for j in jobs)  # each job's own model
    return {"jobs": len(jobs), "downloaded": sum(1 for j in jobs if j["status"] == "DOWNLOADED"),
            "billed_s": sum(j["billed"] or 0 for j in jobs), "money_cny": round(money, 1)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("estimate"); e.add_argument("plan"); e.add_argument("--price", default="list", choices=["list", "discount"])
    n = sub.add_parser("netcheck"); n.add_argument("--oss-url", default=None)
    a = sub.add_parser("actual"); a.add_argument("dirs", nargs="+"); a.add_argument("--price", default="list", choices=["list", "discount"])
    args = ap.parse_args()
    data = load()
    if args.cmd == "estimate":
        plan = json.loads(Path(args.plan).read_text())
        est = estimate(plan, data, args.price)
        print(json.dumps(est, ensure_ascii=False, indent=1))
        print(ask_text(est, plan))
    elif args.cmd == "netcheck":
        print(json.dumps(netcheck(data, args.oss_url), ensure_ascii=False, indent=1))
    else:
        print(json.dumps(actual([Path(d) for d in args.dirs], data, args.price), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

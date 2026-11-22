#!/usr/bin/env python3
"""Job sheets in, videos and images out. The sheet format is formats/job-sheet.md, beside this backends folder.

    filmgen.py run SHEET.json [...] [--out DIR]   generate on this machine; run it in the project folder
    filmgen.py send PROJECT_DIR [--wait 540]       run PROJECT_DIR/jobs/*.json on the machine that has the video keys
    filmgen.py request SHEET.json [...]            print what would be sent; sends nothing, uploads nothing, reads no key

The backend comes from the sheet's "model" (sheets.py). run: videos go to clips/, images to out/ unless --out says
otherwise; a sheet the backend cannot take is refused before anything runs; exit 1 when a sheet was refused or a job
failed. send: see send.py; exit 3 when the wait ran out (call it again to keep waiting).
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True  # leave no __pycache__ in the plugin folder
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "local")]

import sheets  # noqa: E402


def load(paths: list[str]) -> tuple[list[dict], list[str]]:
    """The sheets a backend can take, and why the others cannot go."""
    good, bad = [], []
    for p in paths:
        try:
            s = json.loads(Path(p).read_text(encoding="utf-8"))
            sheets.feed(s)
            why = sheets.backend(s).problem(s)
        except (OSError, ValueError, KeyError) as e:
            why = str(e)
        if why:
            bad.append(f"{p}: {why}")
        else:
            good.append(s)
    return good, bad


def run(paths: list[str], out: str | None) -> int:
    good, bad = load(paths)
    for b in bad:
        print("refused", b, flush=True)
    groups: dict = {}
    for s in good:
        groups.setdefault(sheets.backend(s), []).append(s)

    def go(item) -> list[bool]:
        mod, jobs = item
        return mod.run(jobs, Path(out or ("out" if mod is sheets.openai_image else "clips")))

    with ThreadPoolExecutor(max(1, len(groups))) as pool:  # each backend runs its own few at once
        done = [ok for oks in pool.map(go, groups.items()) for ok in oks]
    return 1 if bad or not all(done) else 0


def request(paths: list[str]) -> int:
    bad = 0
    for p in paths:
        try:
            s = json.loads(Path(p).read_text(encoding="utf-8"))
            mod = sheets.backend(s)
            if why := mod.problem(s):
                raise ValueError(why)
            shown = {"sheet": p, "name": s.get("name"), "kind": sheets.kind(s), "feed": sheets.feed(s),
                     "backend": mod.__name__, **mod.request(s)}
        except Exception as e:  # noqa: BLE001 - show why this sheet cannot go and go on with the others
            shown, bad = {"sheet": p, "problem": f"{type(e).__name__}: {e}"}, bad + 1
        print(json.dumps(shown, ensure_ascii=False, indent=1), flush=True)
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("sheets", nargs="+")
    r.add_argument("--out")
    s = sub.add_parser("send")
    s.add_argument("project")
    s.add_argument("--wait", type=int, default=540)
    q = sub.add_parser("request")
    q.add_argument("sheets", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run(a.sheets, a.out)
    if a.cmd == "request":
        return request(a.sheets)
    import send
    return send.main(Path(a.project), a.wait)


if __name__ == "__main__":
    sys.exit(main())

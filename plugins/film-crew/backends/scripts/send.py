"""filmgen.py send PROJECT_DIR [--wait 540]: run a project's video jobs on the machine that has the video keys.

PROJECT_DIR/jobs/*.json are the sheets; media paths inside them are relative to PROJECT_DIR. Copies the sheets, the media
they name and this plugin's code (into .film-crew/) to REMOTE/<project>/ on HOST, starts `filmgen.py run` there in a
tmux session (SESSION), waits, and copies clips/<name>.mp4 back into PROJECT_DIR/clips/ one by one as they finish, with
the state files and clips/results.jsonl. HOST, REMOTE and SESSION come from FILM_SEND_HOST, FILM_SEND_REMOTE and
FILM_SEND_SESSION (see local/machine.py). A job that already has a clip, or that failed, is skipped: adding jobs and
calling it again only runs the new ones. A job whose files are not there yet (a previz still rendering) or that its
backend cannot take is left out with a note and the others go. To try a job again or with other parameters, save it
under a new name. If the wait runs out it exits with code 3: call it again to keep waiting.
This side does not read the keys: the tmux session on HOST needs them in its environment.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import tarfile
import time
from pathlib import Path

import machine
import sheets

PLUGIN = Path(__file__).resolve().parents[1]
CODE = [*sorted((PLUGIN / "scripts").glob("*.py")), PLUGIN / "local" / "machine.py"]


def ssh(cmd: str, stdin=None, timeout=900) -> bytes:
    return subprocess.run(["ssh", "-o", "ConnectTimeout=20", machine.HOST, cmd], input=stdin, capture_output=True,
                          timeout=timeout).stdout


def sessions() -> list[str]:
    return [line.split(":")[0] for line in ssh("tmux ls 2>/dev/null").decode().splitlines()]


def media(job: dict) -> list[str]:
    files = []
    for k in sheets.MEDIA:
        v = job.get(k)
        files += [p for p in ([v] if isinstance(v, str) else v or []) if not p.startswith("@")]  # @NAME: an earlier job's last frame
    return files


def failures(proj: Path) -> dict:
    failed = {}
    res = proj / "clips" / "results.jsonl"
    if res.exists():
        for line in res.read_text().splitlines():
            r = json.loads(line)
            if not r.get("ok"):
                failed[r["name"]] = (r.get("error") or "")[:300]
    return failed


def not_ready(proj: Path, job: dict) -> str:
    """Why this job cannot be sent yet ("" when it can): a file it names is not there yet, or its backend cannot take it."""
    for p in media(job):
        if not (proj / p).exists():
            return f"file is not there yet: {p}"
    try:
        sheets.feed(job)
        return sheets.backend(job).problem(job)
    except ValueError as e:
        return str(e)


def start(proj: Path, todo: list, sess: str, rdir: str) -> None:
    files = set()
    for path, job in todo:
        files.add(str(path.relative_to(proj)))
        files.update(media(job))
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for f in sorted(files):
            tar.add(proj / f, arcname=f)
        for f in CODE:
            tar.add(f, arcname=f".film-crew/{f.relative_to(PLUGIN)}")
    log = f"logs/run_{time.strftime('%m%d_%H%M%S')}.log"
    ssh(f"mkdir -p ~/{rdir}/logs ~/{rdir}/clips && cd ~/{rdir} && tar xzf -", stdin=buf.getvalue())
    names = " ".join(str(p.relative_to(proj)) for p, _j in todo)
    ssh(f"tmux new-session -d -s {sess} 'cd ~/{rdir} || exit; "
        f"{machine.REMOTE_PYTHON} .film-crew/scripts/filmgen.py run {names} --out clips > {log} 2>&1'")
    print(f"started {len(todo)} jobs in tmux session {sess} on {machine.HOST} (log ~/{rdir}/{log})", flush=True)


def pull(proj: Path, rdir: str) -> list:
    """Bring back the clips that are done and not here yet. Returns their names."""
    have = {p.name for p in (proj / "clips").iterdir()}
    listing = ssh(f"cd ~/{rdir} 2>/dev/null && ls clips 2>/dev/null").decode("utf-8", "replace").split()
    new = [f for f in listing if f.endswith((".mp4", ".json")) and (f not in have or f.endswith(".json"))]
    if listing:
        data = ssh(f"cd ~/{rdir} && tar czf - logs/results.jsonl " + " ".join(f"clips/{f}" for f in new) + " 2>/dev/null")
        if data:
            subprocess.run(["tar", "xzf", "-", "-C", str(proj)], input=data)
            res = proj / "logs" / "results.jsonl"
            if res.exists():
                res.replace(proj / "clips" / "results.jsonl")
    return [f[:-4] for f in new if f.endswith(".mp4")]


def main(proj: Path, wait: int) -> int:
    if not machine.HOST or not machine.REMOTE:
        raise SystemExit("send needs FILM_SEND_HOST (the ssh host that runs the jobs) and FILM_SEND_REMOTE (the folder "
                         "there that holds the projects, relative to its home); set both and call it again")
    proj = proj.resolve()
    os.chdir(proj)  # media paths in the sheets are relative to the project folder
    sess, rdir = machine.SESSION.format(project=proj.name), f"{machine.REMOTE}/{proj.name}"
    jobs = [(p, json.loads(p.read_text())) for p in sorted((proj / "jobs").glob("*.json"))]
    if not jobs:
        print("no jobs in", proj / "jobs")
        return 2
    (proj / "clips").mkdir(exist_ok=True)
    clip = lambda job: proj / "clips" / f"{job['name']}.mp4"  # noqa: E731
    t0, tried = time.time(), set()
    held = {j["name"]: why for _p, j in jobs if not clip(j).exists() and (why := not_ready(proj, j))}
    for n, why in held.items():
        print(f"skip  {n}: {why}")
    running = sess in sessions()
    while True:
        while running and time.time() - t0 < wait:
            time.sleep(30)
            for n in pull(proj, rdir):                      # each clip comes back as soon as it is done
                print("got  ", n, flush=True)
            running = sess in sessions()
        pull(proj, rdir)
        failed = failures(proj)
        todo = [(p, j) for p, j in jobs if not clip(j).exists() and j["name"] not in failed and j["name"] not in held]
        if running or not todo or time.time() - t0 >= wait:
            break
        if tried & {j["name"] for _p, j in todo}:           # ran and left neither a clip nor a failure record
            print("some jobs ended without a result: look at the newest log in the server folder", f"~/{rdir}/logs")
            break
        start(proj, todo, sess, rdir)
        tried |= {j["name"] for _p, j in todo}
        running = True
    for _p, j in jobs:
        n = j["name"]
        state = "ok    " if clip(j).exists() else "FAILED" if n in failed else "skip  " if n in held else "wait  "
        print(f"{state} {n}" + (f"  {failed[n]}" if n in failed and not clip(j).exists() else f"  {held[n]}" if n in held else ""))
    if running or todo or held:
        print("not finished: call filmgen.py send again to keep waiting" + (" (skipped jobs go once their files are there)" if held else ""))
        return 3
    return 0

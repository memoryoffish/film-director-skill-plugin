#!/usr/bin/env python3
"""Check job sheets against the format in job-sheet.md (stdlib only).

    python3 check_job.py SHEET.json [...] [--root PROJECT_DIR]

Checks the format only: required fields, types, one feed per sheet, no unknown fields, and with --root that the media
files exist (relative paths are relative to PROJECT_DIR). It does not check what a particular model accepts; that is the
backend's business. Prints the problems and exits 1 if there are any. In code: check(sheet, root) -> list of problems.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

COMMON = {"name": str, "prompt": str, "model": str, "kind": str}
VIDEO = {"duration": int, "resolution": str, "ratio": str, "audio": bool, "prompt_extend": bool, "seed": int,
         "first_frame": str, "last_frame": str, "reference_images": list, "reference_video": str,
         "return_last_frame": bool}
IMAGE = {"images": list, "size": str, "n": int, "quality": str}
MEDIA = ("first_frame", "last_frame", "reference_images", "reference_video", "images")


def kind(sheet: dict) -> str:
    """An explicit "kind" wins; else a gpt-image model or any image-only field makes it an image; else a video."""
    if sheet.get("kind"):
        return sheet["kind"]
    if str(sheet.get("model") or "").startswith("gpt-image") or any(k in sheet for k in IMAGE):
        return "image"
    return "video"


def feed(sheet: dict) -> str:
    """t2v, first_frame, first_last, refs, ref_video for a video; t2i, edit for an image."""
    if kind(sheet) == "image":
        return "edit" if sheet.get("images") else "t2i"
    if sheet.get("reference_video"):
        return "ref_video"
    if sheet.get("reference_images"):
        return "refs"
    return "first_last" if sheet.get("last_frame") else "first_frame" if sheet.get("first_frame") else "t2v"


def check(sheet: dict, root: Path | None = None) -> list[str]:
    if not isinstance(sheet, dict):
        return ["a job sheet is a JSON object"]
    out = []
    for k in ("name", "prompt"):
        if not isinstance(sheet.get(k), str) or not sheet[k].strip():
            out.append(f"{k} is required (a non-empty string)")
    if isinstance(sheet.get("name"), str) and re.search(r"[/\\]", sheet["name"]):
        out.append("name must not contain a slash (it names the output files)")
    if sheet.get("kind") not in (None, "video", "image"):
        out.append('kind is "video" or "image"')
    k = kind(sheet)
    fields = {**COMMON, **(IMAGE if k == "image" else VIDEO)}
    for f, v in sheet.items():
        if f not in fields:
            other = f in (VIDEO if k == "image" else IMAGE)
            out.append(f"{f} is a field of {'video' if k == 'image' else 'image'} sheets, this one is {k}" if other
                       else f"unknown field {f}")
        elif not (isinstance(v, fields[f]) and not (fields[f] is int and isinstance(v, bool))):
            out.append(f"{f} must be {fields[f].__name__}")
    for f in ("reference_images", "images"):
        if isinstance(sheet.get(f), list) and not all(isinstance(p, str) and p.strip() for p in sheet[f]):
            out.append(f"{f} must be a list of paths")
    if isinstance(sheet.get("duration"), int) and not isinstance(sheet["duration"], bool) and sheet["duration"] <= 0:
        out.append("duration must be positive")
    if isinstance(sheet.get("n"), int) and not isinstance(sheet["n"], bool) and sheet["n"] < 1:
        out.append("n must be at least 1")
    if isinstance(sheet.get("size"), str) and not re.fullmatch(r"\d+x\d+", sheet["size"]):
        out.append('size is "WIDTHxHEIGHT", e.g. "1536x864"')
    if k == "video":
        if sheet.get("last_frame") and not sheet.get("first_frame"):
            out.append("last_frame needs a first_frame")
        if (sheet.get("first_frame") or sheet.get("last_frame")) and (sheet.get("reference_images") or sheet.get("reference_video")):
            out.append("first/last frame do not go with reference images or a reference video (one feed per sheet)")
    if root is not None:
        for f in MEDIA:
            v = sheet.get(f)
            for p in [v] if isinstance(v, str) else v if isinstance(v, list) else []:
                if isinstance(p, str) and p and not p.startswith("@") and not (Path(root) / p).is_file():
                    out.append(f"{f}: file not found: {p}")
    return out


def main(argv: list[str]) -> int:
    root = None
    if "--root" in argv:
        i = argv.index("--root")
        root = Path(argv[i + 1])
        del argv[i:i + 2]
    if not argv:
        print(__doc__)
        return 2
    bad = 0
    for p in argv:
        try:
            problems = check(json.loads(Path(p).read_text(encoding="utf-8")), root)
        except (OSError, ValueError) as e:
            problems = [f"cannot read: {e}"]
        for msg in problems:
            print(f"{p}: {msg}")
        bad += bool(problems)
    print(f"{len(argv) - bad} of {len(argv)} sheets fine", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

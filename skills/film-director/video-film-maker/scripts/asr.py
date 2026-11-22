#!/usr/bin/env python3
"""Speech recognition, for checking spoken lines word by word and for finding speech that should not be there.

    python3 asr.py FILE [--start S] [--end E] [--lang zh] [--backend auto|mlx|whisper] [--model NAME] [--json]

FILE is a video or an audio file. Prints one line per segment: start and end (seconds in FILE) and the text;
--json prints the same as a JSON list. Runs on the machine where the clips are; nothing is uploaded. Needs ffmpeg.

Backends (--backend auto takes the first one that is installed):
    mlx      mlx-whisper, Apple-silicon Macs           pip install mlx-whisper      model mlx-community/whisper-large-v3-turbo
    whisper  openai-whisper, any machine, CPU or GPU   pip install openai-whisper   model large-v3
If neither is installed it exits with code 3. Then lines cannot be checked word by word: say so in the report
(the spectrogram still shows when someone speaks and how many phrases there are, see ../stages/3-generation/dialogue.md).

Give it the few seconds where a line is spoken, not a whole clip: on long stretches without speech Whisper loops or
invents words, and the invented words differ from run to run. A few words "recognised" in a quiet stretch are usually that.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

MODELS = {"mlx": "mlx-community/whisper-large-v3-turbo", "whisper": "large-v3"}
MODULES = {"mlx": "mlx_whisper", "whisper": "whisper"}


def pick_backend(want: str = "auto") -> str | None:
    """The backend to use, or None when the wanted one (or, with auto, any) is not installed."""
    for name in (MODULES if want == "auto" else [want]):
        if importlib.util.find_spec(MODULES[name]):
            return name
    return None


def cut_audio(src: str, wav: str, start: float, end: float | None) -> bool:
    ffmpeg = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    cut = ["-ss", f"{start:.3f}"] + (["-t", f"{end - start:.3f}"] if end else [])
    r = subprocess.run([ffmpeg, "-v", "error", "-y", *cut, "-i", src, "-vn", "-ac", "1", "-ar", "16000", wav])
    return r.returncode == 0 and os.path.exists(wav) and os.path.getsize(wav) > 44


def transcribe(backend: str, wav: str, lang: str, model: str) -> list[dict]:
    if backend == "mlx":
        import mlx_whisper
        out = mlx_whisper.transcribe(wav, path_or_hf_repo=model, language=lang, condition_on_previous_text=False, verbose=None)
    else:
        import torch
        import whisper
        gpu = torch.cuda.is_available()
        out = whisper.load_model(model, device="cuda" if gpu else "cpu").transcribe(
            wav, language=lang, fp16=gpu, condition_on_previous_text=False, verbose=None)
    return out.get("segments") or []


def lines(segments: list[dict], offset: float) -> list[dict]:
    return [{"start": round(offset + s["start"], 2), "end": round(offset + s["end"], 2), "text": s["text"].strip()} for s in segments]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--lang", default="zh")
    ap.add_argument("--backend", choices=["auto", *MODULES], default="auto")
    ap.add_argument("--model", help="model name for the backend (default: the one listed above)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    backend = pick_backend(a.backend)
    if not backend:
        print("no speech recognition installed (pip install mlx-whisper, or openai-whisper): "
              "lines cannot be checked word by word; say so in the report", file=sys.stderr)
        return 3
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        if not cut_audio(a.file, wav, a.start, a.end):
            print("no audio could be read from", a.file, file=sys.stderr)
            return 2
        found = lines(transcribe(backend, wav, a.lang, a.model or MODELS[backend]), a.start)
    if a.json:
        print(json.dumps(found, ensure_ascii=False))
    elif not found:
        print("(nothing recognised)")
    for s in ([] if a.json else found):
        print(f"{s['start']:7.2f}–{s['end']:7.2f}  {s['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

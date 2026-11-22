"""cut.py: the onset finder needs nothing; piece / join need ffmpeg (skipped without it)."""
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cut

os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")
FFMPEG = shutil.which("ffmpeg") and shutil.which("ffprobe")


def test_onsets_finds_the_bang():
    rate = 16000
    x = [0.01 * math.sin(i * 0.3) for i in range(rate * 2)]
    for i in range(int(1.2 * rate), int(1.25 * rate)):           # a loud 50 ms bang at 1.2 s
        x[i] = 0.8 * math.sin(i * 0.9)
    found = cut._onsets(x, rate)
    assert found and abs(found[0][0] - 1.2) <= 0.02 and found[0][1] > 20


def make_clip(path, fps, seconds, audio=True):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=size=320x180:rate={fps}:duration={seconds}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}", "-c:a", "aac"]
    subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


@pytest.mark.skipif(not FFMPEG, reason="needs ffmpeg")
def test_pieces_keep_the_frame_rate_and_join_without_drift(tmp_path):
    a = make_clip(tmp_path / "a.mp4", 24, 3)
    b = make_clip(tmp_path / "b.mp4", 24, 3, audio=False)
    parts = [cut.piece(a, 0.5, 1.0, tmp_path / "p1.mp4"), cut.piece(b, 0.0, 0.75, tmp_path / "p2.mp4"),
             cut.tail(a, 1.25, tmp_path / "p3.mp4")]
    assert [cut.frames(p) for p in parts] == [24, 18, 30]
    assert all(cut.fps_of(p) == 24 for p in parts)
    film = cut.join(parts, tmp_path / "film.mp4")
    assert cut.frames(film) == 72
    adur = float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "csv=p=0",
                                 str(film)], capture_output=True, text=True).stdout)
    assert abs(adur - 3.0) < 0.03                                    # the sound is as long as the picture


@pytest.mark.skipif(not FFMPEG, reason="needs ffmpeg")
def test_strip_and_trio_draw(tmp_path):
    pytest.importorskip("PIL")
    a = make_clip(tmp_path / "a.mp4", 30, 2)
    cut.strip(tmp_path / "s.jpg", a, 0.25)
    from PIL import Image
    Image.new("RGB", (64, 36)).save(tmp_path / "wm.png")
    cut.trio(tmp_path / "t.jpg", [(tmp_path / "wm.png", "-", a)])
    assert (tmp_path / "s.jpg").stat().st_size > 0 and (tmp_path / "t.jpg").stat().st_size > 0

"""Unit tests, no network: Seedance rewrite idempotence, video/image and feed detection, backend choice and refusals,
the request bodies the official APIs expect, a task submitted once and polled to the end (fake client), and `request`
sends nothing.

    python3 -B -m unittest discover -s tests -v      (in the backends folder)
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import zlib
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
PLUGIN = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PLUGIN / "scripts"), str(PLUGIN / "local")]

import ark_video  # noqa: E402
import bailian  # noqa: E402
import filmgen  # noqa: E402
import minimax_video  # noqa: E402
import openai_image  # noqa: E402
import sheets  # noqa: E402
import tasks  # noqa: E402


def png(path: Path, w: int = 640, h: int = 360) -> None:
    raw = (b"\x00" + bytes([200, 200, 205]) * w) * h
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))  # noqa: E731
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class Rewrite(unittest.TestCase):
    plain = {"name": "u1", "seed": 3, "duration": 5, "resolution": "720P", "ratio": "16:9", "audio": True,
             "prompt": "图1是一只猫，图2是一只狗；图10是一张木桌。", "reference_images": ["a.png", "b.png"], "model": "seedance-2.5"}

    def test_plain_sheet_is_rewritten(self):
        r = ark_video.rewrite(self.plain)
        self.assertNotIn("seed", r)
        self.assertEqual(r["resolution"], "720p")
        self.assertEqual(r["prompt"], "@图片1是一只猫，@图片2是一只狗；@图片10是一张木桌。")
        self.assertEqual(self.plain["resolution"], "720P")  # the sheet itself is not touched

    def test_idempotent(self):
        once = ark_video.rewrite(self.plain)
        twice = ark_video.rewrite(once)
        self.assertEqual(twice, once)
        self.assertEqual(list(twice), list(once))  # same key order, so the state file is the same text
        self.assertEqual(json.dumps(twice, ensure_ascii=False), json.dumps(once, ensure_ascii=False))


class KindAndFeed(unittest.TestCase):
    def test_kind(self):
        self.assertEqual(sheets.kind({"name": "a", "prompt": "p"}), "video")
        self.assertEqual(sheets.kind({"name": "a", "prompt": "p", "size": "1536x864"}), "image")
        self.assertEqual(sheets.kind({"name": "a", "prompt": "p", "images": ["x.png"]}), "image")
        self.assertEqual(sheets.kind({"name": "a", "prompt": "p", "model": "gpt-image-2.6-flare"}), "image")
        self.assertEqual(sheets.kind({"name": "a", "prompt": "p", "kind": "image"}), "image")
        self.assertEqual(sheets.kind({"name": "a", "prompt": "p", "kind": "video", "n": 1}), "video")

    def test_feed(self):
        f = lambda **kw: sheets.feed({"name": "a", "prompt": "p", **kw})  # noqa: E731
        self.assertEqual(f(), "t2v")
        self.assertEqual(f(first_frame="a.png"), "first_frame")
        self.assertEqual(f(first_frame="a.png", last_frame="b.png"), "first_last")
        self.assertEqual(f(reference_images=["a.png"]), "refs")
        self.assertEqual(f(reference_video="v.mp4"), "ref_video")
        self.assertEqual(f(reference_video="v.mp4", reference_images=["a.png"]), "ref_video")
        self.assertEqual(f(size="1536x864"), "t2i")
        self.assertEqual(f(images=["a.png"]), "edit")
        for bad in ({"last_frame": "b.png"}, {"first_frame": "a.png", "reference_images": ["c.png"]},
                    {"first_frame": "a.png", "reference_video": "v.mp4"}):
            with self.assertRaises(ValueError):
                f(**bad)


class BackendChoice(unittest.TestCase):
    def test_by_model(self):
        b = lambda **kw: sheets.backend({"name": "a", "prompt": "p", **kw})  # noqa: E731
        for model in (None, "wan3.0-video", "wan3.0-video-prime", "happyhorse-1.1", "happyhorse-1.1-r2v"):
            self.assertIs(b(model=model), bailian, model)
        for model in ("seedance-2.5", "seedance-2.0", "doubao-seedance-2-5-260628", "doubao-seedance-2-0-260128"):
            self.assertIs(b(model=model), ark_video, model)
        for model in ("minimax-h3", "MiniMax-H3-Max"):
            self.assertIs(b(model=model), minimax_video, model)
        self.assertIs(b(size="1536x864"), openai_image)
        self.assertIs(b(model="gpt-image-2.6-sunburst"), openai_image)
        for bad in ({"model": "kling-4.0"}, {"model": "seedance-9"}, {"size": "1536x864", "model": "wan3.0-video"}):
            with self.assertRaises(ValueError):
                b(**bad)

    def test_problem(self):
        job = {"name": "a", "prompt": "p", "duration": 4}
        self.assertIn("duration must be 5..15 s", minimax_video.problem({**job, "model": "minimax-h3"}))
        self.assertIn("ratio other than adaptive", minimax_video.problem({**job, "duration": 5, "ratio": "adaptive"}))
        self.assertIn(".mp4", minimax_video.problem({**job, "duration": 5, "reference_video": "v.mov"}))
        self.assertEqual(ark_video.problem({**job, "model": "seedance-2.5"}), "")
        self.assertIn("duration must be 4..15 s", ark_video.problem({**job, "model": "seedance-2.0", "duration": 16}))
        self.assertIn("reference video", ark_video.problem({**job, "model": "seedance-2.5", "reference_video": "v.mp4"}))
        self.assertIn("at most 16", openai_image.problem({"name": "i", "prompt": "p", "images": ["a.png"] * 17}))
        self.assertIn("outside [2, 15]", bailian.problem({"name": "a", "prompt": "p", "duration": 16}))
        self.assertEqual(bailian.problem({"name": "a", "prompt": "p", "duration": 2, "resolution": "480P"}), "")


class Bodies(unittest.TestCase):
    """The request bodies, field by field, as the official docs write them."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        png(self.dir / "a.png")
        png(self.dir / "b.png")

    def tearDown(self):
        self.tmp.cleanup()

    def test_ark(self):
        a, b = str(self.dir / "a.png"), str(self.dir / "b.png")
        refs = tasks.wire_payload(ark_video.build_payload({
            "name": "s", "model": "seedance-2.5", "prompt": "图1和图2", "duration": 5, "resolution": "720P", "seed": 1,
            "reference_images": [a, b]}), self.dir)
        self.assertEqual(refs["model"], "doubao-seedance-2-5-260628")
        self.assertEqual(refs["content"][0], {"type": "text", "text": "@图片1和@图片2"})
        self.assertEqual([(c["type"], c["role"]) for c in refs["content"][1:]], [("image_url", "reference_image")] * 2)
        self.assertTrue(refs["content"][1]["image_url"]["url"].startswith("data:image/png;base64,"))
        self.assertEqual({k: v for k, v in refs.items() if k not in ("model", "content")},
                         {"resolution": "720p", "ratio": "16:9", "duration": 5, "generate_audio": True, "watermark": False})
        frames = tasks.wire_payload(ark_video.build_payload({
            "name": "f", "model": "seedance-2.5", "prompt": "p", "duration": 4, "first_frame": a, "last_frame": b,
            "ratio": "16:9", "return_last_frame": True}), self.dir)
        self.assertEqual([c.get("role") for c in frames["content"]], [None, "first_frame", "last_frame"])
        self.assertEqual((frames["ratio"], frames["return_last_frame"]), ("adaptive", True))  # 2.5: frames take adaptive only

    def test_last_frame_of_an_earlier_job(self):
        job = {"name": "n2", "model": "seedance-2.0", "prompt": "p", "duration": 5, "first_frame": "@n1"}
        payload = ark_video.build_payload(job)
        self.assertIn("<last frame of n1", tasks.wire_payload(payload, None)["content"][1]["image_url"]["url"])
        with self.assertRaises(ValueError):
            tasks.wire_payload(payload, self.dir)
        (self.dir / "n1.last_frame_url").write_text("https://example.invalid/n1.jpeg\n")
        self.assertEqual(tasks.wire_payload(payload, self.dir)["content"][1]["image_url"]["url"],
                         "https://example.invalid/n1.jpeg")

    def test_minimax(self):
        t2v = tasks.wire_payload(minimax_video.build_payload(
            {"name": "m", "model": "minimax-h3", "prompt": "图1", "duration": 5, "resolution": "768p", "seed": 1}), self.dir)
        self.assertEqual(t2v, {"model": "MiniMax-H3-Max", "content": [{"type": "text", "text": "图1"}],
                               "resolution": "768P", "duration": 5, "ratio": "16:9", "generate_audio": True,
                               "extra": {"prompt_expansion_mode": "disabled"}})
        i2v = tasks.wire_payload(minimax_video.build_payload(
            {"name": "m", "model": "MiniMax-H3-Max", "prompt": "p", "duration": 6, "first_frame": str(self.dir / "a.png"),
             "audio": False, "prompt_extend": True}), self.dir)
        self.assertEqual(i2v["content"][1]["role"], "first_frame")
        self.assertEqual((i2v["ratio"], i2v["generate_audio"], i2v["extra"]),
                         ("adaptive", False, {"prompt_expansion_mode": "balanced"}))


class FakeClient:
    """Answers the create call with a task id and the query calls from `polls`; records every call."""

    def __init__(self, created: dict, polls: list[dict], post_fails: bool = False):
        self.created, self.polls, self.post_fails, self.calls = created, list(polls), post_fails, []

    def call(self, method, path, body=None):
        self.calls.append((method, path))
        if method == "POST":
            if self.post_fails:
                raise TimeoutError("no answer")
            return self.created
        return self.polls.pop(0) if len(self.polls) > 1 else self.polls[0]

    def download(self, url, dst):
        dst.write_bytes(b"\x00\x00\x00\x18ftypmp42")


class TaskFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        self.results = self.out / "results.jsonl"
        self.patches = [mock.patch.object(tasks.time, "sleep", lambda _s: None), mock.patch.object(tasks, "log", lambda *_a, **_k: None),
                        mock.patch.object(tasks, "probe", lambda _v: {"format": {"duration": "5.0"}})]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def line(self) -> dict:
        return json.loads(self.results.read_text().splitlines()[-1])

    def test_ark_succeeds_with_last_frame(self):
        job = {"name": "k1", "model": "seedance-2.5", "prompt": "p", "duration": 5, "resolution": "480p",
               "return_last_frame": True}
        done = {"id": "cgt-1", "status": "succeeded", "duration": 5, "created_at": 1, "updated_at": 2,
                "content": {"video_url": "https://example.invalid/v.mp4", "last_frame_url": "https://example.invalid/l.jpeg"},
                "usage": {"completion_tokens": 100, "total_tokens": 100}}
        client = FakeClient({"id": "cgt-1"}, [{"id": "cgt-1", "status": "queued"}, {"id": "cgt-1", "status": "running"}, done])
        self.assertTrue(tasks.one(ark_video, job, client, self.out, self.results))
        state = json.loads((self.out / "k1.json").read_text())
        self.assertEqual((state["status"], state["task_id"]), ("DOWNLOADED", "cgt-1"))
        self.assertEqual(state["payload"]["parameters"]["resolution"], "480p")
        self.assertEqual(state["usage"]["duration"], 5)
        self.assertEqual(set(state["timing"]), {"submit_time", "end_time"})
        link = self.out / "k1.last_frame_url"
        self.assertEqual((link.read_text(), link.stat().st_mode & 0o777), ("https://example.invalid/l.jpeg", 0o600))
        self.assertEqual([m for m, _p in client.calls], ["POST", "GET", "GET", "GET"])
        self.assertEqual(client.calls[1][1], "/contents/generations/tasks/cgt-1")
        self.assertTrue(self.line()["ok"])

    def test_minimax_failure_is_recorded_once(self):
        job = {"name": "m1", "model": "minimax-h3", "prompt": "p", "duration": 5}
        failed = {"task": {"id": "9", "status": "failed", "error": {"code": "1026", "message": "sensitive content"}}}
        client = FakeClient({"task_id": "9"}, [failed])
        self.assertFalse(tasks.one(minimax_video, job, client, self.out, self.results))
        state = json.loads((self.out / "m1.json").read_text())
        self.assertEqual((state["status"], state["failure"]["status"]), ("FAILED", "failed"))
        self.assertEqual(client.calls, [("POST", "/v2/video_generation"), ("GET", "/v2/query/video_generation/9")])
        self.assertIn("1026", self.line()["error"])

    def test_lost_acknowledgement_is_never_resent(self):
        job = {"name": "k2", "model": "seedance-2.0", "prompt": "p", "duration": 5}
        client = FakeClient({"id": "x"}, [{"status": "running"}], post_fails=True)
        self.assertFalse(tasks.one(ark_video, job, client, self.out, self.results))
        self.assertFalse(tasks.one(ark_video, job, client, self.out, self.results))
        self.assertEqual(client.calls, [("POST", "/contents/generations/tasks")])
        self.assertIn("no task id", self.line()["error"])


def refuse(*_a, **_k):
    raise AssertionError("request tried to reach the network, run a command or read a key")


class RequestSendsNothing(unittest.TestCase):
    def test_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            png(tmp / "a.png")
            png(tmp / "b.png")
            sheets_ = {
                "wan.json": {"name": "w", "prompt": "p", "duration": 2, "resolution": "480P", "first_frame": "a.png"},
                "hh.json": {"name": "h", "prompt": "p [Image 1]", "duration": 3, "model": "happyhorse-1.1", "reference_images": ["a.png"]},
                "sd.json": {"name": "s", "prompt": "图1", "duration": 4, "resolution": "720P", "seed": 1,
                            "model": "seedance-2.5", "reference_images": ["a.png", "b.png"]},
                "mm.json": {"name": "m", "prompt": "p", "duration": 5, "model": "minimax-h3", "first_frame": "a.png"},
                "img.json": {"name": "i", "prompt": "p", "size": "1536x864", "images": ["a.png", "b.png"]},
                "t2i.json": {"name": "t", "prompt": "p", "kind": "image"},
            }
            for f, s in sheets_.items():
                (tmp / f).write_text(json.dumps(s, ensure_ascii=False))
            before = sorted(p.name for p in tmp.iterdir())
            out = io.StringIO()
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                with mock.patch.object(socket.socket, "connect", refuse), \
                        mock.patch.object(socket, "create_connection", refuse), \
                        mock.patch.object(urllib.request, "urlopen", refuse), \
                        mock.patch.object(urllib.request.OpenerDirector, "open", refuse), \
                        mock.patch.object(subprocess, "run", refuse), mock.patch.object(subprocess, "Popen", refuse), \
                        mock.patch.object(bailian, "read_key", refuse), mock.patch.object(tasks, "read_key", refuse), \
                        mock.patch.object(openai_image, "key", refuse), \
                        contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    code = filmgen.main(["request", *sheets_])
            finally:
                os.chdir(cwd)
            text = out.getvalue()
            self.assertEqual(code, 0, text)
            self.assertNotIn("problem", text)
            self.assertNotIn("Authorization", text)
            self.assertNotIn("Bearer", text)
            self.assertEqual(sorted(p.name for p in tmp.iterdir()), before)  # nothing written
            shown = [json.loads(chunk) for chunk in text.replace("}\n{", "}\x00{").split("\x00")]
            self.assertEqual([s["backend"] for s in shown],
                             ["bailian", "bailian", "ark_video", "minimax_video", "openai_image", "openai_image"])
            self.assertEqual(shown[1]["model"], "happyhorse-1.1-r2v")
            self.assertEqual(shown[2]["url"], ark_video.BASE + "/contents/generations/tasks")
            self.assertEqual(shown[2]["body"]["content"][0]["text"], "@图片1")
            self.assertEqual(shown[3]["url"], minimax_video.BASE + "/v2/video_generation")
            self.assertEqual(shown[4]["url"], openai_image.machine.IMAGE_BASE + "/images/edits")
            self.assertTrue(all(s.get("body_sha256") for s in shown))


if __name__ == "__main__":
    unittest.main()

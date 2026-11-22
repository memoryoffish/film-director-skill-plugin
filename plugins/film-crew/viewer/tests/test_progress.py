"""scripts/progress.py：给了价格文件写花费，没给只写时间；每一次生成一格。"""
import argparse
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import progress  # noqa: E402

PRICES = {"wan_price_cny_per_s": {"wan3.0-video": {"list": {"720P": 0.6}, "discount": {"720P": 0.42}}}}


class Progress(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = pathlib.Path(self.tmp.name)
        self.clips, self.out = t / "clips", t / "page"
        self.clips.mkdir()
        self.out.mkdir()
        state = {"task_id": "x", "submitted_utc": 1_700_000_000, "payload": {"model": "wan3.0-video", "parameters": {"resolution": "720P"}},
                 "timing": {"submit_time": "2026-11-20 10:00:00", "end_time": "2026-11-20 10:03:00"}}
        (self.clips / "U1_t1.json").write_text(json.dumps({**state, "name": "U1_t1", "status": "FAILED"}))
        (self.clips / "U1_t2.json").write_text(json.dumps({**state, "name": "U1_t2", "status": "DOWNLOADED", "usage": {"duration": 5}}))
        (self.clips / "U1_t2.mp4").write_bytes(b"")
        (t / "prices.json").write_text(json.dumps(PRICES))
        self.prices = str(t / "prices.json")

    def tearDown(self):
        self.tmp.cleanup()

    def page(self, **kw) -> str:
        a = argparse.Namespace(out=str(self.out), jobs=[str(self.clips)], remote=None, cuts=None, local_cuts=None, events=None,
                               story=None, units=None, order=None, title="试", estimate_cny=None, price="list", every=None, prices=None,
                               style=None)
        vars(a).update(kw)
        return progress.build(a).read_text(encoding="utf-8")

    def test_money_from_price_file(self):
        self.assertIn("花费 ¥3（原价）", self.page(prices=self.prices))              # 5 秒 × 0.6
        self.assertIn("花费 ¥2 / 估 ¥10（折扣价）", self.page(prices=self.prices, price="discount", estimate_cny=10))

    def test_time_only_without_prices(self):
        h = self.page()
        self.assertNotIn("花费", h)
        self.assertIn("开工", h)

    def test_takes(self):
        h = self.page()
        self.assertIn("抽了 2 次", h)
        self.assertIn("U1_t2.mp4", h)
        self.assertIn("3.0 分钟", h)


if __name__ == "__main__":
    unittest.main()

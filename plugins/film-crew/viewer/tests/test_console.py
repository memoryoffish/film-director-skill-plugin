"""scripts/console.py 从清单出页面数据：展示台的每一镜、节点图的实体表、从文件读工作流。
用 synth_run.py 的合成运行目录经 ../formats/read_run.py 读成清单；标成还没开拍（plan），不抽帧、不转码，不要 ffmpeg。
要 Pillow（转图）。"""
import concurrent.futures as cf
import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
FORMATS = HERE.parents[1] / "formats"
sys.path[:0] = [str(HERE), str(HERE.parent / "scripts"), str(FORMATS)]


def sealed(wf: dict) -> str:
    """和 shots2comfy 写文件一样：记一笔 sha1 再写成文本。"""
    wf["extra"]["filmkit"]["sha1"] = hashlib.sha1(json.dumps(wf, ensure_ascii=False, indent=1).encode("utf-8")).hexdigest()
    return json.dumps(wf, ensure_ascii=False, indent=1)


@unittest.skipUnless((FORMATS / "read_run.py").is_file() and importlib.util.find_spec("PIL"), "要 formats 在旁边、装了 Pillow")
class Console(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import console
        import read_run
        from synth_run import make_run
        cls.c = console
        cls.tmp = tempfile.TemporaryDirectory()
        t = pathlib.Path(cls.tmp.name)
        root = make_run(t / "run")
        m = read_run.manifest({"key": "synth", "run": str(root)}, root)
        cls.m = {**m, "plan": True, "seconds": 20.0}
        # 工作流目录：每镜一份 shots2comfy 写的；A1 另有一份人改过的
        cls.wf = t / "workflows"
        (cls.wf / "synth").mkdir(parents=True)
        for s in m["shots"]:
            nodes = [{"properties": {"filmkit": {"file": f}}} for f in [*(s.get("keyframes") or {}), *(s.get("images") or {})]]
            wf = {"nodes": nodes, "extra": {"filmkit": {"film": "synth", "shot": s["name"]}}}
            (cls.wf / "synth" / f"{s['name']} {s['what'].replace('/', ' ')}.json").write_text(sealed(wf), encoding="utf-8")
        (cls.wf / "synth" / "A1（人改过）首帧生视频.json").write_text(
            json.dumps({"nodes": [], "extra": {"filmkit": {"film": "synth", "shot": "A1", "sha1": "x"}}}), encoding="utf-8")
        cls.out = t / "site"
        cls.data = cls.build(cls.wf)

    @classmethod
    def build(cls, workflows, compact=False):
        futs = []
        with cf.ThreadPoolExecutor(4) as pool, cf.ThreadPoolExecutor(1) as enc:
            d = cls.c.build(cls.m, cls.out, pool, enc, futs, compact, 960, True, workflows)
            for f in futs:
                f.result()
        return d

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def row(self, name):
        return next(r for r in self.data["shots"] if r["n"] == name)

    def test_film(self):
        d = self.data
        self.assertEqual((d["key"], d["seconds"], d["plan"], d["film"], d["previz"]), ("synth", 20.0, True, None, None))
        self.assertEqual(d["roles"], {"girl": "女孩，全身"})

    def test_rows(self):
        a5 = self.row("A5")
        self.assertEqual(a5["first"]["k"], "k_A5")                       # 参考图生视频也给了首帧，照发出去的摆
        self.assertEqual(a5["rv"], "previz_cut.mp4")
        self.assertEqual(a5["wm"], ["synth/wm/D.jpg", None])
        self.assertEqual(self.row("A3")["kref"], 1)
        self.assertEqual([r["l"] for r in self.row("A3")["refs"]], ["参考图 girl", "关键帧 k_A3_a", "关键帧 k_A4_a", "参考图 ref_plate"])
        self.assertEqual(self.row("A1")["params"], {"duration": 3, "seed": 7, "model": "wan3.0-video", "resolution": "720P",
                                                    "prompt_extend": False})
        self.assertEqual(self.row("A7")["job"], "")
        self.assertEqual(self.row("A6")["wm"][0], "synth/wm/A6_a.jpg")
        self.assertEqual(self.row("A6")["first"]["f"], "synth/keys/k_A6.jpg")   # 绝对路径，媒体名用运行目录里的位置
        self.assertTrue((self.out / "synth" / "keys" / "k_A6.jpg").is_file())

    def test_keys(self):
        k = self.data["keys"]
        self.assertEqual(list(k)[:3], ["k_A1", "k_A2_a2", "k_A2_b"])           # 按镜头次序第一次碰到
        self.assertEqual([x["l"] for x in k["k_A1"]["in"]], ["图1 白模 A1_a", "图2 关键帧 k_D", "图3 参考图 girl"])
        self.assertIn("k_A8", k)                                               # 出图记录在图旁边，展示台认
        self.assertNotIn("k_D", k)                                             # 没直接喂进视频

    def test_graph(self):
        G = self.data["graph"]
        self.assertEqual(G["key"]["k_A1"]["use"], [["A1", "首帧"]])
        self.assertEqual(G["key"]["k_D"]["p"], "the base frame")               # 展示台没记它的 prompt，这里记
        self.assertNotIn("p", G["key"]["k_A1"])
        self.assertNotIn("k_A8", G["key"])                                     # 不在 keys/，节点图当一张图
        self.assertEqual(G["img"]["wm/room/A1_a.png"], {"f": "synth/wm/room/A1_a.jpg", "shot": "room/A1", "end": "a",
                                                        "note": "子目录里的站位"})
        self.assertEqual([t["n"] for t in G["job"]["v2r"]["takes"]], ["v2", "v2r"])
        self.assertEqual(G["job"]["v2r"]["takes"][0]["st"], "failed")
        self.assertEqual(G["job"]["U1_t1"]["shots"], ["A3", "A4"])
        self.assertEqual(G["job"]["U1_t1"]["w"]["model"], "seedance-2.5")
        self.assertEqual(G["job"]["v1"]["w"]["model"], "wan3.0-video")
        self.assertEqual(G["job"]["v6"]["w"]["model"], "Wan 3.0")             # 任务里没写，用片头写的
        self.assertEqual(G["job"]["r5"]["video"], "previz_cut.mp4")
        self.assertEqual(G["shot"][6], {"wm": ["wm/A7_a.png", None]})

    def test_workflows(self):
        G = self.data["graph"]
        wfs = json.loads(self.c.gzip.decompress(self.c.base64.b64decode(G["wfz"])))
        self.assertEqual([n for n, _ in wfs][:2], ["A1 首帧生视频.json", "A2 首尾帧，重抽过.json"])   # 人改过的那份不用
        self.assertEqual(wfs[0][1], (self.wf / "synth" / "A1 首帧生视频.json").read_text(encoding="utf-8"))
        self.assertEqual(G["media"]["keys/k_A1.png"], "synth/keys/k_A1.jpg")

    def test_missing_workflow_or_none(self):
        empty = pathlib.Path(self.tmp.name) / "no-workflows"
        (empty / "synth").mkdir(parents=True)
        self.assertNotIn("wfz", self.build(empty)["graph"])
        self.assertIsNone(self.build(None)["graph"])

    def test_compact(self):
        rows = {r["n"]: r for r in self.build(self.wf, compact=True)["shots"]}
        self.assertIsNone(rows["A1"]["wm"][1])                                 # 精简时没喂尾帧就不放白模尾帧
        self.assertEqual(rows["A2"]["wm"][1], "synth/wm/A2_b.jpg")


if __name__ == "__main__":
    unittest.main()

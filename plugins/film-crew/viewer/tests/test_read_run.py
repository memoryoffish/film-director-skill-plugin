"""../formats/read_run.py 读合成运行目录（synth_run.py）：清单里该有的事实都在，格式查得过。"""
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
FORMATS = HERE.parents[1] / "formats"
sys.path[:0] = [str(HERE), str(FORMATS)]


@unittest.skipUnless((FORMATS / "read_run.py").is_file(), "formats 不在 viewer 旁边")
class ReadRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import check_manifest
        import read_run
        from synth_run import make_run
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = make_run(pathlib.Path(cls.tmp.name) / "run")
        cls.m = read_run.manifest({"key": "synth", "run": str(cls.root), "flag": {"t": 4, "shots": ["A2"], "note": "重抽过"}}, cls.root)
        cls.check = staticmethod(check_manifest.check)
        cls.s = {s["name"]: s for s in cls.m["shots"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_format(self):
        self.assertEqual(self.check(self.m), [])

    def test_film_facts(self):
        m = self.m
        self.assertEqual((m["genre"], m["flag"]["shots"], m["roles"]), ("测试", ["A2"], {"girl": "女孩，全身"}))
        self.assertEqual(m["recon"], "从剪辑表重建的镜头表")
        self.assertNotIn("previz", m)            # 运行目录里没有 previz.mp4
        self.assertNotIn("plan", m)
        self.assertNotIn("seconds", m)           # 开拍了的片子，片长看成片本身

    def test_which_job(self):
        s = self.s
        self.assertEqual(s["A6"]["video"]["name"], "v6")            # 只在剪辑表里
        self.assertNotIn("video", s["A7"])
        self.assertEqual(s["A3"]["video"]["shots"], ["A3", "A4"])

    def test_sent_keeps_what_the_feed_drops(self):
        v = self.s["A5"]["video"]
        self.assertEqual(v["feed"], "R2V")
        self.assertNotIn("first", v)                                # ComfyUI 那几项照喂法取舍
        self.assertEqual(v["sent"]["first_frame"], "keys/k_A5.png")  # 任务文件原样
        self.assertNotIn("prompt", v["sent"])
        self.assertEqual(v["status"], "succeeded")

    def test_stills(self):
        s = self.s
        self.assertEqual(s["A1"]["stills"], ["wm/room/A1_a.png", None])     # 子目录里按名字找到
        self.assertNotIn("named_stills", s["A1"])                          # 白模目录最上层没有
        self.assertEqual(s["A5"]["stills"], ["wm/D.png", None])            # 没有按名字的，取关键帧出图时用的白模
        self.assertEqual(s["A7"]["named_stills"], ["wm/A7_a.png", None])   # 没喂进去的也记
        self.assertEqual(s["A2"]["stills"], ["wm/A2_a.png", "wm/A2_b.png"])

    def test_own_ref(self):
        self.assertEqual((self.s["A3"]["own_ref"], self.s["A4"]["own_ref"]), (1, 2))   # prompt 写了「图2、图3依次是镜头1、镜头2」

    def test_pictures(self):
        p = self.m["pictures"]
        self.assertEqual(p["kf9/k_A8.png"]["made_by"], "k_A8")              # 出图记录在图旁边
        self.assertNotIn("keyframe", p["kf9/k_A8.png"])                    # 不在 keys/，节点图不往上追
        self.assertEqual(p["img/A8_end.png"], {"label": "关键帧 A8_end（A8 尾帧）", "made_by": "A8_end"})
        self.assertTrue(p["keys/k_A1.png"]["keyframe"])
        self.assertEqual(p["keys/ref_plate.png"], {"label": "参考图 ref_plate"})
        self.assertEqual(p["wm/room/A1_a.png"]["still"], ["room/A1", "a"])
        self.assertEqual(p["wm/A2_b.png"]["note"], "她站起来")
        a6 = self.s["A6"]["video"]["sent"]["first_frame"]
        self.assertTrue(a6.startswith("/"))
        self.assertEqual(p[a6]["label"], "关键帧 k_A6（A6 首帧）")          # 绝对路径按运行目录里的位置认
        self.assertIn("keys/k_D.png", p)                                   # 出关键帧用到的图也在（k_A1 的图2）
        self.assertIn("wm/D.png", p)

    def test_attempts(self):
        a = self.s["A2"]["video"]["attempts"]
        self.assertEqual([(t["name"], t["used"], t["status"]) for t in a], [("v2", False, "failed"), ("v2r", True, "ok")])
        self.assertEqual(a[0]["error"], "SetLimitExceeded")
        self.assertEqual(a[0]["diff"], ["prompt", "first_frame", "seed"])
        self.assertEqual(a[0]["was"], {"first_frame": "keys/k_A2_a.png"})
        self.assertIsNone(a[0]["why"])
        r = self.m["image_jobs"]["k_A2_a2"]["attempts"]
        self.assertEqual([(t["name"], t["used"]) for t in r], [("k_A2_a", False), ("k_A2_a2", True)])
        self.assertFalse(self.m["image_jobs"]["k_A5"]["ok"])

    def test_comfy_part_unchanged(self):
        s = self.s["A2"]
        self.assertEqual(s["video"]["takes"], [["v2", False, False], ["v2r", True, True]])
        self.assertEqual(sorted(s["keyframes"]), ["keys/k_A2_a2.png", "keys/k_A2_b.png"])
        self.assertEqual(s["images"]["wm/A2_b.png"], {"kind": "wm", "title": "白模 · A2 结尾"})


if __name__ == "__main__":
    unittest.main()

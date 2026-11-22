"""../formats/check_manifest.py：手写的例子查得过；几种写错的各报出来。"""
import copy
import json
import pathlib
import sys
import unittest

FORMATS = pathlib.Path(__file__).resolve().parents[2] / "formats"
sys.path.insert(0, str(FORMATS))
DEMO = FORMATS / "examples" / "manifest" / "demo.shots.json"


@unittest.skipUnless(DEMO.is_file(), "formats 不在 viewer 旁边")
class CheckManifest(unittest.TestCase):
    def setUp(self):
        from check_manifest import check
        self.check = check
        self.m = json.loads(DEMO.read_text(encoding="utf-8"))

    def bad(self, change, want: str):
        m = copy.deepcopy(self.m)
        change(m)
        problems = self.check(m)
        self.assertTrue(any(want in p for p in problems), problems)

    def test_demo_ok(self):
        self.assertEqual(self.check(self.m), [])

    def test_without_viewer_fields_ok(self):
        m = {k: v for k, v in self.m.items() if k in ("film", "title", "root", "video", "shots")}
        m["shots"] = [{k: v for k, v in s.items() if k not in ("feed_note", "stills", "named_stills", "own_ref")} for s in m["shots"]]
        self.assertEqual(self.check(m), [])

    def test_problems(self):
        self.bad(lambda m: m.pop("root"), "root")
        self.bad(lambda m: m["shots"][0]["video"].update(feed="I2X"), "feed one of")
        self.bad(lambda m: m["shots"][0]["video"].pop("first"), "needs first")
        self.bad(lambda m: m["shots"][1].update(t0=99), "t0 <= t1")
        self.bad(lambda m: m["shots"][1].update(name="A1"), "names used twice")
        self.bad(lambda m: m["shots"][0]["keyframes"].update({"pics/x.png": {"inputs": []}}), "uses directly")
        self.bad(lambda m: m["shots"][0]["images"]["pics/girl.png"].update(kind="person"), "images[pics/girl.png]")
        self.bad(lambda m: m["shots"][2].update(own_ref=3), "own_ref")
        self.bad(lambda m: m["shots"][0].update(stills=["pics/block.png"]), "stills")
        self.bad(lambda m: m["pictures"]["pics/girl.png"].update(made_by="nope"), "not in image_jobs")
        self.bad(lambda m: m["image_jobs"].pop("a3"), "keyframe, but 'a3'")
        self.bad(lambda m: m["shots"][0]["video"]["attempts"][0].update(used=True), "the one used should be")
        self.bad(lambda m: m["flag"].update(shots=["Z9"]), "flag")


if __name__ == "__main__":
    unittest.main()

"""scripts/styles.py 和 styles/：不选风格页面一个字不变；选了的那几套各自只管自己（每条规则都在自己的名字底下）。"""
import argparse
import json
import pathlib
import re
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import progress  # noqa: E402
import styles  # noqa: E402

PAGE = "<html><head><title>x</title></head><body><main><p>事实</p></main></body></html>"
NAMES = sorted(p.name for p in (ROOT / "styles").iterdir() if p.is_dir())


def blocks(css: str):
    """最外层的每一块：(花括号前面的那一段, 花括号里面的)。引号里和 url(...) 里的花括号、分号不算。"""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    i, start, depth, quote, paren = 0, 0, 0, "", 0
    while i < len(css):
        c = css[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = ""
        elif c in "\"'":
            quote = c
        elif c == "(":
            paren += 1
        elif c == ")":
            paren -= 1
        elif paren:
            pass
        elif c == "{":
            if depth == 0:
                head, body = css[start:i].strip(), i + 1
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                yield head, css[body:i]
                start = i + 1
        elif c == ";" and depth == 0:
            yield css[start:i].strip(), None
            start = i + 1
        i += 1


def selectors(head: str) -> list[str]:
    out, cur, depth, quote = [], "", 0, ""
    for c in head:
        if quote:
            quote = "" if c == quote else quote
        elif c in "\"'":
            quote = c
        elif c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
            continue
        cur += c
    return out + [cur.strip()]


def stray(name: str, css: str) -> list[str]:
    """这份 CSS 里管到自己名字外面去的东西。"""
    scope, bad = f':root[data-style="{name}"]', []
    for head, body in blocks(css):
        if body is None:
            bad.append(head[:80])                                  # @import、@charset……都不要
        elif head.startswith(("@media", "@supports", "@container")):
            bad += stray(name, body)
        elif head.startswith("@keyframes"):
            bad += [] if head.split()[1].startswith(f"{name}-") else [head]
        elif head.startswith("@property"):
            bad += [] if head.split()[1].startswith(f"--{name}-") else [head]
        elif head.startswith("@"):
            bad.append(head[:80])
        else:
            bad += [s[:80] for s in selectors(head) if not s.startswith(scope)]
    return bad


class Dress(unittest.TestCase):
    def test_page_itself_is_kept(self):
        out = styles.dress(PAGE, ["plain", *NAMES], ["progress"], {"updated": "10:00:00"})
        self.assertTrue(out.startswith("<html><head><title>x</title>"))
        self.assertIn("</head><body><main><p>事实</p></main>", out)
        self.assertTrue(out.endswith("</body></html>"))

    def test_each_style_in_its_own_block(self):
        out = styles.dress(PAGE, ["plain", *NAMES], ["progress"])
        for n in NAMES:
            self.assertEqual(out.count(f'<style data-style="{n}">'), 1)
        self.assertNotIn('<style data-style="plain">', out)
        cfg = json.loads(re.search(r'\}\)\((\{"names".*?\})\);\s*</script>', out).group(1))
        self.assertEqual(cfg["names"], ["plain", *NAMES])
        self.assertEqual(cfg["labels"]["plain"], "原样")

    def test_facts_cannot_close_the_script(self):
        out = styles.dress(PAGE, ["plain", NAMES[0]], ["progress"], {"title": "</script><b>"})
        facts = re.search(r'<script type="application/json" id="style-facts">(.*?)</script>', out).group(1)
        self.assertEqual(json.loads(facts), {"title": "</script><b>"})

    def test_unknown_style_or_part_stops(self):
        with self.assertRaises(SystemExit):
            styles.dress(PAGE, ["nope"], ["progress"])
        with self.assertRaises(SystemExit):
            styles.dress(PAGE, [NAMES[0]], ["nopart"])


class Scoped(unittest.TestCase):
    def test_parser_sees_what_it_should(self):
        css = ('/* x */:root[data-style="a"] p,:root[data-style="a"] q:is(i,b){color:red}'
               '@media (max-width:9px){:root[data-style="a"] p{background:url("data:x,{};")}h1{top:0}}'
               '@keyframes a-spin{to{rotate:1turn}}@keyframes spin{to{rotate:1turn}}@property --a-x{syntax:"*";inherits:false}'
               '@import url(x.css);body{margin:0}')
        self.assertEqual(stray("a", css), ["h1", "@keyframes spin", "@import url(x.css)", "body"])

    def test_every_rule_under_its_own_name(self):
        for n in NAMES:
            for f in sorted((ROOT / "styles" / n).glob("*.css")):
                with self.subTest(file=f"{n}/{f.name}"):
                    self.assertEqual(stray(n, f.read_text(encoding="utf-8")), [])

    def test_scripts_register_under_their_own_name(self):
        for n in NAMES:
            for f in sorted((ROOT / "styles" / n).glob("*.js")):
                with self.subTest(file=f"{n}/{f.name}"):
                    text = f.read_text(encoding="utf-8")
                    self.assertRegex(text, rf"\b(S|FilmStyles)\.{n}\b")
                    self.assertRegex(text, rf"\.{f.stem}\s*=\s*\{{")
                    self.assertRegex(text, r"\boff\s*\(")


class ProgressPage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = pathlib.Path(self.tmp.name)
        self.clips, self.out = t / "clips", t / "page"
        self.clips.mkdir()
        self.out.mkdir()
        (self.clips / "U1_t1.json").write_text(json.dumps({"task_id": "x", "name": "U1_t1", "status": "DOWNLOADED", "submitted_utc": 1_700_000_000,
                                                           "usage": {"duration": 5}}))
        (self.clips / "U1_t1.mp4").write_bytes(b"")

    def tearDown(self):
        self.tmp.cleanup()

    def page(self, style) -> str:
        a = argparse.Namespace(out=str(self.out), jobs=[str(self.clips)], remote=None, cuts=None, local_cuts=None, events=None,
                               story=None, units=None, order=None, title="试", estimate_cny=None, price="list", every=None, prices=None,
                               style=style)
        return progress.build(a).read_text(encoding="utf-8")

    def test_without_style_nothing_is_added(self):
        text = self.page(None)
        for word in ("data-style", "fs-switch", "FilmStyles", "style-facts"):
            self.assertNotIn(word, text)

    def test_with_style_the_page_is_inside(self):
        plain, dressed = self.page(None), self.page("plain," + ",".join(NAMES))
        clock = re.compile(r"更新 \d\d:\d\d:\d\d|开工 \d+ 分钟")
        body = lambda s: clock.sub("", s[s.index("<main"):s.index("</main>")])  # noqa: E731
        self.assertEqual(body(plain), body(dressed))
        facts = json.loads(re.search(r'id="style-facts">(.*?)</script>', dressed).group(1))
        self.assertEqual(set(facts), {"updated", "elapsed", "spent", "estimate", "price"})


if __name__ == "__main__":
    unittest.main()

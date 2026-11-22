#!/usr/bin/env python3
"""风格：给页面换一身样子，页面上的事实和能做的事不动。

一套风格是 styles/<名字>/ 一个文件夹：
    tokens.css       这套风格的颜色、字体、圆角……（可以没有）；每一页都带上
    <部分>.css        一页由一个或几个部分拼成：进度页是 progress
    <部分>.js         可以没有
CSS 每条规则都写在 :root[data-style="<名字>"] 底下，@keyframes、@property 的名字带「<名字>-」前缀：没选这套时，
它对页面一点影响都没有。JS 登记 FilmStyles["<名字>"]["<部分>"] = {on(), off()}：on 里加的元素、挂的监听、挪过的
节点，off 里都还原。页面上没写成标签的事实（更新时间、开工多久、花费……）从 <script id="style-facts"> 读。
plain 是页面本来的样子，没有文件。
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "styles"
LABEL = {"plain": "原样", "fancy": "Fancy", "warm": "暖心"}
# 先把选中的风格写到 <html> 上，页面第一眼就是那一套：地址里的 ?style= > 浏览器里记的 > 第一套
BOOT = ("<script>(function(n,d){var s=new URLSearchParams(location.search).get('style');"
        "try{s=s||localStorage.getItem('film-style')}catch(e){}"
        "if(n.indexOf(s)<0)s=n[0];if(s!=='plain')d.dataset.style=s})(%s,document.documentElement)</script>")


def script(text: str) -> str:
    return text.replace("</", "<\\/")


def dress(page: str, names: list[str], parts: list[str], facts: dict | None = None, hosts: list[str] | None = None) -> str:
    """把 names 这几套风格装进 page。parts：这一页由哪几个部分拼成。只给一套风格就一直用它；给了几套，页面上多一个切换
    （第一套是默认），选了哪套记在浏览器里。hosts：切换放进页面的哪几处（CSS 选择器，放在它里面的最后；不给就放在
    <main> 的最前面）。facts：页面上没写成标签的事实，给风格的脚本读。"""
    styles = [n for n in names if n != "plain"]
    css, js = {}, {}
    for n in styles:
        files = [ROOT / n / "tokens.css", *(ROOT / n / f"{p}.css" for p in parts)]
        if not any(f.is_file() for f in files[1:]):
            raise SystemExit(f"no style {n!r} for this page: none of {[f.name for f in files[1:]]} in {ROOT / n}")
        css[n] = "\n".join(f.read_text(encoding="utf-8") for f in files if f.is_file())
        js[n] = "\n".join(f.read_text(encoding="utf-8") for p in parts if (f := ROOT / n / f"{p}.js").is_file())
    head = BOOT % json.dumps(names)
    head += f"<style>{(ROOT / 'switch.css').read_text(encoding='utf-8')}</style>"
    head += "".join(f'<style data-style="{n}">{css[n]}</style>' for n in styles)
    tail = f'<script type="application/json" id="style-facts">{json.dumps(facts or {}, ensure_ascii=False).replace("<", chr(92) + "u003c")}</script>'
    tail += "".join(f"<script>{script(js[n])}</script>" for n in styles if js[n])
    cfg = json.dumps({"names": names, "labels": {n: LABEL.get(n, n) for n in names}, "hosts": hosts or []}, ensure_ascii=False)
    tail += f"<script>{script((ROOT / 'switch.js').read_text(encoding='utf-8')).replace('/*CFG*/{}', cfg)}</script>"
    return page.replace("</head>", head + "</head>", 1).replace("</body>", tail + "</body>", 1)

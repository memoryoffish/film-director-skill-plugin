#!/usr/bin/env python3
"""在真 ComfyUI 前端里打开工作流，像人一样看一遍：线接对没有、打开时看得全不全、图和视频出来没有，再跑一遍（replay），
看这一镜该留下的东西（关键帧、这一镜的视频）是不是都留在 output 里了、有没有多留别的。

    PY=<装了 playwright 的 python>
    $PY check_in_comfy.py <工作流…> [--url http://127.0.0.1:8188] [--run] [--shots <截图目录>] [--no-sidebar]

<工作流> 是 ComfyUI 用户目录里的路径（user/default/workflows/ 下面，比如 "filmkit/zz_demo/S3 她把杯子放到桌上.json"），
或者本机的 json 文件。先点开左边栏的 Workflows（人就是从这里点开一镜的，侧栏会挡住画布左边一块），再逐个打开。
每个打印一行 JSON：
    missing      前端不认识的节点类型（节点包没装上、或类型名写错）
    links        文件里的线 / 打开以后还在的线
    bad_links    打开以后接错口的线：[线号, 文件里写的口, 实际接到的口]
    widgets      我们的节点读回来的参数（按名字），对照文件里写的
    scale        打开时的缩放。小于 0.6 前端不画字（small）
    cut          打开时有一部分在看得见的区域外面的节点（被侧栏、顶栏挡住或出了窗口）
    covered      被小地图盖住的节点
    hidden_links 从别的节点背后穿过去的线：[线号, 被它穿过的节点]（线按直线算，拐点算进去）
    empty_slots  节点上还露着的空口
    no_media     图没出来、视频没在放的节点；off_shot 视频放的不是这一镜的 t0–t1
    run          --run 时：success / error，用了几秒，报错的节点；
                 kept = 这一镜该留在 output 里的文件数（每张关键帧 + 这一镜的 mp4），kept_missing = 其中没留下的；
                 reported = 这一次报给前端的产出数（资产系统开着时是 0：节点只写文件，由 ComfyUI 自己扫进库），junk = 报出来但不该有的
                 （别的类型、别的名字）；resized = 跑完以后变了大小或多了控件的节点（前端自带的预览又加上来了）；
                 资产系统开着时还有 no_card = 该留的文件里 Assets 面板没有卡片的，dup_card = 有两张以上卡片的
--run 而且资产系统开着时，最后再打印一行 {"assets": …}：跑之前、跑之后 Generated 里的卡片数，junk = 新多出来、但不是这几镜该留的卡片。
退出码：都对是 0，有问题是 1。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import sys
import time
import urllib.parse

from playwright.async_api import async_playwright

CHECK = """async (wf) => {
  const app = window.app, LG = window.LiteGraph, sleep = ms => new Promise(r => setTimeout(r, ms));
  await app.loadGraphData(wf, true, true, wf.extra && wf.extra.filmkit ? `${wf.extra.filmkit.film}_${wf.extra.filmkit.shot}` : 'check');
  const g = app.graph, byId = new Map(g.nodes.map(n => [String(n.id), n]));
  const missing = [...new Set(g.nodes.filter(n => !LG.registered_node_types[n.type]).map(n => n.type))];
  const live = [...(g.links instanceof Map ? g.links.values() : Object.values(g.links || {}))].filter(Boolean);
  const bad = [];
  for (const L of wf.links) {
    // 按线号对：同一张图喂给同一个节点的两个口时，按来源找会找到第一个口
    const want = wf.nodes.find(n => n.id === L[3]).inputs[L[4]].name;
    const l = live.find(l => String(l.id) === String(L[0]));
    const tgt = l && byId.get(String(l.target_id));
    const got = l && String(l.origin_id) === String(L[1]) && tgt && tgt.inputs[l.target_slot] &&
                String(tgt.inputs[l.target_slot].link) === String(L[0]) ? tgt.inputs[l.target_slot].name : null;
    if (got !== want) bad.push([L[0], want, got]);
  }
  const fk = g.nodes.filter(n => String(n.type).startsWith('FilmKit'));
  const val = (n, k) => n.widgets?.find(w => w.name === k)?.value;
  const widgets = {};
  for (const n of fk)
    widgets[`${n.id} ${n.type}`] = Object.fromEntries((n.widgets || []).filter(w => !String(w.name).startsWith('filmkit_'))
      .map(w => [w.name, typeof w.value === 'string' ? w.value.slice(0, 40) : w.value]));

  // 图、视频：等到都出来（最多 12 秒）
  const el = n => n.filmkitMedia?.element;
  const ready = n => { const e = el(n); return !!e && (e.tagName === 'IMG' ? e.complete && e.naturalWidth > 0 : e.readyState >= 2 && !e.paused); };
  for (let t = Date.now(); Date.now() - t < 12000 && !fk.every(ready);) await sleep(200);
  await sleep(400);                                      // 节点包在载入后两帧才把整镜摆进窗口
  const no_media = fk.filter(n => !ready(n)).map(n => n.title);
  const off_shot = fk.filter(n => el(n)?.tagName === 'VIDEO' && ready(n) &&
    !(el(n).currentTime >= +val(n, 't0') - 0.3 && el(n).currentTime <= +val(n, 't1') + 0.1)).map(n => [n.title, +el(n).currentTime.toFixed(2)]);
  const empty_slots = fk.flatMap(n => (n.inputs || []).filter(i => !i.widget && i.link == null).map(i => `${n.title}: ${i.label || i.name}`));

  // 打开时看得全不全。屏幕坐标 = (图上坐标 + offset) × scale
  const ds = app.canvas.ds, cv = app.canvas.canvas.getBoundingClientRect();
  const box = sel => { const r = document.querySelector(sel)?.getBoundingClientRect(); return r && r.width > 0 && r.height > 0 ? r : null; };
  let left = cv.left, top = cv.top;
  for (const s of ['.side-tool-bar-container', '.side-bar-panel']) { const r = box(s); if (r && r.left < cv.width / 2) left = Math.max(left, r.right); }
  for (const s of ['.workflow-tabs-container', '.actionbar']) { const r = box(s); if (r && r.top < 120) top = Math.max(top, r.bottom); }
  const mm = box('.minimap-main-container');
  const screen = n => [(n.pos[0] + ds.offset[0]) * ds.scale, (n.pos[1] - 30 + ds.offset[1]) * ds.scale,
                       (n.pos[0] + n.size[0] + ds.offset[0]) * ds.scale, (n.pos[1] + n.size[1] + ds.offset[1]) * ds.scale];
  const cut = g.nodes.filter(n => { const [x0, y0, x1, y1] = screen(n); return x0 < left - 1 || y0 < top - 1 || x1 > cv.right + 1 || y1 > cv.bottom + 1; }).map(n => n.title);
  const covered = mm ? g.nodes.filter(n => { const [x0, y0, x1, y1] = screen(n); return x0 < mm.right && x1 > mm.left && y0 < mm.bottom && y1 > mm.top; }).map(n => n.title) : [];

  // 线有没有从别的节点背后穿过去：出口 → 往右 15 → 各个拐点 → 入口左边 15 → 入口，一段一段每 3 像素取一个点
  const rects = g.nodes.map(n => [n, n.pos[0] + 3, n.pos[1] - 30 + 3, n.pos[0] + n.size[0] - 3, n.pos[1] + n.size[1] - 3]);
  const hidden_links = [];
  for (const l of live) {
    const o = byId.get(String(l.origin_id)), t = byId.get(String(l.target_id));
    if (!o || !t) continue;
    const a = o.getOutputPos(l.origin_slot), b = t.getInputPos(l.target_slot), mid = [];
    for (let r = l.parentId != null ? g.reroutes.get(l.parentId) : null; r; r = r.parentId != null ? g.reroutes.get(r.parentId) : null) mid.unshift([r.pos[0], r.pos[1]]);
    const pts = [[a[0] + 15, a[1]], ...mid, [b[0] - 15, b[1]]];
    const hit = new Set();
    for (let i = 0; i + 1 < pts.length; i++) {
      const [x0, y0] = pts[i], [x1, y1] = pts[i + 1], steps = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 3));
      for (let s = 0; s <= steps; s++) {
        const x = x0 + (x1 - x0) * s / steps, y = y0 + (y1 - y0) * s / steps;
        for (const [n, rx0, ry0, rx1, ry1] of rects) if (x > rx0 && x < rx1 && y > ry0 && y < ry1) hit.add(n.title);
      }
    }
    if (hit.size) hidden_links.push([l.id, [...hit]]);
  }
  return {nodes: g.nodes.length, missing, links: [wf.links.length, live.length], bad_links: bad, widgets,
          scale: +ds.scale.toFixed(3), cut, covered, hidden_links, empty_slots, no_media, off_shot};
}"""

RUN = """async () => {
  const app = window.app, api = app.api;
  window.__fkBefore = app.graph.nodes.map(n => [n.id, Math.round(n.size[0]), Math.round(n.size[1]), (n.widgets || []).length]);
  const p = await app.graphToPrompt();
  const r = await api.queuePrompt(0, p);
  return r && (r.prompt_id || r.promptId) || null;
}"""

# 跑完以后：该留的文件在不在 output 里（名字的规矩见节点包的 kept()、shots2comfy.py 的 kept_names()），节点有没有变样
AFTER = """async () => {
  const app = window.app, sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(600);                                      // 前端收到产出后过一两帧才会往节点上加预览
  const val = (n, k) => n.widgets?.find(w => w.name === k)?.value;
  const before = new Map((window.__fkBefore || []).map(b => [b[0], b]));
  const resized = app.graph.nodes.filter(n => { const b = before.get(n.id);
    return !b || b[1] !== Math.round(n.size[0]) || b[2] !== Math.round(n.size[1]) || b[3] !== (n.widgets || []).length; }).map(n => n.title);
  const kept = [];
  for (const n of app.graph.nodes) {
    const film = val(n, 'film');
    if (n.type === 'FilmKitKeyframe')
      kept.push(`filmkit__${film}__${(n.properties?.filmkit?.file || `keys/${val(n, 'name')}.png`).split('/').pop()}`);
    else if (/^FilmKit(T2V|I2V|FLF2V|R2V)$/.test(n.type))
      kept.push(`filmkit__${film}__${String(val(n, 'shot') || val(n, 'name')).replace(/[^A-Za-z0-9_.\\-]+/g, '_')}.mp4`);
  }
  const kept_missing = [];
  for (const f of kept) {
    const r = await fetch(app.api.apiURL('/view?' + new URLSearchParams({filename: f, type: 'output'})), {method: 'HEAD'});
    if (!r.ok) kept_missing.push(f);
  }
  return {kept, kept_missing, resized};
}"""

# 资产系统开着时人看的是 Assets 面板：下面两段取的和面板 Generated 取的是同一份（不算 missing 的）。
# CARDS：全部卡片 [[资产号, 文件名], …]，资产系统没开回 null。LISTED：这几个文件各有几张卡片。
CARDS = """async () => {
  const get = u => fetch(window.app.api.apiURL(u)).then(r => r.json());
  if (!(await get('/features')).assets) return null;
  const cards = [];
  for (let after = '', k = 0; k < 40; k++) {
    const q = new URLSearchParams({tags_any: 'output,temp', tags_none: 'missing', sort: 'created_at', limit: '500'});
    if (after) q.set('after', after);
    const d = await get('/assets?' + q);
    cards.push(...d.assets.map(a => [a.id, a.name]));
    if (!d.has_more) break;
    after = d.next_cursor;
  }
  return cards;
}"""
LISTED = """async (files) => {
  const n = {};
  for (const f of files) {
    const q = new URLSearchParams({tags_any: 'output', tags_none: 'missing', name_contains: f, limit: '50'});
    const d = await fetch(window.app.api.apiURL('/assets?' + q)).then(r => r.json());
    n[f] = d.assets.filter(a => a.name === f).length;
  }
  return n;
}"""

READY = "() => window.app && window.app.graph && window.LiteGraph"
PROBLEMS = ("missing", "bad_links", "cut", "covered", "hidden_links", "empty_slots", "no_media", "off_shot", "page_errors")


async def open_page(page, url: str, sidebar: bool) -> None:
    # 不等 networkidle：前端会接着打开上次开着的那一镜，它的视频一直在取数据，网络闲不下来
    await page.goto(url + "/", wait_until="load")
    await page.wait_for_function(READY, timeout=60000)
    await page.wait_for_timeout(1500)
    if sidebar and not await page.locator(".side-bar-panel").count():
        # 用命令开，不按字找按钮：窗口矮的时候左边栏只剩图标，没有「Workflows」这几个字
        await page.evaluate("() => window.app.extensionManager.command.execute('Workspace.ToggleSidebarTab.workflows')")
        await page.wait_for_timeout(800)


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workflows", nargs="+")
    ap.add_argument("--url", default="http://127.0.0.1:8188")
    ap.add_argument("--run", action="store_true", help="排进队列真跑一遍（replay 模式不调任何接口）")
    ap.add_argument("--shots", default="", help="截图放哪个目录（截的就是打开时的样子）")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--no-sidebar", action="store_true", help="不点开左边栏（默认点开 Workflows，和人打开一镜时一样）")
    a = ap.parse_args()
    shots = pathlib.Path(a.shots).expanduser() if a.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    ok = True
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": a.width, "height": a.height})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await open_page(page, a.url, not a.no_sidebar)
        cards0 = await page.evaluate(CARDS) if a.run else None      # None = 没带 --run，或资产系统没开
        expected: set[str] = set()
        for k, w in enumerate(a.workflows):
            if k and k % 20 == 0:                        # 每打开一个就多一个标签页：隔 20 个刷新一次，内存不涨
                await open_page(page, a.url, not a.no_sidebar)
            local = pathlib.Path(w).expanduser()
            if local.is_file():
                wf = json.loads(local.read_text(encoding="utf-8"))
            else:
                url = f"{a.url}/api/userdata/{urllib.parse.quote('workflows/' + w, safe='')}"
                wf = json.loads(await page.evaluate("u => fetch(u).then(r => r.text())", url))
            errors.clear()
            r = await page.evaluate(CHECK, wf)
            r["file"] = w
            if shots:
                fk = wf.get("extra", {}).get("filmkit", {})
                r["shot"] = str(shots / f"{fk.get('film', 'wf')}_{fk.get('shot', local.stem)}.png")
                await page.screenshot(path=r["shot"])
            if a.run:
                t = time.time()
                pid = await page.evaluate(RUN)
                status, bad_nodes, left = "no prompt id", [], []
                for _ in range(600):
                    h = await page.evaluate("id => fetch(`/history/${id}`).then(r => r.json())", pid) if pid else {}
                    if pid in h:
                        st = h[pid].get("status", {})
                        status = st.get("status_str", "?")
                        left = [f"{i.get('type')}/{i.get('subfolder') or ''}/{i.get('filename')}" for o in h[pid].get("outputs", {}).values()
                                for v in o.values() if isinstance(v, list) for i in v if isinstance(i, dict)]
                        for m in st.get("messages", []):
                            if m[0] == "execution_error":
                                bad_nodes.append([m[1].get("node_id"), m[1].get("node_type"), m[1].get("exception_message", "")[:200]])
                        break
                    await page.wait_for_timeout(300)
                after = await page.evaluate(AFTER)
                r["run"] = {"status": status, "seconds": round(time.time() - t, 1), "errors": bad_nodes,
                            "kept": len(after["kept"]), "kept_missing": after["kept_missing"], "reported": len(left),
                            "junk": [x for x in left if x not in {f"output//{k}" for k in after["kept"]}],
                            "resized": after["resized"]}
                if cards0 is not None:
                    expected.update(after["kept"])
                    for _ in range(30):                  # 新写的文件要等 ComfyUI 自己那遍扫描才有卡片，最晚十来秒
                        n = await page.evaluate(LISTED, after["kept"])
                        if all(n.values()):
                            break
                        await page.wait_for_timeout(500)
                    r["run"]["no_card"] = [f for f, c in n.items() if not c]
                    r["run"]["dup_card"] = [f for f, c in n.items() if c > 1]
            r["page_errors"] = errors[:3]
            r["small"] = r["scale"] < 0.6
            bad = any(r[k] for k in PROBLEMS) or r["small"] or r["links"][0] != r["links"][1] or \
                (a.run and (r["run"]["status"] != "success" or r["run"]["kept_missing"] or r["run"]["junk"] or r["run"]["resized"] or
                            r["run"].get("no_card") or r["run"].get("dup_card")))
            ok = ok and not bad
            print(json.dumps(r, ensure_ascii=False), flush=True)
        if cards0 is not None:
            await page.wait_for_timeout(12000)           # 等最后一镜之后那遍扫描：节点写了没报的文件这时才进库
            cards, old = await page.evaluate(CARDS), {i for i, _ in cards0}
            junk = sorted({n for i, n in cards if i not in old and n not in expected})
            ok = ok and not junk
            print(json.dumps({"assets": {"cards_before": len(cards0), "cards_after": len(cards), "junk": junk}}, ensure_ascii=False), flush=True)
        await b.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

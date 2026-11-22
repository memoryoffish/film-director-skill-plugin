// FilmKit 节点的显示：只露这一步要看的东西，打开就看得全、看得清。
//
// 1. 标成 advanced 的参数（film、name、file、shot、执行方式、size、seed、resolution、t0、t1……，节点找文件用的）藏起来，
//    连带 seed 后面前端自动加的「生成后怎么换种子」控件。设置里打开 Comfy.Node.AlwaysShowAdvancedWidgets 就照常显示。
//    （前端 1.59 的经典画布不管 advanced 标记，所以自己藏。）
// 2. 口：能自动增减的口显示成中文（images.image0 → 图1，refs.ref0 → 参考图1）；打开存好的工作流时，
//    没接线的可选口（自动增减留的那个空口、没用上的参考视频）不显示，节点上只剩这一镜真喂进去的。
// 3. 打开就有图、视频自己播，不用先点 Run：FilmKit 图、关键帧显示运行目录里那张图（/filmkit/file）；
//    视频节点直接放成片里这一镜的 t0–t1（/filmkit/film，静音循环，控件上可以开声音、暂停）。
//    跑过以后节点不变样：关键帧和这一镜的视频会留在 output、出现在 Assets 面板里，但节点上已经有画面了，
//    前端自带的预览不再往节点上加一份（ownPicture）。
// 4. 提示词框字号 12、固定高度，够读开头几行，往下滚看全。
// 5. 打开 shots2comfy 出的工作流（extra.filmkit）时，把整镜摆进看得见的那块区域：避开左边栏、顶上的工具条和小地图，
//    最大放到 100%。前端自己的「适应窗口」按整块画布算，侧栏开着时左边一列会压在侧栏底下，而且总留四分之一的边。
//    只在头一回打开时摆；这些工作流的线画成直的（只改画布，不动用户的设置）。
// 6. 人在回放的节点上改了提示词、模型、时长：提示一句「这是回放，改了也不会重新生成」（每个节点一次）。
//    不提示的话，人改完点 Run，出来的还是原来那条，会以为改动生效了。
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const LiteGraph = window.LiteGraph;

const PREFIX = { images: "图", refs: "参考图" };
const OPTIONAL = /^(images|refs)\.|^ref_video$/;
const VIDEO = new Set(["FilmKitT2V", "FilmKitI2V", "FilmKitFLF2V", "FilmKitR2V"]);
const PROMPT_HEIGHT = { FilmKitKeyframe: 112 };   // 视频节点的提示词框高一点
const TITLE = 30;                                  // 节点标题栏的高度（画在节点位置的上面）
const MARGIN = 6;                                  // 图、视频四周留的边；和 shots2comfy.py 的 MEDIA_MARGIN 一样
const PORTRAIT_CAP = 0.8;                          // 竖图最高到宽的 0.8 倍，再高就两边留空

function isFilmKit(node) {
  return String(node.comfyClass || node.type || "").startsWith("FilmKit");
}

function showAdvanced() {
  try {
    return !!app.extensionManager.setting.get("Comfy.Node.AlwaysShowAdvancedWidgets");
  } catch {
    return false;
  }
}

function value(node, name) {
  return node.widgets?.find((w) => w.name === name)?.value;
}

function url(path, args) {
  return api.apiURL(`${path}?` + new URLSearchParams(args).toString());
}

function tidy(node) {
  if (!isFilmKit(node)) return;
  const hide = !showAdvanced();
  for (const w of node.widgets || []) {
    if (w.advanced || w.options?.advanced) {
      w.hidden = hide;
      for (const l of w.linkedWidgets || []) l.hidden = hide;
    }
    if (w.name === "prompt") {
      const h = PROMPT_HEIGHT[node.comfyClass || node.type] || 132;
      w.options.getMinHeight = w.options.getMaxHeight = () => h;
      const el = w.element || w.inputEl;
      if (el) Object.assign(el.style, { fontSize: "12px", lineHeight: "1.4" });
    }
  }
  for (const inp of node.inputs || []) {
    const m = /^(images|refs)\.[a-z]+(\d+)$/.exec(inp.name || "");
    if (m) inp.label = PREFIX[m[1]] + (Number(m[2]) + 1);
  }
  node.setDirtyCanvas?.(true, true);
}

// 存好的工作流里，没接线的可选口不显示（新拖出来的节点不动，不然没法接线）
function dropEmptySlots(node) {
  if (!isFilmKit(node) || showAdvanced()) return;
  for (let i = (node.inputs || []).length - 1; i >= 0; i--) {
    const inp = node.inputs[i];
    if (inp.link == null && !inp.widget && OPTIONAL.test(inp.name || "")) node.removeInput(i);
  }
}

// 图和视频都放在自己的控件里，高度正好是画面的高度：前端自带的图片预览最少占 220 高，小图节点会被撑高、留白边。
function media(node, name, el, aspect, cap = Infinity) {
  const height = () => {
    const w = node.size[0] - 2 * MARGIN;
    return Math.round(Math.min(w * aspect(), w * cap)) + 2 * MARGIN;
  };
  Object.assign(el.style, { width: "100%", height: "100%", objectFit: "contain", borderRadius: "4px" });
  return node.addDOMWidget(name, name, el, {
    serialize: false, hideOnZoom: false, margin: MARGIN, getMinHeight: height, getMaxHeight: height,
  });
}

// 节点上的画面是我们自己放的：跑完以后前端自带的预览不用再加（加了节点会被撑高，同一个画面出现两遍）。
// 经典画布的预览挂在 onDrawBackground 上；Vue 节点看 hideOutputImages（自带的 Painter、ImageCrop 也是这么关的）。
function ownPicture(node) {
  node.hideOutputImages = true;
  node.onDrawBackground = function () {};
}

function showImage(node) {
  const type = node.comfyClass || node.type;
  const film = value(node, "film");
  const rel = type === "FilmKitImage" ? value(node, "file") : type === "FilmKitKeyframe" && value(node, "name") ? node.properties?.filmkit?.file || `keys/${value(node, "name")}.png` : null;
  if (!film || !rel || node.filmkitMedia) return;
  const img = document.createElement("img");
  img.draggable = false;
  img.style.pointerEvents = "none";                 // 点在图上照样能拖节点、滚轮缩放画布
  img.addEventListener("load", () => node.setDirtyCanvas?.(true, true));
  img.src = url("/filmkit/file", { film, rel });
  node.filmkitMedia = media(node, "filmkit_image", img, () => (img.naturalWidth ? img.naturalHeight / img.naturalWidth : 9 / 16), PORTRAIT_CAP);
  ownPicture(node);
}

// 视频节点：直接放成片里这一镜的 t0–t1，静音、循环
function playShot(node) {
  const film = value(node, "film"), t0 = +value(node, "t0"), t1 = +value(node, "t1");
  if (!VIDEO.has(node.comfyClass || node.type) || node.filmkitMedia || !film || !(t1 > t0)) return;
  const v = document.createElement("video");
  Object.assign(v, { muted: true, autoplay: true, playsInline: true, controls: true, preload: "auto" });
  v.style.background = "#000";
  v.addEventListener("loadedmetadata", () => {
    v.currentTime = t0;
    node.setDirtyCanvas?.(true, true);
  });
  const loop = () => {
    if (v.currentTime >= t1 - 0.04 || v.currentTime < t0 - 0.25) v.currentTime = t0;
  };
  if (v.requestVideoFrameCallback) {
    const tick = () => {
      loop();
      if (node.filmkitMedia) v.requestVideoFrameCallback(tick);
    };
    v.requestVideoFrameCallback(tick);
  } else v.addEventListener("timeupdate", loop);
  v.addEventListener("seeked", () => v.paused && v.currentTime <= t0 + 0.05 && v.play().catch(() => {}));
  v.src = url("/filmkit/film", { film });
  node.filmkitMedia = media(node, "filmkit_video", v, () => (v.videoWidth ? v.videoHeight / v.videoWidth : 9 / 16));
  ownPicture(node);
  const removed = node.onRemoved;
  node.onRemoved = function (...args) {
    node.filmkitMedia = null;
    v.pause();
    v.removeAttribute("src");
    v.load();
    return removed?.apply(this, args);
  };
}

// 回放放的是拍片时已经出好的那一份。人改了看得见的参数，告诉他一声（一个节点只说一次）。
function tellOnEdit(node) {
  if (value(node, "mode") !== "replay") return;
  for (const w of node.widgets || []) {
    if (!["prompt", "model", "duration"].includes(w.name)) continue;
    const loaded = w.value;
    const tell = () => {
      if (node.filmkitTold || w.value === loaded || value(node, "mode") !== "replay") return;
      node.filmkitTold = true;
      app.extensionManager.toast.add({
        severity: "info", life: 9000, summary: "这是回放",
        detail: "这个节点放的是拍片时已经出好的那一份，改了这里再点 Run 也不会重新生成。想按新的重出：存下这份工作流，把改动告诉 agent。",
      });
    };
    const orig = w.callback;
    w.callback = function (...args) {
      tell();
      return orig?.apply(this, args);
    };
    (w.element || w.inputEl)?.addEventListener("input", tell);   // 多行的提示词框打字时不走 callback
  }
}

// 画布上没被界面挡住的那一块（相对画布左上角，CSS 像素），和里面要避开的小块（小地图）
function freeArea() {
  const cv = app.canvas.canvas.getBoundingClientRect();
  const rect = (sel) => {
    const e = document.querySelector(sel), r = e?.getBoundingClientRect();
    return r && r.width > 0 && r.height > 0 ? r : null;
  };
  let left = cv.left, right = cv.right, top = cv.top;
  for (const sel of [".side-tool-bar-container", ".side-bar-panel"]) {
    const r = rect(sel);
    if (!r) continue;
    if (r.left < (cv.left + cv.right) / 2) left = Math.max(left, r.right);
    else right = Math.min(right, r.left);
  }
  for (const sel of [".workflow-tabs-container", ".actionbar"]) {
    const r = rect(sel);
    if (r && r.top < cv.top + 120) top = Math.max(top, r.bottom);
  }
  const pad = 12;
  const area = { x: left + pad - cv.left, y: top + pad - cv.top, w: right - left - 2 * pad, h: cv.bottom - top - 2 * pad };
  const mm = rect(".minimap-main-container");
  return { area, blocks: mm ? [{ x: mm.left - cv.left - 8, y: mm.top - cv.top - 8, w: mm.width + 16, h: mm.height + 16 }] : [] };
}

function fitShot() {
  const graph = app.graph, ds = app.canvas.ds;
  const fk = graph?.extra?.filmkit;
  // 这些工作流的线画成直的、拐点画小一点、线中间不画圆点：拐点之间是直线，shots2comfy 排好的走线才不会鼓出去压到节点。
  // 只改画布，不动用户的设置；切到别的工作流就照用户自己的设置画。
  const setting = (id, fallback) => app.extensionManager.setting.get(id) ?? fallback;
  app.canvas.links_render_mode = fk ? LiteGraph.LINEAR_LINK : setting("Comfy.LinkRenderMode", LiteGraph.SPLINE_LINK);
  app.canvas.linkMarkerShape = fk ? 0 : setting("Comfy.Graph.LinkMarkers", 1);
  if (LiteGraph.Reroute) LiteGraph.Reroute.radius = fk ? 5 : 10;
  app.canvas.setDirty(true, true);
  if (!fk || !graph.nodes?.length) return;
  // 只在头一回打开时摆：存下来的视图还是 shots2comfy 写的那个。自己挪过、缩放过再切回来，就留着自己的。
  const saved = graph.extra.ds, first = fk.view;
  if (first && saved && (Math.abs(saved.scale - first.scale) > 1e-3 || Math.abs(saved.offset[0] - first.offset[0]) > 1 || Math.abs(saved.offset[1] - first.offset[1]) > 1)) return;
  const boxes = graph.nodes.map((n) => [n.pos[0], n.pos[1] - TITLE, n.size[0], n.size[1] + TITLE]);
  const groups = (graph.groups || []).map((g) => [...(g.bounding || g._bounding)]);
  const all = [...boxes, ...groups];
  const x0 = Math.min(...all.map((b) => b[0])), y0 = Math.min(...all.map((b) => b[1]));
  const x1 = Math.max(...all.map((b) => b[0] + b[2])), y1 = Math.max(...all.map((b) => b[1] + b[3]));
  const { area, blocks } = freeArea();
  if (area.w < 200 || area.h < 200) return;
  let scale = Math.min(1, area.w / (x1 - x0), area.h / (y1 - y0));
  let off;
  for (let k = 0; k < 12; k++) {
    // 屏幕 = (图上坐标 + offset) × scale：横着居中，竖着贴顶
    off = [(area.x + (area.w - (x1 - x0) * scale) / 2) / scale - x0, area.y / scale - y0];
    const hit = boxes.some(([x, y, w, h]) => blocks.some((b) => {
      const sx = (x + off[0]) * scale, sy = (y + off[1]) * scale;
      return sx < b.x + b.w && sx + w * scale > b.x && sy < b.y + b.h && sy + h * scale > b.y;
    }));
    if (!hit) break;
    scale *= 0.95;
  }
  ds.scale = scale;
  ds.offset[0] = off[0];
  ds.offset[1] = off[1];
  app.canvas.setDirty(true, true);
}

app.registerExtension({
  name: "filmkit.tidy",
  nodeCreated(node) {
    if (!isFilmKit(node)) return;
    const orig = node.onConnectionsChange;
    node.onConnectionsChange = function (...args) {
      const r = orig?.apply(this, args);
      setTimeout(() => tidy(this), 0);
      return r;
    };
    tidy(node);
  },
  loadedGraphNode(node) {
    if (!isFilmKit(node)) return;
    dropEmptySlots(node);
    tidy(node);
    showImage(node);
    playShot(node);
    tellOnEdit(node);
  },
  afterConfigureGraph() {
    // 前端载入后还会按存下来的视图摆一次，等它摆完再摆
    requestAnimationFrame(() => requestAnimationFrame(fitShot));
  },
});

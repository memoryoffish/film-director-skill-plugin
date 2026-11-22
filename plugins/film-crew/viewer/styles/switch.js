// 风格切换。CFG.names 里第一套是默认；只有一套时不出按钮。CFG.hosts：按钮放进哪几处（放在它里面的最后），不给就放在 <main> 最前面。
// 每套风格的脚本登记在 FilmStyles[名字][部分] = {on(), off()}。
(function (CFG) {
  'use strict';
  const root = document.documentElement, S = window.FilmStyles = window.FilmStyles || {};
  const each = (n, f) => Object.values(S[n] || {}).forEach(p => { try { p[f] && p[f](); } catch (e) { console.error(e); } });
  let cur = null;
  function set(n, keep) {
    if (!CFG.names.includes(n)) n = CFG.names[0];
    if (n === cur) return;
    if (cur) each(cur, 'off');
    cur = n;
    if (n === 'plain') delete root.dataset.style; else root.dataset.style = n;
    if (keep) try { localStorage.setItem('film-style', n); } catch (e) {}
    each(n, 'on');
    document.querySelectorAll('.fs-switch button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.s === n)));
    dispatchEvent(new Event('resize'));          // 页面里按尺寸排的东西照新样子再量一遍
  }
  function nav() {
    const e = document.createElement('nav');
    e.className = 'fs-switch'; e.setAttribute('aria-label', '风格');
    CFG.names.forEach(n => {
      const b = document.createElement('button');
      b.type = 'button'; b.dataset.s = n; b.textContent = CFG.labels[n] || n; b.onclick = () => set(n, true);
      e.append(b);
    });
    return e;
  }
  if (CFG.names.length > 1) {
    const hosts = (CFG.hosts || []).map(q => document.querySelector(q)).filter(Boolean);
    if (hosts.length) hosts.forEach(h => { const e = nav(); e.classList.add('fs-in'); h.append(e); });
    else (document.querySelector('main') || document.body).prepend(nav());
  }
  set(root.dataset.style || 'plain', false);
})(/*CFG*/{});

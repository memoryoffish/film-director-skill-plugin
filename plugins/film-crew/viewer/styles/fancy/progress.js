// Fancy 进度页：顶上一排大数；每一次生成一格，排成一面片墙，同一单元的几次用一道光连起来。
(function () {
  'use strict';
  const S = window.FilmStyles = window.FilmStyles || {};
  const $$ = (q, e) => [...(e || document).querySelectorAll(q)];
  const el = (tag, cls, ...kids) => { const e = document.createElement(tag); if (cls) e.className = cls; e.append(...kids.filter(k => k != null)); return e; };
  const ORDER = ['合格', '生成中', '检查中', '要重抽', '待检查', '失败'];
  let undo = [];

  // 顶上的大数：各种状态的单元有几个、开工多久、花了多少
  function summary(main) {
    const F = JSON.parse((document.getElementById('style-facts') || {}).textContent || '{}');
    const chips = $$(':scope > .unit > h3 .chip', main), by = {};
    chips.forEach(c => { const k = c.textContent.trim(); (by[k] = by[k] || { n: 0, cls: c.className.replace('chip', '').trim() }).n++; });
    const tile = (num, label, cls, tail) => el('div', 'fx-tile ' + (cls || ''), el('b', '', el('span', 'fx-num', String(num)), tail ? el('i', '', tail) : null), el('span', 'fx-lab', label));
    const box = el('div', 'fx-sum', tile((by['合格'] || { n: 0 }).n, '合格', 'ok', ` / ${chips.length}`));
    ORDER.slice(1).forEach(k => { if (by[k]) box.append(tile(by[k].n, k, by[k].cls + (k === '生成中' ? ' fx-live' : ''))); });
    if (F.elapsed != null) box.append(tile(F.elapsed, '开工', 'fx-t', ' 分钟'));
    if (F.spent != null) box.append(tile('¥' + F.spent, '花费（' + (F.price === 'discount' ? '折扣价' : '原价') + '）', 'fx-t', F.estimate ? ` / 估 ¥${F.estimate}` : ''));
    box.append(el('div', 'fx-upd', el('span', '', '更新 ' + (F.updated || '')), el('span', '', '放视频时不自动刷新')));
    const meta = main.querySelector(':scope > .meta');
    (meta || main.firstChild).after(box);
    if (meta) meta.hidden = true;
    undo.push(() => { box.remove(); if (meta) meta.hidden = false; });
    // 数字从 0 数上来：一个标签页里只在第一次打开时做，自动刷新时不再跳
    let seen = true;
    try { seen = sessionStorage.getItem('fancy-seen'); sessionStorage.setItem('fancy-seen', '1'); } catch (e) {}
    if (seen || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    main.classList.add('fx-enter');
    undo.push(() => main.classList.remove('fx-enter'));
    $$('.fx-num', box).forEach(n => {
      const m = /^(\D*)(\d+)$/.exec(n.textContent); if (!m) return;
      const to = +m[2], t0 = performance.now();
      const step = t => { const k = Math.min(1, (t - t0) / 700); n.textContent = m[1] + Math.round(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); };
      requestAnimationFrame(step);
    });
  }

  // 片墙：单元的名字、状态、拍什么挪到它第一次生成那一格的上面；后面几次的上面是一道连过来的光
  function sheet(main) {
    const units = $$(':scope > .unit', main);
    units.forEach(u => {
      const figs = $$(':scope > .takes > figure', u), head = [...u.children].filter(c => !c.classList.contains('takes'));
      if (!figs.length) return;
      const uh = el('div', 'fx-uh', ...head);
      figs[0].prepend(uh);
      const h3 = head.find(c => c.tagName === 'H3'), name = h3 ? [...h3.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('') : '';
      const more = figs.slice(1).map((f, k) => { const m = el('div', 'fx-uh fx-more', el('span', '', `${name} 第 ${k + 2} 次`)); f.prepend(m); return m; });
      undo.push(() => { u.prepend(...head); uh.remove(); more.forEach(m => m.remove()); });
      const about = uh.querySelector('.about');
      if (about && !about.title) { about.title = about.textContent; undo.push(() => about.removeAttribute('title')); }
      figs.forEach(f => {
        // 说明第一行「名字 · 状态 · 用了几分钟 · 计费几秒」：状态挪到画面左上角，其余分成几小段
        const b = f.querySelector(':scope > figcaption > b'), tx = b && b.nextSibling;
        if (tx && tx.nodeType === 3) {
          const parts = tx.textContent.split(' · ').map(s => s.trim()).filter(Boolean);
          if (parts.length) {
            const spans = parts.slice(1).map(p => el('span', 'fx-m', p));
            f.dataset.fxState = parts[0];
            tx.replaceWith(...spans);
            undo.push(() => { b.after(tx); spans.forEach(s => s.remove()); delete f.dataset.fxState; });
          }
        }
        $$(':scope > figcaption li', f).forEach(li => { if (!li.title) { li.title = li.textContent; undo.push(() => li.removeAttribute('title')); } });
      });
    });
    main.classList.add('fx-sheet');
    undo.push(() => main.classList.remove('fx-sheet'));
    // 点顶上那一条里的单元，跳到它那几格
    const strip = main.querySelector(':scope > .strip');
    if (!strip) return;
    const jump = e => {
      const i = [...strip.children].indexOf(e.target.closest('span')), f = i >= 0 && units[i] && units[i].querySelector('figure');
      if (!f) return;
      f.scrollIntoView({ block: 'center', behavior: 'smooth' });
      $$('figure', units[i]).forEach(x => { x.classList.remove('fx-hit'); void x.offsetWidth; x.classList.add('fx-hit'); });
    };
    strip.addEventListener('click', jump);
    undo.push(() => { strip.removeEventListener('click', jump); $$('.fx-hit', main).forEach(x => x.classList.remove('fx-hit')); });
  }

  // 哪一格在放：在放的那一格留着原生的播放条
  function playing(main) {
    const mark = e => { const f = e.target.closest && e.target.closest('.takes > figure'); if (f) f.classList.toggle('fx-playing', e.type === 'play'); };
    ['play', 'pause', 'ended'].forEach(t => main.addEventListener(t, mark, true));
    undo.push(() => { ['play', 'pause', 'ended'].forEach(t => main.removeEventListener(t, mark, true)); $$('.fx-playing', main).forEach(f => f.classList.remove('fx-playing')); });
  }

  // 鼠标到哪一块，那一块亮一点
  function spotlight(main) {
    const move = e => {
      const c = e.target.closest && e.target.closest('.fx-tile');
      if (!c) return;
      const r = c.getBoundingClientRect();
      c.style.setProperty('--mx', `${e.clientX - r.left}px`); c.style.setProperty('--my', `${e.clientY - r.top}px`);
    };
    main.addEventListener('pointermove', move);
    undo.push(() => main.removeEventListener('pointermove', move));
  }

  (S.fancy = S.fancy || {}).progress = {
    on() { const main = document.querySelector('main'); if (!main || undo.length) return; summary(main); sheet(main); playing(main); spotlight(main); },
    off() { undo.reverse().forEach(f => f()); undo = []; },
  };
})();

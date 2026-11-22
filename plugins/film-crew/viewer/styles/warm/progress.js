// 暖心进度页：白模小人说一句现在拍到哪了；每一次生成是一张贴着胶带的照片，同一单元的几次用手画的箭头连着。
(function () {
  'use strict';
  const S = window.FilmStyles = window.FilmStyles || {};
  const $$ = (q, e) => [...(e || document).querySelectorAll(q)];
  const el = (tag, cls, ...kids) => { const e = document.createElement(tag); if (cls) e.className = cls; e.append(...kids.filter(k => k != null)); return e; };
  const TILT = [-0.7, 0.5, -0.3, 0.8, -0.5, 0.3, -0.9, 0.6];
  // 白模小人：圆脑袋、朝前的蓝鼻尖、蓝身子，一只手举着
  const MAN = '<svg viewBox="0 0 64 76" width="74" height="88" aria-hidden="true"><g fill="none" stroke="#43342a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    + '<path d="M22 58c-1 6-2 9-3 13M40 58c1 6 2 9 3 13" /><path d="M14 72h7M41 72h7"/>'
    + '<path d="M19 36c-1-3 2-6 6-6h12c4 0 7 3 6 6l-2 20c0 2-2 3-4 3H25c-2 0-4-1-4-3z" fill="#7ea6d8"/>'
    + '<path d="M20 38c-5 3-8 7-9 12" /><path class="fx-wave" d="M43 37c5-2 8-7 10-13"/>'
    + '<circle cx="11" cy="51" r="2.6" fill="#f3d9bf"/><circle class="fx-wave" cx="53.5" cy="22.5" r="2.6" fill="#f3d9bf"/>'
    + '<path d="M31 4c8 0 14 6 14 13s-6 13-14 13-14-6-14-13S23 4 31 4z" fill="#f3d9bf"/><path d="M44 14l8 3-8 3z" fill="#5f8fc6"/>'
    + '</g><g fill="#43342a"><circle cx="27" cy="16" r="1.5"/><circle cx="36" cy="16" r="1.5"/></g>'
    + '<path d="M28 21.5c2 2 5 2 7 0" fill="none" stroke="#43342a" stroke-width="1.8" stroke-linecap="round"/></svg>';
  let undo = [];

  // 顶上：小人说一句拍到哪了，下面一行小字写开工多久、花了多少
  function hello(main) {
    const F = JSON.parse((document.getElementById('style-facts') || {}).textContent || '{}');
    const chips = $$(':scope > .unit > h3 .chip', main).map(c => c.textContent.trim()), n = k => chips.filter(c => c === k).length;
    const rest = [[n('生成中'), '个正在拍'], [n('检查中'), '个在检查'], [n('要重抽'), '个要重抽'], [n('待检查'), '个还没检查'], [n('失败'), '个没拍成']].filter(([k]) => k);
    const say = n('合格') === chips.length ? `${chips.length} 个单元都拍好了，收工。`
      : [n('合格') ? `拍好 ${n('合格')} 个了` : '还没有拍好的', ...rest.map(([k, t], i) => (i === 0 && t === '个正在拍' ? '还有 ' : '') + k + ' ' + t)].join('，') + '。';
    const facts = [`${chips.length} 个单元`, F.elapsed != null ? `开工 ${F.elapsed} 分钟` : null,
      F.spent != null ? `花了 ¥${F.spent}${F.estimate ? ` / 估 ¥${F.estimate}` : ''}（${F.price === 'discount' ? '折扣价' : '原价'}）` : null,
      F.updated ? `${F.updated} 更新` : null, '放视频时不自动刷新'].filter(Boolean).join(' · ');
    const man = el('span', 'fx-man'); man.innerHTML = MAN;
    const box = el('div', 'fx-hi', man, el('div', 'fx-say', el('b', '', say), el('span', '', facts)));
    const meta = main.querySelector(':scope > .meta');
    (meta || main.firstChild).after(box);
    if (meta) meta.hidden = true;
    undo.push(() => { box.remove(); if (meta) meta.hidden = false; });
  }

  // 照片墙：单元的名字、拍什么挪到它第一次生成那张的上面；后面几次的上面是一支连过来的箭头
  function sheet(main) {
    const units = $$(':scope > .unit', main);
    let k = 0;
    units.forEach(u => {
      const figs = $$(':scope > .takes > figure', u), head = [...u.children].filter(c => !c.classList.contains('takes'));
      if (!figs.length) return;
      const h3 = head.find(c => c.tagName === 'H3'), name = h3 ? [...h3.childNodes].filter(x => x.nodeType === 3).map(x => x.textContent.trim()).join('') : '';
      const uh = el('div', 'fx-uh', ...head);
      figs[0].prepend(uh);
      const more = figs.slice(1).map((f, i) => { const m = el('div', 'fx-uh fx-more', el('span', '', `${name} 第 ${i + 2} 次`)); f.prepend(m); return m; });
      undo.push(() => { u.prepend(...head); uh.remove(); more.forEach(m => m.remove()); });
      const about = uh.querySelector('.about');
      if (about && !about.title) { about.title = about.textContent; undo.push(() => about.removeAttribute('title')); }
      figs.forEach(f => {
        f.style.setProperty('--fx-tilt', `${TILT[k++ % TILT.length]}deg`);
        undo.push(() => f.style.removeProperty('--fx-tilt'));
        // 说明第一行「名字 · 状态 · 用了几分钟 · 计费几秒」：状态做成一枚印章，其余分成几小段
        const cap = f.querySelector(':scope > figcaption'), b = cap && cap.querySelector(':scope > b'), tx = b && b.nextSibling;
        if (tx && tx.nodeType === 3) {
          const parts = tx.textContent.split(' · ').map(s => s.trim()).filter(Boolean);
          if (parts.length) {
            const spans = parts.slice(1).map(p => el('span', 'fx-m', p));
            f.dataset.fxState = cap.dataset.fxState = parts[0];
            tx.replaceWith(...spans);
            undo.push(() => { b.after(tx); spans.forEach(s => s.remove()); delete f.dataset.fxState; delete cap.dataset.fxState; });
          }
        }
        $$(':scope > figcaption li', f).forEach(li => { if (!li.title) { li.title = li.textContent; undo.push(() => li.removeAttribute('title')); } });
      });
    });
    main.classList.add('fx-sheet');
    undo.push(() => main.classList.remove('fx-sheet'));
    // 点顶上那一串标签里的单元，跳到它那几张
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

  // 哪一张在放：在放的那一张留着原生的播放条
  function playing(main) {
    const mark = e => { const f = e.target.closest && e.target.closest('.takes > figure'); if (f) f.classList.toggle('fx-playing', e.type === 'play'); };
    ['play', 'pause', 'ended'].forEach(t => main.addEventListener(t, mark, true));
    undo.push(() => { ['play', 'pause', 'ended'].forEach(t => main.removeEventListener(t, mark, true)); $$('.fx-playing', main).forEach(f => f.classList.remove('fx-playing')); });
  }

  (S.warm = S.warm || {}).progress = {
    on() { const main = document.querySelector('main'); if (!main || undo.length) return; hello(main); sheet(main); playing(main); },
    off() { undo.reverse().forEach(f => f()); undo = []; },
  };
})();

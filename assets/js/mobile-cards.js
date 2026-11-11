/* Small-screen swipeable card collections with visible, accessible arrow buttons. */
(() => {
  'use strict';
  const matchCard = '.subject-card,.network-card,.value-card,.price-card,.blog-card,.exam-card,.feature-card,.review-card,.testimonial-card,.tutor-card,.location-card,.card-soft,[class*="-card"]';
  const targets = 'main .row, main [class*="-grid"]';
  const panels = [...document.querySelectorAll(targets)];
  function qualifies(el) {
    if (el.closest('form,.safety-emergency,.policy-chapters')) return false;
    const children = [...el.children].filter(node => node.nodeType === 1);
    if (children.length < 2 || children.length > 20) return false;
    if (el.classList.contains('row')) {
      return children.every(node =>
        [...node.classList].some(name => name.startsWith('col-')) &&
        !!node.querySelector(matchCard));
    }
    return children.every(node =>
      node.matches('.area-link,.nt-review-card,a,article,[class*="-card"]') ||
      !!node.querySelector(matchCard));
  }
  panels.forEach((track, index) => {
    if (!qualifies(track) || track.closest('.nt-card-slider')) return;
    const area = track.closest('section');
    const sectionName = area?.querySelector('.section-heading h2, h2')?.textContent?.trim() || 'cards';
    const wrap = document.createElement('div');
    wrap.className = 'nt-card-slider';
    const controls = document.createElement('div');
    controls.className = 'nt-scroll-controls';
    controls.setAttribute('aria-label', 'Scroll ' + sectionName);
    const viewport = document.createElement('div');
    viewport.className = 'nt-card-viewport';
    viewport.id = 'nt-scroll-track-' + (index + 1);
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', sectionName + ' carousel');
    viewport.tabIndex = 0;
    const arrow = (dir, text, path) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'nt-scroll-arrow';
      btn.setAttribute('aria-label', text + ' ' + sectionName);
      btn.setAttribute('aria-controls', viewport.id);
      btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + path + '"/></svg>';
      btn.addEventListener('click', () => {
        const card = track.children[0];
        const amount = (card?.getBoundingClientRect().width || viewport.clientWidth * 0.82) + 14;
        viewport.scrollBy({left: dir * amount, behavior: 'smooth'});
      });
      return btn;
    };
    const prev = arrow(-1, 'Previous', 'M15 18l-6-6 6-6');
    const next = arrow(1, 'Next', 'M9 18l6-6-6-6');
    controls.append(prev, next);
    track.before(wrap);
    wrap.append(controls, viewport);
    viewport.appendChild(track);
    track.classList.add('nt-card-track');
    let scheduled = false;
    const update = () => {
      scheduled = false;
      const max = viewport.scrollWidth - viewport.clientWidth;
      prev.disabled = viewport.scrollLeft <= 3;
      next.disabled = viewport.scrollLeft >= max - 3 || max <= 3;
    };
    viewport.addEventListener('scroll', () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
    }, {passive: true});
    window.addEventListener('resize', update, {passive: true});
    update();
  });
})();

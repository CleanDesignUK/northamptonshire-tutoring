/* GTM-56GZFL5S: load only after optional tracking consent. */
(() => {
  'use strict';
  const key = 'northamptonshire_tutoring_cookie_choice_v1';
  const container = 'GTM-56GZFL5S';
  let loaded = false;
  const consented = () => {
    try { return localStorage.getItem(key) === 'accepted'; }
    catch { return false; }
  };
  const loadGTM = () => {
    if (loaded || !consented()) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({'gtm.start': Date.now(), event: 'gtm.js'});
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(container);
    document.head.appendChild(tag);
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadGTM, {once: true});
  } else {
    loadGTM();
  }
  document.addEventListener('nt:cookie-choice', (event) => {
    if (event.detail?.value === 'accepted') loadGTM();
    else if (loaded) location.reload();
  });
})();

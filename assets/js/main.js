(() => {
  'use strict';
  document.querySelectorAll('[data-year]').forEach(el => {el.textContent = String(new Date().getFullYear());});
  const path = location.pathname.replace(/\/index\.html$/, '/');
  document.querySelectorAll('.navbar a.nav-link').forEach(a => {
    try {
      const target = new URL(a.getAttribute('href'), location.href);
      if (target.origin === location.origin && target.pathname === path) a.classList.add('active');
    } catch (_) { /* Preview without a base URL. */ }
  });
  const cookieKey = 'northamptonshire_tutoring_cookie_choice_v1';
  const banner = document.getElementById('cookie-banner');
  const getChoice = () => {try{return localStorage.getItem(cookieKey)}catch{return null}};
  const setChoice = value => {
    try{localStorage.setItem(cookieKey,value)}catch{}
    if(banner) banner.hidden=true;
    document.dispatchEvent(new CustomEvent('nt:cookie-choice',{detail:{value}}));
  };
  if(banner){
    if(!getChoice()) banner.hidden=false;
    banner.querySelectorAll('[data-cookie-choice]').forEach(btn=>btn.addEventListener('click',()=>setChoice(btn.dataset.cookieChoice)));
    banner.addEventListener('keydown',e=>{if(e.key==='Escape')setChoice('rejected')});
  }
  // No advertising or analytics scripts are injected by default. A future
  // consent-aware integration should listen for nt:cookie-choice and check
  // northamptonshire_tutoring_cookie_choice_v1 before loading trackers.
})();

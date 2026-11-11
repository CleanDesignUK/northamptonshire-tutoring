(() => {
  'use strict';
  document.querySelectorAll('[data-year]').forEach(el => {el.textContent = String(new Date().getFullYear());});
  const path = location.pathname === '/' ? '/' : location.pathname.replace(/\/$/, '');
  document.querySelectorAll('.navbar a.nav-link').forEach(a => {if (a.getAttribute('href') === path) a.classList.add('active');});
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
  // Cards are fully clickable, with keyboard access for linked blog cards.
  document.querySelectorAll('.blog-card.card-clickable').forEach(card=>{
    const target=card.querySelector('h3 a')?.getAttribute('href');
    if(!target)return;
    card.addEventListener('click',e=>{if(e.target.closest('a,button'))return;location.href=target;});
    card.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target===card){e.preventDefault();location.href=target;}});
  });
  // No advertising or analytics scripts are injected by default. A future
  // consent-aware integration should listen for nt:cookie-choice and check
  // northamptonshire_tutoring_cookie_choice_v1 before loading trackers.
})();

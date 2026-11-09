'use strict';
(() => {
 const hero = document.querySelector('[data-popsy-hero]');
 if (!hero) return;
 const reduced = matchMedia('(prefers-reduced-motion: reduce)');
 const fine = matchMedia('(hover: hover) and (pointer: fine)');
 const pack = hero.querySelector('.popsy-home-pack-layer');
 const food = hero.querySelector('.popsy-home-food-layer');
 let frame = 0, bounds = null, point = null, listening = false;
 const reset = () => {
  if (frame) cancelAnimationFrame(frame);
  frame = 0; point = null;
  for (const layer of [pack, food]) {
   layer.style.setProperty('--popsy-x', '0px');
   layer.style.setProperty('--popsy-y', '0px');
  }
 };
 function paint() {
  frame = 0;
  if (!point || !bounds) return;
  const x = Math.max(-1, Math.min(1, (point.x - bounds.left) / bounds.width * 2 - 1));
  const y = Math.max(-1, Math.min(1, (point.y - bounds.top) / bounds.height * 2 - 1));
  pack.style.setProperty('--popsy-x', `${x * 5}px`);
  pack.style.setProperty('--popsy-y', `${y * 3}px`);
  food.style.setProperty('--popsy-x', `${x * -8}px`);
  food.style.setProperty('--popsy-y', `${y * -5}px`);
 }
 const enter = () => { bounds = hero.getBoundingClientRect(); };
 const move = event => {
  if (event.pointerType && event.pointerType !== 'mouse') return;
  if (!bounds) enter();
  point = {x:event.clientX, y:event.clientY};
  if (!frame) frame = requestAnimationFrame(paint);
 };
 function configure() {
  const enabled = !reduced.matches && fine.matches;
  if (enabled !== listening) {
   const action = enabled ? 'addEventListener' : 'removeEventListener';
   hero[action]('pointerenter', enter);
   hero[action]('pointermove', move);
   hero[action]('pointerleave', reset);
   listening = enabled;
  }
  if (!enabled) reset();
 }
 const ready = () => { hero.dataset.ready = 'true'; };
 hero.dataset.inView = 'true';
 if (reduced.matches) ready();
 else {
  hero.dataset.enhanced = 'true';
  const fallback = window.setTimeout(ready, 1600);
  const images = [...hero.querySelectorAll('img')].map(img =>
   typeof img.decode === 'function' ? img.decode().catch(() => {}) : Promise.resolve());
  const fonts = document.fonts ? document.fonts.ready : Promise.resolve();
  Promise.all([...images, fonts]).then(() => { window.clearTimeout(fallback); ready(); });
 }
 if ('IntersectionObserver' in window) {
  new IntersectionObserver(entries => {
   hero.dataset.inView = String(entries[0].isIntersecting && !document.hidden);
   if (!entries[0].isIntersecting) reset();
  }, {threshold:0}).observe(hero);
 }
 document.addEventListener('visibilitychange', () => {
  hero.dataset.inView = String(!document.hidden && hero.getBoundingClientRect().bottom > 0);
  if (document.hidden) reset();
 });
 window.addEventListener('resize', () => { bounds = null; reset(); }, {passive:true});
 reduced.addEventListener('change', () => { ready(); configure(); });
 fine.addEventListener('change', configure);
 configure();
})();

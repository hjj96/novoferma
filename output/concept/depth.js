/* Decorative motion only: the layout and all content work without this file. */
(() => {
  'use strict';

  const motionMedia = matchMedia('(min-width: 900px) and (prefers-reduced-motion: no-preference)');
  const pointerMedia = matchMedia('(hover: hover) and (pointer: fine)');
  const menu = document.querySelector('#site-menu');
  const clamp = (value, limit = 1) => Math.max(-limit, Math.min(limit, value));
  const amount = value => Number.isFinite(Number(value)) ? Number(value) : 0;
  const scenes = [...document.querySelectorAll('[data-depth-scene]')].map(element => ({
    element,
    visible: true,
    targets: [...element.querySelectorAll('[data-depth]')]
      .filter(target => target.closest('[data-depth-scene]') === element)
      .map(element => ({ element, travel: amount(element.dataset.depth), turn: amount(element.dataset.depthTurn) }))
  })).filter(scene => scene.targets.length);
  // These product surfaces are intentionally static in the shared CSS.
  const tilts = [...document.querySelectorAll('[data-tilt]')]
    .filter(element => !element.closest('.product-card,.product-detail')).map(element => ({
    element, active: false, dirty: false, x: 0, y: 0
  }));

  if (!scenes.length && !tilts.length) return;

  let frame = 0;
  const paused = () => document.hidden || Boolean(menu?.open);
  const motionEnabled = () => motionMedia.matches && pointerMedia.matches;

  // Avoid repeated inline-style mutations when the rounded value is unchanged.
  function setVariable(element, name, value) {
    if (element.style.getPropertyValue(name) !== value) element.style.setProperty(name, value);
  }

  function resetTilt(tilt) {
    tilt.active = false;
    tilt.dirty = false;
    setVariable(tilt.element, '--tilt-x', '0deg');
    setVariable(tilt.element, '--tilt-y', '0deg');
    setVariable(tilt.element, '--tilt-lift', '0px');
  }

  function stopFrame() {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
  }

  function schedule() {
    if (!frame && motionEnabled() && !paused()) frame = requestAnimationFrame(render);
  }

  function render() {
    frame = 0;
    if (!motionEnabled() || paused()) return;

    const viewportHeight = document.documentElement.clientHeight || innerHeight;
    const changes = [];
    const rectangles = new Map();
    const readRectangle = element => {
      if (!rectangles.has(element)) rectangles.set(element, element.getBoundingClientRect());
      return rectangles.get(element);
    };

    // Read all geometry first. Only stationary scene/tilt hosts are measured.
    for (const scene of scenes) {
      if (!scene.visible) continue;
      const rectangle = readRectangle(scene.element);
      if (!rectangle.height || rectangle.bottom < -160 || rectangle.top > viewportHeight + 160) continue;
      const progress = clamp((viewportHeight / 2 - rectangle.top - rectangle.height / 2) /
        (viewportHeight / 2 + rectangle.height / 2));
      for (const target of scene.targets) {
        changes.push([target.element, '--depth-y', `${(progress * target.travel).toFixed(2)}px`]);
        changes.push([target.element, '--depth-turn', `${(progress * target.turn).toFixed(3)}deg`]);
      }
    }

    for (const tilt of tilts) {
      if (!tilt.dirty) continue;
      tilt.dirty = false;
      let x = 0;
      let y = 0;
      let lift = 0;
      if (tilt.active && motionEnabled()) {
        const rectangle = readRectangle(tilt.element);
        if (rectangle.width && rectangle.height) {
          x = -clamp((tilt.y - rectangle.top) / rectangle.height * 2 - 1) * 3;
          y = clamp((tilt.x - rectangle.left) / rectangle.width * 2 - 1) * 3;
          // Cards receive their shared lift from hover/focus CSS; the detail
          // figure keeps its independent, smaller pointer response.
          lift = tilt.element.closest('.product-card') ? 0 : -4;
        }
      }
      changes.push([tilt.element, '--tilt-x', `${x.toFixed(2)}deg`]);
      changes.push([tilt.element, '--tilt-y', `${y.toFixed(2)}deg`]);
      changes.push([tilt.element, '--tilt-lift', `${lift}px`]);
    }

    // These variables only affect transforms on dedicated moving descendants.
    for (const [element, name, value] of changes) setVariable(element, name, value);
  }

  function updateAvailability() {
    stopFrame();
    if (!motionEnabled() || paused()) {
      for (const scene of scenes) {
        for (const target of scene.targets) {
          setVariable(target.element, '--depth-y', '0px');
          setVariable(target.element, '--depth-turn', '0deg');
        }
      }
    }
    if (!motionEnabled() || paused()) tilts.forEach(resetTilt);
    schedule();
  }

  for (const tilt of tilts) {
    const move = event => {
      if (!motionEnabled() || paused() || event.pointerType === 'touch') return;
      tilt.active = true;
      tilt.dirty = true;
      tilt.x = event.clientX;
      tilt.y = event.clientY;
      schedule();
    };
    const leave = () => {
      tilt.active = false;
      tilt.dirty = true;
      schedule();
    };
    tilt.element.addEventListener('pointerenter', move, { passive: true });
    tilt.element.addEventListener('pointermove', move, { passive: true });
    tilt.element.addEventListener('pointerleave', leave, { passive: true });
    tilt.element.addEventListener('pointercancel', leave, { passive: true });
  }

  if ('IntersectionObserver' in window) {
    const sceneByElement = new Map(scenes.map(scene => [scene.element, scene]));
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) sceneByElement.get(entry.target).visible = entry.isIntersecting;
      schedule();
    }, { rootMargin: '160px 0px', threshold: 0 });
    scenes.forEach(scene => observer.observe(scene.element));
  }

  // Transforms do not resize these stationary hosts, preventing observer loops.
  // Watching body also catches catalogue filtering and image-driven layout shifts.
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(schedule);
    observer.observe(document.body);
    scenes.forEach(scene => observer.observe(scene.element));
  }

  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule, { passive: true });
  addEventListener('pageshow', updateAvailability);
  addEventListener('blur', () => tilts.forEach(resetTilt));
  document.addEventListener('visibilitychange', updateAvailability);
  document.addEventListener('load', schedule, true);
  motionMedia.addEventListener('change', updateAvailability);
  pointerMedia.addEventListener('change', updateAvailability);

  // Native dialog.open is reliable even before the menu's body class changes.
  if (menu) {
    new MutationObserver(updateAvailability).observe(menu, { attributes: true, attributeFilter: ['open'] });
    menu.addEventListener('close', updateAvailability);
  }

  if (document.fonts) {
    document.fonts.ready.then(schedule);
    document.fonts.addEventListener?.('loadingdone', schedule);
  }

  updateAvailability();
})();

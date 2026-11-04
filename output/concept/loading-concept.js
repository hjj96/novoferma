/* Full-viewport motion study, separate from the production site's load path. */
(() => {
  'use strict';
  const screen = document.querySelector('.screen');
  const curtain = document.querySelector('.curtain');
  const canvas = document.querySelector('.meatballs');
  const context = canvas.getContext('2d');
  const play = document.querySelector('.play');
  const playLabel = document.querySelector('.play-label');
  const status = document.querySelector('.playback-state');
  const preview = document.querySelector('iframe');
  const controls = document.querySelector('.preview-controls');
  const placeholder = document.querySelector('.screen-placeholder');
  const replay = document.querySelector('.replay');
  const close = document.querySelector('.close-preview');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const sprite = new Image();
  sprite.src = 'assets/loading-meatball.webp';
  const HOLD_MS = 120, REVEAL_MS = 180;
  let width = 0, height = 0, bodies = [], frame = 0, playing = false;
  let startedAt = 0, lastFrameAt = 0, filledAt = 0, openingAt = 0, generation = 0;
  let world = null;
  let fullscreen = false, opening = false, filled = false, previousFocus = null;
  let exitAnimation = null;
  const surrounding = [...document.querySelector('.presentation').children].filter(element => element !== screen);
  const cancel = () => {
    cancelAnimationFrame(frame);
    exitAnimation?.cancel();
    exitAnimation = null;
    playing = false;
  };
  const fit = () => {
    const rect = screen.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context?.setTransform(ratio, 0, 0, ratio, 0, 0);
  };
  const paint = () => {
    if (!context) return;
    context.clearRect(0, 0, width, height);
    if (!sprite.complete || !sprite.naturalWidth) return;
    for (const body of bodies) {
      if (body.y + body.r < 0 || body.y - body.r > height) continue;
      context.save();
      context.translate(body.x, body.y);
      context.rotate(body.angle);
      // The entire alpha silhouette fits inside the physical collision circle.
      context.drawImage(sprite, -body.r * .97, -body.r * .90, body.r * 1.94, body.r * 1.80);
      context.restore();
    }
  };
  const makePile = () => {
    world = new globalThis.NovofermaPile(width, height);
    bodies = world.bodies;
    screen.dataset.particleCount = String(world.total);
  };
  const poster = () => {
    if (!globalThis.NovofermaPile) return;
    makePile();
    // A settled physical pile, never a pattern of preset sprite positions.
    for (let step = 0; step < 240 && !world.complete; step++) world.step(1 / 60);
    paint();
  };
  const enterFullscreen = () => {
    if (fullscreen) return;
    previousFocus = document.activeElement;
    placeholder.style.height = `${screen.getBoundingClientRect().height}px`;
    placeholder.hidden = false;
    fullscreen = true;
    screen.classList.add('is-fullscreen');
    document.documentElement.classList.add('preview-open');
    surrounding.forEach(element => {element.inert = true;});
    screen.setAttribute('role', 'dialog');
    screen.setAttribute('aria-modal', 'true');
    screen.focus({preventScroll:true});
  };
  const reveal = (message = 'Фрикадельки растворились. Главная открыта.') => {
    generation++;
    cancel();
    curtain.hidden = true;
    preview.inert = false;
    controls.hidden = !fullscreen;
    playLabel.textContent = 'Посмотреть ещё раз';
    status.textContent = message;
    screen.dataset.state = 'complete';
    if (fullscreen) replay.focus({preventScroll:true});
  };
  const leaveFullscreen = () => {
    generation++;
    cancel();
    fullscreen = false;
    screen.classList.remove('is-fullscreen');
    document.documentElement.classList.remove('preview-open');
    surrounding.forEach(element => {element.inert = false;});
    placeholder.hidden = true;
    controls.hidden = true;
    curtain.hidden = false;
    preview.inert = true;
    screen.removeAttribute('role');
    screen.removeAttribute('aria-modal');
    fit();
    poster();
    screen.dataset.state = 'poster';
    status.textContent = 'Свободное падение · на весь экран';
    if (previousFocus?.isConnected) previousFocus.focus({preventScroll:true});
  };
  const beginOpening = () => {
    opening = true;
    screen.dataset.state = 'opening';
    exitAnimation = curtain.animate([
      {opacity:1}, {opacity:0}
    ], {duration:REVEAL_MS,easing:'ease-out',fill:'forwards'});
  };
  const run = () => {
    fit();
    makePile();
    filled = false;
    opening = false;
    playing = true;
    screen.dataset.state = 'playing';
    status.textContent = 'Заполняем весь экран…';
    startedAt = lastFrameAt = performance.now();
    const tick = now => {
      if (!playing) return;
      const elapsed = now - startedAt;
      const dt = Math.min((now - lastFrameAt) / 1000, .05);
      lastFrameAt = now;
      world.step(dt);
      paint();
      if (world.complete && !filled) {
        filled = true;
        filledAt = now;
        screen.dataset.state = 'filled';
      }
      if (filled && now - filledAt >= HOLD_MS && !opening) {
        openingAt = now;
        beginOpening();
      } else if (opening && now - openingAt >= REVEAL_MS) {
        reveal();
        return;
      }
      // The demo must remain escapable on a very slow device.
      if (elapsed > 5500) {reveal('Главная открыта.'); return;}
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
  };
  const start = async () => {
    cancel();
    const currentGeneration = ++generation;
    enterFullscreen();
    controls.hidden = true;
    curtain.hidden = false;
    preview.inert = true;
    screen.focus({preventScroll:true});
    fit();
    context?.clearRect(0, 0, width, height);
    if (reduceMotion.matches || !context || !globalThis.NovofermaPile || typeof curtain.animate !== 'function') {
      reveal('Главная открыта без движения — с учётом настроек устройства.');
      return;
    }
    status.textContent = 'Готовим сцену…';
    screen.dataset.state = 'preparing';
    let waitTimer;
    await Promise.race([
      sprite.decode().catch(() => {}),
      new Promise(resolve => {waitTimer = setTimeout(resolve, 1200);})
    ]);
    clearTimeout(waitTimer);
    if (currentGeneration !== generation) return;
    if (reduceMotion.matches || document.hidden || !sprite.naturalWidth) {
      reveal('Главная страница открыта.');
      return;
    }
    run();
  };
  const onKeydown = event => {
    if (event.key === 'Escape' && fullscreen) {
      event.preventDefault();
      if (!curtain.hidden) reveal('Анимация пропущена. Главная открыта.');
      else leaveFullscreen();
    }
    if (event.key === 'Tab' && fullscreen && !curtain.hidden) event.preventDefault();
    if (event.key === 'Tab' && fullscreen && curtain.hidden) {
      if (event.shiftKey && document.activeElement === replay) {event.preventDefault();close.focus();}
      else if (!event.shiftKey && document.activeElement === close) {event.preventDefault();preview.focus();}
    }
  };
  document.addEventListener('keydown', onKeydown);
  // Same-origin preview: Escape should also work while browsing inside the iframe.
  preview.addEventListener('load', () => {
    try {
      preview.contentDocument.addEventListener('keydown', event => {
        if (event.key === 'Escape' && fullscreen) {event.preventDefault();leaveFullscreen();}
      });
    } catch { /* External pages remain navigable without cross-origin access. */ }
  });
  play.addEventListener('click', start);
  replay.addEventListener('click', start);
  close.addEventListener('click', leaveFullscreen);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && fullscreen && !curtain.hidden) reveal('Главная страница открыта.');
  });
  reduceMotion.addEventListener('change', () => {
    if (reduceMotion.matches && fullscreen && !curtain.hidden) reveal('Главная открыта без движения.');
  });
  new ResizeObserver(() => {
    const rect = screen.getBoundingClientRect();
    // The initial fixed-position resize was already applied synchronously.
    if (Math.abs(rect.width - width) < .5 && Math.abs(rect.height - height) < .5) return;
    fit();
    if (playing) {
      world.resize(width, height);
      bodies = world.bodies;
      paint();
    } else if (!curtain.hidden) poster();
  }).observe(screen);
  fit();
  sprite.decode().then(() => {if (!fullscreen) poster();}).catch(() => {});
  screen.dataset.state = 'poster';
})();

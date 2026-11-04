/* A reviewable motion study. It is deliberately separate from the site's load path. */
(() => {
  'use strict';
  const screen = document.querySelector('.screen');
  const curtain = document.querySelector('.curtain');
  const chicken = document.querySelector('.chicken');
  const note = document.querySelector('.chicken-note');
  const heading = document.querySelector('h1');
  const signature = document.querySelector('.scene-signature');
  const canvas = document.querySelector('canvas');
  const context = canvas.getContext('2d');
  const play = document.querySelector('.play');
  const playLabel = document.querySelector('.play-label');
  const density = document.querySelector('#more-meatballs');
  const status = document.querySelector('.playback-state');
  const preview = document.querySelector('iframe');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const sprite = new Image();
  sprite.src = 'assets/loading-meatball.webp';
  let width = 0, height = 0, bodies = [], frame = 0, playing = false;
  let startedAt = 0, previousTime = 0, spawned = 0, randomState = 431;
  let generation = 0, assetWait = 0;
  const animations = [];
  const random = () => ((randomState = (randomState * 1664525 + 1013904223) >>> 0) / 4294967296);
  const animate = (element, frames, options) => {
    const animation = element.animate(frames, {...options, fill: 'both'});
    animations.push(animation);
    return animation;
  };
  const cancel = () => {
    cancelAnimationFrame(frame);
    clearTimeout(assetWait);
    animations.splice(0).forEach(animation => animation.cancel());
    screen.classList.remove('is-playing');
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
      context.save();
      context.translate(body.x, body.y);
      context.rotate(body.angle);
      context.drawImage(sprite, -body.r * 1.08, -body.r, body.r * 2.16, body.r * 2);
      context.restore();
    }
  };
  const poster = () => {
    const r = width < 600 ? 33 : 51;
    bodies = [
      {x:width * .17, y:height - r * .30, r:r * 1.2, angle:-.3},
      {x:width * .08, y:height - r * .27, r:r, angle:.7},
      {x:width * .27, y:height - r * .22, r:r * .85, angle:.3},
      {x:width * .16, y:height - r * 1.86, r:r * .85, angle:1.4}
    ];
    paint();
  };
  const reveal = (message = 'Все к столу! Главная страница открыта.') => {
    const focusInCurtain = curtain.contains(document.activeElement);
    generation++;
    cancel();
    curtain.hidden = true;
    preview.inert = false;
    playLabel.textContent = 'Посмотреть ещё раз';
    status.textContent = message;
    screen.dataset.state = 'complete';
    if (focusInCurtain) play.focus({preventScroll: true});
  };
  const spawn = index => {
    const small = width < 600;
    const baseRadius = small ? 30 : Math.min(57, width / 19);
    const r = baseRadius * (.8 + random() * .43);
    // Alternate lanes so the opening is legible and the pile spreads across the screen.
    const lane = ((index * 7) % 13 + random() * .65) / 13;
    bodies.push({
      x:r + lane * (width - 2 * r), y:-r * (1 + random() * 2.4), r,
      vx:(random() - .5) * 125, vy:150 + random() * 170,
      angle:random() * Math.PI * 2, spin:(random() - .5) * 4,
      mass:r * r
    });
  };
  const physics = dt => {
    for (const body of bodies) {
      body.vy += 2050 * dt;
      body.x += body.vx * dt;
      body.y += body.vy * dt;
      body.angle += body.spin * dt;
    }
    // A small, bounded circle solver: no runtime library or accumulating particles.
    for (let iteration = 0; iteration < 4; iteration++) {
      for (let i = 0; i < bodies.length; i++) {
        const a = bodies[i];
        for (let j = i + 1; j < bodies.length; j++) {
          const b = bodies[j];
          const dx = b.x - a.x, dy = b.y - a.y;
          const distance = Math.hypot(dx, dy) || .01;
          const overlap = a.r + b.r - distance;
          if (overlap <= 0) continue;
          const nx = dx / distance, ny = dy / distance;
          const share = b.mass / (a.mass + b.mass);
          a.x -= nx * overlap * share;
          a.y -= ny * overlap * share;
          b.x += nx * overlap * (1 - share);
          b.y += ny * overlap * (1 - share);
          const velocity = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny;
          if (velocity < 0) {
            const impulse = -1.24 * velocity;
            a.vx -= impulse * share * nx;
            a.vy -= impulse * share * ny;
            b.vx += impulse * (1 - share) * nx;
            b.vy += impulse * (1 - share) * ny;
            a.spin *= .985;
            b.spin *= .985;
          }
        }
        const floor = height + a.r * .3;
        if (a.y + a.r > floor) {
          a.y = floor - a.r;
          if (a.vy > 0) a.vy *= -.29;
          a.vx *= .97;
          a.spin *= .96;
        }
        if (a.x < a.r) {a.x = a.r; a.vx = Math.abs(a.vx) * .45;}
        if (a.x > width - a.r) {a.x = width - a.r; a.vx = -Math.abs(a.vx) * .45;}
      }
    }
  };
  const run = () => {
    fit();
    bodies = [];
    spawned = 0;
    randomState = 431;
    playing = true;
    screen.dataset.state = 'playing';
    screen.classList.add('is-playing');
    playLabel.textContent = 'Начать сначала';
    status.textContent = 'Собираемся к столу…';
    const small = width < 600;
    const total = density.checked ? (small ? 30 : 58) : (small ? 12 : 25);
    const chickenRest = small ? 140 : 170;
    animate(chicken, [
      {transform:`translateY(${chickenRest}px) rotate(6deg)`, offset:0, easing:'cubic-bezier(.22,.7,.2,1)'},
      {transform:'translateY(-10px) rotate(-12deg)', offset:.27, easing:'ease-in-out'},
      {transform:'translateY(0) rotate(-10deg)', offset:.42, easing:'ease-in-out'},
      {transform:'translateY(-20px) rotate(-15deg)', offset:.78, easing:'ease-in'},
      {transform:`translateY(${chickenRest}px) rotate(8deg)`, offset:1}
    ], {duration:2170, easing:'linear'});
    animate(note, [{opacity:0},{opacity:1,offset:.23},{opacity:1,offset:.72},{opacity:0}], {duration:1920});
    animate(curtain, [{transform:'translateY(0)'},{transform:'translateY(104%)'}], {delay:2200,duration:600,easing:'cubic-bezier(.65,0,.25,1)'});
    startedAt = previousTime = performance.now();
    const tick = now => {
      if (!playing) return;
      const elapsed = now - startedAt;
      const dt = Math.min((now - previousTime) / 1000, .04);
      previousTime = now;
      const target = Math.min(total, Math.max(0, Math.floor((elapsed - 80) / 1500 * total) + 1));
      while (spawned < target) spawn(spawned++);
      const steps = Math.max(1, Math.ceil(dt / (1 / 120)));
      for (let i = 0; i < steps; i++) physics(dt / steps);
      paint();
      if (elapsed >= 1840 && heading.dataset.ready !== 'yes') {
        heading.innerHTML = 'Все<br><em>к столу!</em>';
        heading.dataset.ready = 'yes';
        signature.textContent = 'Повод собраться найдётся.';
      }
      if (elapsed >= 2800) {reveal(); return;}
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
  };
  const start = async () => {
    cancel();
    const currentGeneration = ++generation;
    if (reduceMotion.matches || !context || typeof curtain.animate !== 'function') {
      reveal('Главная открыта без движения — с учётом настроек устройства.');
      return;
    }
    curtain.hidden = false;
    preview.inert = true;
    heading.innerHTML = 'Сейчас будет<br><em>вкусно.</em>';
    heading.dataset.ready = 'no';
    signature.textContent = 'Уже хочется за стол!';
    status.textContent = 'Готовим сцену…';
    const bounds = screen.getBoundingClientRect();
    if (bounds.top < 0 || bounds.bottom > innerHeight) {
      window.scrollTo({top: Math.max(0, window.scrollY + bounds.top - 16), behavior:'instant'});
    }
    // Asset failures must never trap visitors behind an overlay.
    await Promise.race([
      sprite.decode().catch(() => {}),
      new Promise(resolve => {assetWait = setTimeout(resolve, 1200);})
    ]);
    if (currentGeneration !== generation) return;
    clearTimeout(assetWait);
    if (reduceMotion.matches || document.hidden) {
      reveal('Главная открыта без движения.');
      return;
    }
    if (!sprite.naturalWidth) {reveal('Главная открыта. Изображение для анимации недоступно.'); return;}
    run();
  };
  play.addEventListener('click', start);
  document.querySelector('.skip').addEventListener('click', () => reveal());
  density.addEventListener('change', () => {
    if (playing) start();
    else status.textContent = density.checked ? 'Больше фрикаделек · те же 2,8 секунды' : 'Короткая сцена · 2,8 секунды';
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !curtain.hidden) reveal();
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && playing) reveal();
  });
  reduceMotion.addEventListener('change', () => {
    if (reduceMotion.matches && playing) reveal('Главная открыта без движения.');
  });
  new ResizeObserver(() => {
    if (playing) reveal();
    fit();
    if (!curtain.hidden) poster();
  }).observe(screen);
  fit();
  sprite.decode().then(() => {if (!playing && !curtain.hidden) poster();}).catch(() => {});
  screen.dataset.state = 'poster';
})();

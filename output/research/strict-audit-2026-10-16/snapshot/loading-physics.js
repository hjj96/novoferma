/* Small circle-pile simulation used only by the loading motion study. */
(() => {
  'use strict';
  const FIXED_STEP = 1 / 120;

  class NovofermaPile {
    constructor(width, height) {
      this.resize(width, height);
    }

    resize(width, height) {
      this.width = Math.max(120, width);
      this.height = Math.max(120, height);
      this.bodies = [];
      this.elapsed = 0;
      this.complete = false;
      this.emitted = 0;
      this._accumulator = 0;
      this._quiet = 0;
      this._seed = 176431;
      const area = this.width * this.height;
      this.radius = Math.sqrt(area * .88 / (148 * Math.PI));
      this.radius = Math.min(this.width / 9, this.height / 6, this.radius);
      this.gravity = this.height * 9;
      this.floor = this.height + this.radius * .2;
      this._sizes = [];
      let sumArea = 0;
      const targetArea = this.width * (this.height + this.radius * 2) * .865;
      while (sumArea < targetArea && this._sizes.length < 190) {
        const radius = this.radius * (.79 + this._random() * .43);
        this._sizes.push(radius);
        sumArea += Math.PI * radius * radius;
      }
      this.total = this._sizes.length;
      this._emissionDuration = 1.75;
    }

    _random() {
      this._seed = (Math.imul(this._seed, 1664525) + 1013904223) >>> 0;
      return this._seed / 4294967296;
    }

    _emit() {
      const r = this._sizes[this.emitted];
      let bestX = r, bestY = -Infinity;
      // Random candidates choose a clear route into the scene. Checking every
      // existing circle also keeps a queued circle clear above a busy column.
      for (let attempt = 0; attempt < 16; attempt++) {
        const x = r + this._random() * (this.width - r * 2);
        let y = -r - 3;
        for (const body of this.bodies) {
          const sum = r + body.r + 1;
          const dx = Math.abs(x - body.x);
          if (dx < sum) y = Math.min(y, body.y - Math.sqrt(sum * sum - dx * dx));
        }
        if (y > bestY) { bestX = x; bestY = y; }
      }
      this.bodies.push({
        x: bestX, y: bestY, r,
        vx: (this._random() - .5) * this.radius * 2,
        vy: this.height * (.55 + this._random() * .2),
        angle: this._random() * Math.PI * 2,
        spin: (this._random() - .5) * 4,
        mass: r * r,
        visible: true,
      });
      this.emitted++;
    }

    step(dt) {
      if (this.complete || !Number.isFinite(dt) || dt <= 0) return;
      this._accumulator += Math.min(dt, .05);
      while (this._accumulator >= FIXED_STEP) {
        this._advance(FIXED_STEP);
        this._accumulator -= FIXED_STEP;
      }
    }

    _advance(dt) {
      this.elapsed += dt;
      const due = Math.min(this.total, Math.ceil(this.elapsed / this._emissionDuration * this.total));
      while (this.emitted < due) this._emit();
      const bodies = this.bodies;
      for (const body of bodies) {
        body.oldX = body.x;
        body.oldY = body.y;
        body.vy += this.gravity * dt;
        body.vx *= .998;
        body.x += body.vx * dt;
        body.y += body.vy * dt;
        body.angle += body.spin * dt;
        body.contact = false;
      }
      bodies.sort((a, b) => b.y - a.y);
      const pairs = [];
      for (let i = 0; i < bodies.length; i++) {
        const a = bodies[i];
        for (let j = i + 1; j < bodies.length; j++) {
          const b = bodies[j];
          const reach = (a.r + b.r) * 1.5;
          if (Math.abs(a.x - b.x) < reach && Math.abs(a.y - b.y) < reach) pairs.push(a, b);
        }
      }
      for (let iteration = 0; iteration < 48; iteration++) {
        for (const a of bodies) {
          if (a.x < a.r) { a.x = a.r; a.contact = true; }
          if (a.x > this.width - a.r) { a.x = this.width - a.r; a.contact = true; }
          if (a.y > this.floor - a.r) { a.y = this.floor - a.r; a.contact = true; }
        }
        for (let i = 0; i < pairs.length; i += 2) {
          const a = pairs[i], b = pairs[i + 1];
          // A tiny contact skin absorbs numerical settling error without
          // letting the visible silhouettes intersect at dense contacts.
          const limit = (a.r + b.r) * 1.012;
          const dx = b.x - a.x;
          if (Math.abs(dx) >= limit) continue;
          const dy = b.y - a.y;
          if (Math.abs(dy) >= limit) continue;
          const square = dx * dx + dy * dy;
          if (square >= limit * limit) continue;
          const distance = Math.sqrt(square) || .001;
          const nx = dx / distance;
          const ny = dy / distance;
          const penetration = limit - distance;
          const shareA = b.mass / (a.mass + b.mass);
          const moveA = penetration * shareA;
          const moveB = penetration - moveA;
          a.x -= nx * moveA; a.y -= ny * moveA;
          b.x += nx * moveB; b.y += ny * moveB;
          a.contact = b.contact = true;
        }
      }
      let maximumSpeed = 0;
      for (const body of bodies) {
        body.vx = (body.x - body.oldX) / dt;
        body.vy = (body.y - body.oldY) / dt;
        if (body.contact) {
          body.vx *= .96;
          body.vy *= .96;
          body.spin *= .965;
          body.angle += body.vx / body.r * dt * .35;
        }
        maximumSpeed = Math.max(maximumSpeed, Math.hypot(body.vx, body.vy));
      }
      if (this.emitted === this.total && maximumSpeed < this.radius * 1.2) this._quiet += dt;
      else this._quiet = 0;
      if (this._quiet >= .2 || this.elapsed >= 3.5) this.complete = true;
    }
  }

  globalThis.NovofermaPile = NovofermaPile;
})();

#!/usr/bin/env node
'use strict';

// Builtins only: node scripts/check_motion.cjs [path/to/site]
// Runs shipped JS with controlled media, observer, timer and image events.
// This checks state/interaction contracts, not rendering, OS settings, AT or CWV.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const SITE = path.resolve(process.argv[2] || path.join(__dirname, '../output/concept'));
const read = name => fs.readFileSync(path.join(SITE, name), 'utf8');
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return {promise, resolve, reject};
};
async function settle() { for (let i = 0; i < 16; i++) await Promise.resolve(); }

class Events {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, fn, options = {}) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push({fn, once:options.once});
  }
  removeEventListener(type, fn) {
    this.listeners.set(type, (this.listeners.get(type) || []).filter(item => item.fn !== fn));
  }
  dispatch(type, props = {}) {
    const event = {type, target:this, bubbles:true, defaultPrevented:false,
      preventDefault() { this.defaultPrevented = true; }, ...props};
    for (let current = this; current; current = event.bubbles ? current.parent : null) {
      for (const item of [...(current.listeners.get(type) || [])]) {
        if (item.once) current.removeEventListener(type, item.fn);
        item.fn(event);
      }
    }
    return event;
  }
}
class Element extends Events {
  constructor(tag = 'div', attributes = {}, doc = null) {
    super(); this.tagName = tag.toUpperCase(); this.attributes = {...attributes}; this.doc = doc;
    this.children = []; this.dataset = {}; this.inert = 'inert' in attributes;
    this.hidden = 'hidden' in attributes; this.tabIndex = Number(attributes.tabindex ?? -1);
    for (const [key, value] of Object.entries(attributes)) {
      if (key.startsWith('data-')) this.dataset[key.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = value;
    }
    const classes = new Set((attributes.class || '').split(/\s+/).filter(Boolean));
    this.classList = {contains:key => classes.has(key), add:key => classes.add(key), remove:key => classes.delete(key),
      toggle:(key, force = !classes.has(key)) => { if (force) classes.add(key); else classes.delete(key); return force; }};
    this.styleValues = new Map(); this.styleWrites = []; this.rectangleReads = 0; this.focusCalls = [];
    this.style = {getPropertyValue:key => this.styleValues.get(key) || '',
      setProperty:(key, value) => { this.styleValues.set(key, value); this.styleWrites.push([key, value]); }};
    this.rectangle = {left:0, top:0, right:400, bottom:400, width:400, height:400};
  }
  append(...nodes) { for (const node of nodes) { node.parent = this; this.children.push(node); } }
  contains(node) { for (; node; node = node.parent) if (node === this) return true; return false; }
  setAttribute(key, value) { this.attributes[key] = String(value); }
  getAttribute(key) { return this.attributes[key] ?? null; }
  getBoundingClientRect() { this.rectangleReads++; return this.rectangle; }
  getClientRects() { return this.hidden || this.noLayout ? [] : [this.rectangle]; }
  matches(selector) {
    return selector.split(',').some(part => {
      part = part.trim(); let valid = true;
      part = part.replace(/:not\(([^)]+)\)/g, (_, inner) => { if (this.matches(inner)) valid = false; return ''; });
      part = part.replace(/:disabled/g, () => { if (!this.disabled) valid = false; return ''; });
      part = part.replace(/\[([^=\]]+)(?:=['"]?([^'"\]]+)['"]?)?\]/g, (_, key, value) => {
        if (!(key in this.attributes) || (value !== undefined && value !== this.attributes[key])) valid = false;
        return '';
      });
      part = part.replace(/\.([\w-]+)/g, (_, key) => { if (!this.classList.contains(key)) valid = false; return ''; });
      part = part.replace(/#([\w-]+)/g, (_, key) => { if (this.attributes.id !== key) valid = false; return ''; });
      return valid && (!part || part.toUpperCase() === this.tagName);
    });
  }
  closest(selector) { for (let el = this; el; el = el.parent) if (el.matches(selector)) return el; return null; }
  querySelectorAll(selector) {
    return this.children.flatMap(el => [...(el.matches(selector) ? [el] : []), ...el.querySelectorAll(selector)]);
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  focus(options) { this.focusCalls.push(options); this.doc.activeElement = this; }
  setPointerCapture(id) { this.capture = id; }
}
function environment({reduced = false, wide = true, fine = true, observers = true} = {}) {
  const doc = new Element('document'); doc.doc = doc; doc.body = new Element('body', {}, doc);
  doc.documentElement = {clientHeight:844}; doc.append(doc.body); doc.activeElement = doc.body;
  doc.readyState = 'loading'; doc.hidden = false;
  const window = new Events(), frames = new Map(), timers = new Map(), ios = [], mutations = [], media = new Map();
  let jobId = 0;
  const matchMedia = query => {
    if (!media.has(query)) {
      const m = new Events(); m.media = query;
      m.matches = query.includes('min-width') ? wide && !reduced : query.includes('pointer') ? fine : reduced;
      m.change = value => { m.matches = value; m.dispatch('change', {bubbles:false, matches:value}); };
      media.set(query, m);
    }
    return media.get(query);
  };
  class IO {
    constructor(fn) { this.fn = fn; this.elements = new Set(); ios.push(this); }
    observe(el) { this.elements.add(el); }
    unobserve(el) { this.elements.delete(el); }
    disconnect() { this.elements.clear(); this.disconnected = true; }
    deliver(el, isIntersecting) { this.fn([{target:el, isIntersecting}]); }
  }
  class MO {
    constructor(fn) { this.fn = fn; mutations.push(this); }
    observe(el) { this.element = el; }
  }
  if (observers) window.IntersectionObserver = IO;
  window.setTimeout = (fn, ms) => { timers.set(++jobId, {fn, ms}); return jobId; };
  window.clearTimeout = id => timers.delete(id);
  const context = {document:doc, window, navigator:{}, location:{search:'', href:''}, console,
    URLSearchParams, Promise, WeakMap, WeakSet, Map, Set, Date, innerHeight:844, scrollY:0, matchMedia,
    addEventListener:window.addEventListener.bind(window),
    getComputedStyle:element => ({visibility:element.computedVisibility || 'visible'}),
    requestAnimationFrame:fn => { frames.set(++jobId, fn); return jobId; }, cancelAnimationFrame:id => frames.delete(id),
    MutationObserver:MO};
  if (observers) context.IntersectionObserver = IO;
  function flushFrames() { const jobs = [...frames.values()]; frames.clear(); jobs.forEach(fn => fn()); }
  function fireTimers(ms) {
    for (const [id, job] of [...timers]) if (job.ms === ms) { timers.delete(id); job.fn(); }
  }
  return {doc, window, context, media, matchMedia, frames, timers, ios, mutations, flushFrames, fireTimers,
    run:name => vm.runInNewContext(read(name), context, {filename:path.join(SITE, name)}),
    el:(tag, attr = {}) => new Element(tag, attr, doc)};
}

function menuFixture() {
  const e = environment({reduced:true}), menu = e.el('dialog', {id:'site-menu'});
  const first = e.el('a', {href:'index.html',tabindex:'0'});
  const close = e.el('button', {class:'menu-close',tabindex:'0'});
  const last = e.el('a', {href:'where-to-buy.html',tabindex:'0'});
  menu.append(first,close,last);
  // Excluded elements occur after the true last link to expose incorrect wrap bounds.
  const disabled = e.el('button', {tabindex:'0'}); disabled.disabled = true;
  const invisible = e.el('a', {href:'#',tabindex:'0'}); invisible.computedVisibility = 'hidden';
  const noLayout = e.el('a', {href:'#',tabindex:'0'}); noLayout.noLayout = true;
  const negative = e.el('a', {href:'#',tabindex:'-1'});
  const hiddenGroup = e.el('div', {hidden:''}); hiddenGroup.append(e.el('a', {href:'#',tabindex:'0'}));
  const inertGroup = e.el('div', {inert:''}); inertGroup.append(e.el('a', {href:'#',tabindex:'0'}));
  menu.append(disabled,invisible,noLayout,negative,hiddenGroup,inertGroup);
  e.doc.body.append(menu); menu.open = true; e.run('script.js');
  return {...e,menu,first,close,last};
}
test('menu: Tab/Shift+Tab wrap visible enabled bounds without leaving the modal', () => {
  const m = menuFixture(); m.last.focus();
  const forward = m.last.dispatch('keydown', {key:'Tab'});
  assert.equal(forward.defaultPrevented,true); assert.equal(m.doc.activeElement,m.first);
  assert.equal(m.first.focusCalls.at(-1).preventScroll,true);
  const backward = m.first.dispatch('keydown', {key:'Tab',shiftKey:true});
  assert.equal(backward.defaultPrevented,true); assert.equal(m.doc.activeElement,m.last);
});
test('menu: inner traversal, modified Tab and a closed dialog remain native', () => {
  const m = menuFixture(); m.close.focus();
  assert.equal(m.close.dispatch('keydown', {key:'Tab'}).defaultPrevented,false);
  assert.equal(m.close.dispatch('keydown', {key:'Tab',shiftKey:true}).defaultPrevented,false);
  m.last.focus(); assert.equal(m.last.dispatch('keydown', {key:'Tab',ctrlKey:true}).defaultPrevented,false);
  m.menu.open = false; assert.equal(m.last.dispatch('keydown', {key:'Tab'}).defaultPrevented,false);
  m.first.focus(); assert.equal(m.first.dispatch('keydown', {key:'Tab',shiftKey:true}).defaultPrevented,false);
});

function revealFixture(options = {}) {
  const e = environment(options); const first = e.el('section', {class:'page-heading reveal'});
  first.rectangle = {...first.rectangle, top:90, bottom:400};
  const below = e.el('section', {class:'reveal'}); below.rectangle = {...below.rectangle, top:1000, bottom:1400};
  const link = e.el('a'); below.append(link); e.doc.body.append(first, below); e.run('script.js');
  return {...e, first, below, link};
}
test('reveal: first viewport stays unprepared; focus immediately releases a below-fold block', () => {
  const r = revealFixture(); assert.equal(r.first.classList.contains('is-prepared'), false);
  assert.equal(r.below.classList.contains('is-prepared'), true);
  r.link.dispatch('focusin'); assert.equal(r.below.classList.contains('is-prepared'), false);
  assert.equal(r.below.classList.contains('is-visible'), true); assert.equal(r.ios[0].elements.has(r.below), false);
});
test('reveal: reduced motion toggled mid-session releases every prepared/entrance element', () => {
  const r = revealFixture(); assert.ok(r.first.classList.contains('page-enter'));
  r.matchMedia('(prefers-reduced-motion: reduce)').change(true);
  assert.equal(r.first.classList.contains('page-enter'), false); assert.ok(r.ios[0].disconnected);
  assert.equal(r.below.classList.contains('is-prepared'), false); assert.ok(r.below.classList.contains('is-visible'));
  r.matchMedia('(prefers-reduced-motion: reduce)').change(false);
  assert.equal(r.below.classList.contains('is-prepared'), false, 'returning preference does not hide/replay old copy');
});
test('reveal: no observer or reduced preference never prepares offscreen content', () => {
  for (const options of [{observers:false}, {reduced:true}]) {
    const r = revealFixture(options); assert.equal(r.below.classList.contains('is-prepared'), false);
  }
});
test('reveal CSS: shipped override keeps prepared text opaque and focused/printed content immediate', () => {
  const css = read('motion.css');
  assert.match(css, /\.reveal,\.reveal\.is-prepared\s*\{\s*opacity:1;\s*translate:none;\s*transition:none;/);
  assert.doesNotMatch(css, /opacity\s*:\s*0(?:[;}]|\s)/);
  assert.match(css, /\.reveal\.is-prepared:focus-within\s*\{\s*transition:none;/);
  assert.match(css, /@media print\s*\{[\s\S]*opacity:1!important/);
});

function depthFixture(options = {}) {
  const e = environment(options), menu = e.el('dialog', {id:'site-menu'});
  const scene = e.el('section', {'data-depth-scene':''}), art = e.el('img', {'data-depth':'30','data-depth-turn':'2'});
  scene.rectangle = {...scene.rectangle, top:50, bottom:450}; scene.append(art);
  const tilt = e.el('figure', {'data-tilt':''}); e.doc.body.append(menu, scene, tilt); e.run('depth.js');
  const motion = e.matchMedia('(min-width: 900px) and (prefers-reduced-motion: no-preference)');
  const pointer = e.matchMedia('(hover: hover) and (pointer: fine)');
  return {...e, menu, scene, art, tilt, motion, pointer};
}
test('depth: coarse pointer or narrow/reduced viewport schedules no decorative geometry work', () => {
  for (const options of [{fine:false}, {wide:false}, {reduced:true}]) {
    const d = depthFixture(options); d.window.dispatch('scroll'); d.flushFrames();
    assert.equal(d.scene.rectangleReads, 0); assert.equal(d.frames.size, 0);
    assert.equal(d.art.style.getPropertyValue('--depth-y'), '0px');
  }
});
test('depth: changing reduced-motion or pointer availability cancels frames and resets transforms', () => {
  const d = depthFixture(); d.flushFrames(); assert.notEqual(d.art.style.getPropertyValue('--depth-y'), '0px');
  d.window.dispatch('scroll'); assert.equal(d.frames.size, 1); d.motion.change(false);
  assert.equal(d.frames.size, 0); assert.equal(d.art.style.getPropertyValue('--depth-y'), '0px');
  d.motion.change(true); d.flushFrames(); d.pointer.change(false);
  assert.equal(d.art.style.getPropertyValue('--depth-y'), '0px'); assert.equal(d.frames.size, 0);
  d.pointer.change(true); d.flushFrames(); assert.notEqual(d.art.style.getPropertyValue('--depth-y'), '0px');
});
test('depth: hidden document and open menu pause pending work; close/visibility resume once', () => {
  const d = depthFixture(); d.doc.hidden = true; d.doc.dispatch('visibilitychange');
  d.window.dispatch('scroll'); assert.equal(d.frames.size, 0);
  d.doc.hidden = false; d.doc.dispatch('visibilitychange'); d.flushFrames();
  d.menu.open = true; d.mutations[0].fn(); assert.equal(d.art.style.getPropertyValue('--depth-y'), '0px');
  d.window.dispatch('scroll'); assert.equal(d.frames.size, 0);
  d.menu.open = false; d.menu.dispatch('close'); assert.equal(d.frames.size, 1);
});
test('depth: touch never tilts; mouse tilt resets on cancel and hidden state', () => {
  const d = depthFixture(); d.flushFrames();
  d.tilt.dispatch('pointermove', {pointerType:'touch', clientX:350, clientY:20}); assert.equal(d.frames.size, 0);
  d.tilt.dispatch('pointermove', {pointerType:'mouse', clientX:350, clientY:20}); d.flushFrames();
  assert.notEqual(d.tilt.style.getPropertyValue('--tilt-x'), '0deg');
  d.tilt.dispatch('pointercancel'); d.flushFrames(); assert.equal(d.tilt.style.getPropertyValue('--tilt-lift'), '0px');
  d.doc.hidden = true; d.doc.dispatch('visibilitychange'); assert.equal(d.tilt.style.getPropertyValue('--tilt-x'), '0deg');
});
test('depth: product cards/details with CSS-disabled tilt have no listeners or measurement loop', () => {
  const d = environment();
  for (const className of ['product-card','product-detail']) {
    const host = d.el('article', {class:className}), tilt = d.el('span', {'data-tilt':''});
    host.append(tilt); d.doc.body.append(host);
  }
  d.run('depth.js'); d.window.dispatch('scroll'); d.flushFrames();
  assert.equal(d.frames.size, 0);
  for (const tilt of d.doc.querySelectorAll('[data-tilt]')) {
    assert.equal(tilt.listeners.size, 0); assert.equal(tilt.rectangleReads, 0);
  }
});

function attributes(text) {
  const result = {};
  for (const match of text.matchAll(/([^\s=<>/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) {
    result[match[1]] = match[2] ?? match[3] ?? match[4] ?? '';
  }
  return result;
}
function heroFixture() {
  const e = environment(), html = read('index.html');
  const carousel = e.el('section', {'data-product-carousel':''}), stage = e.el('div', {class:'product-stage'});
  const menu = e.el('dialog', {id:'site-menu'}), tablist = e.el('div', {role:'tablist'});
  stage.clientWidth = 1000; carousel.append(stage, tablist); e.doc.body.append(menu, carousel);
  const scenes = [...html.matchAll(/<article\b([^>]*\bclass="product-scene\s[^>]*?)>([\s\S]*?)<\/article>/g)].map(match => {
    const scene = e.el('article', attributes(match[1])); stage.append(scene);
    for (const image of match[2].matchAll(/<img\b([^>]*)>/g)) {
      const img = e.el('img', attributes(image[1])); img.gate = deferred(); img.decodeCalls = 0;
      img.decode = () => { img.decodeCalls++; return img.gate.promise; }; scene.append(img);
    }
    scene.append(e.el('a', {class:'product-scene-cta'})); return scene;
  });
  const picks = [...html.matchAll(/<button\b([^>]*\bdata-product-index="\d+"[^>]*)>/g)].map(match => {
    const pick = e.el('button', attributes(match[1])); tablist.append(pick); return pick;
  });
  assert.equal(scenes.length, 4, 'current generated hero has four manual panels'); assert.equal(picks.length, scenes.length);
  const next = e.el('button', {'data-product-next':''}), prev = e.el('button', {'data-product-prev':''});
  const announcement = e.el('p', {'data-product-announcement':''}); carousel.append(next, prev, announcement);
  const idle = []; e.window.requestIdleCallback = fn => idle.push(fn);
  const connection = new Events(); connection.saveData = false; connection.effectiveType = '4g';
  e.context.navigator.connection = connection; e.run('product-hero.js');
  const load = () => { e.doc.readyState = 'complete'; e.window.dispatch('load', {bubbles:false}); };
  const resolveScene = async (i, error = false) => {
    scenes[i].querySelectorAll('img').filter(img => img.decodeCalls).forEach(img => error ? img.gate.reject(new Error('decode failed')) : img.gate.resolve());
    await settle();
  };
  const active = () => scenes.findIndex(scene => scene.classList.contains('is-active'));
  const pending = i => scenes[i].querySelectorAll('img').some(img => img.decodeCalls);
  return {...e, carousel, stage, menu, picks, scenes, next, prev, announcement, idle, connection, load, resolveScene, active, pending};
}
test('hero: generated tab/panel pair contract, initial art has no entrance or autoplay', async () => {
  const h = heroFixture();
  h.scenes.forEach((scene, i) => {
    assert.equal(h.picks[i].getAttribute('aria-controls'), scene.getAttribute('id'));
    assert.equal(scene.getAttribute('aria-labelledby'), h.picks[i].getAttribute('id'));
    assert.equal(scene.classList.contains('is-user-selected'), false);
  });
  h.load(); h.idle.shift()(); await h.resolveScene(1);
  assert.equal(h.active(), 0); assert.equal(h.scenes[1].classList.contains('is-user-selected'), false);
});
test('hero: rapid keyboard navigation with out-of-order/error decode commits only latest request', async () => {
  const h = heroFixture(); h.picks[0].dispatch('keydown', {key:'ArrowRight'});
  h.picks[1].dispatch('keydown', {key:'ArrowRight'}); assert.equal(h.doc.activeElement, h.picks[2]);
  assert.equal(h.picks[2].focusCalls.at(-1).preventScroll, true);
  await h.resolveScene(2, true); await h.resolveScene(1);
  assert.equal(h.active(), 2); assert.equal(h.stage.getAttribute('aria-busy'), 'false');
  assert.equal(h.scenes.filter(scene => !scene.inert).length, 1);
  assert.equal(h.picks.filter(pick => pick.tabIndex === 0).length, 1);
  assert.ok(h.scenes[2].classList.contains('is-user-selected'));
  h.fireTimers(1500); await settle(); assert.equal(h.active(), 2);
});
test('hero: stalled art cannot block selected text/link beyond the deadline', async () => {
  const h = heroFixture(); h.next.dispatch('click'); assert.equal(h.active(), 0);
  assert.equal(h.stage.getAttribute('aria-busy'), 'true'); h.fireTimers(1500); await settle();
  assert.equal(h.active(), 1); assert.equal(h.stage.getAttribute('aria-busy'), 'false');
  assert.equal(h.scenes[1].inert, false); assert.equal(h.timers.size, 0);
  await h.resolveScene(1); assert.equal(h.active(), 1);
});
test('hero: decoded selection cancels deadline and never repeats entrance on same-tab selection', async () => {
  const h = heroFixture(); h.next.dispatch('click'); await h.resolveScene(1); assert.equal(h.timers.size, 0);
  let classChanges = 0; const toggle = h.scenes[1].classList.toggle;
  h.scenes[1].classList.toggle = (name, value) => { if (name === 'is-user-selected') classChanges++; return toggle(name, value); };
  h.picks[1].dispatch('click'); await settle(); assert.equal(classChanges, 0); assert.equal(h.timers.size, 0);
});
test('hero: queued idle rechecks saveData, slow connection, hidden state and menu before fetching', () => {
  for (const state of ['saveData','2g','hidden','menu']) {
    const h = heroFixture(); h.load(); assert.equal(h.idle.length, 1);
    if (state === 'saveData') h.connection.saveData = true;
    if (state === '2g') h.connection.effectiveType = '2g';
    if (state === 'hidden') h.doc.hidden = true;
    if (state === 'menu') h.menu.open = true;
    h.idle.shift()(); assert.equal(h.pending(1), false, state);
  }
});
test('hero: lifting data saver or closing menu resumes warm without selecting a panel', async () => {
  const h = heroFixture(); h.connection.saveData = true; h.load(); assert.equal(h.idle.length, 0);
  h.connection.saveData = false; h.connection.dispatch('change'); assert.equal(h.idle.length, 1);
  h.menu.open = true; h.idle.shift()(); h.menu.open = false; h.menu.dispatch('close');
  assert.equal(h.idle.length, 1); h.idle.shift()(); await h.resolveScene(1); assert.equal(h.active(), 0);
});
test('hero: a lost pointer capture cancels stale swipe; vertical gesture remains native', async () => {
  const h = heroFixture(); const start = {isPrimary:true, button:0, pointerId:1, clientX:300, clientY:100};
  h.stage.dispatch('pointerdown', start); h.stage.dispatch('lostpointercapture');
  h.stage.dispatch('pointerup', {pointerId:1, clientX:20, clientY:100}); assert.equal(h.pending(1), false);
  h.stage.dispatch('pointerdown', start);
  const up = h.stage.dispatch('pointerup', {pointerId:1, clientX:230, clientY:350});
  assert.equal(up.defaultPrevented, false); assert.equal(h.pending(1), false); await settle(); assert.equal(h.active(), 0);
});

#!/usr/bin/env node
'use strict';

// Run: node scripts/check_interactions.cjs [path/to/site]
// Builtins only. Uses real generated HTML for the relevant DOM topology and
// runs the shipped JavaScript in a VM. These tests do not model layout, network,
// screen readers or browser security policy; browser acceptance is separate.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const SITE = path.resolve(process.argv[2] || path.join(__dirname, '../output/concept'));
const read = name => fs.readFileSync(path.join(SITE, name), 'utf8');
const entity = value => value.replace(/&(?:amp|quot|lt|gt|apos|#39|#(\d+));/g, (all, number) =>
  number ? String.fromCodePoint(Number(number)) : ({'&amp;':'&','&quot;':'"','&lt;':'<','&gt;':'>','&apos;':"'",'&#39;':"'"}[all]));
function attrs(source) {
  const result = {};
  for (const match of source.matchAll(/([^\s=<>/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) {
    result[match[1]] = entity(match[2] ?? match[3] ?? match[4] ?? '');
  }
  return result;
}
const camel = name => name.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return {promise, resolve, reject};
};
async function settle() { for (let i = 0; i < 12; i++) await Promise.resolve(); }

class Node {
  constructor(tag = 'div', attributes = {}, document = null) {
    this.tagName = tag.toUpperCase(); this.attributes = {...attributes}; this.document = document;
    this.children = []; this.parent = null; this.listeners = new Map(); this.dataset = {};
    for (const [name, value] of Object.entries(attributes)) if (name.startsWith('data-')) this.dataset[camel(name.slice(5))] = value;
    this.hidden = 'hidden' in attributes; this.inert = 'inert' in attributes;
    this.tabIndex = Number(attributes.tabindex ?? -1); this.value = attributes.value || ''; this.checked = 'checked' in attributes;
    this.textContent = ''; this.style = {setProperty() {}}; this.focusCalls = [];
    const classes = new Set((attributes.class || '').split(/\s+/).filter(Boolean));
    this.classList = {
      contains: name => classes.has(name), add: name => classes.add(name), remove: name => classes.delete(name),
      toggle: (name, force = !classes.has(name)) => { if (force) classes.add(name); else classes.delete(name); return force; },
    };
  }
  append(...nodes) { for (const node of nodes) { this.children.push(node); node.parent = this; } }
  replaceChildren(...nodes) { this.children.forEach(node => { node.parent = null; }); this.children = []; this.append(...nodes); }
  contains(node) { for (; node; node = node.parent) if (node === this) return true; return false; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name] ?? null; }
  addEventListener(name, handler, options = {}) {
    if (!this.listeners.has(name)) this.listeners.set(name, []);
    this.listeners.get(name).push({handler, once: Boolean(options.once)});
  }
  removeEventListener(name, handler) { this.listeners.set(name, (this.listeners.get(name) || []).filter(item => item.handler !== handler)); }
  dispatch(name, properties = {}) {
    const event = {type:name, target:this, bubbles:true, defaultPrevented:false, preventDefault() { this.defaultPrevented = true; }, ...properties};
    for (let current = this; current; current = event.bubbles ? current.parent : null) {
      for (const entry of [...(current.listeners.get(name) || [])]) {
        if (entry.once) current.removeEventListener(name, entry.handler);
        entry.handler(event);
      }
    }
    return event;
  }
  matches(selector) {
    return selector.split(',').some(part => {
      part = part.trim();
      let excluded = false;
      part = part.replace(/:not\(([^)]+)\)/g, (_, inside) => { if (this.matches(inside)) excluded = true; return ''; });
      if (excluded) return false;
      if (part.endsWith(':checked')) { if (!this.checked) return false; part = part.slice(0, -8); }
      if (part.startsWith('#')) return this.attributes.id === part.slice(1);
      if (part.startsWith('.')) return this.classList.contains(part.slice(1));
      const attr = part.match(/^\[([^=\]]+)(?:=['"]?([^'"\]]+)['"]?)?\]$/);
      if (attr) return attr[1] in this.attributes && (attr[2] === undefined || this.attributes[attr[1]] === attr[2]);
      return this.tagName.toLowerCase() === part;
    });
  }
  closest(selector) { for (let node = this; node; node = node.parent) if (node.matches(selector)) return node; return null; }
  querySelectorAll(selector) {
    return this.children.flatMap(node => [...(node.matches(selector) ? [node] : []), ...node.querySelectorAll(selector)]);
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  focus(options) { this.focusCalls.push(options); if (this.document) this.document.activeElement = this; }
  select() { this.selectionMade = true; }
  setCustomValidity(message) { this.validationMessage = message; }
  setPointerCapture(id) { this.capturedPointer = id; }
}

function makeDocument() {
  const doc = new Node('document'); doc.document = doc; doc.body = new Node('body', {}, doc);
  doc.append(doc.body); doc.hidden = false; doc.readyState = 'loading'; doc.activeElement = doc.body;
  doc.createTextNode = text => Object.assign(new Node('#text', {}, doc), {textContent:text});
  doc.createElement = tag => new Node(tag, {}, doc);
  return doc;
}
function execute(filename, document, extras = {}) {
  const window = extras.window || new Node('window');
  const context = {
    document, window, navigator:{}, location:{search:'', href:'', hash:''},
    URLSearchParams, console, Promise, WeakMap, WeakSet, Map, Set, Date,
    scrollY:0, innerHeight:844, matchMedia:() => ({matches:true, addEventListener() {}}),
    addEventListener:window.addEventListener.bind(window), requestAnimationFrame:fn => fn(), ...extras,
  };
  vm.runInNewContext(read(filename), context, {filename:path.join(SITE, filename)});
  return context;
}

function cityFixture({clipboard, query = ''} = {}) {
  const html = read('where-to-buy.html'); const doc = makeDocument();
  const formMatch = html.match(/<form\b([^>]*\bid="city-form"[^>]*)>([\s\S]*?)<\/form>/);
  const selectMatch = html.match(/<select\b([^>]*\bid="wanted-product"[^>]*)>([\s\S]*?)<\/select>/);
  assert.ok(formMatch && selectMatch, 'generated city form and product select exist');
  const form = new Node('form', attrs(formMatch[1]), doc); doc.body.append(form);
  const wanted = new Node('select', attrs(selectMatch[1]), doc);
  wanted.options = [...selectMatch[2].matchAll(/<option\b([^>]*)>([\s\S]*?)<\/option>/g)]
    .map(match => ({value:attrs(match[1]).value || '', text:entity(match[2].replace(/<[^>]*>/g, ''))}));
  Object.defineProperty(wanted, 'selectedOptions', {get:() => wanted.options.filter(option => option.value === wanted.value)});
  // form= associates submission/validation, but never changes DOM ancestry.
  const external = selectMatch.index < formMatch.index || selectMatch.index > formMatch.index + formMatch[0].length;
  (external ? doc.body : form).append(wanted);
  const cityTag = formMatch[2].match(/<input\b([^>]*\bid="city"[^>]*)>/);
  assert.ok(cityTag, 'city input belongs to form');
  const city = new Node('input', attrs(cityTag[1]), doc); form.append(city);
  const copyTag = html.match(/<button\b([^>]*\bdata-city-copy[^>]*)>/);
  const draftTag = html.match(/<textarea\b([^>]*\bdata-city-draft[^>]*)>/);
  const feedbackTag = html.match(/<p\b([^>]*\bclass="form-feedback"[^>]*)>/);
  assert.ok(copyTag && draftTag && feedbackTag, 'copy, draft and live feedback contract exists');
  const copy = new Node('button', attrs(copyTag[1]), doc); form.append(copy);
  const draft = new Node('textarea', attrs(draftTag[1]), doc); doc.body.append(draft);
  const feedback = new Node('p', attrs(feedbackTag[1]), doc); doc.body.append(feedback);
  form.reportValidity = () => { form.validationCount = (form.validationCount || 0) + 1; return Boolean(city.value && !city.validationMessage); };
  const navigation = []; const location = {search:query, get href() { return navigation.at(-1) || ''; }, set href(value) { navigation.push(value); }};
  execute('script.js', doc, {navigator:clipboard ? {clipboard} : {}, location});
  return {doc, form, wanted, city, copy, draft, feedback, navigation, external, location};
}

function partnerFixture({clipboard} = {}) {
  const html = read('partners.html'); const doc = makeDocument();
  const formMatch = html.match(/<form\b([^>]*\bid="partner-request-form"[^>]*)>([\s\S]*?)<\/form>/);
  assert.ok(formMatch, 'generated partner form exists');
  const form = new Node('form', attrs(formMatch[1]), doc); doc.body.append(form);
  const fields = [...formMatch[2].matchAll(/<(input|textarea)\b([^>]*)>/g)].map(match => {
    const field = new Node(match[1], attrs(match[2]), doc); form.append(field); return field;
  });
  const feedbackTag = html.match(/<p\b([^>]*\bid="partner-request-feedback"[^>]*)>/);
  const helpTag = html.match(/<p\b([^>]*\bid="partner-format-help"[^>]*)>/);
  const copyTag = html.match(/<button\b([^>]*\bid="partner-copy-request"[^>]*)>/);
  assert.ok(feedbackTag && helpTag && copyTag);
  const feedback = new Node('p', attrs(feedbackTag[1]), doc); form.append(feedback);
  const help = new Node('p', attrs(helpTag[1]), doc); form.append(help);
  const copy = new Node('button', attrs(copyTag[1]), doc); form.append(copy);
  const links = [...html.matchAll(/<a\b([^>]*\bdata-partner-format[^>]*)>/g)].map(match => {
    const link = new Node('a', attrs(match[1]), doc); doc.body.append(link); return link;
  });
  const draft = fields.find(field => field.attributes.id === 'partner-request-draft');
  const company = fields.find(field => field.attributes.name === 'company');
  const contact = fields.find(field => field.attributes.name === 'contact');
  const radios = fields.filter(field => field.attributes.type === 'radio');
  form.reportValidity = () => fields.filter(field => 'required' in field.attributes).every(field => field.value && !field.validationMessage);
  class FormData {
    constructor(target) { assert.equal(target, form); }
    entries() { return fields.filter(field => field.attributes.name && (field.attributes.type !== 'radio' || field.checked)).map(field => [field.attributes.name, field.value]); }
  }
  const navigation = []; const location = {set href(value) { navigation.push(value); }}; const window = new Node('window'); window.location = location;
  execute('partners-scenes.js', doc, {window, location, FormData, navigator:clipboard ? {clipboard} : {}});
  const valid = () => { company.value = 'Тестовая компания'; contact.value = 'audit@example.com'; };
  return {doc, form, fields, company, contact, radios, feedback, help, copy, draft, links, navigation, valid};
}

function popsyHeroFixture({reducedMotion = false, pointerFine = true, boot = true, pendingImages = false} = {}) {
  const html = read('index.html'); const doc = makeDocument(); doc.readyState = 'complete';
  const match = html.match(/<section\b([^>]*\bdata-popsy-hero\b[^>]*)>([\s\S]*?)<\/section>/);
  assert.ok(match, 'generated Popсы hero exists');
  const hero = new Node('section', attrs(match[1]), doc); doc.body.append(hero);
  const nodes = [hero], stack = [hero];
  const voidTags = new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
  // Build this section's actual nested markup; no synthetic carousel controls.
  for (const token of match[2].match(/<[^>]+>|[^<]+/g) || []) {
    const closing = token.match(/^<\/([\w:-]+)/);
    if (closing) { if (stack.length > 1) stack.pop(); continue; }
    const opening = token.match(/^<([a-z][\w:-]*)\b([^>]*)>/i);
    if (opening) {
      const node = new Node(opening[1], attrs(opening[2]), doc); stack.at(-1).append(node); nodes.push(node);
      if (opening[1].toLowerCase() === 'img') {
        node.complete = true; node.naturalWidth = Number(node.getAttribute('width')) || 800;
        node.decode = () => pendingImages ? new Promise(() => {}) : Promise.resolve();
      }
      if (!voidTags.has(opening[1].toLowerCase()) && !token.endsWith('/>')) stack.push(node);
    } else if (!token.startsWith('<')) {
      for (const node of stack) node.textContent += entity(token);
    }
  }
  const styles = new Map();
  for (const node of nodes) {
    const values = new Map(); styles.set(node, values);
    node.style = new Proxy({
      setProperty(name, value) { values.set(name, String(value)); },
      getPropertyValue(name) { return values.get(name) || ''; },
      removeProperty(name) { const previous = values.get(name) || ''; values.delete(name); return previous; },
    }, {set(target, name, value) { values.set(name, String(value)); target[name] = value; return true; }});
    node.getBoundingClientRect = () => ({left:0, top:0, right:1440, bottom:900, width:1440, height:900});
  }
  const window = new Node('window'), media = new Map(), frames = new Map(), timers = new Map(); let taskId = 0;
  const matchMedia = query => {
    if (!media.has(query)) {
      const result = new Node('media'); result.media = query;
      result.matches = /prefers-reduced-motion/.test(query) ? reducedMotion : /pointer|hover/.test(query) ? pointerFine : false;
      result.addListener = callback => result.addEventListener('change', callback);
      result.removeListener = callback => result.removeEventListener('change', callback);
      media.set(query, result);
    }
    return media.get(query);
  };
  const requestAnimationFrame = callback => { const id = ++taskId; frames.set(id, callback); return id; };
  const cancelAnimationFrame = id => frames.delete(id);
  const setTimeout = callback => { const id = ++taskId; timers.set(id, callback); return id; };
  const clearTimeout = id => timers.delete(id);
  Object.assign(window, {matchMedia, requestAnimationFrame, cancelAnimationFrame, setTimeout, clearTimeout});
  doc.fonts = {ready:Promise.resolve()};
  if (boot) execute('popsy-home.js', doc, {window, matchMedia, requestAnimationFrame, cancelAnimationFrame, setTimeout, clearTimeout, performance:{now:() => 0}});
  const flushFrames = (count = 2) => {
    for (let i = 0; i < count && frames.size; i++) {
      const batch = [...frames];
      for (const [id, callback] of batch) { frames.delete(id); callback((i + 1) * 16); }
    }
  };
  const ready = () => hero.getAttribute('data-ready') !== null || hero.dataset.ready !== undefined;
  const styleSnapshot = () => nodes.map(node => [...styles.get(node)].sort((a, b) => a[0].localeCompare(b[0])));
  return {doc, window, hero, nodes, frames, timers, flushFrames, ready, styleSnapshot, cta:hero.querySelector('.popsy-home-cta')};
}

test('city: generated copy/manual controls retain their HTML contract', () => {
  const c = cityFixture();
  assert.equal(c.copy.getAttribute('type'), 'button');
  assert.ok('readonly' in c.draft.attributes); assert.ok(c.draft.hidden);
  assert.equal(c.feedback.getAttribute('role'), 'status');
});
test('city: known product query preset; unknown values are ignored', () => {
  const products = cityFixture().wanted.options.filter(option => option.value);
  assert.ok(products.length);
  for (const product of products) {
    assert.equal(cityFixture({query:`?product=${encodeURIComponent(product.value)}`}).wanted.value, product.value);
  }
  assert.equal(cityFixture({query:'?product=not-an-approved-product'}).wanted.value, '');
});
test('city: whitespace fails native validity and does not navigate', () => {
  const c = cityFixture(); c.city.value = '   '; c.form.dispatch('submit');
  assert.equal(c.city.validationMessage, 'Укажите город'); assert.equal(c.navigation.length, 0);
});
test('city: submit prepares current city/product and edit clears stale retry', () => {
  const c = cityFixture(); c.city.value = '  Москва  '; c.wanted.value = c.wanted.options[1].value;
  c.form.dispatch('submit'); const body = new URL(c.navigation[0]).searchParams.get('body');
  assert.ok(body.includes('Город: Москва\n')); assert.ok(body.includes(c.wanted.selectedOptions[0].text));
  assert.equal(c.feedback.hidden, false);
  c.city.value = 'Казань'; c.city.dispatch('input'); assert.equal(c.feedback.hidden, true); assert.equal(c.feedback.children.length, 0);
});
test('city: external product select change clears old retry despite form association', () => {
  const c = cityFixture(); c.city.value = 'Москва'; c.form.dispatch('submit');
  c.wanted.value = c.wanted.options[1].value; c.wanted.dispatch('change');
  assert.equal(c.feedback.hidden, true, `product events must reset feedback (external select: ${c.external})`);
  assert.equal(c.feedback.children.length, 0);
});
test('city: clipboard success never navigates or sends; uses current request', async () => {
  const writes = []; const c = cityFixture({clipboard:{writeText:async text => writes.push(text)}});
  c.city.value = 'Казань'; c.copy.dispatch('click'); await settle();
  assert.equal(writes.length, 1); assert.ok(writes[0].includes('Город: Казань'));
  assert.equal(c.navigation.length, 0); assert.equal(c.feedback.hidden, false); assert.equal(c.draft.hidden, true);
});
test('city: unavailable/rejected clipboard exposes selected manual draft', async () => {
  for (const clipboard of [undefined, {writeText:async() => { throw new Error('denied'); }}]) {
    const c = cityFixture({clipboard}); c.city.value = 'Самара'; c.copy.dispatch('click'); await settle();
    assert.equal(c.draft.hidden, false); assert.ok(c.draft.value.includes('Самара')); assert.equal(c.draft.selectionMade, true);
    assert.equal(c.doc.activeElement, c.draft); assert.equal(c.navigation.length, 0);
    c.wanted.value = c.wanted.options[1].value; c.wanted.dispatch('input');
    assert.equal(c.draft.hidden, true); assert.equal(c.draft.value, ''); assert.equal(c.feedback.hidden, true);
  }
});
test('city: product edit while clipboard is pending suppresses stale success or failure', async () => {
  for (const reject of [false, true]) {
    const gate = deferred(); const c = cityFixture({clipboard:{writeText:() => gate.promise}});
    c.city.value = 'Омск'; c.copy.dispatch('click'); c.wanted.value = c.wanted.options[1].value; c.wanted.dispatch('change');
    if (reject) gate.reject(new Error('denied')); else gate.resolve(); await settle();
    assert.equal(c.feedback.hidden, true); assert.equal(c.draft.hidden, true);
  }
});
test('partners: valid copy contains current form data and never navigates', async () => {
  const writes = []; const p = partnerFixture({clipboard:{writeText:async body => writes.push(body)}}); p.valid();
  p.copy.dispatch('click'); await settle();
  assert.equal(writes.length, 1); assert.ok(writes[0].includes('Тестовая компания')); assert.ok(writes[0].includes('audit@example.com'));
  assert.equal(p.navigation.length, 0); assert.equal(p.feedback.hidden, false); assert.equal(p.draft.hidden, true);
});
test('partners: blank or whitespace required fields prevent copy', async () => {
  const writes = []; const p = partnerFixture({clipboard:{writeText:async body => writes.push(body)}});
  p.company.value = '   '; p.contact.value = 'audit@example.com'; p.copy.dispatch('click'); await settle();
  assert.equal(writes.length, 0); assert.ok(p.company.validationMessage); assert.equal(p.feedback.hidden, true);
});
test('partners: manual draft is selected, then field change clears draft and stale retry', async () => {
  const p = partnerFixture(); p.valid(); p.copy.dispatch('click'); await settle();
  assert.equal(p.draft.hidden, false); assert.equal(p.draft.selectionMade, true);
  p.company.value = 'Новая компания'; p.company.dispatch('change');
  assert.equal(p.draft.hidden, true); assert.equal(p.draft.value, ''); assert.equal(p.feedback.hidden, true);
  p.form.dispatch('submit'); assert.equal(p.feedback.hidden, false); assert.equal(p.navigation.length, 1);
  p.company.dispatch('input'); assert.equal(p.feedback.hidden, true); assert.equal(p.feedback.children.length, 0);
});
test('partners: field/radio/format-link edit cancels pending clipboard success and failure', async () => {
  for (const edit of ['field', 'radio', 'link']) for (const reject of [false, true]) {
    const gate = deferred(); const p = partnerFixture({clipboard:{writeText:() => gate.promise}}); p.valid(); p.copy.dispatch('click');
    if (edit === 'field') { p.company.value = 'Новая компания'; p.company.dispatch('input'); }
    else if (edit === 'radio') { p.radios.forEach((radio, i) => { radio.checked = i === 1; }); p.radios[1].dispatch('change'); }
    else { assert.ok(p.links.length); p.links[0].dispatch('click'); }
    if (reject) gate.reject(new Error('denied')); else gate.resolve(); await settle();
    assert.equal(p.feedback.hidden, true, edit); assert.equal(p.draft.hidden, true, edit);
  }
});
test('popsy hero: title, artwork and product link are available before enhancement', () => {
  const h = popsyHeroFixture({boot:false});
  const title = h.hero.querySelector('#popsy-home-title');
  assert.equal(title?.tagName, 'H1'); assert.equal(title.textContent.trim().toLocaleLowerCase('ru'), 'попсы');
  for (const className of ['.popsy-home-pack', '.popsy-home-food']) {
    const image = h.hero.querySelector(className);
    assert.equal(image?.tagName, 'IMG'); assert.ok(image.getAttribute('src').startsWith('assets/popsy-home/'));
    assert.ok(!image.getAttribute('data-src')); assert.notEqual(image.getAttribute('loading'), 'lazy');
  }
  assert.ok(h.cta); assert.equal(h.cta.getAttribute('href'), 'product-popsy.html');
  assert.equal(h.cta.dispatch('click').defaultPrevented, false);
  assert.ok(!h.hero.hidden && !h.hero.inert && !title.hidden && !title.inert && !h.cta.hidden && !h.cta.inert);
});
test('popsy hero: enhancement starts safely across pointer and motion preferences', async () => {
  for (const reducedMotion of [false, true]) for (const pointerFine of [false, true]) {
    const h = popsyHeroFixture({reducedMotion, pointerFine});
    await settle(); h.flushFrames(); await settle(); h.flushFrames();
    assert.ok(h.ready(), `hero enhancement initializes (reduced motion: ${reducedMotion}, fine pointer: ${pointerFine})`);
    assert.equal(h.cta.getAttribute('href'), 'product-popsy.html');
    assert.equal(h.cta.dispatch('click').defaultPrevented, false, 'the product link retains native navigation');
  }
});
test('popsy hero: reduced motion keeps pointer movement still and the CTA usable', async () => {
  const h = popsyHeroFixture({reducedMotion:true, pointerFine:true});
  await settle(); h.flushFrames(); await settle(); h.flushFrames();
  const before = h.styleSnapshot();
  h.hero.dispatch('pointerenter', {clientX:1200, clientY:500, pointerType:'mouse'});
  h.hero.dispatch('pointermove', {clientX:1200, clientY:500, pointerType:'mouse'});
  h.flushFrames();
  assert.deepEqual(h.styleSnapshot(), before, 'reduced-motion users receive no pointer parallax');
  h.cta.focus(); assert.equal(h.doc.activeElement, h.cta);
  assert.equal(h.cta.dispatch('click').defaultPrevented, false);
});
test('popsy hero: a stalled image decode cannot leave the entrance waiting indefinitely', async () => {
  const h = popsyHeroFixture({pendingImages:true});
  await settle(); h.flushFrames();
  assert.ok(h.timers.size, 'entrance has a bounded fallback when image decoding stalls');
  for (const callback of [...h.timers.values()]) callback();
  h.flushFrames();
  assert.ok(h.ready(), 'hero is revealed even if artwork decoding never resolves');
  assert.equal(h.cta.getAttribute('href'), 'product-popsy.html');
});
test('popsy hero: shared enhancement script is harmless on pages without the hero', () => {
  const doc = makeDocument();
  assert.doesNotThrow(() => execute('popsy-home.js', doc));
});

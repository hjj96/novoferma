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
const {webcrypto} = require('node:crypto');
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
    this.hidden = 'hidden' in attributes; this.inert = 'inert' in attributes; this.disabled = 'disabled' in attributes;
    this.tabIndex = Number(attributes.tabindex ?? -1); this.value = attributes.value || ''; this.checked = 'checked' in attributes;
    this.textContent = ''; this.style = {setProperty() {}}; this.focusCalls = []; this.scrollCalls = [];
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
      let attributesMatch = true;
      part = part.replace(/\[([^=\]]+)(?:=['"]?([^'"\]]+)['"]?)?\]/g, (_, name, value) => {
        if (!(name in this.attributes) || (value !== undefined && this.attributes[name] !== value)) attributesMatch = false;
        return '';
      });
      return attributesMatch && (!part || this.tagName.toLowerCase() === part);
    });
  }
  closest(selector) { for (let node = this; node; node = node.parent) if (node.matches(selector)) return node; return null; }
  querySelectorAll(selector) {
    return this.children.flatMap(node => [...(node.matches(selector) ? [node] : []), ...node.querySelectorAll(selector)]);
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  focus(options) { this.focusCalls.push(options); if (this.document) this.document.activeElement = this; }
  scrollIntoView(options) { this.scrollCalls.push(options); }
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

function partnerFixture({clipboard, query = '', fetch:fetchImplementation, crypto = webcrypto} = {}) {
  const html = read('partners.html'); const doc = makeDocument();
  const formMatch = html.match(/<form\b([^>]*\bid="partner-request-form"[^>]*)>([\s\S]*?)<\/form>/);
  assert.ok(formMatch, 'generated partner form exists');
  const form = new Node('form', attrs(formMatch[1]), doc); doc.body.append(form);
  const fields = [...formMatch[2].matchAll(/<(input|textarea)\b([^>]*)>/g)].map(match => {
    const field = new Node(match[1], attrs(match[2]), doc); form.append(field); return field;
  });
  for (const match of formMatch[2].matchAll(/<select\b([^>]*)>([\s\S]*?)<\/select>/g)) {
    const select = new Node('select', attrs(match[1]), doc);
    select.options = [...match[2].matchAll(/<option\b([^>]*)>([\s\S]*?)<\/option>/g)].map(option => {
      const attributes = attrs(option[1]);
      return {value:attributes.value || '', textContent:entity(option[2].replace(/<[^>]*>/g, '')), selected:'selected' in attributes};
    });
    select.value = select.options.find(option => option.selected)?.value ?? select.options[0]?.value ?? '';
    Object.defineProperty(select, 'selectedOptions', {get:() => select.options.filter(option => option.value === select.value)});
    fields.push(select); form.append(select);
  }
  const feedbackTag = html.match(/<p\b([^>]*\bid="partner-request-feedback"[^>]*)>/);
  const helpTag = html.match(/<p\b([^>]*\bid="partner-format-help"[^>]*)>/);
  const copyTag = html.match(/<button\b([^>]*\bid="partner-copy-request"[^>]*)>/);
  const submitTag = formMatch[2].match(/<button\b([^>]*\btype="submit"[^>]*)>/);
  const emailTag = html.match(/<a\b([^>]*\bid="partner-email-request"[^>]*)>/);
  assert.ok(feedbackTag && helpTag && copyTag && submitTag && emailTag, 'generated partner feedback and submit/copy/mail controls exist');
  const feedback = new Node('p', attrs(feedbackTag[1]), doc); form.append(feedback);
  const help = new Node('p', attrs(helpTag[1]), doc); form.append(help);
  const copy = new Node('button', attrs(copyTag[1]), doc); form.append(copy);
  const submit = new Node('button', attrs(submitTag[1]), doc); form.append(submit);
  const email = new Node('a', attrs(emailTag[1]), doc); form.append(email);
  const links = [...html.matchAll(/<a\b([^>]*\bdata-partner-format[^>]*)>/g)].map(match => {
    const link = new Node('a', attrs(match[1]), doc); doc.body.append(link); return link;
  });
  const draft = fields.find(field => field.attributes.id === 'partner-request-draft');
  const company = fields.find(field => field.attributes.name === 'company');
  const contact = fields.find(field => field.attributes.name === 'contact');
  const consent = fields.find(field => field.attributes.name === 'consent');
  const product = fields.find(field => field.attributes.name === 'product');
  const intent = fields.find(field => field.attributes.name === 'intent');
  const radios = fields.filter(field => field.attributes.type === 'radio');
  assert.ok(product && intent && consent, 'generated product/intent selects and consent checkbox exist');
  for (const radio of radios) {
    radio._checked = radio.checked;
    Object.defineProperty(radio, 'checked', {get:() => radio._checked, set:value => {
      radio._checked = value;
      if (value) radios.filter(other => other !== radio).forEach(other => { other._checked = false; });
    }});
  }
  form.reportValidity = () => {
    form.validationCount = (form.validationCount || 0) + 1;
    return fields.filter(field => !field.disabled).every(field => !field.validationMessage &&
      (!('required' in field.attributes) || (field.attributes.type === 'checkbox' ? field.checked : field.value)) &&
      (!field.attributes.maxlength || field.value.length <= Number(field.attributes.maxlength)));
  };
  const requests = []; const timers = new Map(); let timerId = 0;
  const fetch = (url, options) => {
    const request = {url, options, body:JSON.parse(options.body)}; requests.push(request);
    return fetchImplementation ? fetchImplementation(request, requests.length) : Promise.reject(new Error('offline fixture'));
  };
  const navigation = []; const location = {search:query, set href(value) { navigation.push(value); }};
  const window = new Node('window'); window.location = location;
  window.setTimeout = (fn, ms) => { timers.set(++timerId, {fn, ms}); return timerId; };
  window.clearTimeout = id => timers.delete(id);
  execute('partners-scenes.js', doc, {window, location, crypto, fetch, AbortController, navigator:clipboard ? {clipboard} : {}});
  const valid = () => { company.value = 'Тестовая компания'; contact.value = 'audit@example.com'; consent.checked = true; };
  const message = () => feedback.children.map(node => node.textContent).join('');
  return {doc, form, fields, company, contact, consent, product, intent, radios, feedback, help, copy, submit, email, draft, links, navigation, valid, requests, timers, message};
}

class ImageNode extends Node {
  constructor(attributes, document) {
    super('img', attributes, document); this.writes = []; this.gate = deferred(); this.decodeCalls = 0;
    for (const key of ['src', 'srcset', 'sizes']) {
      this[`_${key}`] = attributes[key] || '';
      Object.defineProperty(this, key, {get:() => this[`_${key}`], set:value => { this.writes.push(key); this[`_${key}`] = value; }});
    }
  }
  decode() { this.decodeCalls++; return this.gate.promise; }
}
function heroFixture({saveData = false, effectiveType = '4g', hidden = false, idleApi = true} = {}) {
  const html = read('index.html'); const doc = makeDocument(); doc.hidden = hidden;
  const carouselTag = html.match(/<section\b([^>]*\bdata-product-carousel[^>]*)>/);
  assert.ok(carouselTag, 'carousel markup exists');
  const carousel = new Node('section', attrs(carouselTag[1]), doc); doc.body.append(carousel);
  const stage = new Node('div', {class:'product-stage'}, doc); stage.clientWidth = 1200; carousel.append(stage);
  const tablist = new Node('div', {role:'tablist'}, doc); carousel.append(tablist);
  const scenes = [...html.matchAll(/<article\b([^>]*\bclass="product-scene\s[^>]*?)>([\s\S]*?)<\/article>/g)].map(match => {
    const scene = new Node('article', attrs(match[1]), doc); stage.append(scene);
    for (const img of match[2].matchAll(/<img\b([^>]*)>/g)) scene.append(new ImageNode(attrs(img[1]), doc));
    scene.append(new Node('a', {class:'product-scene-cta'}, doc));
    return scene;
  });
  const picks = [...html.matchAll(/<button\b([^>]*\bdata-product-index="\d+"[^>]*)>/g)].map(match => {
    const pick = new Node('button', attrs(match[1]), doc); tablist.append(pick); return pick;
  });
  assert.ok(scenes.length > 1); assert.equal(scenes.length, picks.length);
  const prev = new Node('button', {'data-product-prev':''}, doc); carousel.append(prev);
  const next = new Node('button', {'data-product-next':''}, doc); carousel.append(next);
  const announcement = new Node('p', {'data-product-announcement':''}, doc); carousel.append(announcement);
  const window = new Node('window'); const idle = []; const timers = [];
  if (idleApi) window.requestIdleCallback = fn => idle.push(fn);
  window.setTimeout = (fn, ms) => timers.push({fn, ms});
  execute('product-hero.js', doc, {window, navigator:{connection:{saveData,effectiveType}}});
  const pending = index => scenes[index].querySelectorAll('img').filter(image => image.decodeCalls);
  async function resolveScene(index, error = false) {
    pending(index).forEach(image => error ? image.gate.reject(new Error('simulated decode failure')) : image.gate.resolve());
    await settle();
  }
  const active = () => scenes.findIndex(scene => scene.classList.contains('is-active'));
  const load = () => { doc.readyState = 'complete'; window.dispatch('load', {bubbles:false}); };
  return {doc, carousel, stage, scenes, picks, prev, next, announcement, idle, timers, pending, resolveScene, active, load};
}

test('city: generated copy/manual controls retain their HTML contract', () => {
  const c = cityFixture();
  assert.equal(c.copy.getAttribute('type'), 'button');
  assert.ok('readonly' in c.draft.attributes); assert.ok(c.draft.hidden);
  assert.equal(c.feedback.getAttribute('role'), 'status');
});
test('city: known product query preset; unknown values are ignored', () => {
  const example = cityFixture().wanted.options.find(option => option.value);
  assert.ok(example);
  assert.equal(cityFixture({query:`?product=${encodeURIComponent(example.value)}`}).wanted.value, example.value);
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
  p.form.dispatch('submit'); await settle(); assert.equal(p.feedback.hidden, false); assert.equal(p.navigation.length, 0);
  assert.equal(p.requests.length, 1); assert.match(p.message(), /не подтверждено/);
  p.company.dispatch('input'); assert.equal(p.feedback.hidden, true); assert.equal(p.feedback.children.length, 0);
});
test('partners: field/radio/format-link edit cancels pending clipboard success and failure', async () => {
  for (const edit of ['field', 'radio', 'link', 'product', 'intent', 'consent', 'reset']) for (const reject of [false, true]) {
    const gate = deferred(); const p = partnerFixture({clipboard:{writeText:() => gate.promise}}); p.valid(); p.copy.dispatch('click');
    if (edit === 'field') { p.company.value = 'Новая компания'; p.company.dispatch('input'); }
    else if (edit === 'radio') { p.radios.forEach((radio, i) => { radio.checked = i === 1; }); p.radios[1].dispatch('change'); }
    else if (edit === 'link') { assert.ok(p.links.length); p.links[0].dispatch('click'); }
    else if (edit === 'reset') p.form.dispatch('reset');
    else { p[edit].dispatch('change'); }
    if (reject) gate.reject(new Error('denied')); else gate.resolve(); await settle();
    assert.equal(p.feedback.hidden, true, edit); assert.equal(p.draft.hidden, true, edit);
  }
});
const REQUEST_ID = 'b0e021a3-6a75-4b97-bf15-e73a9efc730c';
const receipt = duplicate => ({ok:true, committed:true, requestId:REQUEST_ID, duplicate});
const apiResponse = (status, body) => ({status, ok:status >= 200 && status < 300, json:async() => body});
test('partners: generated controls expose consent, taxonomy and bounded fields', () => {
  const p = partnerFixture();
  assert.equal(p.consent.getAttribute('type'), 'checkbox'); assert.ok('required' in p.consent.attributes);
  assert.equal(p.consent.checked, false); assert.equal(p.feedback.getAttribute('role'), 'status');
  assert.equal(p.copy.getAttribute('type'), 'button'); assert.equal(p.submit.getAttribute('type'), 'submit');
  assert.equal(p.intent.options.map(option => option.value).sort().join(','), 'quote,samples,specification,stm');
  assert.equal(p.product.options.length, 17, '14 catalogue + 2 concepts + no selection');
  for (const [name, max] of [['company',120],['city',100],['contact',160],['message',1200]]) {
    assert.equal(Number(p.fields.find(field => field.attributes.name === name).getAttribute('maxlength')), max);
  }
});
test('partners: query prefill accepts only existing taxonomy; never personal data or consent', () => {
  const example = partnerFixture().product.options.find(option => option.value).value;
  const p = partnerFixture({query:`?format=stm&product=${encodeURIComponent(example)}&intent=samples&company=secret&contact=leak%40example.com&consent=true`});
  assert.equal(p.product.value, example); assert.equal(p.intent.value, 'samples');
  assert.equal(p.radios.find(radio => radio.checked).value, 'stm'); assert.match(p.help.textContent, /вашим брендом/);
  assert.equal(p.company.value, ''); assert.equal(p.contact.value, ''); assert.equal(p.consent.checked, false);
  assert.equal(p.requests.length, 0);
  const invalid = partnerFixture({query:'?format=unknown&product=%3Cscript%3E&intent=unsupported'});
  assert.equal(invalid.product.value, ''); assert.equal(invalid.intent.value, 'quote');
  assert.equal(invalid.radios.find(radio => radio.checked).value, 'retail');
});
test('partners: whitespace, missing consent and over-limit fields never POST', async () => {
  for (const issue of ['blank','consent','length']) {
    const p = partnerFixture(); p.valid();
    if (issue === 'blank') p.company.value = '   ';
    else if (issue === 'consent') p.consent.checked = false;
    else p.company.value = 'a'.repeat(121);
    p.form.dispatch('submit'); await settle();
    assert.equal(p.requests.length, 0, issue); assert.equal(p.submit.disabled, false);
  }
});
test('partners: format links update locally without reloading or clearing product, intent or personal fields', () => {
  const p = partnerFixture(); p.valid(); p.product.value = p.product.options[1].value; p.intent.value = 'samples';
  const chosenProduct = p.product.value;
  const link = p.links.find(link => link.dataset.partnerFormat === 'horeca'); assert.ok(link);
  const event = link.dispatch('click');
  assert.equal(event.defaultPrevented, true, 'query-bearing link must never reload this populated form');
  assert.equal(p.radios.find(radio => radio.checked).value, 'horeca');
  assert.equal(p.product.value, chosenProduct); assert.equal(p.intent.value, 'samples');
  assert.equal(p.company.value, 'Тестовая компания'); assert.equal(p.contact.value, 'audit@example.com'); assert.equal(p.consent.checked, true);
  assert.equal(p.form.scrollCalls.length, 1); assert.equal(p.form.scrollCalls[0].behavior, 'auto');
  assert.equal(p.doc.activeElement, p.radios.find(radio => radio.checked)); assert.equal(p.doc.activeElement.focusCalls.at(-1).preventScroll, true);
  assert.equal(p.navigation.length, 0); assert.equal(p.requests.length, 0);
});
test('partners: explicit link intent is allowlisted, while unspecified or unknown intent is preserved', () => {
  const p = partnerFixture(); p.valid(); p.product.value = p.product.options[1].value; p.intent.value = 'samples';
  const chosenProduct = p.product.value;
  const link = p.links.find(link => link.dataset.partnerIntent === 'specification'); assert.ok(link, 'materials link declares its intent');
  assert.equal(link.dispatch('click').defaultPrevented, true);
  assert.equal(p.intent.value, 'specification'); assert.equal(p.product.value, chosenProduct); assert.equal(p.company.value, 'Тестовая компания');
  link.dataset.partnerIntent = 'unknown'; link.dispatch('click'); assert.equal(p.intent.value, 'specification');
  delete link.dataset.partnerIntent; link.dispatch('click'); assert.equal(p.intent.value, 'specification');
  assert.equal(p.requests.length, 0); assert.equal(p.navigation.length, 0);
});
test('partners: pending locks controls, blocks duplicate submit and fallbacks, then preserves data on failure', async () => {
  const gate = deferred(); let copied = false;
  const p = partnerFixture({fetch:() => gate.promise, clipboard:{writeText:async() => { copied = true; }}}); p.valid();
  p.form.dispatch('submit'); p.form.dispatch('submit'); p.copy.dispatch('click');
  assert.equal(p.links.find(link => link.dataset.partnerFormat === 'horeca').dispatch('click').defaultPrevented, true);
  assert.equal(p.radios.find(radio => radio.checked).value, 'retail'); assert.equal(p.form.scrollCalls.length, 0);
  assert.equal(p.email.dispatch('click').defaultPrevented, true);
  assert.equal(p.form.dispatch('reset').defaultPrevented, true);
  assert.equal(p.requests.length, 1); assert.equal(p.submit.disabled, true); assert.equal(p.company.disabled, true);
  assert.equal(p.form.getAttribute('aria-busy'), 'true'); assert.equal(p.email.getAttribute('aria-disabled'), 'true');
  assert.match(p.message(), /Дождитесь подтверждения/); assert.equal(copied, false);
  const sent = p.requests[0];
  assert.equal(sent.url, '/api/partner-requests'); assert.equal(sent.options.method, 'POST');
  assert.equal(sent.options.mode, 'same-origin'); assert.equal(sent.options.credentials, 'omit');
  assert.equal(sent.options.headers['Content-Type'], 'application/json'); assert.equal(sent.body.consent, true);
  assert.equal(sent.body.company, 'Тестовая компания'); assert.equal(sent.body.intent, 'quote');
  assert.equal(sent.body.product, ''); assert.equal(sent.body.format, 'retail');
  gate.reject(new Error('offline')); await settle();
  assert.equal(p.company.value, 'Тестовая компания'); assert.equal(p.contact.value, 'audit@example.com');
  assert.equal(p.submit.disabled, false); assert.equal(p.company.disabled, false);
  assert.equal(p.form.getAttribute('aria-busy'), 'false'); assert.equal(p.timers.size, 0);
  assert.match(p.message(), /не подтверждено/); assert.equal(p.navigation.length, 0);
});
test('partners: success waits for a parsed durable receipt, retains values and does not resend identical data', async () => {
  const body = deferred(); const p = partnerFixture({fetch:async() => ({status:201,ok:true,json:() => body.promise})}); p.valid();
  p.form.dispatch('submit'); await settle();
  assert.equal(p.submit.disabled, true); assert.doesNotMatch(p.message(), /Заявка сохранена/);
  body.resolve(receipt(false)); await settle();
  assert.match(p.message(), /Заявка сохранена/); assert.ok(p.message().includes(REQUEST_ID));
  assert.equal(p.submit.disabled, false); assert.equal(p.company.value, 'Тестовая компания');
  p.form.dispatch('submit'); await settle(); assert.equal(p.requests.length, 1);
});
test('partners: malformed or uncommitted success never claims delivery', async () => {
  for (const body of [{ok:true},{...receipt(false),committed:false},{...receipt(false),requestId:'invalid'}, {...receipt(false),requestId:[REQUEST_ID]}, {ok:false}]) {
    const p = partnerFixture({fetch:async() => apiResponse(200,body)}); p.valid(); p.form.dispatch('submit'); await settle();
    assert.match(p.message(), /не подтверждено/); assert.doesNotMatch(p.message(), /Заявка сохранена/);
    assert.equal(p.submit.disabled, false);
  }
  const p = partnerFixture({fetch:async() => ({ok:true,status:200,json:async() => {throw new Error('bad json');}})});
  p.valid(); p.form.dispatch('submit'); await settle(); assert.match(p.message(), /не подтверждено/);
});
test('partners: retry after uncertain network failure reuses UUID and accepts duplicate committed receipt', async () => {
  const p = partnerFixture({fetch:async(_,count) => {
    if (count === 1) throw new Error('response lost after possible commit');
    return apiResponse(200,receipt(true));
  }}); p.valid(); p.form.dispatch('submit'); await settle();
  const key = p.requests[0].body.idempotencyKey;
  assert.match(key, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
  p.company.value = '  Тестовая компания  '; p.company.dispatch('input');
  p.form.dispatch('submit'); await settle();
  assert.equal(p.requests[1].body.idempotencyKey, key); assert.match(p.message(), /Заявка сохранена/);
  p.form.dispatch('submit'); await settle(); assert.equal(p.requests.length, 2);
});
test('partners: changed payload has a new identity; returning to an uncertain snapshot keeps its retry identity', async () => {
  const p = partnerFixture(); p.valid(); p.form.dispatch('submit'); await settle();
  const first = p.requests[0].body.idempotencyKey;
  p.company.value = 'Другая компания'; p.company.dispatch('input'); p.form.dispatch('submit'); await settle();
  assert.notEqual(p.requests[1].body.idempotencyKey, first);
  p.company.value = 'Тестовая компания'; p.company.dispatch('input'); p.form.dispatch('submit'); await settle();
  assert.equal(p.requests[2].body.idempotencyKey, first);
});
test('partners: HTTP validation/rate/storage/conflict failures are not success and keep fallback actions usable', async () => {
  for (const status of [422,429,503,409,403]) {
    const p = partnerFixture({fetch:async() => apiResponse(status,{ok:false,error:{code:'test',fields:status === 422 ? {contact:'Укажите телефон или почту'} : undefined}})});
    p.valid(); p.form.dispatch('submit'); await settle();
    assert.doesNotMatch(p.message(), /Заявка сохранена/); assert.equal(p.submit.disabled, false); assert.equal(p.copy.disabled, false);
    assert.equal(p.email.getAttribute('aria-disabled'), 'false'); assert.equal(p.company.value, 'Тестовая компания');
    if (status === 422) {
      assert.equal(p.contact.validationMessage, 'Укажите телефон или почту'); assert.ok(p.form.validationCount >= 2);
      p.contact.value = '+7 900 000-00-00'; p.contact.dispatch('input'); assert.equal(p.contact.validationMessage, '');
    }
  }
});
test('partners: timeout aborts the request, unlocks form and retains safe retry identity', async () => {
  const p = partnerFixture({fetch:request => new Promise((resolve,reject) => request.options.signal.addEventListener('abort', () => reject(new Error('aborted'))))});
  p.valid(); p.form.dispatch('submit');
  assert.equal(p.timers.size, 1); const timer = [...p.timers.values()][0]; assert.equal(timer.ms, 20000);
  timer.fn(); await settle(); assert.equal(p.requests[0].options.signal.aborted, true);
  assert.equal(p.submit.disabled, false); assert.equal(p.timers.size, 0); assert.match(p.message(), /не подтверждено/);
  p.form.dispatch('submit'); assert.equal(p.requests[1].body.idempotencyKey, p.requests[0].body.idempotencyKey);
  [...p.timers.values()][0].fn(); await settle();
});
test('partners: a stale network result cannot overwrite edits or attach old field errors', async () => {
  for (const result of [apiResponse(201,receipt(false)),apiResponse(422,{ok:false,error:{fields:{contact:'Old error'}}})]) {
    const gate = deferred(); const p = partnerFixture({fetch:() => gate.promise}); p.valid(); p.form.dispatch('submit');
    // Programmatic edits can still happen while native controls are disabled.
    p.company.value = 'Новое значение'; p.company.dispatch('input');
    gate.resolve(result); await settle();
    assert.equal(p.feedback.hidden, true); assert.equal(p.company.value, 'Новое значение');
    assert.equal(p.contact.validationMessage, ''); assert.equal(p.submit.disabled, false);
  }
});
test('partners: submit invalidates pending clipboard completion', async () => {
  const gate = deferred(); const p = partnerFixture({clipboard:{writeText:() => gate.promise},fetch:async() => apiResponse(201,receipt(false))});
  p.valid(); p.copy.dispatch('click'); p.form.dispatch('submit'); await settle();
  assert.match(p.message(), /Заявка сохранена/); gate.resolve(); await settle(); assert.match(p.message(), /Заявка сохранена/);
});
test('partners: explicit email fallback contains current selected taxonomy and does not POST', () => {
  const p = partnerFixture(); p.valid(); p.product.value = p.product.options[1].value; p.intent.value = 'samples';
  const event = p.email.dispatch('click'); assert.equal(event.defaultPrevented, false);
  const url = new URL(p.email.href); assert.equal(url.protocol, 'mailto:');
  const body = url.searchParams.get('body'); assert.ok(body.includes(p.product.selectedOptions[0].textContent)); assert.match(body, /Образцы продукции/);
  assert.equal(p.requests.length, 0); assert.match(p.message(), /Сайт не подтверждает отправку/);
  p.company.dispatch('input'); assert.equal(p.email.href, 'mailto:zakaz@novoferma.ru'); assert.equal(p.feedback.hidden, true);
});
test('partners: cryptographic UUID fallback works when randomUUID is unavailable', async () => {
  const p = partnerFixture({crypto:{getRandomValues:webcrypto.getRandomValues.bind(webcrypto)}}); p.valid(); p.form.dispatch('submit'); await settle();
  assert.match(p.requests[0].body.idempotencyKey, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
});
test('hero: generated panels/tabs are paired, first real art eager, inactive art deferred', () => {
  const h = heroFixture();
  h.scenes.forEach((scene, i) => {
    assert.equal(h.picks[i].getAttribute('aria-controls'), scene.getAttribute('id'));
    assert.equal(scene.getAttribute('aria-labelledby'), h.picks[i].getAttribute('id'));
    const art = scene.querySelectorAll('img').find(image => /(?:data:image|product-hero\/.*-art-)/.test(image.src));
    assert.ok(art); assert.equal(Boolean(art.dataset.src), i > 0);
    if (i > 0) assert.ok(art.src.startsWith('data:image'));
    assert.equal(scene.inert, i > 0); assert.equal(h.picks[i].tabIndex, i === 0 ? 0 : -1);
  });
  assert.equal(h.active(), 0); assert.equal(h.idle.length, 0);
  assert.ok(h.scenes.flatMap(scene => scene.querySelectorAll('img')).every(image => !image.decodeCalls));
});
test('hero: selection waits for artwork; responsive hints precede src', async () => {
  const h = heroFixture(); const art = h.scenes[1].querySelectorAll('img').find(image => image.dataset.src);
  art.dataset.srcset = 'fixture-400.webp 400w, fixture-800.webp 800w'; art.dataset.sizes = '50vw';
  h.next.dispatch('click'); assert.equal(h.active(), 0); assert.equal(h.stage.getAttribute('aria-busy'), 'true');
  assert.deepEqual(art.writes, ['sizes','srcset','src']);
  await h.resolveScene(1); assert.equal(h.active(), 1); assert.equal(h.stage.getAttribute('aria-busy'), 'false');
  assert.equal(h.picks[1].getAttribute('aria-selected'), 'true'); assert.equal(h.scenes[0].inert, true);
});
test('hero: rapid navigation commits only the latest scene', async () => {
  const h = heroFixture(); h.next.dispatch('click'); h.next.dispatch('click');
  await h.resolveScene(2); assert.equal(h.active(), 2);
  await h.resolveScene(1); assert.equal(h.active(), 2);
});
test('hero: rejected decode does not trap navigation or aria-busy', async () => {
  const h = heroFixture(); h.next.dispatch('click'); await h.resolveScene(1, true);
  assert.equal(h.active(), 1); assert.equal(h.stage.getAttribute('aria-busy'), 'false');
});
test('hero: End key focuses without scrolling and commits the last scene', async () => {
  const h = heroFixture(); const event = h.picks[0].dispatch('keydown', {key:'End'});
  assert.equal(event.defaultPrevented, true); assert.equal(h.doc.activeElement, h.picks.at(-1));
  assert.equal(h.picks.at(-1).focusCalls.at(-1).preventScroll, true);
  await h.resolveScene(h.scenes.length - 1); assert.equal(h.active(), h.scenes.length - 1);
});
test('hero: focus inside the old panel is moved out before it becomes inert', async () => {
  const h = heroFixture(); h.doc.activeElement = h.scenes[0].querySelector('a'); h.next.dispatch('click');
  await h.resolveScene(1); assert.equal(h.doc.activeElement, h.picks[1]); assert.equal(h.picks[1].focusCalls.at(-1).preventScroll, true);
});
test('hero: idle warm starts after load, one scene at a time, without autoplay', async () => {
  const h = heroFixture(); h.load(); assert.equal(h.idle.length, 1); h.idle.shift()();
  assert.ok(h.pending(1).length); assert.equal(h.pending(2).length, 0); assert.equal(h.idle.length, 0);
  await h.resolveScene(1); assert.equal(h.idle.length, 1); assert.equal(h.active(), 0);
  h.idle.shift()(); assert.ok(h.pending(2).length); assert.equal(h.active(), 0);
});
test('hero: saveData/slow connection skips speculative warm but keeps explicit selection', async () => {
  for (const settings of [{saveData:true},{effectiveType:'2g'},{effectiveType:'slow-2g'}]) {
    const h = heroFixture(settings); h.load(); assert.equal(h.idle.length, 0);
    h.next.dispatch('click'); await h.resolveScene(1); assert.equal(h.active(), 1);
  }
});
test('hero: hidden document defers warm; visibility resumes; timeout fallback remains delayed', () => {
  const h = heroFixture({hidden:true}); h.load(); assert.equal(h.idle.length, 0);
  h.doc.hidden = false; h.doc.dispatch('visibilitychange', {bubbles:false}); assert.equal(h.idle.length, 1);
  const fallback = heroFixture({idleApi:false}); fallback.load();
  assert.equal(fallback.timers.length, 1); assert.ok(fallback.timers[0].ms >= 1000); assert.equal(fallback.pending(1).length, 0);
});

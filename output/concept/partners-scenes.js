'use strict';
(() => {
 const form = document.querySelector('#partner-request-form');
 if (!form) return;
 const names = {retail:'Поставки в магазины', horeca:'Для кафе и ресторанов', stm:'Производство под своей маркой (СТМ)'};
 const intents = {quote:'Ассортимент и условия', specification:'Спецификация продукта', samples:'Образцы продукции', stm:'Проект СТМ'};
 const hints = {retail:'Продукция Новофермы для вашего ассортимента.', horeca:'Продукты из птицы для меню кафе и ресторанов.', stm:'Обсудим продукт, фасовку и упаковку под вашим брендом.'};
 const help = document.querySelector('#partner-format-help');
 const feedback = document.querySelector('#partner-request-feedback');
 const draft = document.querySelector('#partner-request-draft');
 const copy = document.querySelector('#partner-copy-request');
 const email = document.querySelector('#partner-email-request');
 const submit = form.querySelector('button[type="submit"]');
 const product = form.querySelector('[name="product"]');
 const intent = form.querySelector('[name="intent"]');
 const consent = form.querySelector('[name="consent"]');
 const radios = [...form.querySelectorAll('[name="format"]')];
 const controls = [...form.querySelectorAll('input,textarea,select,button')];
 const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
 // Keep retry identities in this page only. No personal data is stored in a URL or browser storage.
 const attempts = new Map();
 let requestRevision = 0;
 let pending = false;
 let disabledBefore = [];
 function selectedFormat() { return form.querySelector('[name="format"]:checked')?.value || 'retail'; }
 function allowed(select, value) { return Boolean(select && [...select.options].some(option => option.value === value)); }
 function textValue(name) { return (form.querySelector(`[name="${name}"]`)?.value || '').trim(); }
 function payload() {
  return {company:textValue('company'), city:textValue('city'), contact:textValue('contact'), message:textValue('message'),
   format:selectedFormat(), product:product?.value || '', intent:intent?.value || '', consent:consent?.checked === true};
 }
 function resetFeedback() {
  requestRevision++;
  feedback.hidden = true; feedback.replaceChildren();
  draft.hidden = true; draft.value = '';
  if (email) email.href = 'mailto:zakaz@novoferma.ru';
 }
 function showFeedback(message) { feedback.hidden = false; feedback.replaceChildren(document.createTextNode(message)); }
 function updateFormat() { help.textContent = hints[selectedFormat()]; resetFeedback(); }
 function setPending(value) {
  pending = value;
  form.setAttribute('aria-busy', String(value));
  if (value) {
   disabledBefore = controls.map(control => control.disabled);
   controls.forEach(control => { control.disabled = true; });
  } else controls.forEach((control, index) => { control.disabled = disabledBefore[index]; });
  if (email) email.setAttribute('aria-disabled', String(value));
 }
 function fieldsChanged(event) {
  if (event.target.matches('input:not([type="radio"]),textarea,select') && event.target.getAttribute('name')) {
   event.target.setCustomValidity(''); resetFeedback();
  }
 }
 form.addEventListener('input', fieldsChanged);
 form.addEventListener('change', fieldsChanged);
 form.addEventListener('reset', event => {
  if (pending) { event.preventDefault(); return; }
  resetFeedback();
  controls.forEach(control => { if (control.setCustomValidity) control.setCustomValidity(''); });
 });
 radios.forEach(input => input.addEventListener('change', updateFormat));
 document.querySelectorAll('[data-partner-format]').forEach(link => link.addEventListener('click', event => {
  event.preventDefault();
  if (pending) return;
  const radio = radios.find(input => input.value === link.dataset.partnerFormat);
  if (radio) {
   radio.checked = true;
   if (allowed(intent, link.dataset.partnerIntent)) intent.value = link.dataset.partnerIntent;
   updateFormat();
   form.scrollIntoView({behavior:'auto', block:'start'});
   radio.focus({preventScroll:true});
  }
 }));
 // Only taxonomy values from existing controls can be copied from a shareable URL.
 const query = new URLSearchParams(window.location.search);
 const formatPreset = radios.find(input => input.value === query.get('format'));
 if (formatPreset) formatPreset.checked = true;
 for (const [name, select] of [['product', product], ['intent', intent]]) {
  const preset = query.get(name);
  if (preset !== null && allowed(select, preset)) select.value = preset;
 }
 updateFormat();
 function validate() {
  if (!product || !intent || !consent || !submit) {
   showFeedback('Форма временно недоступна. Напишите на zakaz@novoferma.ru.'); return false;
  }
  for (const input of form.querySelectorAll('[required]:not([type="radio"])')) {
   const valid = input.getAttribute('type') === 'checkbox' ? input.checked : input.value.trim();
   input.setCustomValidity(valid ? '' : input === consent ? 'Подтвердите согласие на обработку данных' : 'Заполните это поле');
  }
  product.setCustomValidity(allowed(product, product.value) ? '' : 'Выберите продукт из списка');
  intent.setCustomValidity(allowed(intent, intent.value) && Object.hasOwn(intents, intent.value) ? '' : 'Выберите цель запроса');
  return form.reportValidity();
 }
 function makeRequest(data = payload()) {
  const productName = product?.selectedOptions[0]?.textContent.trim() || 'Обсудим ассортимент';
  return `Здравствуйте!\nХочу обсудить сотрудничество с Новофермой.\n\nНаправление: ${names[data.format]}\nЦель: ${intents[data.intent]}\nПродукт: ${productName}\nКомпания: ${data.company}\nГород: ${data.city || 'Уточним при общении'}\nКонтакт для связи: ${data.contact}\n\n${data.message || 'Подскажите, пожалуйста, ассортимент и условия сотрудничества.'}`;
 }
 function newKey() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
  const hex = [...bytes].map(byte => byte.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;
 }
 function showReceipt(receipt) {
  showFeedback(`Заявка сохранена. Номер: ${receipt.requestId}. Сохраните его для обращения по заявке.`);
 }
 function serverFailure(response, result) {
  const fields = result?.error?.fields;
  if (fields && typeof fields === 'object') {
   for (const name of ['company','city','contact','message','product','intent','consent']) {
    if (typeof fields[name] === 'string') form.querySelector(`[name="${name}"]`)?.setCustomValidity(fields[name]);
   }
  }
  if (response.status === 422) return 'Заявка не отправлена. Проверьте отмеченные поля и повторите отправку. Данные сохранены в форме.';
  if (response.status === 429) return 'Заявка не отправлена: слишком много попыток. Подождите немного и повторите отправку. Данные сохранены в форме.';
  if (response.status === 409) return 'Не удалось подтвердить получение заявки. Скопируйте запрос или отправьте его по почте, чтобы уточнить получение.';
  return 'Сервер не подтвердил получение заявки. Данные сохранены в форме. Повторите отправку или воспользуйтесь почтой либо копированием запроса.';
 }
 form.addEventListener('submit', async event => {
  event.preventDefault();
  if (pending) return;
  resetFeedback();
  if (!validate()) return;
  const data = payload(); const signature = JSON.stringify(data); const revision = requestRevision;
  let attempt = attempts.get(signature);
  let timer;
  try {
   if (!attempt) { attempt = {key:newKey()}; attempts.set(signature, attempt); }
   if (attempt.receipt) { showReceipt(attempt.receipt); return; }
   const controller = new AbortController();
   setPending(true);
   showFeedback('Отправляем заявку. Дождитесь подтверждения сохранения.');
   timer = window.setTimeout(() => controller.abort(), 20000);
   const response = await fetch('/api/partner-requests', {
    method:'POST', headers:{'Content-Type':'application/json'}, mode:'same-origin', credentials:'omit',
    body:JSON.stringify({...data, idempotencyKey:attempt.key}), signal:controller.signal,
   });
   const result = await response.json();
   if (!response.ok) {
    if (revision === requestRevision) {
     const message = serverFailure(response, result);
     setPending(false); showFeedback(message);
     if (response.status === 422) form.reportValidity();
    }
    return;
   }
   if (result?.ok !== true || result.committed !== true || typeof result.requestId !== 'string' || !uuidPattern.test(result.requestId)) throw new Error('Missing committed receipt');
   // Remember committed snapshots even if a later edit has made their feedback stale.
   attempt.receipt = {requestId:result.requestId};
   if (revision === requestRevision) showReceipt(attempt.receipt);
  } catch {
   if (revision === requestRevision) showFeedback('Получение заявки не подтверждено. Данные сохранены в форме. Повторите отправку — повторная попытка не создаст дубль. Также можно отправить запрос по почте или скопировать его.');
  } finally {
   if (timer !== undefined) window.clearTimeout(timer);
   if (pending) setPending(false);
  }
 });
 copy?.addEventListener('click', async () => {
  if (pending) return;
  resetFeedback(); if (!validate()) return;
  const body = makeRequest(); const revision = requestRevision;
  try {
   if (!navigator.clipboard?.writeText) throw new Error('clipboard unavailable');
   await navigator.clipboard.writeText(body);
   if (revision !== requestRevision) return;
   showFeedback('Запрос скопирован. Чтобы отправить его по почте, вставьте текст в письмо на zakaz@novoferma.ru.');
  } catch {
   if (revision !== requestRevision) return;
   draft.hidden = false; draft.value = body; draft.focus(); draft.select();
   showFeedback('Текст запроса готов для копирования. Скопируйте его и отправьте на zakaz@novoferma.ru.');
  }
 });
 email?.addEventListener('click', event => {
  if (pending) { event.preventDefault(); return; }
  resetFeedback();
  if (!validate()) { event.preventDefault(); return; }
  email.href = `mailto:zakaz@novoferma.ru?subject=${encodeURIComponent('Новоферма — ' + names[selectedFormat()])}&body=${encodeURIComponent(makeRequest())}`;
  showFeedback('Письмо подготовлено. Проверьте и отправьте его в почтовой программе. Сайт не подтверждает отправку письма.');
 });
})();

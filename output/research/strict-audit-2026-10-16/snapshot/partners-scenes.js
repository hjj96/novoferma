'use strict';
(() => {
 const form=document.querySelector('#partner-request-form');
 if(!form)return;
 const names={retail:'Поставки в магазины',horeca:'Для кафе и ресторанов',stm:'Производство под своей маркой (СТМ)'};
 const hints={retail:'Продукция Новофермы для вашего ассортимента.',horeca:'Продукты из птицы для меню кафе и ресторанов.',stm:'Обсудим продукт, фасовку и упаковку под вашим брендом.'};
 const help=document.querySelector('#partner-format-help');
 const feedback=document.querySelector('#partner-request-feedback');
 const draft=document.querySelector('#partner-request-draft');
 const radios=[...form.querySelectorAll('[name="format"]')];
 function selectedFormat(){return form.querySelector('[name="format"]:checked')?.value||'retail';}
 function resetFeedback(){feedback.hidden=true;feedback.replaceChildren();draft.hidden=true;draft.value='';}
 function updateFormat(){help.textContent=hints[selectedFormat()];resetFeedback();}
 radios.forEach(input=>input.addEventListener('change',updateFormat));
 document.querySelectorAll('[data-partner-format]').forEach(link=>link.addEventListener('click',()=>{
  const radio=radios.find(input=>input.value===link.dataset.partnerFormat);
  if(radio){radio.checked=true;updateFormat();}
 }));
 function values(){return Object.fromEntries(new FormData(form).entries());}
 function makeRequest(){
  const data=values();
  return `Здравствуйте!\nХочу обсудить сотрудничество с Новофермой.\n\nНаправление: ${names[data.format]||names.retail}\nКомпания: ${data.company.trim()}\nГород: ${data.city.trim()||'Уточним при общении'}\nКонтакт для связи: ${data.contact.trim()}\n\n${data.message.trim()||'Подскажите, пожалуйста, ассортимент и условия сотрудничества.'}`;
 }
 function showFeedback(message){feedback.hidden=false;feedback.replaceChildren(document.createTextNode(message));}
 form.addEventListener('input',event=>{
  if(event.target.matches('input:not([type="radio"]),textarea')){event.target.setCustomValidity('');resetFeedback();}
 });
 function validate(){
  for(const input of form.querySelectorAll('[required]:not([type="radio"])'))input.setCustomValidity(input.value.trim()?'':'Заполните это поле');
  return form.reportValidity();
 }
 form.addEventListener('submit',event=>{
  event.preventDefault();if(!validate())return;
  const body=makeRequest();
  const href=`mailto:zakaz@novoferma.ru?subject=${encodeURIComponent('Новоферма — '+names[selectedFormat()])}&body=${encodeURIComponent(body)}`;
  showFeedback('Письмо подготовлено. Если почта не открылась, ');
  const retry=document.createElement('a');retry.href=href;retry.textContent='откройте письмо ещё раз';feedback.append(retry);
  window.location.href=href;
 });
 document.querySelector('#partner-copy-request').addEventListener('click',async()=>{
  if(!validate())return;
  const body=makeRequest();
  try{
   if(!navigator.clipboard?.writeText)throw new Error('clipboard unavailable');
   await navigator.clipboard.writeText(body);showFeedback('Запрос скопирован. Отправьте его на zakaz@novoferma.ru.');
  }catch{
   draft.hidden=false;draft.value=body;draft.focus();draft.select();
   showFeedback('Текст запроса готов. Скопируйте его и отправьте на zakaz@novoferma.ru.');
  }
 });
 updateFormat();
})();

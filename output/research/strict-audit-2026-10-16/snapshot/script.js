'use strict';
const prefersReducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
const menu=document.querySelector('#site-menu');
const menuToggle=document.querySelector('.menu-toggle');
function closeMenu(){if(menu?.open)menu.close();}
menuToggle?.addEventListener('click',()=>{menu.showModal();document.body.classList.add('menu-open');menuToggle.setAttribute('aria-expanded','true');menu.querySelector('.menu-close').focus();});
menu?.querySelector('.menu-close')?.addEventListener('click',closeMenu);
menu?.addEventListener('click',event=>{if(event.target===menu){const r=menu.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right)closeMenu();}});
menu?.addEventListener('close',()=>{document.body.classList.remove('menu-open');menuToggle?.setAttribute('aria-expanded','false');menuToggle?.focus({preventScroll:true});});
const topButton=document.querySelector('.to-top');
function updateTop(){
 if(!topButton)return;
 const visible=scrollY>800;
 topButton.classList.toggle('visible',visible);
 topButton.inert=!visible;
 topButton.tabIndex=visible?0:-1;
 topButton.setAttribute('aria-hidden',String(!visible));
 if(!visible&&document.activeElement===topButton)document.querySelector('.brand')?.focus({preventScroll:true});
}
addEventListener('scroll',updateTop,{passive:true});updateTop();
topButton?.addEventListener('click',()=>{window.scrollTo({top:0,behavior:prefersReducedMotion.matches?'instant':'smooth'});document.querySelector('.brand')?.focus({preventScroll:true});});
// Only prepare content below the viewport: no blank first paint or inaccessible content.
const revealElements=[...document.querySelectorAll('.reveal')];
let revealObserver;
function showReveal(element){element.classList.add('is-visible');revealObserver?.unobserve(element);}
function setRevealDelays(){
 const grids=new Map();
 const measured=revealElements.filter(element=>element.matches('.product-card.is-prepared:not(.is-visible)')&&!element.hidden)
  .map(element=>({element,rectangle:element.getBoundingClientRect(),grid:element.closest('.product-grid')}));
 // Stagger only siblings in the same visual row, including after a resize.
 for(const item of measured){
  if(!item.grid)continue;
  if(!grids.has(item.grid))grids.set(item.grid,[]);
  const rows=grids.get(item.grid);
  let row=rows.find(row=>Math.abs(row.top-item.rectangle.top)<8);
  if(!row){row={top:item.rectangle.top,items:[]};rows.push(row);}
  row.items.push(item);
 }
 for(const rows of grids.values())for(const row of rows){
  row.items.sort((a,b)=>a.rectangle.left-b.rectangle.left);
  row.items.forEach((item,index)=>item.element.style.setProperty('--reveal-delay',`${Math.min(index,3)*55}ms`));
 }
}
if(!prefersReducedMotion.matches&&'IntersectionObserver' in window){
 revealObserver=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting)showReveal(entry.target);})},{threshold:.08,rootMargin:'0px 0px -25px 0px'});
 const measured=revealElements.map(element=>({element,top:element.getBoundingClientRect().top}));
 measured.forEach(({element,top})=>{if(top>=innerHeight){element.classList.add('is-prepared');revealObserver.observe(element);}});
 setRevealDelays();
 addEventListener('resize',()=>requestAnimationFrame(setRevealDelays),{passive:true});
 document.fonts?.ready.then(setRevealDelays);
}
// Focused links and controls never wait behind a scroll reveal.
document.addEventListener('focusin',event=>revealElements.forEach(element=>{if(element.contains(event.target))showReveal(element);}));
const entranceElements=[];
if(!document.body.classList.contains('page-index')&&!prefersReducedMotion.matches){
 const firstEditorial=document.querySelector('.page-heading,.about-hero,.page-intro,.partner-hero,.contacts-main,.product-detail');
 if(firstEditorial){
  const parts=firstEditorial.matches('.product-detail')
   ?[...firstEditorial.querySelectorAll('.detail-copy > .eyebrow,.detail-copy > h1,.detail-copy > .hand')]
   :firstEditorial.matches('.contacts-main')?[firstEditorial.querySelector('.contact-heading')]
   :firstEditorial.matches('.about-hero,.partner-hero')?[...firstEditorial.querySelectorAll('.split > *')]:[firstEditorial];
  const visible=parts.filter(Boolean).filter(element=>{const rectangle=element.getBoundingClientRect();return rectangle.top<innerHeight&&rectangle.bottom>0;});
  visible.forEach((element,index)=>{element.style.setProperty('--entrance-delay',`${index*65}ms`);element.classList.add('page-enter');entranceElements.push(element);});
 }
}
prefersReducedMotion.addEventListener('change',()=>{
 if(!prefersReducedMotion.matches)return;
 revealObserver?.disconnect();
 revealElements.forEach(showReveal);
 entranceElements.forEach(element=>element.classList.remove('page-enter'));
});
const cityForm=document.querySelector('#city-form');
if(cityForm){const wanted=document.querySelector('#wanted-product');const queryProduct=new URLSearchParams(location.search).get('product');if(queryProduct&&[...wanted.options].some(option=>option.value===queryProduct))wanted.value=queryProduct;cityForm.addEventListener('submit',event=>{event.preventDefault();if(!cityForm.reportValidity())return;const city=document.querySelector('#city').value.trim();if(!city){document.querySelector('#city').setCustomValidity('Укажите город');cityForm.reportValidity();return;}const product=wanted.selectedOptions[0]?.text||'Весь ассортимент';const body=`Здравствуйте!\nПодскажите, пожалуйста, где можно купить продукцию Новофермы.\nГород: ${city}\nПродукт: ${product}\nСпасибо!`;const link=`mailto:info@novoferma.ru?subject=${encodeURIComponent('Где купить Новоферму')}&body=${encodeURIComponent(body)}`;const feedback=document.querySelector('.form-feedback');feedback.hidden=false;feedback.replaceChildren(document.createTextNode('Письмо подготовлено. Если почта не открылась, '));const retry=document.createElement('a');retry.href=link;retry.textContent='откройте его ещё раз';retry.style.textDecoration='underline';feedback.append(retry);location.href=link;});document.querySelector('#city').addEventListener('input',event=>event.target.setCustomValidity(''));}

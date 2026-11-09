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
function updateTop(){topButton?.classList.toggle('visible',scrollY>800);}
addEventListener('scroll',updateTop,{passive:true});updateTop();
topButton?.addEventListener('click',()=>{window.scrollTo({top:0,behavior:prefersReducedMotion.matches?'instant':'smooth'});document.querySelector('.brand')?.focus({preventScroll:true});});
// Only prepare content below the viewport: no blank first paint or inaccessible content.
const revealElements=[...document.querySelectorAll('.reveal')];
if(!prefersReducedMotion.matches&&'IntersectionObserver' in window){
 const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}})},{threshold:.08,rootMargin:'0px 0px -25px 0px'});
 revealElements.forEach((element,index)=>{if(element.getBoundingClientRect().top>innerHeight){element.classList.add('is-prepared');element.style.transitionDelay=`${Math.min(index%3,2)*65}ms`;observer.observe(element);}});
 prefersReducedMotion.addEventListener('change',()=>{if(prefersReducedMotion.matches)revealElements.forEach(e=>e.classList.add('is-visible'));});
}
const ideas={
 dinner:{number:'01',heading:['Ужин дома.','Все свои.'],description:'Стрипсы, нежное пюре и свежие овощи. Добавьте любимый соус — и зовите к столу.',image:'assets/serving-dinner-crop.webp',alt:'Стрипсы с пюре и овощами — идея подачи',caption:'Любимый гарнир уже ждёт',button:'Выбрать стрипсы',match:'стрипсы'},
 movie:{number:'02',heading:['Хорошее кино.','Любимый вкус.'],description:'Наггетсы, куриный попкорн и любимый соус. Осталось выбрать фильм и устроиться поудобнее.',image:'assets/serving-movie-crop.webp',alt:'Наггетсы и куриный попкорн с соусом — идея подачи',caption:'Всё готово к хорошему фильму',button:'Выбрать наггетсы',match:'наггетсы куриные'},
 company:{number:'03',heading:['Большая тарелка.','Своя компания.'],description:'Стрипсы и хрустящие кусочки на общем столе — каждый выбирает то, что любит. Добавьте овощи и соусы по вкусу.',image:'assets/serving-company-crop.webp',alt:'Общая тарелка с куриными закусками, овощами и соусами',caption:'Самое вкусное — вместе',button:'Смотреть продукты',match:null}
};
const tabs=[...document.querySelectorAll('[data-serve]')];
const servingPanel=document.querySelector('#serve-panel');
let switchVersion=0;
async function selectIdea(tab){
 const idea=ideas[tab.dataset.serve];const version=++switchVersion;
 tabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;});
 const image=document.querySelector('#serve-image');
 const preload=new Image();preload.src=idea.image;
 try{await preload.decode();}catch{}
 if(version!==switchVersion)return;
 image.src=idea.image;image.alt=idea.alt;
 document.querySelector('#serve-heading').replaceChildren(document.createTextNode(idea.heading[0]),document.createElement('br'),document.createTextNode(idea.heading[1]));
 document.querySelector('#serve-description').textContent=idea.description;
 document.querySelector('#serve-caption').textContent=idea.caption;
 const action=servingPanel.querySelector('.button');action.replaceChildren(document.createTextNode(idea.button),Object.assign(document.createElement('span'),{textContent:'↗'}));action.lastChild.setAttribute('aria-hidden','true');
 const matching=[...document.querySelectorAll('.product-card')].find(card=>idea.match&&card.dataset.name.includes(idea.match));
 action.href=matching?matching.querySelector('a').getAttribute('href'):'catalogue.html';
 servingPanel.setAttribute('aria-labelledby',tab.id);
 servingPanel.classList.remove('is-changing');void servingPanel.offsetWidth;servingPanel.classList.add('is-changing');
}
tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>selectIdea(tab));tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(index+1)%tabs.length;else if(event.key==='ArrowLeft')next=(index-1+tabs.length)%tabs.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=tabs.length-1;else return;event.preventDefault();tabs[next].focus();selectIdea(tabs[next]);});});
const categoryButtons=[...document.querySelectorAll('[data-category-filter]')];
const meatButtons=[...document.querySelectorAll('[data-meat-filter]')];
const search=document.querySelector('#product-search');
const searchClear=document.querySelector('.search-clear');
const productCards=[...document.querySelectorAll('.catalogue-grid .product-card')];
let selectedCategory='all',selectedMeat='all';
const normalize=text=>text.toLowerCase().replaceAll('ё','е').trim();
function productWord(n){return n%10===1&&n%100!==11?'продукт':n%10>=2&&n%10<=4&&(n%100<12||n%100>14)?'продукта':'продуктов';}
function filterProducts(){
 const query=normalize(search?.value||'');let count=0;
 productCards.forEach(card=>{const visible=(selectedCategory==='all'||card.dataset.category===selectedCategory)&&(selectedMeat==='all'||card.dataset.meat===selectedMeat)&&normalize(card.dataset.name).includes(query);const wasHidden=card.hidden;card.hidden=!visible;if(visible){count++;card.classList.add('is-visible');if(wasHidden){card.classList.remove('is-filtered-in');void card.offsetWidth;card.classList.add('is-filtered-in');}}});
 const status=document.querySelector('#product-count');if(status)status.textContent=`${count} ${productWord(count)}`;
 const empty=document.querySelector('.empty-state');if(empty)empty.hidden=count>0;
 if(searchClear)searchClear.hidden=!search.value;
}
categoryButtons.forEach(button=>button.addEventListener('click',()=>{selectedCategory=button.dataset.categoryFilter;categoryButtons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));filterProducts();}));
meatButtons.forEach(button=>button.addEventListener('click',()=>{selectedMeat=button.dataset.meatFilter;meatButtons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));filterProducts();}));
search?.addEventListener('input',filterProducts);
searchClear?.addEventListener('click',()=>{search.value='';filterProducts();search.focus();});
document.querySelector('#reset-filters')?.addEventListener('click',()=>{selectedCategory='all';selectedMeat='all';search.value='';categoryButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.categoryFilter==='all')));meatButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.meatFilter==='all')));filterProducts();document.querySelector('.catalogue-tools').scrollIntoView({behavior:prefersReducedMotion.matches?'instant':'smooth',block:'start'});search.focus({preventScroll:true});});
if(productCards.length)filterProducts();
const cityForm=document.querySelector('#city-form');
if(cityForm){const wanted=document.querySelector('#wanted-product');const queryProduct=new URLSearchParams(location.search).get('product');if(queryProduct)wanted.value=queryProduct;cityForm.addEventListener('submit',event=>{event.preventDefault();if(!cityForm.reportValidity())return;const city=document.querySelector('#city').value.trim();if(!city){document.querySelector('#city').setCustomValidity('Укажите город');cityForm.reportValidity();return;}const product=wanted.options[wanted.selectedIndex].text;const body=`Здравствуйте!\nПодскажите, пожалуйста, где можно купить продукцию Новофермы.\nГород: ${city}\nПродукт: ${product}\nСпасибо!`;const link=`mailto:info@novoferma.ru?subject=${encodeURIComponent('Где купить Новоферму')}&body=${encodeURIComponent(body)}`;const feedback=document.querySelector('.form-feedback');feedback.hidden=false;feedback.replaceChildren(document.createTextNode('Письмо подготовлено. Если почта не открылась, '));const retry=document.createElement('a');retry.href=link;retry.textContent='откройте его ещё раз';retry.style.textDecoration='underline';feedback.append(retry);location.href=link;});document.querySelector('#city').addEventListener('input',event=>event.target.setCustomValidity(''));}

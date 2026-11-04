'use strict';
(() => {
 const tools=document.querySelector('[data-catalogue-tools]');
 if(!tools)return;
 const category=document.querySelector('#catalogue-category');
 const meat=document.querySelector('#catalogue-meat');
 const cards=[...document.querySelectorAll('.catalogue-grid .product-card')];
 const count=document.querySelector('.catalogue-count');
 const empty=document.querySelector('.catalogue-empty');
 const reset=document.querySelector('.catalogue-reset');
 function update(){
  let visible=0;
  cards.forEach(card=>{
   card.hidden=Boolean((category.value&&card.dataset.category!==category.value)||(meat.value&&card.dataset.meat!==meat.value));
   if(!card.hidden)visible++;
  });
  count.textContent=`Показано ${visible} из ${cards.length}`;
  empty.hidden=visible!==0;
  reset.disabled=!category.value&&!meat.value;
 }
 function clear(){category.value='';meat.value='';update();}
 category.addEventListener('change',update);meat.addEventListener('change',update);
 reset.addEventListener('click',clear);
 addEventListener('hashchange',()=>{if(location.hash==='#novelties')clear();});
 tools.hidden=false;update();
})();

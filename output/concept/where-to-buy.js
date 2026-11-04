'use strict';
(() => {
 const select=document.querySelector('#wanted-product');
 const cards=[...document.querySelectorAll('[data-retailer-products]')];
 if(!select||!cards.length)return;
 const empty=document.querySelector('.retailer-empty');
 function update(){
  let visible=0;
  for(const card of cards){
   card.hidden=Boolean(select.value&&!card.dataset.retailerProducts.split(' ').includes(select.value));
   if(!card.hidden)visible++;
  }
  if(empty)empty.hidden=visible>0;
 }
 select.addEventListener('change',update);update();
})();

'use strict';
(() => {
 const carousel=document.querySelector('[data-product-carousel]');
 if(!carousel) return;
 const scenes=[...carousel.querySelectorAll('.product-scene')];
 const picks=[...carousel.querySelectorAll('[data-product-index]')];
 const stage=carousel.querySelector('.product-stage');
 let index=0, pointerStart=null;
 function select(next){
  const focusInPanel=scenes[index].contains(document.activeElement);
  index=(next+scenes.length)%scenes.length;
  scenes.forEach((scene,i)=>{
   const active=i===index;
   scene.classList.toggle('is-active',active);
   scene.setAttribute('aria-hidden',String(!active));
   scene.inert=!active;
   picks[i].setAttribute('aria-selected',String(active));
   picks[i].tabIndex=active?0:-1;
  });
  carousel.querySelector('[data-product-announcement]').textContent=`${picks[index].dataset.productName}. ${index+1} из ${scenes.length}`;
  if(focusInPanel) picks[index].focus({preventScroll:true});
 }
 picks.forEach((pick,i)=>{
  pick.addEventListener('click',()=>select(i));
  pick.addEventListener('keydown',event=>{
   if(event.altKey||event.ctrlKey||event.metaKey) return;
   let next;
   if(event.key==='ArrowRight') next=index+1;
   else if(event.key==='ArrowLeft') next=index-1;
   else if(event.key==='Home') next=0;
   else if(event.key==='End') next=scenes.length-1;
   else return;
   event.preventDefault();select(next);picks[index].focus({preventScroll:true});
  });
 });
 carousel.querySelector('[data-product-prev]').addEventListener('click',()=>select(index-1));
 carousel.querySelector('[data-product-next]').addEventListener('click',()=>select(index+1));
 carousel.addEventListener('keydown',event=>{
  if(event.target.closest('[role=tablist]')||event.altKey||event.ctrlKey||event.metaKey) return;
  if(event.key==='ArrowLeft'||event.key==='ArrowRight'){
   event.preventDefault();select(index+(event.key==='ArrowRight'?1:-1));picks[index].focus({preventScroll:true});
  }
 });
 stage.addEventListener('pointerdown',event=>{
  if(event.target.closest('a,button')||!event.isPrimary||event.button!==0) return;
  pointerStart={x:event.clientX,y:event.clientY,id:event.pointerId};
  stage.setPointerCapture(event.pointerId);
 });
 stage.addEventListener('pointerup',event=>{
  if(!pointerStart||event.pointerId!==pointerStart.id) return;
  const dx=event.clientX-pointerStart.x,dy=event.clientY-pointerStart.y;pointerStart=null;
  if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.35) select(index+(dx<0?1:-1));
 });
 stage.addEventListener('pointercancel',()=>pointerStart=null);
 stage.addEventListener('dragstart',event=>event.preventDefault());
 let lastWheel=0,lastWheelEvent=0,wheelDistance=0;
 stage.addEventListener('wheel',event=>{
  if(event.ctrlKey||Math.abs(event.deltaX)<Math.abs(event.deltaY)*1.4||event.deltaX===0) return;
  event.preventDefault();const now=Date.now();
  if(now-lastWheelEvent>220) wheelDistance=0;
  lastWheelEvent=now;if(now-lastWheel<600) return;
  wheelDistance+=event.deltaX*(event.deltaMode===1?16:event.deltaMode===2?stage.clientWidth:1);
  if(Math.abs(wheelDistance)<55) return;
  lastWheel=now;select(index+(wheelDistance>0?1:-1));wheelDistance=0;
 },{passive:false});
 // Slides stay still until selected. No autoplay or object transformations.
 scenes.slice(1).forEach(scene=>scene.querySelectorAll('img').forEach(img=>img.decode().catch(()=>{})));
})();

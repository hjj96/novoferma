'use strict';
(() => {
 const carousel=document.querySelector('[data-product-carousel]');
 if(!carousel) return;
 const scenes=[...carousel.querySelectorAll('.product-scene')];
 const picks=[...carousel.querySelectorAll('[data-product-index]')];
 const stage=carousel.querySelector('.product-stage');
 const menu=document.querySelector('#site-menu');
 let index=0, requestedIndex=0, selectionVersion=0, pointerStart=null;
 const imageReadiness=new WeakMap();
 const preparedScenes=new WeakSet([scenes[0]]);
 function hydrateImage(img,urgent){
  if(imageReadiness.has(img)){
   if(urgent)img.setAttribute('fetchpriority','auto');
   return imageReadiness.get(img);
  }
  if(!img.dataset.src&&!img.dataset.srcset)return Promise.resolve();
  img.loading='eager';img.decoding='async';
  img.setAttribute('fetchpriority',urgent?'auto':'low');
  // Set responsive hints before src, so the browser can choose one candidate.
  if(img.dataset.sizes){img.sizes=img.dataset.sizes;delete img.dataset.sizes;}
  if(img.dataset.srcset){img.srcset=img.dataset.srcset;delete img.dataset.srcset;}
  if(img.dataset.src){img.src=img.dataset.src;delete img.dataset.src;}
  const ready=typeof img.decode==='function'
   ?img.decode().catch(()=>{})
   :new Promise(resolve=>{
    if(img.complete){resolve();return;}
    const done=()=>{img.removeEventListener('load',done);img.removeEventListener('error',done);resolve();};
    img.addEventListener('load',done);img.addEventListener('error',done);
   });
  imageReadiness.set(img,ready);return ready;
 }
 function hydrateScene(scene,urgent=false){
  return Promise.all([...scene.querySelectorAll('img')].map(img=>hydrateImage(img,urgent)))
   .then(()=>preparedScenes.add(scene));
 }
 function select(next){
  const target=(next+scenes.length)%scenes.length;
  requestedIndex=target;
  const version=++selectionVersion;
  stage.setAttribute('aria-busy',String(!preparedScenes.has(scenes[target])));
  // Give artwork a short head start, but a stalled decorative image must not
  // hold the selected product text, link or keyboard navigation indefinitely.
  let deadline;
  const ready=hydrateScene(scenes[target],true);
  const bounded=preparedScenes.has(scenes[target])?ready:Promise.race([
   ready,new Promise(resolve=>{deadline=window.setTimeout(resolve,1500);})
  ]);
  bounded.then(()=>{
   if(deadline!==undefined)window.clearTimeout(deadline);
   if(version!==selectionVersion)return;
   const focusInPanel=scenes[index].contains(document.activeElement);
   const changed=target!==index;
   index=target;
   scenes.forEach((scene,i)=>{
    const active=i===index;
    scene.classList.toggle('is-active',active);
    // No entrance on first paint, idle hydration or re-selecting the same tab.
    if(changed)scene.classList.toggle('is-user-selected',active);
    scene.setAttribute('aria-hidden',String(!active));
    scene.inert=!active;
    picks[i].setAttribute('aria-selected',String(active));
    picks[i].tabIndex=active?0:-1;
   });
   stage.setAttribute('aria-busy','false');
   carousel.querySelector('[data-product-announcement]').textContent=`${picks[index].dataset.productName}. ${index+1} из ${scenes.length}`;
   if(focusInPanel)picks[index].focus({preventScroll:true});
  });
 }
 picks.forEach((pick,i)=>{
  pick.addEventListener('click',()=>select(i));
  pick.addEventListener('keydown',event=>{
   if(event.altKey||event.ctrlKey||event.metaKey) return;
   let next;
   if(event.key==='ArrowRight') next=requestedIndex+1;
   else if(event.key==='ArrowLeft') next=requestedIndex-1;
   else if(event.key==='Home') next=0;
   else if(event.key==='End') next=scenes.length-1;
   else return;
   event.preventDefault();select(next);picks[requestedIndex].focus({preventScroll:true});
  });
 });
 carousel.querySelector('[data-product-prev]').addEventListener('click',()=>select(requestedIndex-1));
 carousel.querySelector('[data-product-next]').addEventListener('click',()=>select(requestedIndex+1));
 carousel.addEventListener('keydown',event=>{
  if(event.target.closest('[role=tablist]')||event.altKey||event.ctrlKey||event.metaKey) return;
  if(event.key==='ArrowLeft'||event.key==='ArrowRight'){
   event.preventDefault();select(requestedIndex+(event.key==='ArrowRight'?1:-1));picks[requestedIndex].focus({preventScroll:true});
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
  if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.35) select(requestedIndex+(dx<0?1:-1));
 });
 stage.addEventListener('pointercancel',()=>pointerStart=null);
 stage.addEventListener('lostpointercapture',()=>pointerStart=null);
 stage.addEventListener('dragstart',event=>event.preventDefault());
 let lastWheel=0,lastWheelEvent=0,wheelDistance=0;
 stage.addEventListener('wheel',event=>{
  if(event.ctrlKey||Math.abs(event.deltaX)<Math.abs(event.deltaY)*1.4||event.deltaX===0) return;
  event.preventDefault();const now=Date.now();
  if(now-lastWheelEvent>220) wheelDistance=0;
  lastWheelEvent=now;if(now-lastWheel<600) return;
  wheelDistance+=event.deltaX*(event.deltaMode===1?16:event.deltaMode===2?stage.clientWidth:1);
  if(Math.abs(wheelDistance)<55) return;
  lastWheel=now;select(requestedIndex+(wheelDistance>0?1:-1));wheelDistance=0;
 },{passive:false});
 // Warm one inactive scene at a time after initial load, without autoplay.
 // Explicit navigation still works with data saver or a slow connection.
 let idleScheduled=false;
 function canWarm(){
  const connection=navigator.connection;
  return !document.hidden&&!menu?.open&&!connection?.saveData&&!/^(slow-)?2g$/.test(connection?.effectiveType||'');
 }
 function scheduleIdleScene(){
  if(idleScheduled||!canWarm())return;
  if(scenes.every(scene=>preparedScenes.has(scene)))return;
  idleScheduled=true;
  const warm=()=>{
   idleScheduled=false;
   // Settings or dialog state can change after this idle job was queued.
   if(!canWarm())return;
   const scene=scenes.find(scene=>!preparedScenes.has(scene));
   if(scene)hydrateScene(scene).then(scheduleIdleScene);
  };
  if('requestIdleCallback' in window)window.requestIdleCallback(warm);
  else window.setTimeout(warm,1200);
 }
 if(document.readyState==='complete')scheduleIdleScene();
 else window.addEventListener('load',scheduleIdleScene,{once:true});
 const resumeWarm=()=>{if(document.readyState==='complete')scheduleIdleScene();};
 document.addEventListener('visibilitychange',()=>{pointerStart=null;resumeWarm();});
 navigator.connection?.addEventListener?.('change',resumeWarm);
 menu?.addEventListener('close',resumeWarm);
})();

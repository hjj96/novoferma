const { chromium } = require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const rows=[];
 for(const w of [320,375,700,768,1024,1440]) for(const name of ['index','catalogue','about','partners','where-to-buy','contacts','product-frikadelki-klassicheskie']){
 const p=await b.newPage({viewport:{width:w,height:900},reducedMotion:'reduce'}); await p.goto('http://127.0.0.1:8765/output/concept/'+name+'.html');await p.evaluate(()=>document.fonts.ready);
 rows.push({name,width:w,elements:await p.evaluate(()=>[...document.querySelectorAll('h1,h2,h3,p,.hand,.hero-copy>p,.button,.meat-filters button,.category-filters button,.search input,.search-clear,.footer-bottom a,.footer-mail,.menu-toggle,.city-panel input,.city-panel select,.product-meta,.form-hint,.eyebrow')].filter(e=>e.getClientRects().length && !e.closest('[hidden]')).map(e=>{let c=getComputedStyle(e),r=e.getBoundingClientRect(),bg=null,a=e; while(a){let v=getComputedStyle(a).backgroundColor;if(v!=='rgba(0, 0, 0, 0)'){bg=v;break} a=a.parentElement}return{tag:e.tagName,cls:e.className,html:e.outerHTML.slice(0,400),text:e.textContent.trim().replace(/\s+/g,' ').slice(0,90),family:c.fontFamily,size:c.fontSize,weight:c.fontWeight,line:c.lineHeight,letter:c.letterSpacing,transform:c.transform,color:c.color,bg,width:Math.round(r.width),height:Math.round(r.height),x:Math.round(r.x),right:Math.round(r.right)}}))}); await p.close();
 }
 fs.writeFileSync('tmp/type-audit-final.json',JSON.stringify(rows,null,2));await b.close();
 console.log(JSON.stringify(rows.map(r=>({page:r.name,w:r.width,hand:r.elements.filter(e=>e.cls.includes('hand')).map(e=>({text:e.text,size:e.size,color:e.color})),tinyControls:r.elements.filter(e=>(e.tag==='BUTTON'||e.tag==='INPUT'||e.cls.includes('button'))&&(e.width<44||e.height<44)).map(e=>({cls:e.cls,text:e.text,size:e.size,w:e.width,h:e.height}))})),null,2))
})();

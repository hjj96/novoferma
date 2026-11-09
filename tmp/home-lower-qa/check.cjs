const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({reducedMotion:'reduce'});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 async function capture(label,width){
  await page.setViewportSize({width,height:950});
  await page.goto('http://127.0.0.1:63516/output/concept/index.html',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  await page.locator('.where-preview').scrollIntoViewIfNeeded();
  await page.waitForTimeout(200);
  const bounds=await page.evaluate(()=>{const t=document.querySelector('#protein').getBoundingClientRect(),b=document.querySelector('.where-preview').getBoundingClientRect();return {x:0,y:t.top+scrollY,width:innerWidth,height:b.bottom-t.top};});
  await page.screenshot({path:`tmp/home-lower-qa/${label}-${width}.png`,fullPage:true});
  for(const id of ['protein','cooperation','where-preview']) await page.locator(id==='where-preview'?'.where-preview':`#${id}`).screenshot({path:`tmp/home-lower-qa/${label}-${width}-${id}.png`});
 }
 await page.route('**/index.html',r=>r.fulfill({contentType:'text/html',body:fs.readFileSync('tmp/home-lower-before/index.html','utf8')}));
 await capture('before',1440);
 await page.unroute('**/index.html');
 const results=[];
 for(const width of [320,390,768,900,1024,1440,1920]){
  await capture('after',width);
  const info=await page.evaluate(()=>{
   const bounds=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
   return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,headings:[...document.querySelectorAll('.home-section-title')].map(h=>({text:h.innerText,font:getComputedStyle(h).fontFamily,size:parseFloat(getComputedStyle(h).fontSize),weight:getComputedStyle(h).fontWeight,fits:h.scrollWidth<=h.clientWidth,rect:bounds(h)})),sections:[...document.querySelectorAll('#protein,#cooperation,.where-preview')].map(s=>({id:s.id||s.className,rect:bounds(s),background:getComputedStyle(s).backgroundColor})),badImages:[...document.querySelectorAll('#protein img')].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),cardCount:document.querySelectorAll('#products .product-card').length};
  });
  assert.equal(info.width,info.scrollWidth,`Page overflow ${width}`);
  assert.equal(info.headings.length,3);
  assert.equal(info.cardCount,4);
  assert.equal(info.badImages.length,0);
  for(const h of info.headings){assert(h.fits,`${h.text} overflows ${width}`);assert.equal(h.weight,'850');assert(h.size>=39);assert(h.rect.x>=0&&h.rect.right<=width);}
  const ids=await page.locator('[id]').evaluateAll(els=>els.map(e=>e.id));assert.equal(ids.length,new Set(ids).size);
  results.push(info);
 }
 for(const [selector,destination] of [['#cooperation a','partners.html'],['.where-preview a[href="where-to-buy.html"]','where-to-buy.html'],['.where-preview a[href="contacts.html"]','contacts.html']]){
  await page.goto('http://127.0.0.1:63516/output/concept/index.html',{waitUntil:'networkidle'});
  await page.locator(selector).click();await page.waitForURL(`**/${destination}`);
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync('tmp/home-lower-qa/verification.json',JSON.stringify({results,navigation:'pass',pageErrors:errors},null,2));
 console.log(JSON.stringify(results.map(x=>({width:x.width,headings:x.headings.map(h=>({text:h.text,size:h.size,weight:h.weight})),overflow:false}))));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({reducedMotion:'reduce'});
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const results=[];
 for(const width of [320,390,768,1024,1440]){
  await page.setViewportSize({width,height:950});
  const previews=[];
  for(const name of ['about','index']){
   await page.goto(`http://127.0.0.1:61633/output/concept/${name}.html`,{waitUntil:'networkidle'});
   await page.evaluate(()=>document.fonts.ready);
   const section=page.locator('.about-products');
   await section.scrollIntoViewIfNeeded();
   await page.waitForTimeout(150);
   const metrics=await section.evaluate(s=>{
    const style=e=>{const c=getComputedStyle(e);const r=e.getBoundingClientRect();return {width:r.width,height:r.height,color:c.color,font:c.font,fontSize:c.fontSize,lineHeight:c.lineHeight,background:c.backgroundColor,padding:c.padding,gap:c.gap,columns:c.gridTemplateColumns};};
    const h=s.querySelector('h2');
    return {viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,section:style(s),shell:style(s.querySelector('.about-shell')),heading:style(h),cta:style(s.querySelector('.about-pill')),grid:style(s.querySelector('.product-grid')),cards:[...s.querySelectorAll('.product-card')].map(style),headingText:h.innerText,links:[...s.querySelectorAll('a')].map(a=>a.getAttribute('href')),badImages:[...s.querySelectorAll('img')].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),headingFits:h.scrollWidth<=h.clientWidth};
   });
   assert.equal(metrics.pageWidth,width,`${name} overflow at ${width}`);
   assert.equal(metrics.badImages.length,0);
   assert.equal(metrics.cards.length,4);
   assert(metrics.cards.every(c=>c.width>0&&c.height>0));
   assert(metrics.headingFits,`${name} title overflow at ${width}`);
   if(name==='index'){
    assert.equal(await page.locator('#products').count(),1);
    assert.equal(await page.locator('h1').count(),1);
    const ids=await page.locator('[id]').evaluateAll(els=>els.map(e=>e.id));
    assert.equal(ids.length,new Set(ids).size,'Duplicate IDs');
    await section.screenshot({path:`tmp/home-catalogue-qa/home-${width}.png`});
   }
   previews.push(metrics);
  }
  assert.deepEqual(previews[1],previews[0],`Homepage preview differs from About at ${width}`);
  results.push({width,matchingAbout:true,cards:previews[1].cards.length,columns:previews[1].grid.columns});
 }
 const section=page.locator('#products');
 await section.getByRole('link',{name:'Весь каталог'}).click();
 await page.waitForURL('**/catalogue.html');
 await page.goBack();
 await page.locator('#products .product-card a').first().click();
 await page.waitForURL('**/product-popsy.html');
 assert.deepEqual(errors,[]);
 fs.writeFileSync('tmp/home-catalogue-qa/verification.json',JSON.stringify({results,catalogueNavigation:'pass',productNavigation:'pass',pageErrors:errors},null,2));
 console.log(JSON.stringify(results));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

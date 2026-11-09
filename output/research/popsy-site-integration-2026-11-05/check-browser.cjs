const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const ROOT=path.resolve(__dirname,'../../..'),SITE=path.join(ROOT,'output/concept'),OUT=__dirname;
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--allow-file-access-from-files']});
 const page=await browser.newPage({reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));const checks=[];
 for(const width of [1440,390,320]){
  await page.setViewportSize({width,height:1000});
  await page.goto('file://'+SITE+'/index.html',{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
  const home=page.locator('#products');await home.scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>{const i=document.querySelector('#products [data-product-id="popsy"] img');return i?.complete&&i.naturalWidth>0});
  const homeState=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,featured:[...document.querySelectorAll('#products .product-card')].map(n=>n.dataset.productId),pops:[...document.querySelectorAll('#products [data-product-id="popsy"] img')].map(i=>({src:i.currentSrc,loaded:i.complete&&i.naturalWidth>0}))}));
  await home.screenshot({path:path.join(OUT,'home-products-'+width+'.png')});checks.push({page:'home',...homeState});
  await page.locator('#products [data-product-id="popsy"] a').click();await page.waitForURL('**/product-popsy.html');
  await page.locator('.popsy-lifestyle').scrollIntoViewIfNeeded();await page.locator('.product-card').last().scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:path.join(OUT,'popsy-'+width+'.png'),fullPage:true});
  checks.push(await page.evaluate(()=>({page:'popsy',width:innerWidth,scroll:document.documentElement.scrollWidth,h1:document.querySelector('h1')?.textContent,rock:document.querySelector('.popsy-rock-art')?.currentSrc,lifestyle:document.querySelector('.popsy-lifestyle')?.currentSrc,broken:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),buy:[...document.querySelectorAll('main a')].some(a=>a.getAttribute('href')==='where-to-buy.html?product=popsy')})));
 }
 const result={result:checks.every(c=>c.scroll<=c.width&&(c.page==='home'?c.featured[0]==='popsy'&&c.pops.every(i=>i.loaded):c.rock?.includes('popsy-rock-v3')&&c.lifestyle?.includes('popsy-lifestyle-v3')&&c.broken.length===0&&c.buy))&&errors.length===0?'pass':'fail',checks,errors};
 fs.writeFileSync(path.join(OUT,'browser-checks.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));await browser.close();if(result.result!=='pass')process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs=require('fs'),assert=require('assert/strict');
const dir='output/research/fibriki-ink-match-v10/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}),page=await browser.newPage();
 const viewports=[],errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:950});
  await page.goto('http://127.0.0.1:8765/output/concept/catalogue.html?preview=fibriki-v10#novelties',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const card=page.locator('[data-product-id="fibriki"]');
  await card.scrollIntoViewIfNeeded();await page.waitForTimeout(900);
  const check=await card.evaluate(c=>{const i=c.querySelector('img.tilt-plane');return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,cardCount:document.querySelectorAll('.catalogue-grid > .product-card').length,source:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth===800,link:c.querySelector('a').getAttribute('href')};});
  assert(check.loaded);assert(check.source.includes('fibriki-pack-v10.webp'));assert.equal(check.cardCount,16);assert(check.documentWidth<=width);
  await card.screenshot({path:dir+'card-'+width+'.png'});viewports.push(check);
  if(width===1440){
   const cards=page.locator('.catalogue-grid > .product-card');await cards.nth(12).scrollIntoViewIfNeeded();await page.waitForTimeout(800);
   const a=await cards.nth(12).boundingBox(),b=await cards.nth(15).boundingBox(),g=await page.locator('.catalogue-grid').boundingBox();
   await page.screenshot({path:dir+'catalogue-final-row.png',fullPage:true,clip:{x:g.x,y:a.y+await page.evaluate(()=>scrollY),width:g.width,height:Math.max(a.height,b.height)+18}});
  }
 }
 const {data,info}=await sharp('output/concept/assets/novelty-packaging/fibriki-pack-v10.webp').ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let transparentBorder=true;for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if((x===0||y===0||x===info.width-1||y===info.height-1)&&data[(y*info.width+x)*4+3]!==0)transparentBorder=false;
 assert(transparentBorder);assert.equal(errors.length,0);
 const result={viewports,canvas:[info.width,info.height],transparentBorder,errors};fs.writeFileSync(dir+'checks.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

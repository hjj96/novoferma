const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
const dir='output/research/fibriki-ink-match-v10/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:950}});
 let candidate=false;
 await page.route('**/fibriki-pack-v9.webp*',route=>candidate?route.fulfill({contentType:'image/webp',body:fs.readFileSync(dir+'fibriki-pack-v10.webp')}):route.continue());
 for(const version of [9,10]){
  candidate=version===10;
  await page.goto('http://127.0.0.1:8765/output/concept/catalogue.html?preview=ink-v'+version+'#novelties',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const cards=page.locator('.catalogue-grid > .product-card');
  await cards.nth(12).scrollIntoViewIfNeeded();
  await page.waitForTimeout(1000);
  const a=await cards.nth(12).boundingBox(),b=await cards.nth(15).boundingBox(),g=await page.locator('.catalogue-grid').boundingBox();
  await page.screenshot({path:dir+'catalogue-row-v'+version+'.png',fullPage:true,clip:{x:g.x,y:a.y+await page.evaluate(()=>scrollY),width:g.width,height:Math.max(a.height,b.height)+18}});
 }
 await browser.close();
 console.log('Saved real-grid previews for F9 and F10; site files unchanged.');
})().catch(e=>{console.error(e);process.exit(1)});

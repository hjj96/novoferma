const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs=require('fs'),assert=require('assert/strict'),crypto=require('crypto');
const dir='output/research/fibriki-herbs-v11/';
const base='http://127.0.0.1:8765/output/concept/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}),page=await browser.newPage();
 const viewports=[],errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()})});
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:950});
  await page.goto(base+'catalogue.html?preview=fibriki-herbs-v11#novelties',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const card=page.locator('[data-product-id="fibriki"]');
  await card.scrollIntoViewIfNeeded();await page.waitForTimeout(500);
  const check=await card.evaluate(c=>{const i=c.querySelector('img.tilt-plane');return {page:'catalogue',width:innerWidth,documentWidth:document.documentElement.scrollWidth,cardCount:document.querySelectorAll('.catalogue-grid > .product-card').length,source:i.currentSrc,loaded:i.complete&&i.naturalWidth>0,naturalWidth:i.naturalWidth,link:c.querySelector('a').getAttribute('href')};});
  assert(check.loaded);assert(check.source.includes('fibriki-pack-v11-'));assert.equal(check.cardCount,16);assert(check.documentWidth<=width);
  await card.screenshot({path:dir+'card-'+width+'.png'});viewports.push(check);
  if(width===1440){
   const cards=page.locator('.catalogue-grid > .product-card');await cards.nth(12).scrollIntoViewIfNeeded();await page.waitForTimeout(500);
   const a=await cards.nth(12).boundingBox(),b=await cards.nth(15).boundingBox(),g=await page.locator('.catalogue-grid').boundingBox();
   await page.screenshot({path:dir+'catalogue-final-row.png',fullPage:true,clip:{x:g.x,y:a.y+await page.evaluate(()=>scrollY),width:g.width,height:Math.max(a.height,b.height)+18}});
  }
  await card.locator('a.product-card-link').click();await page.waitForURL('**/product-fibriki.html');await page.waitForLoadState('networkidle');
  await page.evaluate(()=>document.fonts.ready);
  const detail=page.locator('.detail-packshot');await detail.scrollIntoViewIfNeeded();
  const d=await detail.evaluate(i=>({page:'product-fibriki',width:innerWidth,documentWidth:document.documentElement.scrollWidth,source:i.currentSrc,loaded:i.complete&&i.naturalWidth>0,naturalWidth:i.naturalWidth}));
  assert(d.loaded);assert(d.source.includes('fibriki-pack-v11-'));assert(d.documentWidth<=width);
  await page.locator('.detail-visual').screenshot({path:dir+'detail-'+width+'.png'});viewports.push(d);
 }
 const {data,info}=await sharp('output/concept/assets/novelty-packaging/fibriki-pack-v11.webp').ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let transparentBorder=true;for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if((x===0||y===0||x===info.width-1||y===info.height-1)&&data[(y*info.width+x)*4+3]!==0)transparentBorder=false;
 assert(transparentBorder);assert.equal(errors.length,0);assert.equal(failed.length,0);
 const before=JSON.parse(fs.readFileSync(dir+'before-asset-variants.json')),after=JSON.parse(fs.readFileSync('output/concept/asset-variants.json'));
 let otherAssetsPreserved=0;
 for(const [source,entry] of Object.entries(before.assets)){
  if(source.includes('fibriki-pack-v10'))continue;
  assert.deepEqual(after.assets[source],entry);
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync('output/concept/'+source)).digest('hex'),entry.sourceSha256);
  otherAssetsPreserved++;
 }
 const newVariants=after.assets['assets/novelty-packaging/fibriki-pack-v11.webp'].variants;
 assert.deepEqual(newVariants.map(v=>v.width),[400,800]);assert(newVariants.every(v=>v.alphaMaxDifference===0));
 const result={viewports,canvas:[info.width,info.height],transparentBorder,otherAssetsPreserved,newVariants,errors,failed};fs.writeFileSync(dir+'checks.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({viewports,transparentBorder,otherAssetsPreserved,errors,failed}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

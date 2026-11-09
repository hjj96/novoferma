const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs=require('fs'),crypto=require('crypto');
const dir='output/research/novelty-color-match/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage(),errors=[],viewports=[];
 page.on('pageerror',e=>errors.push(e.message));
 for(const width of [1440,768,390,320]){
  await page.setViewportSize({width,height:950});
  await page.goto('http://127.0.0.1:8765/output/concept/catalogue.html?preview=novelty-color-match#novelties',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  await page.locator('.catalogue-novelties').scrollIntoViewIfNeeded();
  await page.waitForTimeout(450);
  const check=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,mainProducts:document.querySelectorAll('.catalogue-grid .product-card').length,novelties:[...document.querySelectorAll('.newcomer-card .novelty-packshot img')].map(i=>({source:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth===800,width:i.width,height:i.height})),cardBackgrounds:[...document.querySelectorAll('.newcomer-card')].map(el=>getComputedStyle(el).backgroundColor)}));
  if(check.documentWidth>width||check.mainProducts!==14||check.novelties.length!==2||check.novelties.some(i=>!i.loaded)||!check.novelties[0].source.includes('fibriki-pack-v8.webp')||!check.novelties[1].source.includes('lulia-mini-pack-v3.webp'))throw Error(JSON.stringify(check));
  await page.locator('.catalogue-novelties').screenshot({path:dir+`catalogue-${width}.png`});
  viewports.push(check);
 }
 await page.locator('.newcomer-card .text-link').first().click();
 await page.waitForURL('**/where-to-buy.html?product=fibriki');
 if(await page.locator('#wanted-product').inputValue()!=='fibriki')throw Error('Fibriki selection failed');
 const file='output/concept/assets/novelty-packaging/fibriki-pack-v8.webp';
 const {data,info}=await sharp(file).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let transparentBorder=true;
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if((x===0||y===0||x===info.width-1||y===info.height-1)&&data[(y*info.width+x)*4+3]!==0)transparentBorder=false;
 const baseline=JSON.parse(fs.readFileSync(dir+'preserved-assets-before.json'));
 const preserved=Object.entries(baseline).every(([f,h])=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')===h);
 if(errors.length||!transparentBorder||!preserved)throw Error(JSON.stringify({errors,transparentBorder,preserved}));
 const result={viewports,alpha:{canvas:[info.width,info.height],transparentBorder},preservedOtherPackages:preserved,fibrikiSelection:true,errors};
 fs.writeFileSync(dir+'checks.json',JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

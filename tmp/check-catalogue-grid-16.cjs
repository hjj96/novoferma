const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const fs=require('fs'),crypto=require('crypto'),assert=require('assert/strict');
const dir='output/research/catalogue-grid-16/';
const base='http://127.0.0.1:8765/output/concept/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage(),errors=[],requests=[],viewports=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400)requests.push({url:r.url(),status:r.status()})});
 for(const width of [1440,768,390,320]){
  await page.setViewportSize({width,height:950});
  await page.goto(base+'catalogue.html?preview=grid-16-v9',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const cards=page.locator('.catalogue-grid > .product-card');
  assert.equal(await cards.count(),16);
  for(let i=0;i<16;i++){await cards.nth(i).scrollIntoViewIfNeeded();await page.waitForTimeout(70);}
  await page.waitForFunction(()=>[...document.querySelectorAll('.catalogue-grid img.tilt-plane')].every(i=>i.complete&&i.naturalWidth===800));
  await page.waitForTimeout(850);
  const check=await page.evaluate(()=>{
   const grid=document.querySelector('.catalogue-grid');
   return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,columns:getComputedStyle(grid).gridTemplateColumns.split(' ').length,separateNoveltySection:!!document.querySelector('.catalogue-novelties'),filters:document.querySelectorAll('.catalogue-filters,.catalogue-search').length,cards:[...grid.children].map(c=>{
    const stage=c.querySelector('.packshot-stage'),im=stage.querySelector('img'),title=c.querySelector('.product-title'),style=getComputedStyle(stage),r=c.getBoundingClientRect();
    return {id:c.dataset.productId,name:c.querySelector('h3').textContent,meta:c.querySelector('.product-meta').textContent,source:im.getAttribute('src'),link:title.getAttribute('href'),classes:c.className,stage:{width:stage.clientWidth,height:stage.clientHeight,ratio:style.aspectRatio,border:style.borderWidth,padding:style.padding},title:{font:getComputedStyle(title.querySelector('h3')).fontSize},width:r.width,loaded:im.complete&&im.naturalWidth===800,opacity:getComputedStyle(c).opacity};
   })};
  });
  assert(check.documentWidth<=width);
  assert.equal(check.columns,width>1099?4:width>699?3:2);
  assert.equal(check.separateNoveltySection,false);
  assert.equal(check.filters,0);
  assert(check.cards.every(c=>c.loaded&&c.classes.includes('packshot-preview')&&c.opacity==='1'));
  assert(check.cards.every(c=>JSON.stringify(c.stage)===JSON.stringify(check.cards[0].stage)));
  assert(check.cards.slice(14).every(c=>c.meta==='Из курицы'));
  assert(check.cards[14].source.includes('fibriki-pack-v9.webp'));
  assert(check.cards[15].source.includes('lulia-mini-pack-v3.webp'));
  await page.locator('.catalogue-page').screenshot({path:dir+`catalogue-${width}.png`});
  if(width===1440){
   await cards.nth(12).scrollIntoViewIfNeeded();
   const box=await page.locator('.catalogue-grid').boundingBox(),first=await cards.nth(12).boundingBox(),last=await cards.nth(15).boundingBox();
   await page.screenshot({path:dir+'catalogue-last-row.png',fullPage:true,clip:{x:box.x,y:first.y+await page.evaluate(()=>scrollY),width:box.width,height:Math.max(first.height,last.height)+18}});
  }
  viewports.push(check);
 }
 const selection={};
 for(const slug of ['fibriki','lulia-mini']){
  await page.goto(base+'catalogue.html?preview=grid-16-v9',{waitUntil:'networkidle'});
  await page.locator(`[data-product-id="${slug}"] .product-title`).click();
  await page.waitForURL('**/where-to-buy.html?product='+slug);
  selection[slug]=await page.locator('#wanted-product').inputValue();
  assert.equal(selection[slug],slug);
 }
 const alpha={};
 for(const [slug,version] of [['fibriki',9],['lulia-mini',3]]){
  const {data,info}=await sharp(`output/concept/assets/novelty-packaging/${slug}-pack-v${version}.webp`).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  let transparentBorder=true;
  for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if((x===0||y===0||x===info.width-1||y===info.height-1)&&data[(y*info.width+x)*4+3]!==0)transparentBorder=false;
  alpha[slug]={canvas:[info.width,info.height],transparentBorder};assert(transparentBorder);
 }
 const baseline=JSON.parse(fs.readFileSync('output/research/novelty-color-match/preserved-assets-before.json'));
 const preserved=Object.entries(baseline).every(([f,h])=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')===h);
 const products=JSON.parse(fs.readFileSync('output/concept/products.json'));
 const manifest=JSON.parse(fs.readFileSync('output/concept/site-manifest.json'));
 assert(preserved);assert.equal(products.length,14);assert.equal(manifest.pages.length,20);assert.equal(errors.length,0);assert.equal(requests.length,0);
 const result={viewports,alpha,preservedOriginalPackages:preserved,confirmedProducts:products.length,pageCount:manifest.pages.length,selection,errors,failedRequests:requests};
 fs.writeFileSync(dir+'checks.json',JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({viewports:viewports.map(v=>({width:v.width,columns:v.columns,cards:v.cards.length,overflow:v.documentWidth-v.width})),alpha,preserved,selection,errors,failedRequests:requests}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

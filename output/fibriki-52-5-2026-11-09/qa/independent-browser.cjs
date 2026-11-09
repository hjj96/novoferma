const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const site='/Users/andrey/Desktop/сайт нф/output/concept';
const out=__dirname;
const report={checkedAt:new Date().toISOString(),mode:'local file preview in Chrome, allow-file-access-from-files',widths:[],pageErrors:[],consoleErrors:[],failedRequests:[]};

async function settle(page){
 await page.evaluate(()=>document.fonts.ready);
 await page.evaluate(async()=>{
  for(let y=0;y<document.body.scrollHeight;y+=650){window.scrollTo({top:y,behavior:'instant'});await new Promise(r=>setTimeout(r,40));}
  window.scrollTo({top:0,behavior:'instant'});
  await Promise.all([...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r})));
 });
 await page.mouse.move(0,0);
 await page.waitForTimeout(350);
}
async function metrics(page){return page.evaluate(()=>{
 const texts=[...document.querySelectorAll('main h1,main h2,main h3,main p,main dt,main dd,main summary')].filter(n=>!n.closest('.sr-only,[hidden]'));
 const overflow=texts.filter(n=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n);return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&(r.left < -1||r.right>innerWidth+1||n.scrollWidth>n.clientWidth+2)}).map(n=>({tag:n.tagName,class:n.className,text:n.innerText}));
 const nutrition=document.querySelector('.fibriki-pack-nutrition');
 const rect=n=>{if(!n)return null;const r=n.getBoundingClientRect();return{x:r.x,y:r.y+scrollY,width:r.width,height:r.height}};
 return{url:location.href,title:document.title,viewportWidth:innerWidth,documentWidth:document.documentElement.scrollWidth,textOverflow:overflow,
  brokenImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.currentSrc||i.src),
  nutrition:nutrition?{text:nutrition.innerText,role:nutrition.tagName,labelledby:nutrition.getAttribute('aria-labelledby'),heading:document.getElementById(nutrition.getAttribute('aria-labelledby'))?.innerText,rows:[...nutrition.querySelectorAll('dl>div')].map(n=>({label:n.querySelector('dt')?.innerText,value:n.querySelector('dd')?.innerText,number:n.querySelector('.fibriki-nutrition-number')?.innerText,unit:n.querySelector('.fibriki-nutrition-unit')?.innerText,box:rect(n)})),box:rect(nutrition)}:null,
  packshot:document.querySelector('.detail-packshot')?{src:document.querySelector('.detail-packshot').currentSrc,box:rect(document.querySelector('.detail-packshot'))}:null,
  productCopy:document.querySelector('.product-detail')?.innerText,
  description:document.querySelector('meta[name="description"]')?.content,
  loadedFonts:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family)
 };
});}

(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--allow-file-access-from-files']});
 for(const width of[1440,390,320]){
  const page=await browser.newPage({viewport:{width,height:width>1000?1000:844},deviceScaleFactor:1,reducedMotion:'reduce'});
  page.on('pageerror',e=>report.pageErrors.push({width,message:e.message,page:page.url()}));
  page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push({width,message:m.text(),page:page.url()})});
  page.on('requestfailed',r=>report.failedRequests.push({width,url:r.url(),failure:r.failure()?.errorText}));
  const run={width};
  await page.goto(pathToFileURL(path.join(site,'catalogue.html')).href,{waitUntil:'networkidle'});
  await settle(page);
  const card=page.locator('.product-card[data-product-id="fibriki"]');
  await card.waitFor({state:'visible'});await card.scrollIntoViewIfNeeded();await page.mouse.move(0,0);await page.waitForTimeout(200);
  await page.screenshot({path:path.join(out,`independent-catalogue-context-${width}.png`)});
  await card.screenshot({path:path.join(out,`independent-catalogue-card-${width}.png`)});
  run.catalogue=await metrics(page);
  run.card={text:await card.innerText(),href:await card.locator('a').getAttribute('href'),src:await card.locator('img').evaluate(i=>i.currentSrc)};
  await card.locator('a').click();await page.waitForURL('**/product-fibriki.html');await settle(page);
  await page.screenshot({path:path.join(out,`independent-product-full-${width}.png`),fullPage:true});
  await page.locator('.product-detail').screenshot({path:path.join(out,`independent-product-hero-${width}.png`)});
  await page.locator('.fibriki-pack-nutrition').screenshot({path:path.join(out,`independent-nutrition-${width}.png`)});
  run.product=await metrics(page);
  const n=run.product.nutrition;
  run.nutritionPassed=n?.heading.toLowerCase()==='в одной упаковке'&&n.rows.length===2&&n.rows[0].number==='52'&&n.rows[0].unit==='г'&&n.rows[0].label==='Белка'&&n.rows[1].number==='5'&&n.rows[1].unit==='г'&&n.rows[1].label==='Клетчатки'&&!/на\s*100/i.test(run.product.productCopy);
  run.flowPassed=run.card.href==='product-fibriki.html'&&run.product.title==='Фибрики — Новоферма';
  report.widths.push(run);await page.close();
 }
 await browser.close();
 report.passed=report.widths.every(r=>r.nutritionPassed&&r.flowPassed&&[r.product,r.catalogue].every(p=>p.documentWidth===p.viewportWidth&&p.textOverflow.length===0&&p.brokenImages.length===0))&&report.pageErrors.length===0&&report.consoleErrors.length===0&&report.failedRequests.length===0;
 fs.writeFileSync(path.join(out,'independent-browser-checks.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,widths:report.widths.map(r=>({width:r.width,nutritionPassed:r.nutritionPassed,flowPassed:r.flowPassed,documentWidths:[r.catalogue.documentWidth,r.product.documentWidth],overflow:[r.catalogue.textOverflow,r.product.textOverflow],brokenImages:[r.catalogue.brokenImages,r.product.brokenImages],nutrition:r.product.nutrition,packshot:r.product.packshot})),pageErrors:report.pageErrors,consoleErrors:report.consoleErrors,failedRequests:report.failedRequests},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});

const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const site='/Users/andrey/Desktop/сайт нф/output/concept';
const out=__dirname;
const novelties=['fibriki','lenivchiki','lulia-mini','popsy'];
const classic=['kotlety-kurinye','bitochki-kurinye-s-ovoshchami','ezhiki-iz-tsyplenka-s-risom','kurinyj-popkorn','naggetsy-kurinye','naggetsy-kurinye-s-syrom','naggetsy-dinozavry','naggetsy-ostrye','naggetsy-s-indeykoy-fitnes','stripsy','kotlety-po-domashnemu','kotlety-pikantnye','kotlety-po-italyanski','frikadelki-klassicheskie'];
const report={scope:'accepted task: novelty order, 400 g each, Fibriki v12 without nutrient labels',checkedAt:new Date().toISOString(),expectedOrder:[...novelties,...classic],widths:[],pageErrors:[],consoleErrors:[],failedRequests:[]};
const normalize=s=>s?.replace(/\s+/g,' ').trim();
const url=name=>pathToFileURL(path.join(site,name+'.html')).href;
async function settle(page){
 await page.evaluate(async()=>{await Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,2500))]);for(const i of document.images)i.loading='eager';await Promise.race([Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,2500))]);window.scrollTo({top:0,behavior:'instant'});});
 await page.mouse.move(0,0);await page.waitForTimeout(200);
}
async function metrics(page){return page.evaluate(()=>{
 const rect=n=>{if(!n)return null;const r=n.getBoundingClientRect();return{x:r.x,y:r.y+scrollY,width:r.width,height:r.height}};
 const textOverflow=[...document.querySelectorAll('main h1,main h2,main h3,main p,main dt,main dd,main strong,main summary')].filter(n=>{if(n.closest('.sr-only,[hidden]'))return false;const r=n.getBoundingClientRect(),s=getComputedStyle(n);return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&(r.left < -1||r.right>innerWidth+1||n.scrollWidth>n.clientWidth+2)}).map(n=>({tag:n.tagName,class:n.className,text:n.innerText}));
 return{url:location.href,title:document.title,viewportWidth:innerWidth,documentWidth:document.documentElement.scrollWidth,textOverflow,brokenImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.currentSrc||i.src),
  cards:[...document.querySelectorAll('.catalogue-grid>.product-card')].map(n=>({id:n.dataset.productId,name:n.querySelector('.product-title')?.innerText,weight:n.querySelector('.product-weight')?.innerText,src:n.querySelector('img')?.currentSrc,cardBox:rect(n),imageBox:rect(n.querySelector('img'))})),
  facts:[...document.querySelectorAll('.product-detail .product-facts>div')].map(n=>({label:n.querySelector('span')?.innerText,value:n.querySelector('strong')?.innerText})),
  detailText:document.querySelector('.product-detail')?.innerText,detailEyebrow:document.querySelector('.product-detail .detail-heading .eyebrow')?.innerText,packshot:document.querySelector('.detail-packshot')?.currentSrc,nutritionBlockPresent:!!document.querySelector('.fibriki-pack-nutrition')};
});}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--allow-file-access-from-files']});
 for(const width of[1440,390,320]){
  const page=await browser.newPage({viewport:{width,height:width>1000?1000:844},deviceScaleFactor:1,reducedMotion:'reduce'});
  page.on('pageerror',e=>report.pageErrors.push({width,page:page.url(),message:e.message}));
  page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push({width,page:page.url(),message:m.text()})});
  page.on('requestfailed',r=>report.failedRequests.push({width,url:r.url(),failure:r.failure()?.errorText}));
  const run={width,products:[]};console.log('Opening catalogue',width);await page.goto(url('catalogue'),{waitUntil:'load'});await settle(page);
  await page.screenshot({path:path.join(out,`independent-catalogue-top-${width}.png`),timeout:10000});
  const section=page.locator('.catalogue-grid');
  const crop=await section.evaluate(n=>{const cards=[...n.children].slice(0,4);const b=cards.map(c=>c.getBoundingClientRect());const x=Math.min(...b.map(r=>r.left)),y=Math.min(...b.map(r=>r.top));return{x,y:y+scrollY,width:Math.max(...b.map(r=>r.right))-x,height:Math.max(...b.map(r=>r.bottom))-y}});
  if(width!==320)await page.screenshot({path:path.join(out,`independent-first-four-${width}.png`),clip:crop,fullPage:true,timeout:10000});
  run.catalogue=await metrics(page);run.orderPassed=JSON.stringify(run.catalogue.cards.map(c=>c.id))===JSON.stringify(report.expectedOrder);run.catalogueWeightsPassed=run.catalogue.cards.slice(0,4).every(c=>normalize(c.weight)==='400 г');
  for(const id of novelties){
   console.log('Opening product',width,id);await page.goto(url('product-'+id),{waitUntil:'load'});await settle(page);
   if(id==='fibriki'&&width!==320)await page.locator('.product-detail').screenshot({path:path.join(out,`independent-${id}-hero-${width}.png`),timeout:10000});
   const m=await metrics(page);m.id=id;m.massPassed=/400 г/i.test(normalize(m.detailEyebrow)||'')||m.facts.some(f=>f.label==='Масса нетто'&&normalize(f.value)==='400 г');
   if(id==='fibriki')m.revertPassed=/fibriki-pack-v12/.test(m.packshot)&&!m.nutritionBlockPresent&&!/52\s*г|5\s*г|в одной упаковке/i.test(m.detailText);
   run.products.push(m);
  }
  report.widths.push(run);await page.close();
 }
 await browser.close();
 const manifest=JSON.parse(fs.readFileSync(path.join(site,'site-manifest.json'),'utf8'));
 report.manifestNovelties=manifest.novelties.map(p=>({id:p.id,weight:p.weight,image:p.image,packNutrition:p.packNutrition}));
 report.passed=report.widths.every(r=>r.orderPassed&&r.catalogueWeightsPassed&&r.products.every(p=>p.massPassed&&(p.id!=='fibriki'||p.revertPassed))&&[r.catalogue,...r.products].every(p=>p.viewportWidth===p.documentWidth&&p.textOverflow.length===0&&p.brokenImages.length===0))&&report.pageErrors.length===0&&report.consoleErrors.length===0&&report.failedRequests.length===0;
 fs.writeFileSync(path.join(out,'independent-browser-checks.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,widths:report.widths.map(r=>({width:r.width,orderPassed:r.orderPassed,catalogueWeightsPassed:r.catalogueWeightsPassed,products:r.products.map(p=>({id:p.id,massPassed:p.massPassed,revertPassed:p.revertPassed,documentWidth:p.documentWidth,textOverflow:p.textOverflow,brokenImages:p.brokenImages,facts:p.facts,packshot:p.packshot}))})),manifest:report.manifestNovelties,pageErrors:report.pageErrors,consoleErrors:report.consoleErrors,failedRequests:report.failedRequests},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});

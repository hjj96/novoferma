const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 for(const width of [320,390,768,899,900,1024,1440,1920]){
  const page=await browser.newPage({viewport:{width,height:1050},reducedMotion:'reduce'});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
  await page.addInitScript(()=>{Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.__copiedRequest=text}}});});
  await page.goto('http://127.0.0.1:8765/output/concept/partners.html',{waitUntil:'networkidle'});
  await page.evaluate(async()=>{await document.fonts.ready;await document.querySelector('.partners-business-scene img').decode()});
  await page.screenshot({path:`output/research/partners-compact-v1/page-${width}.png`,fullPage:true});
  await page.locator('#private-label').screenshot({path:`output/research/partners-compact-v1/stm-${width}.png`});
  const data=await page.evaluate(()=>{
   const stm=document.querySelector('#private-label'),contact=document.querySelector('#partner-contact');
   return {overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),badText:[...document.querySelectorAll('main h1,main h2,main p,main a,main button,main label,main legend')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left< -1||e.scrollWidth>e.clientWidth+2)}).map(e=>e.textContent),sections:[...document.querySelectorAll('main>section')].map(e=>e.className),noOldSections:!document.querySelector('.partners-routes,.partners-store,.partners-stm-art,.partners-stm-topics'),stmHeading:stm.querySelector('h2').textContent.trim(),stmHeight:Math.round(stm.getBoundingClientRect().height),contactTop:Math.round(contact.getBoundingClientRect().top+scrollY),formTop:Math.round(document.querySelector('#partner-request-form').getBoundingClientRect().top+scrollY),pageHeight:document.documentElement.scrollHeight};
  });
  await page.locator('.partners-business-actions a[href="#partner-contact"]').click();
  const heroContact=await page.evaluate(()=>location.hash==='#partner-contact');
  await page.locator('#private-label [data-partner-format="stm"]').click();
  const stmContact=await page.evaluate(()=>location.hash==='#partner-contact'&&document.querySelector('[name="format"]:checked').value==='stm');
  await page.locator('#partner-copy-request').click();
  const required=await page.evaluate(()=>!document.querySelector('#partner-request-form').checkValidity()&&!window.__copiedRequest);
  await page.locator('input[name="company"]').fill('QA company');
  await page.locator('input[name="contact"]').fill('qa@example.com');
  await page.locator('#partner-copy-request').click();
  const request=await page.evaluate(()=>window.__copiedRequest||'');
  const copy=request.includes('QA company')&&request.includes('qa@example.com')&&request.includes('СТМ');
  results.push({width,...data,heroContact,stmContact,required,copy,errors});await page.close();
 }
 await browser.close();
 const pass=results.every(r=>!r.overflow&&!r.broken.length&&!r.badText.length&&r.sections.length===3&&r.noOldSections&&r.stmHeading==='Ваш бренд. Наш продукт.'&&r.stmHeight<460&&r.heroContact&&r.stmContact&&r.required&&r.copy&&!r.errors.length);
 fs.writeFileSync('output/research/partners-compact-v1/qa.json',JSON.stringify({pass,results},null,2));console.log(JSON.stringify({pass,results},null,2));if(!pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

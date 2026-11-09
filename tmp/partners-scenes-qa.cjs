const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
const out='output/research/partners-scenes-v2';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 for(const width of [320,390,768,1024,1440,1920]){
  const page=await browser.newPage({viewport:{width,height:950}});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>{if(!r.url().startsWith('mailto:'))errors.push(r.url());});
  await page.addInitScript(()=>{window.copiedRequest='';Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async t=>{window.copiedRequest=t;}}});});
  await page.goto('http://127.0.0.1:8765/output/concept/partners.html',{waitUntil:'networkidle'});
  await page.evaluate(async()=>{await document.fonts.ready;for(const img of document.images){img.loading='eager';await img.decode().catch(()=>{});}for(let y=0;y<document.body.scrollHeight;y+=700){window.scrollTo({top:y,behavior:'instant'});await new Promise(r=>setTimeout(r,60));}window.scrollTo({top:0,behavior:'instant'});});
  await page.waitForTimeout(800);
  await page.screenshot({path:`${out}/partners-${width}.png`,fullPage:true});
  if(width===390||width===1440){for(const [name,selector] of [['hero','.partners-welcome'],['retail','.partners-retail'],['stm','.partners-private-label'],['contact','.partners-contact']])await page.locator(selector).screenshot({path:`${out}/${name}-${width}.png`});}
  const layout=await page.evaluate(()=>{const rectangle=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};return {documentWidth:document.documentElement.scrollWidth,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),overflowingText:[...document.querySelectorAll('main h1,main h2,main h3,main p,main a,main label,main input,main textarea')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left< -1||(!e.matches('input,textarea')&&e.scrollWidth>e.clientWidth+2))}).map(e=>({tag:e.tagName,text:e.textContent,width:e.clientWidth,scroll:e.scrollWidth})),art:[...document.querySelectorAll('.partners-scene-image')].map(i=>({image:i.getAttribute('src'),ratioPreserved:Math.abs(i.clientWidth/i.clientHeight-i.naturalWidth/i.naturalHeight)<0.015,...rectangle(i)})),sections:[...document.querySelectorAll('.partners-welcome,.partners-retail,.partners-private-label,.partners-contact')].map(e=>({class:e.className,...rectangle(e)}))};});
  const formats=[];
  for(const kind of ['retail','horeca','stm']){
   await page.locator(`[data-partner-format="${kind}"]`).click();await page.waitForTimeout(550);
   formats.push(await page.evaluate(()=>({hash:location.hash,checked:document.querySelector('[name="format"]:checked').value,hint:document.querySelector('#partner-format-help').textContent})));}
  await page.locator('[name="company"]').fill('ООО «Партнёр & Co»');await page.locator('[name="city"]').fill('Санкт-Петербург');await page.locator('[name="contact"]').fill('test@example.com');await page.locator('[name="message"]').fill('Нужна своя марка: зелёная упаковка.');
  await page.getByRole('button',{name:'Скопировать запрос',exact:true}).click();
  const copy=await page.evaluate(()=>({text:window.copiedRequest,status:document.querySelector('#partner-request-feedback').textContent}));
  await page.getByRole('button',{name:'Составить письмо',exact:true}).click();await page.waitForTimeout(150);
  const mail=await page.locator('#partner-request-feedback a').getAttribute('href');
  let menu=null;
  if(width<960){await page.locator('.menu-toggle').click();const opened=await page.locator('#site-menu').evaluate(e=>e.open);await page.keyboard.press('Escape');menu={opened,closed:await page.locator('#site-menu').evaluate(e=>!e.open)};}
  results.push({width,...layout,formats,copyCorrect:copy.text.includes('ООО «Партнёр & Co»')&&copy.text.includes('Производство под своей маркой (СТМ)')&&copy.text.includes('test@example.com'),mailCorrect:mail.startsWith('mailto:zakaz@novoferma.ru?')&&decodeURIComponent(mail).includes('Нужна своя марка: зелёная упаковка.'),menu,errors});
  await page.close();
 }
 const page=await browser.newPage({viewport:{width:390,height:950},reducedMotion:'reduce'});await page.goto('file://'+process.cwd()+'/output/concept/partners.html');await page.locator('[data-partner-format="stm"]').click();const fileMode=await page.locator('[name="format"]:checked').inputValue()==='stm';await page.close();
 await browser.close();
 const pass=results.every(r=>r.documentWidth<=r.width&&!r.brokenImages.length&&!r.overflowingText.length&&r.art.every(a=>a.ratioPreserved)&&r.formats.every((f,i)=>f.hash==='#partner-contact'&&f.checked===['retail','horeca','stm'][i])&&r.copyCorrect&&r.mailCorrect&&(!r.menu||(r.menu.opened&&r.menu.closed))&&!r.errors.length)&&fileMode;
 fs.writeFileSync(`${out}/qa.json`,JSON.stringify({pass,fileMode,results},null,2));console.log(JSON.stringify({pass,fileMode,results:results.map(({art,sections,...r})=>r)},null,2));if(!pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

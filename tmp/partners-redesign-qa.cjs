const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
const path=require('path');
const out='output/research/partners-redesign-2026-10-16';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 for(const width of [320,390,768,1024,1440,1920]){
  const page=await browser.newPage({viewport:{width,height:950}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
  for(const name of ['partners','about']){
   await page.goto(`http://127.0.0.1:8765/output/concept/${name}.html`,{waitUntil:'networkidle'});
   await page.evaluate(async()=>{await document.fonts.ready;for(const img of document.images){img.loading='eager';await img.decode().catch(()=>{});}for(let y=0;y<document.body.scrollHeight;y+=700){window.scrollTo({top:y,behavior:'instant'});await new Promise(r=>setTimeout(r,70));}window.scrollTo({top:0,behavior:'instant'});});
   await page.waitForTimeout(800);
   await page.screenshot({path:`${out}/${name}-${width}.png`,fullPage:true});
   const layout=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),h1:document.querySelector('h1')?.textContent,overflowingText:[...document.querySelectorAll('main h1,main h2,main h3,main p,main a')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left< -1||e.scrollWidth>e.clientWidth+2)}).map(e=>({tag:e.tagName,text:e.textContent,width:e.clientWidth,scroll:e.scrollWidth})),intactArt:[...document.querySelectorAll('.partner-intro-visual>img,.brand-character-art')].every(i=>{const r=i.getBoundingClientRect();return Math.abs(r.width/r.height-i.naturalWidth/i.naturalHeight)<0.01;})}));
   const links=await page.locator('main a[href]').evaluateAll(es=>es.map(e=>e.getAttribute('href')));
   let anchor=null,menu=null;
   if(name==='partners'){
    await page.getByRole('link',{name:'Обсудить поставки',exact:true}).click();await page.waitForTimeout(600);
    anchor=await page.locator('#partner-contact').evaluate(e=>({hash:location.hash,top:e.getBoundingClientRect().top,headingVisible:(()=>{const r=e.querySelector('h2').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight})(),emailVisible:(()=>{const r=e.querySelector('.partner-enquiry-email').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight})()}));
    if(width<960){await page.locator('.menu-toggle').click();const opened=await page.locator('#site-menu').evaluate(e=>e.open);await page.keyboard.press('Escape');menu={opened,closed:await page.locator('#site-menu').evaluate(e=>!e.open)};}
   }
   results.push({page:name,width,...layout,links,anchor,menu,errors:[...errors]});
  }
  await page.close();
 }
 await browser.close();
 const pass=results.every(r=>r.documentWidth<=r.width&&!r.brokenImages.length&&!r.overflowingText.length&&r.intactArt&&!r.errors.length&&(!r.anchor||(r.anchor.hash==='#partner-contact'&&r.anchor.headingVisible&&r.anchor.emailVisible))&&(!r.menu||(r.menu.opened&&r.menu.closed)));
 fs.writeFileSync(`${out}/qa.json`,JSON.stringify({pass,results},null,2));
 console.log(JSON.stringify({pass,results:results.map(({links,...r})=>r)},null,2));
 if(!pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

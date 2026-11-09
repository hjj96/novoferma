const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 for(const width of [320,390,768,1024,1440,1920]){
  const page=await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce'});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
  await page.goto('http://127.0.0.1:8765/output/concept/partners.html',{waitUntil:'networkidle'});
  await page.evaluate(async()=>{await document.fonts.ready;await document.querySelector('.partners-business-scene img').decode();await document.querySelector('.partners-business-floor img').decode();});
  await page.screenshot({path:`output/research/partners-hero-v5/viewport-${width}.png`});
  await page.locator('.partners-business').screenshot({path:`output/research/partners-hero-v5/hero-${width}.png`});
  const data=await page.evaluate(()=>{
   const art=document.querySelector('.partners-business-scene img'),r=art.getBoundingClientRect();
   return {overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),badText:[...document.querySelectorAll('.partners-business h1,.partners-business h1>*,.partners-business p,.partners-business a')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left< -1||e.scrollWidth>e.clientWidth+2)}).map(e=>e.textContent),artRatio:Math.abs(r.width/r.height-art.naturalWidth/art.naturalHeight)<.01,artBounds:r.x>=0&&r.right<=innerWidth,heading:document.querySelector('h1').innerText};
  });
  await page.getByRole('link',{name:'Стать партнёром',exact:true}).click();
  const contact=await page.evaluate(()=>location.hash==='#partner-contact');
  await page.locator('[data-partner-format="stm"]').click();
  const format=await page.locator('[name="format"]:checked').inputValue();
  const catalogue=await page.locator('.partners-business-actions a[href="catalogue.html"]').count()===1;
  results.push({width,...data,contact,format,catalogue,errors});await page.close();
 }
 await browser.close();
 const pass=results.every(r=>!r.overflow&&!r.broken.length&&!r.badText.length&&r.artRatio&&r.artBounds&&r.contact&&r.format==='stm'&&r.catalogue&&!r.errors.length);
 fs.writeFileSync('output/research/partners-hero-v5/qa.json',JSON.stringify({pass,results},null,2));console.log(JSON.stringify({pass,results},null,2));if(!pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 for(const width of [320,390,768,1024,1440,1920]){
  const page=await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce'});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
  await page.goto('http://127.0.0.1:8765/output/concept/partners.html',{waitUntil:'networkidle'});
  await page.locator('.partners-route[href="#partner-retail"]').click();
  await page.evaluate(async()=>{await document.fonts.ready;await document.querySelector('.partners-store-art img').decode();});
  await page.locator('.partners-store').screenshot({path:`output/research/partners-store-v1/retail-${width}.png`});
  await page.screenshot({path:`output/research/partners-store-v1/viewport-${width}.png`});
  const data=await page.evaluate(()=>{
   const art=document.querySelector('.partners-store-art img'),r=art.getBoundingClientRect();
   return {overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),badText:[...document.querySelectorAll('.partners-store h2,.partners-store h3,.partners-store p,.partners-store a,.partners-store figcaption')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left< -1||e.scrollWidth>e.clientWidth+2)}).map(e=>e.textContent),artRatio:Math.abs(r.width/r.height-art.naturalWidth/art.naturalHeight)<.01,artBounds:r.x>=0&&r.right<=innerWidth,artNoCrop:getComputedStyle(art).objectFit!=='cover',retailRoute:location.hash==='#partner-retail'};
  });
  await page.locator('.partners-store [data-partner-format="retail"]').click();
  const retailContact=await page.evaluate(()=>location.hash==='#partner-contact'&&document.querySelector('[name="format"]:checked').value==='retail');
  await page.locator('.partners-route[href="#partner-horeca"]').click();
  const horecaRoute=await page.evaluate(()=>location.hash==='#partner-horeca');
  await page.locator('.partners-store [data-partner-format="horeca"]').click();
  const horecaContact=await page.evaluate(()=>location.hash==='#partner-contact'&&document.querySelector('[name="format"]:checked').value==='horeca');
  await page.locator('.partners-store a[href="catalogue.html"]').click();
  const catalogue=page.url().endsWith('/catalogue.html')&&await page.locator('h1').count()===1;
  results.push({width,...data,retailContact,horecaRoute,horecaContact,catalogue,errors});await page.close();
 }
 await browser.close();
 const pass=results.every(r=>!r.overflow&&!r.broken.length&&!r.badText.length&&r.artRatio&&r.artBounds&&r.artNoCrop&&r.retailRoute&&r.retailContact&&r.horecaRoute&&r.horecaContact&&r.catalogue&&!r.errors.length);
 fs.writeFileSync('output/research/partners-store-v1/qa.json',JSON.stringify({pass,results},null,2));console.log(JSON.stringify({pass,results},null,2));if(!pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

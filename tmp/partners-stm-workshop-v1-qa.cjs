const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 for(const width of [320,390,768,899,900,1024,1440,1920]){
  const page=await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce'});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
  await page.goto('http://127.0.0.1:8765/output/concept/partners.html',{waitUntil:'networkidle'});
  await page.locator('.partners-route[href="#private-label"]').click();
  await page.evaluate(async()=>{await document.fonts.ready;await document.querySelector('.partners-stm-art img').decode();});
  await page.locator('.partners-private-label').screenshot({path:`output/research/partners-stm-workshop-v1/stm-${width}.png`});
  await page.screenshot({path:`output/research/partners-stm-workshop-v1/viewport-${width}.png`});
  const data=await page.evaluate(()=>{
   const section=document.querySelector('#private-label'),art=section.querySelector('img'),r=art.getBoundingClientRect();
   return {overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),badText:[...section.querySelectorAll('h2,h2>*,p,a')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left< -1||e.scrollWidth>e.clientWidth+2)}).map(e=>e.textContent),artRatio:Math.abs(r.width/r.height-art.naturalWidth/art.naturalHeight)<.01,artBounds:r.x>=0&&r.right<=innerWidth,artNoCrop:getComputedStyle(art).objectFit!=='cover',background:getComputedStyle(section).backgroundColor,route:location.hash==='#private-label',removedDetails:!section.querySelector('.partners-stm-topics,figcaption'),heading:section.querySelector('h2').textContent.trim()};
  });
  await page.locator('#private-label [data-partner-format="stm"]').click();
  const contact=await page.evaluate(()=>location.hash==='#partner-contact'&&document.querySelector('[name="format"]:checked').value==='stm');
  const focus=await page.locator('#private-label a').evaluate(e=>e.getAttribute('href'))==='#partner-contact';
  results.push({width,...data,contact,focus,errors});await page.close();
 }
 await browser.close();
 const pass=results.every(r=>!r.overflow&&!r.broken.length&&!r.badText.length&&r.artRatio&&r.artBounds&&r.artNoCrop&&r.route&&r.contact&&r.focus&&r.removedDetails&&r.heading==='Ваш бренд. Наш продукт.'&&r.background==='rgb(255, 245, 227)'&&!r.errors.length);
 fs.writeFileSync('output/research/partners-stm-workshop-v1/qa.json',JSON.stringify({pass,results},null,2));console.log(JSON.stringify({pass,results},null,2));if(!pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

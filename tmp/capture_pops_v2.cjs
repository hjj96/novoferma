const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');
const path=require('node:path');
const root='/Users/andrey/Desktop/сайт нф';
const output=path.join(root,'output/pops-2026-11-05/revision-2/assets');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--allow-file-access-from-files']});
 const results=[];
 for(const viewport of [{width:1440,height:920},{width:390,height:844}]){
  const page=await browser.newPage({viewport,deviceScaleFactor:1});
  const pageErrors=[],failedRequests=[];
  page.on('pageerror',e=>pageErrors.push(e.message));
  page.on('requestfailed',r=>failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
  await page.goto('file://'+path.join(root,'output/concept/product-popsy.html'),{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  await page.locator('.detail-packshot').evaluate(im=>im.decode());
  const screenshot=path.join(output,viewport.width===1440?'pops-website-v2.png':'pops-website-v2-mobile.png');
  await page.screenshot({path:screenshot});
  const state=await page.evaluate(()=>{
   const img=document.querySelector('.detail-packshot');
   const r=img.getBoundingClientRect();
   return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelector('h1')?.textContent,currentSrc:img.currentSrc,packshotLoaded:img.complete&&img.naturalWidth>0,packshotBox:{x:r.x,y:r.y,width:r.width,height:r.height},brokenLoadedImages:[...document.images].filter(im=>im.complete&&im.naturalWidth===0&&!im.src.startsWith('data:')).map(im=>im.currentSrc)};
  });
  results.push({...state,screenshot,pageErrors,failedRequests});
  if(state.scrollWidth!==viewport.width||!state.packshotLoaded||!state.currentSrc.includes('popsy-pack-v2')||state.brokenLoadedImages.length||pageErrors.length||failedRequests.length)throw new Error('Pops v2 layout acceptance failed '+JSON.stringify(results));
  await page.close();
 }
 fs.writeFileSync(path.join(output,'pops-site-v2-checks.json'),JSON.stringify({result:'pass',method:'Playwright Chrome file URL with allow-file-access-from-files; desktop and mobile image/layout check',results},null,2));
 console.log(JSON.stringify(results,null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

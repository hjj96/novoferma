const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
const b=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const p=await b.newPage({viewport:{width:1440,height:950}});const dir='tmp/style-final';fs.mkdirSync(dir,{recursive:true});
for(const width of [320,375,700,1440]){
 await p.setViewportSize({width,height:950});
 await p.goto('http://127.0.0.1:8765/output/concept/index.html',{waitUntil:'networkidle'});
 await p.evaluate(async()=>{await document.fonts.ready;for(const i of document.images){i.loading='eager';await i.decode().catch(()=>{});}for(let y=0;y<document.body.scrollHeight;y+=700){window.scrollTo({top:y,behavior:'instant'});await new Promise(r=>setTimeout(r,60));}window.scrollTo({top:0,behavior:'instant'});});
 await p.waitForTimeout(750);
 await p.screenshot({path:`${dir}/home-${width}.png`,fullPage:true});
 if(width===1440){await p.screenshot({path:'output/novoferma-preview.png'});await p.locator('#protein').screenshot({path:'output/novoferma-protein-preview.png'});}
 console.log(width,await p.locator('.home-product').evaluateAll(es=>es.map(e=>({visible:getComputedStyle(e).display!=='none',text:e.querySelector('h3').textContent}))));
}
await b.close();})().catch(e=>{console.error(e);process.exit(1)});

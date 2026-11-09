const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('path');
const fs=require('fs');
(async()=>{
 const root=__dirname;
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({viewport:{width:1800,height:1450},deviceScaleFactor:1});
 await page.goto('file://'+path.join(root,'packaging/pops-packaging-review.html'));
 await page.evaluate(()=>document.fonts.ready);
 for(let i=0;i<2;i++)await page.locator('.sheet').nth(i).screenshot({path:path.join(root,'packaging',i===0?'pops-front.png':'pops-back.png')});
 fs.mkdirSync(path.join(root,'../pdf'),{recursive:true});
 await page.pdf({path:path.join(root,'../pdf/novoferma-popsy-packaging.pdf'),preferCSSPageSize:true,printBackground:true});
 fs.copyFileSync(path.join(root,'../pdf/novoferma-popsy-packaging.pdf'),path.join(root,'packaging/pops-packaging-review.pdf'));
 await browser.close();
 console.log('Packaging SVG, PNG and review PDF rendered.');
})().catch(e=>{console.error(e);process.exit(1)});

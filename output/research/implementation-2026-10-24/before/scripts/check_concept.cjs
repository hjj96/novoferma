const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage();let errors=[];page.on('pageerror',e=>errors.push(e.message));
 let results=[];fs.mkdirSync('tmp/qa',{recursive:true});
 for(const width of [320,375,768,1440]){
  await page.setViewportSize({width,height:900});await page.goto('http://127.0.0.1:8765/output/concept/',{waitUntil:'networkidle'});
  await page.screenshot({path:`tmp/qa/concept-${width}.png`,fullPage:true});
  const layout=await page.evaluate(()=>({viewport:innerWidth,doc:document.documentElement.scrollWidth,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)}));
  if(layout.doc>width)throw Error(`overflow ${width}: ${layout.doc}`);
  await page.getByRole('button',{name:'С индейкой',exact:true}).click();
  if(await page.locator('.product:visible').count()!==1)throw Error('Turkey filter failed');
  await page.getByRole('button',{name:'Все',exact:true}).click();
  if(await page.locator('.product:visible').count()!==4)throw Error('All filter failed');
  const trigger=page.getByRole('button',{name:'Подробнее: Фрикадельки Классические',exact:true});await trigger.click();
  if(!await page.locator('dialog').evaluate(e=>e.open))throw Error('Dialog did not open');
  await page.screenshot({path:`tmp/qa/dialog-${width}.png`});
  await page.keyboard.press('Escape');
  if(await page.locator('dialog').evaluate(e=>e.open))throw Error('Escape failed');
  if(!await trigger.evaluate(e=>e===document.activeElement))throw Error('Focus not returned');
  await trigger.click();await page.locator('#dialog-buy').click();await page.waitForTimeout(700);
  const where=await page.locator('#where').boundingBox();
  if(where.y< -2||where.y>200)throw Error(`where navigation failed ${width}: ${where.y}`);
  results.push({width,layout,filter:true,dialog:true,escape:true,focusReturned:true,whereTop:where.y});
 }
 await page.goto('file://'+process.cwd()+'/output/concept/index.html',{waitUntil:'load'});
 await page.getByRole('button',{name:'С индейкой',exact:true}).click();
 if(await page.locator('.product:visible').count()!==1)throw Error('file mode failed');
 await browser.close();
 fs.writeFileSync('tmp/qa/results.json',JSON.stringify({browser:'Google Chrome headless',results,fileMode:true,errors},null,2));
 console.log(JSON.stringify({results,fileMode:true,errors},null,2));
 if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

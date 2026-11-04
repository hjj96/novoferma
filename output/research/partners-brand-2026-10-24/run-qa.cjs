const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root='/Users/andrey/Desktop/сайт нф';
const out=path.join(root,'output/research/partners-brand-2026-10-24');
const url=pathToFileURL(path.join(root,'output/concept/partners.html')).href;
const widths=[1440,390,320,768,1024,1920];
const results=[];
const errors=[];
function requireCheck(ok,message){if(!ok)throw new Error(message);}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try{
  for(const width of widths){
   const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
   await context.addInitScript(()=>{
    window.__qaClipboard=[];
    Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async value=>{
     if(window.__qaFailClipboard)throw new Error('QA clipboard fallback');
     window.__qaClipboard.push(value);
    }}});
   });
   const page=await context.newPage();
   const pageErrors=[];
   page.on('pageerror',error=>pageErrors.push(error.message));
   await page.goto(url,{waitUntil:'load'});
   await page.evaluate(async()=>{
    await document.fonts.ready;
    await Promise.all([...document.images].map(img=>img.decode().catch(()=>{})));
    document.querySelectorAll('.reveal').forEach(el=>el.classList.add('is-visible'));
   });
   await page.screenshot({path:path.join(out,`partners-${width}.png`),fullPage:true});
   const metrics=await page.evaluate(()=>{
    const box=el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};};
    const visible=el=>{const s=getComputedStyle(el);return s.display!=='none'&&s.visibility!=='hidden'&&el.getClientRects().length>0;};
    const textOverflow=[];
    const walker=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);
    let node;
    while(node=walker.nextNode()){
     if(!node.textContent.trim()||!visible(node.parentElement))continue;
     const range=document.createRange();range.selectNodeContents(node);
     for(const r of range.getClientRects())if(r.width&&((r.left < -1)||(r.right > innerWidth+1))){
      textOverflow.push({text:node.textContent.trim().slice(0,100),left:r.left,right:r.right});break;
     }
    }
    const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);
    const dupIds=ids.filter((id,i)=>ids.indexOf(id)!==i);
    const host=document.querySelector('.partners-host');
    const hero=document.querySelector('.partners-business');
    const cta=document.querySelector('.partners-primary');
    const hostBox=box(host),ctaBox=box(cta);
    return {
     documentWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth,
     textOverflow,duplicateIds:dupIds,h1Count:document.querySelectorAll('h1').length,
     mainSections:[...document.querySelector('main').children].filter(el=>el.tagName==='SECTION').map(el=>el.className),
     offerCount:document.querySelectorAll('.partners-offers article').length,
     titleFont:getComputedStyle(document.querySelector('h1')).fontFamily,
     titleFontLoaded:document.fonts.check('850 40px "Novoferma Protein"'),
     fontFaces:[...document.fonts].filter(f=>f.family.includes('Novoferma Protein')).map(f=>({family:f.family,status:f.status,weight:f.weight})),
     palette:{hero:getComputedStyle(hero).backgroundColor,offers:getComputedStyle(document.querySelector('.partners-offers')).backgroundColor,contact:getComputedStyle(document.querySelector('#partner-contact')).backgroundColor},
     brokenImages:[...document.images].filter(img=>!img.complete||!img.naturalWidth).map(img=>img.getAttribute('src')),
     host:{src:host.getAttribute('src'),naturalWidth:host.naturalWidth,naturalHeight:host.naturalHeight,objectFit:getComputedStyle(host).objectFit,box:hostBox,scene:box(host.closest('figure')),hero:box(hero),boxRatioMatchesNatural:Math.abs(hostBox.w/hostBox.h-host.naturalWidth/host.naturalHeight)<.01,renderedAspectPreserved:getComputedStyle(host).objectFit==='contain'},
     heroCTA:ctaBox,
     hostBoxOverlapsCTA:hostBox.x<ctaBox.right&&hostBox.right>ctaBox.x&&hostBox.y<ctaBox.bottom&&hostBox.bottom>ctaBox.y,
     retailHref:document.querySelector('.partners-offer-retail a')?.getAttribute('href'),
     required:[...document.querySelectorAll('#partner-request-form [required]')].map(el=>el.name),
     headings:[...document.querySelectorAll('main h1,main h2')].map(el=>({text:el.innerText,font:getComputedStyle(el).fontFamily})),
    };
   });
   requireCheck(metrics.documentWidth===width,'Page horizontal overflow');
   requireCheck(!metrics.textOverflow.length,'Text outside viewport');
   requireCheck(!metrics.brokenImages.length,'Broken images');
   requireCheck(metrics.h1Count===1&&!metrics.duplicateIds.length,'Invalid heading or duplicate IDs');
   requireCheck(metrics.mainSections.length===3&&metrics.offerCount===2,'Expected three sections / two offers');
   requireCheck(metrics.titleFontLoaded&&metrics.fontFaces.some(f=>f.status==='loaded'),'Brand font not loaded');
   requireCheck(metrics.palette.hero==='rgb(250, 75, 6)'&&metrics.palette.offers==='rgb(255, 245, 227)'&&metrics.palette.contact==='rgb(64, 33, 17)','Brand section palette mismatch');
   requireCheck(metrics.host.objectFit==='contain'&&metrics.host.naturalWidth>0,'Host asset not contained');
   requireCheck(metrics.retailHref==='catalogue.html','Retail CTA destination');

   await page.locator('.partners-primary').click();
   const primaryCTA=await page.evaluate(()=>({hash:location.hash,selected:document.querySelector('[name="format"]:checked').value,contactTop:document.querySelector('#partner-contact').getBoundingClientRect().top}));
   requireCheck(primaryCTA.hash==='#partner-contact','Hero CTA anchor');
   await page.locator('.partners-specs summary').click();
   const specs=await page.locator('.partners-specs').evaluate(el=>({open:el.open,rows:el.querySelectorAll('tbody tr').length,tableWidth:el.querySelector('table').getBoundingClientRect().width,availableWidth:el.getBoundingClientRect().width,text:el.innerText}));
   requireCheck(specs.open&&specs.rows===5&&specs.tableWidth<=specs.availableWidth+1,'Specs disclosure or table overflow');
   if(width===390||width===1440)await page.locator('.partners-offer-retail').screenshot({path:path.join(out,`specs-open-${width}.png`)});
   await page.locator('.partners-specs summary').click();
   requireCheck(await page.locator('.partners-specs').evaluate(el=>!el.open),'Specs do not close');
   await page.locator('[data-partner-format="stm"]').click();
   const stmCTA=await page.evaluate(()=>({hash:location.hash,selected:document.querySelector('[name="format"]:checked').value,hint:document.querySelector('#partner-format-help').innerText}));
   requireCheck(stmCTA.hash==='#partner-contact'&&stmCTA.selected==='stm','STM CTA does not select form');
   const submit=page.locator('#partner-request-form button[type="submit"]');
   await submit.click();
   const emptyRequired=await page.locator('#partner-request-form').evaluate(form=>({valid:form.checkValidity(),invalid:[...form.querySelectorAll(':invalid')].map(el=>el.name),feedbackHidden:document.querySelector('#partner-request-feedback').hidden}));
   requireCheck(!emptyRequired.valid&&emptyRequired.invalid.includes('company')&&emptyRequired.invalid.includes('contact')&&emptyRequired.feedbackHidden,'Required empty validation');
   await page.locator('[name="company"]').fill('  ');
   await page.locator('[name="contact"]').fill('  ');
   await page.locator('#partner-copy-request').click();
   const whitespaceInvalid=await page.locator('#partner-request-form').evaluate(form=>!form.checkValidity());
   requireCheck(whitespaceInvalid,'Whitespace required fields accepted');
   await page.locator('[name="company"]').fill('Тестовая компания & Партнёр');
   await page.locator('[name="city"]').fill('Санкт-Петербург');
   await page.locator('[name="contact"]').fill('qa@example.test');
   await page.locator('[name="message"]').fill('Тест: продукты, фасовка и объём.');
   await page.locator('#partner-copy-request').click();
   const copied=await page.evaluate(()=>({texts:window.__qaClipboard,feedback:document.querySelector('#partner-request-feedback').innerText,draftHidden:document.querySelector('#partner-request-draft').hidden}));
   requireCheck(copied.texts.length===1&&copied.texts[0].includes('Производство под своей маркой (СТМ)')&&copied.texts[0].includes('Тестовая компания & Партнёр')&&copied.texts[0].includes('qa@example.test')&&copied.texts[0].includes('Тест: продукты, фасовка и объём.')&&copied.feedback.includes('Запрос скопирован.')&&copied.draftHidden,'Mock clipboard content or feedback');
   if(width===390||width===1440)await page.locator('#partner-contact').screenshot({path:path.join(out,`form-copied-${width}.png`)});
   await page.evaluate(()=>{window.__qaFailClipboard=true;});
   await page.locator('#partner-copy-request').click();
   const copyFallback=await page.evaluate(()=>({shown:!document.querySelector('#partner-request-draft').hidden,value:document.querySelector('#partner-request-draft').value,feedback:document.querySelector('#partner-request-feedback').innerText}));
   requireCheck(copyFallback.shown&&copyFallback.value===copied.texts[0],'Copy fallback');
   await page.locator('[name="company"]').fill('Изменённая компания');
   const resetAfterEdit=await page.evaluate(()=>document.querySelector('#partner-request-feedback').hidden&&document.querySelector('#partner-request-draft').hidden);
   requireCheck(resetAfterEdit,'Editing did not clear copy feedback');
   requireCheck(!pageErrors.length,'Browser JS errors');
   const result={width,...metrics,primaryCTA,specs,stmCTA,emptyRequired,whitespaceInvalid,copied,copyFallback,resetAfterEdit,pageErrors,mailSubmission:'Not invoked; no mail client opened',pass:true};
   results.push(result);
   fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({pass:true,url,results,errors},null,2));
   console.log(JSON.stringify({width,pass:true,hostBoxOverlapsCTA:metrics.hostBoxOverlapsCTA,images:!metrics.brokenImages.length,font:metrics.titleFontLoaded,clipboard:true}));
   await context.close();
  }
 }catch(error){errors.push(error.stack);fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({pass:false,url,results,errors},null,2));throw error;}
 finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

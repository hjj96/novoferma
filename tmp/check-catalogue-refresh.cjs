const { chromium } = require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const directory = 'output/research/catalogue-refresh';
  fs.mkdirSync(directory, {recursive:true});
  const results = [];
  for (const width of [1440, 768, 390, 320]) {
    await page.setViewportSize({width, height:950});
    await page.goto('http://127.0.0.1:8765/output/concept/catalogue.html', {waitUntil:'networkidle'});
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 650) {
        scrollTo({top:y, behavior:'instant'});
        await new Promise(resolve => setTimeout(resolve, 90));
      }
      scrollTo({top:0, behavior:'instant'});
    });
    await page.waitForTimeout(800);
    const result = await page.evaluate(() => ({
      width: innerWidth, documentWidth:document.documentElement.scrollWidth,
      columns:getComputedStyle(document.querySelector('.catalogue-grid')).gridTemplateColumns.split(' ').length,
      products:document.querySelectorAll('.catalogue-grid .product-card').length,
      hiddenProducts:document.querySelectorAll('.catalogue-grid .product-card[hidden]').length,
      noveltyCards:document.querySelectorAll('.newcomer-card').length,
      filters:document.querySelectorAll('[data-category-filter], [data-meat-filter], #product-search, #product-count, .empty-state').length,
      visibleHeadingCount:[...document.querySelectorAll('.catalogue-page h2')].filter(element=>element.getBoundingClientRect().height>1).length,
      rectangularBackgrounds:[...document.querySelectorAll('.catalogue-grid .product-image')].filter(element=>getComputedStyle(element).backgroundImage!=='none'||getComputedStyle(element).backgroundColor!=='rgba(0, 0, 0, 0)').length,
      stackedArrows:[...document.querySelectorAll('.catalogue-grid .product-title')].filter(element=>getComputedStyle(element).flexDirection!=='row').length,
      brokenImages:[...document.images].filter(image=>!image.complete||!image.naturalWidth).map(image=>image.src),
      metaBorders:[...document.querySelectorAll('.catalogue-page .product-meta')].map(element=>getComputedStyle(element).borderTopWidth),
      novelBorder:getComputedStyle(document.querySelector('.catalogue-novelties')).borderTopWidth,
      height:document.documentElement.scrollHeight
    }));
    if(result.documentWidth>width || result.products!==14 || result.hiddenProducts || result.noveltyCards!==2 || result.filters || result.brokenImages.length || result.metaBorders.some(border=>border!=='0px') || result.novelBorder!=='0px' || result.visibleHeadingCount!==1 || result.rectangularBackgrounds || result.stackedArrows) throw Error(JSON.stringify(result));
    await page.screenshot({path:`${directory}/catalogue-${width}.png`,fullPage:true});
    if(width===1440) await page.screenshot({path:`${directory}/catalogue-desktop-top.png`});
    if(width===390) {
      await page.locator('.menu-toggle').click();
      if(!await page.locator('#site-menu').evaluate(element=>element.open)) throw Error('Mobile menu failed');
      await page.locator('.menu-close').click();
    }
    results.push(result);
  }
  const firstLink=await page.locator('.catalogue-grid .product-image').first().getAttribute('href');
  await page.locator('.catalogue-grid .product-image').first().click();
  await page.waitForURL(`**/${firstLink}`);
  if(!await page.locator('.detail-copy h1').textContent()) throw Error('Product link failed');
  await page.goto('http://127.0.0.1:8765/output/concept/catalogue.html#novelties');
  await page.locator('.newcomer-card .text-link').first().click();
  await page.waitForURL('**/where-to-buy.html?product=fibriki');
  if(await page.locator('#wanted-product').inputValue()!=='fibriki') throw Error('Novelty link failed');
  if(errors.length) throw Error(JSON.stringify(errors));
  fs.writeFileSync(`${directory}/checks.json`,JSON.stringify({results,productLink:true,noveltySelection:true,mobileMenu:true,errors},null,2));
  console.log(JSON.stringify({viewports:results.map(({width,columns,height})=>({width,columns,height})),productLink:true,noveltySelection:true,mobileMenu:true,errors}));
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});

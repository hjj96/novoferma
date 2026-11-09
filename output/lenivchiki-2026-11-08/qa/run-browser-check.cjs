const {chromium} = require('/Users/andrey/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const out = __dirname;
const base = 'http://127.0.0.1:8767';
const result = {base, checkedAt: new Date().toISOString(), widths: [], consoleErrors: [], pageErrors: [], failedRequests: [], httpErrors: []};

async function settle(page) {
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 650) {
      window.scrollTo({top: y, behavior: 'instant'});
      await new Promise(resolve => setTimeout(resolve, 45));
    }
    window.scrollTo({top: 0, behavior: 'instant'});
    await Promise.all([...document.images].map(img => img.complete ? Promise.resolve() : new Promise(resolve => { img.onload = resolve; img.onerror = resolve; })));
  });
  await page.waitForTimeout(300);
}

async function metrics(page) {
  return page.evaluate(() => {
    const rect = node => {
      if (!node) return null;
      const r = node.getBoundingClientRect();
      const s = getComputedStyle(node);
      return {x: r.x, y: r.y + scrollY, width: r.width, height: r.height, fontSize: s.fontSize, lineHeight: s.lineHeight, objectFit: s.objectFit, overflow: s.overflow};
    };
    const textOverflow = [...document.querySelectorAll('main h1,main h2,main h3,main p,main summary,main label')].filter(node => {
      if (node.closest('.sr-only,[hidden]')) return false;
      const r = node.getBoundingClientRect();
      const s = getComputedStyle(node);
      return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && (r.left < -1 || r.right > innerWidth + 1 || node.scrollWidth > node.clientWidth + 2);
    }).map(node => ({tag: node.tagName, class: node.className, text: node.innerText.slice(0, 100), box: rect(node), scrollWidth: node.scrollWidth, clientWidth: node.clientWidth}));
    return {
      url: location.href, title: document.title, viewportWidth: innerWidth, documentWidth: document.documentElement.scrollWidth,
      h1: document.querySelector('h1')?.innerText, textOverflow,
      packshot: rect(document.querySelector('.detail-packshot')),
      heading: rect(document.querySelector('.detail-heading')),
      detailCopy: rect(document.querySelector('.detail-copy')),
      storyCopy: rect(document.querySelector('.lenivchiki-story-copy')),
      storyVisual: rect(document.querySelector('.lenivchiki-story-visual')),
      productCopy: [...document.querySelectorAll('.product-detail,.lenivchiki-story')].map(node => node.innerText).join('\n'),
      brokenImages: [...document.images].filter(img => !img.complete || img.naturalWidth === 0).map(img => img.currentSrc || img.src),
      productImages: [...document.querySelectorAll('.detail-packshot,.lenivchiki-scene')].map(img => ({src: img.currentSrc, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight, box: rect(img)})),
      wantedProduct: document.querySelector('#wanted-product')?.value,
      wantedLabel: document.querySelector('#wanted-product')?.selectedOptions[0]?.label,
      mailLinks: [...document.querySelectorAll('a[href^="mailto:"]')].map(a => ({text: a.innerText, href: a.getAttribute('href')}))
    };
  });
}

(async () => {
  const browser = await chromium.launch({headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  for (const width of [1440, 390, 320]) {
    const page = await browser.newPage({viewport: {width, height: width > 1000 ? 1000 : 844}, deviceScaleFactor: 1, reducedMotion: 'reduce'});
    page.on('console', msg => { if (msg.type() === 'error') result.consoleErrors.push({width, page: page.url(), message: msg.text()}); });
    page.on('pageerror', error => result.pageErrors.push({width, page: page.url(), message: error.message}));
    page.on('requestfailed', req => result.failedRequests.push({width, url: req.url(), error: req.failure()?.errorText}));
    page.on('response', response => { if (response.status() >= 400) result.httpErrors.push({width, url: response.url(), status: response.status()}); });
    const run = {width};
    await page.goto(base + '/catalogue.html', {waitUntil: 'networkidle'});
    await settle(page);
    const card = page.locator('.product-card[data-product-id="lenivchiki"]');
    await card.waitFor({state: 'visible'});
    await card.scrollIntoViewIfNeeded();
    await page.waitForTimeout(250);
    await page.screenshot({path: path.join(out, `01-catalogue-context-${width}.png`)});
    await card.screenshot({path: path.join(out, `01-catalogue-card-${width}.png`)});
    run.catalogue = await metrics(page);
    run.catalogue.cardText = await card.innerText();
    run.catalogue.cardHref = await card.locator('a').getAttribute('href');
    await card.locator('a').click();
    await page.waitForURL('**/product-lenivchiki.html');
    await settle(page);
    await page.screenshot({path: path.join(out, `02-product-full-${width}.png`), fullPage: true});
    await page.locator('.product-detail').screenshot({path: path.join(out, `02-product-hero-${width}.png`)});
    await page.locator('.lenivchiki-story').screenshot({path: path.join(out, `03-product-story-${width}.png`)});
    run.product = await metrics(page);
    await page.locator('.detail-actions a[href="where-to-buy.html?product=lenivchiki"]').click();
    await page.waitForURL('**/where-to-buy.html?product=lenivchiki');
    await settle(page);
    await page.screenshot({path: path.join(out, `04-where-to-buy-full-${width}.png`), fullPage: true});
    await page.locator('#wanted-product').scrollIntoViewIfNeeded();
    await page.screenshot({path: path.join(out, `04-where-to-buy-choice-${width}.png`)});
    run.whereToBuy = await metrics(page);
    run.flowPassed = run.catalogue.cardHref === 'product-lenivchiki.html' && run.product.h1.toLowerCase() === 'ленивчики' && run.whereToBuy.wantedProduct === 'lenivchiki' && run.whereToBuy.wantedLabel === 'Ленивчики';
    result.widths.push(run);
    await page.close();
  }
  await browser.close();
  result.passed = result.widths.every(run => run.flowPassed && [run.catalogue, run.product, run.whereToBuy].every(p => p.documentWidth === p.viewportWidth && p.textOverflow.length === 0 && p.brokenImages.length === 0)) && result.consoleErrors.length === 0 && result.pageErrors.length === 0 && result.httpErrors.length === 0;
  fs.writeFileSync(path.join(out, 'browser-checks.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({passed: result.passed, flow: result.widths.map(r => ({width: r.width, passed: r.flowPassed, documentWidths: [r.catalogue.documentWidth, r.product.documentWidth, r.whereToBuy.documentWidth], textOverflow: [r.catalogue.textOverflow, r.product.textOverflow, r.whereToBuy.textOverflow], brokenImages: [r.catalogue.brokenImages, r.product.brokenImages, r.whereToBuy.brokenImages]})), consoleErrors: result.consoleErrors, pageErrors: result.pageErrors, httpErrors: result.httpErrors, failedRequests: result.failedRequests}, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });

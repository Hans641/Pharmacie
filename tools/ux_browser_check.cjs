/* Recette navigateur en lecture seule, facultative ; aucun build de l'application.
   Préparer une base fictive et lancer Django, puis :
   PHARMAGEST_USERNAME=... PHARMAGEST_PASSWORD=... node tools/ux_browser_check.cjs
   Dépendance de test : Playwright (PLAYWRIGHT_MODULE_PATH peut désigner son package).
   PHARMAGEST_SALE_ID : vente à examiner ; aucune vente n'est validée par ce script. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const base = process.env.PHARMAGEST_URL || 'http://127.0.0.1:8000';
const origin = new URL(base).origin;
const output = path.resolve(process.env.UX_OUTPUT_DIR || '/tmp/pharmagest-ux');
const routes = (process.env.UX_ROUTES || '/,/catalogue/medicaments/,/stocks/,/achats/,/ventes/,/rapports/').split(',');
if (process.env.PHARMAGEST_SALE_ID) routes.push(`/ventes/${process.env.PHARMAGEST_SALE_ID}/`);

(async () => {
  assert(process.env.PHARMAGEST_USERNAME && process.env.PHARMAGEST_PASSWORD, 'Définir PHARMAGEST_USERNAME et PHARMAGEST_PASSWORD (compte fictif).');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
  const report = [];
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    const runtimeErrors = [];
    const external = [];
    page.on('pageerror', error => runtimeErrors.push(error.message));
    page.on('request', request => { if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== origin) external.push(request.url()); });
    await page.goto(`${base}/comptes/login/`);
    await page.locator('[name="username"]').fill(process.env.PHARMAGEST_USERNAME);
    await page.locator('[name="password"]').fill(process.env.PHARMAGEST_PASSWORD);
    await Promise.all([page.waitForURL(url => !url.pathname.includes('/login/')), page.getByRole('button', { name: 'Se connecter', exact: true }).click()]);
    for (const width of [360, 768, 1280, 1920]) {
      await page.setViewportSize({ width, height: 1000 });
      for (const route of routes) {
        const response = await page.goto(base + route);
        assert.equal(response.status(), 200, `${route} : adapter UX_ROUTES aux droits du rôle testé`);
        assert.equal(await page.locator('h1').count(), 1, `${route} : titre principal unique`);
        const layout = await page.evaluate(() => {
          const width = document.documentElement.clientWidth;
          const tooSmall = [...document.querySelectorAll('a,button,summary,input:not([type="hidden"]),select,textarea')].filter(el => {
            let rect = el.getBoundingClientRect();
            if (!el.getClientRects().length || !rect.width || !rect.height || rect.bottom < 0 || el.closest('.visually-hidden')) return false;
            if (el.matches('input[type="radio"],input[type="checkbox"]') && el.labels?.length) rect = el.labels[0].getBoundingClientRect();
            return rect.height < 43.5 || rect.width < 43.5;
          }).map(el => el.getAttribute('aria-label') || el.textContent.trim().slice(0, 70) || el.name);
          return { overflow: document.documentElement.scrollWidth > width + 1, tooSmall };
        });
        assert(!layout.overflow, `${width}px ${route} : débordement horizontal de page`);
        assert.deepEqual(layout.tooSmall, [], `${width}px ${route} : cibles sous 44 px`);
        if (width <= 768) {
          await page.getByRole('button', { name: 'Menu', exact: true }).click();
          assert.equal(await page.locator('#workspace').evaluate(el => el.inert), true);
          await page.keyboard.press('Escape');
          assert.equal(await page.locator('#workspace').evaluate(el => el.inert), false);
          assert.equal(await page.evaluate(() => document.activeElement.hasAttribute('data-nav-open')), true);
        }
        if (await page.locator('#cash-search').count()) {
          await page.keyboard.press('F2');
          assert.equal(await page.evaluate(() => document.activeElement.id), 'cash-search');
          await page.keyboard.press('F4');
          const cash = page.locator('[data-cash-tools]');
          if (await cash.count()) {
            const total = await page.locator('[data-checkout]').getAttribute('data-total');
            await page.locator('#cash-received').fill((Number(total) + 500).toFixed(2).replace('.', ','));
            assert.equal((await page.locator('#cash-change').textContent()).replace(/\s/g, ''), '500,00Ar');
          }
        }
        await page.screenshot({ path: path.join(output, `${width}-${route.replace(/[^a-z0-9]/gi, '_') || 'accueil'}.png`), fullPage: true });
        report.push({ width, route, status: 'ok' });
      }
    }
    // Repli sans JS, après connexion : navigation et formulaires restent disponibles.
    const nativeContext = await browser.newContext({ javaScriptEnabled: false, storageState: await context.storageState(), viewport: { width: 360, height: 1000 } });
    const nativePage = await nativeContext.newPage();
    for (const route of routes) {
      assert.equal((await nativePage.goto(base + route)).status(), 200);
      assert(await nativePage.locator('#navigation-panel').isVisible());
    }
    await nativeContext.close();
    assert.deepEqual(runtimeErrors, [], 'Erreurs JavaScript');
    assert.deepEqual(external, [], 'Ressources distantes détectées');
    fs.writeFileSync(path.join(output, 'resultats.json'), JSON.stringify(report, null, 2));
    console.log(`${report.length} contrôles de page réussis + repli sans JS. Captures : ${output}`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });

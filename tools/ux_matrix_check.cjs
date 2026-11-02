/* Lot 2 : assertions communes par page ; aucun POST métier et aucun défaut ignoré. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const base = process.env.PHARMAGEST_URL;
const output = process.env.UX_OUTPUT_DIR;
const routes = process.env.UX_ROUTES.split(',');
if (process.env.UX_WIZARD === '1') routes.push('/catalogue/medicaments/ajouter/');
if (process.env.PHARMAGEST_SALE_ID) routes.push(`/ventes/${process.env.PHARMAGEST_SALE_ID}/`);
const rows = [];
const role = process.env.UX_ROLE;
const deferred = ['Filtre de période validé séparément : 20/20 après correction ; non réexercé dans cette matrice',
  'Examen visuel des captures et texte tronqué', 'Ordre complet de tabulation et lecteur d’écran',
  'Erreurs après saisie et soumission : parcours métier séparés', 'Zoom et impression : lots suivants'];
const save = () => fs.writeFileSync(path.join(output, 'matrix.json'), JSON.stringify({ scope: 'assertions communes de présentation', deferred, rows }, null, 2));

async function geometry(page) {
  return page.evaluate(() => {
    const hidden = el => {
      for (let ancestor = el; ancestor; ancestor = ancestor.parentElement) {
        if (ancestor.hidden || getComputedStyle(ancestor).display === 'none') return true;
        if (ancestor.matches('details:not([open])') && !ancestor.querySelector(':scope > summary')?.contains(el)) return true;
      }
      return ['hidden', 'collapse'].includes(getComputedStyle(el).visibility);
    };
    const small = [];
    for (const el of document.querySelectorAll('a,button,summary,input:not([type="hidden"]),select,textarea')) {
      if (hidden(el) || el.closest('.visually-hidden')) continue;
      let rect = el.getBoundingClientRect();
      if (!rect.width || !rect.height || rect.bottom < 0) continue;
      if (el.matches('input[type="radio"],input[type="checkbox"]') && el.labels?.length) rect = el.labels[0].getBoundingClientRect();
      if (rect.width < 43.5 || rect.height < 43.5) small.push({ label: el.getAttribute('aria-label') || el.textContent.trim().slice(0, 90) || el.name, width: rect.width, height: rect.height });
    }
    const clipping = [...document.querySelectorAll('h1,h2,h3,p,legend,.badge')].filter(el => !hidden(el) && el.clientWidth && el.scrollWidth > el.clientWidth + 1).map(el => el.textContent.trim().slice(0, 100));
    return { overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1, small, clipping };
  });
}

(async () => {
  fs.mkdirSync(output, { recursive: true });
  for (const theme of ['light', 'dark']) for (const javascript of [true, false]) for (const width of [360, 768, 1280, 1920]) for (const page of routes) {
    rows.push({ page, role, width, javascript, theme, result: 'non exécuté', capture: null, reason: 'Exécution non commencée ou interrompue' });
  }
  save();
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
  try {
    const authContext = await browser.newContext({ locale: 'fr-FR', timezoneId: 'Indian/Antananarivo' });
    const auth = await authContext.newPage();
    await auth.goto(base + '/comptes/login/');
    await auth.locator('[name="username"]').fill(process.env.PHARMAGEST_USERNAME);
    await auth.locator('[name="password"]').fill(process.env.PHARMAGEST_PASSWORD);
    await Promise.all([auth.waitForURL(url => !url.pathname.includes('/login/')), auth.getByRole('button', { name: 'Se connecter', exact: true }).click()]);
    const storageState = await authContext.storageState(); // Pas de fichier de session.
    await authContext.close();
    for (const theme of ['light', 'dark']) {
      for (const js of [true, false]) {
        for (const width of [360, 768, 1280, 1920]) {
          const context = await browser.newContext({ storageState, colorScheme: theme, javaScriptEnabled: js, viewport: { width, height: 1000 }, locale: 'fr-FR', timezoneId: 'Indian/Antananarivo' });
          const page = await context.newPage();
          page.setDefaultTimeout(8000);
          let errors = [], external = [];
          page.on('pageerror', error => errors.push(error.message));
          page.on('request', request => { if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== new URL(base).origin) external.push(request.url()); });
          for (const route of routes) {
            errors = []; external = [];
            const row = { page: route, role, width, javascript: js, theme, result: 'running', issues: [], checked: [], deferred };
            const check = async (name, fn) => {
              try { await fn(); row.checked.push(name); }
              catch (error) { row.issues.push({ check: name, message: String(error.message) }); }
            };
            try {
              const response = await page.goto(base + route);
              assert.equal(response.status(), 200, 'Réponse HTTP');
              await check('langue et titre', async () => {
                assert.equal(await page.locator('html').getAttribute('lang'), 'fr');
                assert.equal(await page.locator('h1').count(), 1);
                assert((await page.title()).includes('PharmaGest'));
              });
              await check('thème système rendu', async () => {
                assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).colorScheme), theme);
                if (!js) assert(!(await page.locator('[data-theme-control]').isVisible()));
              });
              const layout = await geometry(page);
              row.geometry = layout;
              await check('débordement de page', async () => assert(!layout.overflow));
              await check('cibles tactiles visibles', async () => assert.deepEqual(layout.small, []));
              await check('navigation active', async () => assert.equal(await page.locator('#navigation-panel nav [aria-current="page"]').count(), 1));
              await check('lien d’évitement et focus', async () => {
                await page.keyboard.press('Tab');
                await page.locator('.skip-link').focus();
                const focus = await page.locator('.skip-link').evaluate(el => ({ width: getComputedStyle(el).outlineWidth, style: getComputedStyle(el).outlineStyle }));
                assert(parseFloat(focus.width) >= 2 && focus.style !== 'none');
                await page.keyboard.press('Enter');
                assert.equal(await page.evaluate(() => document.activeElement.id), 'main-content');
              });
              if (js && width <= 768) await check('tiroir clavier', async () => {
                const open = page.getByRole('button', { name: 'Menu', exact: true });
                await open.focus(); await open.press('Enter');
                assert(await page.locator('#workspace').evaluate(el => el.inert));
                const controls = page.locator('#navigation-panel a:visible, #navigation-panel button:visible');
                await controls.first().focus(); await page.keyboard.press('Shift+Tab');
                assert(await controls.last().evaluate(el => document.activeElement === el));
                await page.keyboard.press('Tab');
                assert(await controls.first().evaluate(el => document.activeElement === el));
                await page.keyboard.press('Escape');
                assert(!(await page.locator('#workspace').evaluate(el => el.inert)));
                assert(await open.evaluate(el => document.activeElement === el));
              });
              if (!js) await check('navigation sans JS', async () => assert(await page.locator('#navigation-panel').isVisible()));
              row.tabSequence = [];
              for (let index = 0; index < 6; index++) {
                await page.keyboard.press('Tab');
                row.tabSequence.push(await page.evaluate(() => ({ tag: document.activeElement.tagName, id: document.activeElement.id, name: document.activeElement.getAttribute('aria-label') })));
              }
              await check('erreurs JavaScript et ressources locales', async () => { assert.deepEqual(errors, []); assert.deepEqual(external, []); });
            } catch (error) { row.issues.push({ check: 'chargement', message: String(error.message) }); }
            row.result = row.issues.length ? 'KO' : 'OK';
            row.capture = `${theme}-${js ? 'js' : 'sans-js'}-${width}-${route.replace(/[^a-z0-9]/gi, '_')}.png`;
            try { await page.screenshot({ path: path.join(output, row.capture), fullPage: true }); }
            catch (error) { row.issues.push({ check: 'capture', message: error.message }); row.result = 'KO'; row.capture = null; }
            const index = rows.findIndex(item => item.page === route && item.theme === theme && item.width === width && item.javascript === js);
            rows[index] = row; save();
            console.log(`${row.result} ${role} ${width}px ${theme} ${js ? 'avec JS' : 'sans JS'} ${route}`);
            if (row.issues.length) console.log(JSON.stringify(row.issues));
          }
          await context.close();
        }
      }
    }
  } finally { await browser.close(); }
  const failed = rows.filter(row => row.result === 'KO').length;
  const pending = rows.filter(row => row.result === 'non exécuté').length;
  console.log(`Matrice : ${rows.length} pages, ${failed} KO ; contrôles différés consignés dans matrix.json.`);
  process.exitCode = failed || pending ? 1 : 0;
})().catch(error => { console.error(String(error.message).split(process.env.PHARMAGEST_PASSWORD || '\0').join('[masqué]')); process.exitCode = 1; });

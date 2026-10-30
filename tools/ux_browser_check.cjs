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
if (process.env.UX_WIZARD === '1') routes.push('/catalogue/medicaments/ajouter/');
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
        if (await page.locator('.dashboard').count()) {
          // Entrée active les liens natifs ; la cible doit recevoir le focus.
          for (const link of await page.locator('.dashboard-sections a').all()) {
            const target = (await link.getAttribute('href')).slice(1);
            await link.focus();
            await page.keyboard.press('Enter');
            assert.equal(await page.evaluate(() => document.activeElement.id), target);
          }
          if (await page.locator('#dashboard-start').count()) {
            await page.locator('#dashboard-start').fill('2000-01-01');
            await page.locator('#dashboard-end').fill('2000-01-31');
            await Promise.all([page.waitForURL(url => url.searchParams.get('start') === '2000-01-01'), page.getByRole('button', { name: 'Appliquer la période', exact: true }).click()]);
            assert((await page.locator('#dashboard-period-help').textContent()).includes('01/01/2000 au 31/01/2000'));
            await Promise.all([page.waitForURL(url => !url.search), page.getByRole('link', { name: 'Mois en cours', exact: true }).click()]);
            assert.equal(await page.locator('#dashboard-start').inputValue(), (await page.locator('#dashboard-end').inputValue()).slice(0, 8) + '01');
          }
          assert(!(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)));
        }
        if (await page.locator('#cash-search').count()) {
          await page.keyboard.press('F2');
          assert.equal(await page.evaluate(() => document.activeElement.id), 'cash-search');
          const options = await page.locator('#id_medicine option').evaluateAll(nodes => nodes.filter(node => node.value).map(node => ({ id: node.value, minor: node.dataset.priceMinor })));
          const lots = await page.locator('#lot-data').evaluate(template => [...template.content.querySelectorAll('span')].map(node => ({ ...node.dataset })));
          const rows = await page.locator('[data-cart-lot]').evaluateAll(nodes => nodes.map(node => ({ id: node.dataset.cartLot, quantity: node.dataset.cartQuantity })));
          const reserved = new Map();
          rows.forEach(row => reserved.set(row.id, (reserved.get(row.id) || 0n) + BigInt(row.quantity)));
          const option = options.find(item => lots.some(lot => lot.medicine === item.id && BigInt(lot.quantity) > (reserved.get(lot.id) || 0n)));
          assert(option, 'Préparer au moins un médicament délivrable avec du stock hors panier.');
          await page.locator('#id_medicine').selectOption(option.id);
          assert.equal(await page.evaluate(() => document.activeElement.id), 'id_quantity');
          await page.locator('#id_quantity').fill('1');
          const expected = `${BigInt(option.minor) / 100n},${(BigInt(option.minor) % 100n).toString().padStart(2, '0')}Ar`;
          assert.equal((await page.locator('[data-item-price]').textContent()).replace(/\s/g, ''), expected);
          assert.equal((await page.locator('[data-item-subtotal]').textContent()).replace(/\s/g, ''), expected);
          const available = BigInt(await page.locator('#id_quantity').getAttribute('max'));
          await page.locator('#id_quantity').fill((available + 1n).toString());
          await page.locator('#id_quantity').blur();
          assert(await page.locator('#id_quantity_feedback').textContent());
          await page.locator('#id_quantity').fill('1');
          // Aucun ajout au panier : seul le récapitulatif local est exercé.
        }
        if (await page.locator('[data-checkout]').count()) {
          await page.keyboard.press('F4');
          assert.equal(await page.evaluate(() => document.activeElement.name), 'method');
          const total = BigInt(await page.locator('[data-checkout]').getAttribute('data-total-minor'));
          const received = total + 50000n;
          await page.locator('#cash-received').fill(`${received / 100n},${(received % 100n).toString().padStart(2, '0')}`);
          assert.equal((await page.locator('#cash-change').textContent()).replace(/\s/g, ''), '500,00Ar');
          await page.locator('[data-cash-exact]').click();
          assert.equal((await page.locator('#cash-change').textContent()).replace(/\s/g, ''), '0,00Ar');
          assert.equal(await page.locator('[name="confirm"]').isChecked(), false);
          if (await page.locator('[name="method"][value="mobile"]').count()) {
            await page.locator('[name="method"][value="mobile"]').check();
            assert.equal(await page.locator('[name="reference"]').evaluate(input => input.required && !input.disabled), true);
            assert.equal(await page.locator('[name="verified"]').evaluate(input => input.required && !input.checked), true);
            await page.locator('[name="method"][value="cash"]').check();
            assert.equal(await page.locator('[name="reference"]').evaluate(input => input.disabled && !input.required), true);
          }
          const prescription = await page.locator('[data-prescription="1"]').count() > 0;
          assert.equal(await page.locator('[name="prescription_checked"]').evaluate(input => input.required), prescription);
          // Aucun encaissement et aucune confirmation de paiement ne sont soumis.
        }
        if (await page.locator('form[data-wizard]').count()) {
          const wizard = page.locator('form[data-wizard]');
          await page.getByRole('button', { name: 'Continuer', exact: true }).click();
          assert.equal(await page.evaluate(() => document.activeElement.id), 'id_name');
          assert(await page.locator('#id_name_feedback').textContent());
          await page.locator('#id_name').fill('Médicament de recette UX');
          await page.locator('#id_form').fill('Comprimé');
          const firstCategory = await page.locator('#id_category option').evaluateAll(options => options.find(option => option.value)?.value);
          assert(firstCategory, 'Créer une catégorie fictive avant la recette du formulaire.');
          await page.locator('#id_category').selectOption(firstCategory);
          await page.locator('#id_photo').setInputFiles({
            name: 'recette.png', mimeType: 'image/png',
            buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII=', 'base64'),
          });
          await page.getByRole('button', { name: 'Continuer', exact: true }).click();
          await page.locator('#id_purchase_price').fill('-1');
          await page.locator('#id_sale_price').fill('15000');
          await page.getByRole('button', { name: 'Continuer', exact: true }).click();
          assert.equal(await page.evaluate(() => document.activeElement.id), 'id_purchase_price');
          assert((await page.locator('#id_purchase_price_feedback').textContent()).includes('0,01'));
          await page.locator('#id_purchase_price').fill('10000');
          await page.getByRole('button', { name: 'Continuer', exact: true }).click();
          assert.equal((await page.locator('[data-wizard-summary]').textContent()).replace(/\s/g, '').includes('15000,00Ar'), true);
          assert(await page.locator('[data-wizard-submit]').isVisible());
          await page.getByRole('button', { name: 'Précédent', exact: true }).click();
          await page.getByRole('button', { name: 'Précédent', exact: true }).click();
          assert.equal(await page.locator('#id_name').inputValue(), 'Médicament de recette UX');
          assert.equal(await page.locator('#id_photo').evaluate(input => input.files[0]?.name), 'recette.png');
          await page.locator('[data-wizard-go="2"]').click();
          assert.equal(await wizard.locator('[data-wizard-step]:visible').count(), 1);
          // Aucune soumission finale : les données de recette ne sont pas enregistrées.
        }
        const operationForm = page.locator('form[data-operation]');
        if (await operationForm.count()) {
          const kind = await operationForm.getAttribute('data-operation');
          await page.locator('[data-operation-preview]').waitFor({ state: 'visible' });
          if (kind === 'inventory') {
            const before = BigInt(await operationForm.getAttribute('data-stock-before'));
            const counted = before >= 2n ? before - 2n : before + 1n;
            await page.locator('#id_counted').fill(counted.toString());
            assert((await page.locator('[data-preview-delta]').textContent()).includes(before >= 2n ? '-2' : '+1'));
            await page.locator('#id_blocked').check();
            assert.equal(await page.locator('[data-preview-blocked]').textContent(), 'Bloqué à la vente');
          } else {
            const record = await page.locator('[data-operation-line]').evaluateAll(nodes => nodes.map(node => ({ ...node.dataset })).find(item => BigInt(item.remaining) > 0n));
            assert(record, 'Préparer une ligne avec un reliquat positif pour la recette.');
            await page.locator('#id_line').selectOption(record.lineId);
            const quantity = BigInt(record.remaining) >= 2n ? 2n : 1n;
            await page.locator('#id_quantity').fill(quantity.toString());
            assert.equal(await page.locator('#id_quantity').getAttribute('max'), record.remaining);
            assert((await page.locator('[data-preview-remaining]').textContent()).includes((BigInt(record.remaining) - quantity).toString()));
            assert.notEqual(await page.locator('[data-preview-amount]').textContent(), '—');
            if (kind === 'return') {
              await page.locator('#id_restock').uncheck();
              assert.equal(await page.locator('[data-preview-stock]').textContent(), 'Aucune réintégration');
              const today = await operationForm.getAttribute('data-today');
              if (record.blocked === '1' || record.expires < today) {
                await page.locator('#id_restock').check();
                assert.equal(await page.locator('#id_restock').evaluate(input => input.validity.customError), true);
                assert((await page.locator('#id_restock_feedback').textContent()).includes('Décochez'));
                await page.locator('#id_restock').uncheck();
              }
            }
            await page.locator('#id_quantity').fill((BigInt(record.remaining) + 1n).toString());
            await page.locator('#id_quantity').blur();
            assert(await page.locator('#id_quantity_feedback').textContent());
            await page.locator('#id_quantity').fill(quantity.toString());
          }
          assert(!(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)));
          // Aucun clic sur le bouton final : ni stock, ni retour, ni réception modifiés.
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
      if (await nativePage.locator('#dashboard-start').count()) {
        await nativePage.locator('#dashboard-start').fill('2000-01-01');
        await nativePage.locator('#dashboard-end').fill('2000-01-31');
        await Promise.all([nativePage.waitForURL(url => url.searchParams.get('start') === '2000-01-01'), nativePage.getByRole('button', { name: 'Appliquer la période', exact: true }).click()]);
        assert((await nativePage.locator('#dashboard-period-help').textContent()).includes('01/01/2000 au 31/01/2000'));
        await Promise.all([nativePage.waitForURL(url => !url.search), nativePage.getByRole('link', { name: 'Mois en cours', exact: true }).click()]);
      }
      if (await nativePage.locator('form[data-operation]').count()) {
        assert.equal(await nativePage.locator('form[data-operation]').evaluate(form => form.noValidate), false);
        assert(!(await nativePage.locator('[data-operation-preview]').isVisible()));
      }
      if (await nativePage.locator('form[data-wizard]').count()) {
        assert.equal(await nativePage.locator('[data-wizard-step]:visible').count(), 3);
        assert(await nativePage.locator('[data-wizard-submit]').isVisible());
        assert.equal(await nativePage.locator('form[data-wizard]').evaluate(form => form.noValidate), false);
      }
    }
    await nativeContext.close();
    assert.deepEqual(runtimeErrors, [], 'Erreurs JavaScript');
    assert.deepEqual(external, [], 'Ressources distantes détectées');
    fs.writeFileSync(path.join(output, 'resultats.json'), JSON.stringify(report, null, 2));
    console.log(`${report.length} contrôles de page réussis + repli sans JS. Captures : ${output}`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });

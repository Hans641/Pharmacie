/* Lot 1 : reproductions et preuves, sans modification des composants. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const base = process.env.PHARMAGEST_URL;
const output = process.env.UX_OUTPUT_DIR;
const results = [];

async function instrument(page) {
  await page.evaluate(() => {
    window.uxDiagnostic = { events: [], frames: [] };
    const targetName = el => el?.id || el?.getAttribute?.('data-wizard-next') || el?.tagName;
    for (const type of ['pointerdown', 'pointerup', 'click', 'focusin', 'focusout', 'keydown', 'invalid', 'submit']) {
      document.addEventListener(type, event => {
        const item = { type, at: performance.now(), target: targetName(event.target), focus: targetName(document.activeElement) };
        window.uxDiagnostic.events.push(item);
        if (window.uxDiagnostic.events.length > 150) window.uxDiagnostic.events.shift();
      }, true);
    }
    const frame = () => {
      const button = document.querySelector('[data-wizard-next]') || document.querySelector('.dashboard-filters button');
      if (button) {
        const rect = button.getBoundingClientRect();
        const hit = document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2);
        window.uxDiagnostic.frames.push({ at: performance.now(), x: rect.x, y: rect.y, width: rect.width,
          height: rect.height, scrollY, hit: targetName(hit), covered: !button.contains(hit), disabled: button.disabled });
        if (window.uxDiagnostic.frames.length > 80) window.uxDiagnostic.frames.shift();
      }
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  });
}

async function snapshot(page) {
  return page.evaluate(() => ({
    url: location.pathname + location.search + location.hash,
    focus: document.activeElement?.id || document.activeElement?.tagName,
    forms: [...document.forms].filter(form => form.matches('[data-wizard], .dashboard-filters')).map(form => ({
      method: form.method, noValidate: form.noValidate, action: form.getAttribute('action'),
      controls: [...form.elements].filter(el => !['hidden', 'password'].includes(el.type)).map(el => ({
        id: el.id, name: el.name, required: el.required, disabled: el.disabled,
        willValidate: el.willValidate, valid: el.validity?.valid, validationMessage: el.validationMessage,
        visible: Boolean(el.getClientRects().length) && !el.closest('[hidden]'),
      })),
    })),
    activeStep: [...document.querySelectorAll('[data-wizard-step]')].findIndex(el => !el.hidden),
    messages: [...document.querySelectorAll('[data-field-feedback]')].map(el => ({ id: el.id, text: el.textContent })),
    telemetry: window.uxDiagnostic || null,
  }));
}

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
  try {
    const login = await browser.newContext({ locale: 'fr-FR', timezoneId: 'Indian/Antananarivo' });
    const auth = await login.newPage();
    await auth.goto(base + '/comptes/login/');
    await auth.locator('[name="username"]').fill(process.env.PHARMAGEST_USERNAME);
    await auth.locator('[name="password"]').fill(process.env.PHARMAGEST_PASSWORD);
    await Promise.all([auth.waitForURL(url => !url.pathname.includes('/login/')), auth.getByRole('button', { name: 'Se connecter', exact: true }).click()]);
    const storageState = await login.storageState(); // En mémoire seulement : ne pas écrire les cookies.
    await login.close();
    for (const width of [360, 768]) {
      for (const scenario of ['wizard', 'dashboard']) {
        for (const js of scenario === 'wizard' ? [true] : [true, false]) {
          for (const action of ['mouse', 'keyboard']) {
            const id = `${scenario}-${width}-${js ? 'js' : 'sans-js'}-${action}`;
            const context = await browser.newContext({ locale: 'fr-FR', timezoneId: 'Indian/Antananarivo', storageState, viewport: { width, height: 1000 }, javaScriptEnabled: js, colorScheme: 'light' });
            const page = await context.newPage();
            const entry = { page: scenario, role: 'administrateur', width, javascript: js, theme: 'light', action, status: 'running' };
            const errors = [];
            page.on('pageerror', error => errors.push(error.message));
            page.setDefaultTimeout(8000);
            try {
              await page.goto(base + (scenario === 'wizard' ? '/catalogue/medicaments/ajouter/' : '/'));
              if (js) await instrument(page);
              entry.before = await snapshot(page);
              const activate = async button => {
                if (action === 'mouse') await button.click();
                else { await button.focus(); await button.press('Enter'); }
              };
              if (scenario === 'wizard') {
                const next = page.locator('[data-wizard-next]');
                await activate(next);
                assert.equal(await page.evaluate(() => document.activeElement.id), 'id_name', 'Premier champ invalide non focalisé');
                assert(await page.locator('#id_name_feedback').textContent(), 'Erreur de nom non rendue');
                await page.locator('#id_name').focus();
                await page.keyboard.type('Médicament fictif QA');
                await page.locator('#id_form').focus();
                await page.keyboard.type('Comprimé');
                const category = page.locator('#id_category');
                await category.focus();
                await page.keyboard.press('ArrowDown');
                await page.keyboard.press('Enter');
                assert(await category.inputValue(), 'Aucune catégorie sélectionnée');
                entry.filled = await snapshot(page);
                await activate(next);
                await page.locator('#id_purchase_price').waitFor({ state: 'visible' });
                assert.equal(await page.evaluate(() => [...document.querySelectorAll('[data-wizard-step]')].findIndex(el => !el.hidden)), 1);
              } else {
                const start = page.locator('#dashboard-start');
                const end = page.locator('#dashboard-end');
                await start.fill('2000-01-01');
                await end.fill('2000-01-31');
                const button = page.getByRole('button', { name: 'Appliquer la période', exact: true });
                entry.filled = await snapshot(page);
                await Promise.all([
                  page.waitForURL(url => url.searchParams.get('start') === '2000-01-01' && url.searchParams.get('end') === '2000-01-31'),
                  action === 'mouse' ? button.click() : end.press('Enter'),
                ]);
                assert((await page.locator('#dashboard-period-help').textContent()).includes('01/01/2000 au 31/01/2000'));
              }
              entry.status = 'OK';
            } catch (error) {
              entry.status = 'KO';
              entry.error = String(error.message);
            } finally {
              entry.errors = errors;
              entry.after = await snapshot(page).catch(error => ({ unavailable: error.message }));
              entry.capture = id + '.png';
              await page.screenshot({ path: path.join(output, entry.capture), fullPage: true }).catch(error => { entry.captureError = error.message; });
              results.push(entry);
              fs.writeFileSync(path.join(output, 'lot1.json'), JSON.stringify(results, null, 2));
              await context.close();
            }
          }
        }
      }
    }
    const failed = results.filter(item => item.status === 'KO');
    console.log(`Lot 1 : ${results.length - failed.length} OK, ${failed.length} KO. Rapport : ${path.join(output, 'lot1.json')}`);
    process.exitCode = failed.length ? 1 : 0;
  } finally { await browser.close(); }
})().catch(error => { console.error(String(error.message).split(process.env.PHARMAGEST_PASSWORD || '\0').join('[masqué]')); process.exitCode = 1; });

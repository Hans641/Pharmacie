/* Témoin sans PharmaGest, serveur ou identifiants : ne valide aucune recette produit. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const moduleName = process.env.PLAYWRIGHT_MODULE_PATH || 'playwright';
const { chromium } = require(moduleName);
const output = process.env.UX_OUTPUT_DIR;
const packageRoot = path.dirname(require.resolve(moduleName));
const version = JSON.parse(fs.readFileSync(path.join(packageRoot, 'package.json'))).version;
const report = { playwright: version, browsers: [], scope: 'bouton synthétique sans serveur ; aucune preuve de qualité produit' };
const save = () => fs.writeFileSync(path.join(output, 'browser-probe.json'), JSON.stringify(report, null, 2));
(async () => {
  fs.mkdirSync(output, { recursive: true });
  const targets = [{ label: 'configured', executablePath: process.env.CHROME_PATH }];
  if (process.env.CHROME_PATH && fs.existsSync(chromium.executablePath()) && chromium.executablePath() !== process.env.CHROME_PATH) targets.push({ label: 'bundled', executablePath: chromium.executablePath() });
  report.bundledAvailable = fs.existsSync(chromium.executablePath());
  save();
  for (const target of targets) {
    const entry = { target: target.label, launch: 'non exécuté', cases: [] };
    report.browsers.push(entry);
    let browser;
    try {
      browser = await chromium.launch({ headless: true, ...(target.executablePath ? { executablePath: target.executablePath } : {}) });
      entry.launch = 'OK'; entry.version = browser.version();
      for (const js of [true, false]) {
      for (const scenario of ['viewport', 'offscreen-auto', 'offscreen-smooth']) {
        const context = await browser.newContext({ javaScriptEnabled: js, reducedMotion: 'no-preference', viewport: { width: 360, height: 1000 } });
        await context.tracing.start({ screenshots: true, snapshots: true, sources: false });
        const page = await context.newPage();
        page.setDefaultTimeout(4000);
        const row = { javascript: js, scenario };
        entry.cases.push(row);
        try {
          const offscreen = scenario !== 'viewport';
          const behavior = scenario === 'offscreen-smooth' ? 'smooth' : 'auto';
          await page.setContent(`<!doctype html><html lang="fr" style="scroll-behavior:${behavior}"><head><title>Témoin QA</title></head><body style="min-height:${offscreen ? 4000 : 1000}px"><input id="qa-date" type="date" style="position:absolute;left:40px;top:2500px;width:240px;height:48px"><button id="qa-button" style="position:absolute;left:40px;top:${offscreen ? 2600 : 80}px;width:240px;height:64px">Bouton témoin</button></body></html>`);
          if (offscreen) await page.locator('#qa-date').fill('2000-01-31');
          row.conditions = await page.evaluate(() => ({ scrollBehavior: getComputedStyle(document.documentElement).scrollBehavior, scrollY, focus: document.activeElement.id }));
          row.documentPositionBefore = await page.locator('#qa-button').evaluate(el => { const r = el.getBoundingClientRect(); return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height }; });
          await page.evaluate(() => { window.qaProbe = { frames: 0 }; requestAnimationFrame(() => { window.qaProbe.frames++; }); });
          row.before = await page.locator('#qa-button').boundingBox();
          try { await page.locator('#qa-button').click(); row.locatorClick = 'OK'; }
          catch (error) { row.locatorClick = 'KO'; row.error = error.message; }
          row.after = await page.evaluate(() => ({ frames: window.qaProbe.frames, visibility: document.visibilityState, focus: document.activeElement.id, scrollY }));
          row.boundsAfter = await page.locator('#qa-button').boundingBox();
          row.documentPositionAfter = await page.locator('#qa-button').evaluate(el => { const r = el.getBoundingClientRect(); return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height }; });
          // Témoin physique sur cette seule page synthétique ; jamais utilisé pour
          // contourner un défaut dans le scénario de recette de l'application.
          const rect = row.boundsAfter;
          await page.mouse.click(rect.x + rect.width / 2, rect.y + rect.height / 2);
          row.physicalFocus = await page.evaluate(() => document.activeElement.id);
          row.staticGeometry = JSON.stringify(row.documentPositionBefore) === JSON.stringify(row.documentPositionAfter);
          assert.equal(row.physicalFocus, 'qa-button', 'Le témoin physique ne reçoit pas le focus');
        } catch (error) { row.probeError = error.message; }
        finally {
          const name = `${target.label}-${js ? 'js' : 'sans-js'}-${scenario}`;
          await page.screenshot({ path: path.join(output, name + '.png') }).catch(error => { row.captureError = error.message; });
          await context.tracing.stop({ path: path.join(output, name + '-trace.zip') });
          await context.close(); save();
          console.log(`${target.label} ${scenario} ${js ? 'avec JS' : 'sans JS'} : locator=${row.locatorClick || 'non exécuté'}, géométrie fixe=${row.staticGeometry}`);
        }
      }
      }
    } catch (error) { entry.launchError = error.message; process.exitCode = 1; }
    finally { if (browser) await browser.close(); save(); }
  }
  if (report.browsers.some(browser => browser.launchError || browser.cases.some(row => row.locatorClick === 'KO' || row.probeError))) process.exitCode = 1;
  console.log('Témoin navigateur (sans serveur) : ' + path.join(output, 'browser-probe.json'));
})().catch(error => { report.error = error.message; save(); console.error(error.message); process.exitCode = 1; });

'use strict';
const path = require('node:path');

// sRGB / WCAG : calcul effectué après composition des fonds réellement calculés.
function composite(front, back) {
  const alpha = front[3] ?? 1;
  return front.slice(0, 3).map((value, index) => value * alpha + back[index] * (1 - alpha));
}
function contrast(first, second) {
  const luminance = rgb => rgb.map(value => {
    const channel = value / 255;
    return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  }).reduce((sum, channel, index) => sum + channel * [0.2126, 0.7152, 0.0722][index], 0);
  const values = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

// Fonction autonome exécutée par Playwright ; aucune bibliothèque injectée.
function renderedSamples() {
  const samples = [], skipped = [];
  const rgb = value => {
    const match = value.match(/^rgba?\(([^)]+)\)$/);
    if (!match) return null;
    const values = match[1].split(/[,\s/]+/).map(Number);
    return values.length >= 3 && values.every(Number.isFinite) ? values : null;
  };
  for (const el of document.querySelectorAll('body *')) {
    const text = [...el.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(' ').trim();
    const control = el.matches('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]),textarea,select');
    if (!text && !control) continue;
    if (el.closest('svg,script,style,.visually-hidden')) continue;
    if (el.closest('details:not([open])') && !el.closest('summary')) continue;
    const rect = el.getBoundingClientRect(), style = getComputedStyle(el);
    if (!rect.width || !rect.height || style.visibility !== 'visible') continue;
    // Le lien d’évitement hors écran n’est pas du texte visible au repos.
    if (rect.right <= 0 || rect.bottom <= 0) continue;
    const selector = el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}.${[...el.classList].join('.')}`;
    const item = { selector, text: (text || el.getAttribute('aria-label') || el.name || el.tagName).slice(0, 100) };
    let reason = null;
    const backgrounds = [];
    for (let ancestor = el; ancestor; ancestor = ancestor.parentElement) {
      const computed = getComputedStyle(ancestor);
      if (computed.display === 'none' || computed.visibility !== 'visible') { reason = 'masqué'; break; }
      if (Number(computed.opacity) !== 1 || computed.filter !== 'none' || computed.mixBlendMode !== 'normal') reason = 'opacité/filtre/composition : inspection visuelle';
      if (computed.backgroundImage !== 'none') reason = 'image ou dégradé : inspection visuelle';
      const color = rgb(computed.backgroundColor);
      if (!color) reason = 'couleur non sRGB reconnue : inspection visuelle';
      else backgrounds.unshift(color);
    }
    if (reason === 'masqué') continue;
    if (el.matches(':disabled')) reason = 'contrôle désactivé, hors exigence de contraste texte';
    const foreground = rgb(style.color);
    if (!foreground) reason = 'couleur de texte non sRGB reconnue';
    if (reason) { skipped.push({ ...item, reason }); continue; }
    samples.push({ ...item, foreground, backgrounds, fontSize: style.fontSize, fontWeight: style.fontWeight });
  }
  return { samples, skipped };
}

async function inspectPresentation(page, output, stem, print) {
  const measured = await page.evaluate(renderedSamples);
  const pairs = measured.samples.map(sample => {
    const background = sample.backgrounds.reduce((back, front) => composite(front, back), [255, 255, 255]);
    const foreground = composite(sample.foreground, background);
    const ratio = contrast(foreground, background);
    // Cible projet : 4,5 pour tout texte, y compris les grands titres.
    return { ...sample, foreground, background, ratio, result: ratio >= 4.5 ? 'OK' : 'KO' };
  });
  const result = { scope: 'texte direct et valeurs des contrôles, au repos ; cible projet 4,5:1', pairs, skipped: measured.skipped,
    pending: ['Survol, focus, erreurs, placeholder et pseudo-éléments', 'Contrôles natifs ouverts, images, superpositions et lecteur d’écran', 'Zoom navigateur réel à 200 %'] };
  if (print) {
    const viewport = page.viewportSize();
    try {
      // A4, marges 14 mm : largeur imprimable arrondie à 688 CSS px.
      await page.setViewportSize({ width: 688, height: 1000 });
      await page.emulateMedia({ media: 'print' });
      result.print = await page.evaluate(() => {
        const visible = el => [...el.getClientRects()].some(rect => rect.width && rect.height) && getComputedStyle(el).visibility === 'visible';
        return {
          colorScheme: getComputedStyle(document.documentElement).colorScheme,
          background: getComputedStyle(document.body).backgroundColor,
          controls: [...document.querySelectorAll('.sidebar,.topbar,.page-footer,button,input:not([type="hidden"]),select,textarea')].filter(visible).map(el => el.id || el.name || el.tagName),
          headers: [...document.querySelectorAll('thead')].map(el => getComputedStyle(el).display),
          rowsAvoidBreak: [...document.querySelectorAll('tbody tr')].every(el => getComputedStyle(el).breakInside === 'avoid'),
          overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        };
      });
      result.print.capture = `${stem}-print.png`;
      result.print.document = `${stem}-print.pdf`;
      await page.screenshot({ path: path.join(output, result.print.capture), fullPage: true });
      await page.pdf({ path: path.join(output, result.print.document), format: 'A4', preferCSSPageSize: true, printBackground: true });
      result.print.pending = 'PDF généré, découpage multipage et lisibilité à inspecter visuellement ; indépendant des PDF ReportLab.';
    } finally {
      await page.emulateMedia({ media: 'screen' });
      await page.setViewportSize(viewport);
    }
  }
  return result;
}
module.exports = { composite, contrast, inspectPresentation };

'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const {inspectPresentation} = require('./ux_presentation.cjs');
const output = process.env.UX_OUTPUT_DIR, base = process.env.PHARMAGEST_URL;
const rows = [];
const pages = ['/comptes/login/', '/comptes/password_reset/', '/comptes/password_reset/done/', '/comptes/reset/done/', 'template-403', 'template-404', 'template-500'];
const pending = ['Zoom navigateur réel 200 % et texte agrandi sur caisse/formulaires', 'Lecteur d’écran et ordre complet de tabulation', 'Handlers HTTP 403/404/500 : les captures template-* sont des rendus isolés', 'Dialogues métier, contrôles natifs ouverts et états interactifs des autres familles'];
function save() { fs.writeFileSync(path.join(output,'accessibility.json'),JSON.stringify({pending,rows},null,2)); }
(async () => {
 fs.mkdirSync(output,{recursive:true});
 for (const theme of ['light','dark']) for (const js of [true,false]) for (const width of [360,768,1280,1920]) for (const route of pages)
  rows.push({route,theme,javascript:js,width,result:'non exécuté'});
 save();
 const browser = await chromium.launch({headless:true,...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {})});
 try {
 for (const theme of ['light','dark']) for (const js of [true,false]) for (const width of [360,768,1280,1920]) {
  const context = await browser.newContext({colorScheme:theme,javaScriptEnabled:js,reducedMotion:'reduce',viewport:{width,height:1000},locale:'fr-FR',timezoneId:'Indian/Antananarivo'});
  const page = await context.newPage(); page.setDefaultTimeout(8000);
  // Aucun envoi de formulaire : ces scénarios n’ont besoin que des erreurs locales.
  await page.route('**/*', route => route.request().method()==='POST' ? route.abort() : route.continue());
  for (const route of pages) {
   const row=rows.find(r=>r.route===route&&r.theme===theme&&r.javascript===js&&r.width===width);
   row.issues=[];row.scope=route.startsWith('template-')?'rendu de template, pas de statut HTTP':'page HTTP anonyme';
   try {
    const response=await page.goto(base+(route.startsWith('template-')?'/comptes/login/':route));
    assert.equal(response.status(),200);
    if(route.startsWith('template-')) await page.setContent(fs.readFileSync(path.join(process.env.UX_ERROR_FIXTURES,route.slice(9)+'.html'),'utf8'),{waitUntil:'load'});
    assert.equal(await page.locator('html').getAttribute('lang'),'fr');
    assert.equal(await page.locator('h1').count(),1);
    assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).colorScheme),theme);
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Débordement de page');
    // Le bouton Afficher est volontairement hidden sans JS : ne pas le focaliser.
    const button=page.locator('main .btn:visible').first();
    if(await button.count()) {
     await page.keyboard.press('Tab'); // Modalité clavier avant :focus-visible.
     await button.focus();
     row.focus=await button.evaluate(el=>({label:el.textContent.trim(),active:document.activeElement===el,visible:el.matches(':focus-visible'),width:getComputedStyle(el).outlineWidth,style:getComputedStyle(el).outlineStyle,shadow:getComputedStyle(el).boxShadow}));
     assert(row.focus.active && row.focus.visible,'Bouton focalisé en modalité clavier');
     assert(parseFloat(row.focus.width)>=2&&row.focus.style!=='none','Focus visible');
     await button.hover();
     row.hover=await button.evaluate(el=>({color:getComputedStyle(el).color,background:getComputedStyle(el).backgroundColor,transition:getComputedStyle(el).transitionDuration}));
     assert(row.hover.transition.split(',').every(value=>parseFloat(value)===0),'Mouvement réduit : transition active');
    }
    if(route==='/comptes/login/') {
     const toggle=page.locator('[data-password-toggle]');
     if(js) {
      assert(await toggle.isVisible());
      await toggle.focus();await toggle.press('Enter');
      assert.equal(await toggle.getAttribute('aria-pressed'),'true');
      assert.equal((await toggle.innerText()).trim(),'Masquer');
      assert.equal(await page.locator('#id_password').getAttribute('type'),'text');
      await toggle.press('Space');
      assert.equal(await toggle.getAttribute('aria-pressed'),'false');
      assert.equal(await page.locator('#id_password').getAttribute('type'),'password');
     } else assert(!(await toggle.isVisible()));
    }
    if(js && ['/comptes/login/','/comptes/password_reset/'].includes(route)) {
     await page.locator('form button[type="submit"]').click();
     const invalid=page.locator('main [aria-invalid="true"]').first();
     assert(await invalid.count(),'Erreur inline après formulaire vide');
     assert(await invalid.evaluate(el=>document.activeElement===el),'Focus sur le champ invalide');
     row.localError=true;
    }
    row.presentation=await inspectPresentation(page,output,'unused',false);
    assert(row.presentation.pairs.length>0);
    assert.equal(row.presentation.pairs.filter(pair=>pair.result==='KO').length,0,'Contraste après focus/survol/erreur : voir mesures');
   } catch(error) { row.issues.push(error.message); }
   row.capture=`${theme}-${js?'js':'sans-js'}-${width}-${route.replace(/[^a-z0-9]/gi,'_')}.png`;
   try { await page.screenshot({path:path.join(output,row.capture),fullPage:true}); }
   catch(error) {row.issues.push(error.message);row.capture=null;}
   row.result=row.issues.length?'KO':'OK';save();
   console.log(`${row.result} ${theme} ${width} ${js?'JS':'sans JS'} ${route}`);
   if(row.issues.length) console.log(JSON.stringify(row.issues));
  }
  await context.close();
 }
 } finally { await browser.close(); }
 const counts={}; for(const row of rows)counts[row.result]=(counts[row.result]||0)+1;
 console.log(JSON.stringify(counts));process.exitCode=rows.some(row=>row.result!=='OK')?1:0;
})().catch(error=>{console.error(error.message);process.exitCode=1;});

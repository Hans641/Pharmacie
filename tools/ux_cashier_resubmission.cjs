'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const base=process.env.PHARMAGEST_URL,output=process.env.UX_OUTPUT_DIR;
const rows=JSON.parse(process.env.UX_BENCH_TRIALS).map(t=>({...t,result:'non exécuté'}));
const save=()=>fs.writeFileSync(path.join(output,'resubmission.json'),JSON.stringify({scope:'12 ventes isolées ; audit final dans summary.json',rows},null,2));
(async()=>{
 save(); const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try {
 const auth=await browser.newContext();const login=await auth.newPage();await login.goto(base+'/comptes/login/');
 await login.locator('[name=username]').fill(process.env.PHARMAGEST_USERNAME);await login.locator('[name=password]').fill(process.env.PHARMAGEST_PASSWORD);
 await Promise.all([login.waitForURL(url=>!url.pathname.includes('/login/')),login.getByRole('button',{name:'Se connecter',exact:true}).click()]);
 const storageState=await auth.storageState();await auth.close();
 for(const row of rows){
 const context=await browser.newContext({storageState,javaScriptEnabled:row.javascript,viewport:{width:row.width,height:1000},locale:'fr-FR',timezoneId:'Indian/Antananarivo'});
 const page=await context.newPage();page.setDefaultTimeout(10000);
 row.pageErrors=[];page.on('pageerror',error=>{row.pageErrors.push(error.message);save();});
 row.result='en cours';row.lockEvents=[];save();
 let lockSignal;
 const locked=new Promise(resolve=>lockSignal=resolve);
 await page.exposeBinding('__uxLockState',(_source,state)=>{
  row.lockEvents.push(state);save();
  if(state.disabled && state.submitting==='true' && state.busy==='true')lockSignal(state);
 });
 let release;const barrier=new Promise(resolve=>release=resolve);let payload;row.browserValidationRequests=0;
 const url=`${base}/ventes/${row.sale}/`;
 await page.route('**/*',async route=>{
  const request=route.request();
  if(request.method()==='POST'&&new URLSearchParams(request.postData()||'').get('action')==='validate'){
   row.browserValidationRequests++;payload=request.postData();
   if(row.scenario!=='retour')await barrier;
  }
  await route.continue();
 });
 try{
 await page.goto(base+'/ventes/');await page.goto(url);
 await page.locator('#id_medicine').selectOption(String(row.products[0].id));await page.locator('#id_quantity').fill('1');
 await Promise.all([page.waitForNavigation(),page.locator('[data-add-to-cart]').click()]);
 await page.locator('[name=method][value=cash]').check();await page.locator('[name=confirm]').check();
 const button=page.locator('[data-checkout] button[type=submit]');
 await button.scrollIntoViewIfNeeded();await button.focus();
 // Sonde installée avant navigation : aucune évaluation DOM après le POST.
 row.formMethod=await button.evaluate(el=>{
  const emit=()=>{void window.__uxLockState({disabled:el.disabled,submitting:el.form.dataset.submitting||null,busy:el.form.getAttribute('aria-busy')}).catch(()=>{});};
  new MutationObserver(emit).observe(el.form,{subtree:true,attributes:true,attributeFilter:['disabled','data-submitting','aria-busy']});
  emit();
  return {attribute:el.form.getAttribute('method'),propertyType:typeof el.form.method,propertyClass:Object.prototype.toString.call(el.form.method)};
 });
 const sent=page.waitForRequest(r=>r.method()==='POST'&&new URLSearchParams(r.postData()||'').get('action')==='validate');
 if(row.scenario==='double-clic'){
  const box=await button.boundingBox();assert(box);await page.mouse.click(box.x+box.width/2,box.y+box.height/2,{clickCount:2});await sent;
 }else{
  await page.keyboard.press('Enter');await sent;
  if(row.scenario==='entree-repetee'){
   if(row.javascript){
    let deadline;
    try {
     row.lockAfterWait=await Promise.race([locked,new Promise((_,reject)=>{
      deadline=setTimeout(()=>reject(new Error('Verrou disabled non observé après 10 s ; voir lockEvents')),10000);
     })]);
    } finally {clearTimeout(deadline);}
    assert.equal(row.lockAfterWait.disabled,true);
    assert.equal(row.lockAfterWait.submitting,'true');
    assert.equal(row.lockAfterWait.busy,'true');
   }
   await page.keyboard.press('Enter');await page.keyboard.press('Enter');
  }
 }
 release();await page.locator('#sale-success-title').waitFor({state:'visible'});
 if(row.javascript&&row.scenario!=='retour')assert.equal(row.browserValidationRequests,1,'Verrou JS : une seule requête attendue');
 if(row.scenario==='retour'){
  await page.goBack({waitUntil:'load'});row.backPath=new URL(page.url()).pathname;
  // Historique variable selon PRG/cache : inspecter sans imposer une page fictive.
  if(new URL(page.url()).pathname===`/ventes/${row.sale}/`)assert.equal(await page.locator('[data-checkout] button[type=submit]:visible').count(),0,'Formulaire encaissable ressuscité');
  await page.goto(url);await page.locator('#sale-success-title').waitFor({state:'visible'});
 }
 assert(payload,'Payload de validation capturé en mémoire');
 // Rejeu explicite de la validation déjà réussie, CSRF/session conservés en mémoire.
 const replay=await context.request.post(url,{form:Object.fromEntries(new URLSearchParams(payload))});
 row.replayStatus=replay.status();assert.equal(replay.status(),200);
 await page.reload();await page.locator('#sale-success-title').waitFor({state:'visible'});
 assert.equal(await page.locator('[data-checkout]').count(),0);
 assert.deepEqual(row.pageErrors,[],'Exception JavaScript : voir pageErrors');
 row.result='OK';
 }catch(error){row.result='KO';row.error=error.message;}
 finally{release();}
 row.capture=`${row.scenario}-${row.javascript?'js':'sans-js'}-${row.width}.png`;
 try{await page.screenshot({path:path.join(output,row.capture),fullPage:true});}catch(error){row.result='KO';row.error=error.message;row.capture=null;}
 save();console.log(`${row.result} ${row.scenario} ${row.javascript?'JS':'sans JS'} ${row.width}`);await context.close();
 }
 }finally{await browser.close();}
 process.exitCode=rows.every(r=>r.result==='OK')?0:1;
})().catch(error=>{console.error(error.message.split(process.env.PHARMAGEST_PASSWORD||'\0').join('[masqué]'));process.exitCode=1;});

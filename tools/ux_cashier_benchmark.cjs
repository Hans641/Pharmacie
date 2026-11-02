'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const trials=JSON.parse(process.env.UX_BENCH_TRIALS),output=process.env.UX_OUTPUT_DIR,base=process.env.PHARMAGEST_URL;
const rows=trials.map(t=>({...t,result:'non exécuté'}));
const report={conditions:{viewport:1280,theme:'light',javascript:true,role:'caissier',interaction:'commandes clavier Playwright sans délai humain ; contrôle professionnel simulé sur données fictives'},pending:['Chronométrage humain','Double clic, Entrée répétée et retour navigateur : protocole séparé'],rows};
function save(){fs.writeFileSync(path.join(output,'timings.json'),JSON.stringify(report,null,2));}
const clock=page=>page.evaluate(()=>performance.timeOrigin+performance.now());
(async()=>{
 save();const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 report.conditions.browser=browser.version();
 try{
 const context=await browser.newContext({viewport:{width:1280,height:1000},colorScheme:'light',locale:'fr-FR',timezoneId:'Indian/Antananarivo'});
 const page=await context.newPage();page.setDefaultTimeout(10000);
 await page.goto(base+'/comptes/login/');await page.locator('[name=username]').fill(process.env.PHARMAGEST_USERNAME);await page.locator('[name=password]').fill(process.env.PHARMAGEST_PASSWORD);
 await Promise.all([page.waitForURL(url=>!url.pathname.includes('/login/')),page.getByRole('button',{name:'Se connecter',exact:true}).press('Enter')]);
 for(const row of rows){
 try{
 await page.goto(`${base}/ventes/${row.sale}/`);
 const start=await clock(page);
 for(const product of row.products){
 await page.keyboard.press('F2');await page.locator('#cash-search').fill(product.barcode);
 await Promise.all([page.waitForURL(url=>url.searchParams.get('q')===product.barcode),page.locator('#cash-search').press('Enter')]);
 await page.locator('#id_medicine').selectOption(String(product.id));await page.locator('#id_quantity').fill('1');
 await Promise.all([page.waitForNavigation(),page.locator('[data-add-to-cart]').press('Enter')]);
 assert.equal(await page.locator(`[data-cart-lot="${product.lot}"]`).count(),1,'Lot FEFO attendu');
 }
 if(row.scenario==='trois-produits')assert(await page.locator('#cart .badge.warning').count()>0,'Alerte péremption proche');
 await page.keyboard.press('F4');await page.locator('[name=method][value=cash]').press('Space');
 await page.locator('#cash-received').fill(String(row.products.length*1500));
 if(row.products.some(p=>p.prescription)){await page.locator('[name=prescription_checked]').focus();await page.keyboard.press('Space');}
 await page.locator('[name=confirm]').focus();await page.keyboard.press('Space');
 await Promise.all([page.waitForNavigation(),page.locator('[data-checkout] button[type=submit]').press('Enter')]);
 await page.locator('#sale-success-title').waitFor({state:'visible'});
 row.durationMs=(await clock(page))-start;
 assert(await page.getByRole('link',{name:'Télécharger le reçu PDF',exact:true}).isVisible());
 row.result='OK';
 }catch(error){row.result='KO';row.error=error.message;}
 row.capture=`${row.scenario}-${row.iteration}.png`;
 await page.screenshot({path:path.join(output,row.capture),fullPage:true});save();
 }
 report.statistics={};
 for(const scenario of [...new Set(rows.map(r=>r.scenario))]){
 const subset=rows.filter(r=>r.scenario===scenario),times=subset.filter(r=>r.result==='OK').map(r=>r.durationMs).sort((a,b)=>a-b);
 report.statistics[scenario]={executed:subset.filter(r=>r.result!=='non exécuté').length,ok:times.length,minimumMs:times[0]??null,maximumMs:times.at(-1)??null,medianMs:times.length===5?times[2]:null};
 }
 report.automatedSimpleTarget=report.statistics.simple.ok===5?report.statistics.simple.medianMs<30000:null;save();
 await context.close();process.exitCode=rows.every(r=>r.result==='OK')?0:1;
 }finally{await browser.close();}
})().catch(error=>{console.error(error.message.split(process.env.PHARMAGEST_PASSWORD||'\0').join('[masqué]'));process.exitCode=1;});

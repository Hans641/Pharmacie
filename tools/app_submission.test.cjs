'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../static/js/app.js'),'utf8');
function setup(method='post',shadow=true){
 const listeners={},timers=[];
 class Form {
  constructor(){this.method=shadow?{length:2}:method;this.dataset={};this.attributes={method};}
  getAttribute(key){return this.attributes[key]??null;}
  setAttribute(key,value){this.attributes[key]=value;}
 }
 const form=new Form();
 const button={disabled:false,dataset:{},setAttribute(key,value){this[key]=value;}};
 form.querySelectorAll=()=>[button];
 const document={querySelector:()=>null,querySelectorAll:()=>[],documentElement:{classList:{add(){}}},addEventListener:(type,fn)=>listeners[type]=fn};
 const window={addEventListener(){}};
 vm.runInNewContext(source,{document,window,HTMLFormElement:Form,matchMedia:()=>({matches:false}),setTimeout:fn=>timers.push(fn)});
 const submit=()=>{let prevented=false;listeners.submit({target:form,preventDefault(){prevented=true;}});return prevented;};
 return {form,button,timers,submit};
}
test('champ method : verrou synchrone et désactivation différée sans exception',()=>{
 const s=setup();s.submit();assert.equal(s.form.dataset.submitting,'true');assert.equal(s.form.attributes['aria-busy'],'true');
 assert.equal(s.button.disabled,false);assert.equal(s.timers.length,1);s.timers[0]();assert.equal(s.button.disabled,true);
});
test('champ method : soumission répétée empêchée',()=>{const s=setup();s.submit();assert.equal(s.submit(),true);assert.equal(s.timers.length,1);});
test('GET et formulaire dialog ignorés',()=>{for(const method of ['get','dialog']){const s=setup(method,false);assert.equal(s.submit(),false);assert.equal(s.form.dataset.submitting,undefined);assert.equal(s.timers.length,0);}});

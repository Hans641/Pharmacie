const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../static/js/theme.js'), 'utf8');
function setup(saved, dark, blocked=false) {
  const listeners={}, media={}, change={};
  const control={hidden:true}, metas=[{content:''},{content:''}];
  const select={value:'system',closest:()=>control,addEventListener:(key,fn)=>change[key]=fn};
  const system={matches:dark,addEventListener:(key,fn)=>media[key]=fn};
  const document={documentElement:{dataset:{}},querySelector:()=>select,querySelectorAll:()=>metas,addEventListener:(key,fn)=>listeners[key]=fn};
  const storage={value:saved};
  const localStorage={getItem:()=>{if(blocked)throw Error();return storage.value;},setItem:(_,value)=>{if(blocked)throw Error();storage.value=value;},removeItem:()=>{if(blocked)throw Error();storage.value=null;}};
  vm.runInNewContext(source,{document,localStorage,window:{matchMedia:()=>system,addEventListener:(key,fn)=>listeners[key]=fn}});
  listeners.DOMContentLoaded();
  return {document,metas,select,system,media,change,listeners,storage};
}
test('système sombre puis changement du système',()=>{const s=setup(null,true);assert(s.metas.every(meta=>meta.content==='#101916'));s.system.matches=false;s.media.change();assert(s.metas.every(meta=>meta.content==='#f4f7f5'));});
test('choix clair prioritaire sur système sombre',()=>{const s=setup('light',true);assert.equal(s.document.documentElement.dataset.theme,'light');assert(s.metas.every(meta=>meta.content==='#f4f7f5'));s.media.change();assert(s.metas.every(meta=>meta.content==='#f4f7f5'));});
test('bascule manuelle puis retour système',()=>{const s=setup(null,false);s.select.value='dark';s.change.change();assert.equal(s.storage.value,'dark');assert(s.metas.every(meta=>meta.content==='#101916'));s.select.value='system';s.change.change();assert.equal(s.storage.value,null);assert(s.metas.every(meta=>meta.content==='#f4f7f5'));});
test('synchronisation depuis un autre onglet',()=>{const s=setup(null,false);s.listeners.storage({key:'pharmagest-theme',newValue:'dark'});assert(s.metas.every(meta=>meta.content==='#101916'));});
test('stockage indisponible : bascule sans erreur',()=>{const s=setup(null,false,true);s.select.value='dark';s.change.change();assert(s.metas.every(meta=>meta.content==='#101916'));});

import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('taipei_parking_mobile/index.html','utf8');
const script=html.slice(html.indexOf("(()=>{'use strict';"),html.lastIndexOf('</script>'));
async function run(search='',fail=false){
 const nodes=new Map(),requests=[],history=[];const node=id=>{if(!nodes.has(id))nodes.set(id,{value:'',textContent:'',hidden:false,disabled:false,innerHTML:'',dataset:{},classList:{add(){},remove(){}},addEventListener(){},scrollIntoView(){},replaceChildren(){},setAttribute(){}});return nodes.get(id)};
 const ctx={URLSearchParams,URL,console,Date,Intl,Number,Set,Map,Math,Error,Promise,setTimeout,clearTimeout,location:{search,hash:''},history:{replaceState(a,b,url){history.push(url)}},document:{getElementById:node,querySelectorAll:()=>[],addEventListener(){}},navigator:{},setInterval(){},AbortSignal,fetch:async url=>{requests.push(String(url));if(fail)throw Error('mock service unavailable');return {ok:true,json:async()=>[]}}};vm.createContext(ctx);
 const testScript=script.replace('start();',`setupMap=()=>{};load=async()=>{globalThis.loaded.push({...target})};globalThis.loaded=[];globalThis.api={start,query,pickPoint,searchPickedPoint,clearDraft,getTarget:()=>target,hasDraft:()=>!!draftPoint,setMap:m=>{map=m;centerMark={setLatLng(){},setPopupContent(){}};ring={setLatLng(){},getBounds(){return []}}},setLoading:v=>isLoading=v};`);
 vm.runInContext(testScript,ctx);await ctx.api.start();return {context:ctx,...ctx,node,requests,history};
}
let t=await run();assert.equal(t.api.getTarget().name,'台鐵台北車站');assert.equal(t.node('dest').value,'');assert.equal(t.requests.length,0);
t=await run('?lat=25.01733&lng=121.53324&name=台大正門');assert.equal(t.api.getTarget().lat,25.01733);assert.equal(t.requests.length,0);
t=await run('?q=找不到的校區',true);assert.equal(t.api.getTarget().lat,25.0477214);assert.equal(t.api.getTarget().name,'找不到的校區');assert.equal(t.node('dest').value,'找不到的校區');assert.equal(t.node('destination-error').hidden,false);assert.match(t.node('map-current').textContent,/台鐵台北車站/);assert.match(t.history.at(-1),/unresolved=1/);
const saved=t.history.at(-1);const reload=await run(saved,true);assert.equal(reload.requests.length,0);assert.equal(reload.api.getTarget().name,'找不到的校區');assert.equal(reload.api.getTarget().unresolved,true);
let markerPoint;const fakeMarker={addTo(){return this},on(){return this},setLatLng(v){markerPoint=v;return this}};
t.context.L={divIcon:()=>({}),marker:()=>fakeMarker};t.api.setMap({removeLayer(){},setView(){},fitBounds(){}});
// Use the real selection functions, with a minimal map renderer.

t.api.pickPoint({lat:25.01733,lng:121.53324});assert.equal(t.api.hasDraft(),true);assert.equal(t.api.getTarget().unresolved,true);const before=t.requests.length;await t.api.searchPickedPoint();assert.equal(t.requests.length,before);assert.equal(t.api.getTarget().lat,25.01733);assert.equal(t.api.getTarget().picked,true);assert.equal(t.api.getTarget().name,'找不到的校區');assert.equal(t.node('destination-error').hidden,true);assert.match(t.history.at(-1),/pin=1/);assert.doesNotMatch(t.history.at(-1),/unresolved/);
const requestsBeforeRepeat=t.requests.length;await t.api.query();assert.equal(t.requests.length,requestsBeforeRepeat);assert.equal(t.api.getTarget().picked,true);assert.equal(t.api.getTarget().lat,25.01733);
const pinned=await run(t.history.at(-1));assert.equal(pinned.api.getTarget().picked,true);assert.equal(pinned.api.getTarget().lat,25.01733);assert.equal(pinned.requests.length,0);
t.api.pickPoint({lat:25.02,lng:121.54});t.api.clearDraft();assert.equal(t.api.getTarget().lat,25.01733);assert.equal(t.api.hasDraft(),false);
t.api.setLoading(true);t.api.pickPoint({lat:25.04,lng:121.55});assert.equal(t.api.hasDraft(),false);t.api.setLoading(false);
t.api.pickPoint({lat:99,lng:121.5});assert.equal(t.api.hasDraft(),false);
t.node('dest').value='';await t.api.query();assert.equal(t.api.getTarget().lat,25.0477214);assert.equal(t.api.getTarget().name,'台鐵台北車站');assert.equal(t.node('destination-error').hidden,true);assert.equal(t.node('dest').value,'');
const bad=await run('?lat=bad&lng=121.5&name=測試院區');assert.equal(bad.api.getTarget().name,'測試院區');assert.equal(bad.api.getTarget().unresolved,true);assert.equal(bad.api.getTarget().lat,25.0477214);
console.log('Passed: defaults, explicit coordinates, failed-query name retention, fallback reload, pin confirmation, pin reload, cancellation, busy/out-of-range guard, empty query reset.');
const apple='Map Itemhttps://maps.apple.com/place?address=National%20Taiwan%20University%0ANo.%201%20Roosevelt%20Rd%20Sec%204%0ADaan%20District,%20Taipei%20City%2010617%0ATaiwan&coordinate=25.021666,121.535191&name=NTU%20Sports%20Center&place-id=IA3BC97A572D6BA2B&map=exploreNTU Sports Center';
t=await run('?q='+encodeURIComponent(apple));assert.equal(t.api.getTarget().lat,25.021666);assert.equal(t.api.getTarget().lon,121.535191);assert.equal(t.api.getTarget().name,'NTU Sports Center');assert.equal(t.api.getTarget().resolution.provider,'apple-url');assert.equal(t.requests.length,0);assert.equal(t.node('destination-error').hidden,true);assert.match(t.node('resolution-source').textContent,/Apple Maps/);assert.match(t.node('resolution-address').textContent,/National Taiwan University/);
const appleReload=await run(t.history.at(-1));assert.equal(appleReload.api.getTarget().resolution.provider,'apple-url');assert.equal(appleReload.requests.length,0);
t=await run('?q='+encodeURIComponent('https://maps.apple.com/?ll=25.021666,121.535191&q=NTU'));assert.equal(t.api.getTarget().lat,25.021666);
t=await run('?q='+encodeURIComponent('https://maps.apple.com/place?coordinate=999,121&name=NTU'));assert.equal(t.api.getTarget().unresolved,true);
t=await run('?q='+encodeURIComponent('https://maps.apple.com.evil.example/place?coordinate=25,121&name=NTU'));assert.equal(t.api.getTarget().unresolved,true);
console.log('Passed Apple Maps mixed share text, exact coordinates/name/address, zero geocoder requests, provenance reload, legacy ll, invalid coordinates and spoofed host rejection.');

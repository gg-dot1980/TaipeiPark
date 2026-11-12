import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import worker from '../worker/index.js';
const originalFetch=globalThis.fetch,originalCaches=globalThis.caches;
const rows=[{lat:'25.0531989',lon:'121.5191720',name:'網路回傳的測試地標',display_name:'網路回傳的測試地標, 臺北市',osm_type:'way',osm_id:1234}];
const requests=[],saved=new Map();
globalThis.caches={default:{async match(r){return saved.get(r.url)?.clone()},async put(r,response){saved.set(r.url,response.clone())}}};
globalThis.fetch=async (url,options)=>{requests.push({url:String(url),options});return Response.json(rows)};
try{
 let r=await worker.fetch(new Request('https://example.test/api/geocode?q=建中紅樓'));
 assert.equal(r.headers.get('X-Geocode-Cache'),'MISS');assert.equal(r.headers.get('Cache-Control'),'no-store');assert.equal((await r.json())[0].name,rows[0].name);assert.equal(requests.length,1);assert.match(requests[0].url,/nominatim.openstreetmap.org/);assert.match(decodeURIComponent(requests[0].url),/q=建中紅樓/);const stamp=r.headers.get('X-Geocode-Fetched-At');assert.ok(stamp);
 r=await worker.fetch(new Request('https://example.test/api/geocode?q=建中紅樓'));assert.equal(r.headers.get('X-Geocode-Cache'),'HIT');assert.equal(r.headers.get('X-Geocode-Fetched-At'),stamp);assert.equal(requests.length,1);assert.equal((await r.json())[0].lat,'25.0531989');
 r=await worker.fetch(new Request('https://example.test/api/geocode?q=其他地點'));assert.equal(r.headers.get('X-Geocode-Cache'),'MISS');assert.equal(requests.length,2);
 assert.ok([...saved.keys()].every(k=>k.includes('network-v5')));
 globalThis.caches={default:{async match(){throw Error('cache unavailable')},async put(){throw Error('cache unavailable')}}};r=await worker.fetch(new Request('https://example.test/api/geocode?q=快取故障'));assert.equal(r.headers.get('X-Geocode-Cache'),'BYPASS');assert.equal((await r.json())[0].name,rows[0].name);
 globalThis.fetch=async()=>new Response('offline',{status:503});r=await worker.fetch(new Request('https://example.test/api/geocode?q=網路故障'));assert.equal(r.status,502);assert.ok(!r.headers.get('X-Geocode-Fetched-At'));
 globalThis.fetch=async()=>new Response('',{status:302,headers:{Location:'https://www.google.com/maps/place/'+encodeURIComponent('測試入口')+'/data=!3d25.01733!4d121.53324'}});r=await worker.fetch(new Request('https://example.test/api/resolve-maps?url='+encodeURIComponent('https://maps.app.goo.gl/test')));const pin=await r.json();assert.equal(pin.lat,25.01733);assert.equal(pin.resolution.provider,'google-url');assert.equal(pin.resolution.name,'測試入口');assert.equal(pin.resolution.via,'Google Maps 短網址轉址');
}finally{globalThis.fetch=originalFetch;if(originalCaches===undefined)delete globalThis.caches;else globalThis.caches=originalCaches}
const html=fs.readFileSync('taipei_parking_mobile/index.html','utf8'),script=html.slice(html.indexOf("(()=>{'use strict';"),html.lastIndexOf('</script>'));
assert.doesNotMatch(html,/VERIFIED_PLACES|verifiedDestination|文化部建國中學紅樓/);assert.equal(fs.existsSync('data/verified-places.json'),false);
async function browser(search,response=rows){
 const nodes=new Map(),calls=[],urls=[];const node=id=>{if(!nodes.has(id))nodes.set(id,{value:'',textContent:'',hidden:false,disabled:false,innerHTML:'',dataset:{},classList:{add(){},remove(){}},addEventListener(){},scrollIntoView(){},replaceChildren(){},setAttribute(){}});return nodes.get(id)};
 const ctx={URLSearchParams,URL,console,Date,Intl,Number,Set,Map,Math,Error,Promise,setTimeout,clearTimeout,location:{search,hash:''},history:{replaceState(a,b,url){urls.push(url)}},document:{getElementById:node,querySelectorAll:()=>[],addEventListener(){}},setInterval(){},navigator:{},AbortSignal,fetch:async url=>{calls.push(String(url));return {ok:true,headers:new Headers({'X-Geocode-Cache':'HIT','X-Geocode-Fetched-At':'2026-10-28T00:30:00Z'}),json:async()=>typeof response==='function'?response(String(url)):response}}};vm.createContext(ctx);
 vm.runInContext(script.replace('start();',`setupMap=()=>{};load=async()=>{};globalThis.api={start,resolveDest,query,candidateMatches,geocodeCandidates,parseLocalDestination,previewApproximate,searchPickedPoint,getTarget:()=>target,getDraft:()=>draftPoint,setMap:m=>{map=m;centerMark={setLatLng(){},setPopupContent(){}};ring={setLatLng(){},getBounds(){return []}}}};`),ctx);await ctx.api.start();return {ctx,node,calls,urls};
}
let b=await browser('?q=測試地標',[{...rows[0],name:'實際回傳的測試地標名稱',display_name:'實際回傳的測試地標名稱, 臺北市'}]);assert.equal(b.calls.length,1);assert.match(b.calls[0],/v=network-v5/);assert.equal(b.api,undefined);assert.equal(b.ctx.api.getTarget().name,'實際回傳的測試地標名稱');assert.equal(b.node('dest').value,'測試地標');assert.equal(b.node('resolution-name').textContent,'實際回傳的測試地標名稱');assert.match(b.node('resolution-source').textContent,/Nominatim／OpenStreetMap/);assert.match(b.node('resolution-cache').textContent,/快取命中/);assert.match(b.node('resolution-query').textContent,/實際送往解析服務：測試地標/);assert.match(b.node('resolution-link').href,/openstreetmap.org\/way\/1234/);
const restored=await browser(b.urls.at(-1));assert.equal(restored.calls.length,0);assert.equal(restored.node('resolution-name').textContent,'實際回傳的測試地標名稱');assert.match(restored.node('resolution-source').textContent,/上次來源註記/);assert.match(restored.node('resolution-cache').textContent,/本次未重新查詢/);
b=await browser('?q=建中紅樓',rows);assert.equal(b.calls.length,1);assert.equal(b.ctx.api.getTarget().lat,25.0477214);assert.equal(b.ctx.api.getTarget().name,'建中紅樓');assert.equal(b.node('resolution-name').textContent,'網路回傳的測試地標（未採用）');assert.match(b.node('resolution-source').textContent,/預設座標/);assert.match(b.node('resolution-route').textContent,/Nominatim.*未採用/);
b=await browser('?q=不存在的地點',[]);assert.match(b.node('resolution-name').textContent,/解析失敗/);assert.match(b.node('resolution-source').textContent,/預設/);
b=await browser('?q='+encodeURIComponent('https://www.google.com/maps/place/測試入口/data=!3d25.01733!4d121.53324'));assert.equal(b.calls.length,0);assert.equal(b.node('resolution-name').textContent,'測試入口');assert.match(b.node('resolution-source').textContent,/Google Maps 網址/);assert.equal(b.ctx.api.getTarget().lat,25.01733);
b=await browser('?q=25.01733,121.53324');assert.equal(b.calls.length,0);assert.match(b.node('resolution-source').textContent,/輸入的經緯度/);assert.doesNotMatch(b.node('resolution-source').textContent,/Google/);
b=await browser('?lat=25.030936&lng=121.512235&name=建國中學紅樓');assert.equal(b.calls.length,0);assert.match(b.node('resolution-source').textContent,/原始解析來源未附/);assert.doesNotMatch(b.node('resolution-source').textContent,/文化部|Nominatim/);
b=await browser('');assert.equal(b.calls.length,0);assert.match(b.node('resolution-name').textContent,/未進行地標解析/);assert.match(b.node('resolution-source').textContent,/預設/);
console.log('Network-only geocoding, cache HIT/MISS/failure isolation, source/name provenance, mismatch rejection, restored metadata, explicit coordinates and removed overrides passed.');

const c=await browser('');const shared='10673臺北市大安區學府里基隆路四段42巷5號台大農場本場';assert.deepEqual(Array.from(c.ctx.api.geocodeCandidates(shared)),['台大農場本場','臺北市大安區 台大農場本場','臺北市大安區基隆路四段42巷5號','臺北市大安區基隆路4段42巷5號','基隆路四段42巷 5','臺北市大安區基隆路四段42巷','臺北市大安區基隆路四段']);
const missing=await browser('?q='+encodeURIComponent(shared),[]);assert.equal(missing.calls.length,7);assert.match(missing.node('resolution-attempts').textContent,/基隆路四段42巷5號/);assert.equal(missing.ctx.api.getTarget().lat,25.0477214);console.log('Shared address splitting, village removal, numeral variants and no-result diagnostics passed');

const local=c.ctx.api.parseLocalDestination(shared);assert.equal(local.city,'臺北市');assert.equal(local.district,'大安區');assert.equal(local.name,'台大農場本場');assert.equal(local.street,'基隆路');assert.equal(local.section,'四段');assert.equal(local.lane,'42巷');assert.equal(local.number,'5號');assert.equal(c.ctx.api.parseLocalDestination('臺北市立美術館').name,'臺北市立美術館');
const laneRow={lat:'25.012',lon:'121.539',name:'基隆路四段42巷',display_name:'基隆路四段42巷, 大安區, 臺北市',class:'highway',type:'residential',address:{road:'基隆路四段42巷',suburb:'大安區',city:'臺北市'},osm_type:'way',osm_id:123};
const roadRow={...laneRow,name:'基隆路四段',display_name:'基隆路四段, 大安區, 臺北市',address:{...laneRow.address,road:'基隆路四段'}};const near=await browser('?q='+encodeURIComponent(shared),[roadRow]);assert.equal(near.ctx.api.getTarget().lat,25.0477214);assert.equal(near.ctx.api.getTarget().resolution.precision,'road');assert.equal(near.ctx.api.getTarget().resolution.pendingConfirmation,true);assert.equal(near.node('approximate-location').hidden,false);assert.match(near.node('resolution-parts').textContent,/門牌：5號/);assert.match(near.node('resolution-precision').textContent,/不是確切門牌/);const nearUrl=near.urls.at(-1);const reNear=await browser(nearUrl);assert.equal(reNear.calls.length,0);assert.equal(reNear.node('approximate-location').hidden,false);assert.equal(reNear.ctx.api.getTarget().lat,25.0477214);
const fakeMarker={addTo(){return this},on(){return this},setLatLng(){return this}};near.ctx.L={divIcon:()=>({}),marker:()=>fakeMarker};near.ctx.api.setMap({removeLayer(){},setView(){},fitBounds(){}});const beforePreview=near.calls.length;near.ctx.api.previewApproximate();assert.equal(near.ctx.api.getDraft().lat,25.012);assert.equal(near.ctx.api.getTarget().lat,25.0477214);await near.ctx.api.searchPickedPoint();assert.equal(near.calls.length,beforePreview);assert.equal(near.ctx.api.getTarget().lat,25.012);assert.equal(near.ctx.api.getTarget().resolution.manualConfirmed,true);assert.equal(near.ctx.api.getTarget().resolution.pendingConfirmation,false);assert.equal(near.node('approximate-location').hidden,true);assert.match(near.node('resolution-name').textContent,/手動確認/);
const door=await browser('?q='+encodeURIComponent(shared),[{...laneRow,name:'測試門牌',class:'building',type:'yes',address:{...laneRow.address,house_number:'5'}}]);assert.equal(door.ctx.api.getTarget().lat,25.012);assert.equal(door.ctx.api.getTarget().resolution.precision,'address');assert.equal(door.node('approximate-location').hidden,true);
const wrong=await browser('?q='+encodeURIComponent(shared),[{...laneRow,name:'台大農場本場',display_name:'台大農場本場, 新北市',address:{city:'新北市',suburb:'新店區',road:'莒光路'}}]);assert.equal(wrong.ctx.api.getTarget().lat,25.0477214);assert.equal(wrong.node('approximate-location').hidden,true);
console.log('Local components, precision levels, wrong-city rejection, pending preview/reload and explicit confirmation passed.');

assert.equal(c.ctx.api.candidateMatches({q:'臺北市大安區基隆路四段42巷5號',kind:'address',parts:local},{...laneRow,address:{...laneRow.address,house_number:'15'}}),false);assert.equal(c.ctx.api.parseLocalDestination('104227臺北市中山區 Section 3, Zhongshan N Rd, 181號臺北市立美術館').name,'臺北市立美術館');console.log('Conflicting door numbers and mixed-language POI extraction passed');

const directLane=await browser('?q='+encodeURIComponent(shared),[laneRow]);assert.equal(directLane.ctx.api.getTarget().lat,25.0477214);assert.equal(directLane.ctx.api.getTarget().resolution.precision,'lane');assert.equal(directLane.node('approximate-location').hidden,false);assert.equal(directLane.ctx.api.getTarget().resolution.pendingConfirmation,true);console.log('Door queries resolving only to a lane require confirmation.');

const matchCtx={};vm.createContext(matchCtx);const source=fs.readFileSync('taipei_parking_mobile/index.html','utf8');vm.runInContext(source.slice(source.indexOf('function placeNorm('),source.indexOf('async function nominatim(')),matchCtx);
const matches=matchCtx.geocodeNameMatches;
assert.equal(matches('台北市政府',{name:'政大附中',display_name:'政大附中, 臺北市'}),false);
const hall={name:'臺北市政府',type:'townhall',address:{city:'臺北市',suburb:'信義區',road:'市府路',house_number:'1'}};
assert.equal(matches('台北市政府',hall),true);assert.equal(matches('台北市政府',{...hall,type:'station'}),false);assert.equal(matches('台北市政府',{...hall,name:'臺北市政府警察局'}),false);assert.equal(matches('台北市政府',{...hall,address:{...hall.address,house_number:'2'}}),false);
assert.equal(matches('北投捷運站',{name:'捷運北投站',type:'train_station'}),true);assert.equal(matches('北投捷運站',{name:'捷運新北投站',type:'train_station'}),false);assert.equal(matches('北投捷運站',{name:'捷運北投站(大興)',type:'bus_stop'}),false);
console.log('Passed official-address/type/name validation and transit-order normalization with neighboring-station/bus-stop rejection.');

assert.equal(c.ctx.api.parseLocalDestination('士林夜市').city,'');assert.equal(c.ctx.api.parseLocalDestination('饒河街觀光夜市').city,'');assert.equal(c.ctx.api.parseLocalDestination('臺北市信義區市府路1號').city,'臺北市');console.log('Passed night-market names are not cities, real administrative prefix preserved.');

const compound='臺北市大安區忠孝東路4段162、166號';
const cp=c.ctx.api.parseLocalDestination(compound);assert.equal(cp.number,'162、166號');assert.equal(cp.name,'');
assert.equal(c.ctx.api.geocodeCandidates(compound).some(q=>q==='162、166號'),false);
const otherRoad={lat:'25.028',lon:'121.554',name:'通化街162巷',display_name:'通化街162巷, 大安區, 臺北市',type:'residential',class:'highway',address:{road:'通化街162巷',suburb:'大安區',city:'臺北市'}};
const compoundWrong=await browser('?q='+encodeURIComponent(compound),[otherRoad]);assert.equal(compoundWrong.ctx.api.getTarget().lat,25.0477214);assert.equal(compoundWrong.ctx.api.getTarget().unresolved,true);
const compoundRoad={...otherRoad,name:'忠孝東路四段',display_name:'忠孝東路四段, 大安區, 臺北市',address:{...otherRoad.address,road:'忠孝東路四段'}};
const compoundNear=await browser('?q='+encodeURIComponent(compound),[compoundRoad]);assert.equal(compoundNear.ctx.api.getTarget().resolution.pendingConfirmation,true);assert.equal(compoundNear.ctx.api.getTarget().lat,25.0477214);
assert.equal(c.ctx.api.parseLocalDestination('臺北市南港區三重路19-2、19-3、19-4號').number,'19-2、19-3、19-4號');
console.log('Compound door lists retained as addresses; unrelated road rejected and road-only result requires confirmation.');

assert.equal(c.ctx.api.candidateMatches({kind:'address',parts:local},{...laneRow,address:{...laneRow.address,road:'基隆路四段43巷',house_number:'5'}}),false);console.log('Same house number in a different lane is rejected.');

const largeSite={...laneRow,name:'大型園區',class:'leisure',type:'park',osm_type:'relation',boundingbox:['25.010','25.016','121.536','121.542'],address:{...laneRow.address,house_number:'5'}};
const largeDoor=await browser('?q='+encodeURIComponent(shared),[largeSite]);assert.equal(largeDoor.ctx.api.getTarget().resolution.precision,'site-area');assert.equal(largeDoor.ctx.api.getTarget().resolution.pendingConfirmation,true);assert.equal(largeDoor.ctx.api.getTarget().lat,25.0477214);
const smallSite={...largeSite,boundingbox:['25.0119','25.0121','121.5389','121.5391']};const smallDoor=await browser('?q='+encodeURIComponent(shared),[smallSite]);assert.equal(smallDoor.ctx.api.getTarget().resolution.precision,'address');assert.equal(smallDoor.ctx.api.getTarget().lat,25.012);
console.log('Large-area door matches require confirmation; small building address behavior preserved.');

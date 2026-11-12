function parseMaps(input){
const s=input.trim();const coord=(a,b)=>{a=Number(a);b=Number(b);return Number.isFinite(a)&&Number.isFinite(b)&&a>=-90&&a<=90&&b>=-180&&b<=180?{lat:a,lon:b,name:'Google Maps 分享地點'}:null};
let direct=s.match(/^(-?\d+(?:\.\d+)?)\s*[,，]\s*(-?\d+(?:\.\d+)?)$/);if(direct)return coord(direct[1],direct[2])||{error:'經緯度超出範圍'};
let link=s.match(/https?:\/\/[^\s<>]+/i);if(!link)return {q:s};let u;try{u=new URL(link[0])}catch{return {error:'連結格式無效'}};
if(!isGoogleHost(u.hostname))return {error:'請貼上 Google Maps 連結或輸入地址'};
if(u.hostname==='maps.app.goo.gl'||u.hostname==='goo.gl')return {short:u.href};
let txt=u.href;try{txt=decodeURIComponent(txt)}catch{}
let geo=txt.match(/!3d(-?[\d.]+)!4d(-?[\d.]+)/);if(geo)return coord(geo[1],geo[2])||{error:'座標無效'};
for(let key of ['destination','query','q']){let q=u.searchParams.get(key);if(q){let xy=q.match(/^(-?[\d.]+),\s*(-?[\d.]+)$/);if(xy)return coord(xy[1],xy[2])||{error:'座標無效'};if(!/^place_id:/.test(q))return {q};}}
let place=txt.match(/\/maps\/(?:place|search)\/([^/?]+)/);if(place)return {q:place[1].replace(/\+/g,' ')};
return {error:'連結只有地圖視角或地點編號，無法確認目的地；請分享地點頁，或直接輸入地址'};
}
function isGoogleHost(h){return /^(?:(?:www|maps)\.)?google\.(?:com|com\.tw|co\.jp)$/.test(h)||h==='maps.app.goo.gl'||h==='goo.gl'}
import assert from 'node:assert/strict';
assert.equal(parseMaps('明星咖啡 https://maps.app.goo.gl/abc').short,'https://maps.app.goo.gl/abc');
assert.equal(parseMaps('https://www.google.com/maps/place/Cafe/@25.1,121.2,15z/data=!3d25.04!4d121.51').lat,25.04);
assert.equal(parseMaps('https://www.google.com/maps?q=25.04%2C121.51').lon,121.51);
assert.equal(parseMaps('https://www.google.com/maps/dir/?api=1&destination=台北車站').q,'台北車站');
assert.equal(parseMaps('https://www.google.com/maps/place/台北車站/@25,121,15z').q,'台北車站');
assert.ok(parseMaps('https://www.google.com/maps/@25,121,15z').error);
assert.ok(parseMaps('https://evil.example/').error);
console.log('7 Maps parsing checks passed');

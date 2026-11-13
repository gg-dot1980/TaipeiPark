import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
const dir=new URL('.',import.meta.url).pathname,manifest=JSON.parse(fs.readFileSync(dir+'manifest.json'));
const worker=(await import('./corrected-worker.js')).default;
const sql=(sql,params=[])=>{const r=spawnSync('python3',[dir+'sqlite.py'],{input:JSON.stringify({sql,params}),encoding:'utf8'});if(r.status)throw Error(r.stderr);return JSON.parse(r.stdout)};
const DB={prepare(query){return {bind(...params){const read=()=>sql(query,params);return {first:async()=>read()[0]||null,all:async()=>({results:read()}),run:async()=>{read();return {success:true}}}}}},async batch(items){return Promise.all(items.map(s=>s.run()))}};
const token='test-only-not-a-live-credential-123456789',env={DB,ADDRESS_IMPORT_TOKEN:token};let checks=[];
async function post(body,auth=true,e=env){return worker.fetch(new Request('https://test.local/internal/address-import',{method:'POST',headers:{'Content-Type':'application/json',...(auth?{'X-Address-Import-Token':token}:{})},body:JSON.stringify({snapshotId:manifest.snapshotId,...body})}),e)}
async function check(name,fn){await fn();checks.push(name);console.log('PASS',name)}
const verify={kind:'verify',readbackSha:manifest.indexSha256};
await check('Unauthenticated writes rejected',async()=>assert.equal((await post(verify,false)).status,403));
await check('Missing configured credential fails closed',async()=>assert.equal((await post(verify,true,{DB})).status,403));
await check('Metadata expected2 actual3 rejected',async()=>{sql('update address_snapshot set expected_references=2 where snapshot_id=?',[manifest.snapshotId]);assert.equal((await post(verify)).status,409)});
await check('Bad metadata cannot serve address',async()=>{sql("update address_snapshot set state='verified' where snapshot_id=?",[manifest.snapshotId]);assert.equal((await worker.fetch(new Request('https://test.local/api/address?q='+encodeURIComponent('臺北市北投區文林北路209號')),env)).status,503);sql("update address_snapshot set state='loading',expected_references=3 where snapshot_id=?",[manifest.snapshotId])});
await check('Bad readback hash rejected',async()=>assert.equal((await post({...verify,readbackSha:'invalid'})).status,400));
await check('Correct manifest/metadata/actual3 accepted',async()=>{assert.equal((await post(verify)).status,200);assert.equal(sql('select state from address_snapshot where snapshot_id=?',[manifest.snapshotId])[0].state,'verified')});
await check('Verified content immutable',async()=>assert.equal((await post({kind:'references',rows:[['北投區文林北路209號',250000000,1215000000,'{}']]})).status,409));
await check('Re-verification read-only idempotent',async()=>assert.equal((await (await post(verify)).json()).unchanged,true));
await check('Missing actual row rejected',async()=>{const row=sql('select * from address_conflict where snapshot_id=? limit 1',[manifest.snapshotId])[0];sql('delete from address_conflict where snapshot_id=? and address_key=?',[manifest.snapshotId,row.address_key]);assert.equal((await post(verify)).status,409);sql('insert into address_conflict values (?,?,?)',[manifest.snapshotId,row.address_key,row.districtless_key])});
await check('Reference query returns labeled source',async()=>{const r=await worker.fetch(new Request('https://test.local/api/address?q='+encodeURIComponent('臺北市北投區文林北路209號')),env);assert.equal(r.status,200);const j=await r.json();assert.equal(j.provider,'verified-address');assert.equal(j.precision,'address-reference')});
await check('Old snapshot preserved with original metadata',async()=>{const r=sql('select expected_references,state from address_snapshot where snapshot_id=?',[manifest.snapshotId.replace('-meta2','')])[0];assert.deepEqual(r,{expected_references:2,state:'verified'})});
fs.writeFileSync(dir+'test-result.json',JSON.stringify({checkedAt:new Date().toISOString(),scope:'Local actual SQLite + Worker handler; not cloud/browser',passed:checks.length,checks},null,2));

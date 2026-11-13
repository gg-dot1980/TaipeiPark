import assert from 'node:assert/strict';import fs from 'node:fs';
import worker from '../../wenlin-isolated-site/.sites-checkout/dist/server/index.js';
let calls=0;const env={DB:{prepare(){calls++;throw Error('No writes permitted')}}};let tests=[];
for(const method of ['POST','PUT','DELETE','PATCH']){const r=await worker.fetch(new Request('https://test.local/internal/address-import',{method,body:'{}'}),env);assert.equal(r.status,405);assert.equal(r.headers.get('Allow'),'GET');tests.push(method+' blocked')}
assert.equal(calls,0);tests.push('zero DB access for writes');
const r=await worker.fetch(new Request('https://test.local/internal/address-import?kind=status'),{});assert.equal(r.status,503);tests.push('GET reaches original read handler');
const page=await worker.fetch(new Request('https://test.local/'),{});assert.equal(page.status,200);tests.push('homepage unchanged accessible');
console.log(JSON.stringify({tests,passed:tests.length}));fs.writeFileSync(new URL('safety-test-result.json',import.meta.url),JSON.stringify({checkedAt:new Date().toISOString(),tests,passed:tests.length},null,2));

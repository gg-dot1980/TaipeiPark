import fs from 'node:fs';
import crypto from 'node:crypto';
const input=process.env.TAIPEIPARK_PRIVATE_PACK;
if(!input)throw Error('TAIPEIPARK_PRIVATE_PACK is required; no empty-data deployment is allowed');
const pack=JSON.parse(fs.readFileSync(input,'utf8'));
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const manifest=JSON.parse(fs.readFileSync('build-manifest.json','utf8'));
if(pack.parent!==manifest.parent)throw Error('Private pack version mismatch');
function hydrate(s){return s.replace(/\/\*PRIVATE:([A-Z0-9_]+)\*\//g,(_,k)=>{if(!(k in pack.parts))throw Error('Missing private component: '+k);return pack.parts[k]})}
const html=hydrate(fs.readFileSync('src/page.html.template','utf8'));
if(html!==JSON.parse(pack.htmlLiteral))throw Error('HTML reconstruction mismatch');
const template=fs.readFileSync('src/worker.js.template','utf8');
const worker=hydrate(template.replace('/*PRIVATE:HTML*/',()=>pack.htmlLiteral));
if(hash(worker)!==manifest.workerSha256)throw Error('Worker reconstruction mismatch; review changes before updating release manifest');
fs.mkdirSync('dist/.openai',{recursive:true});
if(fs.existsSync('.openai/hosting.json'))fs.copyFileSync('.openai/hosting.json','dist/.openai/hosting.json');
if(fs.existsSync('drizzle'))fs.cpSync('drizzle','dist/.openai/drizzle',{recursive:true});
fs.mkdirSync('dist/server',{recursive:true});fs.writeFileSync('dist/server/index.js',worker);
console.log(JSON.stringify({parent:pack.parent,workerSha256:hash(worker),exactReconstruction:true}));

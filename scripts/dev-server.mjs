// Local Node adapter for the same dependency-free Worker. Sites preview owns this process.
import http from 'node:http';
import worker from '../worker/index.js';
const server=http.createServer(async(req,res)=>{try{const request=new Request('http://localhost'+req.url,{method:req.method});const result=await worker.fetch(request,{});res.writeHead(result.status,Object.fromEntries(result.headers));res.end(Buffer.from(await result.arrayBuffer()));}catch(error){res.writeHead(500);res.end('Preview request failed');console.error(error);}});
const args=process.argv.slice(2),opt=(key,fallback)=>{const i=args.indexOf(key);return i>=0?args[i+1]:fallback};
server.listen(Number(opt('--port',process.env.PORT||3000)),opt('--host','127.0.0.1'));


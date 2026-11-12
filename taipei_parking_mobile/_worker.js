// Cloudflare Pages advanced mode: proxy officially published open XML sources.
// Install with index.html on Cloudflare Pages; no API key required for official XML.
const SOURCES = Object.freeze({
  '/api/park-static': 'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.xml',
  '/api/park-live': 'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.xml',
  '/api/road-segments': 'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_roadquery.xml'
});
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const upstream = SOURCES[url.pathname];
    if (!upstream) return env.ASSETS.fetch(request);
    if (request.method !== 'GET') return new Response('Method not allowed', {status:405});
    try {
      const response = await fetch(upstream, {cf:{cacheTtl:url.pathname==='/api/park-static'?3600:60, cacheEverything:true}});
      if (!response.ok) return new Response('Official feed unavailable', {status:502});
      return new Response(response.body, {headers:{
        'Content-Type': 'application/xml; charset=utf-8',
        'Cache-Control': url.pathname==='/api/park-static'?'public, max-age=3600':'public, max-age=60',
        'X-Data-Source': 'Taipei City open data',
        'X-Content-Type-Options':'nosniff'
      }});
    } catch(e) {return new Response('Official feed unavailable', {status:502});}
  }
};

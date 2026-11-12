"""Usage: python scripts/prepare-road-fees.py <Taiwan OSM PBF>; no online geocoding."""
import json,re,sys,osmium,zipfile,xml.etree.ElementTree as E,collections,heapq,hashlib,datetime
from pathlib import Path
from shapely.geometry import Point,LineString
from pyproj import Transformer
P=Path('data/road-fees');raw=(P/'source.ods').read_bytes();ns={'t':'urn:oasis:names:tc:opendocument:xmlns:table:1.0'}
root=E.fromstring(zipfile.ZipFile(P/'source.ods').read('content.xml'));rows=[]
for row in root.findall('.//t:table-row',ns)[1:]:
 cells=[]
 for c in row:
  if c.tag.endswith('table-cell'):cells+=[' '.join(c.itertext()).strip()]*min(20,int(c.get('{'+ns['t']+'}number-columns-repeated','1')))
 if len(cells)>=10 and (cells[2] or cells[4]):rows.append({'road':cells[0],'scope':cells[1],'count':cells[2] or cells[4],'mode':'hour' if cells[2] else 'entry','time':cells[7],'rate':cells[8],'days':cells[9]})
def norm(s):
 s=s.replace('臺','台').replace('舘','館');s=re.sub(r'([一二三四五六七八九])段',lambda m:str('一二三四五六七八九'.index(m[1])+1)+'段',s)
 return re.sub(r'\s+','',s)
tr=Transformer.from_crs(4326,3826,always_xy=True);ways=collections.defaultdict(list);coords={}
class Roads(osmium.SimpleHandler):
 def way(self,w):
  if not w.tags.get('highway') or not w.tags.get('name'):return
  try:
   nd=[(n.ref,n.lon,n.lat) for n in w.nodes];
   if not nd or not all(24.95<lat<25.22 and 121.44<lon<121.68 for _,lon,lat in nd):return
   ways[norm(w.tags['name'])].append([n[0] for n in nd])
   for ref,lon,lat in nd:coords[ref]=tr.transform(lon,lat)
  except osmium.InvalidLocationError:pass
Roads().apply_file(sys.argv[1],locations=True,idx='flex_mem')
nodeSets={k:{n for way in v for n in way} for k,v in ways.items()};geoms={};reject=collections.Counter()
for i,r in enumerate(rows):
 road=norm(r['road']);ends=re.split('[-~～至]',r['scope']);nodes=nodeSets.get(road,set())
 if len(ends)!=2 or not nodes:reject['missing-road-or-scope']+=1;continue
 a=nodes & nodeSets.get(norm(ends[0]),set());b=nodes & nodeSets.get(norm(ends[1]),set())
 if not a or not b or a&b:reject['missing-or-overlapping-intersections']+=1;continue
 graph=collections.defaultdict(list)
 for way in ways[road]:
  for u,v in zip(way,way[1:]):
   d=Point(coords[u]).distance(Point(coords[v]));graph[u].append((v,d));graph[v].append((u,d))
 # Each connected carriageway is considered separately. One closest endpoint path per source intersection.
 paths=[]
 for start in a:
  heap=[(0,start)];ds={start:0};prev={};end=None
  while heap:
   d,u=heapq.heappop(heap)
   if d!=ds[u]:continue
   if u in b:end=u;break
   if d>4000:continue
   for v,cost in graph[u]:
    nd=d+cost
    if nd<ds.get(v,float('inf')):ds[v]=nd;prev[v]=u;heapq.heappush(heap,(nd,v))
  if end is None:continue
  ids=[end]
  while ids[-1]!=start:ids.append(prev[ids[-1]])
  line=LineString([coords[n] for n in ids]);
  if 50<line.length<4000:paths.append(line)
 if paths:geoms[i]=paths
 else:reject['no-confirmed-road-path']+=1
roadrows=collections.defaultdict(list)
for i in geoms:roadrows[norm(rows[i]['road'])].append(i)
allroadrows=collections.defaultdict(list)
for i,r in enumerate(rows):allroadrows[norm(r['road'])].append(i)
index=json.load(open('data/road-index.json'));bindings={};conflict=0
for r in index:
 if r[2] not in ['01','03']:continue
 name=norm(re.sub('[A-Z]$','',r[3]));point=Point(tr.transform(r[1],r[0]));matched=[]
 for i in roadrows.get(name,[]):
  if any(line.distance(point)<=18 and line.interpolate(0).distance(point)>25 and line.interpolate(line.length).distance(point)>25 for line in geoms[i]):matched.append(i)
 # Retain all intersecting source rows, even unsupported ones: runtime rejects differing rules.
 if matched:
  signatures={(rows[i]['mode'],rows[i]['time'],rows[i]['rate'],rows[i]['days']) for i in matched}
  unresolved=[i for i in allroadrows[name] if i not in geoms and (rows[i]['mode'],rows[i]['time'],rows[i]['rate'],rows[i]['days']) not in signatures]
  if len(signatures)==1 and not unresolved:bindings[r[7]]={'lat':r[0],'lon':r[1],'rows':matched}
  else:conflict+=1
meta={'source':'https://data.taipei/dataset/detail?id=99392a71-4e8a-42e1-b605-20dfa7bb5f8c','download':'https://data.taipei/api/frontstage/tpeod/dataset/resource.download?rid=86d2a8b6-c360-4349-956d-dd7771cccf91','fileUpdated':'2026-03-27 16:39:04','metadataUpdated':'2026-10-06 10:34:07','retrievedAt':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'osmSnapshot':'2026-10-26','carRows':len(rows),'scopedRows':len(geoms),'boundSpaces':len(bindings),'conflictingSpaces':conflict,'rejectedScopes':dict(reject),'method':'同道路名稱＋OSM道路交會點起訖路徑；車格距道路18m內、離起訖25m以上；衝突不套價。路邊圖資2026-10-02；非現地驗證。'}
(P/'scope-paths.json').write_text(json.dumps({i:[list(p.coords) for p in paths] for i,paths in geoms.items()},separators=(',',':')))
(P/'index.json').write_text(json.dumps({'meta':meta,'rows':rows,'bindings':bindings},ensure_ascii=False,separators=(',',':')));print(json.dumps(meta,ensure_ascii=False))

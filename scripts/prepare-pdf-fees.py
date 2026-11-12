"""Re-use previously checked OSM scope paths only for identical road + endpoint names.
New PDF rows are the active tariff reference. Unmatched/ambiguous rules never fall back to old ODS prices.
Usage: python scripts/prepare-pdf-fees.py <shp-dir>
"""
from pathlib import Path
import json,re,collections,datetime,sys,unicodedata
import shapefile
from shapely.geometry import Point,LineString
from pyproj import Transformer
p=Path('data/road-fees');old=json.loads((p/'ods-index-2026-03-27.json').read_text());paths=json.loads((p/'ods-scope-paths.json').read_text());pdf=json.loads((p/'pdf-2026-10-13/rows.json').read_text())
def norm(s):
 s=unicodedata.normalize('NFKC',s).replace('臺','台').replace('舘','館');s=re.sub(r'([一二三四五六七八九])段',lambda m:str('一二三四五六七八九'.index(m[1])+1)+'段',s)
 return re.sub(r'\s+','',s)
def key(r):return norm(r['road']),norm(r['scope'])
def sig(r):return (r['mode'],r['time'],r['rate'],r['days'])
known=collections.defaultdict(list)
for i,v in paths.items(): known[key(old['rows'][int(i)])].extend(v)
rows=[{k:r[k] for k in ['district','road','scope','time','rate','days','mode','sourceFile','sourcePage','feeType']} for r in pdf['rows']]
geoms={i:[LineString(p) for p in known[key(r)]] for i,r in enumerate(rows) if key(r) in known}
allroad=collections.defaultdict(list)
for i,r in enumerate(rows):allroad[norm(r['road'])].append(i)
idx=json.load(open('data/road-index.json'));district={};reader=shapefile.Reader(str(next(Path(sys.argv[1]).glob('*.shp'))),encoding='utf-8')
for x in reader.iterRecords(fields=['keyid','area_name']):district[str(x['keyid'])]=x['area_name']
tr=Transformer.from_crs(4326,3826,always_xy=True);bindings={};gaps=collections.Counter();boundtypes=collections.Counter()
for r in idx:
 if r[2] not in ['01','03']:continue
 name=norm(re.sub('[A-Z]$','',r[3]));allrows=[i for i in allroad.get(name,[]) if rows[i]['district']==district.get(r[7])]
 if not allrows:gaps['no_exact_road_and_district']+=1;continue
 point=Point(tr.transform(r[1],r[0]));matched=[]
 for i in allrows:
  if i in geoms and any(l.distance(point)<=18 and l.interpolate(0).distance(point)>25 and l.interpolate(l.length).distance(point)>25 for l in geoms[i]):matched.append(i)
 if not matched:gaps['outside_verified_scope_or_no_geometry']+=1;continue
 signatures={sig(rows[i]) for i in matched}
 unresolved=[i for i in allrows if i not in geoms and sig(rows[i]) not in signatures]
 if len(signatures)!=1 or unresolved:gaps['conflicting_or_unresolved_scope']+=1;continue
 bindings[r[7]]={'lat':r[0],'lon':r[1],'rows':matched};boundtypes[r[2]]+=1
meta={'source':'https://pma.gov.taipei/cp.aspx?n=B68496752E5DD5EE','fileUpdated':None,'pdfGeneratedAt':'2026-10-13','effectiveDate':None,'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':pdf['meta']['sources'],'osmSnapshot':old['meta']['osmSnapshot'],'geometrySnapshot':'2026-10-02','carRows':len(rows),'scopedRows':len(geoms),'boundSpaces':len(bindings),'boundTypes':dict(boundtypes),'unboundReasons':dict(gaps),'method':'最新版官方PDF逐列擷取；行政區＋道路＋起訖完全一致才沿用既有OSM路徑；距道路18m內、離端點25m以上；同路段衝突或異價未定位範圍不套價。日期是PDF產製日期，不是生效日期。未找到新PDF規則時不回退舊ODS價格。'}
(p/'scope-paths.json').write_text(json.dumps({i:[list(x.coords) for x in v] for i,v in geoms.items()},separators=(',',':')))
(p/'index.json').write_text(json.dumps({'meta':meta,'rows':rows,'bindings':bindings},ensure_ascii=False,separators=(',',':')))
print(json.dumps(meta,ensure_ascii=False,indent=2))

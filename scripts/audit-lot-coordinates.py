"""Audit downloaded official lot XML and generate independent PROJ reference coordinates.
Usage: PYTHONPATH=/tmp/taipeipark-deps python scripts/audit-lot-coordinates.py <source-dir>
Requires pyproj. Does not fetch data or silently update snapshot times.
"""
from pathlib import Path
import collections,datetime,gzip,hashlib,json,re,sys,xml.etree.ElementTree as E
from pyproj import Transformer
folder=Path(sys.argv[1]);basic=(folder/'TCMSV_alldesc.xml').read_bytes();livebytes=(folder/'TCMSV_allavailable.xml').read_bytes()
b=E.fromstring(basic);l=E.fromstring(livebytes);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
normalize=lambda s:re.sub('[^a-z0-9]','',s.lower())
def fields(row):
 d={}
 for z in row.iter():
  if not len(z):d.setdefault(normalize(z.tag),(z.text or '').strip())
 return d
def num(v):
 try:return float(v)
 except (TypeError,ValueError):return float('nan')
def valid(lat,lon):return 20<lat<27 and 119<lon<123
def oldcoords(d):
 for x,y in [('latitude','longitude'),('xcod','ycod'),('ycod','xcod')]:
  lat,lon=num(d.get(x)),num(d.get(y))
  if valid(lat,lon):return {'lat':lat,'lon':lon}
 return None
transform=Transformer.from_crs(3826,4326,always_xy=True)
rows=[fields(x) for x in b.findall('PARK')];liverows={fields(x)['id']:fields(x) for x in l.findall('PARK')};counts=collections.Counter();fixtures=[];restored=[];rejected=[]
keep=['id','name','latitude','longitude','xcod','ycod','tw97x','tw97y','totalcar','handicapfirst','pregnancyfirst','chargingstation','accessibilityelevator','childpickuparea','handicapdiscount','payex','servicetime','address']
for d in rows:
 old=oldcoords(d);x,y=num(d.get('tw97x')),num(d.get('tw97y'));projected=None
 if 100000<=x<=400000 and 2400000<=y<=3000000:
  lon,lat=transform.transform(x,y)
  if valid(lat,lon):projected={'lat':lat,'lon':lon}
 point=old or projected;car=num(d.get('totalcar'))>0;available=liverows.get(d['id']);v=num((available or {}).get('availablecar'))
 counts['allRecords']+=1;counts['legacyLocated']+=bool(old);counts['locatedAfter']+=bool(point);counts['projectedFallback']+=bool(point and not old)
 if car:
  counts['passengerCarLots']+=1;counts['passengerCarLocatedBefore']+=bool(old);counts['passengerCarLocatedAfter']+=bool(point)
  if point and not old:
   counts['passengerCarRestored']+=1;counts['restoredWithLiveRecord']+=available is not None;counts['restoredWithNonnegativeCarValue']+=v>=0;counts['restoredWithPositiveCarValue']+=v>0
   restored.append({'id':d['id'],'name':d['name'],'lat':point['lat'],'lon':point['lon'],'liveRecord':available is not None,'availability':v if v>=0 else None})
 if not point:rejected.append({'id':d['id'],'name':d['name'],'TW97X':d.get('tw97x'),'TW97Y':d.get('tw97y')})
 fixtures.append({'fields':{k:d[k] for k in keep if k in d},'legacy':old,'projectedReference':projected,'expected':point})
sha=lambda s:hashlib.sha256(s).hexdigest()
report={'checkedAt':now,'inventorySourceTime':b.findtext('UPDATETIME'),'availabilitySourceTime':l.findtext('UPDATETIME'),'source':'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.xml','liveSource':'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.xml','crs':'TWD97 / TM2 zone 121 (EPSG:3826) -> WGS84 (EPSG:4326)','referenceImplementation':'pyproj/PROJ Transformer.from_crs(3826,4326,always_xy=True)','counts':dict(counts),'rejected':rejected,'restored':restored,'notes':['保留有效官方WGS84入口；缺時才使用TW97X/TW97Y轉換場址，場址不保證為出入口。','餘位數僅是本次來源快照的場數；正式站每次查詢仍核對10分鐘新鮮度、車種及非負數，不作空位保證。'],'sha256':{'inventory':sha(basic),'availability':sha(livebytes)}}
Path('data/lot-coordinate-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
Path('data/lot-coordinates-fixture.json').write_text(json.dumps(fixtures,ensure_ascii=False,separators=(',',':')))
Path('data/lot-availability-fixture.json').write_text(json.dumps({'updatetime':l.findtext('UPDATETIME'),'rows':[{k:v for k,v in x.items() if k in ['id','availablecar','availablehandicap','updatetime']} for x in liverows.values()]},ensure_ascii=False,separators=(',',':')))
a=json.loads(Path('data/source-audit.json').read_text());a['checkedAt']=now
lot=a['lots'];basicids={x['id'] for x in rows};liveids=set(liverows)
lot.update({'checkedAt':now,'inventorySourceTime':b.findtext('UPDATETIME'),'availabilitySourceTime':l.findtext('UPDATETIME'),'inventoryRecords':len(rows),'passengerCarLots':sum(num(x.get('totalcar'))>0 for x in rows),'accessibleLots':sum(num(x.get('handicapfirst'))>0 for x in rows),'inventoryWithFeeText':sum(bool(x.get('payex')) for x in rows),'liveRecords':len(liverows),'matchedLiveIds':len(liveids&basicids),'inventoryWithoutLiveRecord':len(basicids-liveids),'liveWithoutInventory':len(liveids-basicids),'nonnegativeCarAvailability':sum(num(x.get('availablecar'))>=0 for x in liverows.values()),'nonnegativeAccessibleAvailability':sum(num(x.get('availablehandicap'))>=0 for x in liverows.values()),'sha256':report['sha256'],'coordinates':{k:v for k,v in report.items() if k not in ['restored','sha256']},'specialUse':{k:{'lotsWithPositiveField':sum(num(x.get(k))>0 for x in rows),'sumRawField':sum(num(x.get(k)) for x in rows if num(x.get(k))>0)} for k in ['handicapfirst','pregnancyfirst','chargingstation','accessibilityelevator','childpickuparea']}})
Path('data/source-audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2))
for name,raw in [('TCMSV_alldesc.xml',basic),('TCMSV_allavailable.xml',livebytes)]:Path('data/source-snapshots/'+name+'.gz').write_bytes(gzip.compress(raw,mtime=0))
print(json.dumps({k:v for k,v in report.items() if k not in ['restored']},ensure_ascii=False,indent=2))

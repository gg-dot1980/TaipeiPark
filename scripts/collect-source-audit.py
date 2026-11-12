"""Read downloaded official sources; never infer per-space occupancy.
Usage: python scripts/collect-source-audit.py <source-dir> <shp-dir>
Requires pyshp. Source files are downloaded separately and are not silently refreshed.
"""
from pathlib import Path
import collections, datetime, hashlib, json, re, sys, unicodedata, xml.etree.ElementTree as E
import shapefile
sources, shpdir = map(Path,sys.argv[1:3])
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(name): return E.parse(sources/name).getroot()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def number(s):
 try:return float(s)
 except (ValueError,TypeError):return None
def norm(s):
 s=unicodedata.normalize('NFKC',s or '').replace('臺','台').replace('舘','館')
 s=re.sub(r'([一二三四五六七八九])段',lambda m:str('一二三四五六七八九'.index(m[1])+1)+'段',s)
 return re.sub(r'\s+','',s)
idx=json.loads(Path('data/road-index.json').read_text());byid={r[7]:r for r in idx}
quality=json.loads(Path('data/road-quality.json').read_text())
shp=next(shpdir.glob('*.shp'))
assert sha(shp)==quality['source_geometry_sha256'], 'SHP changed: rebuild and review road index before auditing.'
reader=shapefile.Reader(str(shp),encoding='utf-8')
keyrows=collections.defaultdict(list);districts=collections.defaultdict(collections.Counter);attrs={}
for rec in reader.iterRecords(fields=['keyid','rdcode','pkid','area_name','pkdel']):
 d=rec.as_dict();id=str(d['keyid'])
 if not d['pkdel'] and d['rdcode'] and d['pkid']:keyrows[(d['rdcode'],d['pkid'])].append(id)
 if id not in byid:continue
 attrs[id]=d;districts[d['area_name'] or '未提供'][byid[id][2]]+=1
roads=read('TCMSV_roadquery.xml');cells=[c for r in roads for c in r.findall('./cellStatusList/cell')]
feedkeys=collections.Counter((r.findtext('roadSegID'),c.findtext('psId')) for r in roads for c in r.findall('./cellStatusList/cell'))
linked={};references=[];rejected=collections.Counter()
for road in roads:
 rid=road.findtext('roadSegID');name=road.findtext('roadSegName') or '';ref=len(references)
 references.append({'roadSegID':rid,'roadName':name,'vehicleCode':road.findtext('roadSegCarType'),'feeText':road.findtext('roadSegFee') or '', 'chargeStart':road.findtext('roadSegtimeStart'),'chargeEnd':road.findtext('roadSegtimeEnd'),'sourceUpdated':road.findtext('roadSegUpdatetime')})
 for cell in road.findall('./cellStatusList/cell'):
  key=(rid,cell.findtext('psId'));matches=keyrows.get(key,[])
  if not key[0] or not key[1]:rejected['missing_identifiers']+=1;continue
  if feedkeys[key]!=1:rejected['duplicate_feed_key']+=1;continue
  if len(matches)!=1:rejected['ambiguous_geometry_key' if matches else 'no_accepted_geometry_key']+=1;continue
  id=matches[0]
  if id not in byid:rejected['geometry_not_accepted']+=1;continue
  space=byid[id]
  if norm(space[3])!=norm(name):rejected['road_name_mismatch']+=1;continue
  if not references[ref]['feeText']:rejected['missing_fee_text']+=1;continue
  # A matching key links reference text, NOT occupancy or a complete tariff rule.
  linked[id]={'lat':space[0],'lon':space[1],'road':ref,'spaceID':key[1]}
nonzero=[c for c in cells if (number(c.findtext('coord_X')) or 0)!=0 and (number(c.findtext('coord_Y')) or 0)!=0]
Path('data/road-identifiers.json').write_text(json.dumps({'accepted':{id:[d['rdcode'],d['pkid'],d['area_name']] for id,d in attrs.items()},'duplicateKeys':[[*k,len(v)] for k,v in keyrows.items() if len(v)>1]},ensure_ascii=False,separators=(',',':')))
meta={'source':'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_roadquery.xml','dataset':'https://data.taipei/dataset/detail?id=434638ca-8770-42c1-940d-0386a74f6eb9','checkedAt':now,'sha256':sha(sources/'TCMSV_roadquery.xml'),'roadSegments':len(roads),'cells':len(cells),'nonzeroCoordinateCells':len(nonzero),'nonzeroWithTimestamp':sum(bool(c.findtext('data_Dt')) for c in nonzero),'linkedSpaces':len(linked),'rejectedCells':dict(rejected),'method':'SHP rdcode＋pkid 與 XML roadSegID＋psId 一對一一致，並核對完整道路名稱（只正規化字形、空白、段數字）；座標仍採 SHP。未驗證即時狀態代碼；不提供逐格空位。','limitations':'XML 未完整提供收費日與計時／計次單位；費率及時段僅為原文參考，不由此資料推定時薪、免費、合法停放或空位。'}
Path('data/road-source-links.json').write_text(json.dumps({'meta':meta,'roads':references,'links':linked},ensure_ascii=False,separators=(',',':')))
basic=read('TCMSV_alldesc.xml');live=read('TCMSV_allavailable.xml');lots=basic.findall('PARK');available=live.findall('PARK');liveids={x.findtext('ID') for x in available};basicids={x.findtext('ID') for x in lots}
car=[x for x in lots if (number(x.findtext('TOTALCAR')) or 0)>0];accessible=[x for x in lots if (number(x.findtext('Handicap_First')) or 0)>0]
valid=lambda x,t: number(x.findtext(t)) is not None and number(x.findtext(t))>=0
lot={'source':'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.xml','liveSource':'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.xml','checkedAt':now,'inventorySourceTime':basic.findtext('UPDATETIME'),'availabilitySourceTime':live.findtext('UPDATETIME'),'inventoryRecords':len(lots),'passengerCarLots':len(car),'accessibleLots':len(accessible),'inventoryWithFeeText':sum(bool((x.findtext('PAYEX') or '').strip()) for x in lots),'liveRecords':len(available),'matchedLiveIds':len(liveids&basicids),'inventoryWithoutLiveRecord':len(basicids-liveids),'liveWithoutInventory':len(liveids-basicids),'nonnegativeCarAvailability':sum(valid(x,'AVAILABLECAR') for x in available),'nonnegativeAccessibleAvailability':sum(valid(x,'AVAILABLEHANDICAP') for x in available),'sha256':{'inventory':sha(sources/'TCMSV_alldesc.xml'),'availability':sha(sources/'TCMSV_allavailable.xml')},'note':'數字為此次來源檔稽核，不是現在空位數；有效餘位仍以頁面當次讀取且10分鐘內的時間戳判定。'}
fees=json.loads(Path('data/road-fees/index.json').read_text());ods=json.loads(Path('data/road-fees/ods-index-2026-03-27.json').read_text());bound=set(fees['bindings']);linked_ids=set(linked);carids={r[7] for r in idx if r[2]=='01'}
audit={'schemaVersion':1,'checkedAt':now,'roadGeometry':{**quality,'lastVerifiedAt':now,'sourceResourceUpdated':'2026-10-06 10:25:50 +08:00','sameGeometryAsPriorVersion':True,'download':'https://data.taipei/api/frontstage/tpeod/dataset/resource.download?rid=7e2f32a0-9201-4666-a0ed-11034e6c2b66'},'lots':lot,'roadReference':meta,'fees':{'activeSource':fees['meta'],'odsSource':ods['meta'],'odsDownloadedSha256':sha(sources/'source.ods'),'sameOdsAsPriorVersion':sha(sources/'source.ods')==ods['meta']['sha256'],'passengerCarSpaces':len(carids),'geometryBoundCarSpaces':len(bound&carids),'referenceLinkedCarSpaces':len(linked_ids&carids),'carSpacesWithEitherReference':len((bound|linked_ids)&carids),'carSpacesWithoutEitherReference':len(carids-(bound|linked_ids))},'districts':[{'district':k,'accepted':sum(v.values()),'passengerCar':v['01'],'accessible':v['03'],'freight':v['07'],'otherSupported':sum(n for t,n in v.items() if t not in ['01','03','07']), 'feeRuleBound':sum(id in bound for id,d in attrs.items() if (d['area_name'] or '未提供')==k), 'officialReferenceLinked':sum(id in linked for id,d in attrs.items() if (d['area_name'] or '未提供')==k)} for k,v in sorted(districts.items())]}
Path('data/source-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
quality['last_verified_at']=now;quality['source_resource_updated']='2026-10-06 10:25:50 +08:00';quality['dynamic_audit']={'source_url':meta['source'],'checked_at':now,'road_segments':len(roads),'cells':len(cells),'nonzero_coordinate_cells':len(nonzero),'verified_per_space_matches':0,'status_code_mapping_verified':False,'identifier_reference_links':len(linked)}
Path('data/road-quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2))
print(json.dumps({'roadReference':meta,'lots':lot,'fees':audit['fees'],'districts':audit['districts']},ensure_ascii=False,indent=2))

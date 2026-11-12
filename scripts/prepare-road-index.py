from pathlib import Path
import shapefile,json,pyproj,sys,collections,hashlib
root=Path(sys.argv[1]);source=next(root.glob('*.shp'));r=shapefile.Reader(str(source),encoding='utf-8');tr=pyproj.Transformer.from_crs(3826,4326,always_xy=True);inverse=pyproj.Transformer.from_crs(4326,3826,always_xy=True);out=[];quarantine=[];raw=collections.Counter();accepted=collections.Counter();reasons=collections.Counter();positions=set();keyids=set();deleted=0;unsupported=0;maxerr=0
expected={'01':'car','03':'accessible','07':'freight','09':'limited','10':'timed','15':'bay','22':'shared','23':'busshared'}
def label_type(t):
 if not t:return None
 if '身' in t or '殘' in t or t=='殘汽':return 'motoraccessible' if '機' in t else 'accessible'
 if '貨' in t or '裝卸' in t:return 'freight'
 if '彈性' in t or '汽機車' in t:return 'shared'
 if '禁停' in t or t=='時段停車':return 'timed'
 if '限時' in t:return 'limited'
 if '大客' in t and '小' in t:return 'busshared'
 if '停車彎' in t:return 'motor' if '機' in t else 'bay'
 if t in ['小型車','小汽車','小行車']:return 'car'
 if '機' in t:return 'motor'
 return 'other'
fields=['pktype','pktype1','pkid','pkroad','roadname','pktime','pkterm','pkdel','keyid']
for rec in r.iterRecords(fields=fields):
 d=rec.as_dict();t=d['pktype'];raw[t]+=1
 if d['pkdel']:deleted+=1;continue
 if t not in expected:unsupported+=1;continue
 shape=r.shape(rec.oid);bb=shape.bbox;x=(bb[0]+bb[2])/2;y=(bb[1]+bb[3])/2;lon,lat=tr.transform(x,y);rx,ry=inverse.transform(lon,lat);maxerr=max(maxerr,abs(rx-x),abs(ry-y));road=d['pkroad'] or d['roadname'];label=d['pktype1'].strip();reason=[]
 if not (24.95<lat<25.22 and 121.44<lon<121.68):reason.append('座標超出臺北市檢查範圍')
 if shape.shapeType!=5 or bb[2]-bb[0]>30 or bb[3]-bb[1]>30:reason.append('車格幾何異常')
 if label_type(label) not in [None,expected[t]]:reason.append('車種代碼與中文分類不一致')
 if '停車場' in road:reason.append('名稱含停車場，路邊屬性待核對')
 position=(round(lat,7),round(lon,7),t);key=str(d['keyid'])
 if key in keyids or position in positions:reason.append('重複識別碼或位置')
 keyids.add(key);positions.add(position)
 if reason:
  quarantine.append({'id':key,'lat':round(lat,7),'lon':round(lon,7),'code':t,'label':label,'road':road,'reason':reason});reasons.update(reason);continue
 out.append([round(lat,7),round(lon,7),t,road,d['pkid'],d['pktime'],d['pkterm'],key,label]);accepted[t]+=1
quality={'checked_date':'2026-10-27','source_snapshot':'2026-10-02','source_url':'https://data.taipei/dataset/detail?id=5a911ea5-1694-4301-808e-e1780d971611','raw_records':sum(raw.values()),'raw_types':dict(raw),'deleted':deleted,'unsupported':unsupported,'accepted':len(out),'accepted_types':dict(accepted),'quarantined':len(quarantine),'quarantine_reasons':dict(reasons),'max_roundtrip_error_m':maxerr,'scope':'全量檔案一致性及轉換檢查，非現地驗證；空白中文分類依官方車種代碼處理；未完成逐格即時配對'}
Path('data/road-index.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')));Path('data/road-quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2));Path('data/road-quarantine.json').write_text(json.dumps(quarantine,ensure_ascii=False,separators=(',',':')));print(json.dumps(quality,ensure_ascii=False))

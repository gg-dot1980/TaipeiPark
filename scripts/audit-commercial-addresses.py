"""Conservative screen against official curb geometry; no coordinate correction.
A distance over 1 km is a review trigger, not proof that the CSV is wrong.
"""
import json, math, re, hashlib
from pathlib import Path
p=Path('data/commercial-stops.json');j=json.loads(p.read_text());raw=Path('data/road-index.json').read_bytes();roads=json.loads(raw)
by={}
for r in roads:by.setdefault(re.sub('[A-Z]$','',r[3]),[]).append(r)
review=[]
for x in j['accepted'][:]:
 m=re.match(r'(.+?[路街](?:[一二三四五六七八九0-9]+段)?)',x['address']);pts=by.get(m[1],[]) if m else []
 if not pts:continue
 distance=min(math.hypot((r[0]-x['lat'])*111320,(r[1]-x['lon'])*100900) for r in pts)
 if distance<=1000:continue
 x['coordinateQuality']='address-road-distance-review';x['quarantineReason']=f'公告座標距同名官方路邊車格最近約 {round(distance)} 公尺，地址與位置待核對；車格不是完整道路幾何，不能據此修正座標。'
 x['addressAudit']={'road':m[1],'nearestOfficialCurbMeters':round(distance),'referencePoints':len(pts)}
 j['accepted'].remove(x);j['quarantined'].append(x);review.append(x)
j['meta'].update(acceptedRecords=len(j['accepted']),acceptedSpaces=sum(x['spaces'] for x in j['accepted']),quarantinedRecords=len(j['quarantined']),quarantinedSpaces=sum(x['spaces'] for x in j['quarantined']))
j['meta']['addressAudit']={'method':'地址主路名（保留段數）對官方車格路名，僅移除車格路名尾端 A-Z 分段碼；最近距離超過1公里先隔離。不是逐點驗證，巷弄或道路未設格可能誤報；不猜座標。','geometrySha256':hashlib.sha256(raw).hexdigest(),'reviewRows':[x['sourceRow'] for x in j['quarantined'] if x.get('addressAudit')]}
p.write_text(json.dumps(j,ensure_ascii=False,indent=2));print(json.dumps(j['meta']['addressAudit'],ensure_ascii=False))

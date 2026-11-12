"""Extend reference TEXT only when unique official IDs match and the sole road
name difference is a trailing geometry section letter. Never bind a tariff or vacancy.
"""
import json,gzip,collections,re,unicodedata,xml.etree.ElementTree as E
from pathlib import Path
p=Path('data/road-source-links.json');j=json.loads(p.read_text());ids=json.load(open('data/road-identifiers.json'));idx={r[7]:r for r in json.load(open('data/road-index.json'))}; by=collections.defaultdict(list)
for k,v in ids['accepted'].items():by[tuple(v[:2])].append(k)
dupes={tuple(v[:2]) for v in ids['duplicateKeys']}
x=E.fromstring(gzip.decompress(Path('data/source-snapshots/TCMSV_roadquery.xml.gz').read_bytes())); counts=collections.Counter((r.findtext('roadSegID'),c.findtext('psId')) for r in x for c in r.findall('./cellStatusList/cell'))
def norm(s):return re.sub(r'([一二三四五六七八九])段',lambda m:str('一二三四五六七八九'.index(m[1])+1)+'段',re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('臺','台').replace('舘','館')))
added=0
for ri,r in enumerate(x):
 for c in r.findall('./cellStatusList/cell'):
  key=(r.findtext('roadSegID'),c.findtext('psId'));matched=by[key]
  if counts[key]!=1 or key in dupes or len(matched)!=1:continue
  id=matched[0];sp=idx[id]
  if id in j['links'] or not j['roads'][ri]['feeText']:continue
  original=norm(sp[3]);official=norm(r.findtext('roadSegName') or '')
  if not re.search(r'[A-Z]$',original) or original[:-1]!=official:continue
  j['links'][id]={'lat':sp[0],'lon':sp[1],'road':ri,'spaceID':key[1],'matchMethod':'unique-official-ids-road-section-suffix','geometryRoadName':sp[3]};added+=1
j['meta']['linkedSpaces']=len(j['links']);j['meta']['rejectedCells']['road_name_mismatch']-=added
j['meta']['sectionSuffixReferences']=sum(v.get('matchMethod')=='unique-official-ids-road-section-suffix' for v in j['links'].values())
j['meta']['method']+='；額外原文參考允許 SHP 路名尾端單一 A-Z 分段碼差異，仍須唯一官方路段ID＋格號一致，不推定時薪、適用範圍或空位。' if added else ''
p.write_text(json.dumps(j,ensure_ascii=False,separators=(',',':')))
p=Path('data/source-audit.json');a=json.loads(p.read_text());a['roadReference']=j['meta'];bound=set(json.load(open('data/road-fees/index.json'))['bindings']);linked=set(j['links']);car={k for k,v in idx.items() if v[2]=='01'}
a['fees'].update(referenceLinkedCarSpaces=len(linked&car),carSpacesWithEitherReference=len((linked|bound)&car),carSpacesWithoutEitherReference=len(car-(linked|bound)))
for d in a['districts']:d['officialReferenceLinked']=sum(k in linked for k,v in ids['accepted'].items() if (v[2] or '未提供')==d['district'])
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('Additional official text references:',added,'remaining car gaps:',a['fees']['carSpacesWithoutEitherReference'])

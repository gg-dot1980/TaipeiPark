import json,gzip,hashlib,xml.etree.ElementTree as E,collections,re,unicodedata
from pathlib import Path
j=json.load(open('data/road-source-links.json'));ids=json.load(open('data/road-identifiers.json'));spaces={r[7]:r for r in json.load(open('data/road-index.json'))};a=json.load(open('data/source-audit.json'))
raw=gzip.decompress(Path('data/source-snapshots/TCMSV_roadquery.xml.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==j['meta']['sha256']
source=E.fromstring(raw);keys=collections.Counter((r.findtext('roadSegID'),c.findtext('psId')) for r in source for c in r.findall('./cellStatusList/cell'));dupes={(x[0],x[1]) for x in ids['duplicateKeys']}
def norm(s):return re.sub(r'([一二三四五六七八九])段',lambda m:str('一二三四五六七八九'.index(m[1])+1)+'段',re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('臺','台').replace('舘','館')))
for id,b in j['links'].items():
 r=j['roads'][b['road']];sp=spaces[id];k=(r['roadSegID'],b['spaceID']);assert keys[k]==1 and k not in dupes;assert ids['accepted'][id][:2]==list(k);assert (b['lat'],b['lon'])==tuple(sp[:2]);assert norm(r['roadName'])==(norm(sp[3])[:-1] if b.get('matchMethod')=='unique-official-ids-road-section-suffix' and re.search('[A-Z]$',norm(sp[3])) else norm(sp[3]));assert r['feeText'];assert 'availability' not in b and 'cellStatus' not in b
assert len(j['links'])==j['meta']['linkedSpaces']==a['roadReference']['linkedSpaces'];assert sum(x['accepted'] for x in a['districts'])==len(spaces)
assert len(j['links'])+sum(j['meta']['rejectedCells'].values())==j['meta']['cells']
for filename,field in [('TCMSV_alldesc.xml','inventory'),('TCMSV_allavailable.xml','availability')]:assert hashlib.sha256(gzip.decompress(Path('data/source-snapshots/'+filename+'.gz').read_bytes())).hexdigest()==a['lots']['sha256'][field]
v=json.load(open('data/road-fees/pdf-2026-10-13/extraction-validation.json'));assert not v['issues'];assert len(v['pages'])==43 and all(x['match'] for x in v['pages']);assert sum(x['rows'] for x in v['pages'])==2431
print('Passed all',len(j['links']),'strict identifier/name/coordinate reference links, duplicate guards, source hashes, coverage totals, and 43-page extraction counts; no occupancy inferred.')

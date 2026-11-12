import pdfplumber,json,re,collections,unicodedata,sys
from pathlib import Path
p=Path(sys.argv[1]);rows=[];issues=[];validation=[]
for name,mode in [('hourly','hour'),('entry','entry')]:
 with pdfplumber.open(p/(name+'.pdf')) as pdf:
  for n,page in enumerate(pdf.pages,1):
   tables=page.extract_tables(); cnt=0
   for ti,t in enumerate(tables):
    for ri,c in enumerate(t):
     if c[0]=='行政區':continue
     if len(c)!=6 or not re.fullmatch('[\u4e00-\u9fff]{2}區',c[0] or ''):issues.append([name,n,ri,c]);continue
     district,road,scope,time,rate,days=c
     clean=lambda x:re.sub(r'\s+','',x or '')
     r=dict(district=clean(district),road=clean(road),scope=clean(scope),time='；'.join(clean(x) for x in (time or '').splitlines()),rate='；'.join(clean(x) for x in (rate or '').splitlines()).removesuffix('元'),days='；'.join(clean(x) for x in (days or '').splitlines()).removeprefix('週'),mode=mode,sourceFile=name+'.pdf',sourcePage=n,sourceTableRow=ri,rawCells=c)
     # Only split exactly one scope separator; multi-part scopes retained, not invented.
     split=re.split('[-~～]',r['scope']);r['start']=split[0] if len(split)==2 else None;r['end']=split[1] if len(split)==2 else None
     r['feeType']='symbol' if re.fullmatch('[A-Z]',r['rate']) else mode if re.fullmatch('[0-9]+',r['rate']) else 'mixed-or-text'
     rows.append(r);cnt+=1
   # Independent count from district glyph groups in extracted page text.
   district_count=len(re.findall(r'(?:中正|大同|中山|松山|大安|萬華|信義|士林|北投|內湖|南港|文山)區',page.extract_text()))
   validation.append(dict(file=name,page=n,rows=cnt,districtTextCount=district_count,match=cnt==district_count))
old=json.load(open('data/road-fees/ods-index-2026-03-27.json'))['rows']
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s)).replace('～','-').replace('~','-')
def key(r):return (norm(r['road']),norm(r['scope']))
def val(r):return (r['mode'],re.sub(r'(?<!\d)0(\d)',r'\1',norm(r['time'])),norm(r['rate']).removesuffix('元'),norm(r['days']).removeprefix('週'))
oldmap=collections.defaultdict(list);newmap=collections.defaultdict(list)
for r in old:oldmap[key(r)].append(r)
for r in rows:newmap[key(r)].append(r)
changed=[];unchanged=[]
for k in newmap.keys()&oldmap.keys():
 a=set(map(val,oldmap[k]));b=set(map(val,newmap[k]));(unchanged if a==b else changed).append(dict(road=k[0],scope=k[1],old=oldmap[k],new=newmap[k]))
report=dict(counts=dict(newRows=len(rows),oldRows=len(old),byFile=dict(collections.Counter(r['sourceFile'] for r in rows)),matchingScopeKeys=len(unchanged)+len(changed),unchangedScopeKeys=len(unchanged),changedScopeKeys=len(changed),newOnlyScopeKeys=len(newmap.keys()-oldmap.keys()),oldOnlyScopeKeys=len(oldmap.keys()-newmap.keys())),changed=changed,newOnly=[r for k in newmap.keys()-oldmap.keys() for r in newmap[k]],oldOnly=[r for k in oldmap.keys()-newmap.keys() for r in oldmap[k]])
for name,data in [('tariffs-2026-10-13.json',dict(meta=dict(sources=json.load(open(p/'sources.json')),effectiveDate=None,statisticsDate=None,dateNote='PDF creation date only; no effective/statistics date found in content.'),rows=rows)),('tariff-comparison.json',report),('extraction-validation.json',dict(pages=validation,issues=issues))]: (p/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))
print(json.dumps(report['counts'],ensure_ascii=False));print('issues',issues,'count mismatches',[r for r in validation if not r['match']]);print('changes',json.dumps(changed[:10],ensure_ascii=False))

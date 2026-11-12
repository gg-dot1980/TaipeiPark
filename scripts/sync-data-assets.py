"""Single synchronization point for reviewed HTML/JSON snapshots and the Worker."""
from pathlib import Path
import json,re
p=Path('worker/index.js');s=p.read_text()
assets={'COMMERCIAL_STOPS':json.loads(Path('data/commercial-stops.json').read_text()),'HTML':Path('taipei_parking_mobile/index.html').read_text(),'ROAD_INDEX':json.loads(Path('data/road-index.json').read_text()),'ROAD_QUALITY':json.loads(Path('data/road-quality.json').read_text()),'ROAD_FEES':json.loads(Path('data/road-fees/index.json').read_text()),'ROAD_SOURCE_LINKS':json.loads(Path('data/road-source-links.json').read_text()),'DATA_AUDIT':json.loads(Path('data/source-audit.json').read_text()),'COVERAGE_HTML':Path('taipei_parking_mobile/data-coverage.html').read_text()}
for name,value in assets.items():
 line='const '+name+' = '+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';'
 pattern=r'^const '+name+r' = .*;$'
 if re.search(pattern,s,re.M):s=re.sub(pattern,lambda _:line,s,flags=re.M)
 else:s+='\n'+line+'\n'
p.write_text(s)

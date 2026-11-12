import json
from shapely.geometry import Point,LineString
from pyproj import Transformer
idx=json.load(open('data/road-fees/index.json'));paths={int(k):[LineString(p) for p in v] for k,v in json.load(open('data/road-fees/scope-paths.json')).items()};tr=Transformer.from_crs(4326,3826,always_xy=True)
for id,b in idx['bindings'].items():
 p=Point(tr.transform(b['lon'],b['lat']))
 for row in b['rows']:
  assert any(line.distance(p)<=18 and line.interpolate(0).distance(p)>25 and line.interpolate(line.length).distance(p)>25 for line in paths[row]),id
print('Passed spatial distance and intersection exclusion checks for',len(idx['bindings']),'bindings (not ground-truth verification).')

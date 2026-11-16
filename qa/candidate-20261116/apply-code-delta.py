"""Reconstruct the reviewed local candidate only; never deploys or writes D1."""
from pathlib import Path
import hashlib,json,sys
here=Path(__file__).resolve().parent
base=Path(sys.argv[1]) if len(sys.argv)>1 else here.parent/'metadata-v2/corrected-worker.js'
out=Path(sys.argv[2]) if len(sys.argv)>2 else here/'fushan-integrated-worker.js'
d=json.loads((here/'candidate-code-delta.json').read_text())
a=base.read_text()
assert hashlib.sha256(a.encode()).hexdigest()==d['baseSha256'],'Unexpected base: do not force apply'
assert not out.exists(),'Refuse overwrite'
html,server=a.split('\n',1)
html=html[:d['htmlPrefixLength']]+d['htmlReplacement']+html[-d['htmlSuffixLength']:]
for old,new in d['serverReplacements']:
    assert server.count(old)==1,'Unexpected server shape'
    server=server.replace(old,new)
b=html+'\n'+server
assert hashlib.sha256(b.encode()).hexdigest()==d['outputSha256']
out.write_text(b)
print(d['outputSha256'])

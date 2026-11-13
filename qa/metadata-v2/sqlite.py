import json,sqlite3,sys
from pathlib import Path
a=json.load(sys.stdin);db=sqlite3.connect(Path(__file__).parent/'candidate.sqlite');db.row_factory=sqlite3.Row
cur=db.execute(a['sql'],a.get('params',[]));rows=[dict(r) for r in cur.fetchall()];db.commit();print(json.dumps(rows))

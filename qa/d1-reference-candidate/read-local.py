import sqlite3,json,sys
a=json.load(sys.stdin);db=sqlite3.connect('file:/workspace/scratch/85889dd4920d/taipeipark-work/qa-next100/d1-reference-candidate/candidate.sqlite?mode=ro',uri=True);db.row_factory=sqlite3.Row;print(json.dumps([dict(r) for r in db.execute(a['sql'],a['params']).fetchall()]))

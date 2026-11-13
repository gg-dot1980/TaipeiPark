"""Rebuild local metadata fixture from the tracked public export. Never contacts D1."""
import datetime, gzip, hashlib, json, pathlib, sqlite3, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
manifest = json.loads((HERE / 'manifest.json').read_text())
new_id = manifest['snapshotId']
old_id = new_id.removesuffix('-meta2')
db_path = HERE / 'candidate.sqlite'
if db_path.exists():
    raise SystemExit('Local fixture already exists. Move it aside before a clean rebuild.')
archive = ROOT / 'data/candidate-data.sql.gz'
tracked = json.loads((ROOT / 'MANIFEST.json').read_text())
expected = next(x['sha256'] for x in tracked if x['path'] == 'data/candidate-data.sql.gz')
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected, 'Source archive changed'
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row
db.executescript(gzip.decompress(archive.read_bytes()).decode())
old = dict(db.execute('SELECT * FROM address_snapshot WHERE snapshot_id=?', (old_id,)).fetchone())
assert old['source_sha256'] == manifest['sourceSha256']
assert old['index_sha256'] == manifest['indexSha256']
assert old['state'] == 'verified' and old['expected_references'] == 2
counts = {kind: db.execute('SELECT count(*) FROM '+table+' WHERE snapshot_id=?', (old_id,)).fetchone()[0]
          for kind, table in [('doors', 'address_door'), ('conflicts', 'address_conflict'), ('references', 'address_reference')]}
assert counts == manifest['counts'], 'Actual counts differ from reviewed manifest'
rows = [dict(r) for r in db.execute('SELECT * FROM address_reference WHERE snapshot_id=? ORDER BY address_key', (old_id,))]
meta = json.loads(old['meta_json'])
base_checked = meta['references']['checkedAt']
reference_dates = [{'addressKey': r['address_key'], 'evidenceCheckedAt': json.loads(r['evidence_json']).get('checkedAt', base_checked),
                    'timestampBasis': 'row' if 'checkedAt' in json.loads(r['evidence_json']) else 'original collection'} for r in rows]
meta['references']['originalCollectionCheckedAt'] = base_checked
meta['references']['checkedAt'] = max(r['evidenceCheckedAt'] for r in reference_dates)
meta['references']['rowCount'] = counts['references']
meta['references']['perReferenceEvidenceTimes'] = reference_dates
meta['migration'] = {'fromSnapshot': old_id, 'preparedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     'importedAt': None, 'scope': 'local fixture only; not a cloud import timestamp'}
with db:
    db.execute('INSERT INTO address_snapshot VALUES (?,?,?,?,?,?,?,?)',
               (new_id, old['source_sha256'], old['index_sha256'], json.dumps(meta, ensure_ascii=False, separators=(',', ':')),
                counts['doors'], counts['conflicts'], counts['references'], 'loading'))
    for table in ['address_door', 'address_conflict', 'address_reference']:
        cols = [r[1] for r in db.execute('PRAGMA table_info('+table+')') if r[1] != 'snapshot_id']
        db.execute('INSERT INTO '+table+' SELECT ?,'+','.join(cols)+' FROM '+table+' WHERE snapshot_id=?', (new_id, old_id))
        assert db.execute('SELECT '+','.join(cols)+' FROM '+table+' WHERE snapshot_id=? EXCEPT SELECT '+','.join(cols)+' FROM '+table+' WHERE snapshot_id=?', (old_id, new_id)).fetchone() is None
    assert dict(db.execute('SELECT * FROM address_snapshot WHERE snapshot_id=?', (old_id,)).fetchone()) == old
assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
assert not db.execute('PRAGMA foreign_key_check').fetchall()
db.close()
subprocess.run(['patch', '--batch', '--fuzz=0', '-o', str(HERE / 'corrected-worker.js'), str(ROOT / 'dist/server/index.js'), str(HERE / 'metadata-candidate.patch')], check=True)
(HERE / 'preparation-result.json').write_text(json.dumps({'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'local only; public write lock unchanged', 'oldSnapshot': old_id, 'newSnapshot': new_id,
    'counts': counts, 'oldSnapshotUntouched': True, 'rowsUnchanged': True, 'referenceDates': reference_dates,
    'historicalImportTimeKnown': False}, ensure_ascii=False, indent=2))
print(json.dumps({'prepared': True, 'counts': counts, 'oldSnapshotUntouched': True}))

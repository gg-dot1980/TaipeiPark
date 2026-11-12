# Database construction and limitations

Production v30 is represented by the bundled Worker and public data. It must not be described as having completed the D1 migration.

The experimental D1 schema has four tables: `address_snapshot`, `address_door`, `address_conflict`, and `address_reference`, with integer E7 coordinates and snapshot-scoped keys. A local empty schema can be created with:

```sh
python - <<'PY'
import sqlite3
from pathlib import Path
c=sqlite3.connect('address-local.sqlite')
c.executescript(Path('experimental/d1/schema.sql').read_text())
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
c.close()
PY
```

Import pipeline design: obtain the official Taipei address dataset and its source metadata; normalize full and districtless address keys; exclude conflicting coordinates; calculate source/index SHA-256; load a new snapshot in `loading` state; import doors, conflicts and independently sourced reference points; compare every restored row and counts against one shared manifest; only mark `verified` after manifest, metadata and actual rows agree. Preserve existing immutable snapshots. Cloud provisioning/import credentials and runtime DB contents are intentionally absent.

Known incomplete gate as of this import: the old isolated importer recorded expected references=2 but a separate validator expected 3. Three actual references were wrongly accepted without metadata consistency. Do not reuse that validation result as a migration pass. The most recent documented new-100 suite is 69/100, below the 85% publication threshold, and an independently reproducible full D1 backup/restore is not yet established. This schema-only export is not a claim that the data import or migration is complete.

# D1 metadata repair checkpoint

## Finding

The live test D1 still declares `expected_references=2` but contains three intended reference rows: Shuangcheng, Bangka and Wenlin. The snapshot initializer hard-coded 2; its separate verifier hard-coded 3 and never compared the persisted metadata. This is a code/manifest synchronization defect, not evidence that one parking geometry row was added or lost.

The original importer appended Wenlin to a two-row reference collection. It retained the collection's `checkedAt=2026-11-10T03:28:04.738613+00:00` (11:28 Taipei), although Wenlin's row records `2026-11-10T09:39:09.533615+00:00` (17:39 Taipei). The local preparation now preserves the original timestamp, records per-reference timestamps with their basis, and records the latest included evidence timestamp separately from preparation/import.

The address source is the Taipei Civil Affairs address dataset, not the street-parking SHP. Its stored source update is 2026-11-02 10:32:43 Asia/Taipei, SHA-256 `51b3d530445f5f6cc742ae4b0f2598891f48e760958278e500cf5a1d52c752e3`; the derived index hash is `42015a39689740c2bf8a1ef1e6c695ae4765ef25564d174bddd8600c1bbcaa4d`. Counts remain 251431 doors, 15 conflict keys and 3 reference points. Source-row total 1158179 and derived unique-door count measure different things.

## Date distinctions

The street-parking source page was independently retrieved in this pass. It separately displays SHP resource update 2026-10-06 10:25:50, CSV update 2026-10-15 11:17:10 and catalog metadata update 2026-10-15 11:17:37. It warns that catalog modification is not actual layer update. Filename `park01_202610021742UTF8.zip` is a further label, not a certified effective date. These dates do not explain reference count 2 vs 3. See source-dates.json for URL and retrieved-page hash.

The historical import report and database schema contain no import start/end timestamp. Exact import time is unknown; file mtime, evidence checkedAt, deployment time and source update must not substitute for it. New local metadata intentionally leaves importedAt null.

## Reproducible local repair

From repository root, with Python 3, Node and GNU patch installed:

```sh
python3 qa/metadata-v2/prepare-local.py
node qa/metadata-v2/test.mjs
node qa/metadata-v2/safety-test.mjs
node qa/metadata-v2/fixed100.mjs
```

Preparation verifies the tracked public SQL archive hash, restores it locally, derives and compares actual counts with the reviewed manifest, copies all rows into the new immutable candidate snapshot, and leaves the historical snapshot untouched. It reconstructs the corrected Worker from the tracked patch without changing the deployed Worker file. Existing fixtures are refused rather than overwritten. Original absolute paths and a missing generated Worker/fixture previously prevented these tests from reproducing from a fresh GitHub checkout; the portable preparation fixes that gap.

The mutation tests run only against local SQLite. Passing them is not a cloud migration, site deployment or location-accuracy improvement. The public Worker still blocks non-GET import requests. There is currently no configured protected import credential. Do not reopen an unauthenticated import endpoint or place dataset backfills in schema migrations.

## Remaining release gates

- Protected, explicitly authorized D1 migration and complete readback, preserving the old snapshot.
- Fixed independent location acceptance remains 69/100, below 85/100. Offline replay classifications are not new independently corroborated passes.
- Browser/API evidence and production migration/rollback checks remain.
- Production main/v30 and all deployed Sites were unchanged in this pass.

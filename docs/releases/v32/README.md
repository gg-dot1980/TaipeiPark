# Production v32 — D1 migration record

This GitHub content sync preserves the existing main history and documentation. The Sites source SHA in provenance.json identifies the deployed source; the GitHub synchronization commit is separate. No Site is redeployed by this synchronization.

Production migrated to D1 on 2026-11-17. The exact deployed Worker, production hosting manifest, build script and four-table schema are synchronized. The final snapshot is `door-42015a39689740c2bf8a1ef1-ref-251f7a27f3-meta2-fushan`: 251431 doors, 15 conflicts, 4 references. Runtime database binding is required; source checkout alone does not populate D1. The released Worker does not provide an unrestricted importer.

## Evidence and limits

- Historical production import/readback: all 251450 rows equal the local candidate; safety checks are recorded in cloud-import-restore-result.json.
- Historical post-release verification: seven HTTP groups and three desktop browser address cases passed. These are not a fresh 100-case regression.
- Fixed location acceptance remains 70/100; 30 unresolved. The user authorized migration before reaching 85%; further location releases retain the original acceptance standard.
- iPhone/390px real-device test was explicitly skipped by the user and remains untested; 500px desktop checks are not mobile-device proof.
- Test v5 rollback/redeployment was previously tested. Production v30 source ba1bd5c93349dba31d70d3b0978bbfbd0c45fd8e and Sites version 30 remain rollback references. Rolling code back does not delete D1.

## Data inventory and restoration limits

Existing repository public parking and road datasets are retained. `pre-fushan-public-small-tables.json` is explicitly the earlier metadata/15-conflict/3-reference backup; it is not the final 4-reference snapshot and must not be imported unchanged as final. `fushan-reference.json` and `data-manifest.json` document the fourth reference and final expected hashes/counts. All small-table evidence contains public location sources only.

The 251431 address rows, full SQLite backup, complete SQL export, runtime secrets and browser/session state are NOT uploaded here. This repository is NOT a complete D1 backup and cannot independently reconstruct the entire database from these files. Obtain the verified full address backup, normalize/import under a new loading snapshot, include all four references with their evidence, verify source/index hashes and every row/count/metadata field, and only then mark verified. Do not overwrite verified snapshots or enable unauthenticated import endpoints.

The old compressed test site's independent full database backup remains incomplete; this sync does not authorize or perform its removal.

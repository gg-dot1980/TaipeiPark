> Superseded migration status: see [2026-11-16 live migration gates](../migration-gates-20261116/README.md). Test v5 now uses the new verified snapshot. The original local-only notes below are historical; 85/100 is now a post-migration improvement target, not the migration release gate.

# 2026-11-16 local candidate: 70 / 100
This is a source/evidence checkpoint on test-d1, not a Site deployment or live D1 migration. Production main/v30, deployed test v2 and existing test branch files remain unchanged.

## Result
Fixed query NEXT-009 now resolves via the independently corroborated Fushan exact-address reference, 6 m from the frozen comparison point. Previous 69 qualified cases retained; other 99 actual results unchanged. Candidate evidence-qualified acceptance is 70/100, below the required 85. NTU exact-name support is independent work and does NOT pass the ambiguous campus-address case.

## Code and data
Run the existing qa/metadata-v2/prepare-local.py instructions first, then:
`python3 qa/candidate-20261116/apply-code-delta.py`
The hash-checked compact delta reconstructs the exact locally tested Worker without tracking another 8 MiB artifact. Delta reconstruction equality was verified in memory against the original candidate. No secrets or runtime database backups are included.
fushan-reference.json is the new public-data row; fushan-manifest.json records the candidate snapshot counts 251431/15/4. This is not an authorized cloud-import script. A protected migration must preserve old snapshots and insert into a new snapshot, verify row/count/metadata identity and read back. Never reopen public import writes.

## Evidence and dates
Checkpoint created 2026-11-16 14:37 Taiwan. Address source date remains 2026-11-02 10:32 Taiwan. Fushan source checked 2026-11-16 14:36; operator article last updated 2026-01-08, not a claim of fresh surveyed entrance or current fee.
fixed100-results-summary.json records all 100 outcomes and original full-result SHA256; request payloads omitted. Descriptive classifications are NOT pass scores. Full raw captures and full replay remain locally retained. batch-source-review.json records why remaining cases cannot be promoted. Source URLs and hashes retain provenance.
The old harness had a stale commit field; summary instead records exact candidate source hash. No published source commit is claimed for the historical replay.

## Validation already performed
100-case offline recorded-response replay with actual local SQLite; only NEXT-009 changed. Entity flow 7 checks, metadata mutation 13 checks. Not browser/live API acceptance, not fresh full checkout CI. Candidate application script is a newly packaged reconstruction helper; core reconstruction verified exactly, full portable replay setup not re-run in this synchronization.

## Remaining gates
15 further independently evidenced passes, Browser/API verification, protected migration and rollback. Current live metadata still expected references 2 vs actual 3. No deployment or score inflation.

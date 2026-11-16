# D1 migration gates, 2026-11-16
Latest user instruction separates the 85/100 location-accuracy work from migration. Migration release gates are (1) live data consistency, (2) protected import/retry protection and backup/restore/rollback, (3) full function Browser/mobile acceptance. The location target continues after migration and no longer blocks it by itself.

## Verified on the public D1 test site
- Fresh cloud GET export: 251431 doors, 15 conflicts, 3 references; all door values verified in SQLite, index SHA matched.
- Protected new snapshot restore: 251431/15/4 including independently sourced Fushan reference; all rows read back from cloud and compared exactly.
- Initialization retry and same-row retry succeeded; conflicting metadata/rows returned409; missing token403; verified snapshot rejected writes; repeated verify read-only.
- Original snapshot remained untouched. Test site activated v5, rolled back to saved v2 and checked old snapshot/read APIs, then restored v5 and checked new snapshot/read APIs.
- Temporary import secret removed (environment revision2, entries empty). Final public write route405; staging route404.
- Current test v5 source: 8375951e81425783d17eb539e7d3c52ce7359b60.

The first import interrupted after a non-JSON HTTP error; the original status code was obscured by JSON parsing and its root cause is not established. Read-only inspection found177200 rows. Resume compared every existing row before uploading only74250 missing rows (74231 doors+15 conflicts+4 references). No overwrite or blind replay.

## Not complete
Browser/mobile acceptance remains blocked: earlier browser denial concerned auth.openai.com observation and a no-login-retry instruction; no bypass attempted. NUC exposed no CUA browser. HTTP and controlled-function tests are not a Browser pass.
Production remains v30. Location acceptance remains70/100.
This is application-level logical export/restore into a separate snapshot and saved-Worker-version rollback, NOT destructive database restoration or D1 Time Travel.
No runtime backup database or credentials are included here. Public-data snapshot backup is retained locally. Scripts and intermediate source are retained for audit; these reports are not a turnkey production migration.

All timestamps in JSON are UTC; public verification finished2026-11-16 16:37 Taiwan.

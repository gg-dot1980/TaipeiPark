# Public address data

This gzip SQL is a reproducible export of the local D1 reference candidate, not a claimed live D1 database backup. Counts: {"address_snapshot": 1, "address_door": 251431, "address_conflict": 15, "address_reference": 3}. It preserves the known expected_references metadata discrepancy. Do not import into production without validation.

Restore locally: `gunzip -c data/candidate-data.sql.gz | sqlite3 candidate.sqlite`. The metadata-v2 patch and validation results are in qa/metadata-v2; that migration is NOT deployed.

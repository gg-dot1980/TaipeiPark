# Import validation, 2026-11-12

- Production v30 source: ba1bd5c93349dba31d70d3b0978bbfbd0c45fd8e.
- Initial import: 69 GitHub blobs individually matched local Git hashes.
- All JavaScript tests in scripts/test-all.sh passed. Initial aggregate run stopped on unavailable Python test dependencies, not an assertion failure.
- Dependencies installed in an isolated Python 3.12 venv from https://pypi.org/simple, versions pinned in requirements-test.txt.
- Resumed remaining sequence passed: road-fee-geometry-test.py (9451 bindings); source-links-test.py (21973 strict links); build.sh; validate-artifact.mjs. No repeated JavaScript run was necessary because its source/input had not changed.
- Empty experimental D1 schema: integrity_check=ok and four expected tables present. This does not validate production database contents or backup/restore.
- Formal production remained v30; compression candidate remained v2; isolated D1 remained v1, on distinct Sites project identities and URLs. No publishing or database-write tools were called.
- New-100 D1 acceptance, live-data freshness, browser/mobile QA and migration readiness remain outside this source-export verification.

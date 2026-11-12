#!/usr/bin/env bash
set -euo pipefail
for f in scripts/*-test.mjs; do node "$f"; done
python scripts/road-fee-geometry-test.py
python scripts/source-links-test.py
bash scripts/build.sh
node scripts/validate-artifact.mjs

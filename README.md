# TaipeiPark test-compressed

This branch tracks the corresponding isolated test site only. `main` remains production v30. See provenance.json for deployed source and site version. GitHub commits do not automatically deploy Sites.

## Update contract
Every future change to this test site must be committed to this branch with data/source provenance, patch intent, test results, and deployed Sites version. Never mix the other test site into this branch. Use a separate dated commit per actual update; do not fabricate past commits. Never commit credentials, private player/user data, or runtime tokens.

## Current status
Compression candidate v2. Full public data is embedded in worker/index.js.

# Historical user-reported regression cases

Run: `node qa/historical-regressions/test.mjs`. No live writes or required network calls. The default tests the checked-out test-d1 worker. Optional TAIPEIPARK_WORKERS is a JSON array of [label, absolute-worker-path] pairs for source comparisons.

Recorded run 2026-11-15 compared main 2915418f86345eee6c9434e1e2f88bb5fc1938fa with test-d1 ffdee82f5062cb83ad860632cb7edfec1251bcdd. Sites metadata at that check remained production v30, D1 candidate v2, old compressed test v3. These are local source/VM tests, not live browser or device tests.

## Added coverage
- Exact user Google Maps short URL with URL-encoded leading newline and nested query encoding. Normalization and both fixture success/failure paths.
- Failure must preserve the query, mark unresolved, explain Taipei Main Station fallback, and never count it as successful destination resolution.
- Jianzhong Red Building mismatched names rejected. Existing general geocode tests already test rejection; this suite links it to the historical user report.
- NTU fixed center (25.01733,121.53324), 500m/1000m results include accessible static spaces without suggesting current vacancy.

## Important limits
- Google redirect success is a synthetic response, not a claim the current short URL resolves live.
- No claim of successful official Jianzhong Red Building positioning. Current source intentionally removed older hardcoded cultural-reference overrides.
- Fixed NTU center is not an independently verified entrance or guaranteed original historical center. Counts 144/1068 total and 3/20 accessible cannot be directly compared with historical 55/15 at a different center.
- NEXT-057 NTU Xinhai underground parking remains spatial-review: whole-campus address point and parking-facility reference differ by 1043m. No new independently accepted cases; 69/100 and 85/100 release gate unchanged.
- Road geometry snapshot 2026-10-02; SHP resource update 2026-10-06 10:25:50 +08; metadata/catalog update 2026-10-15 is not geometry date. ROAD_QUALITY last verification 2026-11-09; static spaces are not live availability. Official address source update 2026-11-02 is a separate dataset.
- No deployment, production changes, database writes, or authorization changes in this commit.

Historical report: https://chatgpt.com/c/6ae03ae9-6060-83ec-b977-e76df9614465?messageId=5139f740-8919-452d-bac7-c1a4c6e73bbe
Official road dataset: https://data.taipei/dataset/detail?id=5a911ea5-1694-4301-808e-e1780d971611

The fixture harness is adapted from this repository's existing main scripts/geocode-test.mjs; it stubs DOM and network, not full rendering.

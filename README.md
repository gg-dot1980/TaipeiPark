# TaipeiPark — public source (main)

Runtime logic and page code are kept in `src/`. Map datasets, supplemental locations,
third-party evidence, mixed SQL and historical data-dependent QA artifacts are held
outside this public tree in ChatGPT Library. They are not replaced with fabricated or empty data.

## Build

Restore the matching private pack from the Library backup, outside this checkout:

```sh
TAIPEIPARK_PRIVATE_PACK=/absolute/private/path/main-private-pack.json npm run build
```

Build checks the pack version and reconstructed Worker SHA-256 against
`build-manifest.json`. Missing data or a mismatched release stops the build.
`dist/` must never be committed. Runtime D1 data is separately backed up; this
repository is not a complete database backup. No deployment occurs on build.
The published Sites deployment and its D1 are unchanged by this source cleanup.

## Data policy

Do not commit map/supplemental location datasets, venue references, OSM/PlugShare
records, private packs, generated Workers, SQL data dumps, or coordinate-bearing
QA evidence. New datasets require individual source and reuse-license review.
Generic map rendering/parsing code remains; third-party software notices remain intact.
See `DATA-SOURCES.md` for the limited official raw files retained here.

This normal commit cleans the current branch only. Earlier commits and third-party
copies may still contain removed data. No history rewriting or visibility change was performed.

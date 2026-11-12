# TaipeiPark

Source tracking for the public Taipei parking application: https://taipeipark.audihsu.chatgpt.site

## Imported baseline

Production Sites version **30**, source commit `ba1bd5c93349dba31d70d3b0978bbfbd0c45fd8e`, imported 2026-11-12. This is a new GitHub history starting from a verified snapshot, not a reconstruction of older patches. Uploading this repository does not deploy or modify the live site.

## Build and test

Requires Node.js, Python 3 (`python` command), and Bash. No application dependency install is needed for the bundled Worker. The geometry test additionally requires Shapely and pyproj; tested versions are pinned in `requirements-test.txt`.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://pypi.org/simple -r requirements-test.txt
cp .openai/hosting.json.example .openai/hosting.json
# Set your own authorized Sites project ID before deploying.
npm test
npm run build
npm run validate
npm run dev
```

The build synchronizes reviewed HTML/data into `worker/index.js`, then creates `dist/server/index.js`. The GitHub export omits the original Sites project identity. For an independently authorized deployment, configure `.openai/hosting.json` with your own project ID before building. Do not accidentally publish to the original production project.

## Data and behavior

`data/` holds reviewed public parking inventory, availability fixtures, road geometry, tariff snapshots, provenance and audit metadata. Fixtures are historical testing inputs, not current parking availability. Unknown or stale capacity is not represented as available. Approximate address results require confirmation and are not surveyed parking entrances.

Sources include Taipei Parking Management and Open Data, and OpenStreetMap. Preserve embedded attribution and source metadata. Source records and third-party assets retain their respective terms; this import grants no new license to third-party data or assets. The repository does not contain credentials, environment secret values, user locations/history, private databases or runtime database backups.

## Experimental database work

`experimental/d1/schema.sql` records the isolated D1 address-storage design, **not production v30's storage**. See `docs/DATABASE.md`. The compression candidate v2 and isolated D1 candidate v1 are separate live experiments and are not represented as production-ready here.

Future reviewed changes should be committed with their test evidence. Do not publish D1 changes until the established acceptance gates are met.

## Import verification

Build and Worker artifact validation passed. All JavaScript tests passed in `npm test`. After installing missing Shapely and pyproj in an isolated virtual environment from official PyPI, the remaining geometry and source-link tests, build and artifact validation passed. This was a resumed sequence rather than one uninterrupted aggregate run. See `docs/IMPORT-VALIDATION.md`. Runtime data freshness, D1 migration and browser acceptance were not revalidated by this source export.

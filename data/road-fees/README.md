# Taipei road fee sources

Current `index.json` is generated from the official PMA hourly/per-entry PDFs in `pdf-2026-10-13/`. The documents were generated on October 13; no effective or statistics date appears in their content. Keep this distinction visible. Sources, hashes, per-page source pointers, raw cells and extraction-count validation are retained.

`prepare-pdf-fees.py` reuses an earlier validated OSM path only for identical normalized road and endpoint text, then requires matching SHP district and road name, <=18 m distance from the path, >25 m distance from endpoints, no overlapping conflicting rule and no unresolved differently priced scope on that road. It does not infer a tariff from a road name alone. Missing/new/ambiguous scopes have no fallback price. Rules still need runtime day/unit/code parsing before coloring; dedicated accessible spaces do not receive ordinary-car prices.

The old March source remains as `source.ods`, `ods-index-2026-03-27.json` and `ods-scope-paths.json` for comparison and path provenance. It is not an active pricing fallback. Its hash was rechecked on November 9 and was unchanged.

Use `scripts/sync-data-assets.py` to embed current HTML and datasets into the Worker. Run `scripts/test-all.sh` for regression, geometry, source-reference and artifact validation. See the root README for refresh order and dependencies.

All data is a dated snapshot. Map refresh does not re-download tariff PDFs or SHP. No street vacancy is inferred from any tariff or identifier reference.

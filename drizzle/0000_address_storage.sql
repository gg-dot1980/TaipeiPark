CREATE TABLE address_snapshot (
 snapshot_id TEXT PRIMARY KEY,
 source_sha256 TEXT NOT NULL,
 index_sha256 TEXT NOT NULL,
 meta_json TEXT NOT NULL,
 expected_doors INTEGER NOT NULL,
 expected_conflicts INTEGER NOT NULL,
 expected_references INTEGER NOT NULL,
 state TEXT NOT NULL DEFAULT 'loading' CHECK(state IN ('loading','verified'))
);
--> statement-breakpoint
CREATE TABLE address_door (
 snapshot_id TEXT NOT NULL REFERENCES address_snapshot(snapshot_id),
 address_key TEXT NOT NULL,
 districtless_key TEXT NOT NULL,
 lat_e7 INTEGER NOT NULL CHECK(lat_e7 BETWEEN 247000000 AND 255000000),
 lon_e7 INTEGER NOT NULL CHECK(lon_e7 BETWEEN 1213000000 AND 1218000000),
 PRIMARY KEY(snapshot_id,address_key)
);
--> statement-breakpoint
CREATE INDEX address_door_districtless ON address_door(snapshot_id,districtless_key);
--> statement-breakpoint
CREATE TABLE address_conflict (
 snapshot_id TEXT NOT NULL REFERENCES address_snapshot(snapshot_id),
 address_key TEXT NOT NULL,
 districtless_key TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,address_key)
);
--> statement-breakpoint
CREATE INDEX address_conflict_districtless ON address_conflict(snapshot_id,districtless_key);
--> statement-breakpoint
CREATE TABLE address_reference (
 snapshot_id TEXT NOT NULL REFERENCES address_snapshot(snapshot_id),
 address_key TEXT NOT NULL,
 lat_e7 INTEGER NOT NULL,
 lon_e7 INTEGER NOT NULL,
 evidence_json TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,address_key)
);
--> statement-breakpoint

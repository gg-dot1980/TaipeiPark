#!/usr/bin/env python3
"""Build a conservative commercial-stop reference layer from an official CSV.

Python 3.9+ standard library only. No network requests or external dependencies.
Defaults are relative to the current working directory, normally the repo root.
Use --checked-at for byte-for-byte reproducibility of a reviewed snapshot.
Malformed or out-of-bounds coordinates fail closed before output is written.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import io
import json
import math
from pathlib import Path

SOURCE_METADATA = {'source': '臺北市停車管理工程處：營業用共用臨停區的位置與數量',
 'dataset': 'https://data.taipei/dataset/detail?id=5a911ea5-1694-4301-808e-e1780d971611',
 'download': 'https://data.taipei/api/frontstage/tpeod/dataset/resource.download?rid=a76540cb-b6ee-410f-a2ca-de9432d62390',
 'license': '政府資料開放授權條款第1版',
 'licenseUrl': 'https://data.taipei/rule',
 'rulesSource': 'https://pma.gov.taipei/News_Content.aspx?n=E860B620A78D1DAA&s=89D421DF230A9CEA&sms=87415A8B9CE81B16',
 'rulesSourceUpdated': '2026-09-30T11:35:00+08:00',
 'hoursSource': 'https://pma.gov.taipei/News_Content.aspx?n=C367863C93700356&s=259EF924BC33BC3E',
 'rules': {'purpose': '限符合資格車輛臨時上下客或裝卸貨；非一般停車位。',
           'eligibleVehicles': ['貨車', '計程車', '復康巴士', '長照車輛（福祉車）', '到宅沐浴車'],
           'maxStayMinutes': 20,
           'truckEligibility': '行照須明確標示貨車（非客貨兩用車），且確有臨停裝卸貨行為；自用或營業用貨車皆可。',
           'taxiRestriction': '僅供上下客，不可排班。',
           'otherVehicles': '其他車種禁止臨停。',
           'hours': '官方2026年新聞稿說明24小時供公共服務車輛上下客及裝卸貨，實際仍應遵守現場牌面。'},
 'acceptedPositionLabel': '官方公告位置，未經逐點現地驗證'}

REVIEWED_SHA256 = 'b255a94f087340e1bf5070f076165079a8a4b4c6017aaac62650e3708d92928c'
REVIEWED_REASONS = {17: '不同地址共用同一座標：庫倫街圓山站與長安西路60號，位置待核對',
 18: '不同地址共用同一座標：庫倫街圓山站與長安西路60號，位置待核對',
 67: '來源有完全重複列：南京東路2段100號',
 80: '來源有完全重複列：南京東路2段100號',
 97: '同座標且地址部分重疊，是否同一臨停區待核對',
 102: '同座標且地址部分重疊，是否同一臨停區待核對'}

REQUIRED = ("行政區", "地址", "格位數", "周邊景點或商圈", "場站緯度", "場站經度")


def build(source, source_updated, checked_at):
    raw = source.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames is None or not set(REQUIRED).issubset(reader.fieldnames):
        raise ValueError("CSV missing required columns: " + ", ".join(REQUIRED))
    rows = list(reader)
    if not rows:
        raise ValueError("CSV is empty")
    groups = collections.defaultdict(list)
    items = []
    for n, row in enumerate(rows, 2):
        try:
            lat, lon = float(row["場站緯度"]), float(row["場站經度"])
            spaces = int(row["格位數"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric value at CSV record {n}") from exc
        if not (math.isfinite(lat) and math.isfinite(lon)
                and 24.9 <= lat <= 25.3 and 121.4 <= lon <= 121.7):
            raise ValueError(f"Invalid/out-of-Taipei coordinate at CSV record {n}; review source")
        if spaces <= 0:
            raise ValueError(f"Invalid space count at CSV record {n}")
        if not row["行政區"] or not row["地址"]:
            raise ValueError(f"Missing district/address at CSV record {n}")
        groups[(lat, lon)].append(n)
        items.append({"id": f"commercial-stop-row-{n}", "sourceRow": n,
                      "district": row["行政區"], "address": row["地址"],
                      "spaces": spaces, "lat": lat, "lon": lon,
                      "nearby": row["周邊景點或商圈"]})
    accepted, quarantined, duplicates = [], [], []
    digest = hashlib.sha256(raw).hexdigest()
    for item in items:
        members = groups[(item["lat"], item["lon"])]
        duplicate = len(members) > 1
        item["coordinateQuality"] = ("duplicate-coordinate-review" if duplicate
                                     else "source-coordinate-unverified")
        item["duplicateCoordinateRows"] = members if duplicate else []
        if duplicate:
            # Detailed findings apply only to the reviewed snapshot, never to a
            # future CSV with rearranged row numbers.
            item["quarantineReason"] = (
                REVIEWED_REASONS.get(item["sourceRow"], "同座標來源列，位置及是否重複待核對")
                if digest == REVIEWED_SHA256 else "同座標來源列，位置及是否重複待核對")
            quarantined.append(item)
        else:
            accepted.append(item)
    for (lat, lon), numbers in groups.items():
        if len(numbers) > 1:
            records = [x for x in quarantined if x["sourceRow"] in numbers]
            duplicates.append({"lat": lat, "lon": lon, "sourceRows": numbers,
                               "reason": records[0]["quarantineReason"], "records": records})
    meta = dict(SOURCE_METADATA)
    meta.update({"sourceUpdated": source_updated, "checkedAt": checked_at,
                 "sha256": digest, "records": len(items),
                 "spaces": sum(x["spaces"] for x in items), "uniqueCoords": len(groups),
                 "parseableInTaipeiBounds": len(items), "invalidCoordinates": 0,
                 "duplicateGroups": duplicates, "duplicateCoordinateRecords": len(quarantined),
                 "exactDuplicateRows": len(rows) - len({tuple(r.get(k) for k in REQUIRED) for r in rows}),
                 "conservativeNonDuplicateRecords": len(accepted),
                 "conservativeNonDuplicateSpaces": sum(x["spaces"] for x in accepted),
                 "acceptedRecords": len(accepted), "acceptedSpaces": sum(x["spaces"] for x in accepted),
                 "quarantinedRecords": len(quarantined),
                 "quarantinedSpaces": sum(x["spaces"] for x in quarantined),
                 "limitations": [
                     "CSV未提供逐點開放時段、牌面條件、費率或即時空位，不能推定免費或有空位。",
                     "沒有SHP keyid、rdcode、pkid，不做逐格綁定；與既有貨車裝卸格可能重疊，不加進車格總數。",
                     f"座標為來源場站經緯度，未完成逐點現地驗證；{len(items)}列不等於{len(items)}個已確認正確的位置。",
                     "來源列號僅在此sha256快照內穩定，更新CSV可能移動或重排，不是官方永久ID。",
                     ("6列重複座標有1組完全重複、1組不同地址明顯矛盾、1組可能同站；保留來源但建議不直接繪製這6列。"
                      if digest == REVIEWED_SHA256 else
                      f"{len(quarantined)}列同座標來源記錄已隔離，須人工核對後才能加入位置參考。")
                 ]})
    if digest == REVIEWED_SHA256:
        assert (len(accepted), len(quarantined), meta["spaces"], meta["acceptedSpaces"],
                meta["quarantinedSpaces"]) == (217, 6, 258, 251, 7)
    return {"schemaVersion": 1, "meta": meta, "accepted": accepted, "quarantined": quarantined}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path,
                        default=Path("data/source-snapshots/commercial-shared-stops.csv"))
    parser.add_argument("output", nargs="?", type=Path, default=Path("data/commercial-stops.json"))
    parser.add_argument("--source-updated", default="2026-10-15T11:17:10+08:00",
                        help="Official resource update timestamp; change when supplying a new snapshot")
    parser.add_argument("--checked-at", help="ISO8601 timestamp with timezone; default current UTC")
    args = parser.parse_args()
    checked_at = args.checked_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        for value in (args.source_updated, checked_at):
            if datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is None:
                raise ValueError("Timestamps must include a timezone")
        if args.source.resolve() == args.output.resolve():
            raise ValueError("Source and output must be different paths")
        result = build(args.source, args.source_updated, checked_at)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        parser.exit(2, f"error: {exc}\n")
    m = result["meta"]
    print(json.dumps({"output": str(args.output), "sha256": m["sha256"],
                      "records": m["records"], "spaces": m["spaces"],
                      "acceptedRecords": m["acceptedRecords"], "acceptedSpaces": m["acceptedSpaces"],
                      "quarantinedRecords": m["quarantinedRecords"],
                      "quarantinedSpaces": m["quarantinedSpaces"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

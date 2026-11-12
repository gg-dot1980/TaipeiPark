# Fee interpretation and calendar

Calendar snapshot retrieved 2026-10-28 from Taipei City Personnel Department CSV:
https://data.taipei/api/frontstage/tpeod/dataset/resource.download?rid=0dcbcfcf-f7a1-4664-a810-82c01cb524e0
Dataset: https://data.taipei/dataset/detail?id=c30ca421-d935-4faa-b523-9c175c8de738

The CSV is sparse: holidays and exceptional working days. Build complete 2026–2027 dates as working days and apply each listed `isHoliday` value; 2026 has 122 holidays and 2027 has 123. Do not infer coverage for 2028 from its single January 1 entry. Dates outside coverage remain unknown for weekday/holiday tariffs. This calendar is a reference for tariff wording; operator-specific holiday definitions or event schedules are not established by it.

Hourly normalization uses the charge unit (amount × 60 / minutes), independently of billing rounding. Calendar/time selection uses Asia/Taipei and half-open time ranges, including overnight ranges. Explicit weekdays and inherited day groups are supported. Cross-tier schedules get a related darker background and star only when the currently applicable rate is unambiguous. Progressive schedules are purple, with parsed stage rates and original wording; they are not a predicted total or a single hourly rate. Unknown, implicit-unit, event or surcharge conditions remain grey. Road geometry contains no verified price field.

Validation: `node scripts/fee-test.mjs` extracts the deployed HTML functions. Additional smoke run against all 1,778 official PAYEX records retrieved 2026-10-28: at 2026-10-28 09:30 Asia/Taipei, 430 low, 303 mid, 656 high, 17 progressive, 372 unknown. These are parser outcomes, not independently verified accuracy counts. Browser QA uses isolated fixtures and transparent map tiles, and does not verify actual basemap delivery.

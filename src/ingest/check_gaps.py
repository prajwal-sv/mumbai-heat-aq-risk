import json
import pandas as pd

with open("data/raw/openaq_sample_pm25_colaba.json", encoding="utf-8") as f:
    rows = json.load(f)["results"]

# Build a time series (UTC): turns the 332 rows into a time-indexed list of PM2.5 values.
times = pd.to_datetime([r["period"]["datetimeFrom"]["utc"] for r in rows], utc=True)
s = pd.Series([r["value"] for r in rows], index=times).sort_index()

print("Rows:", len(s), "| duplicate times:", s.index.duplicated().sum())
print("Min:", s.min(), "| Max:", s.max(), "| Mean:", round(s.mean(), 1))

# Every 15-minute slot we expected
full = pd.date_range("2026-10-21T00:00:00Z", "2026-10-27T23:45:00Z", freq="15min")
missing = full.difference(s.index)
print("Expected:", len(full), "| Missing:", len(missing))
print("Longest gap between readings:", s.index.to_series().diff().max())

# Missing readings per day (IST)
print(pd.Series(1, index=missing).tz_convert("Asia/Kolkata").resample("D").sum())

# Rows: 332 | duplicate times: 0
# Min: 16.8 | Max: 46.55 | Mean: 29.2
# Expected: 672 | Missing: 340
# Longest gap between readings: 3 days 11:45:00
# 2026-10-21 00:00:00+05:30     1
# 2026-10-22 00:00:00+05:30     1
# 2026-10-23 00:00:00+05:30    12
# 2026-10-24 00:00:00+05:30    96
# 2026-10-25 00:00:00+05:30    96
# 2026-10-26 00:00:00+05:30    96
# 2026-10-27 00:00:00+05:30    36
# 2026-10-28 00:00:00+05:30     2
# Freq: D, dtype: int64
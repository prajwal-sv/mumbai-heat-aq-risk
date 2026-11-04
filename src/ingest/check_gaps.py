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


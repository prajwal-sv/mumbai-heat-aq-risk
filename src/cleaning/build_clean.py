import json
import os
import pandas as pd

# ---- Settings (my own choices, not official limits) ----
with open("data/clean/stations_config.json", encoding="utf-8") as f:
    STATIONS = list(json.load(f).keys())
VARIABLES = ["pm25", "pm10", "temperature"]
MIN_COVERAGE = 75                   # a day needs 75% of its readings
PM_MAX = 1000                       # PM above this is impossible
PM_JUMP, PM_JUMP_MIN = 5, 200       # 5x the day's median, and above 200
TEMP_MIN, TEMP_MAX = 10, 45         # daily average temperature limits
TEMP_JUMP = 8                       # degrees away from the day's median

# ---- 1. Read the raw files (never changed) ----
rows = []
for station in STATIONS:
    for name in VARIABLES:
        path = f"data/raw/openaq_days_{station}_{name}.json"
        if not os.path.exists(path):      # a station may have no temperature sensor
            continue
        with open(path, encoding="utf-8") as f:
            results = json.load(f)["results"]
        for r in results:
            rows.append({
                "station": station,
                "variable": name,
                "date_ist": r["period"]["datetimeFrom"]["local"][:10],
                "start_utc": r["period"]["datetimeFrom"]["utc"],
                "value": r["value"],
                "coverage_pct": (r.get("coverage") or {}).get("percentCoverage"),
            })

df = pd.DataFrame(rows)
df["date_ist"] = pd.to_datetime(df["date_ist"])
df["usable"] = df["coverage_pct"] >= MIN_COVERAGE
df["suspect"] = False
df["reason"] = ""
pm = df["variable"].isin(["pm25", "pm10"])
temp = df["variable"] == "temperature"

# ---- 2. Flag suspect PM days ----
a = pm & ((df["value"] <= 0) | (df["value"] > PM_MAX))
df.loc[a, ["suspect", "reason"]] = [True, "impossible value"]
day_median = df.groupby(["variable", "date_ist"])["value"].transform("median")
b = pm & ~a & (df["value"] > PM_JUMP * day_median) & (df["value"] > PM_JUMP_MIN)
df.loc[b, ["suspect", "reason"]] = [True, "far above other stations"]

# ---- 3. Flag suspect temperature days ----
c = temp & ((df["value"] < TEMP_MIN) | (df["value"] > TEMP_MAX))
df.loc[c, ["suspect", "reason"]] = [True, "impossible temperature"]
ok = df["value"].where(temp & ~c)
t_median = ok.groupby([df["variable"], df["date_ist"]]).transform("median")
d = temp & ~c & ((df["value"] - t_median).abs() > TEMP_JUMP)
df.loc[d, ["suspect", "reason"]] = [True, "far from other stations"]

# ---- 4. Blank suspect days (never delete, never fill) ----
df["keep"] = df["usable"] & ~df["suspect"]
df["clean_value"] = df["value"].where(df["keep"])

df.to_csv("data/clean/daily_clean_final.csv", index=False)
df[df["suspect"]].to_csv("data/clean/flagged_days_final.csv", index=False)

# ---- 5. Report ----
print("Stations read:", df["station"].nunique())
print("Flagged PM rows:", int((df["suspect"] & pm).sum()))
print("Flagged temperature rows:", int((df["suspect"] & temp).sum()))
print("\nDays with a clean value:")
print(df[df["keep"]].groupby(["station", "variable"]).size().unstack())
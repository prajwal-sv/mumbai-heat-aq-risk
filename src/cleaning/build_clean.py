import json
import pandas as pd

STATIONS = ["malad_west_iitm", "kherwadi", "shivaji_nagar", "ghatkopar", "byculla", "bkc_mpcb"]
VARIABLES = ["pm25", "pm10", "temperature"]

MIN_COVERAGE = 75                   # a day needs 75% of its readings
PM_MAX = 1000                       # PM above this is impossible
PM_JUMP, PM_JUMP_MIN = 5, 200       # 5x the day's median, and above 200
TEMP_MIN, TEMP_MAX = 10, 45         # daily average temperature limits
TEMP_JUMP = 8                       # degrees away from the day's median

#  Read the raw files (never changed)
rows = []
for station in STATIONS:
    for name in VARIABLES:
        with open(f"data/raw/openaq_days_{station}_{name}.json", encoding="utf-8") as f:
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

# 2. Flag suspect PM days
a = pm & ((df["value"] <= 0) | (df["value"] > PM_MAX))
df.loc[a, ["suspect", "reason"]] = [True, "impossible value"]
day_median = df.groupby(["variable", "date_ist"])["value"].transform("median")
b = pm & ~a & (df["value"] > PM_JUMP * day_median) & (df["value"] > PM_JUMP_MIN)
df.loc[b, ["suspect", "reason"]] = [True, "far above other stations"]

# 3. Flag suspect temperature days
c = temp & ((df["value"] < TEMP_MIN) | (df["value"] > TEMP_MAX))
df.loc[c, ["suspect", "reason"]] = [True, "impossible temperature"]
ok = df["value"].where(temp & ~c)
t_median = ok.groupby([df["variable"], df["date_ist"]]).transform("median")
d = temp & ~c & ((df["value"] - t_median).abs() > TEMP_JUMP)
df.loc[d, ["suspect", "reason"]] = [True, "far from other stations"]

# 4. Blank suspect days (never delete, never fill)
df["keep"] = df["usable"] & ~df["suspect"]
df["clean_value"] = df["value"].where(df["keep"])

df.to_csv("data/clean/daily_clean_final.csv", index=False)
df[df["suspect"]].to_csv("data/clean/flagged_days.csv", index=False)

#  5. Report 
print("Flagged PM rows:", int((df["suspect"] & pm).sum()), "(expect 47)")
print("Flagged temperature rows:", int((df["suspect"] & temp).sum()), "(expect 292)")
print("\nDays with a clean value:")
print(df[df["keep"]].groupby(["variable", "station"]).size().unstack(0))


# Flagged PM rows: 47 (expect 47)
# Flagged temperature rows: 292 (expect 292)

# Days with a clean value:
# variable          pm10   pm25  temperature
# station                                   
# bkc_mpcb         513.0  508.0        460.0
# byculla          518.0  516.0        519.0
# ghatkopar        517.0  522.0        508.0
# kherwadi         544.0  543.0        544.0
# malad_west_iitm  553.0  555.0          NaN
# shivaji_nagar    519.0  522.0        499.0
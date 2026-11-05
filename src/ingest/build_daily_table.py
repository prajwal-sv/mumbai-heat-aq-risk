import json
import os
import pandas as pd

stations = ["malad_west_iitm", "kherwadi", "shivaji_nagar", "ghatkopar", "byculla", "bkc_mpcb"]
names = ["pm25", "pm10", "temperature"]

rows = []
for station in stations:
    for name in names:
        path = f"data/raw/openaq_days_{station}_{name}.json"
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
df["usable"] = df["coverage_pct"] >= 75   # flag only, nothing is filled

os.makedirs("data/clean", exist_ok=True)
df.to_csv("data/clean/daily_long.csv", index=False)

print("Total rows:", len(df))
print("Duplicate days:", df.duplicated(["station", "variable", "date_ist"]).sum())

summary = df.groupby(["station", "variable"]).agg(
    days=("date_ist", "count"),
    usable_days=("usable", "sum"),
    first=("date_ist", "min"),
    last=("date_ist", "max"),
)
span = (pd.to_datetime(summary["last"]) - pd.to_datetime(summary["first"])).dt.days + 1
summary["absent_days"] = span - summary["days"]

pd.set_option("display.width", 200)
print(summary)

# Total rows: 10350
# Duplicate days: 0
#                              days  usable_days       first        last  absent_days
# station         variable                                                           
# bkc_mpcb        pm10          595          516  2025-02-19  2026-10-31           25
#                 pm25          595          515  2025-02-19  2026-10-31           25
#                 temperature   583          502  2025-02-19  2026-10-31           37
# byculla         pm10          597          518  2025-02-19  2026-11-03           26
#                 pm25          597          517  2025-02-19  2026-11-03           26
#                 temperature   595          519  2025-02-19  2026-11-03           28
# ghatkopar       pm10          594          518  2025-02-19  2026-11-03           29
#                 pm25          594          523  2025-02-19  2026-11-03           29
#                 temperature   592          521  2025-02-19  2026-11-03           31
# kherwadi        pm10          608          544  2025-02-19  2026-11-03           15
#                 pm25          608          544  2025-02-19  2026-11-03           15
#                 temperature   608          544  2025-02-19  2026-11-03           15
# malad_west_iitm pm10          604          553  2025-02-19  2026-11-03           19
#                 pm25          607          557  2025-02-19  2026-11-03           16
#                 temperature   187          158  2025-02-19  2026-03-07          195
# shivaji_nagar   pm10          595          532  2025-02-19  2026-11-03           28
#                 pm25          596          535  2025-02-19  2026-11-03           27
#                 temperature   595          530  2025-02-19  2026-11-03           28
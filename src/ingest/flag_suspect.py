import pandas as pd

df = pd.read_csv("data/clean/daily_long.csv", parse_dates=["date_ist"])
df["suspect"] = False
df["reason"] = ""
pm = df["variable"].isin(["pm25", "pm10"])

# Rule A: impossible values
a = pm & ((df["value"] <= 0) | (df["value"] > 1000))
df.loc[a, "suspect"] = True
df.loc[a, "reason"] = "impossible value"

# Rule B: more than 5x the same-day median of all stations, and above 200
day_median = df.groupby(["variable", "date_ist"])["value"].transform("median")
b = pm & ~a & (df["value"] > 5 * day_median) & (df["value"] > 200)
df.loc[b, "suspect"] = True
df.loc[b, "reason"] = "far above other stations"

df.to_csv("data/clean/daily_flagged.csv", index=False)

flagged = df[df["suspect"]]
print("Flagged rows:", len(flagged))
print(flagged.groupby(["station", "variable"]).size())
print(flagged.sort_values("value", ascending=False)[["station", "variable", "date_ist", "value", "reason"]].to_string())


# Flagged rows: 47
# station          variable
# bkc_mpcb         pm10         4
#                  pm25         8
# byculla          pm25         1
# ghatkopar        pm10         1
#                  pm25         1
# kherwadi         pm25         1
# malad_west_iitm  pm10         1
#                  pm25         2
# shivaji_nagar    pm10        14
#                  pm25        14
# dtype: int64
#               station variable   date_ist    value                    reason
# 9450         bkc_mpcb     pm10 2025-11-30  92300.0          impossible value
# 9451         bkc_mpcb     pm10 2025-12-01  82600.0          impossible value
# 8998         bkc_mpcb     pm25 2026-05-02  74500.0          impossible value
# 8997         bkc_mpcb     pm25 2026-05-01  57300.0          impossible value
# 8847         bkc_mpcb     pm25 2025-11-22  12400.0          impossible value
# 8846         bkc_mpcb     pm25 2025-11-21   6750.0          impossible value
# 8991         bkc_mpcb     pm25 2026-04-25    574.0  far above other stations
# 1675         kherwadi     pm25 2025-11-24    529.0  far above other stations
# 8992         bkc_mpcb     pm25 2026-04-26    528.0  far above other stations
# 7210          byculla     pm25 2026-05-09    319.0  far above other stations
# 1084  malad_west_iitm     pm10 2026-06-23    242.0  far above other stations
# 452   malad_west_iitm     pm25 2026-05-29      0.0          impossible value
# 3281    shivaji_nagar     pm25 2025-04-20      0.0          impossible value
# 3282    shivaji_nagar     pm25 2025-04-21      0.0          impossible value
# 451   malad_west_iitm     pm25 2026-05-28      0.0          impossible value
# 3291    shivaji_nagar     pm25 2025-04-30      0.0          impossible value
# 3290    shivaji_nagar     pm25 2025-04-29      0.0          impossible value
# 3289    shivaji_nagar     pm25 2025-04-28      0.0          impossible value
# 3288    shivaji_nagar     pm25 2025-04-27      0.0          impossible value
# 3287    shivaji_nagar     pm25 2025-04-26      0.0          impossible value
# 3286    shivaji_nagar     pm25 2025-04-25      0.0          impossible value
# 3285    shivaji_nagar     pm25 2025-04-24      0.0          impossible value
# 3284    shivaji_nagar     pm25 2025-04-23      0.0          impossible value
# 3283    shivaji_nagar     pm25 2025-04-22      0.0          impossible value
# 3292    shivaji_nagar     pm25 2025-05-01      0.0          impossible value
# 3588    shivaji_nagar     pm25 2026-03-11      0.0          impossible value
# 3293    shivaji_nagar     pm25 2025-05-02      0.0          impossible value
# 3878    shivaji_nagar     pm10 2025-04-21      0.0          impossible value
# 3879    shivaji_nagar     pm10 2025-04-22      0.0          impossible value
# 3880    shivaji_nagar     pm10 2025-04-23      0.0          impossible value
# 3877    shivaji_nagar     pm10 2025-04-20      0.0          impossible value
# 3889    shivaji_nagar     pm10 2025-05-02      0.0          impossible value
# 3888    shivaji_nagar     pm10 2025-05-01      0.0          impossible value
# 3887    shivaji_nagar     pm10 2025-04-30      0.0          impossible value
# 3886    shivaji_nagar     pm10 2025-04-29      0.0          impossible value
# 3885    shivaji_nagar     pm10 2025-04-28      0.0          impossible value
# 3884    shivaji_nagar     pm10 2025-04-27      0.0          impossible value
# 3883    shivaji_nagar     pm10 2025-04-26      0.0          impossible value
# 3882    shivaji_nagar     pm10 2025-04-25      0.0          impossible value
# 3881    shivaji_nagar     pm10 2025-04-24      0.0          impossible value
# 8985         bkc_mpcb     pm25 2026-04-19      0.0          impossible value
# 5133        ghatkopar     pm25 2025-06-29      0.0          impossible value
# 5727        ghatkopar     pm10 2025-06-29      0.0          impossible value
# 4184    shivaji_nagar     pm10 2026-03-11      0.0          impossible value
# 8984         bkc_mpcb     pm25 2026-04-18      0.0          impossible value
# 9579         bkc_mpcb     pm10 2026-04-18      0.0          impossible value
# 9580         bkc_mpcb     pm10 2026-04-19      0.0          impossible value
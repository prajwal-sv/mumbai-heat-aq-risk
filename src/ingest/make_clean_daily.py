import pandas as pd

df = pd.read_csv("data/clean/daily_flagged.csv", parse_dates=["date_ist"])

# Keep a value only if coverage is enough AND it is not suspect
df["keep"] = df["usable"] & ~df["suspect"]
df["clean_value"] = df["value"].where(df["keep"])   # blanked, never deleted
df.to_csv("data/clean/daily_clean.csv", index=False)

# PM2.5: one column per station, every calendar day present
pm = df[df["variable"] == "pm25"].pivot(index="date_ist", columns="station", values="clean_value")
pm = pm.reindex(pd.date_range(pm.index.min(), pm.index.max()))

print("Days with a value:")
print(pm.notna().sum())
print("\nMonthly mean after cleaning:")
print(pm.resample("MS").mean().round(0))

# Length of each run of missing days
print("\nMissing runs (in days):")
for station in pm.columns:
    m = pm[station].isna()
    runs = m.groupby((~m).cumsum()).sum()
    runs = runs[runs > 0]
    print(station, "| runs:", len(runs), "| 1 day:", (runs == 1).sum(),
          "| 2-3 days:", ((runs >= 2) & (runs <= 3)).sum(),
          "| 4+ days:", (runs >= 4).sum(), "| longest:", runs.max())


# What the output says
# Each station has about 508 to 555 days with a good PM2.5 value.
# The monthly averages now look normal. BKC’s 4,567 dropped to 24, and its 734 dropped to 54.
# Most missing stretches are short: 1 day, or 2 to 3 days.
# A few stretches are long, 10 to 13 days.


#     Days with a value:
# station
# bkc_mpcb           508
# byculla            516
# ghatkopar          522
# kherwadi           543
# malad_west_iitm    555
# shivaji_nagar      522
# dtype: int64

# Monthly mean after cleaning:
# station     bkc_mpcb  byculla  ghatkopar  kherwadi  malad_west_iitm  shivaji_nagar
# 2025-02-01      62.0     52.0       46.0      46.0             47.0           60.0
# 2025-03-01      56.0     37.0       36.0      45.0             40.0           45.0
# 2025-04-01      33.0     22.0       26.0      33.0             21.0           31.0
# 2025-05-01      34.0     18.0       14.0      26.0             19.0           31.0
# 2025-06-01      25.0     12.0       16.0      16.0             11.0           25.0
# 2025-07-01      23.0     11.0        7.0      16.0             10.0           19.0
# 2025-08-01      19.0     13.0        9.0      14.0             10.0           20.0
# 2025-09-01      21.0     18.0       12.0      16.0             13.0           23.0
# 2025-10-01      39.0     43.0       34.0      46.0             39.0           59.0
# 2025-11-01      54.0     47.0       52.0      63.0             64.0          110.0
# 2025-12-01      68.0     59.0       45.0      65.0             49.0           65.0
# 2026-01-01      41.0     57.0       52.0      56.0             48.0           40.0
# 2026-02-01      58.0     41.0       55.0      53.0             46.0           40.0
# 2026-03-01      36.0     27.0       38.0      28.0             24.0           34.0
# 2026-04-01      40.0     20.0       40.0      26.0             23.0           26.0
# 2026-05-01      24.0     21.0       25.0      13.0             14.0           17.0
# 2026-06-01      17.0     14.0       29.0      18.0             10.0           16.0
# 2026-07-01      18.0     13.0       12.0      15.0              9.0           14.0
# 2026-08-01      20.0     11.0       14.0      15.0              9.0           16.0
# 2026-09-01      19.0     12.0       25.0      18.0             10.0           20.0
# 2026-10-01      53.0     41.0       43.0      50.0             50.0           47.0
# 2026-11-01       NaN     24.0       25.0      40.0             39.0           38.0

# Missing runs (in days):Missing runs: how many gaps of 1 day, 2 to 3 days and 4 or more days each station has.
# bkc_mpcb | runs: 55 | 1 day: 27 | 2-3 days: 21 | 4+ days: 7 | longest: 11
# byculla | runs: 44 | 1 day: 20 | 2-3 days: 18 | 4+ days: 6 | longest: 11
# ghatkopar | runs: 42 | 1 day: 21 | 2-3 days: 14 | 4+ days: 7 | longest: 12
# kherwadi | runs: 44 | 1 day: 25 | 2-3 days: 16 | 4+ days: 3 | longest: 10
# malad_west_iitm | runs: 36 | 1 day: 24 | 2-3 days: 8 | 4+ days: 4 | longest: 11
# shivaji_nagar | runs: 40 | 1 day: 18 | 2-3 days: 17 | 4+ days: 5 | longest: 13
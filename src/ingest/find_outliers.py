import pandas as pd

df = pd.read_csv("data/clean/daily_long.csv", parse_dates=["date_ist"])
pm = df[(df["variable"] == "pm25") & (df["usable"])]

print("15 highest daily PM2.5 values:")
print(pm.sort_values("value", ascending=False).head(15)[["station", "date_ist", "value", "coverage_pct"]])

print("\nSpread per station:")
print(pm.groupby("station")["value"].describe().round(1))

# 8998         bkc_mpcb 2026-05-02  74500.0          75.0
# 8997         bkc_mpcb 2026-05-01  57300.0         100.0
# 8847         bkc_mpcb 2025-11-22  12400.0         100.0
# 8846         bkc_mpcb 2025-11-21   6750.0          96.0
# 8991         bkc_mpcb 2026-04-25    574.0          96.0
# 1675         kherwadi 2025-11-24    529.0         100.0
# 8992         bkc_mpcb 2026-04-26    528.0          96.0
# 7210          byculla 2026-05-09    319.0         100.0
# 3489    shivaji_nagar 2025-11-21    228.0         100.0
# 3456    shivaji_nagar 2025-10-19    226.0         100.0
# 241   malad_west_iitm 2025-10-21    185.0         100.0
# 3495    shivaji_nagar 2025-11-27    181.0         100.0
# 8857         bkc_mpcb 2025-12-02    177.0         100.0
# 3491    shivaji_nagar 2025-11-23    172.0          92.0
# 3487    shivaji_nagar 2025-11-19    168.0         100.0

# Spread per station:
#                  count   mean     std  min   25%   50%   75%      max
# station                                                              
# bkc_mpcb         515.0  330.0  4179.4  0.0  19.8  28.8  48.4  74500.0
# byculla          517.0   26.6    23.8  3.5  12.0  17.6  35.1    319.0
# ghatkopar        523.0   29.3    18.9  0.0  13.0  23.6  43.7     96.0
# kherwadi         544.0   32.1    30.8  5.0  14.2  21.5  44.2    529.0
# malad_west_iitm  557.0   25.6    23.0  0.0   9.1  16.5  36.8    185.0
# shivaji_nagar    535.0   34.7    30.7  0.0  16.8  24.2  41.5    228.0


# 1 and 2 May 2026: 57,300 and 74,500 µg/m³.
# 21 and 22 Nov 2025: 6,750 and 12,400 µg/m³.
# Those values are not physically possible.
# Both runs also had full coverage (96 to 100%),
# so the coverage flag let them through.
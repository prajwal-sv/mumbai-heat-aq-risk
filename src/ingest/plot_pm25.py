import pandas as pd
import plotly.express as px

df = pd.read_csv("data/clean/daily_long.csv", parse_dates=["date_ist"])
pm = df[(df["variable"] == "pm25") & (df["usable"])]

# One column per station, one row per day. Missing days stay empty (NaN).
wide = pm.pivot(index="date_ist", columns="station", values="value")
wide = wide.reindex(pd.date_range(wide.index.min(), wide.index.max()))

fig = px.line(wide, title="Daily PM2.5 by station (IST days, usable days only)")
fig.write_html("notebooks/pm25_daily.html")

print(wide.resample("MS").mean().round(0))


#  src\ingest\plot_pm25.py
# station     bkc_mpcb  byculla  ghatkopar  kherwadi  malad_west_iitm  shivaji_nagar
# 2025-02-01      62.0     52.0       46.0      46.0             47.0           60.0
# 2025-03-01      56.0     37.0       36.0      45.0             40.0           45.0
# 2025-04-01      33.0     22.0       26.0      33.0             21.0           17.0
# 2025-05-01      34.0     18.0       14.0      26.0             19.0           29.0
# 2025-06-01      25.0     12.0       15.0      16.0             11.0           25.0
# 2025-07-01      23.0     11.0        7.0      16.0             10.0           19.0
# 2025-08-01      19.0     13.0        9.0      14.0             10.0           20.0
# 2025-09-01      21.0     18.0       12.0      16.0             13.0           23.0
# 2025-10-01      39.0     43.0       34.0      46.0             39.0           59.0
# 2025-11-01     734.0     47.0       52.0      79.0             64.0          110.0
# 2025-12-01      68.0     59.0       45.0      65.0             49.0           65.0
# 2026-01-01      41.0     57.0       52.0      56.0             48.0           40.0
# 2026-02-01      58.0     41.0       55.0      53.0             46.0           40.0
# 2026-03-01      36.0     27.0       38.0      28.0             24.0           34.0
# 2026-04-01      76.0     20.0       40.0      26.0             23.0           26.0
# 2026-05-01    4567.0     31.0       25.0      13.0             13.0           17.0
# 2026-06-01      17.0     14.0       29.0      18.0             10.0           16.0
# 2026-07-01      18.0     13.0       12.0      15.0              9.0           14.0
# 2026-08-01      20.0     11.0       14.0      15.0              9.0           16.0
# 2026-09-01      19.0     12.0       25.0      18.0             10.0           20.0
# 2026-10-01      53.0     41.0       43.0      50.0             50.0           47.0
# 2026-11-01       NaN     24.0       25.0      40.0             39.0           38.0
import numpy as np
import pandas as pd

FILE = "data/clean/daily_clean_final.csv"   # change if you saved under another name
TEST_START = "2026-07-01"

df = pd.read_csv(FILE, parse_dates=["date_ist"])
pm = df[df["variable"] == "pm25"].pivot(index="date_ist", columns="station", values="clean_value")
pm = pm.reindex(pd.date_range(pm.index.min(), pm.index.max()))   # every calendar day

rows = []
for station in pm.columns:
    both = pd.DataFrame({"today": pm[station], "tomorrow": pm[station].shift(-1)}).dropna()
    for label, part in [("all days", both), ("test period", both[both.index >= TEST_START])]:
        err = part["tomorrow"] - part["today"]
        rows.append({"station": station, "period": label, "days": len(part),
                     "MAE": err.abs().mean(), "RMSE": np.sqrt((err ** 2).mean())})

print(pd.DataFrame(rows).round(1).to_string(index=False))


#       station      period  days  MAE  RMSE
#        bkc_mpcb    all days   453  7.7  12.0
#        bkc_mpcb test period    78  4.2   5.5
#         byculla    all days   472  5.6   9.3
#         byculla test period   105  2.9   5.1
#       ghatkopar    all days   480  5.5   8.5
#       ghatkopar test period    85  4.2   6.1
#        kherwadi    all days   499  6.9  10.9
#        kherwadi test period    97  4.2   6.5
# malad_west_iitm    all days   519  6.8  12.3
# malad_west_iitm test period   100  3.2   4.7
#   shivaji_nagar    all days   482  9.0  17.1
#   shivaji_nagar test period    99  3.3   4.4
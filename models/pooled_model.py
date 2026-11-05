import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Step 1: read the cleaned data, one column per station, every calendar day
df = pd.read_csv("data/clean/daily_clean_final.csv", parse_dates=["date_ist"])
pm = df[df["variable"] == "pm25"].pivot(index="date_ist", columns="station", values="clean_value")
pm = pm.reindex(pd.date_range(pm.index.min(), pm.index.max()))

# Step 2: build the same inputs for each station, then stack them into one table
parts = []
for station in pm.columns:
    s = pm[station]
    d = pd.DataFrame({
        "today": s,
        "yesterday": s.shift(1),
        "mean_7d": s.rolling(7, min_periods=4).mean(),
        "tomorrow": s.shift(-1),
    }).dropna()
    d["station"] = station
    parts.append(d)
data = pd.concat(parts)

# Step 3: split by time (same dates as before)
train = data[data.index <= "2026-06-29"]
test = data[data.index >= "2026-07-01"]
inputs = ["today", "yesterday", "mean_7d"]

def miss(actual, predicted):
    error = actual - predicted
    return round(float(error.abs().mean()), 1), round(float(np.sqrt((error ** 2).mean())), 1)

# Step 4: one model for all stations
lin = LinearRegression().fit(train[inputs], train["tomorrow"])
rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(train[inputs], train["tomorrow"])
test = test.assign(lin=lin.predict(test[inputs]), rf=rf.predict(test[inputs]))

print("train rows:", len(train), "| test rows:", len(test))
print("ALL STATIONS  baseline:", miss(test["tomorrow"], test["today"]),
      "| linear:", miss(test["tomorrow"], test["lin"]),
      "| forest:", miss(test["tomorrow"], test["rf"]))

# Step 5: the same scores, station by station (MAE, RMSE)
for station in pm.columns:
    t = test[test["station"] == station]
    print(station, "| baseline:", miss(t["tomorrow"], t["today"]),
          "| linear:", miss(t["tomorrow"], t["lin"]),
          "| forest:", miss(t["tomorrow"], t["rf"]))


import os
rows = []
for station in pm.columns:
    t = test[test["station"] == station]
    for name, predicted in [("baseline", t["today"]), ("linear", t["lin"]), ("forest", t["rf"])]:
        mae, rmse = miss(t["tomorrow"], predicted)
        rows.append({"station": station, "model": name, "test_days": len(t), "MAE": mae, "RMSE": rmse})
os.makedirs("models_saved", exist_ok=True)
pd.DataFrame(rows).to_csv("models_saved/model_comparison.csv", index=False)
print("Saved models_saved/model_comparison.csv")


# bkc_mpcb | baseline: (4.0, 5.2) | linear: (4.0, 5.3) | forest: (4.7, 6.5)
# byculla | baseline: (2.9, 5.1) | linear: (3.3, 5.3) | forest: (3.3, 5.6)
# ghatkopar | baseline: (4.7, 6.6) | linear: (4.8, 6.5) | forest: (5.4, 7.5)
# kherwadi | baseline: (4.3, 6.7) | linear: (4.3, 6.6) | forest: (5.2, 8.5)
# malad_west_iitm | baseline: (3.3, 4.9) | linear: (3.6, 5.3) | forest: (3.7, 5.3)
# shivaji_nagar | baseline: (3.3, 4.5) | linear: (3.5, 4.7) | forest: (4.1, 5.4)

    
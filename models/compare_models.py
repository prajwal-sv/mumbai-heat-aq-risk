import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Step 1: read the cleaned data, one column per station, every calendar day
df = pd.read_csv("data/clean/daily_clean_final.csv", parse_dates=["date_ist"])
pm = df[df["variable"] == "pm25"].pivot(index="date_ist", columns="station", values="clean_value")
pm = pm.reindex(pd.date_range(pm.index.min(), pm.index.max()))

# Step 2: a small helper that measures the average miss (MAE) and big-miss score (RMSE)
def miss(actual, predicted):
    error = actual - predicted
    return round(error.abs().mean(), 1), round(np.sqrt((error ** 2).mean()), 1)

# Step 3: for each station, build inputs, split by time, and compare three forecasts
for station in pm.columns:
    s = pm[station]
    d = pd.DataFrame({
        "today": s,
        "yesterday": s.shift(1),
        "mean_7d": s.rolling(7, min_periods=4).mean(),
        "tomorrow": s.shift(-1),
    }).dropna()

    train = d[d.index <= "2026-06-29"]   # the past
    test = d[d.index >= "2026-07-01"]    # the future
    inputs = ["today", "yesterday", "mean_7d"]

    print(station, "| train days:", len(train), "| test days:", len(test))
    print("  baseline          MAE, RMSE:", miss(test["tomorrow"], test["today"]))

    lin = LinearRegression().fit(train[inputs], train["tomorrow"])
    print("  linear regression MAE, RMSE:", miss(test["tomorrow"], lin.predict(test[inputs])))

    rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(train[inputs], train["tomorrow"])
    print("  random forest     MAE, RMSE:", miss(test["tomorrow"], rf.predict(test[inputs])))


#     bkc_mpcb | train days: 329 | test days: 63
#   baseline          MAE, RMSE: (np.float64(4.0), np.float64(5.2))
#   linear regression MAE, RMSE: (np.float64(4.2), np.float64(5.4))
#   random forest     MAE, RMSE: (np.float64(5.5), np.float64(7.5))
# byculla | train days: 324 | test days: 97
#   baseline          MAE, RMSE: (np.float64(2.9), np.float64(5.1))
#   linear regression MAE, RMSE: (np.float64(2.9), np.float64(5.1))
#   random forest     MAE, RMSE: (np.float64(3.6), np.float64(5.8))
# ghatkopar | train days: 356 | test days: 69
#   baseline          MAE, RMSE: (np.float64(4.7), np.float64(6.6))
#   linear regression MAE, RMSE: (np.float64(4.8), np.float64(6.5))
#   random forest     MAE, RMSE: (np.float64(5.1), np.float64(6.9))
# kherwadi | train days: 361 | test days: 86
#   baseline          MAE, RMSE: (np.float64(4.3), np.float64(6.7))
#   linear regression MAE, RMSE: (np.float64(4.2), np.float64(6.5))
#   random forest     MAE, RMSE: (np.float64(4.9), np.float64(7.6))
# malad_west_iitm | train days: 389 | test days: 88
#   baseline          MAE, RMSE: (np.float64(3.3), np.float64(4.9))
#   linear regression MAE, RMSE: (np.float64(3.6), np.float64(5.4))
#   random forest     MAE, RMSE: (np.float64(4.1), np.float64(5.6))
# shivaji_nagar | train days: 344 | test days: 87
#   baseline          MAE, RMSE: (np.float64(3.3), np.float64(4.5))
#   linear regression MAE, RMSE: (np.float64(3.7), np.float64(4.9))
#   random forest     MAE, RMSE: (np.float64(4.3), np.float64(5.7))


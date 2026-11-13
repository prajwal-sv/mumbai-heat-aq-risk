import pandas as pd

df = pd.read_csv("data/clean/daily_clean_final.csv", parse_dates=["date_ist"])
flag = df[df["suspect"]]

print("Flags by variable and reason:")
print(flag.groupby(["variable", "reason"]).size())

print("\nStations with the most flags:")
print(flag.groupby(["station", "variable"]).size().sort_values(ascending=False).head(12))

m = df[(df["station"] == "loc12040") & (df["variable"] == "pm10")]
print("\nMulund West PM10 values:")
print(m["value"].describe().round(1))
print(m[m["suspect"]]["reason"].value_counts())

pm = df[df["variable"] == "pm25"].pivot(index="date_ist", columns="station", values="clean_value")
print("\nCity-wide median PM2.5 per day, from 1 Nov:")
print(pm.loc["2026-11-01":].median(axis=1).round(0))
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

st.title("Which inputs mattered?")
st.warning("Neither model beat the baseline (see the Forecast page). This page shows what the models "
           "learned. It is not a recommended forecast.")

INPUTS = ["today", "yesterday", "mean_7d"]
NAMES = {"today": "Today's value", "yesterday": "Yesterday's value", "mean_7d": "Average of the last 7 days"}

@st.cache_data
def fit():
    df = pd.read_csv("data/clean/daily_clean_final.csv", parse_dates=["date_ist"])
    pm = df[df["variable"] == "pm25"].pivot(index="date_ist", columns="station", values="clean_value")
    pm = pm.reindex(pd.date_range(pm.index.min(), pm.index.max()))
    parts = []
    for station in pm.columns:
        s = pm[station]
        parts.append(pd.DataFrame({
            "today": s, "yesterday": s.shift(1),
            "mean_7d": s.rolling(7, min_periods=4).mean(), "tomorrow": s.shift(-1),
        }).dropna())
    data = pd.concat(parts)
    train = data[data.index <= "2026-06-29"]          # same training days as the comparison
    lin = LinearRegression().fit(train[INPUTS], train["tomorrow"])
    rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(train[INPUTS], train["tomorrow"])
    table = pd.DataFrame({
        "Input": [NAMES[i] for i in INPUTS],
        "Linear Regression weight": lin.coef_.round(2),
        "Random Forest importance": rf.feature_importances_.round(2),
    })
    return table, len(train), train[INPUTS].corr().round(2).rename(index=NAMES, columns=NAMES)

table, n, corr = fit()
st.dataframe(table, hide_index=True, use_container_width=True)
top = table.sort_values("Random Forest importance", ascending=False).iloc[0]["Input"]
st.write(f"The Random Forest relied most on: **{top}**.")
st.caption(f"Trained on {n} station-days up to 29 Jun 2026, all six stations pooled | Source: OpenAQ daily data after cleaning")

st.subheader("How to read this")
st.markdown("""
- **Linear Regression weight:** how many µg/m³ tomorrow's forecast moves when this input is 1 µg/m³ higher,
  with the other inputs held the same.
- **Random Forest importance:** the share of the forest's decisions that used this input. The shares add up to 1.
""")

st.subheader("Why you should be careful")
st.markdown("""
- The three inputs overlap a lot: the 7-day average contains today's and yesterday's values. When inputs overlap,
  the split of credit between them is unreliable, so a small weight does not mean an input is useless.
- These models did not beat "tomorrow = today". What they learned is not a reason to trust them.
- This shows which inputs the models used. It does not show what causes PM2.5. Correlation is not causation.
""")

st.subheader("How much the inputs overlap (correlation, 1 = move together)")
st.dataframe(corr, use_container_width=True)
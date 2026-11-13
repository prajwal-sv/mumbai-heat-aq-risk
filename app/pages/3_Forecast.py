import os
import pandas as pd
import json
import streamlit as st

FILE = "models_saved/model_comparison.csv"
NAMES = {"baseline": "Baseline (tomorrow = today)", "linear": "Linear Regression", "forest": "Random Forest"}

st.title("Forecast: next-day PM2.5")
st.caption("Question: can we predict tomorrow's daily average PM2.5 (IST day) better than simply copying today's value?")

if not os.path.exists(FILE):
    st.warning("The comparison table is missing. Run models\\pooled_model.py with the save lines first.")
    st.stop()

t = pd.read_csv(FILE)
with open("data/clean/stations_config.json", encoding="utf-8") as f:
    names = {k: c["name"] for k, c in json.load(f).items()}
t["station"] = t["station"].map(names)
mae = t.pivot(index="station", columns="model", values="MAE")
rmse = t.pivot(index="station", columns="model", values="RMSE")

# A model beats the baseline only if it is lower on BOTH MAE and RMSE
winners = [(s, m) for s in mae.index for m in ["linear", "forest"]
           if mae.loc[s, m] < mae.loc[s, "baseline"] and rmse.loc[s, m] < rmse.loc[s, "baseline"]]

if not winners:
    st.error("No forecast is shown. Neither model beat the baseline at any station.")
else:
    st.info("A model beat the baseline at: " + ", ".join(f"{s} ({NAMES[m]})" for s, m in winners)
            + ". This is one test period only, so we do not show a forecast until it is checked on another.")

st.subheader("Model comparison (lower is better)")
table = t.copy()
table["model"] = table["model"].map(NAMES)
st.dataframe(table.rename(columns={"station": "Station", "model": "Model", "test_days": "Test days",
                                   "MAE": "MAE (µg/m³)", "RMSE": "RMSE (µg/m³)"}),
             hide_index=True, use_container_width=True)

st.caption("Historical evaluation, not live | Test period: 1 Jul 2026 to early Nov 2026 | "
           "Data: OpenAQ daily summaries after our cleaning | Models trained on the past and tested on the future.")

st.subheader("How to read this")
st.markdown("""
- **MAE** is the average miss in µg/m³. **RMSE** is similar, but big misses count more.
- **Baseline** means "tomorrow will be the same as today". Any model must beat it to be worth showing.
- Inputs: today's value, yesterday's value, and the average of the last 7 days. No future data is used.
""")

st.subheader("Why no forecast, and what we do not know")
st.markdown("""
These are our best guesses. We have not tested them.
- PM2.5 changes slowly from one day to the next, so copying today is already a strong forecast.
- The test period is mostly monsoon, when PM2.5 is low and smooth. It contains no winter.
- We have about 20 months of data and some gaps, which is little for a model to learn from.
""")

st.subheader("Limitations")
st.markdown("""
- The result applies to this test period only. It says nothing about winter.
- Each station is one sensor at one spot. It does not describe a whole neighborhood.
- Patterns a model finds show a link between inputs and PM2.5. They do not show a cause.
- We show no prediction range, because with this little data we cannot estimate one reliably.
""")
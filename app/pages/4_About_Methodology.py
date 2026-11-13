import pandas as pd
import streamlit as st

st.title("About & Methodology")

st.header("What this app does")
st.markdown("""
Shows PM2.5, PM10 and temperature from six monitoring stations in Mumbai, with charts, a map, and a test of
whether a simple model can forecast next-day PM2.5. Every card and chart shows its source and how fresh it is.
""")

st.header("Data sources")
st.markdown("""
- **OpenAQ (API v3):** latest readings and daily summaries. OpenAQ collects the data from station operators:
  MPCB, BMC and IITM for the six stations used here. Free tier: 60 requests per minute.
- **Not used yet:** NASA POWER (weather, delayed 2 to 7 days), CPCB, IMD and Open-Meteo.
- **Data licences:** still to be checked before this project is published. They are not stated here.
- **Stations used:** Kherwadi (MPCB), Shivaji Nagar (BMC), Ghatkopar (BMC), Byculla (BMC),
  Bandra Kurla Complex (MPCB) and Malad West (IITM). We started from 44 stations near Mumbai and kept
  these six because their PM2.5 data was among the most complete.
- **Not used:** older sensors from 2019 to 2022. They stop in 2022 and the new ones start in February 2025,
  so there is a gap of about two years.
- **Period:** daily data from 19 Feb 2025 to early Nov 2026, about 20 months.

- **Credit:** data come from OpenAQ and the original station operators (MPCB, BMC, IITM). Each location's licence
  is set by its operator, and we credit both OpenAQ and the operators.
""")

st.header("Time and freshness")
st.markdown("""
- Times are stored in UTC and shown in IST (Asia/Kolkata). Daily values are IST calendar days.
- Freshness labels on cards: **Live** under 2 hours old, **Delayed** 2 to 48 hours, **Historical** older than 48 hours.
  These cut-offs are our own choice, not an official rule.
- Charts use daily history, so they are labeled Historical.
""")

st.header("How we cleaned the data")
st.markdown("""
Raw downloads are kept untouched. Nothing is deleted, and **nothing is filled in**. A day is left blank if:
- fewer than 75% of its readings exist,
- PM is zero or below, above 1,000 µg/m³, or more than 5 times the same-day median of all stations and above 200,
- temperature is below 10 °C or above 45 °C, or more than 8 °C from the same-day median of the stations.

All of these limits are our own choices, not official rules. They catch obvious faults, but not every bad value.
Blank days appear as breaks in the charts.
""")

df = pd.read_csv("data/clean/daily_clean_final.csv")
flagged = df[df["suspect"]]
counts = flagged.groupby(["station", "variable", "reason"]).size().reset_index(name="days flagged")
st.subheader("Days we flagged and blanked")
st.dataframe(counts, hide_index=True, use_container_width=True)
st.caption("Read live from the cleaned data file.")

st.markdown("""
**Problems we found:**
- Malad West's temperature sensor reports exactly 0.0, so all its temperature data is excluded.
- Shivaji Nagar's PM sensors reported zeros for 13 days in a row in April and May 2025.
- Bandra Kurla Complex (MPCB) reported impossible PM values in late 2025 and spring 2026.

**Not explained, and left in the data:**
- Shivaji Nagar's November 2025 PM2.5 is much higher than at the other stations. It may be real or a sensor problem.
- Ghatkopar's temperature runs about 4 °C warmer than Byculla's. We did not adjust it.
- Some temperature values near 39 °C passed our checks but look high to us.
""")

st.header("Map colors")
st.markdown("""
Colors use the CPCB 24-hour category bands (2014 breakpoints, taken from a research paper that reproduces them, not from
CPCB's own page). We apply them to a single latest reading, so they are **indicative and not an official AQI**.
Gray means no valid reading in the last 48 hours. A dot is one sensor at one spot, not a whole neighborhood.
""")

st.header("Forecast method")
st.markdown("""
- **Target:** daily average PM2.5 (IST day). **Horizon:** the next day.
- **Baseline:** tomorrow equals today. **Models:** Linear Regression and Random Forest, with a fixed random seed (42).
- **Inputs:** today's value, yesterday's value and the average of the last 7 days.
- **Split by time:** trained on days up to 29 June 2026, tested from 1 July 2026. No random splits.
- **Avoiding data leakage:** a forecast uses only data up to its own day. Gaps are not filled, because filling would use
  values from after the gap. All forecasts are scored on exactly the same test days.
- **Result:** no model beat the baseline. See the Forecast page for the table.
""")

st.header("Limitations")
st.markdown("""
- About 20 months of data and only one winter.
- The test period (July to early November 2026) is mostly monsoon and contains no winter.
- The 1 July split date is our own choice, and we did not try other dates.
- Six stations are not the whole city.
- Model patterns show links, not causes. Correlation is not causation.
- Not built yet: the question-and-answer assistant and the risk indicator.
""")
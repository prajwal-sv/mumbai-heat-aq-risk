import os
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
try:
    KEY = st.secrets["OPENAQ_API_KEY"]
except Exception:
    KEY = os.getenv("OPENAQ_API_KEY")

# name: (operator, {variable: sensor id})
STATIONS = {
    "Kherwadi, Bandra East": ("MPCB", {"pm25": 12238411, "pm10": 12238410, "temperature": 12238414}),
    "Shivaji Nagar": ("BMC", {"pm25": 12238576, "pm10": 12238575, "temperature": 12238579}),
    "Ghatkopar": ("BMC", {"pm25": 12238603, "pm10": 12238602, "temperature": 12238606}),
    "Byculla": ("BMC", {"pm25": 12238567, "pm10": 12238566, "temperature": 12238570}),
    "Bandra Kurla Complex": ("MPCB", {"pm25": 12238375, "pm10": 12238374, "temperature": 12238378}),
    "Malad West": ("IITM", {"pm25": 12236426, "pm10": 12236425, "temperature": 12236429}),
}
LABELS = {"pm25": "PM2.5", "pm10": "PM10", "temperature": "Temperature"}
UNITS = {"pm25": "µg/m³", "pm10": "µg/m³", "temperature": "°C"}

@st.cache_data(ttl=300)   # reuse the answer for 5 minutes
def get_readings(sensor_id):
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=48)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    r = requests.get(f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements",
                     params={"datetime_from": start.strftime(fmt), "datetime_to": end.strftime(fmt), "limit": 1000},
                     headers={"X-API-Key": KEY}, timeout=30)
    r.raise_for_status()
    return [(x["period"]["datetimeFrom"]["utc"], x["value"]) for x in r.json()["results"]]

def is_valid(variable, value):
    if variable == "temperature":
        return 10 <= value <= 45
    return 0 < value <= 1000

st.title("Last 48 hours")
name = st.selectbox("Station", list(STATIONS))
variable = st.selectbox("Variable", list(LABELS), format_func=lambda v: LABELS[v])
operator, sensors = STATIONS[name]

rows = get_readings(sensors[variable])
if not rows:
    st.warning("No readings in the last 48 hours for this station and variable.")
    st.stop()

s = pd.Series([v for _, v in rows], index=pd.to_datetime([t for t, _ in rows], utc=True)).sort_index()
s.index = s.index.tz_convert("Asia/Kolkata")
bad = int((~s.apply(lambda v: is_valid(variable, v))).sum())
s = s[s.apply(lambda v: is_valid(variable, v))]
if s.empty:
    st.warning("No valid readings in the last 48 hours for this station and variable.")
    st.stop()

s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="15min"))   # gaps stay empty

fig = px.line(x=s.index, y=s.values, labels={"x": "Time (IST)", "y": UNITS[variable]})
fig.update_layout(title=f"{LABELS[variable]} at {name} (15-minute readings)")
st.plotly_chart(fig, use_container_width=True)

latest = s.dropna().index.max()
age = (datetime.now(timezone.utc) - latest.tz_convert("UTC")).total_seconds() / 3600
label = "Live" if age < 2 else "Delayed" if age < 48 else "Historical"
st.caption(f"{label} | newest point: {latest:%d %b %Y, %H:%M IST} | Source: OpenAQ, station operator {operator}")
st.caption(f"Each point is a 15-minute period, shown at its start. {bad} reading(s) failed our checks and were left out. "
           "Gaps are not filled.")
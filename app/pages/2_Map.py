import json
import os
import requests
import folium
import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from streamlit_folium import st_folium

load_dotenv()
try:
    KEY = st.secrets["OPENAQ_API_KEY"]
except Exception:
    KEY = os.getenv("OPENAQ_API_KEY")

with open("data/clean/stations_config.json", encoding="utf-8") as f:
    CONFIG = json.load(f)
STATIONS = {c["name"]: (c["location_id"], c["operator"], {v: k for k, v in c["sensors"].items()})
            for c in CONFIG.values()}
POSITIONS = {c["location_id"]: (c["lat"], c["lon"]) for c in CONFIG.values()}
LABELS = {"pm25": "PM2.5", "pm10": "PM10", "temperature": "Temperature"}
UNITS = {"pm25": "µg/m³", "pm10": "µg/m³", "temperature": "°C"}

# CPCB 24-hour upper limits for the first five categories
BANDS = {"pm25": [30, 60, 90, 120, 250], "pm10": [50, 100, 250, 350, 430]}
NAMES = ["Good", "Satisfactory", "Moderate", "Poor", "Very poor", "Severe"]
COLORS = ["#2e7d32", "#9ccc65", "#fbc02d", "#fb8c00", "#e53935", "#7b1fa2"]
GRAY, BLUE = "#9e9e9e", "#1e88e5"

@st.cache_data(ttl=300)
def get_latest(location_id):
    r = requests.get(f"https://api.openaq.org/v3/locations/{location_id}/latest",
                     headers={"X-API-Key": KEY}, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

def is_valid(variable, value):
    if variable == "temperature":
        return 10 <= value <= 45
    return 0 < value <= 1000

def category(variable, value):
    for i, limit in enumerate(BANDS[variable]):
        if value <= limit:
            return i
    return 5

st.title("Station map")
variable = st.selectbox("Show", list(LABELS), format_func=lambda v: LABELS[v])
now = datetime.now(timezone.utc)

m = folium.Map(location=[19.076, 72.8777], zoom_start=11)

for name, (location_id, operator, sensors) in STATIONS.items():
    lat, lon = POSITIONS[location_id]
    try:
        latest = get_latest(location_id)
    except Exception:
        latest = []
    item = next((x for x in latest if sensors.get(x["sensorsId"]) == variable), None)

    color, text = GRAY, "No recent valid reading"
    if item is not None:
        when = datetime.fromisoformat(item["datetime"]["utc"].replace("Z", "+00:00"))
        age = (now - when).total_seconds() / 3600
        when_ist = when.astimezone(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %H:%M IST")
        if age < 48 and is_valid(variable, item["value"]):
            value = item["value"]
            color = BLUE if variable == "temperature" else COLORS[category(variable, value)]
            band = "" if variable == "temperature" else f"<br>Band: {NAMES[category(variable, value)]}"
            text = (f"{LABELS[variable]}: {value:.1f} {UNITS[variable]}{band}"
                    f"<br>Time: {when_ist}<br>Measured (sensor reading)")

    popup = folium.Popup(f"<b>{name}</b><br>Operator: {operator}<br>{text}", max_width=260)
    folium.CircleMarker([lat, lon], radius=11, color="black", weight=1,
                        fill=True, fill_color=color, fill_opacity=0.9, popup=popup).add_to(m)

st_folium(m, height=500, use_container_width=True)

if variable == "temperature":
    st.markdown(f"<span style='color:{BLUE}'>●</span> Valid reading &nbsp; "
                f"<span style='color:{GRAY}'>●</span> No recent valid reading", unsafe_allow_html=True)
else:
    items = [f"<span style='color:{c}'>●</span> {n}" for c, n in zip(COLORS, NAMES)]
    items.append(f"<span style='color:{GRAY}'>●</span> No recent valid reading")
    st.markdown(" &nbsp; ".join(items), unsafe_allow_html=True)

st.caption("Live or delayed | latest readings, each popup shows its time | Source: OpenAQ")
st.caption("Each dot is one sensor at one spot. It does not describe the whole neighborhood.")
st.caption("Gray means no valid reading in the last 48 hours, or that OpenAQ did not answer.")
if variable != "temperature":
    st.caption("Colors use CPCB's 24-hour category bands on a single latest reading, so they are "
               "indicative only and not an official AQI.")
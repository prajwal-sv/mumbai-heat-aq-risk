import os
import requests
import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
try:
    KEY = st.secrets["OPENAQ_API_KEY"]
except Exception:
    KEY = os.getenv("OPENAQ_API_KEY")

# station name: (location id, operator, {sensor id: variable})
STATIONS = {
    "Kherwadi, Bandra East": (3409486, "MPCB", {12238411: "pm25", 12238410: "pm10", 12238414: "temperature"}),
    "Shivaji Nagar": (3409511, "BMC", {12238576: "pm25", 12238575: "pm10", 12238579: "temperature"}),
    "Ghatkopar": (3409514, "BMC", {12238603: "pm25", 12238602: "pm10", 12238606: "temperature"}),
    "Byculla": (3409510, "BMC", {12238567: "pm25", 12238566: "pm10", 12238570: "temperature"}),
    "Bandra Kurla Complex": (3409482, "MPCB", {12238375: "pm25", 12238374: "pm10", 12238378: "temperature"}),
    "Malad West": (11611, "IITM", {12236426: "pm25", 12236425: "pm10", 12236429: "temperature"}),
}
LABELS = {"pm25": "PM2.5", "pm10": "PM10", "temperature": "Temperature"}
UNITS = {"pm25": "µg/m³", "pm10": "µg/m³", "temperature": "°C"}

@st.cache_data(ttl=300)   # reuse the answer for 5 minutes, so we stay under the rate limit
def get_latest(location_id):
    r = requests.get(f"https://api.openaq.org/v3/locations/{location_id}/latest",
                     headers={"X-API-Key": KEY}, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

def is_valid(variable, value):
    if variable == "temperature":
        return 10 <= value <= 45
    return 0 < value <= 1000

def freshness(age_hours):
    if age_hours < 2:
        return "Live"
    if age_hours < 48:
        return "Delayed"
    return "Historical"

st.title("Mumbai air quality and temperature")
name = st.selectbox("Station", list(STATIONS))
location_id, operator, sensors = STATIONS[name]
try:
    results = get_latest(location_id)
except Exception:
    st.error("OpenAQ did not answer, possibly because of its rate limit. Try again in a minute.")
    st.stop()
now = datetime.now(timezone.utc)

for col, variable in zip(st.columns(3), ["pm25", "pm10", "temperature"]):
    item = next((x for x in results if sensors.get(x["sensorsId"]) == variable), None)
    with col:
        st.subheader(LABELS[variable])
        if item is None:
            st.write("No data")
            continue
        when = datetime.fromisoformat(item["datetime"]["utc"].replace("Z", "+00:00"))
        age = (now - when).total_seconds() / 3600
        when_ist = when.astimezone(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %H:%M IST")
        if is_valid(variable, item["value"]):
            st.metric("Latest reading", f"{item['value']:.1f} {UNITS[variable]}")
        else:
            st.metric("Latest reading", "No valid reading")
        st.caption(f"{freshness(age)} | reading time: {when_ist}")
        st.caption(f"Source: OpenAQ, station operator {operator}")
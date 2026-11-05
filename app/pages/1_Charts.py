import pandas as pd
import plotly.express as px
import streamlit as st

LABELS = {"pm25": "PM2.5", "pm10": "PM10", "temperature": "Temperature"}
UNITS = {"pm25": "µg/m³", "pm10": "µg/m³", "temperature": "°C"}
STATIONS = {
    "kherwadi": ("Kherwadi, Bandra East", "MPCB"),
    "shivaji_nagar": ("Shivaji Nagar", "BMC"),
    "ghatkopar": ("Ghatkopar", "BMC"),
    "byculla": ("Byculla", "BMC"),
    "bkc_mpcb": ("Bandra Kurla Complex", "MPCB"),
    "malad_west_iitm": ("Malad West", "IITM"),
}

def season(month):   # my own grouping, not an official definition
    if month in (12, 1, 2):
        return "Winter (Dec-Feb)"
    if month in (3, 4, 5):
        return "Summer (Mar-May)"
    if month in (6, 7, 8, 9):
        return "Monsoon (Jun-Sep)"
    return "Post-monsoon (Oct-Nov)"

@st.cache_data
def load():
    return pd.read_csv("data/clean/daily_clean_final.csv", parse_dates=["date_ist"])

df = load()
st.title("Charts")

variable = st.selectbox("Variable", list(LABELS), format_func=lambda v: LABELS[v])
station = st.selectbox("Station", list(STATIONS), format_func=lambda s: STATIONS[s][0])
view = st.radio("View", ["Daily", "Weekly average", "Monthly average", "By season"], horizontal=True)

rows = df[(df["variable"] == variable) & (df["station"] == station)]
daily = rows.set_index("date_ist")["clean_value"]
daily = daily.reindex(pd.date_range(daily.index.min(), daily.index.max()))   # every day, gaps stay empty

if daily.notna().sum() == 0:
    st.warning("No valid data for this station and variable.")
    st.stop()

if view == "Daily":
    data = daily
elif view == "Weekly average":
    data = daily.resample("W").mean()
elif view == "Monthly average":
    data = daily.resample("MS").mean()
else:
    by_season = daily.groupby(daily.index.month.map(season)).mean()
    data = by_season

if view == "By season":
    fig = px.bar(x=data.index, y=data.values, labels={"x": "Season", "y": UNITS[variable]})
else:
    fig = px.line(x=data.index, y=data.values, labels={"x": "Date (IST)", "y": UNITS[variable]})
fig.update_layout(title=f"{LABELS[variable]} at {STATIONS[station][0]} ({view.lower()})")
st.plotly_chart(fig, use_container_width=True)

last = daily.dropna().index.max()
st.caption(f"Historical | daily data up to {last:%d %b %Y} (IST days) | "
           f"Source: OpenAQ daily summaries, station operator {STATIONS[station][1]}")
st.caption("Days that failed our checks are left blank, not filled. Averages use only the days that passed.")
if view == "By season":
    st.caption("Seasons are my own grouping. Winter has less data than the others, so compare seasons with care.")
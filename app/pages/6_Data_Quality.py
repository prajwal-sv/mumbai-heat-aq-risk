import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache_data
def load():
    return pd.read_csv("data/clean/daily_clean_final.csv", parse_dates=["date_ist"])

df = load()
st.title("Data quality")

# One row per station and variable
s = df.groupby(["station", "variable"]).agg(
    first=("date_ist", "min"),
    last=("date_ist", "max"),
    rows=("date_ist", "count"),
    low_coverage=("usable", lambda x: int((~x).sum())),
    flagged=("suspect", "sum"),
    clean=("clean_value", "count"),
).reset_index()
s["calendar_days"] = (s["last"] - s["first"]).dt.days + 1
s["no_row"] = s["calendar_days"] - s["rows"]
s["clean_pct"] = (100 * s["clean"] / s["calendar_days"]).round(0)

fig = px.bar(s, x="station", y="clean_pct", color="variable", barmode="group",
             labels={"clean_pct": "Days with a clean value (%)", "station": "Station"})
fig.update_layout(title="Share of calendar days with a clean value")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Summary by station and variable")
st.dataframe(s.rename(columns={
    "first": "First day", "last": "Last day", "rows": "Days with a row",
    "low_coverage": "Low coverage (under 75%)", "flagged": "Flagged as suspect",
    "clean": "Clean days", "calendar_days": "Calendar days",
    "no_row": "Days with no row", "clean_pct": "Clean %"}),
    hide_index=True, use_container_width=True)
st.caption("A day can be both low coverage and flagged, so those two columns can overlap. "
           "Days with no row were never returned by OpenAQ.")

st.subheader("Every flagged day")
flagged = df[df["suspect"]].sort_values(["station", "variable", "date_ist"])
st.dataframe(flagged[["station", "variable", "date_ist", "value", "reason"]].assign(
    date_ist=flagged["date_ist"].dt.strftime("%d %b %Y")),
    hide_index=True, use_container_width=True)

st.caption("Historical | daily data, IST days | Source: OpenAQ daily summaries after our cleaning | "
           "Flagged days are blanked, never filled. The limits are our own choices.")
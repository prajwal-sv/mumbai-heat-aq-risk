"""Look closely at one saved hourly file: coverage and gaps. Changes nothing.
Run:  python -m src.inspect_raw 6956 pm25
(variable is pm25, pm10 or temperature)"""
import json
import sys

import pandas as pd

from src import config

IST = "Asia/Kolkata"


def latest_file(station_id, variable):
    files = [f for f in config.RAW_OPENAQ.glob(f"hours_station{station_id}_{variable}_*.json")
             if not f.name.endswith(".meta.json")]
    if not files:
        raise SystemExit("No saved file. Run first: python -m src.download_sample " + str(station_id))
    return sorted(files)[-1]


def load_hours(path):
    """Read the raw file into a small table, oldest hour first."""
    rows = json.loads(path.read_text(encoding="utf-8"))["results"]
    cov = [r.get("coverage") or {} for r in rows]
    table = pd.DataFrame({
        "start_utc": pd.to_datetime([r["period"]["datetimeFrom"]["utc"] for r in rows], utc=True),
        "value": [r.get("value") for r in rows],
        "readings": [c.get("observedCount") for c in cov],
        "expected": [c.get("expectedCount") for c in cov],
        "percent": [c.get("percentComplete") for c in cov],
    })
    return table.sort_values("start_utc").reset_index(drop=True)


def ist(ts):
    return ts.tz_convert(IST).strftime("%d %b %Y %H:%M")


def main(station_id, variable):
    path = latest_file(station_id, variable)
    t = load_hours(path)
    print(f"File: {path.name}")
    if t.empty:
        print("The file has no rows.")
        return
    first, last = t["start_utc"].iloc[0], t["start_utc"].iloc[-1]
    print(f"Rows: {len(t)}   Empty values: {t['value'].isna().sum()}   "
          f"Duplicate hours: {t['start_utc'].duplicated().sum()}")
    print(f"First hour starts: {first:%Y-%m-%d %H:%M} UTC = {ist(first)} IST")
    print(f"Last hour starts:  {last:%Y-%m-%d %H:%M} UTC = {ist(last)} IST")
    print(f"Minute of each hour's start (UTC): {t['start_utc'].dt.minute.value_counts().to_dict()}")

    print("\nHow many readings sit inside each hour (expected per hour:",
          t["expected"].mode().iloc[0], ")")
    print(t["readings"].value_counts().sort_index().to_string())

    full = pd.date_range(first, last, freq="1h")
    missing = pd.Series(full.difference(pd.DatetimeIndex(t["start_utc"])))
    span = len(full)
    print(f"\nHours with data: {len(t)} of {span} between first and last "
          f"({100 * len(t) / span:.1f}%). Missing hours: {len(missing)}")
    if len(missing):
        group = (missing.diff() != pd.Timedelta(hours=1)).cumsum()
        gaps = missing.groupby(group).agg(["min", "count"]).sort_values("count", ascending=False)
        print("Longest gaps (IST, hours long):")
        for _, g in gaps.head(10).iterrows():
            print(f"  from {ist(g['min'])}  ->  {g['count']} h")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python -m src.inspect_raw <station_id> <pm25|pm10|temperature>")
    main(int(sys.argv[1]), sys.argv[2])
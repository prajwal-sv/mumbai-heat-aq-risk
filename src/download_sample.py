"""Download ONE station's last 30 days of hourly data as a test.
Run:  python -m src.download_sample 6956
(6956 is just an example id. Pick any id from: python -m src.stations)"""
import json
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

from src import config, openaq, stations


def start_utc(row):
    """Find the row's start time. The field may sit at the top or inside 'period'."""
    top = (row.get("datetimeFrom") or {}).get("utc")
    inside = ((row.get("period") or {}).get("datetimeFrom") or {}).get("utc")
    return top or inside


def summarise(name, data):
    rows = data["results"]
    print(f"\n--- {name}: {len(rows)} rows from {data['pages']} request(s) ---")
    if not rows:
        print("No rows came back.")
        return
    empty = sum(1 for r in rows if r.get("value") is None)
    units = {(r.get("parameter") or {}).get("units") for r in rows}
    starts = sorted(s for s in (start_utc(r) for r in rows) if s)
    print(f"Empty values: {empty}")
    print(f"Units: {units}")
    if starts:
        print(f"First hour starts (UTC): {starts[0]}")
        print(f"Last hour starts (UTC):  {starts[-1]}")
    print("One raw row, exactly as received:")
    print(json.dumps(rows[0], indent=2))


def main(station_id):
    key = config.get_openaq_key()
    table = stations.mumbai_stations()
    match = table[table["id"] == station_id]
    if match.empty:
        raise SystemExit(f"Station {station_id} is not in the Mumbai-city list. "
                         "Run: python -m src.stations")
    row = match.iloc[0]
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=30)
    print(f"Station {station_id}: {row['name']}")
    print(f"Asking for hourly data from {start:%Y-%m-%d %H:%M} to {end:%Y-%m-%d %H:%M} UTC")

    for variable in stations.VARIABLES:
        sensor_id = row[f"{variable}_sensor"]
        if pd.isna(sensor_id):
            print(f"\n--- {variable}: this station has no such sensor ---")
            continue
        data, url = openaq.get_sensor_hours(key, int(sensor_id), start, end)
        note = (f"OpenAQ v3 sensors/{int(sensor_id)}/hours, station {station_id}, {variable}; "
                f"{data['pages']} page(s) merged into one list, rows untouched")
        openaq.save_raw(data, config.RAW_OPENAQ, f"hours_station{station_id}_{variable}", url, note)
        summarise(variable, data)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python -m src.download_sample <station_id>")
    main(int(sys.argv[1]))
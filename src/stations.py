"""Pick Mumbai-city stations from the saved OpenAQ station list.
Run to see the list:  python -m src.stations"""
import json

import pandas as pd

from src import config

VARIABLES = ["pm25", "pm10", "temperature"]


def latest_station_file():
    files = [f for f in config.RAW_OPENAQ.glob("locations_*.json")
             if not f.name.endswith(".meta.json")]
    if not files:
        raise SystemExit("No saved station list. Run first: python -m src.check_sources")
    return sorted(files)[-1]


def is_mumbai_city(name):
    """Keep 'Mumbai' stations, drop 'Navi Mumbai'. Thane etc. have no 'Mumbai' in the name."""
    return "Mumbai" in name and "Navi Mumbai" not in name


def mumbai_stations():
    data = json.loads(latest_station_file().read_text(encoding="utf-8"))
    rows = []
    for loc in data.get("results", []):
        name = loc.get("name") or ""
        if not is_mumbai_city(name):
            continue
        sensor_ids = {}
        for s in loc.get("sensors", []):
            p = s.get("parameter", {})
            if p.get("name") in VARIABLES:
                sensor_ids[p["name"]] = s.get("id")
        if not sensor_ids:
            continue
        rows.append({
            "id": loc.get("id"),
            "name": name,
            "provider": (loc.get("provider") or {}).get("name"),
            "first_utc": pd.to_datetime((loc.get("datetimeFirst") or {}).get("utc"), utc=True),
            "last_utc": pd.to_datetime((loc.get("datetimeLast") or {}).get("utc"), utc=True),
            "pm25_sensor": sensor_ids.get("pm25"),
            "pm10_sensor": sensor_ids.get("pm10"),
            "temperature_sensor": sensor_ids.get("temperature"),
        })
    if not rows:
        raise SystemExit("No Mumbai-city stations found in the saved list.")
    return pd.DataFrame(rows).sort_values("first_utc").reset_index(drop=True)


if __name__ == "__main__":
    table = mumbai_stations()
    table["first_utc"] = table["first_utc"].dt.date
    table["last_utc"] = table["last_utc"].dt.date
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    print(table.to_string(index=False))
    print(f"\n{len(table)} Mumbai-city stations (Navi Mumbai, Thane etc. left out)")
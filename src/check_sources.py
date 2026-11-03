"""Step 2 report: what data really exists for Mumbai?
Run from the project folder:  python -m src.check_sources
It only READS data and saves raw copies. It changes nothing else."""
import pandas as pd

from src import config, nasa_power, openaq

WANTED = ["pm25", "pm10", "temperature"]


def check_openaq(cfg):
    key = config.get_openaq_key()
    city = cfg["city"]
    data, url = openaq.get_locations(key, city["latitude"], city["longitude"])
    path = openaq.save_raw(data, config.RAW_OPENAQ, "locations", url,
                           "OpenAQ v3 /locations, stations within 25 km of Mumbai centre")
    results = data.get("results", [])
    found = data.get("meta", {}).get("found")
    print(f"\n=== OpenAQ: {len(results)} locations returned (API says found: {found}) ===")
    print(f"Raw copy saved: {path.name}\n")

    now = pd.Timestamp.now(tz="UTC")
    rows = []
    for loc in results:
        params = {}
        for s in loc.get("sensors", []):
            p = s.get("parameter", {})
            if p.get("name") in WANTED:
                params[p["name"]] = p.get("units")
        if not params:
            continue
        first = pd.to_datetime((loc.get("datetimeFirst") or {}).get("utc"), utc=True)
        last = pd.to_datetime((loc.get("datetimeLast") or {}).get("utc"), utc=True)
        rows.append({
            "id": loc.get("id"),
            "name": loc.get("name"),
            "provider": (loc.get("provider") or {}).get("name"),
            "has": ",".join(f"{k}({v})" for k, v in params.items()),
            "first_utc": first,
            "last_utc": last,
            "span_days": (last - first).days if pd.notna(first) and pd.notna(last) else None,
            "hours_since_last": round((now - last).total_seconds() / 3600, 1) if pd.notna(last) else None,
        })

    if not rows:
        print("No stations with PM2.5, PM10 or temperature were found.")
        return
    table = pd.DataFrame(rows).sort_values("span_days", ascending=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    print(table.to_string(index=False))

    pm25 = table[table["has"].str.contains("pm25")]
    print("\n--- Summary ---")
    print(f"Stations with PM2.5: {len(pm25)}")
    print(f"Stations with PM2.5 and span >= 365 days: {(pm25['span_days'] >= 365).sum()}")
    print(f"Stations with PM2.5 updated in the last 24 h: {(pm25['hours_since_last'] <= 24).sum()}")
    print("NOTE: span_days = first to last reading. It does NOT prove the data is complete.")
    print("We measure real gaps in Step 3.")


def check_nasa(cfg):
    city = cfg["city"]
    data, url = nasa_power.get_daily_sample(city["latitude"], city["longitude"], "20240101", "20240131")
    path = openaq.save_raw(data, config.RAW_NASA, "daily_sample", url,
                           "NASA POWER daily point, T2M and RH2M, Jan 2024 sample")
    print("\n=== NASA POWER sample ===")
    print(f"Raw copy saved: {path.name}")
    values = data.get("properties", {}).get("parameter", {})
    for name, series in values.items():
        missing = sum(1 for v in series.values() if v == -999)
        print(f"{name}: {len(series)} days, {missing} marked missing (-999)")
    print("Units reported by NASA:", data.get("parameters", {}))


if __name__ == "__main__":
    cfg = config.load_config()
    check_openaq(cfg)
    check_nasa(cfg)
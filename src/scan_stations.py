"""Scan every ACTIVE Mumbai-city station: how complete is each sensor over the last 24 months?
Uses DAILY values, so it is quick. It takes several minutes and prints progress.
Run:  python -m src.scan_stations"""
import gzip
import json
from datetime import datetime, timezone

import pandas as pd

from src import config, openaq, stations

ACTIVE_DAYS = 14    # a station counts as active if it reported in the last 14 days
WINDOW_DAYS = 730   # look back about 24 months


def day_text(row):
    """The row's day as text like 2026-10-07 (Indian local date if available)."""
    top = row.get("datetimeFrom") or {}
    inside = (row.get("period") or {}).get("datetimeFrom") or {}
    text = top.get("local") or inside.get("local") or top.get("utc") or inside.get("utc")
    return text[:10] if text else None


def summarise(rows, start, end):
    """Count the days that have data and the longest run of missing days."""
    window_days = (end.date() - start.date()).days + 1
    days = sorted({d for d in (day_text(r) for r in rows if r.get("value") is not None) if d})
    if not days:
        return {"first": None, "last": None, "days": 0, "pct_of_window": 0.0, "longest_gap_d": None}
    d = pd.Series(pd.to_datetime(days))
    return {
        "first": d.iloc[0].date(),
        "last": d.iloc[-1].date(),
        "days": len(d),
        "pct_of_window": round(100 * len(d) / window_days, 1),
        "longest_gap_d": int(d.diff().dt.days.fillna(1).sub(1).max()),
    }


def main():
    key = config.get_openaq_key()
    table = stations.mumbai_stations()
    now = pd.Timestamp.now(tz="UTC")
    is_active = table["last_utc"] >= now - pd.Timedelta(days=ACTIVE_DAYS)
    active = table[is_active]
    print(f"Scanning {len(active)} active stations. Left out (no reading in the last {ACTIVE_DAYS} days):")
    for _, s in table[~is_active].iterrows():
        print(f"  {s['id']}  {s['name']}  (last reading {s['last_utc']:%Y-%m-%d})")

    todo = [(s, v) for _, s in active.iterrows() for v in stations.VARIABLES
            if pd.notna(s[f"{v}_sensor"])]
    print(f"\n{len(todo)} sensors to check. Expect roughly 5 to 15 minutes.\n")

    end = datetime.now(timezone.utc)
    raw, results, failed_in_a_row = {}, [], 0
    for i, (s, v) in enumerate(todo, 1):
        sensor_id = int(s[f"{v}_sensor"])
        start = max(s["first_utc"], now - pd.Timedelta(days=WINDOW_DAYS))
        print(f"[{i}/{len(todo)}] {s['name']} - {v}", flush=True)
        try:
            data, url = openaq.get_sensor_days(key, sensor_id, start, end)
        except SystemExit as e:  # one sensor failed after its retries
            print(f"   FAILED: {e}")
            results.append({"station_id": s["id"], "station": s["name"], "variable": v,
                            "sensor_id": sensor_id, "first": None, "last": None, "days": None,
                            "pct_of_window": None, "longest_gap_d": None})
            failed_in_a_row += 1
            if failed_in_a_row >= 2:
                raise SystemExit("Two sensors failed in a row. Stopping so we do not hammer the API.")
            continue
        failed_in_a_row = 0
        raw[f"{s['id']}/{v}"] = {"sensor_id": sensor_id, "url": url,
                                 "pages": data["pages"], "results": data["results"]}
        results.append({"station_id": s["id"], "station": s["name"], "variable": v,
                        "sensor_id": sensor_id, **summarise(data["results"], start, end)})

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = config.RAW_OPENAQ / f"daily_scan_{stamp}.json.gz"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(raw_path, "wt", encoding="utf-8") as f:
        json.dump(raw, f)
    meta = {"source": "OpenAQ v3 sensors/{id}/measurements/daily, active Mumbai-city stations, "
                      f"last {WINDOW_DAYS} days; pages merged per sensor, rows untouched; gzip file",
            "downloaded_at_utc": stamp, "file": raw_path.name}
    (config.RAW_OPENAQ / f"daily_scan_{stamp}.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    summary = pd.DataFrame(results)
    summary[["days", "longest_gap_d"]] = summary[["days", "longest_gap_d"]].astype("Int64")
    config.CLEAN.mkdir(parents=True, exist_ok=True)
    summary.to_csv(config.CLEAN / "station_scan_summary.csv", index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", None)
    summary["station"] = summary["station"].str.slice(0, 38)
    for v in stations.VARIABLES:
        part = summary[summary["variable"] == v].sort_values("pct_of_window", ascending=False)
        print(f"\n===== {v} =====")
        print(part.drop(columns=["variable", "sensor_id"]).to_string(index=False))
        good = (part["pct_of_window"] >= 80).sum()
        print(f"Sensors with data on at least 80% of days in the window: {good} of {len(part)}")
    print(f"\nRaw copy: {raw_path.name}")
    print("Summary saved: data/clean/station_scan_summary.csv")


if __name__ == "__main__":
    main()
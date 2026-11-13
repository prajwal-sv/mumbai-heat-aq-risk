import json
import os
import time
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}

with open("data/clean/stations_config.json", encoding="utf-8") as f:
    config = json.load(f)

end = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
params = {"datetime_from": "2025-02-18T00:00:00Z", "datetime_to": end, "limit": 1000}
failed = []

for key, c in config.items():
    for name, sensor_id in c["sensors"].items():
        url = f"https://api.openaq.org/v3/sensors/{sensor_id}/days"
        r = requests.get(url, params=params, headers=headers, timeout=60)
        if r.status_code == 429:
            print("Too many requests, waiting 60 seconds...")
            time.sleep(60)
            r = requests.get(url, params=params, headers=headers, timeout=60)
        if r.status_code != 200:
            print(key, name, "failed, status", r.status_code)
            failed.append((key, name))
            continue

        base = f"data/raw/openaq_days_{key}_{name}"
        with open(base + ".json", "w", encoding="utf-8") as f:
            f.write(r.text)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with open(base + "_metadata.md", "w", encoding="utf-8") as f:
            f.write(f"Source: OpenAQ API v3\nURL: {r.url}\nDownloaded: {now}\nSensor: {sensor_id}\n")

        rows = len(r.json()["results"])
        print(key, name, "rows:", rows, "(WARNING: may be cut off)" if rows >= 1000 else "")
        time.sleep(1.2)

print("Failed downloads:", failed if failed else "none")
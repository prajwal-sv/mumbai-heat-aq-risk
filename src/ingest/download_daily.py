import os
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}

# station: (pm25 sensor, pm10 sensor, temperature sensor)
stations = {
    "malad_west_iitm":  (12236426, 12236425, 12236429),
    "kherwadi":         (12238411, 12238410, 12238414),
    "shivaji_nagar":    (12238576, 12238575, 12238579),
    "ghatkopar":        (12238603, 12238602, 12238606),
    "byculla":          (12238567, 12238566, 12238570),
    "bkc_mpcb":         (12238375, 12238374, 12238378),
}
names = ["pm25", "pm10", "temperature"]

params = {"datetime_from": "2025-02-18T00:00:00Z",
          "datetime_to": "2026-11-05T00:00:00Z", "limit": 1000}
shown = False

for station, ids in stations.items():
    for name, sensor_id in zip(names, ids):
        url = "https://api.openaq.org/v3/sensors/" + str(sensor_id) + "/days"
        r = requests.get(url, params=params, headers=headers)
        if r.status_code != 200:
            print(station, name, "failed, status", r.status_code)
            continue

        base = f"data/raw/openaq_days_{station}_{name}"
        with open(base + ".json", "w", encoding="utf-8") as f:
            f.write(r.text)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with open(base + "_metadata.md", "w", encoding="utf-8") as f:
            f.write(f"Source: OpenAQ API v3\nURL: {r.url}\nDownloaded: {now}\nSensor: {sensor_id}\n")

        rows = r.json()["results"]
        print(station, name, "rows:", len(rows))
        if rows and not shown:
            print("SAMPLE ROW:", rows[0])
            shown = True
        time.sleep(1.2)


# malad_west_iitm pm25 rows: 607
# SAMPLE ROW: {'value': 70.0, 'flagInfo': {'hasFlags': False}, 'parameter': {'id': 2, 'name': 'pm25', 'units': 'µg/m³', 'displayName': None}, 'period': {'label': '1day', 'interval': '24:00:00', 'datetimeFrom': {'utc': '2025-02-18T18:30:00Z', 'local': '2025-02-19T00:00:00+05:30'}, 'datetimeTo': {'utc': '2025-02-19T18:30:00Z', 'local': '2025-02-20T00:00:00+05:30'}}, 'coordinates': None, 'summary': {'min': 8.83, 'q02': 16.902900000000002, 'q25': 39.698750000000004, 'median': 49.7, 'q75': 66.10874999999999, 'q98': 229.77629999999994, 'max': 254.10500000000002, 'avg': 70.00945652173912, 'sd': 59.160714535548074}, 'coverage': {'expectedCount': 24, 'expectedInterval': '24:00:00', 'observedCount': 23, 'observedInterval': '23:00:00', 'percentComplete': 96.0, 'percentCoverage': 96.0, 'datetimeFrom': {'utc': '2025-02-18T20:15:00Z', 'local': '2025-02-19T01:45:00+05:30'}, 'datetimeTo': {'utc': '2025-02-19T18:15:00Z', 'local': '2025-02-19T23:45:00+05:30'}}}
# malad_west_iitm pm10 rows: 604
# malad_west_iitm temperature rows: 187
# kherwadi pm25 rows: 608
# kherwadi pm10 rows: 608
# kherwadi temperature rows: 608
# shivaji_nagar pm25 rows: 596
# shivaji_nagar pm10 rows: 595
# shivaji_nagar temperature rows: 595
# ghatkopar pm25 rows: 594
# ghatkopar pm10 rows: 594
# ghatkopar temperature rows: 592
# byculla pm25 rows: 597
# byculla pm10 rows: 597
# byculla temperature rows: 595
# bkc_mpcb pm25 rows: 595
# bkc_mpcb pm10 rows: 595
# bkc_mpcb temperature rows: 583
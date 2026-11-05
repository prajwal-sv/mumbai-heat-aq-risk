import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}

# Step 1: our six stations (location IDs)
locations = {
    "malad_west_iitm": 11611, "kherwadi": 3409486, "shivaji_nagar": 3409511,
    "ghatkopar": 3409514, "byculla": 3409510, "bkc_mpcb": 3409482,
}

# Step 2: our sensor IDs and what they measure
sensor_names = {
    12236426: "pm25", 12236425: "pm10", 12236429: "temperature",
    12238411: "pm25", 12238410: "pm10", 12238414: "temperature",
    12238576: "pm25", 12238575: "pm10", 12238579: "temperature",
    12238603: "pm25", 12238602: "pm10", 12238606: "temperature",
    12238567: "pm25", 12238566: "pm10", 12238570: "temperature",
    12238375: "pm25", 12238374: "pm10", 12238378: "temperature",
}

now = datetime.now(timezone.utc)

# Step 3: ask for the latest readings of each station
for station, location_id in locations.items():
    r = requests.get(f"https://api.openaq.org/v3/locations/{location_id}/latest", headers=headers)
    print("---", station, "| status:", r.status_code)
    if r.status_code != 200:
        continue
    for item in r.json()["results"]:
        name = sensor_names.get(item["sensorsId"])
        if name is None:
            continue
        when = datetime.fromisoformat(item["datetime"]["utc"].replace("Z", "+00:00"))
        age_hours = (now - when).total_seconds() / 3600
        print(f"  {name:12} value: {item['value']:8} | time (UTC): {item['datetime']['utc']} | age: {age_hours:.1f} h")


#         (venv) C:\Users\praja\mumbai-heat-aq-risk\mumbai-heat-aq-risk>python src\ingest\check_latest.py
# --- malad_west_iitm | status: 200
#   pm10         value:   119.87 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   pm25         value:    38.74 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   temperature  value:      0.0 | time (UTC): 2026-03-07T15:15:00Z | age: 5824.1 h
# --- kherwadi | status: 200
#   pm10         value:   114.25 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   temperature  value:    36.97 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   pm25         value:    58.81 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
# --- shivaji_nagar | status: 200
#   pm10         value:    96.34 | time (UTC): 2026-11-05T06:15:00Z | age: 1.1 h
#   temperature  value:    35.78 | time (UTC): 2026-11-05T06:30:00Z | age: 0.9 h
#   pm25         value:    50.71 | time (UTC): 2026-11-05T06:30:00Z | age: 0.9 h
# --- ghatkopar | status: 200
#   pm10         value:    78.89 | time (UTC): 2026-11-05T06:15:00Z | age: 1.1 h
#   pm25         value:    45.95 | time (UTC): 2026-11-05T06:15:00Z | age: 1.1 h
#   temperature  value:     32.2 | time (UTC): 2026-11-05T06:15:00Z | age: 1.1 h
# --- byculla | status: 200
#   pm25         value:    27.89 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   temperature  value:    35.97 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   pm10         value:    102.4 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
# --- bkc_mpcb | status: 200
#   pm25         value:    62.06 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   pm10         value:   131.86 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
#   temperature  value:     32.8 | time (UTC): 2026-11-05T06:00:00Z | age: 1.4 h
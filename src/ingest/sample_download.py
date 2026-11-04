import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}

# Part 1: one week of PM2.5 from Colaba (sensor 12235926)
sensor_id = 12235926
url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"
params = {
    "datetime_from": "2026-10-21T00:00:00Z",
    "datetime_to": "2026-10-28T00:00:00Z",
    "limit": 1000,
}
r = requests.get(url, params=params, headers=headers)
print("Status:", r.status_code)

# Save raw answer and a metadata note
with open("data/raw/openaq_sample_pm25_colaba.json", "w", encoding="utf-8") as f:
    f.write(r.text)
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
with open("data/raw/openaq_sample_pm25_colaba_metadata.md", "w", encoding="utf-8") as f:
    f.write(f"Source: OpenAQ API v3\nURL: {r.url}\nDownloaded: {now}\nSensor: {sensor_id}\n")

rows = r.json()["results"]
print("Rows:", len(rows))
for row in rows[:3]:
    print(row)

# Part 2: who runs station 8039?
info = requests.get("https://api.openaq.org/v3/locations/8039", headers=headers).json()["results"][0]
for key in ["name", "provider", "owner", "coordinates", "isMobile", "isMonitor", "timezone"]:
    print(key, ":", info.get(key))
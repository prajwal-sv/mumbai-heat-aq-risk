import json
from datetime import datetime, timedelta, timezone

KEEP_WORDS = ["Mumbai"]        # name must contain one of these (add "Thane" to include Thane)
DROP_WORDS = ["Navi Mumbai"]   # ...and none of these (set to [] to include Navi Mumbai)
MAX_AGE_DAYS = 7               # must have reported in the last 7 days

with open("data/raw/openaq_locations_mumbai.json", encoding="utf-8") as f:
    stations = json.load(f)["results"]

now = datetime.now(timezone.utc)
config = {}

for s in stations:
    name = s["name"]
    if not any(w in name for w in KEEP_WORDS) or any(w in name for w in DROP_WORDS):
        continue
    if not s["datetimeLast"]:
        continue
    last = datetime.fromisoformat(s["datetimeLast"]["utc"].replace("Z", "+00:00"))
    if now - last > timedelta(days=MAX_AGE_DAYS):
        continue

    # newest sensor (highest id) for each variable
    sensors = {}
    for x in s["sensors"]:
        p = x["parameter"]["name"]
        if p in ("pm25", "pm10", "temperature"):
            sensors[p] = max(sensors.get(p, 0), x["id"])
    if "pm25" not in sensors or "pm10" not in sensors:
        continue

    config[f"loc{s['id']}"] = {
        "location_id": s["id"],
        "name": name,
        "operator": name.split(" - ")[-1] if " - " in name else "unknown",
        "lat": s["coordinates"]["latitude"],
        "lon": s["coordinates"]["longitude"],
        "sensors": sensors,
    }

with open("data/clean/stations_config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print("Stations kept:", len(config))
for key, c in sorted(config.items(), key=lambda kv: kv[1]["name"]):
    print(f"  {c['name']:55} sensors: {sorted(c['sensors'])}")
print("Without a temperature sensor:", sum("temperature" not in c["sensors"] for c in config.values()))

# stations very close together are probably the same place
items = list(config.values())
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        km = (((items[i]["lat"] - items[j]["lat"]) * 111) ** 2
              + ((items[i]["lon"] - items[j]["lon"]) * 105) ** 2) ** 0.5
        if km < 0.3:
            print(f"Close together ({km * 1000:.0f} m): {items[i]['name']} | {items[j]['name']}")
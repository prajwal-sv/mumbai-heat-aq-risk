import json
from collections import Counter

with open("data/raw/openaq_locations_mumbai.json", encoding="utf-8") as f:
    stations = json.load(f)["results"]
with open("data/clean/stations_config.json", encoding="utf-8") as f:
    ids = {c["location_id"] for c in json.load(f).values()}

count = Counter()
for s in stations:
    if s["id"] in ids:
        print(s["id"], "|", s["name"], "|", s.get("licenses"))
        count[str(s.get("licenses"))] += 1
print(count)

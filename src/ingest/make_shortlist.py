import json
from datetime import datetime, timedelta, timezone

with open("data/raw/openaq_locations_mumbai.json", encoding="utf-8") as f:
    stations = json.load(f)["results"]

now = datetime.now(timezone.utc)

shortlist = []

for s in stations:
    name = s["name"]

    # Keep only Mumbai stations (exclude Navi Mumbai)
    if "Mumbai" in name and "Navi Mumbai" not in name:
        last = s.get("datetimeLast")

        if last:
            last_date = datetime.fromisoformat(
                last["utc"].replace("Z", "+00:00")
            )

            if now - last_date <= timedelta(days=7):
                shortlist.append(s["id"])

print("Stations kept:", len(shortlist))
print(shortlist)

# output: [6927, 6945, 6956, 6959, 6965, 6967, 8039, 11606, 11611, 12024, 12039, 12040, 3409323, 3409328, 3409329, 3409479, 3409482, 3409483, 3409486, 3409510, 3409511, 3409512, 3409513, 3409514]
import json

# Long-history stations first, then the newer 2025 ones
shortlist = [
    6927, 6945, 6956, 6959, 6965, 6967, 11606, 11611, 12024, 12039, 12040,
    3409323, 3409328, 3409329, 3409479, 3409482, 3409483, 3409486,
    3409510, 3409511, 3409512, 3409513, 3409514,
    8039,
]

with open("data/raw/openaq_locations_mumbai.json", encoding="utf-8") as f:
    stations = json.load(f)["results"]

for s in stations:
    if s["id"] not in shortlist:
        continue
    print("---")
    print(s["id"], "|", s["name"])
    for sensor in s["sensors"]:
        p = sensor["parameter"]
        print("   sensor", sensor["id"], "|", p["name"], "|", p["units"])

# Almost every station has PM2.5, PM10 and temperature. The exceptions are 8039 (see below) and none else. Temperature is reported in °C.

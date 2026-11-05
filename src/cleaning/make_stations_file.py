import json

# the six stations used in the app
ids = {
    3409486: "Kherwadi, Bandra East",
    3409511: "Shivaji Nagar",
    3409514: "Ghatkopar",
    3409510: "Byculla",
    3409482: "Bandra Kurla Complex",
    11611: "Malad West",
}

with open("data/raw/openaq_locations_mumbai.json", encoding="utf-8") as f:
    stations = json.load(f)["results"]

out = {}
for s in stations:
    if s["id"] in ids:
        out[str(s["id"])] = {
            "name": ids[s["id"]],
            "lat": s["coordinates"]["latitude"],
            "lon": s["coordinates"]["longitude"],
        }
        print(ids[s["id"]], s["coordinates"]["latitude"], s["coordinates"]["longitude"])

print("Stations saved:", len(out), "(expect 6)")
with open("data/clean/stations.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
#     Malad West 19.19709 72.82204
# Bandra Kurla Complex 19.065931 72.862131
# Kherwadi, Bandra East 19.0632143 72.8456324
# Byculla 18.9767 72.838
# Shivaji Nagar 19.060498 72.923356
# Ghatkopar 19.083694 72.920967
# Stations saved: 6 (expect 6)
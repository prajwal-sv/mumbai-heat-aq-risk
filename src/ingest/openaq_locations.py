import os
import requests
from dotenv import load_dotenv

# Step 1: get the key from the .env file
load_dotenv()
key = os.getenv("OPENAQ_API_KEY")\

# Step 2: ask OpenAQ for stations near Mumbai
url = "https://api.openaq.org/v3/locations"
params = {"coordinates": "19.0760,72.8777", "radius": 25000, "limit": 1000}
answer = requests.get(url, params=params, headers={"X-API-Key": key})
print("Status:", answer.status_code)


with open("data/raw/openaq_locations_mumbai.json","w",encoding="utf-8") as f :
    f.write(answer.text)


# Step 4: print one line per station
stations = answer.json()["results"]
print("Stations found:", len(stations))

for s in stations:
    first = s["datetimeFirst"]
    last = s["datetimeLast"]
    first_date = first["utc"] if first else "none"
    last_date = last["utc"] if last else "none"
    print(s["id"], "|", s["name"], "|", first_date, "|", last_date)

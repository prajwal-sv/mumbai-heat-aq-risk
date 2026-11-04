import os
import time
import requests
from dotenv import load_dotenv

# Step 1: get the key
load_dotenv()
headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}

# Step 2: the Mumbai stations we want to check
shortlist = [
    6927, 6945, 6956, 6959, 6965, 6967, 11606, 11611, 12024, 12039, 12040,
    3409323, 3409328, 3409329, 3409479, 3409482, 3409483, 3409486,
    3409510, 3409511, 3409512, 3409513, 3409514, 8039,
]

# Step 3: read the station file we saved earlier
stations = requests.get(
    "https://api.openaq.org/v3/locations",
    params={"coordinates": "19.0760,72.8777", "radius": 25000, "limit": 1000},
    headers=headers,
).json()["results"]


for s in stations:
    if s["id"] not in shortlist:
        continue

    print("---", s["id"], "|", s["name"])


    for sensor in s["sensors"]:
        name = sensor["parameter"]["name"]
        if name not in ["pm25", "pm10", "temperature"]:
            continue

        r = requests.get("https://api.openaq.org/v3/sensors/" + str(sensor["id"]), headers=headers)

        if r.status_code == 429:
            print("Too many requests, waiting 60 seconds...")
            time.sleep(60)
            r = requests.get("https://api.openaq.org/v3/sensors/" + str(sensor["id"]), headers=headers)
        
        
        info = r.json()["results"][0]
        first = info["datetimeFirst"]["utc"] if info["datetimeFirst"] else "none"
        last = info["datetimeLast"]["utc"] if info["datetimeLast"] else "none"
        print("  sensor", sensor["id"], "|", name, "| first:", first, "| last:", last)
        time.sleep(1.2)



# --- 6927 | Colaba, Mumbai - MPCB
#   sensor 20142 | pm10 | first: 2019-06-28T05:30:00Z | last: 2022-10-31T01:45:00Z
#   sensor 12235925 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 20143 | pm25 | first: 2019-06-28T05:30:00Z | last: 2022-10-31T01:45:00Z
#   sensor 12235926 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12235929 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-03-06T07:15:00Z
# --- 6945 | Kurla, Mumbai - MPCB
#   sensor 19975 | pm10 | first: 2019-06-19T00:00:00Z | last: 2022-10-31T02:00:00Z
#   sensor 12235833 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12235834 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 19978 | pm25 | first: 2019-06-19T00:00:00Z | last: 2022-10-31T02:00:00Z
#   sensor 12235836 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:15:00Z
# --- 6956 | Powai, Mumbai - MPCB
#   sensor 12235895 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 20010 | pm10 | first: 2019-06-18T23:15:00Z | last: 2022-10-16T13:15:00Z
#   sensor 20079 | pm25 | first: 2019-06-18T23:15:00Z | last: 2022-10-16T13:15:00Z
#   sensor 12235896 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12235899 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-10-27T11:45:00Z
# --- 6959 | Siddharth Nagar-Worli, Mumbai - IITM
#   sensor 20032 | pm10 | first: 2019-06-20T12:00:00Z | last: 2022-10-31T02:00:00Z
#   sensor 12236434 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T05:45:00Z
#   sensor 20033 | pm25 | first: 2019-06-20T12:00:00Z | last: 2022-10-31T02:00:00Z
#   sensor 12236435 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:15:00Z
#   sensor 12236437 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-06-26T07:15:00Z
# --- 6965 | Borivali East, Mumbai - MPCB
#   sensor 20085 | pm10 | first: 2019-06-20T16:00:00Z | last: 2022-10-31T02:00:00Z
#   sensor 12252657 | pm10 | first: 2025-02-20T08:30:00Z | last: 2026-11-04T11:00:00Z
#   sensor 20087 | pm25 | first: 2019-06-20T16:00:00Z | last: 2022-10-31T02:00:00Z
#   sensor 12252658 | pm25 | first: 2025-02-20T08:30:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12252661 | temperature | first: 2025-02-20T08:30:00Z | last: 2026-11-04T11:00:00Z
# --- 6967 | Sion, Mumbai - MPCB
#   sensor 20097 | pm10 | first: 2019-06-27T05:15:00Z | last: 2022-10-31T01:45:00Z
#   sensor 12243929 | pm10 | first: 2025-02-19T09:30:00Z | last: 2026-11-04T11:15:00Z
#   sensor 20096 | pm25 | first: 2019-06-27T05:15:00Z | last: 2022-10-31T01:45:00Z
#   sensor 12243930 | pm25 | first: 2025-02-19T09:30:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12243933 | temperature | first: 2025-02-19T09:30:00Z | last: 2026-11-04T11:15:00Z
# --- 8039 | Mumbai
#   sensor 23320 | pm25 | first: 2016-11-09T19:00:00Z | last: 2026-11-04T12:30:00Z
# --- 11606 | Borivali East, Mumbai - IITM
#   sensor 12236417 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 39429 | pm10 | first: 2020-11-13T12:30:00Z | last: 2022-07-08T07:15:00Z
#   sensor 39428 | pm25 | first: 2020-11-13T12:30:00Z | last: 2022-07-08T07:15:00Z
#   sensor 12236418 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12236420 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-02-13T09:00:00Z
# --- 11611 | Malad West, Mumbai - IITM
#   sensor 39455 | pm10 | first: 2020-11-13T12:15:00Z | last: 2022-10-16T15:45:00Z
#   sensor 12236425 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12236426 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 39454 | pm25 | first: 2020-11-13T12:15:00Z | last: 2022-10-16T15:45:00Z
#   sensor 12236429 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-03-07T15:15:00Z
# --- 12024 | Chakala-Andheri East, Mumbai - IITM
#   sensor 40572 | pm10 | first: 2020-12-08T09:00:00Z | last: 2022-10-16T13:00:00Z
#   sensor 12442195 | pm10 | first: 2025-03-11T08:00:00Z | last: 2026-11-04T11:15:00Z
#   sensor 40571 | pm25 | first: 2020-12-08T09:00:00Z | last: 2022-10-16T13:00:00Z
#   sensor 12442196 | pm25 | first: 2025-03-11T08:00:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12236412 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-06-16T07:30:00Z
# --- 12039 | Khindipada-Bhandup West, Mumbai - IITM
#   sensor 12236393 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 40615 | pm10 | first: 2020-12-16T12:45:00Z | last: 2022-09-22T05:30:00Z
#   sensor 40608 | pm25 | first: 2020-12-16T12:45:00Z | last: 2022-09-22T05:30:00Z
#   sensor 12236394 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12236397 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
# --- 12040 | Mulund West, Mumbai - MPCB
#   sensor 12236480 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T04:15:00Z
#   sensor 40628 | pm10 | first: 2020-12-16T12:30:00Z | last: 2022-10-16T15:45:00Z
#   sensor 12236481 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 40641 | pm25 | first: 2020-12-16T12:30:00Z | last: 2022-10-16T15:45:00Z
#   sensor 12236484 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-02T06:15:00Z
# --- 3409323 | Worli, Mumbai - MPCB
#   sensor 12235913 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:30:00Z
#   sensor 12235914 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:30:00Z
#   sensor 12235917 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:30:00Z
# --- 3409328 | Bandra Kurla Complex, Mumbai - IITM
#   sensor 12708245 | pm10 | first: 2025-04-07T13:00:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12708246 | pm25 | first: 2025-04-07T13:00:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12708249 | temperature | first: 2025-04-07T13:00:00Z | last: 2026-10-11T07:15:00Z
# --- 3409329 | Deonar, Mumbai - IITM
#   sensor 12236384 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12236385 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12236388 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-06-26T07:30:00Z
# --- 3409479 | Mindspace-Malad West, Mumbai - MPCB
#   sensor 12238347 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:45:00Z
#   sensor 12238348 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:45:00Z
#   sensor 12238351 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:45:00Z
# --- 3409482 | Bandra Kurla Complex, Mumbai - MPCB
#   sensor 12238374 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12238375 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12238378 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
# --- 3409483 | Chembur, Mumbai - MPCB
#   sensor 12238383 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12238384 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
#   sensor 12238387 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:00:00Z
# --- 3409486 | Kherwadi_Bandra East, Mumbai - MPCB
#   sensor 12238410 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12238411 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12238414 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
# --- 3409510 | Byculla, Mumbai - BMC
#   sensor 12238566 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12238567 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12238570 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
# --- 3409511 | Shivaji Nagar, Mumbai - BMC
#   sensor 12238575 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:30:00Z
#   sensor 12238576 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:30:00Z
#   sensor 12238579 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-02T21:00:00Z
# --- 3409512 | Kandivali West, Mumbai - BMC
#   sensor 12238584 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:00:00Z
#   sensor 12238585 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:00:00Z
#   sensor 12238588 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T10:00:00Z
# --- 3409513 | Sewri, Mumbai - BMC
#   sensor 12238593 | pm10 | first: 2025-02-18T20:45:00Z | last: 2026-11-04T11:30:00Z
#   sensor 12238594 | pm25 | first: 2025-02-18T20:45:00Z | last: 2026-11-04T11:30:00Z
#   sensor 12238597 | temperature | first: 2025-02-18T20:45:00Z | last: 2026-11-04T11:30:00Z
# --- 3409514 | Ghatkopar, Mumbai - BMC
#   sensor 12238602 | pm10 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12238603 | pm25 | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z
#   sensor 12238606 | temperature | first: 2025-02-18T20:15:00Z | last: 2026-11-04T11:15:00Z




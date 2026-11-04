import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}

# New PM2.5 sensors (Feb 2025 to now)
sensors = {
    "Colaba": 12235926, "Kurla": 12235834, "Powai": 12235896,
    "Worli IITM": 12236435, "Borivali East MPCB": 12252658, "Sion": 12243930,
    "Borivali East IITM": 12236418, "Malad West IITM": 12236426,
    "Chakala-Andheri": 12442196, "Khindipada-Bhandup": 12236394,
    "Mulund West": 12236481, "Worli MPCB": 12235914, "BKC IITM": 12708246,
    "Deonar": 12236385, "Mindspace-Malad": 12238348, "BKC MPCB": 12238375,
    "Chembur": 12238384, "Kherwadi-Bandra E": 12238411, "Byculla": 12238567,
    "Shivaji Nagar": 12238576, "Kandivali West": 12238585, "Sewri": 12238594,
    "Ghatkopar": 12238603, "Station 8039": 23320,
}

for name, sensor_id in sensors.items():
    url = "https://api.openaq.org/v3/sensors/" + str(sensor_id) + "/days"
    params = {"datetime_from": "2025-02-18T00:00:00Z",
              "datetime_to": "2026-11-05T00:00:00Z", "limit": 1000}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        print(name, "failed, status", r.status_code)
        continue

    rows = r.json()["results"]
    if not rows:
        print(name, "no rows")
        continue

    # percent of expected readings that exist for each day
    coverage = [(x.get("coverage") or {}).get("percentCoverage") or 0 for x in rows]
    good_days = len([c for c in coverage if c >= 75])
    average = sum(coverage) / len(coverage)
    print(f"{name:20} days: {len(rows):4} | good days (75%+): {good_days:4} | avg coverage: {average:.0f}%")
    time.sleep(1.2)



# Colaba               days:  475 | good days (75%+):  414 | avg coverage: 91%
# Kurla                days:  555 | good days (75%+):  435 | avg coverage: 86%
# Powai                days:  495 | good days (75%+):  408 | avg coverage: 88%
# Worli IITM           days:  587 | good days (75%+):  498 | avg coverage: 90%
# Borivali East MPCB   days:  499 | good days (75%+):  390 | avg coverage: 85%
# Sion                 days:  523 | good days (75%+):  430 | avg coverage: 88%
# Borivali East IITM   days:  604 | good days (75%+):  548 | avg coverage: 93%
# Malad West IITM      days:  607 | good days (75%+):  557 | avg coverage: 93%
# Chakala-Andheri      days:  579 | good days (75%+):  511 | avg coverage: 91%
# Khindipada-Bhandup   days:  337 | good days (75%+):  285 | avg coverage: 89%
# Mulund West          days:  567 | good days (75%+):  450 | avg coverage: 87%
# Worli MPCB           days:  515 | good days (75%+):  404 | avg coverage: 85%
# BKC IITM             days:  499 | good days (75%+):  335 | avg coverage: 79%
# Deonar               days:  551 | good days (75%+):  460 | avg coverage: 89%
# Mindspace-Malad      days:  600 | good days (75%+):  507 | avg coverage: 89%
# BKC MPCB             days:  595 | good days (75%+):  515 | avg coverage: 90%
# Chembur              days:  598 | good days (75%+):  502 | avg coverage: 89%
# Kherwadi-Bandra E    days:  608 | good days (75%+):  544 | avg coverage: 92%
# Byculla              days:  597 | good days (75%+):  517 | avg coverage: 90%
# Shivaji Nagar        days:  596 | good days (75%+):  535 | avg coverage: 92%
# Kandivali West       days:  591 | good days (75%+):  471 | avg coverage: 85%
# Sewri                days:  565 | good days (75%+):  326 | avg coverage: 72%
# Ghatkopar            days:  594 | good days (75%+):  523 | avg coverage: 91%
# Station 8039         days: 1000 | good days (75%+):  928 | avg coverage: 142%
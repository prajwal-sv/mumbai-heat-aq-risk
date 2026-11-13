import os
import requests
from dotenv import load_dotenv

load_dotenv()
r = requests.get("https://api.openaq.org/v3/locations/6927",
                 headers={"X-API-Key": os.getenv("OPENAQ_API_KEY")})
print(r.status_code)
res = r.json()["results"][0]
print(list(res.keys()))
print("licenses:", res.get("licenses"))
print("provider:", res.get("provider"))

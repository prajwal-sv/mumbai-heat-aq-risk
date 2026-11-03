"""Find out why the hourly request fails. Sends 5 small requests, one at a time.
Run:  python -m src.probe 12235896      (12235896 = the Powai PM2.5 sensor)"""
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

from src import config

BASE = "https://api.openaq.org/v3"


def try_request(label, path, params, key):
    """Send one request and print what happened. Never crashes."""
    began = time.time()
    try:
        r = requests.get(f"{BASE}/{path}", params=params,
                         headers={"X-API-Key": key}, timeout=60)
    except requests.exceptions.RequestException as e:
        print(f"{label}: FAILED after {time.time() - began:.1f}s -> {type(e).__name__}")
        time.sleep(2)
        return
    rows = ""
    try:
        rows = f", rows={len(r.json().get('results', []))}"
    except ValueError:
        pass
    left = r.headers.get("x-ratelimit-remaining", "?")
    print(f"{label}: HTTP {r.status_code} in {time.time() - began:.1f}s{rows}, "
          f"requests left this minute={left}")
    if r.status_code >= 400:
        print("   server said:", r.text[:200])
    time.sleep(2)


def main(sensor_id):
    key = config.get_openaq_key()
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    def window(days):
        return {"datetime_from": (end - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "datetime_to": end.strftime("%Y-%m-%dT%H:%M:%SZ")}

    print(f"Probing sensor {sensor_id}\n")
    try_request("1. station list (worked before)", "locations", {"limit": 1}, key)
    try_request("2. hours, no dates, 3 rows", f"sensors/{sensor_id}/hours", {"limit": 3}, key)
    try_request("3. hours, last 1 day", f"sensors/{sensor_id}/hours",
                {**window(1), "limit": 100}, key)
    try_request("4. hours, last 30 days", f"sensors/{sensor_id}/hours",
                {**window(30), "limit": 1000}, key)
    try_request("5. DAILY values, last 30 days", f"sensors/{sensor_id}/measurements/daily",
                {**window(30), "limit": 100}, key)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python -m src.probe <sensor_id>")
    main(int(sys.argv[1]))
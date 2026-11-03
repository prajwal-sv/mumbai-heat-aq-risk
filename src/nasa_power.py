"""Download from OpenAQ (API v3) and save the raw answer untouched."""
import json
import time
from datetime import datetime, timezone

import requests

BASE_URL = "https://api.openaq.org/v3"
PAGE_SIZE = 1000      # rows per request
MAX_PAGES = 200       # safety stop so a bug can never hammer the API
PAUSE_SECONDS = 1.1   # about 55 requests/minute, under the 60/minute limit


def _get(path, params, key):
    """One request to OpenAQ. Waits and retries if we hit the rate limit."""
    url = f"{BASE_URL}/{path}"
    for _ in range(3):
        r = requests.get(url, params=params, headers={"X-API-Key": key}, timeout=60)
        if r.status_code == 429:  # too many requests: wait, then try again
            try:
                wait = int(r.headers.get("x-ratelimit-reset", 60))
            except ValueError:
                wait = 60
            print(f"Rate limit reached. Waiting {wait + 1} seconds...")
            time.sleep(wait + 1)
            continue
        if r.status_code >= 400:
            raise SystemExit(f"OpenAQ error {r.status_code}: {r.text[:300]}")
        return r
    raise SystemExit("Rate limit hit 3 times in a row. Stopping to avoid a ban.")


def get_locations(key, lat, lon, radius_m=25000, limit=1000):
    """Stations within radius_m metres of a point. Returns (json_answer, url_used)."""
    params = {"coordinates": f"{lat},{lon}", "radius": radius_m, "limit": limit}
    r = _get("locations", params, key)
    return r.json(), r.url


def get_sensor_hours(key, sensor_id, start, end):
    """Hourly values for ONE sensor between two UTC datetimes.
    Fetches page after page until there is nothing left.
    Returns ({"results": [...], "pages": n}, url_of_first_request)."""
    params = {
        "datetime_from": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "datetime_to": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": PAGE_SIZE,
        "page": 1,
    }
    all_rows, first_url, pages = [], None, 0
    while pages < MAX_PAGES:
        r = _get(f"sensors/{sensor_id}/hours", params, key)
        first_url = first_url or r.url
        batch = r.json().get("results", [])
        all_rows.extend(batch)
        pages += 1
        if len(batch) < PAGE_SIZE:  # last page
            break
        params["page"] += 1
        time.sleep(PAUSE_SECONDS)
    return {"results": all_rows, "pages": pages}, first_url


def save_raw(data, folder, name, source_url, note):
    """Write the answer exactly as received, plus a small .meta.json note."""
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data_path = folder / f"{name}_{stamp}.json"
    data_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    meta = {
        "source": note,
        "url": source_url,
        "downloaded_at_utc": stamp,
        "file": data_path.name,
    }
    meta_path = folder / f"{name}_{stamp}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return data_path
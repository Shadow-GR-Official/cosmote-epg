import requests
import json
import sys
import time
import re
from datetime import datetime, timedelta, timezone

def clean_program(p):
    desc = p.get("description") or ""

    # Extract episode
    episode = None
    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        episode = match.group(1).strip()
        desc = desc.replace(match.group(0), "")

    # Remove durations
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)

    # Cleanup
    desc = re.sub(r"\s{2,}", " ", desc).strip()

    p["description"] = desc
    if episode:
        p["episode"] = episode

    return p


def get_timestamps():
    now = datetime.now(timezone.utc)

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    return int(start.timestamp()), int(end.timestamp())


def fetch_with_retry(session, url, headers, retries=3):
    for i in range(retries):
        try:
            r = session.get(url, headers=headers, timeout=25)

            if r.status_code == 200:
                return r

            print(f"Retry {i+1} - Status: {r.status_code}")
            time.sleep(2)

        except Exception as e:
            print(f"Retry {i+1} - Error: {e}")
            time.sleep(2)

    return None


def main():
    start_ts, end_ts = get_timestamps()

    API = f"https://www.cosmotetv.gr/api/channels/schedule?locale=el&from={start_ts}&to={end_ts}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()

    try:
        print(f"Target URL: {API}")

        # get cookies
        session.get("https://cosmotetv.gr", headers=headers, timeout=20)

        # fetch with retry
        r = fetch_with_retry(session, API, headers)

        if not r:
            print("API FAILED after retries")
            sys.exit(1)

        data = r.json()
        all_channels = []

        stripes = data.get("stripes", [])

        if isinstance(stripes, list):
            for stripe in stripes:
                if isinstance(stripe, dict) and "channels" in stripe:
                    all_channels.extend(stripe["channels"])
        elif isinstance(stripes, dict):
            all_channels = stripes.get("channels", [])

        if not all_channels:
            print("No channels found.")
            sys.exit(1)

        # CLEAN PROGRAMS
        for ch in all_channels:
            programs = ch.get("items") or ch.get("programs") or []

            cleaned = [clean_program(p) for p in programs]

            if "items" in ch:
                ch["items"] = cleaned
            else:
                ch["programs"] = cleaned

        # save
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(all_channels, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(all_channels)} channels")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

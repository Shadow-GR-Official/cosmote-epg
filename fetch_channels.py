import requests
import json
import sys
import time
import re
from datetime import datetime, timedelta, timezone


# ----------------------------
# CLEAN PROGRAM DATA
# ----------------------------
def clean_program(p):
    desc = p.get("description") or ""

    episode = None
    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        episode = match.group(1).strip()
        desc = desc.replace(match.group(0), "")

    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)
    desc = re.sub(r"\s{2,}", " ", desc).strip()

    p["description"] = desc

    if episode:
        p["episode"] = episode

    return p


# ----------------------------
# 48H WINDOW (TODAY + TOMORROW)
# ----------------------------
def get_range():
    now = datetime.now(timezone.utc)

    start = now
    end = now + timedelta(days=2)  # 48 hours

    return int(start.timestamp()), int(end.timestamp())


# ----------------------------
# SAFE REQUEST WITH RETRY
# ----------------------------
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


# ----------------------------
# EXTRACT CHANNELS
# ----------------------------
def extract_channels(data):
    channels = []

    stripes = data.get("stripes", [])

    if isinstance(stripes, list):
        for stripe in stripes:
            if isinstance(stripe, dict) and "channels" in stripe:
                channels.extend(stripe["channels"])

    elif isinstance(stripes, dict):
        channels = stripes.get("channels", [])

    return channels


# ----------------------------
# MAIN
# ----------------------------
def main():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()

    try:
        # warm-up request (important for session cookies)
        session.get("https://cosmotetv.gr", headers=headers, timeout=20)

        start_ts, end_ts = get_range()

        api_url = (
            "https://www.cosmotetv.gr/api/channels/schedule"
            f"?locale=el&from={start_ts}&to={end_ts}"
        )

        print(f"[EPG 48H] {api_url}")

        r = fetch_with_retry(session, api_url, headers)

        if not r:
            print("Failed to fetch EPG")
            sys.exit(1)

        data = r.json()
        all_channels = extract_channels(data)

        if not all_channels:
            print("No channels found in response")
            sys.exit(1)

        # ----------------------------
        # CLEAN PROGRAMS
        # ----------------------------
        for ch in all_channels:
            programs = ch.get("items") or ch.get("programs") or []
            cleaned = [clean_program(p) for p in programs]

            if "items" in ch:
                ch["items"] = cleaned
            else:
                ch["programs"] = cleaned

        # ----------------------------
        # SAVE
        # ----------------------------
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(all_channels, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(all_channels)} channels (48h EPG)")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

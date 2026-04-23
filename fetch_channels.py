import requests
import json
import os
import time
from datetime import datetime, timedelta

BASE_URL = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

os.makedirs("data", exist_ok=True)


def safe_get(session, url, retries=20, delay=50):
    for attempt in range(retries):
        try:
            r = session.get(
                url,
                timeout=(1000, 3000)  # (connect timeout, read timeout)
            )

            if r.status_code != 200:
                print("HTTP ERROR:", r.status_code)
            elif not r.text.strip():
                print("EMPTY RESPONSE")
            else:
                return r.json()

        except Exception as e:
            print("REQUEST ERROR:", e)

        # retry logic
        if attempt < retries - 1:
            print(f"Retrying in {delay}s... ({attempt+1}/{retries})")
            time.sleep(delay)

    return None


def extract_channels(data):
    """
    FIX: Cosmote stripes can be dict OR list OR nested structure
    """
    stripes = data.get("stripes")

    channels = []

    if isinstance(stripes, dict):
        channels.extend(stripes.get("channels", []))

    elif isinstance(stripes, list):
        for s in stripes:
            if isinstance(s, dict):
                channels.extend(s.get("channels", []))

    return channels


def run():
    session = requests.Session()

    # warm-up (important for Cosmote session behavior)
    session.get("https://www.cosmotetv.gr", timeout=20)

    channels_by_id = {}

    print("[FETCH] Cosmote EPG")

    for i in range(0, 7):
        day = datetime.now() + timedelta(days=i)

        from_ts = int(day.replace(hour=0, minute=0, second=0).timestamp())
        to_ts = int(day.replace(hour=23, minute=59, second=59).timestamp())

        url = f"{BASE_URL}&from={from_ts}&to={to_ts}"

        print("→", day.strftime("%Y-%m-%d"))

        data = safe_get(session, url)

        if not data:
            print("skip")
            continue

        channels = extract_channels(data)

        print("  channels found:", len(channels))

        for ch in channels:
            guid = ch.get("guid")
            if not guid:
                continue

            if guid not in channels_by_id:
                channels_by_id[guid] = {
                    "id": guid,
                    "name": ch.get("title"),
                    "logo": (ch.get("logos") or {}).get("square"),
                    "items": []
                }

            for p in ch.get("items", []):
                channels_by_id[guid]["items"].append({
                    "title": p.get("title"),
                    "startTime": p.get("startTime"),
                    "endTime": p.get("endTime"),
                    "description": p.get("description"),
                    "genres": p.get("genres")
                })

        time.sleep(1.2)

    epg_list = list(channels_by_id.values())

    with open("data/epg.json", "w", encoding="utf-8") as f:
        json.dump(epg_list, f, ensure_ascii=False, indent=2)

    print("✔ epg.json saved")
    print("✔ TOTAL channels:", len(epg_list))


if __name__ == "__main__":
    run()

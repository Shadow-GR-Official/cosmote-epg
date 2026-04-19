import requests
import json
import os
import time
from datetime import datetime, timedelta

BASE_URL = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

os.makedirs("data", exist_ok=True)


def safe_get(session, url):
    try:
        r = session.get(url, timeout=30)

        if r.status_code != 200:
            print("HTTP ERROR:", r.status_code)
            return None

        if not r.text.strip():
            return None

        return r.json()

    except Exception as e:
        print("REQUEST ERROR:", e)
        return None


def run():
    session = requests.Session()

    # warm-up session (important for Cosmote API stability)
    session.get("https://www.cosmotetv.gr", timeout=20)

    channels_by_id = {}

    print("[FETCH] Cosmote multi-day EPG")

    # limited range = more stable (Cosmote API constraint)
    for i in range(0, 3):
        day = datetime.now() + timedelta(days=i)

        from_ts = int(day.replace(hour=0, minute=0, second=0).timestamp())
        to_ts = int(day.replace(hour=23, minute=59, second=59).timestamp())

        url = f"{BASE_URL}&from={from_ts}&to={to_ts}"

        print("→", day.strftime("%Y-%m-%d"))

        data = safe_get(session, url)

        if not data:
            print("skip")
            continue

        stripes = data.get("stripes", {})
        channels = stripes.get("channels", []) if isinstance(stripes, dict) else []

        for ch in channels:
            guid = ch.get("guid")
            if not guid:
                continue

            # create channel if not exists
            if guid not in channels_by_id:
                channels_by_id[guid] = {
                    "id": guid,
                    "name": ch.get("title"),
                    "logo": (ch.get("logos") or {}).get("square"),
                    "items": []
                }

            # merge programs safely
            for p in ch.get("items", []):
                channels_by_id[guid]["items"].append({
                    "title": p.get("title"),
                    "startTime": p.get("startTime"),
                    "endTime": p.get("endTime"),
                    "description": p.get("description"),
                    "genres": p.get("genres"),
                    "channelGuid": guid
                })

        time.sleep(1.5)  # avoid API throttling

    # save final dataset
    epg_list = list(channels_by_id.values())

    with open("data/epg.json", "w", encoding="utf-8") as f:
        json.dump(epg_list, f, ensure_ascii=False, indent=2)

    print("✔ epg.json saved")
    print("✔ channels:", len(epg_list))


if __name__ == "__main__":
    run()

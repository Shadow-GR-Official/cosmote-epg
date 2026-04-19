import requests
import json
import os
import time
from datetime import datetime, timedelta

BASE_URL = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

os.makedirs("data", exist_ok=True)

def get_range(date_str):
    start = datetime.strptime(date_str, "%Y-%m-%d")
    end = start.replace(hour=23, minute=59, second=59)
    return int(start.timestamp()), int(end.timestamp())

def safe_get(session, url):
    try:
        r = session.get(url, timeout=30)
        if r.status_code == 200 and r.text.strip():
            return r.json()
        print("HTTP ERROR:", r.status_code)
    except Exception as e:
        print("REQUEST ERROR:", e)
    return None

def run():
    session = requests.Session()
    session.get("https://www.cosmotetv.gr", timeout=20)

    all_days = []

    print("[FETCH] Cosmote multi-day EPG")

    for i in range(0, 3):  # safe range (Cosmote unstable for long range)
        d = datetime.now() + timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")

        from_ts, to_ts = get_range(date_str)
        url = f"{BASE_URL}&from={from_ts}&to={to_ts}"

        print("→", date_str)

        data = safe_get(session, url)
        if not data:
            print("skip")
            continue

        stripes = data.get("stripes", {})
        channels = stripes.get("channels", []) if isinstance(stripes, dict) else []

        normalized = []

        for ch in channels:
            programs = []

            for p in ch.get("items", []):
                programs.append({
                    "title": p.get("title"),
                    "startTime": p.get("startTime"),
                    "endTime": p.get("endTime"),
                    "description": p.get("description"),
                    "genres": p.get("genres"),
                    "channelGuid": p.get("channelGuid")
                })

            normalized.append({
                "id": ch.get("guid"),
                "name": ch.get("title"),
                "logo": (ch.get("logos") or {}).get("square"),
                "items": programs
            })

        all_days.extend(normalized)

        time.sleep(1)

    with open("data/epg.json", "w", encoding="utf-8") as f:
        json.dump(all_days, f, ensure_ascii=False, indent=2)

    print("✔ epg.json saved")

if __name__ == "__main__":
    run()

import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "https://www.magentatv.gr/api/channels/schedule"

os.makedirs("data", exist_ok=True)


def safe_get(session, params, retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            r = session.get(
                BASE_URL,
                params=params,
                timeout=(20, 60),
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )

            if r.status_code == 200:
                if not r.text.strip():
                    print("EMPTY RESPONSE")
                else:
                    try:
                        return r.json()
                    except ValueError as e:
                        print("JSON ERROR:", e)
            else:
                print("HTTP ERROR:", r.status_code)

        except requests.RequestException as e:
            print("REQUEST ERROR:", e)

        if attempt < retries:
            print(f"Retrying in {delay}s... ({attempt}/{retries})")
            time.sleep(delay)

    return None


def extract_channels(data):
    stripes = data.get("stripes")

    if isinstance(stripes, dict):
        return stripes.get("channels", [])

    if isinstance(stripes, list):
        channels = []

        for stripe in stripes:
            if isinstance(stripe, dict):
                channels.extend(
                    stripe.get("channels", [])
                )

        return channels

    return []


def run():
    session = requests.Session()

    try:
        session.get(
            "https://www.magentatv.gr",
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
    except requests.RequestException as e:
        print("Warm-up error:", e)

    channels_by_id = {}

    print("[FETCH] Magenta TV EPG")

    for i in range(-1, 5):
        day = datetime.now(timezone.utc) + timedelta(days=i)

        from_dt = day.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        to_dt = day.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=0
        )

        from_ts = int(from_dt.timestamp())
        to_ts = int(to_dt.timestamp())

        params = {
            "locale": "el",
            "from": from_ts,
            "to": to_ts
        }

        print("→", from_dt.strftime("%Y-%m-%d"))

        data = safe_get(session, params)

        if not data:
            print("  skip")
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
                    "items": {}
                }

            for p in ch.get("items", []):
                program_id = (
                    p.get("programGuid")
                    or p.get("guid")
                )

                if not program_id:
                    program_id = (
                        f"{p.get('startTime')}|"
                        f"{p.get('endTime')}|"
                        f"{p.get('title')}"
                    )

                channels_by_id[guid]["items"][program_id] = {
                    "title": p.get("title"),
                    "startTime": p.get("startTime"),
                    "endTime": p.get("endTime"),
                    "description": p.get("description"),
                    "genres": p.get("genres")
                }

        time.sleep(1.2)

    epg_list = []

    for channel in channels_by_id.values():
        items = list(channel["items"].values())

        items.sort(
            key=lambda x: x.get("startTime") or ""
        )

        channel["items"] = items
        epg_list.append(channel)

    epg_list.sort(
        key=lambda x: x.get("name") or ""
    )

    output_file = "data/epg.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            epg_list,
            f,
            ensure_ascii=False,
            indent=2
        )

    total_programmes = sum(
        len(ch["items"])
        for ch in epg_list
    )

    print()
    print("✔ epg.json saved")
    print("✔ TOTAL channels:", len(epg_list))
    print("✔ TOTAL programmes:", total_programmes)


if __name__ == "__main__":
    run()

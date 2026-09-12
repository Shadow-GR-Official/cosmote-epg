
import requests
import json
import os
import time
import shutil
from datetime import datetime, timedelta, timezone

BASE_URL = "https://www.magentatv.gr/api/channels/schedule"

# ============================================================
# ΠΛΗΡΗΣ ΔΙΑΓΡΑΦΗ DATA ΣΕ ΚΑΘΕ RUN
# ============================================================

if os.path.exists("data"):
    shutil.rmtree("data")

os.makedirs("data", exist_ok=True)


# ============================================================
# API REQUEST
# ============================================================

def safe_get(session, params, retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            response = session.get(
                BASE_URL,
                params=params,
                timeout=(20, 60),
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )

            if response.status_code != 200:
                print("HTTP ERROR:", response.status_code)
            elif not response.text.strip():
                print("EMPTY RESPONSE")
            else:
                try:
                    return response.json()
                except ValueError:
                    print("JSON ERROR")

        except requests.RequestException as e:
            print("REQUEST ERROR:", e)

        if attempt < retries:
            print(
                f"Retrying in {delay}s... "
                f"({attempt}/{retries})"
            )
            time.sleep(delay)

    return None


# ============================================================
# MAGENTA API STRUCTURE
#
# stripes
#   └── channels
#         ├── guid
#         ├── title
#         ├── type
#         ├── logos
#         └── items
# ============================================================

def extract_channels(data):

    if not isinstance(data, dict):
        return []

    stripes = data.get("stripes")

    if not isinstance(stripes, dict):
        return []

    channels = stripes.get("channels")

    if not isinstance(channels, list):
        return []

    return [
        ch
        for ch in channels
        if isinstance(ch, dict)
        and ch.get("type") == "channel"
        and ch.get("guid")
    ]


# ============================================================
# MAIN
# ============================================================

def run():

    session = requests.Session()

    # Warm-up
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
    print("[FETCH] No channel list / no channels= parameter")
    print()

    # Yesterday + today + next 6 days
    for i in range(-1, 7):

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

        params = {
            "locale": "el",
            "from": int(from_dt.timestamp()),
            "to": int(to_dt.timestamp())
        }

        date_text = from_dt.strftime("%Y-%m-%d")

        print("→", date_text)

        data = safe_get(
            session,
            params
        )

        if not data:
            print("  API response: EMPTY")
            continue

        channels = extract_channels(data)

        print("  channels:", len(channels))

        day_programmes = 0

        for ch in channels:

            guid = str(ch.get("guid")).strip()

            if not guid:
                continue

            name = (
                ch.get("title")
                or ch.get("callSign")
                or guid
            )

            logos = ch.get("logos") or {}

            logo = (
                logos.get("square")
                or logos.get("wide")
                or ""
            )

            if guid not in channels_by_id:

                channels_by_id[guid] = {
                    "id": guid,
                    "name": name,
                    "logo": logo,
                    "items": {}
                }

            else:

                # Συμπληρώνουμε metadata αν εμφανιστεί
                # καλύτερη πληροφορία σε επόμενη ημέρα.

                if not channels_by_id[guid]["name"]:
                    channels_by_id[guid]["name"] = name

                if not channels_by_id[guid]["logo"]:
                    channels_by_id[guid]["logo"] = logo

            items = ch.get("items") or []

            for program in items:

                if not isinstance(program, dict):
                    continue

                start_time = program.get("startTime")
                end_time = program.get("endTime")
                title = program.get("title")

                # Το Magenta δίνει programGuid.
                # Αν λείπει, χρησιμοποιούμε guid.
                # Τελευταίο fallback: start/end/title.

                program_id = (
                    program.get("programGuid")
                    or program.get("guid")
                )

                if not program_id:
                    program_id = (
                        f"{start_time}|"
                        f"{end_time}|"
                        f"{title}"
                    )

                channels_by_id[guid]["items"][program_id] = {
                    "title": title,
                    "startTime": start_time,
                    "endTime": end_time,
                    "description": program.get("description"),
                    "genres": program.get("genres")
                }

                day_programmes += 1

        print("  programmes:", day_programmes)

        time.sleep(1.2)

    # ============================================================
    # FINAL SORT
    # ============================================================

    epg_list = []

    for channel in channels_by_id.values():

        items = list(
            channel["items"].values()
        )

        items.sort(
            key=lambda x: x.get("startTime") or ""
        )

        channel["items"] = items

        epg_list.append(channel)

    epg_list.sort(
        key=lambda x: x.get("name") or ""
    )

    # ============================================================
    # SAVE EPG JSON
    # ============================================================

    with open(
        "data/epg.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            epg_list,
            f,
            ensure_ascii=False,
            indent=2
        )

    # ============================================================
    # STATISTICS
    # ============================================================

    total_channels = len(epg_list)

    total_programmes = sum(
        len(channel["items"])
        for channel in epg_list
    )

    channels_with_epg = sum(
        1
        for channel in epg_list
        if channel["items"]
    )

    channels_without_epg = sum(
        1
        for channel in epg_list
        if not channel["items"]
    )

    print()
    print("=" * 60)
    print("✔ DATA CLEANED")
    print("✔ epg.json CREATED FROM SCRATCH")
    print()
    print("✔ TOTAL CHANNELS:", total_channels)
    print("✔ CHANNELS WITH EPG:", channels_with_epg)
    print("✔ CHANNELS WITHOUT EPG:", channels_without_epg)
    print("✔ TOTAL PROGRAMMES:", total_programmes)
    print("=" * 60)


if __name__ == "__main__":
    run()


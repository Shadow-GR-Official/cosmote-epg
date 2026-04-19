import requests
import json
import os
import sys
import re
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(BASE_DIR, "epg.json")

BASE_URL = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"


def get_range(date):
    start = datetime.strptime(date, "%Y-%m-%d")
    end = start.replace(hour=23, minute=59, second=59)
    return int(start.timestamp()), int(end.timestamp())


def fetch(session, url, headers):
    try:
        r = session.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()
        print("HTTP ERROR:", r.status_code)
    except Exception as e:
        print("REQUEST ERROR:", e)
    return None


def extract_channels(data):
    stripes = data.get("stripes", [])
    channels = []

    if isinstance(stripes, list):
        for s in stripes:
            if isinstance(s, dict) and "channels" in s:
                channels.extend(s["channels"])
    elif isinstance(stripes, dict):
        channels = stripes.get("channels", [])

    return channels


def clean_program(p):
    if not isinstance(p, dict):
        return p

    desc = p.get("description") or ""

    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        p["episode"] = match.group(1).strip()
        desc = desc.replace(match.group(0), "")

    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)

    p["description"] = re.sub(r"\s{2,}", " ", desc).strip()

    return p


def merge_channels(all_days):
    merged = {}
    seen = set()

    for channels in all_days:
        for ch in channels:
            cid = ch.get("id") or ch.get("uuid") or ch.get("channelId")
            if not cid:
                continue

            if cid not in merged:
                merged[cid] = ch
                merged[cid]["items"] = []

            for p in ch.get("items", []):
                key = f"{cid}-{p.get('startTime')}-{p.get('endTime')}"

                if key not in seen:
                    seen.add(key)
                    merged[cid]["items"].append(p)

    return list(merged.values())


def save_json(data):
    tmp = OUT_FILE + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp, OUT_FILE)

    print("✔ epg.json saved:", OUT_FILE)
    print("✔ channels:", len(data))


def run():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr"
    }

    session = requests.Session()
    session.get("https://cosmotetv.gr", timeout=20)

    all_days = []

    print("[FETCH] multi-day Cosmote EPG...")

    for i in range(0, 7):
        d = datetime.now() + timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")

        from_ts, to_ts = get_range(date_str)
        url = f"{BASE_URL}&from={from_ts}&to={to_ts}"

        print("→", date_str)

        data = fetch(session, url, headers)
        if not data:
            print("  skip")
            continue

        channels = extract_channels(data)

        for ch in channels:
            prog = ch.get("items") or ch.get("programs") or []
            ch["items"] = [clean_program(p) for p in prog]

        all_days.append(channels)

    if not all_days:
        print("NO DATA AT ALL")
        sys.exit(1)

    merged = merge_channels(all_days)

    save_json(merged)


if __name__ == "__main__":
    run()

import requests
import json
import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "epg.json")


def fetch(session, url, headers):
    try:
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r
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


def save_json(data):
    tmp = JSON_FILE + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp, JSON_FILE)

    print("✔ epg.json saved:", JSON_FILE)
    print("✔ channels:", len(data))


def run():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr"
    }

    session = requests.Session()
    session.get("https://cosmotetv.gr", timeout=10)

    url = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

    print("[FETCH] getting data...")

    r = fetch(session, url, headers)
    if not r:
        print("FAILED FETCH")
        sys.exit(1)

    data = r.json()
    channels = extract_channels(data)

    if not channels:
        print("NO CHANNELS")
        sys.exit(1)

    for ch in channels:
        prog = ch.get("items") or ch.get("programs") or []
        ch["items"] = [clean_program(p) for p in prog]

    save_json(channels)


if __name__ == "__main__":
    run()

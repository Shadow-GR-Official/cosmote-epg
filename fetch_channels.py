import requests
import json
import sys
import time
import re
from datetime import datetime, timezone


# ----------------------------
# CLEAN PROGRAM
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
# SAFE REQUEST
# ----------------------------
def fetch(session, url, headers):
    try:
        r = session.get(url, headers=headers, timeout=25)
        if r.status_code == 200:
            return r
        print("HTTP Error:", r.status_code)
    except Exception as e:
        print("Request error:", e)

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
# RUN ONE FETCH CYCLE
# ----------------------------
def run_fetch():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()

    # warm-up
    session.get("https://cosmotetv.gr", headers=headers, timeout=20)

    url = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

    print("[EPG 24H] Fetching:", url)

    r = fetch(session, url, headers)

    if not r:
        print("Failed to fetch EPG")
        return

    data = r.json()

    all_channels = extract_channels(data)

    if not all_channels:
        print("No channels found")
        return

    # clean programs
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

    print(f"SUCCESS: Saved {len(all_channels)} channels (24h EPG)")


# ----------------------------
# MAIN LOOP (EVERY 1 HOUR)
# ----------------------------
if __name__ == "__main__":
    while True:
        try:
            run_fetch()
        except Exception as e:
            print("CRITICAL ERROR:", e)

        print("Sleeping 1 hour...\n")
        time.sleep(60 * 60)

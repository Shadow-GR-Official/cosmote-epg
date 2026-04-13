import requests
import json
import sys
import re
import os


# ----------------------------
# FORCE BASE DIRECTORY (LOCKED)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "epg.json")


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
# FETCH (SAFE)
# ----------------------------
def fetch(session, url, headers):
    try:
        r = session.get(url, headers=headers, timeout=25)
        if r.status_code == 200:
            return r
        print("HTTP ERROR:", r.status_code)
    except Exception as e:
        print("REQUEST ERROR:", e)

    return None


# ----------------------------
# EXTRACT CHANNELS
# ----------------------------
def extract_channels(data):
    stripes = data.get("stripes", [])
    channels = []

    if isinstance(stripes, list):
        for stripe in stripes:
            if isinstance(stripe, dict) and "channels" in stripe:
                channels.extend(stripe["channels"])

    elif isinstance(stripes, dict):
        channels = stripes.get("channels", [])

    return channels


# ----------------------------
# ATOMIC SAVE (GUARANTEED SAFE WRITE)
# ----------------------------
def atomic_save_json(data, filename):
    tmp_file = filename + ".tmp"

    # NEVER write empty file
    if not data:
        raise Exception("REFUSING TO WRITE EMPTY DATA")

    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp_file, filename)

    print("✔ SAVED:", filename)
    print("✔ PATH :", os.path.abspath(filename))
    print("✔ SIZE :", os.path.getsize(filename), "bytes")


# ----------------------------
# RUN ONCE
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
    session.get("https://cosmotetv.gr", timeout=20)

    url = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

    print("[EPG] FETCHING...")

    r = fetch(session, url, headers)

    if not r:
        print("FAILED FETCH")
        return

    data = r.json()
    all_channels = extract_channels(data)

    if not all_channels:
        print("NO CHANNELS FOUND (ABORT)")
        return

    # clean
    for ch in all_channels:
        programs = ch.get("items") or ch.get("programs") or []
        ch_clean = [clean_program(p) for p in programs]

        if "items" in ch:
            ch["items"] = ch_clean
        else:
            ch["programs"] = ch_clean

    # save safely
    atomic_save_json(all_channels, OUTPUT_FILE)

    print(f"✔ DONE: {len(all_channels)} channels")


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    try:
        run_fetch()
    except Exception as e:
        print("CRITICAL ERROR:", e)

    sys.exit(0)

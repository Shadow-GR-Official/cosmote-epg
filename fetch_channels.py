import requests
import json
import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "epg.json")

def fetch(session, url, headers):
    try:
        # Χρήση των headers του session που ορίσαμε στο run()
        r = session.get(url, timeout=20)
        if r.status_code == 200:
            return r
        print(f"HTTP ERROR: {r.status_code}")
        # Αν επιστρέφει 500, εκτυπώνουμε ένα μέρος του περιεχομένου για debugging
        if r.status_code == 500:
            print("Server logic error or Bot detection triggered.")
    except Exception as e:
        print("REQUEST ERROR:", e)
    return None

def extract_channels(data):
    # Το API επιστρέφει συνήθως μια λίστα από stripes
    stripes = data.get("stripes", [])
    channels = []
    
    for s in stripes:
        if isinstance(s, dict) and "channels" in s:
            channels.extend(s["channels"])
    return channels

def clean_program(p):
    if not isinstance(p, dict):
        return p
    desc = p.get("description") or ""
    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        p["episode"] = match.group(1).strip()
        desc = desc.replace(match.group(0), "")
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}(:\d{2})?", "", desc)
    p["description"] = re.sub(r"\s{2,}", " ", desc).strip()
    return p

def save_json(data):
    tmp = JSON_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, JSON_FILE)
    print(f"✔ epg.json saved: {JSON_FILE}")
    print(f"✔ channels: {len(data)}")

def run():
    # Πιο "ανθρώπινα" headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9,en-US;q=0.8",
        "Referer": "https://cosmotetv.gr",
        "Origin": "https://www.cosmotetv.gr",
        "Connection": "keep-alive"
    }

    session = requests.Session()
    session.headers.update(headers)

    # 1. Πρώτα χτυπάμε την κεντρική σελίδα για να πάρουμε τα απαραίτητα cookies (π.χ. TS01...)
    print("[INIT] Getting cookies...")
    try:
        session.get("https://cosmotetv.gr", timeout=20)
    except:
        pass

    # 2. Κλήση του API
    url = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"
    print("[FETCH] Getting EPG data...")

    r = fetch(session, url, headers)
    if not r:
        print("FAILED FETCH")
        sys.exit(1)

    try:
        data = r.json()
    except Exception as e:
        print("JSON DECODE ERROR:", e)
        sys.exit(1)

    channels = extract_channels(data)

    if not channels:
        print("NO CHANNELS FOUND IN DATA")
        sys.exit(1)

    for ch in channels:
        # Η Cosmote συνήθως χρησιμοποιεί το κλειδί 'programs' στο API
        prog = ch.get("programs") or ch.get("items") or []
        ch["items"] = [clean_program(p) for p in prog]

    save_json(channels)

if __name__ == "__main__":
    run()

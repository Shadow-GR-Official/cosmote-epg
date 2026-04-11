import requests
import json
import sys
from datetime import datetime

# Προσθέτουμε την ημερομηνία στο URL (YYYY-MM-DD)
current_date = datetime.now().strftime("%Y-%m-%d")
API = f"https://cosmotetv.gr{current_date}"

def extract_channels(data):
    if not isinstance(data, dict): return []
    if isinstance(data.get("stripes"), list):
        for item in data["stripes"]:
            if isinstance(item, dict) and isinstance(item.get("channels"), list):
                return item["channels"]
    return []

def normalize_channel(ch):
    if not isinstance(ch, dict): return None
    channel_id = ch.get("id") or ch.get("guid") or ch.get("number")
    if not channel_id: return None
    return {
        "id": str(channel_id),
        "name": ch.get("title") or ch.get("name") or "UNKNOWN",
        "programs": ch.get("programs", []) # Παίρνουμε και τα προγράμματα εδώ!
    }

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Referer": "https://cosmotetv.gr",
    }

    try:
        r = requests.get(API, headers=headers, timeout=20)
        if r.status_code != 200:
            print(f"Σφάλμα API: {r.status_code}")
            sys.exit(1)

        data = r.json()
        channels_raw = extract_channels(data)
        
        # Εδώ σώζουμε ΟΛΑ τα δεδομένα (κανάλια + προγράμματα) στο epg.json
        channels_with_programs = []
        for ch in channels_raw:
            norm = normalize_channel(ch)
            if norm:
                channels_with_programs.append(norm)

        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_with_programs, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved data for {len(channels_with_programs)} channels")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

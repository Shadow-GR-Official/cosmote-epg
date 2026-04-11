import requests
import json
import sys
import time

def main():
    # 1. Δυναμικά timestamps (Σήμερα 00:00 έως αύριο 00:00)
    # Χρησιμοποιούμε στρογγυλά νούμερα που προτιμάει η Cosmote
    start_ts = int(time.time() // 3600 * 3600) 
    end_ts = start_ts + 86400 

    # 2. Καθαρό URL χωρίς έξτρα κενά
    API = f"https://www.cosmotetv.gr/api/channels/schedule?locale=el&from={start_ts}&to={end_ts}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }

    session = requests.Session()
    
    try:
        print(f"Target URL: {API}")
        
        # ΒΗΜΑ 1: Παίρνουμε φρέσκα cookies από το portal
        session.get("https://cosmotetv.gr", headers=headers, timeout=20)
        
        # ΒΗΜΑ 2: Κλήση API
        r = session.get(API, headers=headers, timeout=25)
        
        if r.status_code != 200:
            print(f"API Error {r.status_code}: {r.text[:200]}")
            sys.exit(1)

        data = r.json()
        all_channels = []

        # Εξαγωγή όλων των καναλιών από όλα τα stripes
        stripes = data.get("stripes", [])
        if isinstance(stripes, list):
            for stripe in stripes:
                if isinstance(stripe, dict) and "channels" in stripe:
                    all_channels.extend(stripe["channels"])
        elif isinstance(stripes, dict):
            all_channels = stripes.get("channels", [])

        if not all_channels:
            print("No channels found in response.")
            sys.exit(1)

        # Αποθήκευση στο epg.json
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(all_channels, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(all_channels)} channels to epg.json")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

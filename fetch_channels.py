import requests
import json
import sys
import time

def main():
    # 1. Υπολογισμός Timestamps (48 ώρες πρόγραμμα)
    start_ts = int(time.time()) - 36000  # 10 ώρες πίσω
    end_ts = start_ts + 172800           # +48 ώρες

    # 2. Το σταθερό API URL
    API_URL = "https://cosmotetv.gr"
    
    # 3. Οι παράμετροι ξεχωριστά για να μην γίνει λάθος στο URL
    params = {
        "locale": "el",
        "from": start_ts,
        "to": end_ts
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        print(f"Fetching EPG from {start_ts} to {end_ts}...")
        # Warm up session
        session.get("https://cosmotetv.gr", headers=headers, timeout=15)
        
        # Κλήση API με params
        r = session.get(API_URL, params=params, headers=headers, timeout=20)
        
        print(f"Request URL: {r.url}") # Για να βλέπουμε αν χτίστηκε σωστά
        
        if r.status_code != 200:
            print(f"API Error: {r.status_code}")
            sys.exit(1)

        data = r.json()
        
        channels_raw = []
        if isinstance(data.get("stripes"), list):
            for item in data["stripes"]:
                if isinstance(item, dict) and "channels" in item:
                    channels_raw = item["channels"]
                    break
        elif isinstance(data.get("stripes"), dict):
            channels_raw = data["stripes"].get("channels", [])

        if not channels_raw:
            print("No channels found in response.")
            sys.exit(1)

        # Αποθήκευση
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)
            
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(channels_raw)} channels.")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

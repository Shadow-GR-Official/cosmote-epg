import requests
import json
import sys
import time

def main():
    # 1. Υπολογίζουμε τα Timestamps (από χθες το βράδυ μέχρι αύριο το βράδυ)
    # 172800 δευτερόλεπτα = 48 ώρες για να είμαστε σίγουροι
    start_ts = int(time.time()) - 36000  # 10 ώρες πίσω από τώρα
    end_ts = start_ts + 172800           # 48 ώρες πρόγραμμα

    # 2. Το "ακριβές" API URL που χρησιμοποιεί η Cosmote
    API = f"https://cosmotetv.gr{start_ts}&to={end_ts}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        print(f"Fetching 48h EPG from {start_ts} to {end_ts}...")
        # Hit th σελίδα για cookies
        session.get("https://cosmotetv.gr", headers=headers, timeout=15)
        
        # Κλήση API
        r = session.get(API, headers=headers, timeout=20)
        
        if r.status_code != 200:
            print(f"API Error: {r.status_code}")
            sys.exit(1)

        data = r.json()
        
        # Εξαγωγή καναλιών από το stripes
        channels_raw = []
        if isinstance(data.get("stripes"), list):
            for item in data["stripes"]:
                if "channels" in item:
                    channels_raw = item["channels"]
                    break
        
        if not channels_raw:
            print("No channels found in API response.")
            sys.exit(1)

        # Αποθήκευση στο epg.json
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)
            
        # Αποθήκευση και στο channels.json για το άλλο script
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(channels_raw)} channels with full 48h schedule.")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

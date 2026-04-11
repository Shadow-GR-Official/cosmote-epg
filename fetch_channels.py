import requests
import json
import sys
import time
from datetime import datetime, time as dt_time

def main():
    # 1. Υπολογισμός "στρογγυλών" timestamps για το σημερινό 24ωρο (00:00 έως 23:59)
    today = datetime.combine(datetime.now(), dt_time.min)
    start_ts = int(today.timestamp())
    end_ts = start_ts + 86399 # +24 ώρες μείον 1 δευτερόλεπτο

    # 2. Χτίζουμε το URL με τα σωστά timestamps
    API = f"https://www.cosmotetv.gr/api/channels/schedule?locale=el&from={start_ts}&to={end_ts}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        print(f"Target URL: {API}")
        
        # Προθέρμανση session για cookies
        session.get("https://cosmotetv.gr", headers=headers, timeout=20)
        
        # Κλήση API
        r = session.get(API, headers=headers, timeout=25)
        
        if r.status_code != 200:
            print(f"API Error: {r.status_code}")
            sys.exit(1)

        data = r.json()
        
        # Εξαγωγή καναλιών από το stripes
        channels_raw = []
        if isinstance(data.get("stripes"), list):
            for item in data["stripes"]:
                if isinstance(item, dict) and "channels" in item:
                    channels_raw = item["channels"]
                    break
        elif isinstance(data.get("stripes"), dict):
            channels_raw = data["stripes"].get("channels", [])

        if not channels_raw:
            print("No data found in stripes.")
            sys.exit(1)

        # Αποθήκευση στα αρχεία
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)
            
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Φορτώθηκαν {len(channels_raw)} κανάλια για το 24ωρο.")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

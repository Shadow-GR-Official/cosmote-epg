import requests
import json
import sys
import time

def main():
    # 1. Timestamps για 48 ώρες
    start_ts = int(time.time()) - 36000
    end_ts = start_ts + 172800

    # 2. Χτίζουμε το URL χειροκίνητα για σιγουριά
    API = f"https://cosmotetv.gr{start_ts}&to={end_ts}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }

    session = requests.Session()
    
    try:
        print(f"Target API: {API}")
        
        # Βήμα 1: Παίρνουμε cookies από την κεντρική σελίδα
        session.get("https://cosmotetv.gr", headers=headers, timeout=15)
        
        # Βήμα 2: Καλούμε το API (απενεργοποιούμε το allow_redirects για να δούμε αν μας διώχνει)
        r = session.get(API, headers=headers, timeout=20, allow_redirects=False)
        
        if r.status_code != 200:
            print(f"API Error {r.status_code}. Possible redirect or block.")
            sys.exit(1)

        data = r.json()
        
        # Εξαγωγή καναλιών
        channels_raw = []
        if "stripes" in data:
            stripes = data["stripes"]
            if isinstance(stripes, list):
                for s in stripes:
                    if "channels" in s:
                        channels_raw = s["channels"]
                        break
            elif isinstance(stripes, dict):
                channels_raw = stripes.get("channels", [])

        if not channels_raw:
            print("No channels found in JSON.")
            sys.exit(1)

        # Αποθήκευση
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)
            
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Fetched {len(channels_raw)} channels.")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

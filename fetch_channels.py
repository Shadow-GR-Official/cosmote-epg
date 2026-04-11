import requests
import json
import sys
import time

def main():
    # 1. Timestamps για 48 ώρες
    start_ts = int(time.time()) - 36000
    end_ts = start_ts + 172800

    # 2. Χτίζουμε το URL με τον πιο απλό τρόπο (concatenation) για να μην γίνει λάθος
    base_url = "https://cosmotetv.gr"
    query = "?locale=el&from=" + str(start_ts) + "&to=" + str(end_ts)
    API = base_url + query

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        print("Target URL: " + API)
        
        # Προθέρμανση session
        session.get("https://cosmotetv.grportal/el/epg/program", headers=headers, timeout=15)
        
        # Κλήση API
        r = session.get(API, headers=headers, timeout=20)
        
        if r.status_code != 200:
            print("API Error: " + str(r.status_code))
            sys.exit(1)

        data = r.json()
        
        # Εξαγωγή καναλιών (το API επιστρέφει stripes -> [ {channels: []} ])
        channels_raw = []
        if isinstance(data.get("stripes"), list):
            for item in data["stripes"]:
                if isinstance(item, dict) and "channels" in item:
                    channels_raw = item["channels"]
                    break
        elif isinstance(data.get("stripes"), dict):
             channels_raw = data["stripes"].get("channels", [])

        if not channels_raw:
            print("No channels found in JSON structure.")
            sys.exit(1)

        # Αποθήκευση
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)
            
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print("SUCCESS: Fetched " + str(len(channels_raw)) + " channels.")

    except Exception as e:
        print("CRITICAL ERROR: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

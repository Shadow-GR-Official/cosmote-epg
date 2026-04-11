import requests
import json
import sys
import time

def main():
    # 1. Δυναμικά timestamps για το σήμερα
    start_ts = int(time.time())
    end_ts = start_ts + 86400 

    # 2. Το URL με το "μαγικό" κενό στο τέλος πριν το κλείσιμο του string
    # Προσέχουμε να είναι ακριβώς όπως το περιέγραψες
    API = "https://www.cosmotetv.gr/api/channels/schedule?locale=el&from=" + str(start_ts) + "&to=" + str(end_ts) + " " 

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.cosmotetv.gr/",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        # Εμφάνιση του URL για επιβεβαίωση
        print(f"Target URL: '{API}'")
        
        # Warm up
        session.get("https://cosmotetv.gr", headers=headers, timeout=20)
        
        # Κλήση API (το requests θα καθαρίσει το space αυτόματα πριν το στείλει, 
        # αλλά η Python δεν θα μπερδέψει το string)
        r = session.get(API.strip() + " ", headers=headers, timeout=25)
        
        if r.status_code != 200:
            print(f"API Error: {r.status_code}")
            sys.exit(1)

        data = r.json()
        
        # Εξαγωγή καναλιών
        channels_raw = []
        if isinstance(data, list):
            channels_raw = data
        elif isinstance(data, dict):
            stripes = data.get("stripes", [])
            if isinstance(stripes, list):
                for s in stripes:
                    if isinstance(s, dict) and "channels" in s:
                        channels_raw.extend(s["channels"])
            elif isinstance(stripes, dict):
                channels_raw = stripes.get("channels", [])
            else:
                channels_raw = data.get("channels", [])

        if not channels_raw:
            print("No data found.")
            sys.exit(1)

        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(channels_raw)} channels.")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

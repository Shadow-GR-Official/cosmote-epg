import requests
import json
import sys
import time

def main():
    # 1. Δυναμικός υπολογισμός Timestamps για το "Τώρα"
    # start_ts: Η τρέχουσα στιγμή (Unix Timestamp)
    # end_ts: Μετά από 24 ώρες
    start_ts = int(time.time())
    end_ts = start_ts + 86400 

    # 2. Χτίζουμε το URL με τα φρέσκα Timestamps
    API = f"https://cosmotetv.gr{start_ts}&to={end_ts}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        print(f"Fetching fresh EPG starting from: {time.ctime(start_ts)}")
        
        # Προθέρμανση session για cookies
        session.get("https://cosmotetv.gr", headers=headers, timeout=20)
        
        # Κλήση API
        r = session.get(API, headers=headers, timeout=25)
        
        if r.status_code != 200:
            print(f"API Error: {r.status_code}")
            sys.exit(1)

        data = r.json()
        
        # Εξαγωγή καναλιών από το stripes (Format που είδαμε στο JSON σου)
        channels_raw = []
        if isinstance(data.get("stripes"), list):
            for item in data["stripes"]:
                if isinstance(item, dict) and "channels" in item:
                    channels_raw = item["channels"]
                    break
        elif isinstance(data.get("stripes"), dict):
            channels_raw = data["stripes"].get("channels", [])
        else:
            # Fallback αν το JSON είναι απευθείας λίστα
            channels_raw = data if isinstance(data, list) else []

        if not channels_raw:
            print("No fresh data found in API response.")
            sys.exit(1)

        # Αποθήκευση στο epg.json για το generate_epg.py
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(channels_raw)} channels with CURRENT schedule.")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

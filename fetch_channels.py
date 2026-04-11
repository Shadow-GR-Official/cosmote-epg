import requests
import json
import sys
import time

def main():
    # 1. Δυναμικά timestamps
    start_ts = int(time.time())
    end_ts = start_ts + 86400 

    # 2. Χτίσιμο URL κομμάτι-κομμάτι για να αποφύγουμε το NameResolutionError
    base = "https://cosmotetv.gr"
    params = "?locale=el&from=" + str(start_ts) + "&to=" + str(end_ts)
    full_url = base + params

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        print("Target URL: " + full_url)
        
        # Προθέρμανση session
        session.get("https://cosmotetv.grportal/el/epg/program", headers=headers, timeout=20)
        
        # Κλήση API
        r = session.get(full_url, headers=headers, timeout=25)
        
        if r.status_code != 200:
            print("API Error: " + str(r.status_code))
            sys.exit(1)

        data = r.json()
        
        # Εξαγωγή καναλιών (δοκιμή όλων των πιθανών structure της Cosmote)
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
            print("No data found in JSON response.")
            sys.exit(1)

        # Αποθήκευση στο epg.json
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print("SUCCESS: Saved " + str(len(channels_raw)) + " channels to epg.json")

    except Exception as e:
        print("CRITICAL ERROR: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

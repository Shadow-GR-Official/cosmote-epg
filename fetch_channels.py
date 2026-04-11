import requests
import json
import sys
import time
from urllib.parse import urljoin

def fetch_data(url, headers, session, retries=3, delay=5):
    for i in range(retries):
        try:
            print(f"Προσπάθεια {i+1} από {retries}...")
            r = session.get(url, headers=headers, timeout=25)
            if r.status_code == 200:
                data = r.json()
                if data.get("stripes"):
                    return data
                print("Το API επέστρεψε κενά δεδομένα.")
            else:
                print(f"Σφάλμα API: {r.status_code}")
        except Exception as e:
            print(f"Σφάλμα σύνδεσης: {str(e)}")
        
        time.sleep(delay)
    return None

def main():
    start_ts = int(time.time()) - 36000
    end_ts = start_ts + 172800
    
    # Ασφαλές χτίσιμο URL
    base_domain = "https://cosmotetv.gr"
    api_path = "api/channels/schedule"
    portal_path = "portal/el/epg/program"
    
    full_api_url = urljoin(base_domain, api_path) + f"?locale=el&from={start_ts}&to={end_ts}"
    full_portal_url = urljoin(base_domain, portal_path)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": base_domain,
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        print("Target URL: " + full_api_url)
        # Προθέρμανση με σωστό URL
        session.get(full_portal_url, headers=headers, timeout=20)
        
        data = fetch_data(full_api_url, headers, session)
        
        if not data:
            print("Αποτυχία λήψης δεδομένων.")
            sys.exit(1)

        channels_raw = []
        stripes = data.get("stripes", [])
        if isinstance(stripes, list):
            for item in stripes:
                if isinstance(item, dict) and "channels" in item:
                    channels_raw = item["channels"]
                    break
        elif isinstance(stripes, dict):
            channels_raw = stripes.get("channels", [])

        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels_raw, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Φορτώθηκαν {len(channels_raw)} κανάλια.")

    except Exception as e:
        print("CRITICAL ERROR: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

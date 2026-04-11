import requests
import json
import sys

# Το endpoint παραμένει το ίδιο
API = "https://cosmotetv.gr"

def extract_channels(data):
    if not isinstance(data, dict): return []
    # Η Cosmote αλλάζει συχνά το structure, ψάχνουμε παντού για τη λίστα καναλιών
    if isinstance(data.get("stripes"), list):
        for item in data["stripes"]:
            if isinstance(item, dict) and isinstance(item.get("channels"), list):
                return item["channels"]
    return data.get("channels", [])

def normalize_channel(ch):
    if not isinstance(ch, dict): return None
    cid = ch.get("id") or ch.get("guid") or ch.get("number")
    if not cid: return None
    
    logos = ch.get("logos", {})
    logo_url = logos.get("square") if isinstance(logos, dict) else None
    
    return {
        "id": str(cid),
        "name": ch.get("title") or ch.get("name") or "Unknown",
        "logo": logo_url,
        "number": ch.get("number")
    }

def main():
    # Αυτά τα headers είναι "μαγικά" για να μην τρως 500 error
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    session = requests.Session()
    
    try:
        # Βήμα 1: "Ζεστάνουμε" το session επισκεπτόμενοι την κεντρική σελίδα
        print("Initializing session...")
        session.get("https://cosmotetv.gr", headers=headers, timeout=15)
        
        # Βήμα 2: Κλήση του API
        print(f"Fetching channels from API...")
        r = session.get(API, headers=headers, timeout=15)
        
        if r.status_code != 200:
            print(f"FAILED: Server returned status {r.status_code}")
            # Αν αποτύχει, εκτυπώνουμε ένα μέρος της απάντησης για να δούμε τι φταίει
            print("Response hint:", r.text[:200])
            sys.exit(1)

        data = r.json()
        raw_list = extract_channels(data)
        channels = [norm for ch in raw_list if (norm := normalize_channel(ch))]

        if not channels:
            print("ERROR: API returned 200 but no channels were found in the JSON.")
            sys.exit(1)

        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(channels)} channels to channels.json")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

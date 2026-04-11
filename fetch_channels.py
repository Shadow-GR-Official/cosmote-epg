import requests
import json
import sys

API = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

def extract_channels(data):
    if not isinstance(data, dict):
        return []
    if isinstance(data.get("stripes"), list):
        for item in data["stripes"]:
            if isinstance(item, dict) and isinstance(item.get("channels"), list):
                return item["channels"]
    return []

def normalize_channel(ch):
    if not isinstance(ch, dict) or (ch.get("type") and ch.get("type") != "channel"):
        return None
    channel_id = ch.get("id") or ch.get("guid") or ch.get("number")
    name = ch.get("title") or ch.get("name") or "UNKNOWN"
    logos = ch.get("logos", {})
    logo = logos.get("square") if isinstance(logos, dict) else None
    if not channel_id: return None
    return {"id": str(channel_id), "name": name, "logo": logo, "number": ch.get("number")}

def main():
    # Ενισχυμένα headers για αποφυγή του 500 error
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    
    try:
        # Βήμα 1: Χτυπάμε τη σελίδα για να πάρουμε τα cookies
        session.get("https://cosmotetv.gr", headers=headers, timeout=15)
        
        # Βήμα 2: Καλούμε το API με το ίδιο session
        r = session.get(API, headers=headers, timeout=15)
        print(f"STATUS: {r.status_code}")

        if r.status_code != 200:
            print(f"ERROR: API returned {r.status_code}")
            sys.exit(1)

        data = r.json()
        channels_raw = extract_channels(data)
        
        channels = [normalized for ch in channels_raw if (normalized := normalize_channel(ch))]

        if not channels:
            print("ERROR: No channels found")
            sys.exit(1)

        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(channels)} channels")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

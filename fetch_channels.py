import requests
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(BASE_DIR, "epg.json")


def fetch(session, url, headers):
    try:
        r = session.get(url, headers=headers, timeout=25)
        if r.status_code == 200:
            return r
        print("HTTP ERROR:", r.status_code)
    except Exception as e:
        print("REQUEST ERROR:", e)
    return None


def extract_channels(data):
    stripes = data.get("stripes", [])
    channels = []

    if isinstance(stripes, list):
        for s in stripes:
            if isinstance(s, dict) and "channels" in s:
                channels.extend(s["channels"])

    elif isinstance(stripes, dict):
        channels = stripes.get("channels", [])

    return channels


def run():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://cosmotetv.gr"
    }

    session = requests.Session()
    session.get("https://cosmotetv.gr", timeout=20)

    url = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

    print("[FETCH] downloading EPG...")

    r = fetch(session, url, headers)
    if not r:
        print("FAILED")
        return

    data = r.json()
    channels = extract_channels(data)

    if not channels:
        print("EMPTY DATA")
        return

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print("OK JSON SAVED:", OUTPUT_JSON)


if __name__ == "__main__":
    run()

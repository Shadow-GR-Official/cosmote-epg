import requests
import json

API = "https://www.cosmotetv.gr/api/channels?locale=el"

def main():
    r = requests.get(API, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    data = r.json()

    channels = []

    for ch in data:
        if ch.get("type") != "channel":
            continue

        channels.append({
            "id": ch.get("guid"),
            "name": ch.get("title"),
            "callSign": ch.get("callSign"),
            "logo": (ch.get("logos") or {}).get("square")
        })

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"Loaded {len(channels)} channels")

if __name__ == "__main__":
    main()

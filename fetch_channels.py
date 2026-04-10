import requests
import json

CHANNELS_API = "https://www.cosmotetv.gr/api/channels"

def main():
    r = requests.get(CHANNELS_API, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    try:
        data = r.json()
    except:
        print("Response is not JSON:")
        print(r.text)
        return

    channels = []

    # περίπτωση 1: dict με key
    if isinstance(data, dict):
        data = data.get("channels", [])

    # περίπτωση 2: list
    if isinstance(data, list):
        for ch in data:
            if isinstance(ch, dict):
                channels.append({
                    "id": ch.get("id"),
                    "name": ch.get("name", ch.get("id"))
                })
            elif isinstance(ch, str):
                channels.append({
                    "id": ch,
                    "name": ch
                })

    else:
        print("Unknown format:", type(data))
        return

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(channels)} channels.")

if __name__ == "__main__":
    main()

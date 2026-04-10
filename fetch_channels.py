import requests
import json

CHANNELS_API = "https://www.cosmotetv.gr/api/channels"

def main():
    r = requests.get(CHANNELS_API)
    data = r.json()

    channels = []

    for ch in data:
        channels.append({
            "id": ch.get("id"),
            "name": ch.get("name", ch.get("id"))
        })

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(channels)} channels.")

if __name__ == "__main__":
    main()

import requests
import json

API = "https://www.cosmotetv.gr/api/channels?locale=el"

def main():
    r = requests.get(API, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    try:
        data = r.json()
    except:
        print("Not JSON response:")
        print(r.text)
        return

    channels = []

    # unwrap πιθανών formats
    if isinstance(data, dict):
        data = data.get("channels", data.get("data", []))

    if not isinstance(data, list):
        print("Unexpected format:", type(data))
        return

    for ch in data:

        # CASE 1: dict object
        if isinstance(ch, dict):
            if ch.get("type") and ch.get("type") != "channel":
                continue

            channels.append({
                "id": ch.get("guid") or ch.get("id"),
                "name": ch.get("title") or ch.get("name"),
                "logo": ((ch.get("logos") or {}).get("square"))
            })

        # CASE 2: string ID
        elif isinstance(ch, str):
            channels.append({
                "id": ch,
                "name": ch
            })

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(channels)} channels")

if __name__ == "__main__":
    main()

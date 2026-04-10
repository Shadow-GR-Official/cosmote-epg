import requests
import json

API = "https://www.cosmotetv.gr/api/channels/schedule"

def main():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.cosmotetv.gr/"
    }

    r = requests.get(API, headers=headers, timeout=20)

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("content-type"))

    try:
        data = r.json()
    except Exception:
        print("ERROR: Response is not JSON")
        print(r.text[:500])
        return

    # 🔍 DEBUG: δες structure
    print("TOP KEYS:", list(data.keys()) if isinstance(data, dict) else type(data))

    channels = []

    """
    Most likely structures:
    1) data["channels"]
    2) data["items"]
    3) data["data"]["channels"]
    """

    if isinstance(data, dict):

        if "channels" in data:
            raw = data["channels"]

        elif "data" in data and isinstance(data["data"], dict):
            raw = data["data"].get("channels", [])

        else:
            raw = []

    else:
        raw = []

    for ch in raw:
        if isinstance(ch, dict):
            channels.append({
                "id": ch.get("id") or ch.get("guid"),
                "name": ch.get("name") or ch.get("title")
            })

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(channels)} channels")


if __name__ == "__main__":
    main()

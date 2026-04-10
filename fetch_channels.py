import requests
import json


API = "https://www.cosmotetv.gr/api/channels?locale=el"


def extract_channels(data):
    """
    Try to robustly extract channel list from different possible API formats.
    """
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    # common keys used by APIs
    possible_keys = ["channels", "data", "result", "items", "entries"]

    for key in possible_keys:
        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            # sometimes nested again
            for subkey in ["channels", "items", "data"]:
                subvalue = value.get(subkey)
                if isinstance(subvalue, list):
                    return subvalue

    return []


def main():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.cosmotetv.gr/"
    }

    r = requests.get(API, headers=headers, timeout=20)

    # 🔍 Debug HTTP issues
    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("content-type"))

    if r.status_code != 200:
        print("Request failed:")
        print(r.text[:500])
        return

    # 🔍 Parse JSON safely
    try:
        data = r.json()
    except Exception:
        print("Response is not valid JSON. First 500 chars:")
        print(r.text[:500])
        return

    # 🔍 Extract channels
    data = extract_channels(data)

    if not data:
        print("No channels found after parsing.")
        print("Raw JSON preview:", json.dumps(data, indent=2)[:500])
        return

    channels = []

    for ch in data:

        # CASE 1: dict format
        if isinstance(ch, dict):

            if ch.get("type") and ch.get("type") != "channel":
                continue

            channels.append({
                "id": ch.get("guid") or ch.get("id"),
                "name": ch.get("title") or ch.get("name"),
                "logo": (
                    ch.get("logos", {}).get("square")
                    if isinstance(ch.get("logos"), dict)
                    else None
                )
            })

        # CASE 2: string IDs
        elif isinstance(ch, str):
            channels.append({
                "id": ch,
                "name": ch
            })

    # Save output
    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(channels)} channels")


if __name__ == "__main__":
    main()

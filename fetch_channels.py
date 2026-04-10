import requests
import json
import sys

API = "https://www.cosmotetv.gr/api/channels?locale=el"


def extract_channels(data):
    """
    Try to extract channel list from multiple possible API formats.
    """
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    # common API keys
    for key in ["channels", "data", "result", "items", "entries"]:
        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            for subkey in ["channels", "items", "data"]:
                subvalue = value.get(subkey)
                if isinstance(subvalue, list):
                    return subvalue

    return []


def main():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
        "Referer": "https://www.cosmotetv.gr/",
        "Origin": "https://www.cosmotetv.gr",
    }

    try:
        r = requests.get(API, headers=headers, timeout=20)
    except Exception as e:
        print("REQUEST FAILED:", e)
        sys.exit(1)

    print("STATUS:", r.status_code)
    content_type = r.headers.get("content-type")
    print("CONTENT-TYPE:", content_type)

    if r.status_code != 200:
        print("ERROR: Non-200 response")
        print(r.text[:500])
        sys.exit(1)

    # ensure JSON
    try:
        data = r.json()
    except Exception:
        print("ERROR: Response is not JSON")
        print(r.text[:1000])
        sys.exit(1)

    # extract channels
    raw_channels = extract_channels(data)

    if not raw_channels:
        print("ERROR: No channels found in API response.")
        print("DEBUG SAMPLE:", json.dumps(data, indent=2)[:1000])
        sys.exit(1)

    channels = []

    for ch in raw_channels:

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

        elif isinstance(ch, str):
            channels.append({
                "id": ch,
                "name": ch
            })

    if not channels:
        print("ERROR: Parsed channels list is empty.")
        sys.exit(1)

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Saved {len(channels)} channels")


if __name__ == "__main__":
    main()

import requests
import json
import sys

API = "https://www.cosmotetv.gr/api/channels?locale=el"


def extract_channels(data):
    """
    Extract channels from multiple possible Cosmote API structures.
    """

    if not isinstance(data, dict):
        return []

    # Case 1: stripes as dict
    if isinstance(data.get("stripes"), dict):
        channels = data["stripes"].get("channels")
        if isinstance(channels, list):
            return channels

    # Case 2: stripes as list
    if isinstance(data.get("stripes"), list):
        for item in data["stripes"]:
            if isinstance(item, dict) and isinstance(item.get("channels"), list):
                return item["channels"]

    # Generic fallbacks
    for key in ["channels", "data", "result", "items"]:
        if isinstance(data.get(key), list):
            return data[key]

        if isinstance(data.get(key), dict):
            for subkey in ["channels", "items"]:
                if isinstance(data[key].get(subkey), list):
                    return data[key][subkey]

    return []


def normalize_channel(ch):
    """
    Normalize Cosmote channel into stable schema.
    """

    if not isinstance(ch, dict):
        return None

    # skip non-channel items
    if ch.get("type") and ch.get("type") != "channel":
        return None

    channel_id = (
        ch.get("id")
        or ch.get("guid")
        or ch.get("channel_id")
        or (ch.get("channel", {}) if isinstance(ch.get("channel"), dict) else {}).get("guid")
        or ch.get("number")
    )

    name = ch.get("title") or ch.get("name") or "UNKNOWN"

    logos = ch.get("logos")
    logo = None
    if isinstance(logos, dict):
        logo = logos.get("square") or logos.get("logo")

    number = ch.get("number")

    if not channel_id:
        return None

    return {
        "id": str(channel_id),
        "name": name,
        "logo": logo,
        "number": number
    }


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
        print("ERROR: request failed", str(e))
        sys.exit(1)

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("content-type"))

    if r.status_code != 200:
        print("ERROR: HTTP request failed")
        print(r.text[:500])
        sys.exit(1)

    try:
        data = r.json()
    except Exception:
        print("ERROR: response is not JSON")
        print(r.text[:500])
        sys.exit(1)

    channels_raw = extract_channels(data)

    if not channels_raw:
        print("ERROR: No channels found after extraction")
        print(json.dumps(data, indent=2)[:1000])
        sys.exit(1)

    channels = []

    for ch in channels_raw:
        normalized = normalize_channel(ch)
        if normalized:
            channels.append(normalized)

    if not channels:
        print("ERROR: parsed channels empty after normalization")
        sys.exit(1)

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Saved {len(channels)} channels")


if __name__ == "__main__":
    main()

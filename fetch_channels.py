import requests
import json
import sys

API = "https://www.cosmotetv.gr/api/channels?locale=el"


def extract_channels(data):
    """
    Extract channels from known Cosmote TV API structure.
    """

    if not isinstance(data, dict):
        return []

    # ✅ REAL STRUCTURE (your debug output)
    if "stripes" in data and isinstance(data["stripes"], dict):
        if isinstance(data["stripes"].get("channels"), list):
            return data["stripes"]["channels"]

    # fallback (just in case API changes again)
    for key in ["channels", "data", "result", "items"]:
        if isinstance(data.get(key), list):
            return data[key]

        if isinstance(data.get(key), dict):
            for subkey in ["channels", "items"]:
                if isinstance(data[key].get(subkey), list):
                    return data[key][subkey]

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

    r = requests.get(API, headers=headers, timeout=20)

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("content-type"))

    if r.status_code != 200:
        print("ERROR: request failed")
        print(r.text[:500])
        sys.exit(1)

    try:
        data = r.json()
    except Exception:
        print("ERROR: not JSON")
        print(r.text[:500])
        sys.exit(1)

    channels_raw = extract_channels(data)

    if not channels_raw:
        print("ERROR: No channels found (after extraction)")
        print(json.dumps(data, indent=2)[:1000])
        sys.exit(1)

    channels = []

    for ch in channels_raw:
        if isinstance(ch, dict):

            if ch.get("type") and ch.get("type") != "channel":
                continue

            channels.append({
                "id": ch.get("guid") or ch.get("id"),
                "name": ch.get("title") or ch.get("name"),
                "logo": ch.get("logos", {}).get("square") if isinstance(ch.get("logos"), dict) else None,
                "number": ch.get("number")
            })

    if not channels:
        print("ERROR: parsed channels empty")
        sys.exit(1)

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Saved {len(channels)} channels")


if __name__ == "__main__":
    main()

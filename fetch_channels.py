import requests
import json
import xml.etree.ElementTree as ET

API = "https://www.cosmotetv.gr/api/channels?locale=el"


def try_json(text):
    try:
        return json.loads(text)
    except:
        return None


def try_xml(text):
    try:
        return ET.fromstring(text)
    except:
        return None


def extract_from_json(data):
    if not isinstance(data, dict):
        return []

    if "stripes" in data and "channels" in data["stripes"]:
        return data["stripes"]["channels"]

    return []


def extract_from_xml(root):
    channels = []
    for ch in root.findall("channel"):
        channels.append({
            "id": ch.get("id"),
            "name": ch.findtext("display-name")
        })
    return channels


def main():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://www.cosmotetv.gr/"
    }

    r = requests.get(API, headers=headers, timeout=20)

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("content-type"))

    text = r.text.strip()

    # 1️⃣ Try JSON
    data = try_json(text)
    if data:
        print("Detected JSON response")
        channels_raw = extract_from_json(data)
    else:
        # 2️⃣ Try XML
        root = try_xml(text)
        if root:
            print("Detected XML response")
            channels_raw = extract_from_xml(root)
        else:
            # 3️⃣ FAIL SAFE
            print("ERROR: Unknown response format")
            print(text[:500])
            return

    if not channels_raw:
        print("ERROR: No channels found")
        print(text[:500])
        return

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels_raw, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Saved {len(channels_raw)} channels")


if __name__ == "__main__":
    main()

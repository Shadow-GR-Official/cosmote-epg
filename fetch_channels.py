import requests
import json
import xml.etree.ElementTree as ET

API = "https://www.cosmotetv.gr/api/channels?locale=el"


def main():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.cosmotetv.gr/"
    }

    r = requests.get(API, headers=headers, timeout=20)

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("content-type"))

    if r.status_code != 200:
        print("ERROR: request failed")
        print(r.text[:500])
        return

    try:
        root = ET.fromstring(r.text)
    except Exception as e:
        print("ERROR: XML parse failed:", e)
        print(r.text[:500])
        return

    channels = []

    for ch in root.findall("channel"):
        cid = ch.get("id")
        name = ch.findtext("display-name")

        if cid and name:
            channels.append({
                "id": cid,
                "name": name.strip()
            })

    if not channels:
        print("ERROR: No channels parsed from XML")
        return

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Saved {len(channels)} channels")


if __name__ == "__main__":
    main()

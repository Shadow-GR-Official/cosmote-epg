import requests
import json
import xml.etree.ElementTree as ET

API = "https://www.cosmotetv.gr/api/channels?locale=el"

def main():
    r = requests.get(API, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/xml"
    })

    root = ET.fromstring(r.text)

    channels = []

    for ch in root.findall("channel"):
        channels.append({
            "id": ch.get("id"),
            "name": ch.findtext("display-name")
        })

    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(channels)} channels")

if __name__ == "__main__":
    main()

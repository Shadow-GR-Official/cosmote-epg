import requests
import json
import sys
import time
import re

def clean_program(p):
    desc = p.get("description") or ""

    # 🔹 Extract episode (Επεισόδιο)
    episode = None
    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        episode = match.group(1).strip()
        desc = desc.replace(match.group(0), "")

    # 🔹 Remove ALL duration fields
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)

    # 🔹 Cleanup spaces
    desc = re.sub(r"\s{2,}", " ", desc).strip()

    # 🔹 Save cleaned values
    p["description"] = desc
    if episode:
        p["episode"] = episode

    return p


def main():
    # timestamps
    start_ts = int(time.time() // 3600 * 3600)
    end_ts = start_ts + 86400

    API = f"https://www.cosmotetv.gr/api/channels/schedule?locale=el&from={start_ts}&to={end_ts}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()

    try:
        print(f"Target URL: {API}")

        # cookies
        session.get("https://cosmotetv.gr", headers=headers, timeout=20)

        # API call
        r = session.get(API, headers=headers, timeout=25)

        if r.status_code != 200:
            print(f"API Error {r.status_code}: {r.text[:200]}")
            sys.exit(1)

        data = r.json()
        all_channels = []

        stripes = data.get("stripes", [])
        if isinstance(stripes, list):
            for stripe in stripes:
                if isinstance(stripe, dict) and "channels" in stripe:
                    all_channels.extend(stripe["channels"])
        elif isinstance(stripes, dict):
            all_channels = stripes.get("channels", [])

        if not all_channels:
            print("No channels found.")
            sys.exit(1)

        # 🔥 CLEAN PROGRAMS HERE
        for ch in all_channels:
            programs = ch.get("items") or ch.get("programs") or []
            cleaned = []

            for p in programs:
                cleaned.append(clean_program(p))

            # overwrite cleaned data
            if "items" in ch:
                ch["items"] = cleaned
            else:
                ch["programs"] = cleaned

        # save
        with open("epg.json", "w", encoding="utf-8") as f:
            json.dump(all_channels, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS: Saved {len(all_channels)} channels (cleaned)")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

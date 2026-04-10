import requests
import json

API = "https://www.cosmotetv.gr/api/channels/schedule?"


def main():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.cosmotetv.gr/"
    }

    r = requests.get(API, headers=headers, timeout=20)

    print("STATUS:", r.status_code)

    data = r.json()

    epg = []

    if not isinstance(data, list):
        print("ERROR: unexpected format")
        print(type(data))
        return

    for ch in data:

        channel_id = ch.get("guid") or ch.get("channelGuid")
        channel_name = ch.get("title")

        items = ch.get("items", [])

        programs = []

        for p in items:

            qoe = p.get("qoe", {})

            programs.append({
                "id": p.get("programGuid"),
                "title": qoe.get("title") or p.get("title"),
                "start": p.get("startTime"),
                "end": p.get("endTime"),
                "description": p.get("description"),
                "genre": qoe.get("genre"),
                "thumbnail": (
                    p.get("thumbnails", {}).get("medium")
                    if isinstance(p.get("thumbnails"), dict)
                    else None
                )
            })

        epg.append({
            "channel_id": channel_id,
            "channel_name": channel_name,
            "programs": programs
        })

    with open("epg.json", "w", encoding="utf-8") as f:
        json.dump(epg, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Saved EPG for {len(epg)} channels")


if __name__ == "__main__":
    main()

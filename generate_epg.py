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

    try:
        data = r.json()
    except Exception as e:
        print("ERROR: invalid JSON:", e)
        print(r.text[:500])
        return

    # ✅ correct path
    channels = data.get("stripes", {}).get("channels", [])

    if not channels:
        print("ERROR: no channels found in stripes")
        print(json.dumps(data, indent=2)[:1000])
        return

    epg = []

    for ch in channels:
        channel_id = ch.get("guid")
        channel_name = ch.get("title")

        items = ch.get("items", []) or []

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

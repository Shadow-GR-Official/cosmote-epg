import requests
import json

API = "https://www.cosmotetv.gr/api/channels/schedule?"


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
        "Connection": "keep-alive"
    }

    try:
        r = requests.get(API, headers=headers, timeout=20)
    except Exception as e:
        print("REQUEST FAILED:", e)
        return

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("content-type"))

    # 🔥 HARD STOP if server fails
    if r.status_code != 200:
        print("ERROR: non-200 response")
        print(r.text[:500])
        return

    # 🔥 parse JSON safely
    try:
        data = r.json()
    except Exception:
        print("ERROR: response is not JSON")
        print(r.text[:500])
        return

    # 🔥 debug empty response
    if not data:
        print("ERROR: empty response {}")
        print(r.text[:500])
        return

    # 🔥 correct structure
    channels = data.get("stripes", {}).get("channels", [])

    if not channels:
        print("ERROR: no channels in stripes")
        print(json.dumps(data, indent=2)[:1000])
        return

    epg = []

    for ch in channels:
        channel_id = ch.get("guid")
        channel_name = ch.get("title")

        items = ch.get("items") or []

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

    print(f"SUCCESS: saved EPG for {len(epg)} channels")


if __name__ == "__main__":
    main()

import json
import urllib.parse

with open("data/epg.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

lines = ["#EXTM3U"]

for ch in channels:
    cid = ch.get("id")
    name = ch.get("name", "")
    logo = ch.get("logo", "")

    if not cid:
        continue

    cid_enc = urllib.parse.quote(str(cid))

    lines.append(
        f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" tvg-logo="{logo}",{name}'
    )
    lines.append(f"http://127.0.0.1/{cid_enc}")

with open("data/channels.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("✔ M3U generated")

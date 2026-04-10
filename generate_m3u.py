import json

with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

lines = ["#EXTM3U"]

for ch in channels:
    cid = ch["guid"]
    name = ch.get("title", "")
    logo = ch.get("logos", {}).get("square", "")

    lines.append(
        f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" tvg-logo="{logo}",{name}'
    )
    lines.append(f"http://127.0.0.1/{cid}")

with open("channels.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"SUCCESS: M3U generated for {len(channels)} channels")

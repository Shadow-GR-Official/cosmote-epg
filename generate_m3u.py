import json

def get_id(ch):
    if not isinstance(ch, dict):
        return None

    return (
        ch.get("guid")
        or ch.get("channel_id")
        or (ch.get("channel", {}) if isinstance(ch.get("channel"), dict) else {}).get("guid")
    )

def get_name(ch):
    if not isinstance(ch, dict):
        return ""
    return ch.get("title") or ch.get("name") or ""

def get_logo(ch):
    return (ch.get("logos", {}) or {}).get("square", "")


with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

lines = ["#EXTM3U"]

for ch in channels:
    cid = get_id(ch)
    if not cid:
        continue

    name = get_name(ch)
    logo = get_logo(ch)

    lines.append(f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" tvg-logo="{logo}",{name}')
    lines.append(f"http://127.0.0.1/{cid}")

with open("channels.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"SUCCESS: M3U generated for {len(channels)} channels")

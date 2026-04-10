import json

def get_id(ch):
    if not isinstance(ch, dict):
        return None
    return ch.get("id")  # FIX: your real schema

def get_name(ch):
    if not isinstance(ch, dict):
        return ""
    return ch.get("name") or ""

def get_logo(ch):
    if not isinstance(ch, dict):
        return ""
    return ch.get("logo") or ""


with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

lines = ["#EXTM3U"]

count = 0

for ch in channels:
    cid = get_id(ch)
    name = get_name(ch)
    logo = get_logo(ch)

    if not cid or not name:
        continue

    lines.append(
        f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" tvg-logo="{logo}",{name}'
    )

    lines.append(f"http://127.0.0.1/{cid}")

    count += 1

with open("channels.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"SUCCESS: M3U generated for {count} channels")

import json
import urllib.parse

def safe(v):
    return str(v).strip() if v else ""

def get_id(ch):
    return ch.get("id") if isinstance(ch, dict) else None

def get_name(ch):
    return safe(ch.get("name")) if isinstance(ch, dict) else ""

def get_logo(ch):
    return safe(ch.get("logo")) if isinstance(ch, dict) else ""


with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

lines = ["#EXTM3U"]

count = 0

BASE_STREAM_URL = "http://127.0.0.1"  # άλλαξέ το σε real server αν έχεις

for ch in channels:
    cid = get_id(ch)
    name = get_name(ch)
    logo = get_logo(ch)

    if not cid or not name:
        continue

    # URL encode για safety
    cid_enc = urllib.parse.quote(str(cid))

    name = name.replace(",", " ")

    extinf = (
        f'#EXTINF:-1 '
        f'tvg-id="{cid}" '
        f'tvg-name="{name}" '
        f'tvg-logo="{logo}",{name}'
    )

    lines.append(extinf)

    stream_url = f"{BASE_STREAM_URL}/{cid_enc}"
    lines.append(stream_url)

    count += 1

with open("channels.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"SUCCESS: M3U generated for {count} channels")

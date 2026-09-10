import json
import os
import urllib.parse

INPUT_FILE = "data/epg.json"
OUTPUT_FILE = "data/channels.m3u"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
channels = json.load(f)

lines = ["#EXTM3U"]
seen = set()

for ch in channels:
cid = str(ch.get("id") or "").strip()
name = str(ch.get("name") or "").strip()
logo = str(ch.get("logo") or "").strip()

if not cid:
    continue

if cid in seen:
    continue

seen.add(cid)

if not name:
    name = cid

cid_enc = urllib.parse.quote(cid)

lines.append(
    f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" tvg-logo="{logo}",{name}'
)

lines.append(
    f"http://127.0.0.1/{cid_enc}"
)

os.makedirs("data", exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
f.write("\n".join(lines))
f.write("\n")

print("M3U generated")
print("channels:", len(seen))
print("file:", OUTPUT_FILE)

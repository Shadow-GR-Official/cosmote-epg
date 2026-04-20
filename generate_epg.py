import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import os

# ----------------------------
# TIME FORMAT FIX
# ----------------------------
def to_xmltv_time(value):
    if not value:
        return ""

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        dt = dt.astimezone(ZoneInfo("Europe/Athens"))
        return dt.strftime("%Y%m%d%H%M%S %z")
    except:
        return ""

# ----------------------------
# LOAD DATA
# ----------------------------
with open("data/epg.json", "r", encoding="utf-8") as f:
    epg = json.load(f)

# ----------------------------
# LOAD EXISTING CHANNELS
# ----------------------------
channels_cache_file = "data/channels_cache.json"

if os.path.exists(channels_cache_file):
    with open(channels_cache_file, "r", encoding="utf-8") as f:
        channels_cache = json.load(f)
else:
    channels_cache = {}

# ----------------------------
# MERGE CHANNELS
# ----------------------------
for ch in epg:
    cid = ch.get("id")
    if not cid:
        continue

    if cid not in channels_cache:
        channels_cache[cid] = {
            "id": cid,
            "name": ch.get("name"),
            "logo": ch.get("logo")
        }

# save cache
with open(channels_cache_file, "w", encoding="utf-8") as f:
    json.dump(channels_cache, f, ensure_ascii=False, indent=2)

# ----------------------------
# BUILD XML
# ----------------------------
tv = ET.Element("tv")

# channels
for cid, ch in channels_cache.items():
    c = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(c, "display-name").text = ch.get("name") or cid

# ----------------------------
# PROGRAMMES
# ----------------------------
total = 0

for ch in epg:
    cid = ch.get("id")
    if not cid:
        continue

    for p in ch.get("items", []):

        start = to_xmltv_time(p.get("startTime"))
        stop = to_xmltv_time(p.get("endTime"))

        if not start or not stop:
            continue

        prog = ET.SubElement(tv, "programme", {
            "start": start,
            "stop": stop,
            "channel": cid
        })

        # title
        ET.SubElement(prog, "title", {"lang": "el"}).text = p.get("title") or "No title"

        # description
        if p.get("description"):
            ET.SubElement(prog, "desc", {"lang": "el"}).text = p["description"]

        # ----------------------------
        # CATEGORY / GENRE FIX
        # ----------------------------
        cats = p.get("genres") or []

        if isinstance(cats, str):
            cats = [cats]

        cats = [c for c in cats if c]
        cats = list(dict.fromkeys(cats))

        for c in cats:
            ET.SubElement(prog, "category", {"lang": "el"}).text = c

        total += 1

# ----------------------------
# SAVE XML
# ----------------------------
os.makedirs("data", exist_ok=True)

ET.indent(tv, space="  ")
xml_str = ET.tostring(tv, encoding="utf-8").decode()

with open("data/epg.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(xml_str)

print("✔ XML generated")
print("✔ channels cached:", len(channels_cache))
print("✔ programmes:", total)

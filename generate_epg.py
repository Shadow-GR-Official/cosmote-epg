import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import re
import os
import html

# ----------------------------
# SAFE XML TIME (Vodafone + Cosmote compatible)
# ----------------------------
def to_xmltv_time(value):
    if not value:
        return ""

    try:
        value = str(value)

        # Unix timestamp support (Cosmote)
        if value.isdigit():
            value = int(value)
            dt = datetime.fromtimestamp(value, tz=ZoneInfo("Europe/Athens"))
        else:
            value = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(value)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))

            dt = dt.astimezone(ZoneInfo("Europe/Athens"))

        return dt.strftime("%Y%m%d%H%M%S %z")

    except Exception:
        return ""

# ----------------------------
# CLEAN DESCRIPTION
# ----------------------------
def clean_desc(desc):
    if not desc:
        return "", None

    desc = str(desc)
    subtitle = None

    m = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if m:
        subtitle = m.group(1).strip()
        desc = desc.replace(m.group(0), "")

    desc = re.sub(r"Διάρκεια:\s*\d{1,2}:\d{2}(:\d{2})?", "", desc)
    desc = re.sub(r"\s{2,}", " ", desc)

    return desc.strip(), subtitle

# ----------------------------
# CHANNEL ID SAFE
# ----------------------------
def cid(ch):
    return str(ch.get("id") or ch.get("uuid") or ch.get("channel_id") or "")

# ----------------------------
# LOAD DATA
# ----------------------------
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg = json.load(f)

# ----------------------------
# MAP
# ----------------------------
epg_map = {}

for ch in epg:
    key = cid(ch)
    if not key:
        continue

    items = ch.get("items") or ch.get("programs") or []
    epg_map[key] = items

# ----------------------------
# XML ROOT
# ----------------------------
tv = ET.Element("tv")

# ----------------------------
# CHANNELS
# ----------------------------
for ch in channels:
    key = cid(ch)
    if not key:
        continue

    c = ET.SubElement(tv, "channel", id=key)
    ET.SubElement(c, "display-name").text = html.escape(ch.get("name") or key)

# ----------------------------
# PROGRAMS
# ----------------------------
total = 0

for ch in channels:
    key = cid(ch)

    if key not in epg_map:
        continue

    seen = set()

    for p in epg_map[key]:

        start = to_xmltv_time(p.get("startTime") or p.get("start"))
        stop = to_xmltv_time(p.get("endTime") or p.get("end"))

        if not start:
            continue

        if not stop:
            stop = start

        # dedupe
        dedupe_key = f"{start}-{stop}-{p.get('title')}"
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        prog = ET.SubElement(tv, "programme", {
            "start": start,
            "stop": stop,
            "channel": key
        })

        ET.SubElement(prog, "title", {"lang": "el"}).text = html.escape(str(p.get("title") or "No title"))

        desc, sub = clean_desc(p.get("description"))

        if sub:
            ET.SubElement(prog, "sub-title", {"lang": "el"}).text = html.escape(sub)

        if desc:
            ET.SubElement(prog, "desc", {"lang": "el"}).text = html.escape(desc)

        # GENRES (dedupe)
        genres = p.get("genres")
        if genres:
            if isinstance(genres, list):
                for g in set(genres):
                    if g:
                        ET.SubElement(prog, "category", {"lang": "el"}).text = html.escape(str(g))
            else:
                ET.SubElement(prog, "category", {"lang": "el"}).text = html.escape(str(genres))

        total += 1

# ----------------------------
# SAVE
# ----------------------------
os.makedirs("data", exist_ok=True)

ET.indent(tv, space="  ")
xml_str = ET.tostring(tv, encoding="utf-8").decode("utf-8")

file_path = os.path.join("data", "epg.xml")

with open(file_path, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(xml_str)

print(f"✔ EPG created: {file_path}")
print(f"✔ Channels: {len(channels)}, Programs: {total}")

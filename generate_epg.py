import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import re
import os

# ----------------------------
# TIME FIX (ROBUST + XMLTV SAFE)
# ----------------------------
def to_xmltv_time(value):
    if not value:
        return ""

    try:
        value = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)

        # If naive datetime, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        # Convert to Greece time (DST auto)
        dt = dt.astimezone(ZoneInfo("Europe/Athens"))

        # XMLTV format (WITH SPACE BEFORE OFFSET)
        return dt.strftime("%Y%m%d%H%M%S %z")

    except Exception:
        return ""

# ----------------------------
# CLEAN DESCRIPTION
# ----------------------------
def clean_desc(desc):
    if not desc:
        return "", None

    subtitle = None

    m = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if m:
        subtitle = m.group(1).strip()
        desc = desc.replace(m.group(0), "")

    desc = re.sub(r"Διάρκεια:\s*\d{1,2}:\d{2}(:\d{2})?", "", desc)
    desc = re.sub(r"\s{2,}", " ", desc)

    return desc.strip(), subtitle

# ----------------------------
# CHANNEL ID
# ----------------------------
def cid(ch):
    return str(ch.get("id") or ch.get("guid") or ch.get("channel_id") or "")

# ----------------------------
# LOAD FILES
# ----------------------------
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg = json.load(f)

# ----------------------------
# MAP CHANNELS -> PROGRAMS
# ----------------------------
epg_map = {}

for ch in epg:
    key = cid(ch)
    if not key:
        continue
    epg_map[key] = ch.get("items") or ch.get("programs") or []

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
    ET.SubElement(c, "display-name").text = ch.get("name") or key

# ----------------------------
# PROGRAMS
# ----------------------------
total = 0

for ch in channels:
    key = cid(ch)

    if key not in epg_map:
        continue

    for p in epg_map[key]:

        start = to_xmltv_time(p.get("startTime") or p.get("start"))
        stop = to_xmltv_time(p.get("endTime") or p.get("end"))

        if not start:
            continue

        if not stop:
            stop = start

        prog = ET.SubElement(tv, "programme", {
            "start": start,
            "stop": stop,
            "channel": key
        })

        # TITLE
        ET.SubElement(prog, "title", {"lang": "el"}).text = str(p.get("title") or "No title")

        # DESCRIPTION
        desc, sub = clean_desc(p.get("description" {"lang": "el"}) or "")

        if sub:
            ET.SubElement(prog, "sub-title", {"lang": "el"}).text = sub

        if desc:
            ET.SubElement(prog, "desc", {"lang": "el"}).text = desc

        # GENRES
        genres = p.get("genres")
        if genres:
            if isinstance(genres, list):
                for g in genres:
                    if g:
                        ET.SubElement(prog, "category" {"lang": "el"}).text = str(g)
            else:
                ET.SubElement(prog, "category" {"lang": "el"}).text = str(genres)

        total += 1

# ----------------------------
# SAVE XML (VODAFONE/COSMOTE GITHUB STYLE)
# ----------------------------
# Δημιουργία φακέλου data
if not os.path.exists("data"):
    os.makedirs("data")

# Μορφοποίηση με 4 κενά για indent
ET.indent(tv, space="  ")
xml_str = ET.tostring(tv, encoding="utf-8").decode("utf-8")

# Αφαίρεση κενών γραμμών για συνεχή αρίθμηση στο GitHub
lines = [line for line in xml_str.splitlines() if line.strip()]
xml_content = "\n".join(lines)

file_path = os.path.join("data", "epg.xml")

with open(file_path, "w", encoding="utf-8") as f:
    # Header ακριβώς όπως στις εικόνες
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(xml_content)

print(f"✔ Επιτυχία! Το αρχείο δημιουργήθηκε: {file_path}")
print(f"✔ Κανάλια: {len(channels)}, Προγράμματα: {total}")

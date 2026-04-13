import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import re


# ----------------------------
# TIME FIX (ROBUST)
# ----------------------------
def to_xmltv_time(value):
    if not value:
        return ""

    try:
        value = str(value)

        # ISO Z fix
        value = value.replace("Z", "+00:00")

        dt = datetime.fromisoformat(value)
        dt = dt.astimezone(ZoneInfo("Europe/Athens"))

        return dt.strftime("%Y%m%d%H%M%S %z")
    except:
        return ""


# ----------------------------
# CLEAN DESCRIPTION (NO DUPLICATES)
# ----------------------------
def clean_desc(desc):
    if not desc:
        return "", None

    subtitle = None

    # episode extraction
    m = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if m:
        subtitle = m.group(1).strip()
        desc = desc.replace(m.group(0), "")

    # remove ALL duration variants (safe)
    desc = re.sub(r"Διάρκεια:\s*\d{1,2}:\d{2}(:\d{2})?", "", desc)
    desc = re.sub(r"\s{2,}", " ", desc)

    return desc.strip(), subtitle


# ----------------------------
# CHANNEL ID
# ----------------------------
def cid(ch):
    return str(
        ch.get("id")
        or ch.get("guid")
        or ch.get("channel_id")
        or ""
    )


# ----------------------------
# LOAD FILES
# ----------------------------
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg = json.load(f)


# ----------------------------
# BUILD MAP
# ----------------------------
epg_map = {}

for ch in epg:
    key = cid(ch)
    if not key:
        continue

    epg_map[key] = ch.get("items") or ch.get("programs") or []


# ----------------------------
# XML ROOT (Kodi-safe)
# ----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG FIXED"})


# ----------------------------
# CHANNELS (MUST FIRST)
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

        start = to_xmltv_time(p.get("startTime"))
        stop = to_xmltv_time(p.get("endTime"))

        # ONLY skip if no start
        if not start:
            continue

        # fallback (IMPORTANT for Kodi timeline continuity)
        if not stop:
            stop = start

        prog = ET.SubElement(tv, "programme", {
            "start": start,
            "stop": stop,
            "channel": key
        })

        # title always safe string
        title = p.get("title") or "No title"
        ET.SubElement(prog, "title").text = str(title)

        # description
        desc, sub = clean_desc(p.get("description") or "")

        if sub:
            ET.SubElement(prog, "sub-title").text = sub

        if desc:
            ET.SubElement(prog, "desc").text = desc

        total += 1


# ----------------------------
# SAVE
# ----------------------------
tree = ET.ElementTree(tv)
ET.indent(tree, space="  ")

with open("epg.xml", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)


print("✔ epg.xml UPDATED SUCCESSFULLY")
print("✔ channels:", len(channels))
print("✔ programs:", total)

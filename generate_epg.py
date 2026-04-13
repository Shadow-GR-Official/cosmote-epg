import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import re


# ----------------------------
# TIME FIX
# ----------------------------
def to_xmltv_time(value):
    if not value:
        return ""

    try:
        value = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        dt = dt.astimezone(ZoneInfo("Europe/Athens"))
        return dt.strftime("%Y%m%d%H%M%S %z")
    except:
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
# MAP
# ----------------------------
epg_map = {}

for ch in epg:
    key = cid(ch)
    if key:
        epg_map[key] = ch.get("items") or ch.get("programs") or []


# ----------------------------
# XML ROOT
# ----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG FIXED"})


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

        start = to_xmltv_time(p.get("startTime"))
        stop = to_xmltv_time(p.get("endTime"))

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
        ET.SubElement(prog, "title").text = str(p.get("title") or "No title")

        # DESCRIPTION
        desc, sub = clean_desc(p.get("description") or "")

        if sub:
            ET.SubElement(prog, "sub-title").text = sub

        if desc:
            ET.SubElement(prog, "desc").text = desc

        # ----------------------------
        # GENRE / CATEGORY FIX
        # ----------------------------
        genre = p.get("genres") or p.get("genre")

        if genre:
            if isinstance(genre, list):
                for g in genre:
                    if g:
                        ET.SubElement(prog, "category", lang="el").text = str(g)
            else:
                ET.SubElement(prog, "category", lang="el").text = str(genre)

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

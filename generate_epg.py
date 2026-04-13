import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import re


def to_xmltv_time(iso_str):
    if not iso_str:
        return ""

    try:
        iso_str = str(iso_str).strip().replace("Z", "+00:00")

        dt_obj = datetime.fromisoformat(iso_str)
        dt_athens = dt_obj.astimezone(ZoneInfo("Europe/Athens"))

        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except:
        return ""


def clean_description(desc):
    if not desc:
        return "", None

    subtitle = None

    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        subtitle = match.group(1).strip()
        desc = desc.replace(match.group(0), "")

    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)

    desc = re.sub(r"\s{2,}", " ", desc)

    return desc.strip(), subtitle


def get_channel_id(ch):
    # unified id resolver (IMPORTANT FIX)
    return str(
        ch.get("id")
        or ch.get("guid")
        or ch.get("channel_id")
        or ch.get("channelId")
        or ""
    )


# 1. LOAD CHANNELS
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        static_channels = json.load(f)
except Exception as e:
    print(f"ERROR: Missing channels.json: {e}")
    sys.exit(1)

# 2. LOAD EPG
try:
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except Exception as e:
    print(f"ERROR: Missing epg.json: {e}")
    sys.exit(1)


# 3. BUILD EPG MAP (FIXED)
epg_map = {}

for ch in epg_data:
    cid = get_channel_id(ch)
    if not cid:
        continue

    programs = ch.get("items") or ch.get("programs") or []
    epg_map[cid] = programs


# 4. XML ROOT
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG"})


# 5. CHANNELS
for ch in static_channels:
    cid = get_channel_id(ch)
    name = ch.get("name") or ch.get("title") or "Unknown"

    if not cid:
        continue

    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = name


# 6. PROGRAMMES
for ch in static_channels:
    cid = get_channel_id(ch)

    if cid not in epg_map:
        continue

    for p in epg_map[cid]:
        start = to_xmltv_time(p.get("start") or p.get("startTime"))
        stop = to_xmltv_time(p.get("end") or p.get("endTime"))

        if not start or not stop:
            continue

        prog_el = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)

        # TITLE
        title = p.get("title") or "Χωρίς τίτλο"
        ET.SubElement(prog_el, "title", lang="el").text = title

        # DESCRIPTION
        desc, subtitle = clean_description(p.get("description") or "")

        if subtitle:
            ET.SubElement(prog_el, "sub-title", lang="el").text = subtitle

        if desc:
            ET.SubElement(prog_el, "desc", lang="el").text = desc

        # CATEGORY
        genre = p.get("genres") or p.get("genre")
        if genre:
            if isinstance(genre, list):
                genre = genre[0] if genre else None

            if genre:
                ET.SubElement(prog_el, "category", lang="el").text = str(genre)


# 7. SAVE XML
tree = ET.ElementTree(tv)

if hasattr(ET, "indent"):
    ET.indent(tree, space="\t", level=0)

with open("epg.xml", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: epg.xml generated. Channels: {len(static_channels)}")

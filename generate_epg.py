import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys
import re

def to_xmltv_time(iso_str):
    if not iso_str: return ""
    try:
        iso_str = iso_str.strip().replace("Z", "+00:00")
        if '+' not in iso_str and '-' not in iso_str[10:]:
            iso_str += "+00:00"
        dt_obj = datetime.fromisoformat(iso_str)
        dt_athens = dt_obj.astimezone(ZoneInfo("Europe/Athens"))
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except:
        return ""

# ✅ Ελληνικοποίηση (safe)
def greekize_safe(text):
    if not text:
        return text

    # Αν είναι κυρίως λατινικά → μην το πειράξεις
    latin_ratio = sum(c.isascii() for c in text) / len(text)
    if latin_ratio > 0.6:
        return text

    mapping = {
        "News": "Ειδήσεις",
        "Movie": "Ταινία",
        "Series": "Σειρά",
        "Sports": "Αθλητικά",
        "Show": "Σόου",
        "Documentary": "Ντοκιμαντέρ",
        "Kids": "Παιδικά",
        "Entertainment": "Ψυχαγωγία"
    }

    for en, gr in mapping.items():
        text = text.replace(en, gr)

    return text

# ✅ CLEAN DESCRIPTION
def clean_description(desc):
    if not desc:
        return "", None

    subtitle = None

    # Extract subtitle
    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        subtitle = match.group(1).strip()
        desc = desc.replace(match.group(0), "")

    # Remove durations
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)

    # Cleanup spaces
    desc = re.sub(r"\s{2,}", " ", desc)

    return desc.strip(), subtitle

# 1. Channels
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        static_channels = json.load(f)
except Exception as e:
    print(f"ERROR: Missing channels.json: {e}")
    sys.exit(1)

# 2. EPG
try:
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except Exception as e:
    print(f"ERROR: Missing epg.json: {e}")
    sys.exit(1)

# Indexing
epg_map = {}
for ch in epg_data:
    cid = str(ch.get("guid") or ch.get("channel_id") or ch.get("id") or "")
    if cid:
        epg_map[cid] = ch.get("items") or ch.get("programs") or []

# 3. XML
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG"})

# Channels
for ch in static_channels:
    cid = str(ch.get("id") or ch.get("guid") or "")
    name = ch.get("name") or ch.get("title") or "Unknown"
    if not cid:
        continue

    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = name

# Programmes
for ch in static_channels:
    cid = str(ch.get("id") or ch.get("guid") or "")
    if cid not in epg_map:
        continue

    for p in epg_map[cid]:
        start = to_xmltv_time(p.get("startTime") or p.get("start"))
        stop = to_xmltv_time(p.get("endTime") or p.get("end"))
        if not start or not stop:
            continue

        prog_el = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)

        # Title
        title = greekize_safe(p.get("title") or "Χωρίς τίτλο")
        ET.SubElement(prog_el, "title", lang="el").text = title

        # Description + subtitle
        raw_desc = p.get("description") or ""
        desc, subtitle = clean_description(raw_desc)

        desc = greekize_safe(desc)
        if subtitle:
            subtitle = greekize_safe(subtitle)

        if subtitle:
            ET.SubElement(prog_el, "sub-title", lang="el").text = subtitle

        if desc:
            ET.SubElement(prog_el, "desc", lang="el").text = desc

        # Category
        genre = p.get("genres") or p.get("genre")
        if genre:
            cat_text = genre[0] if isinstance(genre, list) and genre else genre
            cat_text = greekize_safe(str(cat_text))
            ET.SubElement(prog_el, "category", lang="el").text = cat_text

# 4. SAVE
tree = ET.ElementTree(tv)
if hasattr(ET, "indent"):
    ET.indent(tree, space="\t", level=0)

with open("epg.xml", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: epg.xml generated. Channels: {len(static_channels)}")

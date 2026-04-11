import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo # Standard στην Python 3.9+

# -----------------------------
# TIME FORMAT (NO EXTERNAL LIB)
# -----------------------------
def to_xmltv_time(iso_str):
    if not iso_str:
        return ""
    try:
        # Αντικατάσταση του Z με +00:00 για να το διαβάσει η fromisoformat
        iso_str = iso_str.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(iso_str)
        
        # Μετατροπή σε ώρα Ελλάδος (υπολογίζει αυτόματα καλοκαίρι/χειμώνα)
        dt_athens = dt_utc.astimezone(ZoneInfo("Europe/Athens"))
        
        # Format για XMLTV: YYYYMMDDHHMMSS +0300
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except Exception:
        return ""

# -----------------------------
# LOAD DATA
# -----------------------------
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        channels = json.load(f)
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except FileNotFoundError:
    print("Error: Missing JSON files!")
    exit(1)

# Indexing EPG data by ID
epg_by_id = {str(ch.get("id")): ch.get("programs", []) for ch in epg_data if isinstance(ch, dict)}

# -----------------------------
# BUILD XMLTV
# -----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Fixer"})

# 1. Channels Section
for ch in channels:
    cid = str(ch.get("id"))
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = ch.get("name")

# 2. Programmes Section
for ch in channels:
    cid = str(ch.get("id"))
    programs = epg_by_id.get(cid, [])

    for p in programs:
        start = to_xmltv_time(p.get("start"))
        stop = to_xmltv_time(p.get("end"))
        
        if not start or not stop: continue

        prog = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)
        ET.SubElement(prog, "title", lang="el").text = p.get("title", "Χωρίς τίτλο")
        
        if p.get("description"):
            ET.SubElement(prog, "desc", lang="el").text = p["description"]
        
        if p.get("genre"):
            cat = ET.SubElement(prog, "category", lang="el")
            cat.text = p["genre"]

# -----------------------------
# WRITE OUTPUT
# -----------------------------
tree = ET.ElementTree(tv)
ET.indent(tree, space="\t", level=0)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print("SUCCESS: epg.xml generated with correct Athens time!")

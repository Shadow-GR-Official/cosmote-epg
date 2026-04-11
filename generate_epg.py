import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

# -----------------------------
# TIME FORMAT (FIXED - NO PYTZ NEEDED)
# -----------------------------
def to_xmltv_time(iso_str):
    if not iso_str:
        return ""
    try:
        # Το Cosmote API δίνει "2024-04-11T10:30:00Z"
        # Αντικαθιστούμε το Z με +00:00 για να το αναγνωρίσει η Python ως UTC
        iso_str = iso_str.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(iso_str)
        
        # Μετατροπή στην ώρα Ελλάδος (υπολογίζει αυτόματα καλοκαίρι/χειμώνα)
        dt_athens = dt_utc.astimezone(ZoneInfo("Europe/Athens"))
        
        # Format για XMLTV: YYYYMMDDHHMMSS +offset
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except Exception:
        return ""

# -----------------------------
# LOAD FILES
# -----------------------------
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        channels = json.load(f)
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except FileNotFoundError as e:
    print(f"Σφάλμα: Δεν βρέθηκε το αρχείο {e.filename}")
    exit(1)

# Indexing EPG
epg_by_id = {}
for ch in epg_data:
    if not isinstance(ch, dict): continue
    cid = str(ch.get("id") or ch.get("channel_id") or ch.get("guid", ""))
    epg_by_id[cid] = ch.get("programs", [])

# -----------------------------
# CREATE XMLTV ROOT
# -----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Fixer"})

# 1. CHANNELS
for ch in channels:
    cid = str(ch.get("id", ""))
    if not cid: continue
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = ch.get("name", "Unknown")

# 2. PROGRAMMES
for ch in channels:
    cid = str(ch.get("id", ""))
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
            ET.SubElement(prog, "category", lang="el").text = str(p["genre"])

# -----------------------------
# WRITE OUTPUT
# -----------------------------
tree = ET.ElementTree(tv)
# Το indent θέλει Python 3.9+
try:
    ET.indent(tree, space="\t", level=0)
except AttributeError:
    pass 

tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print("SUCCESS: Το epg.xml δημιουργήθηκε με σωστή ώρα Ελλάδος!")

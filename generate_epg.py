import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

# -----------------------------
# FIXED TIME FORMAT
# -----------------------------
def to_xmltv_time(iso_str):
    if not iso_str:
        return ""
    try:
        # Καθαρίζουμε το string και βεβαιωνόμαστε ότι η Python το βλέπει ως UTC
        iso_str = iso_str.strip()
        
        # Αν η ημερομηνία έρχεται με Z ή χωρίς offset, την κάνουμε standard UTC
        if iso_str.endswith('Z'):
            iso_str = iso_str.replace("Z", "+00:00")
        elif '+' not in iso_str and '-' not in iso_str[10:]: # αν δεν έχει offset
            iso_str += "+00:00"

        # Μετατροπή σε datetime αντικείμενο
        dt_obj = datetime.fromisoformat(iso_str)
        
        # Μετατροπή στην ώρα Ελλάδος (Europe/Athens)
        # Αυτό θα μετατρέψει π.χ. το 21:00 UTC σε 00:00 Athens (+3)
        dt_athens = dt_obj.astimezone(ZoneInfo("Europe/Athens"))
        
        # Format για XMLTV: YYYYMMDDHHMMSS +0300
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except Exception as e:
        return ""

# -----------------------------
# LOAD DATA
# -----------------------------
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        channels = json.load(f)
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except FileNotFoundError as e:
    print(f"Error: Missing file {e.filename}")
    exit(1)

# Indexing EPG data by ID για γρήγορη αναζήτηση
epg_by_id = {}
for ch in epg_data:
    if not isinstance(ch, dict): continue
    cid = str(ch.get("id") or ch.get("channel_id") or ch.get("guid", ""))
    if cid:
        epg_by_id[cid] = ch.get("programs", [])

# -----------------------------
# BUILD XMLTV
# -----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Fixer v2"})

# 1. CHANNELS SECTION
for ch in channels:
    cid = str(ch.get("id", ""))
    if not cid: continue
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = ch.get("name", "Unknown")

# 2. PROGRAMMES SECTION
for ch in channels:
    cid = str(ch.get("id", ""))
    # Παίρνουμε τις εκπομπές για το συγκεκριμένο κανάλι
    programs = epg_by_id.get(cid, [])

    for p in programs:
        start_xml = to_xmltv_time(p.get("start"))
        stop_xml = to_xmltv_time(p.get("end"))
        
        if not start_xml or not stop_xml: continue

        prog = ET.SubElement(tv, "programme", start=start_xml, stop=stop_xml, channel=cid)
        ET.SubElement(prog, "title", lang="el").text = p.get("title", "Χωρίς τίτλο")
        
        if p.get("description"):
            ET.SubElement(prog, "desc", lang="el").text = p["description"]
        
        if p.get("genre"):
            ET.SubElement(prog, "category", lang="el").text = str(p["genre"])

# -----------------------------
# WRITE OUTPUT
# -----------------------------
tree = ET.ElementTree(tv)

# Indentation για να είναι ευανάγνωστο (Python 3.9+)
try:
    ET.indent(tree, space="\t", level=0)
except AttributeError:
    pass 

tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print("SUCCESS: epg.xml generated. Check your times now!")

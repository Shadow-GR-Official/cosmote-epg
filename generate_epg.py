import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys

def to_xmltv_time(iso_str):
    if not iso_str: return ""
    try:
        iso_str = iso_str.strip().replace("Z", "+00:00")
        if '+' not in iso_str and '-' not in iso_str[10:]:
            iso_str += "+00:00"
        dt_obj = datetime.fromisoformat(iso_str)
        dt_athens = dt_obj.astimezone(ZoneInfo("Europe/Athens"))
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except: return ""

# 1. ΦΟΡΤΩΝΟΥΜΕ ΤΗ ΣΤΑΘΕΡΗ ΛΙΣΤΑ ΚΑΝΑΛΙΩΝ
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        static_channels = json.load(f)
except Exception as e:
    print(f"ERROR: Missing channels.json (σταθερή λίστα): {e}")
    sys.exit(1)

# 2. ΦΟΡΤΩΝΟΥΜΕ ΤΟ ΠΡΟΓΡΑΜΜΑ (ΕΚΠΟΜΠΕΣ)
try:
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except Exception as e:
    print(f"ERROR: Missing epg.json (εκπομπές): {e}")
    sys.exit(1)

# Indexing εκπομπών για γρήγορη εύρεση
epg_map = {}
for ch in epg_data:
    cid = str(ch.get("guid") or ch.get("channel_id") or ch.get("id") or "")
    if cid:
        # Κρατάμε τις εκπομπές (items ή programs)
        epg_map[cid] = ch.get("items") or ch.get("programs") or []

# 3. ΧΤΙΖΟΥΜΕ ΤΟ XML
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Static List"})

# ΠΡΩΤΑ: Γράφουμε ΟΛΑ τα κανάλια από τη σταθερή λίστα (πάντα ίδια)
for ch in static_channels:
    cid = str(ch.get("id") or ch.get("guid") or "")
    name = ch.get("name") or ch.get("title") or "Unknown"
    if not cid: continue
    
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = name

# ΜΕΤΑ: Γράφουμε τις εκπομπές μόνο για όσα κανάλια βρήκαμε πρόγραμμα
for ch in static_channels:
    cid = str(ch.get("id") or ch.get("guid") or "")
    if cid in epg_map:
        for p in epg_map[cid]:
            start = to_xmltv_time(p.get("startTime") or p.get("start"))
            stop = to_xmltv_time(p.get("endTime") or p.get("end"))
            if not start or not stop: continue

            prog_el = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)
            ET.SubElement(prog_el, "title", lang="el").text = p.get("title") or "Χωρίς τίτλο"
            
            desc = p.get("description") or ""
            if desc: ET.SubElement(prog_el, "desc", lang="el").text = desc
            
            # Categories
            genre = p.get("genres") or p.get("genre")
            if genre:
                cat_text = genre[0] if isinstance(genre, list) and genre else genre
                ET.SubElement(prog_el, "category", lang="el").text = str(cat_text)

# 4. ΑΠΟΘΗΚΕΥΣΗ
tree = ET.ElementTree(tv)
if hasattr(ET, "indent"): ET.indent(tree, space="\t", level=0)
with open("epg.xml", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: epg.xml generated. Channels: {len(static_channels)}")

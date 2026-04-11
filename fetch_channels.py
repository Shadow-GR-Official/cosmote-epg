import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

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

# Φόρτωση δεδομένων
try:
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except Exception as e:
    print(f"Error loading epg.json: {e}")
    exit(1)

tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Fixer"})

for ch in epg_data:
    if not isinstance(ch, dict): continue
    
    # ID και Όνομα καναλιού
    cid = str(ch.get("guid") or ch.get("id") or "")
    name = ch.get("title") or ch.get("name") or "Unknown"
    
    if not cid: continue

    # Προσθήκη καναλιού στο XML
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = name

    # Εύρεση εκπομπών (δοκιμάζει 'items' ή 'programs')
    progs = ch.get("items") or ch.get("programs") or []
    
    for p in progs:
        # Η Cosmote χρησιμοποιεί 'startTime'/'endTime' μέσα στο items
        start = to_xmltv_time(p.get("startTime") or p.get("start"))
        stop = to_xmltv_time(p.get("endTime") or p.get("end"))
        
        if not start or not stop: continue

        prog_el = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)
        ET.SubElement(prog_el, "title", lang="el").text = p.get("title", "Χωρίς τίτλο")
        
        desc_text = p.get("description") or ""
        if desc_text:
            ET.SubElement(prog_el, "desc", lang="el").text = desc_text
            
        # Κατηγορία από το genres list ή το genre string
        genres = p.get("genres")
        genre = genres[0] if isinstance(genres, list) and genres else p.get("genre")
        if genre:
            ET.SubElement(prog_el, "category", lang="el").text = str(genre)

# Αποθήκευση
tree = ET.ElementTree(tv)
try: ET.indent(tree, space="\t", level=0)
except: pass
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print("SUCCESS: epg.xml generated! Now IPTVnator should see the programs.")

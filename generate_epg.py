import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys

# -----------------------------
# ΣΩΣΤΟ FORMAT ΩΡΑΣ (UTC -> Athens)
# -----------------------------
def to_xmltv_time(iso_str):
    if not iso_str:
        return ""
    try:
        # Καθαρισμός και μετατροπή σε ISO format που καταλαβαίνει η Python
        iso_str = iso_str.strip().replace("Z", "+00:00")
        if '+' not in iso_str and '-' not in iso_str[10:]:
            iso_str += "+00:00"
            
        dt_obj = datetime.fromisoformat(iso_str)
        # Μετατροπή σε ώρα Ελλάδος (υπολογίζει αυτόματα DST)
        dt_athens = dt_obj.astimezone(ZoneInfo("Europe/Athens"))
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except Exception:
        return ""

# -----------------------------
# ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ
# -----------------------------
input_file = "epg.json"
output_file = "epg.xml"

if not os.path.exists(input_file):
    print(f"ERROR: Το αρχείο {input_file} δεν βρέθηκε!")
    sys.exit(1)

try:
    with open(input_file, "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except Exception as e:
    print(f"ERROR reading json: {e}")
    sys.exit(1)

# -----------------------------
# ΔΗΜΙΟΥΡΓΙΑ XMLTV
# -----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Fixer"})

channels_count = 0
programs_count = 0

for ch in epg_data:
    if not isinstance(ch, dict): continue
    
    # ID και Όνομα καναλιού (δοκιμάζει όλα τα πιθανά κλειδιά)
    cid = str(ch.get("guid") or ch.get("id") or "")
    name = ch.get("title") or ch.get("name") or "Unknown Channel"
    
    if not cid: continue

    # 1. Προσθήκη Καναλιού
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = name
    channels_count += 1

    # 2. Εύρεση Εκπομπών (η Cosmote τις έχει στο 'items')
    progs = ch.get("items") or ch.get("programs") or []
    
    for p in progs:
        # Χρήση startTime/endTime (UTC) από το JSON
        start = to_xmltv_time(p.get("startTime") or p.get("start"))
        stop = to_xmltv_time(p.get("endTime") or p.get("end"))
        
        if not start or not stop: continue

        prog_el = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)
        
        # Τίτλος
        title_text = p.get("title") or "Χωρίς τίτλο"
        ET.SubElement(prog_el, "title", lang="el").text = title_text
        
        # Περιγραφή
        desc_text = p.get("description") or ""
        if desc_text:
            ET.SubElement(prog_el, "desc", lang="el").text = desc_text
            
        # Κατηγορία (Genre)
        genres = p.get("genres")
        genre_val = ""
        if isinstance(genres, list) and genres:
            genre_val = genres[0]
        else:
            genre_val = p.get("genre") or ""
            
        if genre_val:
            ET.SubElement(prog_el, "category", lang="el").text = str(genre_val)
        
        programs_count += 1

# -----------------------------
# ΑΠΟΘΗΚΕΥΣΗ (ΑΝΤΙΚΑΤΑΣΤΑΣΗ)
# -----------------------------
if os.path.exists(output_file):
    os.remove(output_file)

try:
    tree = ET.ElementTree(tv)
    if hasattr(ET, "indent"):
        ET.indent(tree, space="\t", level=0)
    
    with open(output_file, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    
    print(f"SUCCESS: Δημιουργήθηκε το {output_file}")
    print(f"Στατιστικά: {channels_count} κανάλια, {programs_count} εκπομπές.")

except Exception as e:
    print(f"CRITICAL ERROR writing XML: {e}")
    sys.exit(1)

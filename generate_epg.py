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

# Φόρτωση
input_file = "epg.json"
if not os.path.exists(input_file):
    print("ERROR: epg.json not found")
    sys.exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Προσπάθεια εύρεσης της λίστας καναλιών (σε περίπτωση που είναι μέσα σε stripes)
channels_list = []
if isinstance(data, list):
    channels_list = data
elif isinstance(data, dict):
    if "stripes" in data:
        stripes = data["stripes"]
        if isinstance(stripes, list):
            for s in stripes:
                if "channels" in s:
                    channels_list.extend(s["channels"])
        elif isinstance(stripes, dict):
            channels_list = stripes.get("channels", [])
    else:
        channels_list = data.get("channels", [])

if not channels_list:
    print("ERROR: No channels found in epg.json structure")
    sys.exit(1)

tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Fixer Final"})

for ch in channels_list:
    if not isinstance(ch, dict): continue
    
    cid = str(ch.get("guid") or ch.get("id") or "")
    name = ch.get("title") or ch.get("name") or "Unknown"
    if not cid: continue

    # Κανάλι
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = name

    # Εκπομπές (items ή programs)
    progs = ch.get("items") or ch.get("programs") or []
    
    for p in progs:
        start = to_xmltv_time(p.get("startTime") or p.get("start"))
        stop = to_xmltv_time(p.get("endTime") or p.get("end"))
        if not start or not stop: continue

        prog_el = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)
        ET.SubElement(prog_el, "title", lang="el").text = p.get("title") or "No Title"
        
        desc = p.get("description") or ""
        if desc: ET.SubElement(prog_el, "desc", lang="el").text = desc
        
        genre = p.get("genres") or p.get("genre")
        if genre:
            genre_text = genre[0] if isinstance(genre, list) else genre
            ET.SubElement(prog_el, "category", lang="el").text = str(genre_text)

# Αποθήκευση
tree = ET.ElementTree(tv)
if hasattr(ET, "indent"): ET.indent(tree, space="\t", level=0)
with open("epg.xml", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: epg.xml created with {len(channels_list)} channels")

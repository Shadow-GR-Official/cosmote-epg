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

input_file = "epg.json"
if not os.path.exists(input_file):
    print("Error: epg.json missing")
    sys.exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    channels_list = json.load(f)

tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Ultimate"})

for ch in channels_list:
    # Δοκιμάζει όλα τα πιθανά κλειδιά για ID και Όνομα
    cid = str(ch.get("channel_id") or ch.get("guid") or ch.get("id") or "")
    name = ch.get("channel_name") or ch.get("title") or ch.get("name") or "Unknown"
    
    if not cid: continue

    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = name

    # Δοκιμάζει 'programs' ή 'items'
    progs = ch.get("programs") or ch.get("items") or []
    
    for p in progs:
        # Δοκιμάζει start/startTime και end/endTime
        start = to_xmltv_time(p.get("start") or p.get("startTime"))
        stop = to_xmltv_time(p.get("end") or p.get("endTime"))
        
        if not start or not stop: continue

        prog_el = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)
        ET.SubElement(prog_el, "title", lang="el").text = p.get("title") or "No Title"
        
        desc = p.get("description") or ""
        if desc: ET.SubElement(prog_el, "desc", lang="el").text = desc
        
        genre = p.get("genre") or p.get("genres")
        if genre:
            ET.SubElement(prog_el, "category", lang="el").text = str(genre[0] if isinstance(genre, list) else genre)

tree = ET.ElementTree(tv)
if hasattr(ET, "indent"): ET.indent(tree, space="\t", level=0)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: epg.xml generated for {len(channels_list)} channels")

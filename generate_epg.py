import json
import xml.etree.ElementTree as ET
from datetime import datetime

def to_xmltv_time(iso_str):
    if not iso_str:
        return ""

    # handle Z or +00:00
    iso_str = iso_str.replace("Z", "")
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%Y%m%d%H%M%S +0000")

# load files
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg_data = json.load(f)

# map epg by channel_id
epg_map = {}
for ch in epg_data:
    cid = ch.get("channel_id")
    if cid:
        epg_map[cid] = ch.get("programs", [])

tv = ET.Element("tv")

# CHANNELS (always preserved)
for ch in channels:
    channel_id = ch["guid"]

    channel_el = ET.SubElement(tv, "channel", id=channel_id)
    name_el = ET.SubElement(channel_el, "display-name")
    name_el.text = ch.get("title", "")

# PROGRAMMES
for ch in channels:
    cid = ch["guid"]
    programs = epg_map.get(cid, [])

    for p in programs:
        prog_el = ET.SubElement(
            tv,
            "programme",
            start=to_xmltv_time(p.get("start")),
            stop=to_xmltv_time(p.get("end")),
            channel=cid
        )

        title_el = ET.SubElement(prog_el, "title", lang="el")
        title_el.text = p.get("title", "")

        desc_text = p.get("description")
        if desc_text:
            desc_el = ET.SubElement(prog_el, "desc", lang="el")
            desc_el.text = desc_text

        genre = p.get("genre")
        if genre:
            cat_el = ET.SubElement(prog_el, "category", lang="el")
            cat_el.text = genre

# write file
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: XMLTV generated for {len(channels)} channels")

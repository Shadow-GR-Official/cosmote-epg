import json
import xml.etree.ElementTree as ET
from datetime import datetime

def to_xmltv_time(iso_str):
    if not iso_str:
        return ""

    iso_str = iso_str.replace("Z", "")
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%Y%m%d%H%M%S +0000")

# load
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg_data = json.load(f)

# map epg
epg_map = {}
for ch in epg_data:
    cid = ch.get("channel_id")
    if cid:
        epg_map[cid] = ch.get("programs", [])

tv = ET.Element("tv")

# CHANNELS (SAFE LOOP)
for ch in channels:
    channel_id = ch.get("guid") or ch.get("channel_id")

    if not channel_id:
        continue  # skip broken entries

    channel_el = ET.SubElement(tv, "channel", id=channel_id)

    name = ch.get("title") or ch.get("name") or ""
    name_el = ET.SubElement(channel_el, "display-name")
    name_el.text = name

# PROGRAMMES
for ch in channels:
    cid = ch.get("guid") or ch.get("channel_id")

    if not cid:
        continue

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

        if p.get("description"):
            desc_el = ET.SubElement(prog_el, "desc", lang="el")
            desc_el.text = p["description"]

        if p.get("genre"):
            cat_el = ET.SubElement(prog_el, "category", lang="el")
            cat_el.text = p["genre"]

# write
ET.ElementTree(tv).write(
    "epg.xml",
    encoding="utf-8",
    xml_declaration=True
)

print(f"SUCCESS: XML generated for {len(channels)} channels")

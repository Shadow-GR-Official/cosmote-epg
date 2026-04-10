import json
import xml.etree.ElementTree as ET
from datetime import datetime


def to_xmltv_time(iso_str):
    if not iso_str:
        return ""

    iso_str = iso_str.replace("Z", "")
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%Y%m%d%H%M%S +0000")


# ✅ FIX: ONLY USE REAL CHANNEL ID (XTV...)
def get_channel_id(ch):
    if not isinstance(ch, dict):
        return None
    return ch.get("id")


def get_channel_name(ch):
    if not isinstance(ch, dict):
        return ""
    return ch.get("name", "")


# load files
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg_data = json.load(f)


# ✅ FIXED: epg.json mapping MUST use SAME ID system (XTV...)
epg_map = {}

for ch in epg_data:
    cid = ch.get("id")  # 🔥 ONLY THIS (no channel_id, no guid)
    if cid:
        epg_map[cid] = ch.get("programs", [])


tv = ET.Element("tv")


# CHANNELS
for ch in channels:
    cid = get_channel_id(ch)
    if not cid:
        continue

    name = get_channel_name(ch)

    channel_el = ET.SubElement(tv, "channel", id=cid)
    dn = ET.SubElement(channel_el, "display-name")
    dn.text = name


# PROGRAMMES
for ch in channels:
    cid = get_channel_id(ch)
    if not cid:
        continue

    programs = epg_map.get(cid, [])

    for p in programs:
        prog = ET.SubElement(
            tv,
            "programme",
            start=to_xmltv_time(p.get("start")),
            stop=to_xmltv_time(p.get("end")),
            channel=cid
        )

        title = ET.SubElement(prog, "title", lang="el")
        title.text = p.get("title", "")

        if p.get("description"):
            desc = ET.SubElement(prog, "desc", lang="el")
            desc.text = p["description"]

        if p.get("genre"):
            cat = ET.SubElement(prog, "category", lang="el")
            cat.text = p["genre"]


ET.ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: XML generated for {len(channels)} channels")

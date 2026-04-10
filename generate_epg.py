import json
import xml.etree.ElementTree as ET
from datetime import datetime


def to_xmltv_time(iso_str):
    if not iso_str:
        return ""

    try:
        iso_str = iso_str.replace("Z", "")
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y%m%d%H%M%S +0000")
    except Exception:
        return ""


# ✅ CHANNELS (ONLY REAL ID USED)
def get_channel_id(ch):
    return ch.get("id") if isinstance(ch, dict) else None


def get_channel_name(ch):
    return ch.get("name", "") if isinstance(ch, dict) else ""


# load files
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg_data = json.load(f)


# 🔥 FIX: normalize epg channels (handles ANY API variation safely)
epg_map = {}

for ch in epg_data:
    if not isinstance(ch, dict):
        continue

    cid = (
        ch.get("id")
        or ch.get("channel_id")
        or ch.get("guid")
        or (ch.get("channel", {}) if isinstance(ch.get("channel"), dict) else {}).get("id")
        or (ch.get("channel", {}) if isinstance(ch.get("channel"), dict) else {}).get("guid")
    )

    if cid and isinstance(ch.get("programs"), list):
        epg_map[cid] = ch["programs"]


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
        if not isinstance(p, dict):
            continue

        prog = ET.SubElement(
            tv,
            "programme",
            start=to_xmltv_time(p.get("start")),
            stop=to_xmltv_time(p.get("end")),
            channel=cid
        )

        title = ET.SubElement(prog, "title", lang="el")
        title.text = p.get("title", "") or "No Title"

        if p.get("description"):
            desc = ET.SubElement(prog, "desc", lang="el")
            desc.text = p["description"]

        if p.get("genre"):
            cat = ET.SubElement(prog, "category", lang="el")
            cat.text = p["genre"]


ET.ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: XML generated for {len(channels)} channels")

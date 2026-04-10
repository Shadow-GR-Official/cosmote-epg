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


# -----------------------------
# CHANNEL HELPERS
# -----------------------------
def get_channel_id(ch):
    return ch.get("id") if isinstance(ch, dict) else None


def get_channel_name(ch):
    return ch.get("name", "") if isinstance(ch, dict) else ""


# -----------------------------
# LOAD FILES
# -----------------------------
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg_data = json.load(f)


# -----------------------------
# BUILD EPG INDEX (ROBUST)
# -----------------------------
epg_by_id = {}
epg_by_name = {}

for ch in epg_data:
    if not isinstance(ch, dict):
        continue

    cid = ch.get("id") or ch.get("channel_id") or ch.get("guid")
    name = ch.get("name") or ch.get("title")

    programs = ch.get("programs", [])

    if cid:
        epg_by_id[cid] = programs

    if name:
        epg_by_name[name.lower().strip()] = programs


# -----------------------------
# CREATE XMLTV ROOT
# -----------------------------
tv = ET.Element("tv")


# -----------------------------
# CHANNELS SECTION
# -----------------------------
for ch in channels:
    cid = get_channel_id(ch)
    name = get_channel_name(ch)

    if not cid:
        continue

    channel_el = ET.SubElement(tv, "channel", id=cid)
    dn = ET.SubElement(channel_el, "display-name")
    dn.text = name


# -----------------------------
# PROGRAMMES SECTION
# -----------------------------
for ch in channels:
    cid = get_channel_id(ch)
    name = get_channel_name(ch)

    if not cid:
        continue

    # 1️⃣ try match by ID
    programs = epg_by_id.get(cid, [])

    # 2️⃣ fallback: match by name (VERY IMPORTANT SAFETY NET)
    if not programs:
        programs = epg_by_name.get(name.lower().strip(), [])

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
        title.text = p.get("title", "No Title")

        if p.get("description"):
            desc = ET.SubElement(prog, "desc", lang="el")
            desc.text = p["description"]

        if p.get("genre"):
            cat = ET.SubElement(prog, "category", lang="el")
            cat.text = p["genre"]


# -----------------------------
# WRITE OUTPUT
# -----------------------------
ET.ElementTree(tv).write(
    "epg.xml",
    encoding="utf-8",
    xml_declaration=True
)

print(f"SUCCESS: XML generated for {len(channels)} channels")

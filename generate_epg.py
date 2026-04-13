import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import re


def to_xmltv_time(value):
    if not value:
        return ""

    try:
        value = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        dt = dt.astimezone(ZoneInfo("Europe/Athens"))
        return dt.strftime("%Y%m%d%H%M%S %z")
    except:
        return ""


def clean_desc(desc):
    if not desc:
        return "", None

    subtitle = None

    m = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if m:
        subtitle = m.group(1).strip()
        desc = desc.replace(m.group(0), "")

    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)

    return re.sub(r"\s{2,}", " ", desc).strip(), subtitle


def cid(ch):
    return str(ch.get("id") or ch.get("channel_id") or ch.get("guid") or "")


# LOAD
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

with open("epg.json", "r", encoding="utf-8") as f:
    epg = json.load(f)


# MAP
epg_map = {}
for ch in epg:
    key = cid(ch)
    if key:
        epg_map[key] = ch.get("items") or ch.get("programs") or []


tv = ET.Element("tv", {"generator-info-name": "EPG Builder FIXED"})


# CHANNEL LIST (ALWAYS FIRST)
for ch in channels:
    key = cid(ch)
    if not key:
        continue

    c = ET.SubElement(tv, "channel", id=key)
    ET.SubElement(c, "display-name", lang="el").text = ch.get("name") or key


# PROGRAMS
total = 0

for ch in channels:
    key = cid(ch)
    if key not in epg_map:
        continue

    for p in epg_map[key]:
        start = to_xmltv_time(p.get("startTime") or p.get("start"))
        stop = to_xmltv_time(p.get("endTime") or p.get("end"))

        # 🔥 FIX: do NOT drop everything
        if not start:
            continue
        if not stop:
            stop = start  # fallback

        prog = ET.SubElement(tv, "programme", {
            "start": start,
            "stop": stop,
            "channel": key
        })

        ET.SubElement(prog, "title", lang="el").text = p.get("title") or "No title"

        desc, sub = clean_desc(p.get("description") or "")
        if sub:
            ET.SubElement(prog, "sub-title", lang="el").text = sub
        if desc:
            ET.SubElement(prog, "desc", lang="el").text = desc

        total += 1


tree = ET.ElementTree(tv)
ET.indent(tree, space="  ")

with open("epg.xml", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print("✔ epg.xml UPDATED")
print("✔ channels:", len(channels))
print("✔ programs:", total)

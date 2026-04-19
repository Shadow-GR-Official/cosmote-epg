import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import html
import os

def to_xmltv_time(value):
    if not value:
        return ""

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        dt = dt.astimezone(ZoneInfo("Europe/Athens"))
        return dt.strftime("%Y%m%d%H%M%S %z")
    except:
        return ""

def cid(ch):
    return str(ch.get("id") or "")

def clean_text(t):
    return html.escape(str(t)) if t else ""

with open("data/epg.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

tv = ET.Element("tv")

total = 0

for ch in channels:
    key = cid(ch)
    if not key:
        continue

    c = ET.SubElement(tv, "channel", id=key)
    ET.SubElement(c, "display-name").text = clean_text(ch.get("name"))

    for p in ch.get("items", []):
        start = to_xmltv_time(p.get("startTime"))
        end = to_xmltv_time(p.get("endTime"))

        if not start:
            continue

        prog = ET.SubElement(tv, "programme", {
            "start": start,
            "stop": end or start,
            "channel": key
        })

        ET.SubElement(prog, "title", {"lang": "el"}).text = clean_text(p.get("title"))

        if p.get("description"):
            ET.SubElement(prog, "desc", {"lang": "el"}).text = clean_text(p.get("description"))

        if p.get("genres"):
            for g in p["genres"]:
                ET.SubElement(prog, "category", {"lang": "el"}).text = clean_text(g)

        total += 1

os.makedirs("data", exist_ok=True)

ET.indent(tv, space="  ")
xml = ET.tostring(tv, encoding="utf-8").decode()

with open("data/epg.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(xml)

print(f"✔ XML generated: {total} programs")

import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from zoneinfo import ZoneInfo


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "epg.json")
XML_FILE = os.path.join(BASE_DIR, "epg.xml")


def to_xmltv_time(ts):
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone(ZoneInfo("Europe/Athens")).strftime("%Y%m%d%H%M%S %z")
    except:
        return ""


def get_id(ch):
    return str(ch.get("id") or ch.get("guid") or ch.get("channel_id") or "")


def run():
    if not os.path.exists(JSON_FILE):
        print("NO JSON FOUND")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    tv = ET.Element("tv")

    for ch in data:
        cid = get_id(ch)
        if not cid:
            continue

        channel_el = ET.SubElement(tv, "channel", id=cid)
        ET.SubElement(channel_el, "display-name").text = cid

        programs = ch.get("items") or ch.get("programs") or []

        for p in programs:
            start = to_xmltv_time(p.get("start") or p.get("startTime"))
            stop = to_xmltv_time(p.get("end") or p.get("endTime"))

            if not start or not stop:
                continue

            prog = ET.SubElement(tv, "programme", {
                "start": start,
                "stop": stop,
                "channel": cid
            })

            ET.SubElement(prog, "title").text = p.get("title") or "No title"

            desc = p.get("description") or ""
            if desc:
                ET.SubElement(prog, "desc").text = desc

    tree = ET.ElementTree(tv)
    ET.indent(tree, space="  ")
    tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

    print("OK XML SAVED:", XML_FILE)


if __name__ == "__main__":
    run()

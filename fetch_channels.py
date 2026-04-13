import requests
import json
import sys
import re
import os
import xml.etree.ElementTree as ET


# ----------------------------
# FORCE BASE DIRECTORY (LOCKED)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

JSON_FILE = os.path.join(BASE_DIR, "epg.json")
XML_FILE = os.path.join(BASE_DIR, "epg.xml")


# ----------------------------
# CLEAN PROGRAM
# ----------------------------
def clean_program(p):
    desc = p.get("description") or ""

    episode = None
    match = re.search(r"Επεισόδιο:\s*(.+?)(?:\n|$)", desc)
    if match:
        episode = match.group(1).strip()
        desc = desc.replace(match.group(0), "")

    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}:\d{2}", "", desc)
    desc = re.sub(r"Διάρκεια:\s*\d+:\d{2}", "", desc)
    desc = re.sub(r"\s{2,}", " ", desc).strip()

    p["description"] = desc

    if episode:
        p["episode"] = episode

    return p


# ----------------------------
# FETCH
# ----------------------------
def fetch(session, url, headers):
    try:
        r = session.get(url, headers=headers, timeout=25)
        if r.status_code == 200:
            return r
        print("HTTP ERROR:", r.status_code)
    except Exception as e:
        print("REQUEST ERROR:", e)

    return None


# ----------------------------
# EXTRACT CHANNELS
# ----------------------------
def extract_channels(data):
    stripes = data.get("stripes", [])
    channels = []

    if isinstance(stripes, list):
        for stripe in stripes:
            if isinstance(stripe, dict) and "channels" in stripe:
                channels.extend(stripe["channels"])

    elif isinstance(stripes, dict):
        channels = stripes.get("channels", [])

    return channels


# ----------------------------
# SAVE JSON (TEMP)
# ----------------------------
def save_json(data):
    if not data:
        raise Exception("EMPTY DATA - ABORT")

    tmp = JSON_FILE + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp, JSON_FILE)

    print("✔ JSON SAVED:", JSON_FILE)


# ----------------------------
# BUILD XMLTV
# ----------------------------
def build_xml(data):
    tv = ET.Element("tv")

    for ch in data:
        channel_id = str(ch.get("id") or ch.get("channel_id") or "unknown")

        channel_el = ET.SubElement(tv, "channel", id=channel_id)
        ET.SubElement(channel_el, "display-name").text = channel_id

        programs = ch.get("items") or ch.get("programs") or []

        for p in programs:
            start = str(p.get("start") or "")
            stop = str(p.get("end") or "")

            prog = ET.SubElement(tv, "programme", {
                "start": start,
                "stop": stop,
                "channel": channel_id
            })

            ET.SubElement(prog, "title").text = p.get("title") or "No title"

            desc = p.get("description") or ""
            if desc:
                ET.SubElement(prog, "desc").text = desc

    return tv


def save_xml(data):
    tv = build_xml(data)

    tree = ET.ElementTree(tv)
    ET.indent(tree, space="  ")

    tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

    print("✔ XML SAVED:", XML_FILE)


# ----------------------------
# RUN ONCE
# ----------------------------
def run_fetch():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "el-GR,el;q=0.9",
        "Referer": "https://cosmotetv.gr",
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    session.get("https://cosmotetv.gr", timeout=20)

    url = "https://www.cosmotetv.gr/api/channels/schedule?locale=el"

    print("[EPG] FETCHING...")

    r = fetch(session, url, headers)

    if not r:
        print("FAILED FETCH")
        return

    data = r.json()
    all_channels = extract_channels(data)

    if not all_channels:
        print("NO CHANNELS FOUND")
        return

    # clean
    for ch in all_channels:
        programs = ch.get("items") or ch.get("programs") or []
        cleaned = [clean_program(p) for p in programs]

        if "items" in ch:
            ch["items"] = cleaned
        else:
            ch["programs"] = cleaned

    # SAVE BOTH
    save_json(all_channels)
    save_xml(all_channels)

    print(f"✔ DONE: {len(all_channels)} channels")


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    try:
        run_fetch()
    except Exception as e:
        print("CRITICAL ERROR:", e)

    sys.exit(0)

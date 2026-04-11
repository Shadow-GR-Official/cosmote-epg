import json
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

# -----------------------------
# TIME FORMAT (FIXED)
# -----------------------------
def to_xmltv_time(iso_str):
    if not iso_str:
        return ""
    try:
        # Η Cosmote επιστρέφει: "2024-04-11T10:30:00Z"
        # Το 'Z' σημαίνει UTC.
        iso_str = iso_str.replace("Z", "")
        dt_utc = datetime.fromisoformat(iso_str)
        
        # Ορίζουμε ότι είναι UTC
        dt_utc = pytz.utc.localize(dt_utc)
        
        # Μετατροπή σε ώρα Ελλάδος (υπολογίζει αυτόματα DST/Καλοκαιρινή)
        athens_tz = pytz.timezone('Europe/Athens')
        dt_athens = dt_utc.astimezone(athens_tz)
        
        # Format για XMLTV: YYYYMMDDHHMMSS +0300 ή +0200
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except Exception:
        return ""

# -----------------------------
# CATEGORY MAP (Συνοπτικό)
# -----------------------------
CATEGORY_MAP = {"Movie": "Ταινία", "Film": "Ταινία", "Series": "Σειρά", "Sports": "Αθλητικά", "News": "Ειδήσεις"}

def normalize_genre(genre):
    if not genre: return None
    return CATEGORY_MAP.get(genre, genre)

# -----------------------------
# LOAD DATA
# -----------------------------
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        channels = json.load(f)
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except FileNotFoundError:
    print("Σφάλμα: Λείπουν τα αρχεία json!")
    exit(1)

# Indexing EPG
epg_by_id = {str(ch.get("id")): ch.get("programs", []) for ch in epg_data if isinstance(ch, dict)}

# -----------------------------
# BUILD XMLTV
# -----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote TV Grabber"})

# Channels
for ch in channels:
    cid = str(ch.get("id"))
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = ch.get("name")

# Programmes
for ch in channels:
    cid = str(ch.get("id"))
    programs = epg_by_id.get(cid, [])

    for p in programs:
        start = to_xmltv_time(p.get("start"))
        stop = to_xmltv_time(p.get("end"))
        
        if not start or not stop: continue

        prog = ET.SubElement(tv, "programme", start=start, stop=stop, channel=cid)
        ET.SubElement(prog, "title", lang="el").text = p.get("title", "Χωρίς τίτλο")
        
        if p.get("description"):
            ET.SubElement(prog, "desc", lang="el").text = p["description"]
        
        if p.get("genre"):
            cat = ET.SubElement(prog, "category", lang="el")
            cat.text = normalize_genre(p["genre"])

# -----------------------------
# SAVE XML
# -----------------------------
tree = ET.ElementTree(tv)
ET.indent(tree, space="\t", level=0)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print("SUCCESS: Το epg.xml δημιουργήθηκε με σωστές ώρες Ελλάδος!")

import json
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz  # Χρειάζεται εγκατάσταση: pip install pytz

# -----------------------------
# TIME FORMAT (FIXED FOR GREECE)
# -----------------------------
def to_xmltv_time(iso_str):
    if not iso_str:
        return ""

    try:
        # 1. Καθαρισμός του 'Z' και μετατροπή σε datetime αντικείμενο (θεωρούμε ότι η πηγή είναι UTC)
        iso_str = iso_str.replace("Z", "")
        dt_utc = datetime.fromisoformat(iso_str)
        
        # 2. Ορίζουμε ότι αυτή η ώρα είναι UTC
        dt_utc = pytz.utc.localize(dt_utc)
        
        # 3. Μετατροπή σε ώρα Ελλάδος (υπολογίζει αυτόματα καλοκαίρι/χειμώνα)
        athens_tz = pytz.timezone('Europe/Athens')
        dt_athens = dt_utc.astimezone(athens_tz)
        
        # 4. Επιστροφή στο σωστό XMLTV format με το σωστό offset (π.χ. +0300 ή +0200)
        return dt_athens.strftime("%Y%m%d%H%M%S %z")
    except Exception as e:
        return ""

# -----------------------------
# CATEGORY SYSTEM (EL)
# -----------------------------
CATEGORY_MAP = {
    "Movie": "Ταινία", "Film": "Ταινία", "Series": "Σειρά", "Drama": "Δραματική σειρά",
    "Comedy": "Κωμωδία", "Romance": "Ρομαντική", "Action": "Δράσης", "Thriller": "Θρίλερ",
    "Horror": "Τρόμου", "Mystery": "Μυστηρίου", "Crime": "Αστυνομική", "Sci Fi": "Επιστημονικής φαντασίας",
    "Science Fiction": "Επιστημονικής φαντασίας", "Fantasy": "Φαντασίας", "Adventure": "Περιπέτεια",
    "Animation": "Κινούμενα σχέδια", "Family": "Οικογενειακή", "News": "Ειδήσεις", "Weather": "Καιρός",
    "Documentary": "Ντοκιμαντέρ", "Reality": "Reality", "Game Show": "Παιχνίδι", "Quiz": "Παιχνίδι γνώσεων",
    "Lifestyle": "Lifestyle", "Cooking": "Μαγειρική", "Travel": "Ταξίδια", "Health": "Υγεία",
    "Sports": "Αθλητικά", "Football": "Ποδόσφαιρο", "Soccer": "Ποδόσφαιρο", "Basketball": "Μπάσκετ",
    "Tennis": "Τένις", "Motorsport": "Μηχανοκίνητα", "Kids": "Παιδικά", "Cartoon": "Κινούμενα σχέδια",
    "Anime": "Anime", "Science": "Επιστήμη", "Engineering": "Μηχανική", "History": "Ιστορία", "Nature": "Φύση",
    "Music": "Μουσική", "Concert": "Συναυλία",
}

def normalize_genre(genre):
    if not genre: return None
    g = " ".join(genre.replace("&", "and").replace("-", " ").replace("_", " ").split()).title()
    return CATEGORY_MAP.get(g, CATEGORY_MAP.get(genre, genre))

# -----------------------------
# CHANNEL HELPERS
# -----------------------------
def get_channel_id(ch): return ch.get("id") if isinstance(ch, dict) else None
def get_channel_name(ch): return ch.get("name", "") if isinstance(ch, dict) else ""

# -----------------------------
# LOAD FILES
# -----------------------------
try:
    with open("channels.json", "r", encoding="utf-8") as f:
        channels = json.load(f)
    with open("epg.json", "r", encoding="utf-8") as f:
        epg_data = json.load(f)
except FileNotFoundError as e:
    print(f"Σφάλμα: Δεν βρέθηκε το αρχείο {e.filename}")
    exit(1)

# -----------------------------
# BUILD EPG INDEX
# -----------------------------
epg_by_id = {}
epg_by_name = {}

for ch in epg_data:
    if not isinstance(ch, dict): continue
    cid = ch.get("id") or ch.get("channel_id") or ch.get("guid")
    name = ch.get("name") or ch.get("title")
    programs = ch.get("programs", [])
    if cid: epg_by_id[cid] = programs
    if name: epg_by_name[name.lower().strip()] = programs

# -----------------------------
# CREATE XMLTV ROOT
# -----------------------------
tv = ET.Element("tv", {"generator-info-name": "Cosmote EPG Fixer"})

# -----------------------------
# CHANNELS & PROGRAMMES
# -----------------------------
# Πρώτα γράφουμε όλα τα κανάλια
for ch in channels:
    cid = get_channel_id(ch)
    if not cid: continue
    channel_el = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(channel_el, "display-name", lang="el").text = get_channel_name(ch)

# Μετά γράφουμε όλα τα προγράμματα
for ch in channels:
    cid = get_channel_id(ch)
    name = get_channel_name(ch)
    if not cid: continue

    programs = epg_by_id.get(cid, epg_by_name.get(name.lower().strip(), []))

    for p in programs:
        if not isinstance(p, dict): continue
        
        start_time = to_xmltv_time(p.get("start"))
        stop_time = to_xmltv_time(p.get("end"))
        
        if not start_time or not stop_time: continue

        prog = ET.SubElement(tv, "programme", start=start_time, stop=stop_time, channel=cid)
        ET.SubElement(prog, "title", lang="el").text = p.get("title", "Χωρίς τίτλο")
        
        if p.get("description"):
            ET.SubElement(prog, "desc", lang="el").text = p["description"]

        genre_raw = p.get("genre")
        if genre_raw:
            for g in str(genre_raw).split(","):
                normalized = normalize_genre(g.strip())
                if normalized:
                    ET.SubElement(prog, "category", lang="el").text = normalized

# -----------------------------
# WRITE OUTPUT
# -----------------------------
tree = ET.ElementTree(tv)
ET.indent(tree, space="\t", level=0) # Για να είναι ευανάγνωστο το XML
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print(f"SUCCESS: Το epg.xml δημιουργήθηκε για {len(channels)} κανάλια.")

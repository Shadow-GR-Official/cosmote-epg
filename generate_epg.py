import json
import xml.etree.ElementTree as ET
from datetime import datetime


# -----------------------------
# TIME FORMAT
# -----------------------------
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
# CATEGORY SYSTEM (EL)
# -----------------------------
CATEGORY_MAP = {
    # Movies / Series
    "Movie": "Ταινία",
    "Film": "Ταινία",
    "Series": "Σειρά",
    "Drama": "Δραματική σειρά",
    "Comedy": "Κωμωδία",
    "Romance": "Ρομαντική",
    "Action": "Δράσης",
    "Thriller": "Θρίλερ",
    "Horror": "Τρόμου",
    "Mystery": "Μυστηρίου",
    "Crime": "Αστυνομική",
    "Sci Fi": "Επιστημονικής φαντασίας",
    "Science Fiction": "Επιστημονικής φαντασίας",
    "Fantasy": "Φαντασίας",
    "Adventure": "Περιπέτεια",
    "Animation": "Κινούμενα σχέδια",
    "Family": "Οικογενειακή",

    # TV
    "News": "Ειδήσεις",
    "Weather": "Καιρός",
    "Documentary": "Ντοκιμαντέρ",
    "Reality": "Reality",
    "Game Show": "Παιχνίδι",
    "Quiz": "Παιχνίδι γνώσεων",
    "Lifestyle": "Lifestyle",
    "Cooking": "Μαγειρική",
    "Travel": "Ταξίδια",
    "Health": "Υγεία",

    # Sports
    "Sports": "Αθλητικά",
    "Football": "Ποδόσφαιρο",
    "Soccer": "Ποδόσφαιρο",
    "Basketball": "Μπάσκετ",
    "Tennis": "Τένις",
    "Motorsport": "Μηχανοκίνητα",

    # Kids
    "Kids": "Παιδικά",
    "Cartoon": "Κινούμενα σχέδια",
    "Anime": "Anime",

    # Knowledge
    "Science": "Επιστήμη",
    "Engineering": "Μηχανική",
    "Science Engineering": "Επιστήμη και Μηχανική",
    "Science And Engineering": "Επιστήμη και Μηχανική",
    "Science Technology": "Επιστήμη και Τεχνολογία",
    "Technology": "Τεχνολογία",
    "History": "Ιστορία",
    "Nature": "Φύση",

    # Music
    "Music": "Μουσική",
    "Concert": "Συναυλία",
}


def normalize_genre(genre):
    if not genre:
        return None

    g = genre.strip()

    # normalize weird formats
    g = g.replace("&", "and")
    g = g.replace("-", " ")
    g = g.replace("_", " ")
    g = " ".join(g.split())  # remove double spaces
    g = g.title()

    # direct hit
    if g in CATEGORY_MAP:
        return CATEGORY_MAP[g]

    # fallback original
    return CATEGORY_MAP.get(genre, genre)


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
# BUILD EPG INDEX
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
# CHANNELS
# -----------------------------
for ch in channels:
    cid = get_channel_id(ch)
    name = get_channel_name(ch)

    if not cid:
        continue

    channel_el = ET.SubElement(tv, "channel", id=cid)
    dn = ET.SubElement(channel_el, "display-name", lang="el")
    dn.text = name


# -----------------------------
# PROGRAMMES
# -----------------------------
for ch in channels:
    cid = get_channel_id(ch)
    name = get_channel_name(ch)

    if not cid:
        continue

    programs = epg_by_id.get(cid, [])

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

        # Title
        title = ET.SubElement(prog, "title", lang="el")
        title.text = p.get("title", "Χωρίς τίτλο")

        # Description
        if p.get("description"):
            desc = ET.SubElement(prog, "desc", lang="el")
            desc.text = p["description"]

        # Categories (MULTI SUPPORT)
        genre_raw = p.get("genre")

        if genre_raw:
            genres = str(genre_raw).split(",")

            for g in genres:
                g = g.strip()
                normalized = normalize_genre(g)

                if normalized:
                    cat = ET.SubElement(prog, "category", lang="el")
                    cat.text = normalized


# -----------------------------
# WRITE OUTPUT
# -----------------------------
ET.ElementTree(tv).write(
    "epg.xml",
    encoding="utf-8",
    xml_declaration=True
)

print(f"SUCCESS: XML generated for {len(channels)} channels")

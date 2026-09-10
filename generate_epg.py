
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import os


def to_xmltv_time(value):
    if not value:
        return ""

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        dt = dt.astimezone(ZoneInfo("Europe/Athens"))
        return dt.strftime("%Y%m%d%H%M%S %z")
    except Exception:
        return ""


with open("data/epg.json", "r", encoding="utf-8") as f:
    epg = json.load(f)


channels_cache_file = "data/channels_cache.json"
channels_cache = {}


for ch in epg:
    cid = ch.get("id")

    if not cid:
        continue

    channels_cache[cid] = {
        "id": cid,
        "name": ch.get("name") or cid,
        "logo": ch.get("logo") or ""
    }


os.makedirs("data", exist_ok=True)

with open(channels_cache_file, "w", encoding="utf-8") as f:
    json.dump(
        channels_cache,
        f,
        ensure_ascii=False,
        indent=2
    )


tv = ET.Element("tv")


for cid, ch in channels_cache.items():
    channel = ET.SubElement(
        tv,
        "channel",
        {"id": cid}
    )

    ET.SubElement(
        channel,
        "display-name"
    ).text = ch.get("name") or cid

    logo = ch.get("logo")

    if logo:
        ET.SubElement(
            channel,
            "icon",
            {"src": logo}
        )


total = 0


for ch in epg:
    cid = ch.get("id")

    if not cid:
        continue

    for p in ch.get("items", []):
        start = to_xmltv_time(p.get("startTime"))
        stop = to_xmltv_time(p.get("endTime"))

        if not start or not stop:
            continue

        programme = ET.SubElement(
            tv,
            "programme",
            {
                "start": start,
                "stop": stop,
                "channel": cid
            }
        )

        ET.SubElement(
            programme,
            "title",
            {"lang": "el"}
        ).text = p.get("title") or "No title"

        description = p.get("description")

        if description:
            ET.SubElement(
                programme,
                "desc",
                {"lang": "el"}
            ).text = description

        genres = p.get("genres") or []

        if isinstance(genres, str):
            genres = [genres]

        genres = [
            genre for genre in genres
            if genre
        ]

        genres = list(dict.fromkeys(genres))

        for genre in genres:
            ET.SubElement(
                programme,
                "category",
                {"lang": "el"}
            ).text = genre

        total += 1


ET.indent(tv, space="  ")

xml_str = ET.tostring(
    tv,
    encoding="utf-8"
).decode("utf-8")


with open("data/epg.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(xml_str)


print("✔ XML generated")
print("✔ channels refreshed:", len(channels_cache))
print("✔ programmes:", total)


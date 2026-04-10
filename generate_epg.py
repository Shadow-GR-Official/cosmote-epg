import requests
import json
from datetime import datetime

API = "https://www.cosmotetv.gr/api/channels/schedule?"


def to_xmltv_time(iso_str):
    dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%Y%m%d%H%M%S +0000")


def main():

    # -------------------------
    # LOAD CHANNELS (STATIC)
    # -------------------------
    try:
        with open("channels.json", "r", encoding="utf-8") as f:
            channels_list = json.load(f)
    except:
        channels_list = []

    channel_map = {
        c["id"]: c.get("name")
        for c in channels_list
        if "id" in c
    }

    # -------------------------
    # FETCH EPG
    # -------------------------
    r = requests.get(API, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.cosmotetv.gr/"
    })

    data = r.json()
    channels = data.get("stripes", {}).get("channels", [])

    # -------------------------
    # BUILD XMLTV
    # -------------------------
    xml = []
    xml.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml.append("<tv>")

    # ✔ STATIC CHANNELS (from file, NOT API rewrite)
    for cid, name in channel_map.items():
        xml.append(f'<channel id="{cid}">')
        xml.append(f"<display-name>{name}</display-name>")
        xml.append("</channel>")

    # -------------------------
    # PROGRAMMES ONLY
    # -------------------------
    for ch in channels:

        cid = ch.get("guid")
        items = ch.get("items", []) or []

        for p in items:

            qoe = p.get("qoe", {})

            title = qoe.get("title") or p.get("title") or ""
            desc = p.get("description") or ""

            start = to_xmltv_time(p.get("startTime"))
            stop = to_xmltv_time(p.get("endTime"))

            xml.append(
                f'<programme start="{start}" stop="{stop}" channel="{cid}">'
            )
            xml.append(f"<title lang=\"el\">{title}</title>")
            xml.append(f"<desc lang=\"el\">{desc}</desc>")
            xml.append("</programme>")

    xml.append("</tv>")

    # -------------------------
    # WRITE OUTPUT
    # -------------------------
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))

    print(f"SUCCESS: XMLTV generated with {len(channel_map)} channels")


if __name__ == "__main__":
    main()

import time
import datetime
import requests
import json
from xml.etree.ElementTree import Element, SubElement, ElementTree

API = "https://www.cosmotetv.gr/api/channels/schedule?"

def xmltv_time(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y%m%d%H%M%S +0300")

def fetch(channel_id, start, end):
    r = requests.get(API, params={
        "locale": "el",
        "from": start,
        "to": end,
        "channels": channel_id
    }, headers={"User-Agent": "Mozilla/5.0"})

    try:
        return r.json()
    except:
        return []

def main():
    with open("channels.json", encoding="utf-8") as f:
        channels = json.load(f)

    now = int(time.time())
    end = now + 3 * 24 * 3600

    tv = Element("tv")

    for ch in channels:

        data = fetch(ch["id"], now, end)

        channel_el = SubElement(tv, "channel", id=ch["id"])
        SubElement(channel_el, "display-name").text = ch["name"]

        if ch.get("logo"):
            SubElement(channel_el, "icon", {"src": ch["logo"]})

        for p in data:
            prog = SubElement(tv, "programme", {
                "start": xmltv_time(p["startTime"]),
                "stop": xmltv_time(p["endTime"]),
                "channel": ch["id"]
            })

            SubElement(prog, "title").text = p.get("title", "")
            SubElement(prog).text = p.get("description", "")

    ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()

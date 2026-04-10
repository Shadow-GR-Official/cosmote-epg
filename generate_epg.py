import time
import datetime
import requests
import json
from xml.etree.ElementTree import Element, SubElement, ElementTree

API_URL = "https://www.cosmotetv.gr/api/channels/schedule?"

def unix_to_xmltv(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%Y%m%d%H%M%S +0300")

def fetch_epg(channel_id, start, end):
    params = {
        "locale": "el",
        "from": start,
        "to": end,
        "channels": channel_id
    }

    r = requests.get(API_URL, params=params, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    if r.status_code != 200:
        return []

    try:
        return r.json()
    except:
        return []

def main():
    with open("channels.json", encoding="utf-8") as f:
        channels = json.load(f)

    now = int(time.time())
    end = now + 2 * 24 * 3600

    tv = Element("tv")

    for ch in channels:
        if not ch.get("id"):
            continue

        data = fetch_epg(ch["id"], now, end)

        channel_el = SubElement(tv, "channel", id=ch["id"])
        SubElement(channel_el, "display-name").text = ch.get("name", ch["id"])

        for prog in data:
            if not prog.get("startTime"):
                continue

            p = SubElement(tv, "programme", {
                "start": unix_to_xmltv(prog["startTime"]),
                "stop": unix_to_xmltv(prog["endTime"]),
                "channel": ch["id"]
            })

            SubElement(p, "title").text = prog.get("title", "")
            SubElement(p, "desc").text = prog.get("description", "")

    ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()

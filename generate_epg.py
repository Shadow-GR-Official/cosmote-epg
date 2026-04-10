import requests
import time
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree
import json

API_URL = "https://www.cosmotetv.gr/api/channels/schedule"

def unix_to_xmltv(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%Y%m%d%H%M%S +0300")

def get_schedule(channel_id, start, end):
    params = {
        "locale": "el",
        "from": start,
        "to": end,
        "channels": channel_id
    }

    r = requests.get(API_URL, params=params)
    if r.status_code != 200:
        return []
    return r.json()

def main():
    with open("channels.json", encoding="utf-8") as f:
        channels = json.load(f)

    now = int(time.time())
    future = now + 2 * 24 * 3600  # 2 μέρες

    tv = Element("tv")

    for ch in channels:
        if not ch["id"]:
            continue

        channel_el = SubElement(tv, "channel", id=ch["id"])
        SubElement(channel_el, "display-name").text = ch["name"]

        data = get_schedule(ch["id"], now, future)

        for prog in data:
            if not prog.get("startTime"):
                continue

            programme = SubElement(tv, "programme", {
                "start": unix_to_xmltv(prog["startTime"]),
                "stop": unix_to_xmltv(prog["endTime"]),
                "channel": ch["id"]
            })

            SubElement(programme, "title").text = prog.get("title", "")
            SubElement(programme, "desc").text = prog.get("description", "")

        time.sleep(0.2)

    ElementTree(tv).write("guide.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()

import time
import datetime
import requests
import json
from xml.etree.ElementTree import Element, SubElement, ElementTree

API = "https://www.cosmotetv.gr/api/channels/schedule?"

def xmltv_time(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y%m%d%H%M%S +0300")

def fetch_epg(channel_id, start, end):

    r = requests.get(API, params={
        "locale": "el",
        "from": start,
        "to": end,
        "channels": channel_id
    }, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    # 🔥 DEBUG (important)
    print("\n==============================")
    print("CHANNEL:", channel_id)
    print("URL:", r.url)
    print("STATUS:", r.status_code)
    print("RESPONSE (first 300 chars):", r.text[:300])

    try:
        data = r.json()
    except Exception as e:
        print("JSON ERROR:", e)
        return []

    print("PARSED DATA TYPE:", type(data))
    print("PARSED DATA SAMPLE:", str(data)[:200])

    # normalize πιθανών formats
    if isinstance(data, dict):
        data = data.get("data") or data.get("programs") or data.get("schedule") or []

    if not isinstance(data, list):
        return []

    return data


def main():

    with open("channels.json", encoding="utf-8") as f:
        channels = json.load(f)

    if not channels:
        print("ERROR: channels.json is empty")
        return

    now = int(time.time())
    end = now + 2 * 24 * 3600

    tv = Element("tv")

    for ch in channels:

        channel_id = ch.get("id")
        name = ch.get("name", channel_id)

        if not channel_id:
            continue

        data = fetch_epg(channel_id, now, end)

        # channel node
        channel_el = SubElement(tv, "channel", id=channel_id)
        SubElement(channel_el, "display-name").text = name

        # programmes
        for p in data:

            if not isinstance(p, dict):
                continue

            start = p.get("startTime") or p.get("start")
            end_t = p.get("endTime") or p.get("end")

            if not start or not end_t:
                continue

            prog = SubElement(tv, "programme", {
                "start": xmltv_time(start),
                "stop": xmltv_time(end_t),
                "channel": channel_id
            })

            SubElement(prog, "title").text = p.get("title", "")
            SubElement(prog, "desc").text = p.get("description", "")

    ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)

    print("\nDONE → epg.xml generated")


if __name__ == "__main__":
    main()

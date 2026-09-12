import json
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from collections import defaultdict


INPUT_FILE = "data/epg.json"
CHANNELS_CACHE_FILE = "data/channels_cache.json"
OUTPUT_FILE = "data/epg.xml"


def to_xmltv_time(value):
    if not value:
        return ""

    try:
        dt = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        dt = dt.astimezone(
            ZoneInfo("Europe/Athens")
        )

        return dt.strftime("%Y%m%d%H%M%S %z")

    except Exception:
        return ""


# ============================================================
# LOAD EPG
# ============================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    epg = json.load(f)

if not isinstance(epg, list):
    raise RuntimeError("data/epg.json does not contain a channel list")


# ============================================================
# BUILD CHANNEL CACHE
# ============================================================

channels_cache = {}

for ch in epg:
    cid = str(ch.get("id") or "").strip()

    if not cid:
        continue

    channels_cache[cid] = {
        "id": cid,
        "name": ch.get("name") or cid,
        "logo": ch.get("logo") or ""
    }


os.makedirs("data", exist_ok=True)

with open(
    CHANNELS_CACHE_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        channels_cache,
        f,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# INPUT STATISTICS
# ============================================================

input_channels = 0
input_programmes = 0

channel_input_counts = defaultdict(int)

for ch in epg:
    cid = str(ch.get("id") or "").strip()

    if not cid:
        continue

    input_channels += 1

    items = ch.get("items") or []

    for p in items:
        input_programmes += 1
        channel_input_counts[cid] += 1


print()
print("=" * 60)
print("MAGENTA EPG INPUT")
print("=" * 60)
print("Channels:", input_channels)
print("Programmes:", input_programmes)
print("=" * 60)


# ============================================================
# CREATE XML
# ============================================================

tv = ET.Element("tv")


# ------------------------------------------------------------
# CHANNELS
# ------------------------------------------------------------

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


# ============================================================
# PROGRAMMES
# ============================================================

written_programmes = 0
skipped_invalid_time = 0

channel_output_counts = defaultdict(int)

for ch in epg:

    cid = str(ch.get("id") or "").strip()

    if not cid:
        continue

    for p in ch.get("items", []):

        start = to_xmltv_time(
            p.get("startTime")
        )

        stop = to_xmltv_time(
            p.get("endTime")
        )

        if not start or not stop:

            skipped_invalid_time += 1

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

        title = p.get("title") or "No title"

        ET.SubElement(
            programme,
            "title",
            {"lang": "el"}
        ).text = title

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
            genre
            for genre in genres
            if genre
        ]

        genres = list(
            dict.fromkeys(genres)
        )

        for genre in genres:

            ET.SubElement(
                programme,
                "category",
                {"lang": "el"}
            ).text = genre

        written_programmes += 1
        channel_output_counts[cid] += 1


# ============================================================
# WRITE XML
# ============================================================

ET.indent(
    tv,
    space="  "
)

xml_str = ET.tostring(
    tv,
    encoding="utf-8"
).decode("utf-8")


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
    )

    f.write(xml_str)


# ============================================================
# FINAL STATISTICS
# ============================================================

output_channels = len(channels_cache)

print()
print("=" * 60)
print("MAGENTA EPG XML OUTPUT")
print("=" * 60)
print("Channels:", output_channels)
print("Programmes:", written_programmes)
print("Skipped invalid time:", skipped_invalid_time)
print("=" * 60)


# ============================================================
# CHANNEL-BY-CHANNEL CHECK
# ============================================================

print()
print("=" * 60)
print("CHANNEL PROGRAMME CHECK")
print("=" * 60)

zero_output_channels = []

for ch in sorted(
    epg,
    key=lambda x: (x.get("name") or "").lower()
):

    cid = str(ch.get("id") or "").strip()

    if not cid:
        continue

    name = ch.get("name") or cid

    input_count = channel_input_counts.get(
        cid,
        0
    )

    output_count = channel_output_counts.get(
        cid,
        0
    )

    print(
        f"{name} [{cid}] "
        f"→ input: {input_count} / XML: {output_count}"
    )

    if input_count > 0 and output_count == 0:

        zero_output_channels.append(
            f"{name} [{cid}]"
        )


# ============================================================
# WARNINGS
# ============================================================

print()
print("=" * 60)
print("DIAGNOSTICS")
print("=" * 60)

if skipped_invalid_time > 0:

    print(
        "WARNING: programs skipped because "
        "startTime/endTime could not be parsed:",
        skipped_invalid_time
    )

else:

    print(
        "OK: No programmes were skipped "
        "because of invalid timestamps."
    )


if zero_output_channels:

    print()
    print(
        "WARNING: CHANNELS WITH PROGRAMMES "
        "IN JSON BUT ZERO PROGRAMMES IN XML:"
    )

    for name in zero_output_channels:
        print("  -", name)

else:

    print(
        "OK: Every channel containing programmes "
        "in epg.json also has programmes in epg.xml."
    )


print()
print("=" * 60)
print("EPG GENERATION COMPLETE")
print("=" * 60)

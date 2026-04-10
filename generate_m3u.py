import json

OUTPUT = "channels.m3u"
CHANNELS_FILE = "channels.json"


def main():

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        channels = json.load(f)

    lines = []

    # M3U header
    lines.append("#EXTM3U")

    for ch in channels:

        channel_id = ch.get("id") or ch.get("channel_id")
        name = ch.get("name") or ch.get("channel_name") or "Unknown"
        logo = ch.get("logo") or ""

        # placeholder stream url (you will fill later)
        stream_url = "http://127.0.0.1/stream/" + channel_id

        lines.append(
            f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name}" tvg-logo="{logo}",{name}'
        )
        lines.append(stream_url)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"SUCCESS: M3U created with {len(channels)} channels")


if __name__ == "__main__":
    main()

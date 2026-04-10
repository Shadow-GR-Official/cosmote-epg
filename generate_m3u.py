import json
import os

OUTPUT = "channels.m3u"
CHANNELS_FILE = "channels.json"


def main():

    if not os.path.exists(CHANNELS_FILE):
        print("ERROR: channels.json not found")
        return

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        channels = json.load(f)

    if not channels:
        print("ERROR: channels.json is empty")
        return

    lines = ["#EXTM3U"]

    for ch in channels:

        channel_id = ch.get("id") or ch.get("channel_id")
        name = ch.get("name") or ch.get("channel_name") or "Unknown"
        logo = ch.get("logo") or ""

        if not channel_id:
            continue

        stream_url = f"http://127.0.0.1/{channel_id}"

        lines.append(
            f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name}" tvg-logo="{logo}",{name}'
        )
        lines.append(stream_url)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"SUCCESS: created {OUTPUT} with {len(lines)//2} channels")


if __name__ == "__main__":
    main()

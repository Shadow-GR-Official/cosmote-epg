def parse_m3u(file="playlist.m3u"):
    channels = []

    with open(file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#EXTINF"):
                name = line.split(",")[-1].strip()
                channels.append({
                    "name": name,
                    "id": name.lower().replace(" ", "")
                })

    return channels

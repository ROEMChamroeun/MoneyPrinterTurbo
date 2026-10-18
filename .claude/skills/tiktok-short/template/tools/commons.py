"""Wikimedia Commons helper: search photos, download one with its licence and author.

  python3 tools/commons.py search "Bon Om Touk" [limit]
  python3 tools/commons.py get "File:Some photo.jpg" assets/commons/<name>.jpg [width]
`get` writes the image plus <name>.json (title, author, licence, page URL) for the credits.
Commons answers 429 to fast or anonymous clients, so every request names this tool and waits a second.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = "money-printer-short/1.0 (Khmer education short; contact chamroeun via project)"
API = "https://commons.wikimedia.org/w/api.php"


def call(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({"format": "json", **params})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    time.sleep(3.0)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def strip(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def info(pages: dict) -> list[dict]:
    out = []
    for p in sorted(pages.values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        out.append({"title": p["title"], "w": ii["width"], "h": ii["height"],
                    "license": strip(m.get("LicenseShortName", {}).get("value", "")),
                    "author": strip(m.get("Artist", {}).get("value", "")),
                    "url": ii.get("url"), "thumb": ii.get("thumburl"), "page": ii.get("descriptionurl")})
    return out


def search(q: str, limit: int = 12) -> None:
    d = call({"action": "query", "generator": "search", "gsrnamespace": 6, "gsrlimit": limit, "gsrsearch": q,
              "prop": "imageinfo", "iiprop": "size|extmetadata|url", "iiextmetadatafilter": "LicenseShortName|Artist"})
    for x in info(d.get("query", {}).get("pages", {})):
        print(f'{x["w"]:5d}x{x["h"]:<5d} | {x["license"][:16]:16s} | {x["author"][:28]:28s} | {x["title"][5:95]}')


def get(title: str, dest: str, width: int = 2160) -> None:
    d = call({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "size|extmetadata|url",
              "iiurlwidth": width, "iiextmetadatafilter": "LicenseShortName|Artist"})
    x = info(d["query"]["pages"])[0]
    src = x["thumb"] if x["w"] > width else x["url"]
    dest_p = Path(dest)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(src, headers={"User-Agent": UA})
    time.sleep(5.0)
    with urllib.request.urlopen(req, timeout=120) as r:
        dest_p.write_bytes(r.read())
    dest_p.with_suffix(".json").write_text(json.dumps(x, ensure_ascii=False, indent=1))
    print(f'{dest}: {x["w"]}x{x["h"]} {x["license"]} by {x["author"]}')


def sheet(titles: list[str], dest: str, width: int = 360) -> None:
    """Contact sheet of numbered thumbnails (to choose photos by eye)."""
    from io import BytesIO
    from PIL import Image, ImageDraw
    thumbs = []
    for i in range(0, len(titles), 40):
        d = call({"action": "query", "titles": "|".join(titles[i:i + 40]), "prop": "imageinfo",
                  "iiprop": "size|url", "iiurlwidth": width})
        by_title = {p["title"]: p for p in d["query"]["pages"].values()}
        for t in titles[i:i + 40]:
            p = by_title.get(t) or by_title.get(t.replace("_", " "))
            if p and "imageinfo" in p:
                thumbs.append((t, p["imageinfo"][0]["thumburl"]))
    cols, cell = 6, width
    sheet_img = Image.new("RGB", (cols * cell, ((len(thumbs) + cols - 1) // cols) * (cell + 24)), "white")
    for n, (t, url) in enumerate(thumbs):
        time.sleep(0.3)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
            im = Image.open(BytesIO(r.read())).convert("RGB")
        im.thumbnail((cell, cell))
        x, y = (n % cols) * cell, (n // cols) * (cell + 24)
        sheet_img.paste(im, (x, y))
        ImageDraw.Draw(sheet_img).text((x + 4, y + cell + 4), f"{n}: {t[5:40]}", fill="black")
    sheet_img.save(dest, quality=85)
    print(f"{dest}: {len(thumbs)} thumbnails")


if __name__ == "__main__":
    if sys.argv[1] == "search":
        search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12)
    elif sys.argv[1] == "sheet":
        sheet([ln.strip() for ln in Path(sys.argv[2]).read_text().splitlines() if ln.strip()], sys.argv[3])
    elif sys.argv[1] == "get":
        get(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 2160)

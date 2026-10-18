"""Pixabay video helper: find portrait clips, look at them, download one.

  python3 tools/pixabay.py sheet "full moon" <out.jpg> [n]   numbered contact sheet of portrait clips (id under each)
  python3 tools/pixabay.py get "<query>" <id> assets/pixabay/<name>.mp4   largest rendition + <name>.json
     (the API refuses lookups by id for these clips, so the clip is found again through its search)
The key is config.toml's pixabay_api_keys. Pixabay refuses Python's default User-Agent (403, error 1010).
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def key() -> str:
    txt = (ROOT / "config.toml").read_text()
    m = re.search(r"pixabay_api_keys\s*=\s*\[([^\]]*)\]", txt, re.S)
    return re.findall(r'"([^"]+)"', m.group(1))[0]


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
        return r.read()


def search(q: str, pages: int = 2) -> list[dict]:
    hits = []
    for page in range(1, pages + 1):
        url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
            {"key": key(), "q": q, "per_page": 200, "page": page, "safesearch": "true"})
        d = json.loads(fetch(url))
        hits += d.get("hits", [])
        if len(d.get("hits", [])) < 200:
            break
    out = []
    for h in hits:
        v = h["videos"]
        best = max((v[s] for s in ("large", "medium", "small") if v.get(s, {}).get("url")),
                   key=lambda r: r["width"] * r["height"])
        if best["height"] > best["width"] and best["height"] >= 1280:
            out.append({"id": h["id"], "w": best["width"], "h": best["height"], "dur": h["duration"],
                        "tags": h["tags"], "user": h["user"], "page": h["pageURL"], "url": best["url"],
                        "thumb": v["medium"].get("thumbnail") or v["small"].get("thumbnail")})
    return out


def sheet(q: str, dest: str, n: int = 24) -> None:
    from PIL import Image, ImageDraw
    clips = search(q)[:n]
    cols, cw, ch = 8, 220, 390
    img = Image.new("RGB", (cols * cw, ((len(clips) + cols - 1) // cols) * (ch + 30)), "white")
    for i, c in enumerate(clips):
        try:
            im = Image.open(BytesIO(fetch(c["thumb"]))).convert("RGB")
            im.thumbnail((cw, ch))
            img.paste(im, ((i % cols) * cw, (i // cols) * (ch + 30)))
        except Exception as e:                       # a missing thumbnail leaves a blank cell
            print("thumb failed", c["id"], e)
        ImageDraw.Draw(img).text(((i % cols) * cw + 4, (i // cols) * (ch + 30) + ch + 4),
                                 f'{c["id"]} {c["dur"]}s {c["w"]}x{c["h"]}', fill="black")
    img.save(dest, quality=85)
    for c in clips:
        print(c["id"], c["dur"], f'{c["w"]}x{c["h"]}', c["tags"][:60])


def get(q: str, clip_id: str, dest: str) -> None:
    c = next(c for c in search(q) if str(c["id"]) == str(clip_id))
    p = Path(dest)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(fetch(c["url"]))
    p.with_suffix(".json").write_text(json.dumps({"id": c["id"], "user": c["user"], "page": c["page"],
                                                  "w": c["w"], "h": c["h"], "dur": c["dur"],
                                                  "license": "Pixabay Content License"}, indent=1))
    print(f'{dest}: {c["w"]}x{c["h"]} {c["dur"]}s by {c["user"]}')


if __name__ == "__main__":
    if sys.argv[1] == "sheet":
        sheet(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 24)
    elif sys.argv[1] == "get":
        get(sys.argv[2], sys.argv[3], sys.argv[4])

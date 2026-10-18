"""Rank TikTok search results saved as playwright-cli snapshots (tiktok.com/search/video?q=...).

  python3 tiktok_cards.py cards snap.yml [n]        posts by likes: likes | date | @author | caption
  python3 tiktok_cards.py tags snap1.yml [snap2..]  hashtags used by those posts: posts, posts this season, total likes
The number on a search card is LIKES (heart icon), not views. Dates read "13h ago", "2d ago", "1w ago", "M-D" (this
year) or "YYYY-M-D" (older). Snapshot: playwright-cli -s=chrome snapshot --filename=snap.yml
"""
from __future__ import annotations

import collections
import re
import sys


def cards(path: str) -> list[dict]:
    lines = open(path, encoding="utf-8").read().splitlines()
    out, seen = [], set()
    for i, line in enumerate(lines):
        m = re.search(r"/url: https://www\.tiktok\.com/@([^/]+)/video/(\d+)", line)
        if not m or m.group(2) in seen:
            continue
        seen.add(m.group(2))
        count = cap = date = ""
        for s in lines[i + 1:i + 40]:
            if not count and (c := re.search(r'strong \[ref=[^\]]+\]: "?([\d.]+[KM]?)"?$', s)):
                count = c.group(1)
            if not cap and (c := re.search(r'img "(.+?)( created by .*)?" \[ref', s)):
                cap = c.group(1)
            if c := re.search(r'generic \[ref=[^\]]+\]: (\d+[hdmw] ago|\d{4}-\d+-\d+|\d+-\d+)$', s):
                date = c.group(1)
                break
        mult = 1000 if count.endswith("K") else 1_000_000 if count.endswith("M") else 1
        likes = float(count.rstrip("KM") or 0) * mult
        fresh = bool(re.match(r"\d+[hdw] ago$", date))
        out.append({"author": m.group(1), "id": m.group(2), "likes": likes, "shown": count, "date": date,
                    "fresh": fresh, "caption": cap})
    return out


def show_cards(path: str, n: int = 25) -> None:
    for c in sorted(cards(path), key=lambda c: -c["likes"])[:n]:
        print(f'{c["shown"]:>6} | {c["date"]:>10} | @{c["author"]} | {c["caption"][:110]}')


def show_tags(paths: list[str], n: int = 20) -> None:
    tags: dict[str, list] = collections.defaultdict(lambda: [0, 0, 0.0])
    total = 0
    for p in paths:
        for c in cards(p):
            total += 1
            for t in {t.rstrip(".,!?") for t in re.findall(r"#[^\s#]+", c["caption"])}:
                tags[t][0] += 1
                tags[t][1] += c["fresh"] or bool(re.match(r"^\d{1,2}-\d+$", c["date"]))
                tags[t][2] += c["likes"]
    print(f"{total} posts")
    for t, (posts, season, likes) in sorted(tags.items(), key=lambda kv: -kv[1][2])[:n]:
        print(f"   {t:36s} posts {posts:3d}  this season {season:3d}  likes {likes / 1000:8.1f}K")


if __name__ == "__main__":
    if sys.argv[1] == "cards":
        show_cards(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 25)
    elif sys.argv[1] == "tags":
        show_tags(sys.argv[2:])

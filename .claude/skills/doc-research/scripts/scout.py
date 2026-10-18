#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["ddgs>=9", "trafilatura>=2", "httpx", "pypdf", "yt-dlp"]
# ///
"""Search, fetch and grep web sources for doc-research without filling an agent's context.

Pages are saved as text under <plan>/sources/ (git-ignored). Every command prints one short line per
result; an agent reads only the paragraphs it asks for with `find`, never a whole page.

  scout.py search --plan docs/video-plan-05 "query one" "query two" [--news] [-n 8]
  scout.py fetch  --plan docs/video-plan-05 <id or url> ...
  scout.py find   --plan docs/video-plan-05 "word" "other word" [--all] [--ids a1b2c3,d4e5f6]
  scout.py list   --plan docs/video-plan-05

An id is the first 6 hex digits of the URL's SHA-1, so parallel agents share one cache without clashing.
Saved pages are <plan>/sources/<id>-<slug>.txt; open one with Read only when `find` isn't enough.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import io
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
MIN_CHARS = 400  # less text than this after extraction means a blocked page or a cookie wall
UNFETCHABLE = ("facebook.com", "fb.watch", "tiktok.com", "instagram.com", "threads.net")
TRACKING = re.compile(r"^(utm_|fbclid|gclid|mc_|ref_src|igshid)")

_client = httpx.Client(follow_redirects=True, timeout=25, headers={"User-Agent": UA, "Accept-Language": "en,km;q=0.8"})
_host_locks: dict[str, threading.Semaphore] = {}
_host_locks_guard = threading.Lock()


@dataclass
class Page:
    title: str
    text: str
    site: str = ""
    author: str = ""
    date: str = ""
    via: str = ""
    note: str = ""


class Skip(Exception):
    """A URL that can't be fetched; the message says what to do instead."""


# ---------- ids and storage ----------

def normalize(url: str) -> str:
    parts = urlsplit(url.strip())
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not TRACKING.match(k)])
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, query, ""))


def uid(url: str) -> str:
    return hashlib.sha1(normalize(url).encode()).hexdigest()[:6]


def host(url: str) -> str:
    return urlsplit(url).netloc.lower().removeprefix("www.")


def sources_dir(plan: str) -> Path:
    src = Path(plan) / "sources"
    src.mkdir(parents=True, exist_ok=True)
    ignore = src / ".gitignore"
    if not ignore.exists():
        ignore.write_text("# Cached copies of web pages: research material, not ours to publish.\n*\n")
    return src


def append_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def saved_page(src: Path, page_id: str) -> Path | None:
    return next(iter(src.glob(f"{page_id}-*.txt")), None)


def slugify(title: str, url: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40].strip("-")
    return slug or re.sub(r"[^a-z0-9]+", "-", host(url)).strip("-")


def read_header(path: Path) -> dict:
    head, _, _ = path.read_text(encoding="utf-8").partition("\n---\n")
    lines = head.splitlines()
    meta = {"title": lines[0].removeprefix("# ") if lines else ""}
    for line in lines[1:]:
        key, _, value = line.partition(": ")
        meta[key] = value
    return meta


def save(src: Path, url: str, page: Page) -> Path:
    path = src / f"{uid(url)}-{slugify(page.title, url)}.txt"
    header = [f"# {page.title or url}", f"url: {url}"]
    header += [f"{k}: {v}" for k, v in (("via", page.via), ("site", page.site), ("author", page.author),
                                         ("date", page.date), ("note", page.note)) if v]
    header += [f"fetched: {date.today().isoformat()}", f"chars: {len(page.text)}"]
    tmp = path.with_suffix(".tmp")
    tmp.write_text("\n".join(header) + "\n---\n" + page.text.strip() + "\n", encoding="utf-8")
    tmp.replace(path)
    for stale in src.glob(f"{uid(url)}-*.txt"):  # a refetch can change the title, and so the file name
        if stale != path:
            stale.unlink()
    return path


# ---------- fetching ----------

def get(url: str) -> httpx.Response:
    with _host_locks_guard:
        lock = _host_locks.setdefault(host(url), threading.Semaphore(2))
    with lock:
        for wait in (0, 10, 30):
            time.sleep(wait)
            resp = _client.get(url)
            if resp.status_code != 429:
                return resp
        return resp


def extract_html(content: bytes, url: str) -> Page:
    import trafilatura

    doc = trafilatura.bare_extraction(content, url=url, with_metadata=True, include_comments=False,
                                      include_tables=True, favor_recall=True,
                                      date_extraction_params={"original_date": True, "extensive_search": True})
    if not doc or not doc.text:
        return Page(title="", text="")
    return Page(title=doc.title or "", text=doc.text, site=doc.sitename or "", author=doc.author or "",
                date=doc.date or "")


def extract_pdf(content: bytes) -> Page:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    pages = [f"[p. {i}] {(p.extract_text() or '').strip()}" for i, p in enumerate(reader.pages, 1)]
    first_line = next((line for line in pages[0].removeprefix("[p. 1] ").splitlines() if line.strip()), "") if pages else ""
    title = (reader.metadata.title if reader.metadata else None) or first_line[:120]
    return Page(title=title, text="\n".join(pages), note="PDF; [p. N] marks page numbers")


def fetch_generic(url: str) -> Page:
    resp = get(url)
    page = Page(title="", text="")
    if resp.status_code < 400:
        is_pdf = "pdf" in resp.headers.get("content-type", "") or resp.content[:5] == b"%PDF-"
        page = extract_pdf(resp.content) if is_pdf else extract_html(resp.content, str(resp.url))
    if len(page.text) >= MIN_CHARS:
        return page
    # Blocked, paywalled or a cookie wall: the Wayback raw view usually has the full page. The newest
    # snapshot can itself be a bot-check page, so step back through older ones.
    status = resp.status_code
    for year in (date.today().year, date.today().year - 2, 2019):
        archived = get(f"https://web.archive.org/web/{year}id_/{url}")
        if archived.status_code >= 400:
            continue
        old = extract_html(archived.content, url)
        if len(old.text) >= MIN_CHARS and len(old.text) > len(page.text):
            old.via = str(archived.url)
            return old
    if page.text:
        page.note = "short page; may be blocked or a stub"
        return page
    raise Skip(f"HTTP {status}, no usable archived copy; try WebFetch")


def fetch_x(url: str) -> Page:
    path = [p for p in urlsplit(url).path.split("/") if p]
    api = "https://api.fxtwitter.com/" + "/".join(path[:3] if len(path) >= 3 and path[1] == "status" else path[:1])
    data = get(api).json()
    if "tweet" in data:
        t = data["tweet"]
        text = t.get("text", "")
        if article := t.get("article"):
            text += "\n\n" + "\n".join(b.get("text", "") for b in article.get("content", {}).get("blocks", []))
        stats = f"views {t.get('views')}, likes {t.get('likes')}, reposts {t.get('retweets')}"
        author = t.get("author", {})
        posted = t.get("created_timestamp")
        return Page(title=f"{author.get('name')} on X", text=f"{text}\n\n({stats})", site="X",
                    author=f"{author.get('name')} (@{author.get('screen_name')})",
                    date=date.fromtimestamp(posted).isoformat() if posted else "", via=api)
    if "user" in data:
        u = data["user"]
        return Page(title=f"{u.get('name')} (@{u.get('screen_name')}) profile", site="X",
                    text=f"{u.get('description', '')}\n\nfollowers {u.get('followers')}, joined {u.get('joined')}",
                    via=api)
    raise Skip("fxtwitter returned nothing; the post may be deleted or private")


def fetch_github(url: str) -> Page:
    path = [p for p in urlsplit(url).path.split("/") if p]
    if len(path) >= 5 and path[2] == "blob":
        raw = f"https://raw.githubusercontent.com/{path[0]}/{path[1]}/{'/'.join(path[3:])}"
    elif len(path) == 2:
        raw = f"https://raw.githubusercontent.com/{path[0]}/{path[1]}/HEAD/README.md"
    else:
        return fetch_generic(url)
    resp = get(raw)
    if resp.status_code >= 400:
        return fetch_generic(url)
    return Page(title=f"{path[0]}/{path[1]}: {path[-1] if len(path) > 2 else 'README'}", text=resp.text,
                site="GitHub", via=raw, note="commit history gives the first-published date")


def fetch_youtube(url: str) -> Page:
    import yt_dlp

    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    manual, auto = info.get("subtitles") or {}, info.get("automatic_captions") or {}
    orig = [k for k in auto if k.endswith("-orig")]
    choices = [(manual, k, False) for k in manual if k.startswith("en")] + [(manual, k, False) for k in manual]
    choices += [(auto, k, True) for k in orig] + [(auto, k, True) for k in auto if k == "en"]
    upload = info.get("upload_date") or ""
    page = Page(title=info.get("title", ""), text=info.get("description", ""), site="YouTube",
                author=info.get("channel") or info.get("uploader") or "",
                date=f"{upload[:4]}-{upload[4:6]}-{upload[6:]}" if upload else "")
    for tracks, lang, is_auto in choices:
        fmt = next((f for f in tracks[lang] if f.get("ext") == "json3"), None)
        if not fmt:
            continue
        events = get(fmt["url"]).json().get("events", [])
        lines, bucket, start = [], [], 0
        for ev in events:
            words = "".join(s.get("utf8", "") for s in ev.get("segs", [])).replace("\n", " ").strip()
            if not words:
                continue
            ms = ev.get("tStartMs", 0)
            if bucket and ms - start > 30_000:
                lines.append(f"[{start // 60000}:{start // 1000 % 60:02d}] " + " ".join(bucket))
                bucket, start = [], ms
            if not bucket:
                start = ms
            bucket.append(words)
        if bucket:
            lines.append(f"[{start // 60000}:{start // 1000 % 60:02d}] " + " ".join(bucket))
        page.text = f"Description: {page.text}\n\nTranscript ({lang}):\n" + "\n".join(lines)
        page.note = "auto-captions; check quotes against audio" if is_auto else f"captions ({lang})"
        return page
    page.note = "no captions; description only"
    return page


def fetch_one(src: Path, url: str, force: bool) -> str:
    page_id = uid(url)
    if (old := saved_page(src, page_id)) and not force:
        meta = read_header(old)
        return f"{page_id}  cached  {meta.get('chars', '?'):>7} ch  {meta.get('date', '')[:10]:10}  {meta['title'][:70]}"
    h = host(url)
    try:
        if any(h == d or h.endswith("." + d) for d in UNFETCHABLE):
            raise Skip("not fetchable; search around it for the same story")
        if h in ("x.com", "twitter.com", "mobile.twitter.com"):
            page = fetch_x(url)
        elif h == "github.com":
            page = fetch_github(url)
        elif h in ("youtube.com", "m.youtube.com", "youtu.be"):
            page = fetch_youtube(url)
        else:
            page = fetch_generic(url)
    except Skip as e:
        return f"{page_id}  SKIP  {h}  {e}"
    except Exception as e:  # one bad page must not stop the batch
        return f"{page_id}  FAIL  {h}  {type(e).__name__}: {str(e)[:120]}"
    save(src, url, page)
    flag = f"  [{page.note}]" if page.note else ""
    via = "  (via Wayback)" if "web.archive.org" in page.via else ""
    return f"{page_id}  {len(page.text):>7} ch  {page.date[:10]:10}  {h}  {page.title[:70]}{via}{flag}"


# ---------- commands ----------

def cmd_search(args: argparse.Namespace) -> None:
    from ddgs import DDGS

    src = sources_dir(args.plan)
    fetched = {p.name[:6] for p in src.glob("*.txt")}
    shown: set[str] = set()
    ddgs = DDGS()
    for query in args.queries:
        try:
            rows = (ddgs.news(query, max_results=args.n, region=args.region) if args.news
                    else ddgs.text(query, max_results=args.n, region=args.region))
        except Exception as e:
            print(f'## {query}\n  ! {str(e)[:120]}')
            continue
        print(f"## {query}")
        records = []
        for r in rows:
            url = r.get("href") or r.get("url") or ""
            if not url:
                continue
            rid = uid(url)
            records.append({"id": rid, "url": url, "title": r.get("title", ""), "snippet": r.get("body", ""),
                            "date": r.get("date", ""), "source": r.get("source", ""), "query": query})
            if rid in shown:
                continue
            shown.add(rid)
            mark = "*" if rid in fetched else " "
            when = f"{r['date'][:10]}  " if r.get("date") else ""
            snippet = re.sub(r"\s+", " ", r.get("body", ""))[: args.snippet]
            print(f" {mark}{rid}  {host(url)}  {when}{r.get('title', '')[:80]} | {snippet}")
        append_jsonl(src / "search.jsonl", records)
        time.sleep(1)  # DuckDuckGo throttles bursts
    print("(* = already fetched)")


def cmd_fetch(args: argparse.Namespace) -> None:
    src = sources_dir(args.plan)
    known = {r["id"]: r["url"] for r in read_jsonl(src / "search.jsonl")}
    urls = []
    for target in args.targets:
        if target.startswith("http"):
            urls.append(target)
        elif target in known:
            urls.append(known[target])
        else:
            print(f"{target}  FAIL  unknown id; pass the URL instead")
    # Import the extractors here: importing them from several threads at once aborts the process.
    import pypdf, trafilatura  # noqa: F401
    if any(host(u) in ("youtube.com", "m.youtube.com", "youtu.be") for u in urls):
        import yt_dlp  # noqa: F401
    with ThreadPoolExecutor(max_workers=6) as pool:
        for line in pool.map(lambda u: fetch_one(src, u, args.force), urls):
            print(line)


def trim(paragraph: str, terms: list[str], width: int) -> str:
    if len(paragraph) <= width:
        return paragraph
    low = paragraph.lower()
    pos = min((low.find(t) for t in terms if t in low), default=0)
    start = max(0, pos - width // 3)
    return ("…" if start else "") + paragraph[start:start + width] + "…"


def cmd_find(args: argparse.Namespace) -> None:
    src = sources_dir(args.plan)
    terms = [t.lower() for t in args.terms]
    wanted = set(args.ids.split(",")) if args.ids else None
    results = []
    for path in sorted(src.glob("*.txt")):
        if wanted and path.name[:6] not in wanted:
            continue
        _, _, body = path.read_text(encoding="utf-8").partition("\n---\n")
        paragraphs = [p.strip() for p in body.splitlines() if p.strip()]
        match = all if args.all else any
        hits = [i for i, p in enumerate(paragraphs) if match(t in p.lower() for t in terms)]
        if hits:
            results.append((len(hits), path, paragraphs, hits))
    results.sort(key=lambda r: -r[0])
    total = 0
    for shown_pages, (count, path, paragraphs, hits) in enumerate(results):
        if total >= args.limit:
            print(f"… {len(results) - shown_pages} more pages match; narrow the terms, add --all or --ids")
            break
        meta = read_header(path)
        print(f"== {path.name[:6]}  {meta.get('date', '')[:10]}  {meta['title'][:70]}  ({count} hits)")
        used, last, budget = 0, -1, min(args.per_page, args.limit - total)
        for i in hits:
            for j in range(max(i - args.context, last + 1), min(i + args.context + 1, len(paragraphs))):
                if used >= budget:
                    break
                line = trim(paragraphs[j], terms, min(args.width, budget - used))
                print(f"  {line}")
                used += len(line)
                last = j
        total += used
    if not results:
        print("no matches")


def cmd_list(args: argparse.Namespace) -> None:
    src = sources_dir(args.plan)
    pages = sorted(src.glob("*.txt"))
    for path in pages:
        meta = read_header(path)
        print(f"{path.name[:6]}  {meta.get('chars', '?'):>7} ch  {meta.get('date', '')[:10]:10}  "
              f"{host(meta.get('url', ''))}  {meta['title'][:70]}")
    print(f"{len(pages)} pages, {len(read_jsonl(src / 'search.jsonl'))} search results in {src}")


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--plan", required=True, help="the documentary folder, e.g. docs/video-plan-05")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", parents=[common], help="run several web searches in one call")
    s.add_argument("queries", nargs="+")
    s.add_argument("-n", type=int, default=8, help="results per query")
    s.add_argument("--news", action="store_true", help="news search; results carry a date")
    s.add_argument("--region", default="us-en", help="DuckDuckGo region, e.g. us-en, uk-en, th-th, vn-vi")
    s.add_argument("--snippet", type=int, default=160, help="snippet characters per result")
    s.set_defaults(func=cmd_search)

    f = sub.add_parser("fetch", parents=[common], help="save pages as text; prints one line each")
    f.add_argument("targets", nargs="+", help="search-result ids or URLs")
    f.add_argument("--force", action="store_true", help="fetch again even if cached")
    f.set_defaults(func=cmd_fetch)

    g = sub.add_parser("find", parents=[common], help="print only the paragraphs that match")
    g.add_argument("terms", nargs="+")
    g.add_argument("--all", action="store_true", help="a paragraph must contain every term")
    g.add_argument("--ids", help="comma-separated page ids to search")
    g.add_argument("--context", type=int, default=0, help="paragraphs to show around each hit")
    g.add_argument("--width", type=int, default=500, help="max characters per paragraph")
    g.add_argument("--per-page", type=int, default=1500, help="max characters per page")
    g.add_argument("--limit", type=int, default=6000, help="max characters in total")
    g.set_defaults(func=cmd_find)

    ls = sub.add_parser("list", parents=[common], help="list saved pages")
    ls.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build the /speaking/ section of imransiddique.com.

Reads speaking/speaking.json, writes speaking/index.html, and refreshes the
/speaking/ entry in the root sitemap.xml.

    python speaking/build.py            # build
    python speaking/build.py --check    # validate and report, write nothing

speaking.json is the single source of truth. To add a talk, add one object and
re-run this. Nothing else needs editing.

Record format:

    {
      "date": "2026-06-23",              # required, YYYY-MM-DD, the DELIVERY date,
                                         #   not the date a recording was uploaded
      "title": "Talk title",             # required
      "event": "Conference name",        # required
      "location": "San Francisco, CA",   # required, or "Online"
      "format": "Breakout session",      # required, e.g. Keynote / Panel / Webinar
      "status": "delivered",             # required: delivered | scheduled | submitted
      "summary": "One or two sentences", # required in the data, NOT shown on the page
      "url": "https://...",              # optional, the event or session page
      "recording": "https://...",        # optional, a YouTube link gives the card art
      "tags": ["confidential-computing"] # optional, not shown on the page
    }

`status` matters, and it controls publication.

    delivered  published, and counts as a prior talk when a CFP asks for history
    scheduled  published; accepted or self-hosted, confirmed but not yet given
    submitted  NOT PUBLISHED. Tracked here only, hidden from the page entirely.

A submitted talk is a pending CFP entry, not a credential and not news. It stays in
this file so there is one record of what is outstanding, and it appears on the site
only once its status changes to `scheduled`.

`summary`, `format` and `tags` are deliberately kept in the data but kept off the
page. The page is a shop window, not an archive: date, place, title, event, and a
way to watch. The long form belongs to whoever reads the JSON, or to the recording.

Card art comes free from any YouTube recording link, via img.youtube.com. Talks
with no recording get a typographic panel instead, so the grid stays even.

Deliberately dependency-free, matching notes/build.py: this runs on a bare Python 3
with no pip install.
"""

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "speaking"
DATA = HERE / "speaking.json"
VIDEOS = HERE / "videos.json"
OUT = HERE / "index.html"
SITEMAP = ROOT / "sitemap.xml"
CSS_VERSION = "b7c31d2"

REQUIRED = ("date", "title", "event", "location", "format", "status", "summary")
VALID_STATUS = {"delivered", "scheduled", "submitted"}

YT = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})")


def load():
    records = json.loads(DATA.read_text(encoding="utf-8"))
    problems = []
    for i, r in enumerate(records):
        where = f"record {i} ({r.get('title', 'untitled')!r})"
        for field in REQUIRED:
            if not r.get(field):
                problems.append(f"{where}: missing required field {field!r}")
        if r.get("status") not in VALID_STATUS:
            problems.append(
                f"{where}: status {r.get('status')!r} not one of {sorted(VALID_STATUS)}"
            )
        try:
            datetime.strptime(r["date"], "%Y-%m-%d")
        except (KeyError, ValueError):
            problems.append(f"{where}: date must be YYYY-MM-DD")
    records.sort(key=lambda r: r.get("date", ""), reverse=True)
    return records, problems


def load_videos():
    """Proof videos. A separate series from talks, so a separate file."""
    if not VIDEOS.exists():
        return []
    vids = json.loads(VIDEOS.read_text(encoding="utf-8"))
    vids.sort(key=lambda v: v.get("date", ""), reverse=True)
    return vids


def fmt_date(iso, short=False):
    d = datetime.strptime(iso, "%Y-%m-%d")
    if short:
        return d.strftime("%b %Y")
    return d.strftime("%#d %b %Y" if sys.platform == "win32" else "%-d %b %Y")


def esc(s):
    return html.escape(s or "", quote=True)


def video_id(url):
    m = YT.search(url or "")
    return m.group(1) if m else None


def render_delivered(r):
    """A card. Thumbnail if there is a video, typographic panel if not."""
    vid = video_id(r.get("recording"))
    href = r.get("recording") or r.get("url") or ""
    tag = "a" if href else "div"
    attrs = (
        f' href="{esc(href)}" target="_blank" rel="noopener noreferrer"' if href else ""
    )

    if vid:
        art = (
            f'<div class="talk-thumb">'
            f'<img src="https://img.youtube.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">'
            f'<span class="talk-play" aria-hidden="true">&#9654;</span></div>'
        )
    else:
        art = (
            f'<div class="talk-thumb talk-thumb-plain">'
            f'<span>{esc(fmt_date(r["date"], short=True))}</span></div>'
        )

    return f"""                <{tag} class="talk-card"{attrs}>
                    {art}
                    <div class="talk-body">
                        <p class="talk-meta">{esc(fmt_date(r["date"]))} &middot; {esc(r["location"])}</p>
                        <h3>{esc(r["title"])}</h3>
                        <p class="talk-event">{esc(r["event"])}</p>
                    </div>
                </{tag}>"""


def render_video(v):
    """A proof-video card. Local art if given, else the YouTube thumbnail."""
    thumb = v.get("thumb") or ""
    if not thumb:
        vid = video_id(v.get("url"))
        thumb = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg" if vid else ""
    cls = "talk-thumb proof-video-short" if v.get("short") else "talk-thumb"
    badge = '<span class="proof-video-badge">Short</span>' if v.get("short") else ""
    return f"""                <a class="talk-card" href="{esc(v["url"])}" target="_blank" rel="noopener noreferrer">
                    <div class="{cls}"><img src="{esc(thumb)}" alt="" loading="lazy"><span class="talk-play" aria-hidden="true">&#9654;</span>{badge}</div>
                    <div class="talk-body">
                        <p class="talk-meta">{esc(fmt_date(v["date"]))} &middot; Proof video {esc(v["number"])}</p>
                        <h3>{v["title"]}</h3>
                        <p class="talk-event">{esc(v["subtitle"])}</p>
                    </div>
                </a>"""


def render_upcoming(r):
    """A compact row. No art, because there is nothing to watch yet."""
    href = r.get("url") or ""
    title = esc(r["title"])
    if href:
        title = (
            f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer">{title}</a>'
        )
    return f"""                <li class="talk-row">
                    <span class="talk-row-date">{esc(fmt_date(r["date"]))}</span>
                    <span class="talk-row-main"><strong>{title}</strong><span>{esc(r["event"])} &middot; {esc(r["location"])}</span></span>
                </li>"""


def render(records, videos=(), _stale_out=None):
    today = datetime.now().strftime("%Y-%m-%d")
    delivered = [r for r in records if r["status"] == "delivered"]
    # Upcoming is date-gated, not status-gated. A scheduled talk whose date has
    # passed used to sit under "Coming up" until somebody hand-edited the JSON.
    # "submitted" stays withheld. A submission is not a booking, and listing one
    # would advertise a talk that may never happen.
    upcoming = [
        r for r in records if r["status"] == "scheduled" and r["date"] >= today
    ]
    upcoming.sort(key=lambda r: r["date"])
    stale = [
        r
        for r in records
        if r["status"] in ("scheduled", "submitted") and r["date"] < today
    ]
    if _stale_out is not None:
        _stale_out.extend(stale)

    upcoming_section = ""
    if upcoming:
        rows = "\n".join(render_upcoming(r) for r in upcoming)
        upcoming_section = f"""
        <section class="talk-section">
            <div class="container">
                <h2 class="talk-h2">Coming up</h2>
                <ul class="talk-rows">
{rows}
                </ul>
            </div>
        </section>
"""

    videos_section = ""
    if videos:
        cards = "\n\n".join(render_video(v) for v in videos)
        videos_section = f"""
        <section class="talk-section proof-video-section" aria-labelledby="proof-videos-heading">
            <div class="container">
                <div class="talk-head proof-video-head">
                    <div>
                        <h2 class="talk-h2" id="proof-videos-heading">Proof videos</h2>
                        <p class="proof-video-intro">Short, evidence-led demonstrations of what trustworthy AI systems can actually prove.</p>
                    </div>
                    <a class="proof-video-channel" href="https://www.youtube.com/@imransiddiqueai" target="_blank" rel="noopener noreferrer">View all on YouTube <span aria-hidden="true">&rarr;</span></a>
                </div>
                <div class="talk-grid">
{cards}
                </div>
            </div>
        </section>
"""

    delivered_section = ""
    if delivered:
        cards = "\n\n".join(render_delivered(r) for r in delivered)
        watchable = sum(1 for r in delivered if video_id(r.get("recording")))
        note = (
            f'<p class="talk-note">{watchable} of {len(delivered)} recorded</p>'
            if watchable
            else ""
        )
        delivered_section = f"""
        <section class="talk-section">
            <div class="container">
                <div class="talk-head"><h2 class="talk-h2">Past talks</h2>{note}</div>
                <div class="talk-grid">
{cards}
                </div>
            </div>
        </section>
"""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speaking | Imran Siddique</title>
    <meta name="description" content="Talks by Imran Siddique on AI agent governance, confidential computing, and verifiable evidence. Conference sessions, summits and community talks, most with recordings.">
    <link rel="canonical" href="https://imransiddique.com/speaking/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏛️</text></svg>">
    <link rel="stylesheet" href="/styles-new.css?v={CSS_VERSION}">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="/index.html" class="logo">Imran Siddique</a>
            <ul class="nav-links">
                <li><a href="/index.html">Home</a></li>
                <li><a href="/about.html">About</a></li>
                <li><a href="/projects.html">Projects</a></li>
                <li><a href="/notes/index.html">Writing</a></li>
                <li><a href="/speaking/" class="active">Speaking</a></li>
                <li><a href="/contact.html">Contact</a></li>
            </ul>
        </div>
    </nav>

    <main>
        <section class="hero-small talk-hero">
            <div class="container">
                <h1>Speaking</h1>
                <p class="hero-subtitle">Agent governance, confidential computing, and what a system can actually prove.</p>
            </div>
        </section>
{upcoming_section}{videos_section}{delivered_section}
    </main>
</body>
</html>
"""


def update_sitemap(check):
    if not SITEMAP.exists():
        return "sitemap.xml not found, skipped"
    s = SITEMAP.read_text(encoding="utf-8")
    loc = "https://imransiddique.com/speaking/"
    if loc in s:
        return "sitemap already lists /speaking/"
    entry = (
        f"  <url>\n    <loc>{loc}</loc>\n"
        f"    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
    )
    if "</urlset>" not in s:
        return "sitemap has no </urlset>, skipped"
    if not check:
        SITEMAP.write_text(s.replace("</urlset>", entry + "</urlset>"), encoding="utf-8")
    return "added /speaking/ to sitemap"


def main():
    check = "--check" in sys.argv
    records, problems = load()
    if problems:
        for p in problems:
            print(f"PROBLEM: {p}")
        return 1
    counts = {}
    for r in records:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    videos = load_videos()
    stale = []
    out = render(records, videos, _stale_out=stale)
    hidden = counts.get("submitted", 0)
    published = len(records) - hidden
    art = sum(
        1
        for r in records
        if r["status"] == "delivered" and video_id(r.get("recording"))
    )
    if check:
        print(f"OK: {published} would be published, {hidden} withheld, {art} with card art")
    else:
        OUT.write_text(out, encoding="utf-8")
        print(
            f"wrote {OUT.relative_to(ROOT)}: {published} published, "
            f"{hidden} withheld, {art} with card art"
        )
    print(f"  {len(videos)} proof videos")
    for r in stale:
        print(
            f"  STALE: {r['date']} {r['title'][:48]!r} is still {r['status']} "
            f"but the date has passed. Set it to delivered, or move the date."
        )
    print("  " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    print("  " + update_sitemap(check))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

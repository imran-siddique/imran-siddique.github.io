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
      "date": "2026-06-23",              # required, YYYY-MM-DD, the delivery date
      "title": "Talk title",             # required
      "event": "Conference name",        # required
      "location": "San Francisco, CA",   # required, or "Online"
      "format": "Breakout session",      # required, e.g. Keynote / Panel / Webinar
      "status": "delivered",             # required: delivered | scheduled | submitted
      "summary": "One or two sentences", # required
      "url": "https://...",              # optional, the event or session page
      "recording": "https://...",        # optional, video or audio
      "tags": ["confidential-computing"] # optional
    }

Keep it ordered newest first; the build sorts anyway, so appending anywhere is fine.

`status` matters. Only `delivered` counts as a prior talk when a CFP asks for
speaking history. `submitted` means it has not been accepted yet and must never be
presented as a credential.

Deliberately dependency-free, matching notes/build.py: this runs on a bare Python 3
with no pip install.
"""

import html
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "speaking"
DATA = HERE / "speaking.json"
OUT = HERE / "index.html"
SITEMAP = ROOT / "sitemap.xml"

REQUIRED = ("date", "title", "event", "location", "format", "status", "summary")
VALID_STATUS = {"delivered", "scheduled", "submitted"}

STATUS_LABEL = {
    "delivered": "Delivered",
    "scheduled": "Scheduled",
    "submitted": "Submitted",
}


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


def fmt_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%-d %B %Y") if sys.platform != "win32" else d.strftime("%#d %B %Y")


def esc(s):
    return html.escape(s or "", quote=True)


def render_entry(r):
    links = []
    if r.get("url"):
        links.append(
            f'<a href="{esc(r["url"])}" target="_blank" rel="noopener noreferrer">Event page →</a>'
        )
    if r.get("recording"):
        links.append(
            f'<a href="{esc(r["recording"])}" target="_blank" rel="noopener noreferrer">Recording →</a>'
        )
    links_html = (
        f'\n                        <div class="project-links">{" ".join(links)}</div>'
        if links
        else ""
    )
    tags = "".join(
        f'<span class="tech-badge">{esc(t)}</span>' for t in r.get("tags", [])
    )
    tags_html = (
        f'\n                        <div class="project-tech">{tags}</div>' if tags else ""
    )
    return f"""                    <article class="project-card">
                        <div class="project-header">
                            <div class="project-stars">{esc(STATUS_LABEL[r["status"]])}</div>
                        </div>
                        <p class="talk-meta">{esc(fmt_date(r["date"]))} · {esc(r["event"])} · {esc(r["location"])} · {esc(r["format"])}</p>
                        <h3>{esc(r["title"])}</h3>
                        <p class="project-description">{esc(r["summary"])}</p>{tags_html}{links_html}
                    </article>"""


def render(records):
    delivered = [r for r in records if r["status"] == "delivered"]
    upcoming = [r for r in records if r["status"] in ("scheduled", "submitted")]

    def block(items):
        return "\n\n".join(render_entry(r) for r in items)

    upcoming_section = ""
    if upcoming:
        upcoming_section = f"""
        <section class="section">
            <div class="container">
                <h2>Upcoming</h2>
                <p class="section-intro">Submitted talks are listed as submitted until they are accepted. They are not speaking credentials.</p>
                <div class="projects-grid">
{block(upcoming)}
                </div>
            </div>
        </section>
"""

    delivered_section = ""
    if delivered:
        delivered_section = f"""
        <section class="section">
            <div class="container">
                <h2>Delivered</h2>
                <div class="projects-grid">
{block(delivered)}
                </div>
            </div>
        </section>
"""

    built = datetime.now().strftime("%Y-%m-%d")
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speaking | Imran Siddique</title>
    <meta name="description" content="Talks and conference sessions by Imran Siddique on AI agent governance, confidential computing, verifiable evidence, and supply-chain provenance.">
    <link rel="canonical" href="https://imransiddique.com/speaking/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏛️</text></svg>">
    <link rel="stylesheet" href="/styles-new.css?v=a8a4c5f">
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
        <section class="hero-small">
            <div class="container">
                <h1>Speaking</h1>
                <p class="hero-subtitle">Conference sessions, summits, and webinars on agent governance, confidential computing, and verifiable evidence.</p>
            </div>
        </section>
{upcoming_section}{delivered_section}
        <section class="section">
            <div class="container">
                <p class="section-intro">For speaker enquiries, see <a href="/contact.html">contact</a>. Last built {built}.</p>
            </div>
        </section>
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
    out = render(records)
    counts = {}
    for r in records:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    if check:
        print(f"OK: {len(records)} talks, would write {OUT.relative_to(ROOT)}")
    else:
        OUT.write_text(out, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    print("  " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    print("  " + update_sitemap(check))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

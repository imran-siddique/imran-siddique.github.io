#!/usr/bin/env python3
"""Build the /notes/ section of imransiddique.com.

Reads every note in notes/src/*.md, writes one HTML page per note, rebuilds
notes/index.html and notes/feed.xml, and refreshes the /notes/ entries in the
root sitemap.xml.

    python notes/build.py            # build
    python notes/build.py --check    # build into memory, report problems, write nothing

Note source format, notes/src/YYYY-MM-DD-slug.md:

    ---
    title: You cannot redact a field you cannot read
    date: 2026-08-14
    standfirst: One sentence that says what the note found.
    tags: [agent-security, evidence]
    linkedin: https://www.linkedin.com/feed/update/urn:li:activity:123/
    sources:
      - label: arXiv 2608.09867, the paper
        url: https://arxiv.org/abs/2608.09867
    ---

    Body in markdown.

`linkedin` is optional and only set once a note has been posted to the feed.
`sources` is not optional. A note with no source it was checked against does
not belong here.

Deliberately dependency-free: this runs on a bare Python 3 with no pip install,
because a publishing path that can break on a missing package is a publishing
path that will break at 6am.
"""

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "notes"
SRC = NOTES / "src"
SITE = "https://imransiddique.com"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# ---------------------------------------------------------------- frontmatter

def parse_front_matter(text, path):
    """Tolerant subset of YAML: scalars, [a, b] lists, and a sources: block."""
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: no front matter block")
    _, fm, body = text.split("---", 2)
    meta = {"sources": [], "tags": []}
    lines = fm.strip("\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if line.startswith("sources:"):
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("-")):
                m = re.match(r"\s*-\s*label:\s*(.+)", lines[i])
                if m:
                    entry = {"label": m.group(1).strip(), "url": ""}
                    if i + 1 < len(lines):
                        u = re.match(r"\s*url:\s*(.+)", lines[i + 1])
                        if u:
                            entry["url"] = u.group(1).strip()
                            i += 1
                    meta["sources"].append(entry)
                i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            meta[key] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[key] = value
        i += 1
    return meta, body.strip("\n")


# ------------------------------------------------------------------ markdown

def inline(text):
    """Inline markdown. Escapes first, so note bodies cannot inject markup."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  r'<a href="\2" rel="noopener">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", text)
    return text


def render(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        start = i          # every branch below must advance the cursor; a branch
        line = lines[i]    # that forgets would otherwise spin here forever
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            i += 1
            block = []
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(block) + "</code></pre>")
        elif re.match(r"#{2,4} ", line):
            level = len(line) - len(line.lstrip("#"))
            out.append(f"<h{level}>{inline(line[level:].strip())}</h{level}>")
            i += 1
        elif line.startswith("> "):
            block = []
            while i < len(lines) and lines[i].startswith("> "):
                block.append(inline(lines[i][2:]))
                i += 1
            out.append("<blockquote><p>" + " ".join(block) + "</p></blockquote>")
        elif re.match(r"[-*] ", line):
            block = []
            while i < len(lines) and re.match(r"[-*] ", lines[i]):
                block.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(block) + "</ul>")
        elif line.strip() == "---":
            out.append("<hr>")
            i += 1
        else:
            block = []
            while i < len(lines) and lines[i].strip() and not re.match(r"([-*>#]|```)", lines[i]):
                block.append(inline(lines[i]))
                i += 1
            out.append("<p>" + " ".join(block) + "</p>")
        if i == start:
            raise RuntimeError(
                f"renderer stalled at line {start + 1}: {lines[start]!r}. "
                f"A branch in render() failed to advance the cursor.")
    return "\n".join(out)


# ------------------------------------------------------------------- chrome

def nav(prefix=""):
    return f"""    <nav class="navbar">
        <div class="container">
            <a href="{prefix}index.html" class="logo">Imran Siddique</a>
            <ul class="nav-links">
                <li><a href="{prefix}index.html">Home</a></li>
                <li><a href="{prefix}about.html">About</a></li>
                <li><a href="{prefix}projects.html">Projects</a></li>
                <li><a href="{prefix}writings.html">Writings</a></li>
                <li><a href="{prefix}notes/index.html" class="active">Notes</a></li>
                <li><a href="{prefix}contact.html">Contact</a></li>
            </ul>
            <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                <svg class="sun-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="5"></circle>
                    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
                </svg>
            </button>
            <div class="hamburger"><span></span><span></span><span></span></div>
        </div>
    </nav>"""


def footer(prefix=""):
    return f"""    <footer class="footer">
        <div class="container">
            <div class="footer-bottom">
                <p>&copy; {datetime.now().year} Imran Siddique.</p>
                <p><a href="{prefix}notes/feed.xml">RSS</a> &middot; <a href="{prefix}index.html">imransiddique.com</a></p>
            </div>
        </div>
    </footer>
    <script src="{prefix}script.js"></script>"""


def head(title, desc, canonical, prefix=""):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{html.escape(desc, quote=True)}">
    <meta name="author" content="Imran Siddique">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{canonical}">
    <link rel="alternate" type="application/rss+xml" title="Notes by Imran Siddique" href="{SITE}/notes/feed.xml">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{html.escape(title, quote=True)}">
    <meta property="og:description" content="{html.escape(desc, quote=True)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:site" content="@mosiddi">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <title>{html.escape(title, quote=True)} | Imran Siddique</title>
    <link rel="stylesheet" href="{prefix}styles-new.css">
    <link rel="stylesheet" href="{prefix}notes/notes.css">
</head>
<body>"""


def pretty(datestr):
    d = datetime.strptime(datestr, "%Y-%m-%d")
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


# --------------------------------------------------------------------- pages

def note_page(n):
    src_items = "".join(
        f'<li><a href="{s["url"]}" rel="noopener">{html.escape(s["label"])}</a></li>'
        if s["url"] else f'<li>{html.escape(s["label"])}</li>'
        for s in n["sources"])
    tags = "".join(f'<span class="concept-tag">{html.escape(t)}</span>' for t in n["tags"])
    posted = ""
    if n.get("linkedin"):
        posted = (f'<p class="note-elsewhere">A shorter version of this note ran on '
                  f'<a href="{n["linkedin"]}" rel="noopener">LinkedIn</a>.</p>')
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": n["title"], "datePublished": n["date"],
        "description": n["standfirst"],
        "author": {"@type": "Person", "name": "Imran Siddique", "url": SITE},
        "mainEntityOfPage": n["url"],
    }, indent=None)
    return f"""{head(n["title"], n["standfirst"], n["url"], prefix="../")}
    <script type="application/ld+json">{ld}</script>
{nav(prefix="../")}
    <main>
        <article class="note">
            <div class="container container-narrow">
                <p class="note-back"><a href="index.html">&larr; All notes</a></p>
                <time class="note-date" datetime="{n["date"]}">{pretty(n["date"])}</time>
                <h1>{html.escape(n["title"])}</h1>
                <p class="note-standfirst">{html.escape(n["standfirst"])}</p>
                <div class="note-tags">{tags}</div>
                <div class="note-body">
{n["html"]}
                </div>
                <section class="note-sources">
                    <h2>Checked against</h2>
                    <ul>{src_items}</ul>
                </section>
                {posted}
            </div>
        </article>
    </main>
{footer(prefix="../")}
</body>
</html>
"""


def index_page(notes):
    cards = []
    for n in notes:
        tags = "".join(f'<span class="concept-tag">{html.escape(t)}</span>' for t in n["tags"])
        cards.append(f"""                    <article class="article-card note-card">
                        <time class="note-date" datetime="{n["date"]}">{pretty(n["date"])}</time>
                        <h3><a href="{n["slug"]}.html">{html.escape(n["title"])}</a></h3>
                        <p class="article-tagline">{html.escape(n["standfirst"])}</p>
                        <div class="article-concepts">{tags}</div>
                    </article>""")
    desc = ("Working notes on agent security, evidence and governance. Each one names "
            "the primary source it was checked against.")
    return f"""{head("Notes", desc, f"{SITE}/notes/", prefix="../")}
{nav(prefix="../")}
    <main>
        <section class="hero-small">
            <div class="container">
                <h1 class="fade-in">Notes</h1>
                <p class="hero-subtitle fade-in">Read the source, then write down what it actually says</p>
            </div>
        </section>
        <section class="content-section">
            <div class="container">
                <div class="writings-intro">
                    <p class="lead">Short working notes on agent security, evidence and governance. Every figure in
                    a note has been read at its primary source, and every note lists what it was checked against.
                    Where the source did not support a claim, the claim is not here.</p>
                    <p class="feed-link"><a href="feed.xml">RSS</a></p>
                </div>
                <div class="articles-grid notes-grid">
{chr(10).join(cards)}
                </div>
            </div>
        </section>
    </main>
{footer(prefix="../")}
</body>
</html>
"""


def feed_body(n):
    """Full article HTML for content:encoded, with the sources list appended.

    `description` alone is not enough. Feed *readers* are happy with a summary, but
    importers treat description as the whole article: dev.to's RSS import produced a
    post containing nothing but the title and the standfirst until this was added.
    """
    srcs = "".join(
        f'<li><a href="{s["url"]}">{html.escape(s["label"])}</a></li>'
        if s["url"] else f'<li>{html.escape(s["label"])}</li>'
        for s in n["sources"])
    return (f'<p><em>{html.escape(n["standfirst"])}</em></p>\n'
            f'{n["html"]}\n'
            f'<h2>Checked against</h2>\n<ul>{srcs}</ul>')


def feed(notes):
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for n in notes[:30]:
        pub = datetime.strptime(n["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0000")
        cats = "".join(f"\n      <category>{html.escape(t)}</category>" for t in n["tags"])
        body = feed_body(n).replace("]]>", "]]]]><![CDATA[>")
        items.append(f"""    <item>
      <title>{html.escape(n["title"])}</title>
      <link>{n["url"]}</link>
      <guid isPermaLink="true">{n["url"]}</guid>
      <pubDate>{pub}</pubDate>{cats}
      <description>{html.escape(n["standfirst"])}</description>
      <content:encoded><![CDATA[{body}]]></content:encoded>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Notes by Imran Siddique</title>
    <link>{SITE}/notes/</link>
    <atom:link href="{SITE}/notes/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Working notes on agent security, evidence and governance.</description>
    <language>en</language>
    <dc:creator>Imran Siddique</dc:creator>
    <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""


def update_sitemap(notes):
    path = ROOT / "sitemap.xml"
    xml = path.read_text(encoding="utf-8")
    xml = re.sub(r"\s*<!-- notes:start -->.*?<!-- notes:end -->", "", xml, flags=re.S)
    block = ["  <!-- notes:start -->",
             f"""  <url>
    <loc>{SITE}/notes/</loc>
    <lastmod>{notes[0]["date"] if notes else datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>"""]
    for n in notes:
        block.append(f"""  <url>
    <loc>{n["url"]}</loc>
    <lastmod>{n["date"]}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.7</priority>
  </url>""")
    block.append("  <!-- notes:end -->")
    xml = xml.replace("</urlset>", "\n".join(block) + "\n</urlset>")
    return path, xml


# ---------------------------------------------------------------------- main

def load():
    notes, problems = [], []
    for path in sorted(SRC.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
        slug = path.stem
        for field in ("title", "date", "standfirst"):
            if not meta.get(field):
                problems.append(f"{path.name}: missing `{field}`")
        if not meta["sources"]:
            problems.append(f"{path.name}: no sources listed. A note with nothing to check "
                            f"against does not belong in /notes/.")
        # dev.to silently truncates tags at 20 characters on RSS import, which is how
        # `confidentialcomputing` became the dead tag `confidentialcomputin` on six
        # Medium cross-posts. Catch it here rather than downstream.
        for tag in meta.get("tags", []):
            if len(tag.replace("-", "")) > 20:
                problems.append(f"{path.name}: tag `{tag}` is longer than 20 characters "
                                f"once hyphens are stripped, so dev.to will truncate it "
                                f"into a tag nobody follows. Shorten it.")
        dashes = "—–"
        scanned = body + meta.get("title", "") + meta.get("standfirst", "")
        if any(d in scanned for d in dashes):
            problems.append(f"{path.name}: contains an em or en dash")
        words = len(body.split())
        if words > 900:
            problems.append(f"{path.name}: {words} words. Over 900 it is an article, "
                            f"not a note. Send it to dev.to or the newsletter.")
        notes.append({
            "slug": slug, "title": meta.get("title", ""), "date": meta.get("date", ""),
            "standfirst": meta.get("standfirst", ""), "tags": meta.get("tags", []),
            "sources": meta["sources"], "linkedin": meta.get("linkedin", ""),
            "words": words, "html": render(body),
            "url": f"{SITE}/notes/{slug}.html",
        })
    notes.sort(key=lambda n: (n["date"], n["slug"]), reverse=True)
    return notes, problems


def main():
    check = "--check" in sys.argv
    if not SRC.exists():
        SRC.mkdir(parents=True)
    notes, problems = load()

    for p in problems:
        print(f"PROBLEM  {p}")
    if not notes:
        print("No notes in notes/src/. Nothing to build.")
        return 1 if problems else 0
    if problems and not check:
        print("\nRefusing to build with problems above. Fix them and re-run.")
        return 1
    if check:
        for n in notes:
            print(f"  ok  {n['date']}  {n['words']:>4}w  {n['slug']}")
        print(f"\n{len(notes)} note(s), {len(problems)} problem(s). Nothing written.")
        return 1 if problems else 0

    for n in notes:
        (NOTES / f"{n['slug']}.html").write_text(note_page(n), encoding="utf-8")
    (NOTES / "index.html").write_text(index_page(notes), encoding="utf-8")
    (NOTES / "feed.xml").write_text(feed(notes), encoding="utf-8")
    sm_path, sm_xml = update_sitemap(notes)
    sm_path.write_text(sm_xml, encoding="utf-8")
    (NOTES / "notes.json").write_text(json.dumps(
        [{k: n[k] for k in ("slug", "title", "date", "standfirst", "tags",
                            "sources", "linkedin", "words", "url")} for n in notes],
        indent=2), encoding="utf-8")

    print(f"Built {len(notes)} note(s):")
    for n in notes:
        print(f"  {n['date']}  {n['words']:>4}w  notes/{n['slug']}.html")
    print("Wrote notes/index.html, notes/feed.xml, notes/notes.json, sitemap.xml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render a 1200x630 share card for every note, plus one for /speaking/.

    python notes/cards.py            # render cards that do not exist yet
    python notes/cards.py --force    # re-render all of them
    python notes/build.py            # then rebuild, so pages point at the cards

Writes notes/cards/<slug>.png and speaking/card.png. build.py uses a note's card
for og:image, twitter:image and the JSON-LD image when the file exists, and falls
back to the site-wide og-image.png when it does not. So a note published without
running this still ships with an image, just not its own.

Kept out of build.py on purpose: rendering needs a Chromium browser, and build.py
has to keep running on a bare Python 3 at 6am. Look at the PNGs before pushing;
the headline shrinks to fit, but that is not the same as checking.
"""

import html
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
CARDS = build.NOTES / "cards"
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "msedge",
]

# Literal colours, matching og-image.png, so the PNG never follows the OS theme.
TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1200px; height: 630px; overflow: hidden; background: #111827; }
  body { font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
         color: #ffffff; position: relative; }
  .edge { position: absolute; left: 0; top: 0; bottom: 0; width: 16px;
          background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 55%, #9333ea 100%); }
  .wrap { position: absolute; left: 84px; right: 84px; top: 64px; bottom: 56px;
          display: flex; flex-direction: column; }
  .kicker { font-size: 26px; color: #a5b4fc; letter-spacing: 0.04em; text-transform: uppercase;
            font-weight: 600; }
  .rule { width: 120px; height: 5px; background: #9333ea; margin: 22px 0 30px; }
  h1 { font-size: 64px; line-height: 1.12; font-weight: 700; flex: 0 0 auto; }
  .sub { margin-top: 26px; font-size: 28px; line-height: 1.4; color: #aeb6c6; }
  .foot { margin-top: auto; display: flex; justify-content: space-between; align-items: baseline;
          font-size: 27px; }
  .name { font-weight: 700; }
  .site { color: #a855f7; }
</style></head><body>
  <div class="edge"></div>
  <div class="wrap">
    <div class="kicker">{kicker}</div>
    <div class="rule"></div>
    <h1 id="h">{title}</h1>
    <p class="sub" id="s">{sub}</p>
    <div class="foot"><span class="name">Imran Siddique</span><span class="site">imransiddique.com</span></div>
  </div>
<script>
  // Shrink the headline until headline + subline fit above the footer, then
  // drop the subline entirely if even the smallest headline leaves no room.
  const wrap = document.querySelector('.wrap'), h = document.getElementById('h'),
        s = document.getElementById('s'), foot = document.querySelector('.foot');
  const fits = () => s.getBoundingClientRect().bottom + 24 <= foot.getBoundingClientRect().top
                     && h.scrollWidth <= wrap.clientWidth;
  let size = 64;
  while (!fits() && size > 40) { size -= 2; h.style.fontSize = size + 'px'; }
  if (!fits()) s.style.display = 'none';
</script>
</body></html>
"""


def browser():
    for b in BROWSERS:
        if os.path.isabs(b) and Path(b).exists():
            return b
        found = shutil.which(b)
        if found:
            return found
    return None


def render(exe, out, kicker, title, sub):
    page = TEMPLATE.replace("{kicker}", html.escape(kicker)) \
                   .replace("{title}", html.escape(title)) \
                   .replace("{sub}", html.escape(sub))
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "card.html"
        src.write_text(page, encoding="utf-8")
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,630",
                        "--virtual-time-budget=2000", f"--user-data-dir={Path(tmp) / 'profile'}",
                        f"--screenshot={out}", src.as_uri()],
                       check=True, capture_output=True, timeout=60)
    if not out.exists() or out.stat().st_size == 0:
        raise RuntimeError(f"browser exited cleanly but wrote no {out.name}")


def main():
    force = "--force" in sys.argv
    exe = browser()
    if not exe:
        print("No Chromium-family browser found. Cards not rendered; pages keep og-image.png.")
        return 1
    notes, problems = build.load()
    if problems:
        print("build.py reports problems; fix those first:")
        for p in problems:
            print(f"  {p}")
        return 1
    CARDS.mkdir(exist_ok=True)
    jobs = [(CARDS / f'{n["slug"]}.png', f'Note \u00b7 {build.pretty(n["date"])}',
             n["title"], n["standfirst"]) for n in notes]
    speaker = ROOT / "speaking" / "card.png"
    jobs.append((speaker, "Speaking", "Agent governance, confidential computing, and what a "
                 "system can actually prove.", "Conference talks, summits and proof videos, "
                 "most with recordings."))
    made = 0
    for out, kicker, title, sub in jobs:
        if out.exists() and not force:
            continue
        render(exe, out, kicker, title, sub)
        made += 1
        print(f"  rendered {out.relative_to(ROOT)}")
    print(f"{made} card(s) rendered, {len(jobs) - made} already present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

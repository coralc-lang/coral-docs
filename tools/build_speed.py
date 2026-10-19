#!/usr/bin/env python3
"""Build the Coral Speed Edition.

The prose is shortened by hand (by agents) in SITE/textbook-speedy/; this
script only renders that manuscript, exactly like build_book.py renders the
full edition. It performs no automatic condensing.

Output: SITE/speed/<slug>/index.html + SITE/speed/index.html.
"""
import html
import os
import re

import build_book as bb

SRC = os.path.join(bb.SITE, "textbook-speedy")
OUT = os.path.join(bb.SITE, "speed")


def collect():
    """Populate the module-level chapter tables used by bb.inline/parse."""
    ch, ch_href, apx = {}, {}, {}
    for f in sorted(f for f in os.listdir(SRC) if re.match(r"^\d\d-.*\.txt$", f)):
        num, slug = f[:2], f[:-4]
        ch[num] = {"slug": slug, "href": f"{slug}/index.html", "file": os.path.join(SRC, f)}
        ch_href[num] = ch[num]["href"]
    for f in sorted(os.listdir(SRC)):
        if f.startswith("appendix-") and f.endswith(".txt"):
            slug = f[:-4]
            apx[slug] = {"slug": slug, "href": f"{slug}/index.html",
                         "file": os.path.join(SRC, f),
                         "title": bb.APX_TITLES.get(slug.split("-")[1], slug)}
    sref = os.path.join(SRC, "std_api_reference.md")
    if os.path.exists(sref):
        apx["std-api-reference"] = {"slug": "std-api-reference",
                                    "href": "std-api-reference/index.html",
                                    "file": sref, "title": "Standard Library API Reference"}
    bb.CH_HREF = ch_href
    return ch, apx


def shell(root, title_tag, page_title, kicker, lead, body, prev, nxt, canonical, description):
    prev_html = f'<a href="{root}speed/{prev}">← Previous</a>' if prev else "<span></span>"
    next_html = f'<a href="{root}speed/{nxt}">Next →</a>' if nxt else "<span></span>"
    desc = re.sub(r"\s+", " ", description or "").strip()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(desc)}" />
  <meta name="robots" content="index, follow" />
  <title>{html.escape(title_tag)}</title>
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{html.escape(title_tag)}" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:url" content="{canonical}" />
  <meta name="twitter:card" content="summary" />
  <link rel="stylesheet" href="{root}textbook/book.css" />
  <script src="{root}assets/js/script.js" defer></script>
</head>
<body>
  <header class="topbar">
    <a class="brand-wrap" href="{root}speed/index.html" style="color:inherit;text-decoration:none">
      <span class="brand-mark">C</span><span><span class="brand-name">Coral</span><br /><span class="brand-subtitle">speed edition</span></span>
    </a>
    <nav class="topnav" aria-label="Main navigation">
      <a href="{root}speed/index.html">Speed contents</a><a href="{root}textbook/index.html">Lengthy edition</a><a href="{root}coral-docs/index.html">Coral Docs</a>
    </nav>
  </header>
  <main class="content">
    <article class="article">
      {kicker}
      <h1>{html.escape(page_title)}</h1>
      {lead}
      {body}
      <nav class="chapter-nav">{prev_html}{next_html}</nav>
    </article>
  </main>
</body>
</html>
"""


def main():
    ch, apx = collect()
    order = sorted(ch)
    apx_order = sorted(apx.values(), key=lambda a: a["href"])
    chain = [ch[n]["href"] for n in order] + [a["href"] for a in apx_order]

    for num in order:
        info = ch[num]
        title, subtitle, els, topics = bb.parse_manuscript(info["file"], num)
        info.update(title=title, subtitle=subtitle, topics=topics, els=els)
        idx = chain.index(info["href"])
        prev = chain[idx - 1] if idx > 0 else None
        nxt = chain[idx + 1] if idx + 1 < len(chain) else None
        kicker = f'<p class="chapter-kicker">Speed Edition · Chapter {int(num)}</p>'
        lead = f'<p class="lead">{bb.inline(subtitle)}</p>' if subtitle else ""
        page = shell("../../", f"Chapter {num} · {title} | Coral Speed Edition",
                     title, kicker, lead, bb.render_chapter(els), prev, nxt,
                     canonical=f"{bb.BASE_URL}/speed/{info['href']}",
                     description=subtitle or f"Speed Edition of Chapter {int(num)}: {title}.")
        bb.write(os.path.join(OUT, info["slug"], "index.html"), page)

    for a in apx_order:
        title, _sub, els, topics = bb.parse_markdown(a["file"], a["title"])
        a["title"] = bb.APX_TITLES.get(a["slug"].split("-")[1], a["title"]) if a["slug"].startswith("appendix") else a["title"]
        a["topics"], a["els"] = topics, els
    for a in apx_order:
        idx = chain.index(a["href"])
        prev = chain[idx - 1] if idx > 0 else None
        nxt = chain[idx + 1] if idx + 1 < len(chain) else None
        page = shell("../../", f"{a['title']} | Coral Speed Edition", a["title"],
                     '<p class="chapter-kicker">Speed Edition · Reference</p>', "",
                     bb.render_elements(a["els"]), prev, nxt,
                     canonical=f"{bb.BASE_URL}/speed/{a['href']}",
                     description=f"{a['title']} (speed edition).")
        bb.write(os.path.join(OUT, a["slug"], "index.html"), page)

    parts_html = []
    for label, nums in bb.PARTS:
        lis = "".join(
            f'<li><a href="{ch[n]["href"]}"><span><span class="chapter-title">{html.escape(ch[n]["title"])}</span>'
            f'<span class="chapter-summary">{bb.inline(ch[n]["subtitle"] or "", "")}</span></span>'
            f'<span class="chapter-state">Chapter {int(n)}</span></a></li>'
            for n in nums if n in ch
        )
        parts_html.append(
            f'<section class="book-part"><p class="part-label">{label}</p><ol class="chapter-list">{lis}</ol></section>'
        )
    apx_lis = "".join(
        f'<li><a href="{a["href"]}"><span><span class="chapter-title">{html.escape(a["title"])}</span>'
        f'<span class="chapter-summary"></span></span><span class="chapter-state">Reference</span></a></li>'
        for a in apx_order
    )
    parts_html.append(
        f'<section class="book-part"><p class="part-label">Reference</p><ol class="chapter-list">{apx_lis}</ol></section>'
    )

    landing = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="The Coral Speed Edition: the book shortened for speed, with the full explanations cut." />
  <meta name="robots" content="index, follow" />
  <title>Coral Speed Edition</title>
  <link rel="canonical" href="{bb.BASE_URL}/speed/" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Coral Speed Edition" />
  <meta property="og:description" content="The Coral Book, shortened for speed." />
  <meta property="og:url" content="{bb.BASE_URL}/speed/" />
  <meta name="twitter:card" content="summary" />
  <link rel="stylesheet" href="../textbook/book.css" />
  <script src="../assets/js/script.js" defer></script>
</head>
<body>
  <header class="topbar">
    <a class="brand-wrap" href="./index.html" style="color:inherit;text-decoration:none">
      <span class="brand-mark">C</span><span><span class="brand-name">Coral</span><br /><span class="brand-subtitle">speed edition</span></span>
    </a>
    <nav class="topnav" aria-label="Main navigation">
      <a href="./index.html" aria-current="page">Speed contents</a><a href="../textbook/index.html">Lengthy edition</a><a href="../coral-docs/index.html">Coral Docs</a>
    </nav>
  </header>
  <main class="content">
    <article class="article">
      <header class="book-hero">
        <div class="book-kicker">Coral — Speed Edition</div>
        <h1>The Coral Book, sped up</h1>
        <p>The same ground, the prose cut to the bone. Same structure, same code, far fewer words. For the full explanations, read the <a href="../textbook/index.html">Lengthy Edition</a>.</p>
      </header>
      {''.join(parts_html)}
    </article>
  </main>
</body>
</html>
"""
    bb.write(os.path.join(OUT, "index.html"), landing)
    print(f"speed edition: {len(order)} chapters, {len(apx_order)} reference pages")


if __name__ == "__main__":
    main()

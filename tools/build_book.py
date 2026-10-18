#!/usr/bin/env python3
"""Build The Coral Book site pages from the manuscript in
/home/cerie/Documents/coralc/coral-docs/textbook/.

Chapters 00-43 are plain text (indented code blocks, N.x section headings).
Appendices (appendix-*.txt) and std_api_reference.md are Markdown.

Output: textbook/<slug>/index.html for every chapter/appendix, a regenerated
textbook/index.html landing page, and textbook/book-data.js (navigation data).
"""
import html
import os
import re
import shutil

SRC = "/home/cerie/Documents/coralc/coral-docs/textbook"
SITE = "/home/cerie/Documents/coral-docs"
OUT = os.path.join(SITE, "textbook")

APX_TITLES = {
    "a": "Appendix A · A Tour of the Standard Library",
    "b": "Appendix B · Built-in Functions",
    "d": "Appendix D · Prelude, Core, and Platform",
    "e": "Appendix E · Collections",
    "f": "Appendix F · Text, Data, Time, and Formatting",
    "g": "Appendix G · Input, Output, and System Interaction",
    "h": "Appendix H · Memory and Concurrency",
    "i": "Appendix I · Math and Crypto",
    "j": "Appendix J · Parsers",
    "k": "Appendix K · Misc and Testing",
}

PARTS = [
    ("Part I · Getting oriented", [f"{n:02d}" for n in range(0, 2)]),
    ("Part II · The language core", [f"{n:02d}" for n in range(2, 8)]),
    ("Part III · Types, data, and text", [f"{n:02d}" for n in range(8, 18)]),
    ("Part IV · Systems and the standard library", [f"{n:02d}" for n in range(18, 24)]),
    ("Part V · Live examples", [f"{n:02d}" for n in range(24, 44)]),
]

CH = {}          # number -> {slug, href, title, subtitle, topics}
APX = {}         # slug -> {href, title, topics}
CH_HREF = {}     # number -> href

STEP_LABELS = {
    "The problem",
    "Picture this",
    "The better approach",
    "Brute force, then better",
    "The approach",
    "The idea",
    "The intuition",
    "The principle",
    "The implementation",
    "The Coral implementation",
    "Time and space",
    "Cost and notes",
    "The cost",
    "Edge cases",
    "Edge cases and variations",
    "Edge cases and a variation",
    "A variation",
    "Variation",
    "The before",
    "The after",
    "When the before is fine",
    "Why greedy works here",
    "Why greedy fails here",
    "A note on the imports",
    "A note on the imports these examples use",
    "A note on the shape of every example",
}


def as_definition_list(block):
    """Recognise a glossary-style definition list: a 4-space term line
    followed by one or more 8-space definition lines, three or more times."""
    entries = []
    j, n = 0, len(block)
    while j < n:
        if block[j].strip() == "":
            j += 1
            continue
        if block[j].startswith("        ") or not re.match(r"^ {4}\S", block[j]):
            return None
        term = block[j].strip()
        if not re.match(r"^[A-Za-z][A-Za-z0-9 _-]*$", term) or len(term) > 40:
            return None
        j += 1
        defn = []
        while j < n and block[j].strip() != "" and re.match(r"^ {8,}\S", block[j]):
            defn.append(block[j].strip())
            j += 1
        if not defn:
            return None
        entries.append((term, " ".join(defn)))
    return entries if len(entries) >= 3 else None


def collect_list(lines, i, item_re, strip_re):
    """Collect list items, tolerating blank lines between items and
    absorbing wrapped continuation lines that are indented past the bullet."""
    def indent_of(s):
        return len(s) - len(s.lstrip(" "))
    items = []
    n = len(lines)
    bullet_indent = 0
    while i < n:
        if item_re.match(lines[i]):
            bullet_indent = indent_of(lines[i])
            items.append(strip_re.sub("", lines[i]).strip())
            i += 1
        elif lines[i].strip() == "" and i + 1 < n and item_re.match(lines[i + 1]):
            i += 1
        elif items and lines[i].strip() != "" and indent_of(lines[i]) > bullet_indent:
            items[-1] = items[-1] + " " + lines[i].strip()
            i += 1
        else:
            break
    return items, i


def plain(text):
    """Plain text for JSON nav data: drop HTML tags, backticks, emphasis."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", text)
    return text.replace("`", "")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def inline(text, ref_prefix="../"):
    out = esc(text)
    # chapter cross references
    def chref(m):
        n = int(m.group(1))
        href = CH_HREF.get(f"{n:02d}")
        if href:
            return f'<a href="{ref_prefix}{href}">Chapter {n}</a>'
        return m.group(0)

    out = re.sub(r"\bChapter\s*(\d+)\b", chref, out)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    return out


def is_section_heading(line):
    return re.match(r"^\d+\.\d+\s+\S", line) is not None


def parse_block(lines, i):
    """Parse one block starting at line i. Return (element, next_i)."""
    line = lines[i]
    if line.strip() == "":
        return None, i + 1
    if line.strip() in ("---", "***", "___"):
        return ("hr", None), i + 1
    m = re.match(r"^(\d+)\.(\d+)\s+(.*)$", line)
    if m:
        d, x, title = m.group(1), m.group(2), m.group(3).strip()
        return ("h2", f"s{d}-{x}", title), i + 1
    if re.match(r"^Exercises\s*$", line):
        return ("h2", "exercises", "Exercises"), i + 1
    # indented bullet / ordered list (mis-indented lists)
    if re.match(r"^ {4,}[-*]\s+\S", line):
        items, i = collect_list(lines, i, re.compile(r"^ {4,}[-*]\s+\S"),
                                re.compile(r"^\s*[-*]\s+"))
        return ("ul", items), i
    if re.match(r"^ {4,}\d+\.\s+\S", line):
        items, i = collect_list(lines, i, re.compile(r"^ {4,}\d+\.\s+\S"),
                                re.compile(r"^\s*\d+\.\s+"))
        return ("ol", items), i
    # indented code block
    if re.match(r"^ {4,}\S", line):
        block = []
        while i < len(lines) and (lines[i].strip() == "" or re.match(r"^ {4,}\S", lines[i])):
            block.append(lines[i])
            i += 1
        while block and block[-1].strip() == "":
            block.pop()
        dl = as_definition_list(block)
        if dl is not None:
            return ("dl", dl), i
        ded = [l[4:] if l.startswith("    ") else l for l in block]
        stripped = [l.strip() for l in ded if l.strip()]
        head = stripped[0] if stripped else ""
        if head.startswith("module") or head.startswith("lib/") or any(
            ch in head for ch in ("├", "└", "│")
        ):
            lang = "text"
        else:
            lang = "coral"
        return ("pre", lang, "\n".join(ded)), i
    # list
    if re.match(r"^\s*[-*]\s+\S", line):
        items, i = collect_list(lines, i, re.compile(r"^\s*[-*]\s+\S"),
                                re.compile(r"^\s*[-*]\s+"))
        return ("ul", items), i
    if re.match(r"^\s*\d+\.\s+\S", line):
        items, i = collect_list(lines, i, re.compile(r"^\s*\d+\.\s+\S"),
                                re.compile(r"^\s*\d+\.\s+"))
        return ("ol", items), i
    # paragraph
    para = [line.strip()]
    i += 1
    while i < len(lines) and lines[i].strip() != "" and not re.match(r"^ {4,}\S", lines[i]) \
            and not re.match(r"^\s*(\d+\.\d+|[-*]\s|\d+\.\s)", lines[i]) \
            and lines[i].strip() not in ("---", "***", "___") \
            and not re.match(r"^\s*Exercises\s*$", lines[i]):
        para.append(lines[i].strip())
        i += 1
    text = " ".join(para)
    if text in STEP_LABELS:
        return ("step", text), i
    return ("p", text), i


def render_elements(elements):
    parts = []
    for el in elements:
        kind = el[0]
        if kind == "h2":
            parts.append(f'<section><h2 id="{el[1]}">{inline(el[2])}</h2></section>')
        elif kind == "h3":
            parts.append(f'<h3 id="{el[1]}">{inline(el[2])}</h3>')
        elif kind == "p":
            text = el[1]
            m = re.match(r"^([A-Z][^.]{1,70}?)\.\s+(\S.*)$", text)
            if m and m.group(1).strip() in STEP_LABELS:
                parts.append(f'<p class="step-label">{inline(m.group(1))}</p>')
                parts.append(f"<p>{inline(m.group(2))}</p>")
            else:
                parts.append(f"<p>{inline(text)}</p>")
        elif kind == "step":
            parts.append(f'<p class="step-label">{inline(el[1])}</p>')
        elif kind == "dl":
            rows = "".join(f"<dt>{inline(t)}</dt><dd>{inline(d)}</dd>" for t, d in el[1])
            parts.append(f'<dl class="glossary">{rows}</dl>')
        elif kind == "pre":
            code = html.escape(el[2])
            parts.append(
                '<pre class="code-block"><button class="copy-btn" type="button">Copy</button>'
                f'<code class="language-{el[1]}">{code}</code></pre>'
            )
        elif kind == "ul":
            items = "".join(f"<li>{inline(x)}</li>" for x in el[1])
            parts.append(f"<ul>{items}</ul>")
        elif kind == "ol":
            items = "".join(f"<li>{inline(x)}</li>" for x in el[1])
            parts.append(f"<ol>{items}</ol>")
        elif kind == "hr":
            parts.append("<hr />")
        elif kind == "table":
            head = "".join(f"<th>{inline(c)}</th>" for c in el[1]["head"])
            rows = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                for row in el[1]["rows"]
            )
            parts.append(
                '<div class="table-wrap"><table>'
                f"<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>"
            )
        elif kind == "blockquote":
            inner = "".join(f"<p>{inline(p)}</p>" for p in el[1])
            parts.append(f"<blockquote>{inner}</blockquote>")
    return "\n".join(parts)


def parse_manuscript(path, num):
    lines = open(path, encoding="utf-8").read().split("\n")
    # header line
    title = None
    body_start = 0
    m = re.match(r"^Chapter\s*\d+\s*:\s*(.+)$", lines[0].strip())
    if m:
        title = m.group(1).strip()
        body_start = 1
    elif re.match(r"^Chapter\s*\d+\s*$", lines[0].strip()):
        body_start = 1
    # find title if not in header
    idx = body_start
    if title is None:
        while idx < len(lines) and lines[idx].strip() == "":
            idx += 1
        if idx < len(lines) and not is_section_heading(lines[idx]):
            title = lines[idx].strip()
            idx += 1
    if title is None:
        title = num
    # subtitle: next non-empty short line
    subtitle = None
    j = idx
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j < len(lines):
        cand = lines[j].strip()
        if len(cand) < 100 and ". " not in cand and not is_section_heading(cand) \
                and not cand.startswith(("#", "-", "*")) and cand[-1] not in ".!?":
            subtitle = cand
            idx = j + 1
    body = lines[idx:]
    els, topics = [], []
    i = 0
    while i < len(body):
        el, i = parse_block(body, i)
        if el is None:
            continue
        if el[0] == "h2":
            topics.append({"title": el[2], "id": el[1]})
        els.append(el)
    return title, subtitle, els, topics


def parse_markdown(path, fallback_title, num_prefix=None):
    lines = open(path, encoding="utf-8").read().split("\n")
    title = fallback_title
    els, topics = [], []
    i = 0
    in_code = False
    code_lang = "coral"
    code = []
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_lang = line.strip()[3:].strip() or "text"
                code = []
            else:
                in_code = False
                els.append(("pre", code_lang, "\n".join(code)))
            i += 1
            continue
        if in_code:
            code.append(line)
            i += 1
            continue
        stripped = line.lstrip()
        # pipe table
        if stripped.startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*$", lines[i + 1]):
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]
            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            els.append(("table", {"head": head, "rows": rows}))
            continue
        # blockquote
        if stripped.startswith(">"):
            quoted = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quoted.append(re.sub(r"^\s*>\s?", "", lines[i]).rstrip())
                i += 1
            paras, cur = [], []
            for q in quoted:
                if q.strip() == "":
                    if cur:
                        paras.append(" ".join(cur))
                        cur = []
                else:
                    cur.append(q.strip())
            if cur:
                paras.append(" ".join(cur))
            els.append(("blockquote", paras))
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1:
                title = text
            elif level == 2:
                sid = slugify(re.sub(r"[^a-zA-Z0-9 ]", " ", text))[:40]
                els.append(("h2", sid, text))
                topics.append({"title": text, "id": sid})
            else:
                sid = slugify(re.sub(r"[^a-zA-Z0-9 ]", " ", text))[:40]
                els.append(("h3", sid, text))
                topics.append({"title": text, "id": sid})
            i += 1
            continue
        el, i = parse_block(lines, i)
        if el is None:
            continue
        if el[0] == "h2":
            topics.append({"title": el[2], "id": el[1]})
        els.append(el)
    return title, None, els, topics


def shell(title_tag, page_title, kicker_html, lead_html, body_html, prev, nxt):
    prev_html = f'<a href="../{prev}">← Previous</a>' if prev else "<span></span>"
    next_html = f'<a href="../{nxt}">Next →</a>' if nxt else "<span></span>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title_tag)}</title>
  <link rel="stylesheet" href="../book.css" />
  <script src="../../assets/js/script.js" defer></script>
</head>
<body>
  <header class="topbar">
    <a class="brand-wrap" href="../../coral-docs/index.html" style="color:inherit;text-decoration:none">
      <span class="brand-mark">C</span><span><span class="brand-name">Coral</span><br /><span class="brand-subtitle">the book</span></span>
    </a>
    <nav class="topnav" aria-label="Main navigation">
      <a href="../index.html">Book contents</a><a href="../../coral-docs/index.html">Coral Docs</a>
    </nav>
  </header>
  <main class="content">
    <article class="article">
      {kicker_html}
      <h1>{html.escape(page_title)}</h1>
      {lead_html}
      {body_html}
      <nav class="chapter-nav">{prev_html}{next_html}</nav>
    </article>
  </main>
</body>
</html>
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    # ---- collect chapters ----
    chapter_files = sorted(
        f for f in os.listdir(SRC)
        if re.match(r"^\d\d-.*\.txt$", f)
    )
    for f in chapter_files:
        num = f[:2]
        path = os.path.join(SRC, f)
        slug = f[:-4]
        CH[num] = {"slug": slug, "href": f"{slug}/index.html", "file": path}
        CH_HREF[num] = CH[num]["href"]

    # appendices
    apx_files = sorted(f for f in os.listdir(SRC) if f.startswith("appendix-") and f.endswith(".txt"))
    for f in apx_files:
        slug = f[:-4]
        key = slug.split("-")[1]
        APX[slug] = {"slug": slug, "href": f"{slug}/index.html",
                     "file": os.path.join(SRC, f),
                     "title": APX_TITLES.get(key, slug)}
        APX[slug]["is_md"] = True
    if os.path.exists(os.path.join(SRC, "std_api_reference.md")):
        APX["std-api-reference"] = {
            "slug": "std-api-reference",
            "href": "std-api-reference/index.html",
            "file": os.path.join(SRC, "std_api_reference.md"),
            "title": "Standard Library API Reference",
            "is_md": True,
        }

    # ---- back up old stub chapters ----
    backup = os.path.join(SITE, "tools", "_old_stubs")
    os.makedirs(backup, exist_ok=True)
    old_stub_names = [
        "01-foundation", "02-core-syntax", "03-operators", "04-control-flow",
        "05-functions", "06-data-structures", "07-type-system", "08-extensions",
        "09-memory", "10-concurrency", "11-modules", "12-attributes-comptime",
        "13-standard-library", "14-ffi-build", "15-tooling",
    ]
    for d in old_stub_names:
        full = os.path.join(OUT, d)
        if os.path.isdir(full):
            dest = os.path.join(backup, d)
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            shutil.move(full, dest)

    # ---- parse + render chapters ----
    for num in sorted(CH):
        info = CH[num]
        title, subtitle, els, topics = parse_manuscript(info["file"], num)
        info["title"], info["subtitle"], info["topics"], info["els"] = title, subtitle, topics, els

    # prev/next chain = chapters then appendices
    apx_order = sorted(APX.values(), key=lambda a: a["href"])
    chain = [c["href"] for c in CH.values()] + [a["href"] for a in apx_order]

    for num in sorted(CH):
        info = CH[num]
        idx = chain.index(info["href"])
        prev = chain[idx - 1] if idx > 0 else None
        nxt = chain[idx + 1] if idx + 1 < len(chain) else None
        kicker = f'<p class="chapter-kicker">Chapter {int(num)}</p>'
        lead = f'<p class="lead">{inline(info["subtitle"])}</p>' if info["subtitle"] else ""
        page = shell(
            f"Chapter {num} · {info['title']} | The Coral Book",
            info["title"], kicker, lead, render_elements(info["els"]), prev, nxt,
        )
        write(os.path.join(OUT, info["slug"], "index.html"), page)

    # ---- parse + render appendices ----
    for slug, a in APX.items():
        title, _sub, els, topics = parse_markdown(a["file"], a["title"])
        a["title"] = APX_TITLES.get(slug.split("-")[1], a["title"]) if slug.startswith("appendix") else a["title"]
        a["topics"] = topics
        a["els"] = els
    for slug, a in APX.items():
        idx = chain.index(a["href"])
        prev = chain[idx - 1] if idx > 0 else None
        nxt = chain[idx + 1] if idx + 1 < len(chain) else None
        kicker = '<p class="chapter-kicker">Reference</p>'
        page = shell(
            f"{a['title']} | The Coral Book",
            a["title"], kicker, "", render_elements(a["els"]), prev, nxt,
        )
        write(os.path.join(OUT, slug, "index.html"), page)

    # ---- book-data.js ----
    def nav_chapter(num):
        info = CH[num]
        return {
            "href": info["href"], "number": num, "title": plain(info["title"]),
            "topics": [{"title": plain(t["title"]), "id": t["id"]} for t in info["topics"]],
        }

    data_parts = []
    for label, nums in PARTS:
        data_parts.append({"title": label, "chapters": [nav_chapter(n) for n in nums if n in CH]})
    data_parts.append({"title": "Reference", "chapters": [
        {"href": a["href"], "number": "", "title": plain(a["title"]),
         "topics": [{"title": plain(t["title"]), "id": t["id"]} for t in a["topics"]]}
        for a in apx_order
    ]})
    import json
    js = "window.CORAL_BOOK = " + json.dumps({"parts": data_parts}, ensure_ascii=False) + ";\n"
    write(os.path.join(OUT, "book-data.js"), js)

    # ---- landing page ----
    def chapter_li(num):
        info = CH[num]
        state = "Lesson"
        summary = info["subtitle"] or ""
        topics = "".join(f"<li>{inline(t['title'], '')}</li>" for t in info["topics"][:8])
        return (
            f'<li><a href="{info["href"]}"><span><span class="chapter-title">{html.escape(info["title"])}</span>'
            f'<span class="chapter-summary">{inline(summary, "")}</span></span>'
            f'<span class="chapter-state">{state}</span></a>'
            f'<details class="chapter-topics"><summary>Chapter topics</summary><ul>{topics}</ul></details></li>'
        )

    parts_html = []
    for label, nums in PARTS:
        lis = "".join(chapter_li(n) for n in nums if n in CH)
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
  <title>The Coral Book</title>
  <link rel="stylesheet" href="./book.css" />
  <script src="../assets/js/script.js" defer></script>
</head>
<body>
  <header class="topbar">
    <a class="brand-wrap" href="../coral-docs/index.html" style="color:inherit;text-decoration:none">
      <span class="brand-mark">C</span><span><span class="brand-name">Coral</span><br /><span class="brand-subtitle">the book</span></span>
    </a>
    <nav class="topnav" aria-label="Main navigation">
      <a href="../coral-docs/index.html">Coral Docs</a><a href="../coral-docs/tooling/index.html">Tooling</a><a href="./index.html" aria-current="page">Textbook</a>
    </nav>
  </header>
  <main class="content">
    <article class="article">
      <header class="book-hero">
        <div class="book-kicker">A guided path through Coral</div>
        <h1>The Coral Book</h1>
        <p>A chapter-by-chapter introduction to the language: its C-family syntax, type-first declarations, and the newer features built around them.</p>
      </header>
      <h2>Reading path</h2>
      <p>The book follows a progression: first learn to read Coral, then use it to build programs, then work problems end to end.</p>
      {''.join(parts_html)}
    </article>
  </main>
</body>
</html>
"""
    write(os.path.join(OUT, "index.html"), landing)
    print(f"chapters: {len(CH)}  appendices: {len(APX)}  parts: {len(data_parts)}")


if __name__ == "__main__":
    main()

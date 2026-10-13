"""The field guide (/guide/): content sources owned by AgentWorkshop, rendering owned by Kynoss.

Each source is _build/guide/<slug>.md:

    ---
    title: It said it was done, and it wasn't
    slug: said-done
    summary: One or two sentences for the index and the page description.
    order: 1
    status: draft            # or: published. Only published pages render.
    ---
    Intro paragraph(s), then ## sections.

Markdown supported (a small, fixed subset; anything else renders as plain text):
paragraphs, ## and ### headings, - and 1. lists (one level), > quotes, ``` code blocks,
`code`, **bold**, *italic*, [text](https://… or /path). No raw HTML.

Lines of the form <sub>Source: …</sub> are for fact-checking only: they're removed before
rendering, and the build fails if anything that looks like one survives.
"""
import html
import re
from pathlib import Path

FIELDS = ("title", "slug", "summary", "order", "status")
SOURCE_LINE = re.compile(r"^\s*<sub>\s*Source:.*?</sub>\s*$", re.I)
LEAK = re.compile(r"<sub|Source:|/Users/|~/(?:AgentWorkshop|Kynoss|Systems|Personal|HOA|Trading|Documents)\b", re.I)
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise ValueError(f"{path.name}: front matter missing")
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.split(" #", 1)[0].strip()
    missing = [f for f in FIELDS if not meta.get(f)]
    if missing:
        raise ValueError(f"{path.name}: missing {', '.join(missing)}")
    if meta["status"] not in ("draft", "published"):
        raise ValueError(f"{path.name}: status must be draft or published")
    if not SLUG.match(meta["slug"]):
        raise ValueError(f"{path.name}: slug must be lowercase words joined by hyphens")
    meta["order"] = int(meta["order"])
    body = "\n".join(l for l in m.group(2).splitlines() if not SOURCE_LINE.match(l))
    meta["body_html"], meta["toc"] = to_html(body)
    for k in ("title", "summary", "body_html"):
        if LEAK.search(meta[k]):
            raise ValueError(f"{path.name}: a source note or internal path would be published ({k})")
    meta["words"] = len(re.sub(r"<[^>]+>", " ", meta["body_html"]).split())
    return meta


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)

    def link(m):
        url = m.group(2)
        if not re.match(r"^(https://|/)", url):
            return m.group(0)
        ext = url.startswith("https://") and not url.startswith("https://kynossstudios.com")
        attrs = ' rel="noopener"' if ext else ""
        return f'<a href="{html.escape(url)}"{attrs}>{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def anchor(text, seen):
    a = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    base, n = a, 2
    while a in seen:
        a, n = f"{base}-{n}", n + 1
    seen.add(a)
    return a


def to_html(md):
    out, toc, seen = [], [], set()
    para, items, kind, quote = [], [], None, []
    lines = md.splitlines()

    def flush():
        nonlocal para, items, kind, quote
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
        if items:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{kind}>")
        if quote:
            out.append(f"<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
        para, items, kind, quote = [], [], None, []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("```"):
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
            continue
        h = re.match(r"^(#{2,3})\s+(.*)$", line)
        li = re.match(r"^\s*(?:([-*])|(\d+)\.)\s+(.*)$", line)
        if not line.strip():
            flush()
        elif h:
            flush()
            level, text = len(h.group(1)), h.group(2).strip()
            a = anchor(text, seen)
            if level == 2:
                toc.append((a, text))
            out.append(f'<h{level} id="{a}">{inline(text)}</h{level}>')
        elif li:
            want = "ul" if li.group(1) else "ol"
            if para or quote or (kind and kind != want):
                flush()
            kind = want
            items.append(li.group(3))
        elif line.startswith(">"):
            if para or items:
                flush()
            quote.append(line.lstrip("> ").strip())
        elif items and line.startswith(("  ", "\t")):
            items[-1] += " " + line.strip()
        else:
            if items or quote:
                flush()
            para.append(line.strip())
        i += 1
    flush()
    return "\n".join(out), toc


def load(folder):
    """Every published guide, in order. Drafts are parsed too, so a broken draft fails the build early."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    guides = [parse(p) for p in sorted(folder.glob("*.md"))]
    slugs = [g["slug"] for g in guides]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        raise ValueError(f"guide: duplicate slug {', '.join(sorted(dupes))}")
    return sorted((g for g in guides if g["status"] == "published"), key=lambda g: (g["order"], g["slug"]))

#!/usr/bin/env python3
"""Build kynossstudios.com.

Reads _build/site.json (the app registry), live App Store data (iTunes Lookup,
cached), each app's APP-STORE.md and the hand-written support/privacy pages,
then writes the generated pages into the repo root and wraps the legacy
support/privacy pages in the shared site chrome.

    python3 _build/build.py            # build (uses cached App Store data < 12 h old)
    python3 _build/build.py --refresh  # re-fetch App Store data and images

GitHub Pages serves the repo root as-is, so commit the output.
"""
import datetime as dt
import html
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import jinja2
import segno
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import appstore  # noqa: E402

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent
ALL_NAMES = []
CACHE = BUILD / "cache"
WORKSHOP = Path.home() / "AgentWorkshop"
REFRESH = "--refresh" in sys.argv
LOCALE_NAMES = {"de-DE": "Deutsch", "en-GB": "English (UK)", "es-MX": "Español", "fr-FR": "Français",
                "it-IT": "Italiano", "ja-JP": "日本語", "pt-BR": "Português (Brasil)"}
FLOW_ICONS = {"device": "device", "icloud": "icloud", "relay": "out", "gamecenter": "people",
              "network": "wifi", "byok": "key", "other": "out", "people": "people", "link": "out"}


# ---------------------------------------------------------------- fetching

def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "kynoss-site-build/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            return data if binary else data.decode("utf-8")
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def lookup(store_id):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"lookup-{store_id}.json"
    if f.exists() and not REFRESH and time.time() - f.stat().st_mtime < 12 * 3600:
        return json.loads(f.read_text())
    data = json.loads(fetch(f"https://itunes.apple.com/lookup?id={store_id}&country=us"))
    res = data["results"][0] if data.get("results") else {}
    f.write_text(json.dumps(res, indent=1))
    return res


def save_image(url_or_path, dest, size=None, fmt="WEBP", quality=82):
    """Download (or read) an image, optionally square-resize it, and save it."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not REFRESH:
        return
    raw = fetch(url_or_path, binary=True) if str(url_or_path).startswith("http") else Path(url_or_path).read_bytes()
    im = Image.open(io.BytesIO(raw))
    im = im.convert("RGBA" if fmt == "PNG" else "RGB")
    if size:
        im = im.resize((size, size), Image.LANCZOS)
    kw = {"quality": quality, "method": 6} if fmt == "WEBP" else {"optimize": True}
    im.save(dest, fmt, **kw)


# ---------------------------------------------------------------- text helpers

PROPER = ["iCloud", "iPhone", "iPad", "iOS", "Apple", "Apple Watch", "Game Center", "AI", "PDF", "Pro", "Premium",
          "Plus", "TV", "QR", "OpenAI", "Siri", "Duo", "HRV", "APR", "US"]


def sentence_case(s, names=()):
    s = s.strip().strip(":")
    s = s[:1].upper() + s[1:].lower()
    for w in list(names) + PROPER:
        s = re.sub(r"(?<![A-Za-z])" + re.escape(w.lower()) + r"(?![A-Za-z])", w, s, flags=re.I)
    return s[:1].upper() + s[1:]


def linkify(esc):
    return re.sub(r"(https?://[^\s<]+[^\s<.,;:)])", r'<a href="\1">\1</a>', esc)


PRIVACY_LINE = re.compile(r"privacy|private icloud|stays? on your (phone|iphone|device)|stores everything on your|"
                          r"never leaves?|nowhere else|no cloud|no servers?|not stored|policy:", re.I)


def is_heading(line):
    letters = re.sub(r"[^A-Za-z]", "", line)
    return bool((len(line) <= 64 and letters and letters.isupper() and len(letters) > 3)
                or re.fullmatch(r"\*\*[^*]+\*\*:?", line))


def drop_privacy_claims(text):
    """Remove the description's own privacy claims; app pages show the verified data panel instead."""
    keep, skipping = [], False
    for raw in text.splitlines():
        line = raw.strip()
        if line and is_heading(line):
            skipping = bool(re.search(r"privacy|your data", line, re.I))
            if skipping:
                continue
        elif skipping or (line and PRIVACY_LINE.search(line)):
            continue
        keep.append(raw)
    return "\n".join(keep)


def text_to_html(text, names=()):
    """App Store description text → simple HTML (paragraphs, lists, headings)."""
    out, para, items = [], [], []

    def flush():
        nonlocal para, items
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para = []
        if items:
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        esc = html.escape(line)
        esc = re.sub(r"\*\*(.+?)\*\*", r"\1", esc)
        bullet = re.match(r"^([•\-–*▸]|\d+[.)])\s+(.*)$", line)
        if is_heading(line):
            flush()
            out.append(f"<h3>{html.escape(sentence_case(line.strip('*'), names))}</h3>")
        elif bullet:
            if para:
                out.append("<p>" + " ".join(para) + "</p>")
                para = []
            items.append(linkify(re.sub(r"\*\*(.+?)\*\*", r"\1", html.escape(bullet.group(2)))))
        else:
            if items:
                flush()
            para.append(linkify(esc))
    flush()
    return "\n".join(out)


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def extract_faq(page_html):
    """Question/answer pairs from a support page, whatever template it uses."""
    pairs = []
    for q, a in re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", page_html, re.S):
        pairs.append((strip_tags(q), strip_tags(a)))
    if not pairs:
        for q, a in re.findall(r"<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>", page_html, re.S):
            if q.strip().endswith("?"):
                pairs.append((strip_tags(q), strip_tags(a)))
    if not pairs:
        for q, a in re.findall(r"<p[^>]*>\s*<strong>(.*?)</strong>\s*<br\s*/?>(.*?)</p>", page_html, re.S):
            pairs.append((strip_tags(q), strip_tags(a)))
    return [(q, a) for q, a in pairs if q and a]


def month_day_year(iso):
    d = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return d.strftime("%b %-d, %Y")


# ---------------------------------------------------------------- stats for "how we build"

IDEA_NOISE = re.compile(r"^(Step|Steps|Verdict|Path|Key|Contrarian|Gaps|Idea|Process|Served-User|Why|iPhone|Report|"
                        r"Vision|Obstacle|Scoring|Soul|Naming|Competitive|Recommended|Market|Risks?|Summary|Notes?|Raw|"
                        r"Research|Sources?|Score|Developer|Framework|Pre-Step-1|Sibling-redirect)\b", re.I)


def count_killed():
    """Ideas killed before any code (IDEAS-ARCHIVE.md) and projects stopped after work began (PORTFOLIO.md)."""
    s = (WORKSHOP / "docs" / "archive" / "IDEAS-ARCHIVE.md").read_text(encoding="utf-8")
    names = set()
    for h in re.findall(r"^#{2,3} (.+)$", s, re.M):
        w = re.split(r"[ (—:·,/+]", h.strip())[0].strip("*")
        if w and w[0].isupper() and not IDEA_NOISE.match(w) and w not in ("Path-Aware", "Moved", "DEVELOPER"):
            names.add(w)
    for m in re.finditer(r"(?:order|ideas?|candidates)[^:\n]{0,80}:\s*((?:[A-Z][a-zA-Z]+(?:,\s*|\s+and\s+|\.\s*$)){3,})", s, re.M):
        names.update(re.findall(r"[A-Z][a-zA-Z]+", m.group(1)))
    names.update(re.findall(r"\*\*([A-Z][a-z]+[a-z])\*\*\s*\((?:PASS|Kill)", s))
    i = s.find("## Moved from IDEAS.md Evaluation Queue")
    for stub in re.findall(r"<!--\s*(.*?)-->", s[i:] if i >= 0 else "", re.S):
        nm = re.match(r"\**([A-Z][A-Za-z\-]+)", stub.strip())
        if not nm:
            continue
        if re.search(r"GREENLIT|greenlit|folded into|FOLDED|→ project|PURSUE", stub[:400]) and not re.search(r"killed|KILLED", stub[:200]):
            names.discard(nm.group(1))
        elif re.search(r"PASS|killed|KILLED|Kill", stub):
            names.add(nm.group(1))
    unnamed = 0  # batches recorded without per-idea headings, e.g. "the other 13 candidates", "survivors (a · b · c)"
    for h in re.findall(r"^### (.+)$", s, re.M):
        if "archived" in h:
            continue
        n = re.search(r"other (\d+) candidates", h)
        if n:
            unnamed += int(n.group(1))
        elif re.search(r"survivors \(", h):
            unnamed += h.count("·") + 1
    before = len(names) + unnamed

    p = (WORKSHOP / "docs" / "PORTFOLIO.md").read_text(encoding="utf-8")
    shelved = re.search(r"^## Shelved Apps\n(.*?)(?=^## |\Z)", p, re.M | re.S)
    after = len(re.findall(r"^### ", shelved.group(1), re.M)) if shelved else 0
    active = re.search(r"^## Active Portfolio\n(.*?)(?=^## |\Z)", p, re.M | re.S)
    for sec in re.split(r"^### ", active.group(1), flags=re.M)[1:] if active else []:
        if re.search(r"KILLED", sec[:600]):
            after += 1
    return before, after


def build_stats():
    stats = {"updates": 170, "read_ratio": "1,000", "killed_before": 105, "killed_after": 26}
    try:
        stats["killed_before"], stats["killed_after"] = count_killed()
    except Exception as e:
        print(f"warn: kill count fell back to the stored numbers ({e})")
    stats["killed"] = stats["killed_before"] + stats["killed_after"]
    try:
        vh = json.loads((WORKSHOP / "scripts" / "version_history_data.json").read_text())
        n = sum(len({v["version"] for v in vs if v["state"] == "READY_FOR_SALE"}) for vs in vh.values())
        stats["updates"] = n // 10 * 10
    except Exception:
        pass
    try:
        t = (WORKSHOP / "docs" / "reports" / "TOKENS.md").read_text()
        inp = re.search(r"\*\*Input tokens:\*\* ([\d.]+)B", t)
        outp = re.search(r"\*\*output:\*\* ([\d.]+)M", t)
        if inp and outp:
            ratio = float(inp.group(1)) * 1000 / float(outp.group(1))
            stats["read_ratio"] = f"{round(ratio, -2):,.0f}"
    except Exception:
        pass
    return stats


# ---------------------------------------------------------------- og images

OG_W, OG_H = 1200, 630
OG_FONT = ROOT / "assets" / "fonts" / "bricolage-latin.woff2"
INK = (15, 21, 34)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """t of colour a, the rest b (like CSS color-mix)."""
    return tuple(round(x * t + y * (1 - t)) for x, y in zip(a, b))


def og_font(size, weight=700, width=86):
    f = ImageFont.truetype(str(OG_FONT), size)
    try:
        f.set_variation_by_axes([min(96, size), weight, width])
    except Exception:
        pass
    return f


def text_font(size, weight=500):
    f = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)
    try:  # axes: width, optical size, grade, weight
        f.set_variation_by_axes([100, min(96, max(17, size)), 400, weight])
    except Exception:
        pass
    return f


def og_backdrop(accent):
    """The app header's gradient: deep accent, a lighter glow top right, film grain against banding."""
    from PIL import ImageFilter
    c = hex_rgb(accent)
    top, mid, low = mix(c, (0, 0, 0), 0.78), mix(c, (0, 0, 0), 0.52), mix(c, (4, 6, 11), 0.34)
    grad = Image.new("RGB", (3, 1))
    grad.putdata([top, mid, low])
    im = grad.resize((OG_W * 2, 1), Image.BICUBIC).resize((OG_W * 2, OG_H * 2))
    im = im.rotate(-28, resample=Image.BICUBIC).crop((OG_W // 2, OG_H // 2, OG_W // 2 + OG_W, OG_H // 2 + OG_H))
    glow = Image.new("L", (OG_W, OG_H), 0)
    ImageDraw.Draw(glow).ellipse([OG_W * 0.55, -OG_H * 0.6, OG_W * 1.35, OG_H * 0.55], fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    im = Image.composite(Image.new("RGB", im.size, mix(c, (255, 255, 255), 0.92)), im, glow)
    noise = Image.effect_noise((OG_W, OG_H), 18).convert("RGB")
    return Image.blend(im, noise, 0.035)


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def paste_card(canvas, card, xy, angle=0, shadow=60, blur=28, offset=18):
    """Paste an RGBA card with a soft drop shadow, optionally rotated."""
    from PIL import ImageFilter
    pad = blur * 3
    sh = Image.new("RGBA", (card.size[0] + pad * 2, card.size[1] + pad * 2), (0, 0, 0, 0))
    a = card.split()[3].point(lambda v: v * shadow // 100)
    sh.paste((0, 0, 0, 255), (pad, pad + offset), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    layer.alpha_composite(sh)
    layer.alpha_composite(card, (pad, pad))
    if angle:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = xy
    canvas.alpha_composite(layer, (int(x - layer.size[0] / 2), int(y - layer.size[1] / 2)))


def wrap(d, text, font, width, max_lines=3):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if d.textlength((cur + " " + w).strip(), font=font) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines[:max_lines]


def og_footer(d, color):
    d.text((80, OG_H - 78), "kynossstudios.com", font=text_font(26, 600), fill=color)


def og_app(dest, app):
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = og_backdrop(app["accent"]).convert("RGBA")
    adir = ROOT / "assets" / "apps" / app["id"]
    shots = [adir / f"shot-{i}.webp" for i in (1, 2)]
    shots = [p for p in shots if p.exists()]
    if shots:  # a fan of real screens on the right, cropped by the bottom edge
        for p, x, y, ang, k in reversed([(shots[0], 905, 470, 0, 1.0)] + ([(shots[1], 1085, 520, -9, 0.9)] if len(shots) > 1 else [])):
            s = Image.open(p).convert("RGB")
            w = int(300 * k)
            s = s.resize((w, int(s.size[1] * w / s.size[0])), Image.LANCZOS)
            if k < 1:
                s = Image.blend(s, Image.new("RGB", s.size, (0, 0, 0)), 0.18)
            paste_card(im, rounded(s, 34), (x, y), ang, shadow=70)
    else:  # upcoming: the icon carries the image
        ic = Image.open(adir / "icon-1024.png").convert("RGBA").resize((340, 340), Image.LANCZOS)
        paste_card(im, rounded(ic, 76), (930, 315), 6, shadow=80, blur=40, offset=30)
    left = 80
    if shots:
        ic = Image.open(adir / "icon-1024.png").convert("RGBA").resize((132, 132), Image.LANCZOS)
        paste_card(im, rounded(ic, 30), (left + 66, 150), 0, shadow=55, blur=18, offset=10)
    im = im.convert("RGB")  # ImageDraw only blends translucent fills onto RGB
    d = ImageDraw.Draw(im, "RGBA")
    name_font = og_font(124 if len(app["name"]) <= 8 else 104)
    y = 250 if shots else 190
    d.text((left - 4, y), app["name"], font=name_font, fill="white")
    sub = text_font(36, 500)
    for i, line in enumerate(wrap(d, app["tagline"], sub, 600 if shots else 560, 3)):
        d.text((left, y + 150 + i * 46), line, font=sub, fill=(255, 255, 255, 222))
    if app["status"] != "live":
        d.rounded_rectangle([left, y - 56, left + 186, y - 14], radius=21, fill=(255, 255, 255, 40), outline=(255, 255, 255, 90), width=2)
        d.text((left + 20, y - 49), "Coming soon", font=text_font(24, 600), fill="white")
    og_footer(d, (255, 255, 255, 200))
    im.convert("RGB").save(dest, "PNG", optimize=True)


def og_page(dest, title, subtitle, accent="#2B54E0", wall=None, apps=None):
    """Studio-level previews: deep ink with the brand mark, or a wall of real screens."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    c = hex_rgb(accent)
    im = og_backdrop(accent if accent != "#2B54E0" else "#1E3A9E").convert("RGBA")
    if wall:  # tilted wall of screenshots on the right, like the home page
        tile_w, gap = 190, 22
        layer = Image.new("RGBA", (4 * (tile_w + gap), 1500), (0, 0, 0, 0))
        for ci, col in enumerate(wall[:4]):
            yy = -160 if ci % 2 else 0
            for p in col:
                s = Image.open(ROOT / p.lstrip("/")).convert("RGB")
                s = s.resize((tile_w, int(s.size[1] * tile_w / s.size[0])), Image.LANCZOS)
                layer.alpha_composite(rounded(s, 22), (ci * (tile_w + gap), yy))
                yy += s.size[1] + gap
                if yy > 1500:
                    break
        layer = layer.rotate(10, resample=Image.BICUBIC, expand=True)
        from PIL import ImageFilter
        fade = Image.new("L", (OG_W, OG_H), 0)
        fd = ImageDraw.Draw(fade)
        for x in range(OG_W):
            fd.line([(x, 0), (x, OG_H)], fill=max(0, min(255, int((x - 560) * 255 / 180))))
        placed = Image.new("RGBA", (OG_W, OG_H), (0, 0, 0, 0))
        placed.alpha_composite(layer, (600, -int(layer.size[1] * 0.3)))
        placed.putalpha(Image.composite(placed.split()[3], Image.new("L", (OG_W, OG_H), 0), fade))
        im.alpha_composite(placed)
    elif apps:  # a loose cluster of app icons
        for i, (p, x, y, ang, sz) in enumerate(apps):
            ic = Image.open(p).convert("RGBA").resize((sz, sz), Image.LANCZOS)
            paste_card(im, rounded(ic, int(sz * 0.224)), (x, y), ang, shadow=70, blur=22, offset=14)
    im = im.convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    # the studio mark: 3x3 rounded squares, centre one in signal blue
    for r in range(3):
        for col in range(3):
            x0, y0 = 80 + col * 22, 80 + r * 22
            d.rounded_rectangle([x0, y0, x0 + 17, y0 + 17], radius=5, fill=(91, 131, 255) if (r, col) == (1, 1) else (255, 255, 255))
    d.text((160, 86), "Kynoss Studios", font=og_font(40, 650, 88), fill="white")
    size = 104 if len(title) <= 14 else 84
    big = og_font(size)
    lh = int(size * 0.98)
    lines = wrap(d, title, big, 540 if (wall or apps) else 1000, 3)
    sub = text_font(32, 500)
    sublines = wrap(d, subtitle, sub, 520 if (wall or apps) else 900, 3)
    block = len(lines) * lh + 28 + len(sublines) * 42
    y = 160 + (OG_H - 160 - 110 - block) // 2  # centred between the mark and the footer
    for i, line in enumerate(lines):
        d.text((76, y + i * lh), line, font=big, fill="white")
    for i, line in enumerate(sublines):
        d.text((80, y + len(lines) * lh + 28 + i * 42), line, font=sub, fill=(255, 255, 255, 215))
    og_footer(d, (255, 255, 255, 190))
    im.convert("RGB").save(dest, "PNG", optimize=True)


# ---------------------------------------------------------------- favicon

def favicons():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#172033"/>'
           '<g fill="#F5F7FA">' + "".join(
               f'<rect x="{5 + c * 8}" y="{5 + r * 8}" width="6" height="6" rx="1.6"{" fill=%s" % chr(34) + "#5B83FF" + chr(34) if (r, c) == (1, 1) else ""}/>'
               for r in range(3) for c in range(3)) + "</g></svg>")
    (ROOT / "favicon.svg").write_text(svg)
    for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png")):
        s = size * 4
        im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if name.startswith("apple"):
            d.rectangle([0, 0, s, s], fill="#172033")
        else:
            d.rounded_rectangle([0, 0, s - 1, s - 1], radius=s // 4, fill="#172033")
        u = s / 32
        for r in range(3):
            for c in range(3):
                x0, y0 = (5 + c * 8) * u, (5 + r * 8) * u
                d.rounded_rectangle([x0, y0, x0 + 6 * u, y0 + 6 * u], radius=1.6 * u,
                                    fill="#5B83FF" if (r, c) == (1, 1) else "#F5F7FA")
        im.resize((size, size), Image.LANCZOS).save(ROOT / name, "PNG", optimize=True)


# ---------------------------------------------------------------- legacy chrome

MARK_HEAD = ("<!-- ks:head -->", "<!-- /ks:head -->")
MARK_TOP = ("<!-- ks:top -->", "<!-- /ks:top -->")
MARK_BOTTOM = ("<!-- ks:bottom -->", "<!-- /ks:bottom -->")


def strip_marked(s, marks):
    return re.sub(re.escape(marks[0]) + r".*?" + re.escape(marks[1]) + r"\n?", "", s, flags=re.S)


def wrap_legacy(path, head_html, top_html, bottom_html, app_id, accent):
    s = path.read_text(encoding="utf-8")
    for m in (MARK_HEAD, MARK_TOP, MARK_BOTTOM):
        s = strip_marked(s, m)
    s = s.replace("https://sknauss7.github.io/KynossStudiosSupport/", "/")
    # drop meta tags the shared head supplies, so pages don't carry two
    s = re.sub(r'\s*<meta name="description"[^>]*>', "", s) if 'name="description"' in head_html else s
    s = re.sub(r'(<body\b[^>]*?)\s+class="ks-legacy"', r"\1", s)
    s = re.sub(r"<body\b([^>]*)>", r'<body\1 class="ks-legacy">', s, count=1)
    css = s.split("</style>")[0] if "</style>" in s else ""
    bw = re.search(r"(?:^|[\s}])body\s*\{[^}]*?max-width:\s*([^;}]+)", css)
    main_cls = "ks-legacy-main ks-appscope" + (" is-narrow" if bw else "")
    style = f"--app: {accent}" + (f"; --legacy-width: {bw.group(1).strip()}" if bw else "")
    main_style = f' data-page="{path.stem.split(".")[0]}" data-app="{app_id}" style="{style}"'
    s = s.replace("</head>", f"{MARK_HEAD[0]}\n{head_html}\n{MARK_HEAD[1]}\n</head>", 1)
    s = re.sub(r'(<body\b[^>]*>)', lambda m: f"{m.group(1)}\n{MARK_TOP[0]}\n{top_html}\n<div class=\"{main_cls}\"{main_style}>\n{MARK_TOP[1]}", s, count=1)
    i = s.rfind("</body>")
    s = s[:i] + f"{MARK_BOTTOM[0]}\n</div>\n{bottom_html}\n{MARK_BOTTOM[1]}\n" + s[i:]
    path.write_text(s, encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    site = json.loads((BUILD / "site.json").read_text())
    # "unlisted" apps (not yet announced) get no page, tile or catalog row
    site["apps"] = [a for a in site["apps"] if a["status"] in ("live", "upcoming")]
    flows_path = BUILD / "flows.json"
    flows = json.loads(flows_path.read_text()) if flows_path.exists() else {"checked": "", "apps": {}}
    now = dt.datetime.now()
    site["year"] = now.year
    import hashlib  # cache-buster changes only when the shared CSS/JS does, so unchanged pages stay unchanged
    site["build_id"] = hashlib.sha1(b"".join((ROOT / "assets" / f).read_bytes() for f in ("site.css", "site.js"))).hexdigest()[:10]
    site["flows_checked"] = flows.get("checked", "")
    cats = {c["id"]: c["name"] for c in site["categories"]}
    global ALL_NAMES
    ALL_NAMES = [a["name"] for a in site["apps"]] + ["Kynoss"]

    for a in site["apps"]:
        aid = a["id"]
        adir = ROOT / "assets" / "apps" / aid
        a["category_name"] = cats[a["category"]]
        copy = appstore.copy(a["name"])
        a.setdefault("tagline", copy["subtitle"] or a["kind"])
        a["shots"], a["version"], a["updated"], a["rating"], a["min_ios"], a["genre"] = [], "", "", None, "", ""
        a["shots_s"] = []
        a["whats_new_html"] = ""
        f = flows.get("apps", {}).get(aid, {})
        a["flows"] = [{"icon": FLOW_ICONS.get(x["kind"], "out"), "text": x["text"]} for x in f.get("flows", [])]
        a["permissions"] = f.get("permissions", "")
        if a["status"] == "live":
            r = lookup(a["store_id"])
            a["store_url"] = f"https://apps.apple.com/us/app/id{a['store_id']}"
            art = r["artworkUrl512"].rsplit("/", 1)[0]
            save_image(f"{art}/512x512bb.png", adir / "icon.webp", size=256)
            save_image(f"{art}/1024x1024bb.png", adir / "icon-1024.png", fmt="PNG")
            a["shots_s"] = []
            for i, u in enumerate(r.get("screenshotUrls", [])[:6], 1):
                base = u.rsplit("/", 1)[0]
                save_image(base + "/600x0w.webp", adir / f"shot-{i}.webp", quality=80)
                save_image(base + "/300x0w.webp", adir / f"shot-{i}-s.webp", quality=78)
                a["shots"].append(f"/assets/apps/{aid}/shot-{i}.webp")
                a["shots_s"].append(f"/assets/apps/{aid}/shot-{i}-s.webp")
            keep = {p.rsplit("/", 1)[1] for p in a["shots"] + a["shots_s"]}
            for old in sorted(adir.glob("shot-*.webp")):
                if old.name not in keep:
                    old.unlink()
            a["version"] = r.get("version", "")
            a["updated"] = month_day_year(r["currentVersionReleaseDate"]) if r.get("currentVersionReleaseDate") else ""
            a["min_ios"] = r.get("minimumOsVersion", "").removesuffix(".0")
            a["genre"] = r.get("primaryGenreName", "")
            if (r.get("userRatingCount") or 0) >= 5:
                a["rating"] = f"{r['averageUserRating']:.1f}"
                a["rating_count"] = r["userRatingCount"]
            desc = r.get("description") or copy["description"]
            a["whats_new_html"] = text_to_html(r.get("releaseNotes", ""), ALL_NAMES) if r.get("releaseNotes") else ""
            qr = segno.make(a["store_url"], error="m")
            buf = io.BytesIO()
            qr.save(buf, kind="svg", xmldecl=False, svgns=True, border=0, dark="#172033", light=None, omitsize=True)
            a["qr_svg"] = re.sub(r'\s(width|height)="[^"]*"', "", buf.getvalue().decode(), count=2)
        else:
            src = WORKSHOP / a["icon_src"]
            save_image(src, adir / "icon.webp", size=256)
            save_image(src, adir / "icon-1024.png", fmt="PNG")
            desc = copy["description"]
            a["store_url"] = ""
        a["icon"] = f"/assets/apps/{aid}/icon.webp"
        a["icon_1024"] = f"/assets/apps/{aid}/icon-1024.png"
        a["description_html"] = text_to_html(drop_privacy_claims(desc), ALL_NAMES)
        a["locale_links"] = [{"href": f"/{aid}-support.{loc}.html", "code": loc, "label": f"Help in {LOCALE_NAMES.get(loc, loc)}"}
                             for loc in a.get("locales", []) if (ROOT / f"{aid}-support.{loc}.html").exists()]
        support = ROOT / f"{aid}-support.html"
        a["faq"] = extract_faq(support.read_text(encoding="utf-8")) if support.exists() else []

    site["live"] = [a for a in site["apps"] if a["status"] == "live"]
    site["upcoming"] = [a for a in site["apps"] if a["status"] == "upcoming"]
    pool = [a["shots_s"][k] for k in range(3) for a in site["live"] if len(a["shots_s"]) > k]
    site["wall"] = [pool[c::4] for c in range(4)]
    site["by_cat"] = {c["id"]: [a for a in site["apps"] if a["category"] == c["id"]] for c in site["categories"]}
    for a in site["apps"]:
        peers = [b for b in site["by_cat"][a["category"]] if b["id"] != a["id"] and b["status"] == "live"]
        if len(peers) < 3:
            peers += [b for b in site["live"] if b["id"] != a["id"] and b not in peers][: 3 - len(peers)]
        a["related"] = peers[:4]

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(BUILD / "templates"), autoescape=True,
                             trim_blocks=False, lstrip_blocks=False)

    def render(template, out, page, **extra):
        html_out = env.get_template(template).render(site=site, page=page, **extra)
        dest = ROOT / out
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")

    og = ROOT / "assets" / "og"
    og_page(og / "studio.png", "Small iPhone apps that do one job well.", "No ads, no accounts, no tracking.", wall=site["wall"])
    stats = build_stats()
    pages = []

    def page(path, title, description, nav="", crumbs=None, og_image_path=None, **kw):
        p = {"path": path, "title": title, "description": description, "nav": nav, "crumbs": crumbs, "og_image": og_image_path}
        p.update(kw)
        pages.append(p)
        return p

    render("home.html", "index.html", page("/", "Kynoss Studios: small iPhone apps that do one job well",
           f"An independent iPhone app studio in Florida. {len(site['live'])} apps on the App Store: daily games, money tools and home organizers, with no ads, accounts or tracking."))
    render("apps.html", "apps/index.html", page("/apps/", "Apps · Kynoss Studios",
           "Every Kynoss Studios app for iPhone, grouped by category, with prices, help and privacy policies.", nav="apps"))

    hub = {a["id"]: {"name": a["name"], "kind": a["kind"], "icon": a["icon"], "support": f"/{a['id']}-support.html",
                     "privacy": f"/{a['id']}-privacy.html", "faq": [{"q": q, "a": ans} for q, ans in a["faq"][:6]]}
           for a in site["live"]}
    render("support.html", "support/index.html", page("/support/", "Get help with an app · Kynoss Studios",
           "Common answers for every Kynoss Studios app, and a quick way to email support with the details filled in.", nav="support"),
           hub_json=json.dumps(hub).replace("</", "<\\/"))

    icons = [ROOT / "assets" / "apps" / a["id"] / "icon-1024.png" for a in site["live"]]
    spots = [(840, 170, -8, 150), (1030, 250, 7, 130), (870, 390, 5, 170), (1070, 470, -6, 140), (700, 470, -4, 110)]
    og_page(og / "how-we-build.png", "How we build", "One developer and Claude: from written instructions to the App Store.",
            apps=[(icons[i * 3 % len(icons)], *xy) for i, xy in enumerate(spots)])
    render("how.html", "how-we-build/index.html", page("/how-we-build/", "How we build · Kynoss Studios",
           "Kynoss Studios is one developer and Claude. How work moves from written instructions to the App Store, and what keeps it honest.",
           nav="build", og_image_path="/assets/og/how-we-build.png"), stats=stats)
    og_page(og / "hoa.png", "For condo and HOA boards", "A concept: deadlines kept, answers cited from your documents, paperwork drafted.", accent="#2E9C6A")
    render("hoa.html", "hoa/index.html", page("/hoa/", "An assistant for condo and HOA boards · Kynoss Studios",
           "A concept from Kynoss Studios: an assistant for volunteer condo and HOA boards that tracks deadlines, cites governing documents and drafts meeting paperwork.",
           nav="hoa", og_image_path="/assets/og/hoa.png"))
    render("about.html", "about/index.html", page("/about/", "About · Kynoss Studios",
           f"Kynoss Studios LLC is an independent iPhone app studio in Florida, founded in {site['studio']['founded']}.", nav="about"))
    render("privacy.html", "privacy/index.html", page("/privacy/", "Privacy across our apps · Kynoss Studios",
           "How every Kynoss Studios app handles your data: what stays on your iPhone, what syncs through your iCloud, and what is sent anywhere else."))
    render("press.html", "press/index.html", page("/press/", "Press kit · Kynoss Studios",
           "Icons, screenshots and descriptions for every Kynoss Studios app."))
    apps_404 = [{"id": a["id"], "name": a["name"], "url": f"/{a['id']}/", "support": f"/{a['id']}-support.html",
                 "privacy": f"/{a['id']}-privacy.html"} for a in site["live"] + site["upcoming"]]
    p404 = page("/404.html", "Page not found · Kynoss Studios", "This page doesn't exist.")
    render("404.html", "404.html", p404, apps_json=json.dumps(apps_404))
    pages.remove(p404)

    for a in site["apps"]:
        og_app(og / f"{a['id']}.png", a)
        title = f"{a['name']}: {a['tagline']}" if a["status"] == "live" else f"{a['name']} (coming soon)"
        desc = a["blurb"] + ("" if a["status"] == "live" else " Coming soon to the App Store.")
        render("app.html", f"{a['id']}/index.html",
               page(f"/{a['id']}/", f"{title} · Kynoss Studios", desc, nav="apps",
                    crumbs=[("/", "Home"), ("/apps/", "Apps"), (f"/apps/?category={a['category']}", a["category_name"]), (None, a["name"])],
                    og_image_path=f"/assets/og/{a['id']}.png", store_id=a.get("store_id") if a["status"] == "live" else None,
                    style=f"--app: {a['accent']}"), app=a)

    # ---- legacy support/privacy pages: shared chrome
    chrome = env.from_string('{% from "_chrome.html" import bar, crumbs, foot, head_common, appband %}'
                             '{% if part == "head" %}{{ head_common(site, page) }}'
                             '<meta name="description" content="{{ page.description }}">'
                             '<style>.ks-legacy-main > .container, .ks-legacy-main > .wrap { margin-top: 0; }</style>'
                             '{% elif part == "top" %}{{ bar("support" if kind == "support" else "") }}{{ appband(app, tabs, label, page.crumbs) }}'
                             '{% if kind == "privacy" and not loc %}<p class="ks-stance">Kynoss Studios is built to know as little about you as possible: no accounts, no ads, no third-party trackers, and we never sell your data or share it with advertisers. <a href="/privacy/">Compare every app</a></p>{% endif %}'
                             '{% else %}{{ foot(site) }}{% endif %}')
    for a in site["apps"]:
        variants = [("", None)] + [(f".{loc}", loc) for loc in a.get("locales", [])]
        for kind in ("support", "privacy"):
            for suffix, loc in variants:
                f = ROOT / f"{a['id']}-{kind}{suffix}.html"
                if not f.exists():
                    continue
                label = "Help" if kind == "support" else "Privacy policy"
                if loc:
                    label += f" ({LOCALE_NAMES.get(loc, loc)})"
                desc = (f"Help and answers for {a['name']}, {a['kind'].lower()} for iPhone by Kynoss Studios." if kind == "support"
                        else f"How {a['name']} handles your data: what stays on your iPhone and what, if anything, is sent elsewhere.")
                pg = {"path": f"/{f.name}", "title": "", "description": desc, "og_image": f"/assets/og/{a['id']}.png",
                      "og_title": f"{a['name']} {label.lower()}", "store_id": a.get("store_id") if a["status"] == "live" else None,
                      "crumbs": [("/", "Home"), ("/apps/", "Apps"), (f"/{a['id']}/", a["name"]), (None, label)]}
                def tab(k):  # same-language page when it exists, else the English one
                    return f"/{a['id']}-{k}{suffix}.html" if (ROOT / f"{a['id']}-{k}{suffix}.html").exists() else f"/{a['id']}-{k}.html"
                tabs = [(f"/{a['id']}/", "Overview", False), (tab("support"), "Help", kind == "support"),
                        (tab("privacy"), "Privacy", kind == "privacy")]
                parts = {p: chrome.render(site=site, page=pg, part=p, kind=kind, loc=loc, app=a, tabs=tabs, label=label)
                         for p in ("head", "top", "bottom")}
                wrap_legacy(f, parts["head"], parts["top"], parts["bottom"], a["id"], a["accent"])
                if not loc and a["status"] == "live":
                    pages.append({"path": pg["path"]})

    # ---- redirects for old URLs still referenced by past App Store versions
    stub = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>Moved · Kynoss Studios</title>\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="robots" content="noindex">\n'
            '<link rel="canonical" href="{u}">\n<meta http-equiv="refresh" content="0; url={u}">\n'
            '<script>location.replace("{u}");</script>\n</head>\n<body><p>This page has moved to <a href="{u}">{u}</a>.</p></body>\n</html>\n')
    redirects = {"substrata-marketing.html": "/substrata/"}
    redirects.update({f"substrata-marketing.{loc}.html": "/substrata/" for loc in LOCALE_NAMES})
    for path, target in redirects.items():
        (ROOT / path).write_text(stub.format(u=site["studio"]["domain"] + target), encoding="utf-8")

    # ---- search index
    idx = [{"t": a["name"], "d": a["kind"] + ". " + a["blurb"], "u": f"/{a['id']}/", "k": "app", "i": a["icon"]} for a in site["apps"]]
    for a in site["live"]:
        idx.append({"t": f"{a['name']} help", "d": "Support page and FAQ", "u": f"/{a['id']}-support.html", "k": "page", "i": a["icon"]})
        idx.append({"t": f"{a['name']} privacy policy", "d": "What the app does with your data", "u": f"/{a['id']}-privacy.html", "k": "page", "i": a["icon"]})
        for q, ans in a["faq"]:
            idx.append({"t": q, "d": ans[:140], "a": a["name"], "u": f"/{a['id']}-support.html", "k": "faq"})
    for path, t, d in (("/support/", "Get help with an app", "Support for every app"), ("/how-we-build/", "How we build", "One developer and Claude"),
                       ("/hoa/", "HOA and condo boards", "Board assistant concept"), ("/about/", "About Kynoss Studios", "Company, contact"),
                       ("/privacy/", "Privacy across our apps", "What each app sends"), ("/press/", "Press kit", "Icons, screenshots, contact"),
                       ("/shortfall-doc-fees-by-state.html", "Dealer doc fees by state", "Shortfall's state-by-state doc fee guide"),
                       ("/support/#billing", "Refunds, cancellations and billing", "Refund, cancel subscription, restore purchase: handled by Apple")):
        idx.append({"t": t, "d": d, "u": path, "k": "page"})
    (ROOT / "search-index.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))

    # ---- sitemap + robots
    today = now.strftime("%Y-%m-%d")
    urls = [p["path"] for p in pages] + ["/shortfall-doc-fees-by-state.html"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{site['studio']['domain']}{u}</loc><lastmod>{today}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site['studio']['domain']}/sitemap.xml\n")

    favicons()
    print(f"built {len(pages)} indexed pages, {len(idx)} search entries; "
          f"{sum(len(a['shots']) for a in site['apps'])} screenshots; stats {stats}")


if __name__ == "__main__":
    main()

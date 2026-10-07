"""Extract customer-facing App Store copy from an app's APP-STORE.md."""
import re
from pathlib import Path

WORKSHOP = Path.home() / "AgentWorkshop"


def appstore_md(app):
    for p in (WORKSHOP / app / "docs" / "APP-STORE.md", WORKSHOP / app / "APP-STORE.md"):
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def section(md, names, platform_skip=("tvos",)):
    """Body of the first ### heading whose title starts with one of names."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{2,4})\s+(.*)$", line)
        if not m:
            continue
        title = m.group(2).strip().lower()
        if not any(title.startswith(n.lower()) for n in names):
            continue
        if any(s in title for s in platform_skip):
            continue
        level = len(m.group(1))
        body = []
        for nxt in lines[i + 1:]:
            h = re.match(r"^(#{1,4})\s", nxt)
            if h and len(h.group(1)) <= level:
                break
            body.append(nxt)
        text = "\n".join(body)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        text = re.sub(r"^```\w*\s*$", "", text, flags=re.M)
        text = re.sub(r"^>\s?", "", text, flags=re.M)
        text = "\n".join(l for l in text.splitlines() if not re.match(r"^\s*(\*\*?(Character|Chars|Count)|\(\d+ char|---\s*$)", l, re.I))
        return text.strip()
    return ""


def copy(app):
    md = appstore_md(app)
    return {
        "subtitle": section(md, ["Subtitle"]).splitlines()[0].strip("` *") if section(md, ["Subtitle"]) else "",
        "promo": section(md, ["Promotional Text"]),
        "description": section(md, ["Description"]),
        "whats_new": section(md, ["What's New — iOS", "What's New", "Whats New"]),
    }


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        c = copy(a)
        print(f"===== {a}: subtitle={c['subtitle']!r}")
        print("promo:", c["promo"][:160].replace("\n", " "))
        print("desc:", len(c["description"]), "chars |", c["description"][:200].replace("\n", " / "))
        print("new:", c["whats_new"][:160].replace("\n", " / "))

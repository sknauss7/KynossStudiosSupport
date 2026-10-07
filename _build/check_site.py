#!/usr/bin/env python3
"""Check kynossstudios.com against what actually ships.

    python3 _build/check_site.py          # registry, prices, privacy phrases
    python3 _build/check_site.py --live   # also fetch every support/privacy URL on kynossstudios.com

Exits 1 on any failure. Run it after any release that changes prices, data
flows or an app's status, and before pushing the site.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent
WORKSHOP = Path.home() / "AgentWorkshop"
APP_DIRS = {"homebaseai": "HomeBaseAI"}
# Phrases that are false for any app that sends data off the device.
NO_SERVER = re.compile(r"no servers|nothing is sent to any server|without sending data anywhere|"
                       r"never leaves your (device|iphone)|all ai processing happens entirely on your iphone|"
                       r"we have no servers|we don't have any", re.I)

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL", msg)


def storekit_prices(app_dir):
    prices = set()
    for f in app_dir.rglob("*.storekit"):
        if any(p in f.parts for p in ("build", "DerivedData")):
            continue
        d = json.loads(f.read_text())
        items = d.get("products", []) + d.get("nonRenewingSubscriptions", [])
        items += [s for g in d.get("subscriptionGroups", []) for s in g["subscriptions"]]
        for p in items:
            if "legacy" not in p.get("referenceName", "").lower():
                prices.add(f"{float(p['displayPrice']):.2f}")
    return prices


def lookup(store_id):
    with urllib.request.urlopen(f"https://itunes.apple.com/lookup?id={store_id}&country=us", timeout=30) as r:
        res = json.load(r).get("results", [])
    return res[0] if res else None


def main():
    site = json.loads((BUILD / "site.json").read_text())
    flows = json.loads((BUILD / "flows.json").read_text()) if (BUILD / "flows.json").exists() else {"apps": {}}

    # 1. status matches the App Store
    cfg = json.loads((WORKSHOP / "scripts" / "asc_config.json").read_text())["apps"]
    listed = {a["name"]: a for a in site["apps"]}
    for name, store_id in cfg.items():
        live = lookup(store_id) is not None
        a = listed.get(name)
        if live and (not a or a["status"] != "live"):
            fail(f"{name} is on the App Store but not listed as live in site.json")
        if a and a["status"] == "live" and not live:
            fail(f"{name} is listed as live but isn't on the App Store")
    for a in site["apps"]:
        if a["status"] == "live" and a.get("store_id") not in cfg.values():
            fail(f"{a['name']} store_id {a.get('store_id')} not in asc_config.json")

    # 2. every quoted price exists in the app's StoreKit config
    for a in site["apps"]:
        app_dir = WORKSHOP / APP_DIRS.get(a["id"], a["name"])
        known = storekit_prices(app_dir)
        if not known:
            print(f"skip  {a['name']}: no .storekit found")
            continue
        texts = {"site.json price": a["price"]}
        for kind in ("support", "privacy"):
            f = ROOT / f"{a['id']}-{kind}.html"
            if f.exists():
                texts[f.name] = re.sub(r"<[^>]+>", " ", f.read_text(encoding="utf-8"))
        for where, text in texts.items():
            for p in re.findall(r"\$(\d+\.\d{2})\b", text):
                if f"{float(p):.2f}" not in known:
                    fail(f"{a['name']}: ${p} in {where} isn't a current StoreKit price ({', '.join(sorted(known))})")

    # 3. apps that send data off the device must not claim they don't
    for a in site["apps"]:
        f = flows.get("apps", {}).get(a["id"], {})
        sends = any(x["kind"] in ("relay", "byok", "other") for x in f.get("flows", []))
        if not sends:
            continue
        for kind in ("support", "privacy"):
            page = ROOT / f"{a['id']}-{kind}.html"
            if page.exists():
                text = re.sub(r"<[^>]+>", " ", page.read_text(encoding="utf-8"))
                for m in NO_SERVER.finditer(text):
                    fail(f"{a['name']} {kind}: says \"{m.group(0)}\" but the app sends data off the device")

    # 4. optional: live URLs the App Store listings point at
    if "--live" in sys.argv:
        for a in site["apps"]:
            if a["status"] != "live":
                continue
            for path in (f"/{a['id']}-support.html", f"/{a['id']}-privacy.html", f"/{a['id']}/"):
                try:
                    with urllib.request.urlopen(site["studio"]["domain"] + path, timeout=30) as r:
                        if r.status != 200:
                            fail(f"{path} returned {r.status}")
                except Exception as e:
                    fail(f"{path}: {e}")

    print(f"{'FAILED' if failures else 'OK'}: {len(failures)} problem(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

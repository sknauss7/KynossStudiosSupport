# Who owns what on kynossstudios.com

Decided by Steven, 2026-10-12. Kynoss owns the site as a whole. AgentWorkshop owns the app pages and app content. Systems owns the /systems/ page and its content. The full plan is in the Kynoss workspace, `docs/ops/website.md`.

This repo is **public** and **a push to `main` is the deploy** (GitHub Pages, custom domain via `CNAME`).

## Owners by source path
There is one build: any edit regenerates shared outputs (`sitemap.xml`, `search-index.json`, the catalog and home page). So ownership is by **source** file. Whoever's change regenerates a shared output pushes it.

| Owner | Source paths |
|---|---|
| **Kynoss** (shared site) | `index.html`, `about/`, `how-we-build/`, `press/`, `privacy/` (company), `support/` (hub), `apps/` (catalog page), `404.html`, `hoa/`; `sitemap.xml`, `robots.txt`, `search-index.json`, the IndexNow key file, `CNAME`, favicons, `apple-touch-icon.png`; `assets/site.css`, `assets/site.js`, `assets/brand/`, `assets/fonts/`, site-level images in `assets/og/`; templates `base`, `_chrome`, `_icons`, `home`, `about`, `how`, `press`, `privacy`, `support`, `apps`, `404`; the `studio` and `categories` keys in `site.json`; `build.py`, `check_site.py`, this file; the field guide's rendering: `guide.py`, templates `guide` and `guide_index`, `assets/guide.css`; the shared chrome between `<!-- ks:* -->` markers on every page |
| **AgentWorkshop** (apps) | `<app>/` folders; root `<app>-support.html` and `<app>-privacy.html`; `substrata-*.{locale}.html`; `shortfall-doc-fees-by-state.html`; the `apps` and `retired` keys in `site.json`; `flows.json`; `appstore.py`; `assets/apps/`; templates `app.html` and `_catalog.html`; everything on its pages outside the `ks:*` markers |
| **AgentWorkshop** (field guide words) | `_build/guide/<slug>.md`, published pages only (front matter and format in `guide.py`). Drafts and `Source:` notes stay in AgentWorkshop's private repo, because this repo is public |
| **Systems** | `_build/systems.json`, `templates/systems.html`, `assets/systems.css`, `systems/`, `assets/og/systems.png` |

A change one owner needs in another owner's paths goes to that owner as an ask.

## Rules for every writer
1. **Don't rename or move the repo, change the Pages source or `CNAME`, or rename root files.** App Store support and privacy URLs point at them, and older listings use `sknauss7.github.io/KynossStudiosSupport/…`.
2. **Rebase on `origin/main` before every push**, because there are several writers, including AgentWorkshop's automatic App Store refresh.
3. **`python3 _build/check_site.py` must pass** before pushing. It also checks app privacy wording against `flows.json`.
4. **No secrets, ever.** The repo is public. The IndexNow key file is public by design.
5. `sknauss7.github.io` (Rusti's universal links) is a separate repo, owned by AgentWorkshop, and **must never get a custom domain**.
6. Pushes by Kynoss, and by Systems, need Steven's yes each time.

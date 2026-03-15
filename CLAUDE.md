# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development

```bash
# Sync from Obsidian vault + local dev server
make serve VAULT=/path/to/vault

# Sync only
make sync VAULT=/path/to/vault

# Production build
make publish VAULT=/path/to/vault

# Hugo only (no sync)
hugo server
hugo --gc --minify --baseURL "https://envoss11.github.io/"
```

Requires Hugo Extended v0.152.2+ and Dart Sass. Python 3.9+ for the sync script (standard library only). No Node.js or Ruby dependencies.

Deployment is automatic via GitHub Actions (`.github/workflows/hugo.yaml`) on push to `main`.

## Architecture

Hugo static site with **custom project-level templates** (no external theme). Designed as a scrollable commentary feed — short-form posts rendered inline on the homepage so readers never need to click into individual posts.

**Design approach:** Warm, journal-style aesthetic. Cream background (`#FBF8F3`), terracotta accents (`#B05E3B`), Source Serif 4 body font, Inter for headings/UI. Single-column layout, max-width 680px.

**Configuration:** Single `config.yaml` with taxonomies, menu (About only), params (including `tagline`), privacy, and services. No theme reference.

**Templates:**
- `layouts/_default/baseof.html` — base HTML shell
- `layouts/index.html` — homepage feed, iterates posts sorted by date descending
- `layouts/_default/single.html` — standalone post page for permalinks/RSS
- `layouts/_default/list.html` — fallback for taxonomy pages
- `layouts/partials/head.html` — meta tags, Google Fonts, CSS, RSS autodiscovery
- `layouts/partials/header.html` — site name, tagline, About nav, LinkedIn icon
- `layouts/partials/footer.html` — copyright + RSS link
- `layouts/partials/feed-card.html` — post rendered as an inline card with source callout, full content, date, and categories
- `layouts/partials/source-callout.html` — "Commenting on:" block for commentary posts (uses `source` frontmatter URL + `.Title` for display text)
- `layouts/shortcodes/blogdown/postref.html` — R Markdown cross-references

**Content structure:**
- `/content/posts/` — blog posts as page bundles (`slug/index.md`)
- `/content/about.md` — About Me page (url: `/about/`)

**Frontmatter format:** Posts use YAML frontmatter (`---` delimiters) with title, date, categories, tags, and draft fields. Commentary posts add a `source` field (URL of the article being commented on). The `title` field serves as the display text in the source callout.

**Obsidian sync pipeline:** `sync_obsidian.py` walks an Obsidian vault for notes with `publish: true`, transforms frontmatter (maps `title`, `domain` → `categories`, `tags`, `author`, `source`, `description`/`summary`), strips `[[wikilinks]]`, truncates at `<!-- end-publish -->`, and outputs Hugo page bundles. Dates are **not** pulled from Obsidian — the script stamps today's date on first sync and preserves the existing date on subsequent syncs. State tracked in `.sync_state.json` (gitignored).

**Styling:** All styles in `/static/css/style.css`. No external theme CSS.

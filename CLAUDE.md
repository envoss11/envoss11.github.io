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

Hugo static site using the **PaperMod** theme (git submodule at `themes/PaperMod`). Blog-forward design — homepage shows a post feed.

**Configuration:** Single `config.yaml` with theme, taxonomies, menus, params, privacy, and services.

**Templates:** PaperMod provides base templates. Custom overrides:
- `layouts/_default/single.html` — adds "Commenting on:" block for commentary posts (shown when `source` frontmatter param exists)
- `layouts/partials/extend_head.html` — loads custom CSS
- `layouts/shortcodes/blogdown/postref.html` — R Markdown cross-references

**Content structure:**
- `/content/posts/` — blog posts as page bundles (`slug/index.md`)
- `/content/about.md` — About Me page (url: `/about/`)
- Top-level pages: `archives.md`, `search.md`

**Frontmatter format:** Posts use YAML frontmatter (`---` delimiters) with title, date, categories, tags, and draft fields. Commentary posts add a `source` field.

**Obsidian sync pipeline:** `sync_obsidian.py` walks an Obsidian vault for notes with `publish: true`, transforms frontmatter, strips `[[wikilinks]]`, truncates at `<!-- end-publish -->`, and outputs Hugo page bundles. State tracked in `.sync_state.json` (gitignored).

**Styling:** Minimal custom CSS in `/static/css/custom.css` for commentary source block styling. PaperMod handles all other styling. LinkedIn social icon configured via `params.socialIcons` in config.

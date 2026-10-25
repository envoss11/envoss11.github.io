# Working on this repo

`ericvoss.com` is a personal notebook. The notebook comes first: Markdown files
in two sections, written through a local editor app (`make notebook`). The
Jekyll site is the public view of those files. Hand-written Jekyll, no theme
gem, no JavaScript framework. The editor (`tools/notebook/`) is stdlib Python
plus one plain HTML/JS page; keep it dependency-free. Design plan:
`~/.claude/plans/` (notebook refactor, in phases; see the PR history for which
have landed).

Sections: **Reading** (one page per book, seeded from Goodreads) and
**Writing** (essays, notes, and project write-ups). `_pages/about.md` is not a
page: its body is the homepage intro, and `/about/` redirects home.

## Commands

| Target | What it does |
|---|---|
| `make notebook` | The local editor at `localhost:4100` (`tools/notebook/`) |
| `make entry SECTION=writing TITLE="..."` | Start an unpublished entry. `SECTION` is `reading` or `writing` |
| `make serve` | Preview at `localhost:4000`, unpublished entries included |
| `make build` | Production build into `_site/` |
| `make check` | Build, then html-proofer — the same gate CI runs on every PR |
| `make sync-books` | Pull the public Goodreads shelf into `_books/` (`DRY=1` to preview) |
| `make test-tools` | Unit tests for the editor server; run after changing `tools/notebook/` |

## Where things go

| | |
|---|---|
| `_books/` | Reading. `<slug>.md`, live at `/reading/<slug>/`. Body is my notes and may be empty. |
| `_writing/` | Writing. `YYYY-MM-DD-slug.md`, live at `/writing/<slug>/`, in RSS. |
| `_pages/` | `about.md` (the homepage intro), and redirect stubs for old URLs. |
| `_data/notebook.yml` | Tab order and footer links. |

## Front matter

```yaml
---
title: "Required"
published: false    # omit or true to publish
excerpt: ""         # optional; meta description and RSS summary
---
```

Books add `author`, `rating`, `date_read`, and later `goodreads_id`, `shelf`,
`cover`. A project write-up is a writing entry and may add `summary` and
`links: [{title, url}]`. There are no topics.

## Rules

- Branch and open a PR. Never push to `master`; the PR check builds the site
  and runs html-proofer.
- Do not edit a published entry unless asked. Writing already went out on the
  feed.
- Run `make check` before pushing. It works locally.

## Traps

1. **Liquid runs before Markdown, even inside code fences.** Anything quoting
   `{{` or `{%` breaks the build. Wrap it in `{% raw %}` … `{% endraw %}`.
2. **`future: false`.** A writing entry dated after the build date silently
   does not publish.
3. **html-proofer gates the deploy.** Every internal link and image must
   resolve.
4. **`exclude:` in `_config.yml` replaces Jekyll's defaults.** Adding an entry
   means keeping the existing ones.
5. **`published: false` hides an entry from the production build only.** It is
   still in git and visible under `make serve`.
6. **jekyll-feed always builds a posts feed.** It is parked at
   `/feed/posts.xml`; Writing owns `/feed.xml`. Do not use `{% feed_meta %}`.
7. **Do not name a section index's slug after a redirect stub** (`/posts/`,
   `/blog/`, ...) in `_pages/`.

## Voice

Plain and specific. Say what something is and why when it is not obvious. No
marketing register, no exclamation marks.

# Working on this repo

`ericvoss.com` is a personal landing page plus a writing feed. Two pages:
the home page and `/writing/`. Hand-written Jekyll, no theme gem, no
JavaScript. (The earlier "Commonplace" notebook version lives in git history
on `master` before this branch.)

## Commands

| Target | What it does |
|---|---|
| `make post TITLE="..."` | Start an unpublished post in `_writing/` |
| `make serve` | Preview at `localhost:4000`, unpublished posts included |
| `make build` | Production build into `_site/` |
| `make check` | Build, then html-proofer — the same gate CI runs on every PR |
| `make topo` | Redraw the contour drawing from `tools/topo.py` |

## Where things go

| | |
|---|---|
| `index.md` | The homepage intro (its body). Layout: `_layouts/home.html`. |
| `_writing/` | Posts. `YYYY-MM-DD-slug.md`, live at `/writing/<slug>/`, in `/feed.xml`. |
| `writing.html` | The writing index. |
| `_data/links.yml` | X, LinkedIn, GitHub: homepage and footer. |
| `_includes/topo.svg` | The contour drawing behind every page: a three-component Gaussian mixture, dots at the means. Written by `make topo` from `tools/topo.py`; change the components there, not the SVG. |
| `assets/css/site.scss` | All styles. Colour tokens at the top, light and dark. |
| `_pages/` | Redirect stubs for old URLs. |

## Front matter

```yaml
---
title: "Required"
published: false    # omit or true to publish
excerpt: ""         # optional; meta description and RSS summary
---
```

## Rules

- Branch and open a PR. Never push to `master`; the PR check builds the site
  and runs html-proofer.
- Do not edit a published post unless asked. Writing already went out on the
  feed.
- Run `make check` before pushing. It works locally.

## Traps

1. **Liquid runs before Markdown, even inside code fences.** Anything quoting
   `{{` or `{%` breaks the build. Wrap it in `{% raw %}` … `{% endraw %}`.
2. **`future: false`.** A post dated after the build date silently does not
   publish.
3. **html-proofer gates the deploy.** Every internal link and image must
   resolve.
4. **`exclude:` in `_config.yml` replaces Jekyll's defaults.** Adding an entry
   means keeping the existing ones.
5. **`published: false` hides a post from the production build only.** It is
   still in git and visible under `make serve`.
6. **jekyll-feed always builds a posts feed.** It is parked at
   `/feed/posts.xml`; Writing owns `/feed.xml`.
7. **Do not give a page the permalink of a redirect stub** in `_pages/`.

## Voice

Plain and specific. No marketing register, no exclamation marks.

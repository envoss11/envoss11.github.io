# ericvoss.com

Commonplace, Eric Voss's notebook: notes on books, and other writing. Jekyll 4, built
and deployed by GitHub Actions (`.github/workflows/deploy.yml`). The site is
the public view of a set of Markdown files; the files are the notebook.

## Sections

| Tab | Directory | URL |
|---|---|---|
| Reading | `_books/` | `/reading/<slug>/` |
| Excerpts | (from `_books/`) | `/excerpts/` |
| Writing | `_writing/` | `/writing/<slug>/` |
| Homepage intro | `_pages/about.md` | `/` (`/about/` redirects there) |

## Writing in the notebook

```sh
make notebook    # the editor, at localhost:4100
make serve       # the site, at localhost:4000, unpublished entries included
```

`make notebook` opens a small local editor over the same Markdown files: pick a
tab and an entry, write, and it saves to the file a moment after you stop
typing (or on cmd-S). It can start an entry, flip `published`, edit the front
matter, preview the Markdown roughly, and on Reading run the Goodreads sync.
It refuses to save over a file that changed on disk since you opened it, so it
is safe to edit in another editor or run the sync alongside it. It does not
touch git: commit and open a PR as usual.

From the command line instead:

```sh
make entry SECTION=writing TITLE="Some title"   # reading | writing
make sync-books                                 # pull the Goodreads shelf (DRY=1 to preview)
```

The few Markdown conventions the site reads (excerpts, the featured passage,
margin notes, backlinks) are listed in `CLAUDE.md` under "Writing conventions".

A new entry starts with `published: false`. Delete that line, or set it to
`true`, when it is ready; the production build skips unpublished entries.

## Layout

- `index.html` — the first page: the intro from `_pages/about.md`, the
  featured excerpt, recent books, and recent writing once there is some.
- `reading/` — books with notes first, then the rest as a shelf of small
  covers by year read. `excerpts/` — every excerpt, by book. `writing/`.
- `_layouts/notebook.html` — header, tabs, footer. `book.html` and `entry.html`
  extend it.
- `_includes/` — `tabs.html`, `book-card.html`, `shelf.html`, `excerpts.html`,
  `mentioned-in.html`, `entry-list.html`, `head.html`.
- `assets/js/site.js` — margin notes; the only script, and optional.
- `_data/notebook.yml` — tab order and footer links.
- `tools/goodreads_sync.py` — the Goodreads sync behind `make sync-books`.
- `tools/notebook/` — the editor: `server.py` (standard library only, bound to
  127.0.0.1), and one page (`index.html`, `app.js`, `app.css`) that reuses the
  site stylesheet. `make test-tools` runs its tests.
- `assets/css/site.scss` — the only stylesheet. Colors are tokens on `:root`;
  dark mode follows the OS.

## Setup

Ruby 3.4 (`.ruby-version`), then `bundle install`. `make check` builds the site
and runs html-proofer, the same gate CI runs on every PR.

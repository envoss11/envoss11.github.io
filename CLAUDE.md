# Working on this repo

`ericvoss.com` is **Commonplace**, a commonplace book: passages copied out of
what I read, notes on them, and other writing. The notebook comes first: Markdown files
in two sections, written through a local editor app (`make notebook`). The
Jekyll site is the public view of those files. Hand-written Jekyll, no theme
gem, no JavaScript framework. The editor (`tools/notebook/`) is stdlib Python
plus one plain HTML/JS page; keep it dependency-free. Design plan:
`~/.claude/plans/` (notebook refactor, in phases; see the PR history for which
have landed).

Sections: **Reading** (one page per book, seeded from Goodreads, plus
articles synced from Raindrop.io) and **Writing** (essays, notes, and project
write-ups). **Excerpts** is a tab but not a collection: it gathers the
blockquotes from Reading's notes, books and articles both. `_pages/about.md`
is not a page: its body is the homepage intro, and `/about/` redirects home.

## Commands

| Target | What it does |
|---|---|
| `make notebook` | The local editor at `localhost:4100` (`tools/notebook/`) |
| `make entry SECTION=writing TITLE="..."` | Start an unpublished entry. `SECTION` is `reading` or `writing` |
| `make serve` | Preview at `localhost:4000`, unpublished entries included |
| `make build` | Production build into `_site/` |
| `make check` | Build, then html-proofer — the same gate CI runs on every PR |
| `make sync-books` | Pull the public Goodreads shelf into `_books/` (`DRY=1` to preview) |
| `make sync-articles` | Pull Raindrop.io bookmarks and highlights into `_articles/` (`DRY=1` to preview) |
| `make test-tools` | Unit tests for the editor server and the Raindrop sync; run after changing `tools/` |

## Where things go

| | |
|---|---|
| `_books/` | Reading. `<slug>.md`, live at `/reading/<slug>/`. Body is my notes and may be empty. |
| `_articles/` | Articles, written by `make sync-articles`, live at `/reading/articles/<slug>/`. Raindrop owns these: never edit them by hand. |
| `_writing/` | Writing. `YYYY-MM-DD-slug.md`, live at `/writing/<slug>/`, in RSS. |
| `_pages/` | `about.md` (the homepage intro), and redirect stubs for old URLs. |
| `excerpts/` | The Excerpts page. Built from book and article notes; nothing to edit here. |
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
`links: [{title, url}]`.

Articles carry `source`, `site`, `date_read` (when saved to Raindrop) and
`raindrop_id`, all written by the sync.

## Writing conventions

Plain Markdown; these are the only conventions the site reads.

- **Excerpts.** A blockquote in a book's notes is an excerpt. Transcribe the
  passage as written. If the blockquote has more than one paragraph, the last
  one is the source, e.g. `p. 112`. Notes go between the excerpts as ordinary
  paragraphs.
- **The homepage passage** is picked by hand: put `{: .featured}` on the line
  right after a blockquote. If several are marked, the most recently read book
  wins, so unmark the old one when choosing a new one.
- **Margin notes** are Markdown footnotes (`[^1]`). On wide screens they sit
  in the margin beside the text; elsewhere they are footnotes.
- **Mentioned in.** Linking one entry from another adds a backlink at the foot
  of the linked page. Link with the trailing slash (`/reading/dune/`).

## Heads, later

Commonplace books were traditionally sorted under *heads*: short topic words
(*Attention*, *Cities*) with an A–Z index. There are none yet, on purpose.
Revisit once there are enough excerpts that groupings show up on their own.
Likely shape: a `heads: [..]` list in front matter and one `/heads/` index
page, not a taxonomy designed up front.

## Articles

Raindrop.io is the source for articles. The bookmark's note comes first, then
each highlight as a blockquote (so it is an excerpt) followed by its note.
Bookmarks in a collection whose name contains "queue", or nested under one,
are to-read and stay out. Notes that touch my work stay in Raindrop but off
the site: list the bookmark or highlight id in `tools/raindrop_private.txt`,
or tag the bookmark `private` in Raindrop. Check new notes for this before
pushing a sync. Each sync rewrites `_articles/` to match Raindrop and
deletes files whose bookmark is gone. The token lives in `RAINDROP_TOKEN` or
`.raindrop-token`; never commit it. Articles render without Liquid
(`render_with_liquid: false`), so trap 1 does not apply to them.

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
8. **Excerpts are cut out of rendered HTML.** `_includes/excerpts.html` splits
   `book.content` on `<blockquote`, which works because collections render
   before pages. Use it from pages (`index.html`, `excerpts/`), not from a
   collection's layout.

## Voice

Plain and specific. Say what something is and why when it is not obvious. No
marketing register, no exclamation marks.

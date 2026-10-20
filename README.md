# ericvoss.com

Eric Voss's site: posts, working notes, and side projects on AI engineering in
financial services. Jekyll 4, built and deployed by GitHub Actions
(`.github/workflows/deploy.yml`). `CLAUDE.md` has the editorial rules.

## Writing a post

```sh
make post TITLE="Power analysis for AI evals" TOPIC=evaluation
make serve                       # preview at localhost:4000, drafts included
make publish SLUG=power-analysis-for-ai-evals
```

Topics are the keys in `_data/topics.yml`: `document-intelligence`,
`evaluation`. Leave `TOPIC` off for Other. Add `FROM_NOTE=<note-slug>` when the
post grew out of a note.

## Writing a note

```sh
make note TITLE="Notes on The Alignment Problem" TOPIC=reading
make touch SLUG=notes-on-the-alignment-problem   # bump updated: after a revision
```

A note is private until its front matter says `published: true`. Status is
`idea`, `wip`, or `complete`. Topics are the keys in `_data/note_topics.yml`.

From a phone, or anywhere without the toolchain, add a file in GitHub's web
editor at `_posts/2026-10-17-some-slug.md` or `_notes/some-slug.md`, copying
the front matter from `CLAUDE.md`.

## Layout

- `index.html` — home: pitch, latest posts, recently updated notes.
- `_pages/writing.html` — every post by category, with a filter.
- `_pages/notes.html`, `_pages/projects.html`, `_pages/about.md`.
- `_layouts/default.html` — header, footer, everything around the content.
- `_layouts/post.html`, `_layouts/note.html` — a single post or note.
- `_includes/entry-list.html` — a dated list of posts and notes.
- `_includes/note-list.html`, `_includes/status.html` — note lists and badges.
- `assets/css/site.scss` — the only stylesheet. Colors are tokens on `:root`;
  dark mode follows the OS.
- `assets/js/site.js` — the Writing filter. Without it every section shows.

## Setup

Ruby 3.4 (`.ruby-version`), then `bundle install`. `make check` runs the same
build and link check as CI.

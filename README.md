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
make note TITLE="Faith as a leap" TOPIC=philosophy           # a subject
make book TITLE="Either/Or" AUTHOR="Søren Kierkegaard" TOPIC=philosophy
make session                     # today's heading in the last note, opened
make session NOTE=either LABEL="Rotation of Crops"
make next                        # what to pick up, what is linked but unwritten
```

A note is private until its front matter says `published: true`. The repo is
public, though, so `LOCAL=1` on `make note` or `make book` puts a note in the
gitignored `_notes/local/` instead. Status is `idea`, `wip`, or `complete`.
Topics are the keys in `_data/note_topics.yml`; each sits on the `work` or
`life` shelf. `[[slug]]` or `[[Title]]` links notes together.

From a phone, or anywhere without the toolchain, add a file in GitHub's web
editor at `_posts/2026-10-17-some-slug.md` or `_notes/some-slug.md`, copying
the front matter from `CLAUDE.md`.

## Layout

- `index.html` — home: pitch, latest posts, recently updated work notes.
- `_pages/writing.html` — every post by category, with a filter.
- `_pages/notes.html`, `reading.html`, `log.html`, `projects.html`, `about.md`.
- `_plugins/notes.rb` — wiki links, backlinks, and study sessions.
- `bin/study` — behind `make note`, `book`, `session`, and `next`.
- `_layouts/default.html` — header, footer, everything around the content.
- `_layouts/post.html`, `_layouts/note.html` — a single post or note.
- `_includes/entry-list.html` — a dated list of posts and notes.
- `_includes/note-list.html`, `book-list.html`, `status.html` — lists and badges.
- `assets/css/site.scss` — the only stylesheet. Colors are tokens on `:root`;
  dark mode follows the OS.
- `assets/js/site.js` — the Writing filter. Without it every section shows.

## Setup

Ruby 3.4 (`.ruby-version`), then `bundle install`. `make check` runs the same
build and link check as CI.

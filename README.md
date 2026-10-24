# ericvoss.com

Eric Voss's notebook: notes on books, writing, and projects. Jekyll 4, built
and deployed by GitHub Actions (`.github/workflows/deploy.yml`). The site is
the public view of a set of Markdown files; the files are the notebook.

## Sections

| Tab | Directory | URL |
|---|---|---|
| Reading | `_books/` | `/reading/<slug>/` |
| Writing | `_writing/` | `/writing/<slug>/` |
| Projects | `_projects/` | `/projects/<slug>/` |
| About | `_pages/about.md` | `/about/` |

## Adding an entry

```sh
make entry SECTION=writing TITLE="Some title"   # reading | writing | projects
make serve                                      # localhost:4000, unpublished entries included
```

A new entry starts with `published: false`. Delete that line, or set it to
`true`, when it is ready; the production build skips unpublished entries.

## Layout

- `index.html` — the cover, with the latest entries of each section.
- `reading/`, `writing/`, `projects/` — the section index pages.
- `_layouts/notebook.html` — header, tabs, footer. `book.html` and `entry.html`
  extend it.
- `_includes/` — `tabs.html`, `book-card.html`, `entry-list.html`, `head.html`.
- `_data/notebook.yml` — tab order and footer links.
- `assets/css/site.scss` — the only stylesheet. Colors are tokens on `:root`;
  dark mode follows the OS.

## Setup

Ruby 3.4 (`.ruby-version`), then `bundle install`. `make check` builds the site
and runs html-proofer, the same gate CI runs on every PR.

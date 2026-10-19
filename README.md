# ericvoss.com

Writing by Eric Voss on AI/ML, data science, and the books he reads. Jekyll 4,
built and deployed by GitHub Actions (`.github/workflows/deploy.yml`).

## Writing a post

```sh
make post TITLE="Notes on The Alignment Problem" TOPIC=books
make serve                       # preview at localhost:4000, drafts included
make publish SLUG=notes-on-the-alignment-problem
```

Topics are the keys in `_data/topics.yml`: `ai-ml`, `books`.
Leave `TOPIC` off for Other.

From a phone, or anywhere without the toolchain, add a file in GitHub's web
editor at `_posts/2026-10-17-some-slug.md`:

```yaml
---
title: "Some title"
topics: [ai-ml]
---

The post.
```

## Layout

- `index.html` — the feed: a filter row, latest posts, then one section per topic.
- `_layouts/default.html` — header, footer, everything around the content.
- `_layouts/post.html` — a single post.
- `_includes/post-list.html` — one dated list section of the feed.
- `_pages/about.md` — the About page.
- `assets/css/site.scss` — the only stylesheet. Colors are tokens on `:root`;
  dark mode follows the OS.
- `assets/js/site.js` — the filter. Without it every section shows.

## Setup

Ruby 3.4 (`.ruby-version`), then `bundle install`. `make check` runs the same
build and link check as CI.

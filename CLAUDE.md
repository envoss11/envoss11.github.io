# Working on this repo

`ericvoss.com`: a dated list of posts, filterable by topic, on a hand-written
Jekyll site. One layout file, one stylesheet (`assets/css/site.scss`), one small
script (`assets/js/site.js`, the homepage filter). No framework, no theme gem.

## Commands

| Target | What it does |
|---|---|
| `make post TITLE="..." TOPIC=ai-ml` | Start `_drafts/<slug>.md`. `TOPIC` is optional and checked |
| `make serve` | Preview at `localhost:4000`, drafts included |
| `make publish SLUG=<slug>` | Move the draft into `_posts/`, dated today |
| `make build` | Production build into `_site/` |
| `make check` | Build, then html-proofer — the same gate CI runs on every PR |

## Where things go

| | |
|---|---|
| `_posts/` | Published. `YYYY-MM-DD-slug.md`, live at `/posts/<slug>/`, in RSS and the sitemap. |
| `_drafts/` | Private. Shows under `make serve` only. |
| `_pages/` | About, and redirect stubs for old URLs. |
| `_data/topics.yml` | The filter list. Adding a topic is three lines here. |
| `_data/navigation.yml` | Header links. A Projects page goes here when it exists. |

## Front matter

```yaml
---
title: "Required"
topics: [ai-ml]     # optional; any keys from _data/topics.yml, or none
excerpt: ""         # optional; meta description and RSS summary
---
```

That is the whole contract. A post with no topics, or only unknown ones, lands
in **Other**. A book note is a post with `topics: [books]`; the title names the
book.

## Rules

- Branch and open a PR. Never push to `master`; the PR check builds the site
  and runs html-proofer.
- Do not edit a published `_posts/` entry unless asked. It already went out on
  the feed.
- Run `make check` before pushing. It works locally.

## Traps

1. **Liquid runs before Markdown, even inside code fences.** Anything quoting
   `{{` or `{%` breaks the build. Wrap it in `{% raw %}` … `{% endraw %}`.
2. **`future: false`.** A post dated after the build date silently does not
   publish.
3. **html-proofer gates the deploy.** Every internal link and image must
   resolve, including `/#topic` anchors (each feed section carries its key as
   its `id`).
4. **An unknown topic key is silent.** The post just shows under Other.
   `make post` checks `TOPIC`; a hand-typed front matter is not checked.
5. **`exclude:` in `_config.yml` replaces Jekyll's defaults.** Adding an entry
   means keeping the existing ones.
6. **Do not slug a post `posts`,** or anything that matches a redirect stub.

## Voice

Plain and specific. Say what something is and why when it is not obvious. No
marketing register, no exclamation marks.

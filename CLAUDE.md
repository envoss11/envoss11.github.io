# Working on this repo

`ericvoss.com`: Eric Voss's career site. A hand-written Jekyll 4 site with no
framework or theme gem: two content types (Posts and Notes), a Projects list,
and an About page. One stylesheet (`assets/css/site.scss`) and one small script
(`assets/js/site.js`, the filter on `/writing/`).

## Positioning

The site is the pitch, made browsable:

> I'm an AI engineer in financial services. I build document intelligence
> platforms and decision support systems, mostly on AWS, and I care a lot about
> measuring whether they actually work.

- Eric is a Lead Data Scientist in an AI Center of Excellence at a financial
  services company (life insurance, annuities, group benefits). In practice the
  role is AI engineering. MS in Statistics; undergraduate degrees in economics
  and CS; deep insurance and underwriting domain knowledge.
- He has shipped a production GenAI pipeline for underwriting and medical
  document extraction, and is building out his employer's document processing
  platform.
- **The differentiator** within the positioning is statistical rigor in
  evaluation and measurement: an AI engineer who can do power analysis on an
  eval, not just ship the system.
- "AI Engineer" vs. "AI Platform Engineer" is unresolved on purpose. The site
  says "AI engineer"; platform-oriented writing carries the platform signal.
- Inspirations: robinlinacre.com (topic categories *are* the identity, one
  clear area of depth, light side projects) and hamel.dev (a Blog of finished
  pieces plus public working Notes, with matured notes listed beside posts).

Writing categories mirror the pitch: Document intelligence, Evaluation &
measurement, and Other. Add a category (e.g. AWS & AI platforms) only when
there is writing that needs it, not in advance.

## Editorial philosophy

**Posts and Notes are two different contracts.**

- **Posts are for others.** Finished, argue something, dated, a stance Eric
  attaches his name to. They are the evidence a hiring manager reads.
- **Notes are for Eric, in public.** Unfinished, revised freely, judged only on
  whether they help him understand something. He learns by producing a page
  that demonstrates his understanding to himself.

**Promotion connects them.** When a note grows an opinion, it becomes (or
spawns) a post. The post names the note in `from_note`; a note that is worth
reading as finished writing can also be listed on `/writing/` with `writing:`.

**Note maturity is visible.** Every note shows its status (`idea`, `wip`,
`complete`) and last-updated date at the top. This sets reader expectations and
removes the pressure to polish. Do not hold a note back because it is rough.

**Publishing is opt-in and default-private.** Drafts and unpublished notes must
never render or reach the feed or sitemap. Do not weaken this default.

**Organization stays flat.** One topic per note, no hierarchy deeper than one
level. Simplicity beats taxonomy.

**Side interests live in Notes and Projects, not Writing categories.**
Stylometry, interpretability, and philosophy signal breadth without diluting
the headline. If one bridges to the core (e.g. stylometry used to compare or
fingerprint LLMs), its post goes under Evaluation & measurement.

**Cadence:** Notes whenever Eric is studying, with no minimum; a Post roughly
every 6–8 weeks. Most personal sites die because the bar to publish is too
high, and Notes exist to lower it. Do not add features, checks, or steps that
raise friction.

## Confidentiality

Eric's strongest material is employer work. Public writing covers patterns,
trade-offs, and measurement approaches. Anything empirical is reproduced on
public data. Never include internal names, systems, data, or figures.

**If content looks like it may expose employer internals, flag it to Eric
rather than publishing it**, even when asked only to edit or publish.

## Commands

| Target | What it does |
|---|---|
| `make post TITLE="..." TOPIC=evaluation` | Start `_drafts/<slug>.md`. `TOPIC` optional and checked; `FROM_NOTE=<note-slug>` links the note it grew from |
| `make publish SLUG=<slug>` | Move the draft into `_posts/`, dated today |
| `make note TITLE="..." TOPIC=evals-statistics` | Start a private `_notes/<slug>.md`, status `idea`, dated today. `TOPIC` required and checked |
| `make touch SLUG=<note-slug>` | Set a note's `updated:` to today |
| `make serve` | Preview at `localhost:4000`, drafts and private notes included |
| `make build` | Production build into `_site/` |
| `make check` | Build, then html-proofer — the same gate CI runs on every PR |

## Where things go

| | |
|---|---|
| `_posts/` | Published posts. `YYYY-MM-DD-slug.md`, live at `/posts/<slug>/`, in RSS and the sitemap. |
| `_drafts/` | Unpublished posts. Shown under `make serve` only. |
| `_notes/` | Notes, at `/notes/<slug>/`. Private until `published: true`. Never in RSS. |
| `_pages/` | Writing, Notes, Projects, About, and redirect stubs for old URLs. |
| `_data/topics.yml` | Writing categories (the `/writing/` filter). |
| `_data/note_topics.yml` | Note groups on `/notes/`. |
| `_data/projects.yml` | The `/projects/` list. An entry is a few lines; the format is in the file. |
| `_data/navigation.yml` | Header links. `_data/social.yml` holds the footer's off-site links. |
| `_layouts/` | `default`, `post`, `note`, `redirect`. |

## Front matter

Post:

```yaml
---
title: "Required"
topics: [evaluation]   # optional; keys from _data/topics.yml, or none for Other
excerpt: ""            # optional; meta description and RSS summary
from_note: some-note   # optional; the note this grew out of (linked both ways)
updated: 2026-12-01    # optional; shown beside the date after a real revision
---
```

The date comes from the filename. A post with no topics, or only unknown ones,
lands in **Other**.

Note:

```yaml
---
title: "Required"
topic: evals-statistics  # exactly one key from _data/note_topics.yml
status: idea             # idea | wip | complete
updated: 2026-10-20      # set by hand or `make touch`
published: false         # true puts it on the live site
writing: evaluation      # optional; also list it on /writing/ under this category
excerpt: ""
---
```

Book notes are notes with `topic: reading`; the title names the book.

## How publishing works

- **Post:** `make post` → write → `make serve` to preview → `make publish` →
  PR. Once merged it is on the site and in `/feed.xml`.
- **Note:** `make note` → write → set `published: true` when it is worth
  someone else seeing (any status is fine) → PR. Bump `updated:` with
  `make touch` when the content changes meaningfully.
- **Promote a note:** `make post TITLE="..." TOPIC=... FROM_NOTE=<note-slug>`.
  The post shows "This grew out of a working note…", and the note shows "This
  note became a post…" automatically; the link lives only on the post. Keep
  the note (it is the working record) and usually move its status to
  `complete`. If a note itself reads as finished writing, `writing: <category>`
  lists it on `/writing/` without writing a separate post.
- **Project:** add an entry to `_data/projects.yml`. Link the repo, and a post
  or note about it in `writeup:` if there is one.

## Rules

- Branch and open a PR. Never push to `master`; the PR check builds the site
  and runs html-proofer.
- Do not edit a published `_posts/` entry unless asked. It already went out on
  the feed. Notes can be edited freely; that is their point.
- Do not write prose in Eric's voice beyond what he has supplied. Use a marked
  placeholder (a `{% raw %}{% comment %}{% endraw %}` block) where content is
  needed. The About page's career-arc paragraph is one.
- Run `make check` before pushing. It works locally.

## Traps

1. **Liquid runs before Markdown, even inside code fences.** Anything quoting
   `{{` or `{%` breaks the build. Wrap it in `{% raw %}` … `{% endraw %}`.
2. **`future: false`.** A post dated after the build date silently does not
   publish.
3. **html-proofer gates the deploy.** Every internal link and image must
   resolve, including `#anchor` links: `/writing/#<key>` and `/notes/#<key>`
   sections carry their key as their `id`. Empty note groups are hidden, so
   do not hand-link to one.
4. **An unknown topic key is silent.** The post or note shows under Other.
   `make post` and `make note` check `TOPIC`; hand-typed front matter is not
   checked.
5. **A note's `published: false` is the default from `_config.yml`**, not just
   the template. A note with no `published:` line is private.
6. **`exclude:` in `_config.yml` replaces Jekyll's defaults.** Adding an entry
   means keeping the existing ones.
7. **Do not slug a post `posts`, or a note `index`,** or anything that matches
   a redirect stub.

## Voice

Plain and specific. Say what something is and why when it is not obvious. No
marketing register, no exclamation marks.

# Working on this repo

`ericvoss.com`: Eric Voss's career site, and the visible half of a study
practice. A hand-written Jekyll 4 site with no framework or theme gem: Posts,
Notes (book notes among them), Reading, a Log, Projects, and About. One
stylesheet (`assets/css/site.scss`), one small script (`assets/js/site.js`, the
filter on `/writing/`), one plugin (`_plugins/notes.rb`, wiki links and
sessions), and one helper (`bin/study`, behind the study `make` targets).

## What the site is for

Eric is building tools and habits for a consistent practice of intellectual
exploration: low friction, part of ordinary life, and leaving visible
artifacts that show progress. This site is the visible-artifacts part. Beyond
that it is only a light landing page (pitch, short bio, links).

Everything is organized on two axes:

- **Professional relevance**, set once per topic as its `shelf` (`work` or
  `life`) in `_data/note_topics.yml`. Work comes first everywhere and is the
  only shelf on the homepage; life is one click away. An AI project or an ML
  book is work; Kierkegaard is life.
- **Content type**: a Post (finished, argued) is presented differently from a
  Note (a working page, wiki-style), a book note (a note with `author:`, also
  on `/reading/`), or a Project.

The practice side must fade into the background: open a file, write, close it.
Anything that adds upkeep (tags to maintain, indexes to update by hand,
required fields) works against it.

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
level. Connections are `[[wiki links]]`, not folders or tags. Simplicity beats
taxonomy.

**A session is the unit of practice.** One sitting with a book or subject is a
dated `## YYYY-MM-DD` heading in its note, added by `make session`. Sessions
drive the note's `updated` date, its session count, and `/log/`, so the
record of progress builds itself.

**Side interests live in Notes and Projects, not Writing categories.**
Stylometry, interpretability, and philosophy signal breadth without diluting
the headline. If one bridges to the core (e.g. stylometry used to compare or
fingerprint LLMs), its post goes under Evaluation & measurement.

**Cadence:** Notes whenever Eric is studying, with no minimum; a Post roughly
every 6–8 weeks. Most personal sites die because the bar to publish is too
high, and Notes exist to lower it. Do not add features, checks, or steps that
raise friction.

## Confidentiality

**The repo is public.** `published: false` keeps a note off the site, not out
of GitHub. Anything Eric would not want read goes in `_notes/local/`
(gitignored: `make serve` shows it, nothing commits or deploys it). Suggest
`LOCAL=1` when a note looks personal.

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
| `make note TITLE="..." TOPIC=evals-statistics` | Start a private `_notes/<slug>.md`, status `idea`, dated today. `TOPIC` required and checked. `LOCAL=1` puts it in `_notes/local/` |
| `make book TITLE="..." AUTHOR="..." TOPIC=philosophy` | Start a book note with today's session open. `LOCAL=1` as above |
| `make session [NOTE=...] [LABEL="..."]` | Add today's `## YYYY-MM-DD` heading and open the note. No `NOTE`: the last one worked on. `NOTE` can be part of a slug or title |
| `make next` | Sessions lately, days since the last post, what is in progress or stale, links made to notes not yet written, complete notes not yet a post, ideas, and `_data/queue.yml` |
| `make touch SLUG=<note-slug>` | Set a note's `updated:` to today (sessions do this already) |
| `make serve` | Preview at `localhost:4000`, drafts, private and local notes included. Doubles as a private dashboard: `/log/` and `/notes/` show everything |
| `make build` | Production build into `_site/` |
| `make check` | Build, then html-proofer — the same gate CI runs on every PR |

## Where things go

| | |
|---|---|
| `_posts/` | Published posts. `YYYY-MM-DD-slug.md`, live at `/posts/<slug>/`, in RSS and the sitemap. |
| `_drafts/` | Unpublished posts. Shown under `make serve` only. |
| `_notes/` | Notes, at `/notes/<slug>/`. Private until `published: true`. Never in RSS. |
| `_notes/local/` | Gitignored notes: seen by `make serve` and `make next` only. |
| `_plugins/notes.rb` | Wiki links, backlinks, sessions, and the `/log/` data. |
| `bin/study` | The study targets (`note`, `book`, `session`, `next`). Plain Ruby, no gems. |
| `_pages/` | Writing, Notes, Reading, Log, Projects, About, and redirect stubs for old URLs. |
| `_data/topics.yml` | Writing categories (the `/writing/` filter). |
| `_data/note_topics.yml` | Note groups on `/notes/`, each with its `shelf` (`work` or `life`). |
| `_data/queue.yml` | Books and subjects up next: `/reading/` and `make next`. |
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
updated: 2026-10-20      # optional once it has sessions; the newest session wins
published: false         # true puts it on the live site
writing: evaluation      # optional; also list it on /writing/ under this category
excerpt: ""
---
```

A book note adds `author:` (which is what makes it a book), `started:`, and
`finished:` when done; `make book` writes these. It takes its subject's topic,
so its shelf follows: an ML book is on the work shelf, Kierkegaard is not.

In a note body, `## 2026-10-24` or `## 2026-10-24 · Diapsalmata` is a session.
In a note or post body, `[[slug]]`, `[[Some Title]]`, or `[[slug|text]]` links
to a note or post. A missing or private target renders as dotted plain text
and is listed by `make next` as wanted. Linked pages get a "Linked from" list
automatically.

## How publishing works

- **Post:** `make post` → write → `make serve` to preview → `make publish` →
  PR. Once merged it is on the site and in `/feed.xml`.
- **Note:** `make note` → write → set `published: true` when it is worth
  someone else seeing (any status is fine) → PR. Each later sitting is
  `make session`, which dates it.
- **Book:** `make book` at the start, `make session` each sitting, `finished:`
  at the end. It moves from Now to Finished on `/reading/`.
- **Promote a note:** `make post TITLE="..." TOPIC=... FROM_NOTE=<note-slug>`.
  The post shows "This grew out of a working note…", and the note shows "This
  note became a post…" automatically; the link lives only on the post. Keep
  the note (it is the working record) and usually move its status to
  `complete`. If a note itself reads as finished writing, `writing: <category>`
  lists it on `/writing/` without writing a separate post.
- **Project:** add an entry to `_data/projects.yml`. Link the repo, and a post
  or note about it in `writeup:` if there is one.

## Study sessions with Claude

When Eric is studying, Claude is a study partner, not a ghostwriter. The notes
are how he learns, so the writing in them is his.

- **Do:** ask questions that test his understanding, point out tensions with
  his earlier notes (read them; follow `[[links]]` and "Linked from"), suggest
  connections and what to read next, check facts and quotations, run `make
  next` and help choose among what it lists, and do the mechanics (start a
  book, add a session, move an entry from the queue, set `finished:`).
- **Do not:** write note prose for him, summarize a book into his note, or tidy
  his notes' wording. Offer text only when he asks, and say it is a suggestion.
- When he asks what to work on next, start from `make next`: links he has
  already made but not written are the strongest signal, then stale work in
  progress, then the queue. Keep the post cadence in view.

## Sample content

Pages with `sample: true` are made up to preview the layout; they show a
banner and a "sample" tag. They were added in one commit titled "SAMPLE
CONTENT", together with entries marked `# SAMPLE` in `_data/queue.yml` and
`_data/projects.yml`. Remove all of it before merging to `master`:
`git revert <that commit>`, then check that `git grep -n "sample: true"` and
`git grep -n SAMPLE _data` come back empty.

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
8. **The plugin needs the Actions build.** `_plugins/` does not run under
   GitHub's legacy Pages builder; the deploy workflow builds with Jekyll
   directly, so it does. Keep it that way.
9. **A session heading must be `## ` plus an ISO date at the start of the
   line.** `### 2026-10-24`, or a date in prose, is not counted.

## Voice

Plain and specific. Say what something is and why when it is not obvious. No
marketing register, no exclamation marks.

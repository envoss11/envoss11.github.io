# Working on this repo

Read this before writing anything. It is the whole briefing — a session started
from the cloud gets this file, `.claude/`, and nothing else from my machine.

## What the site is

`ericvoss.com`: a career landing page and everything I write, on a hand-written
Jekyll theme. No framework, no build step beyond Jekyll — plain HTML, one
stylesheet, one JavaScript file. `README.md` has the fuller tour; the section
comments in `_sass/` and the header comments in `_data/*.yml` are the real
documentation and are worth reading before changing anything they describe.

The `make` interface is the whole toolchain:

| Target | What it does |
|---|---|
| `make serve` | Preview at `localhost:4000`, drafts included, reloads on save |
| `make build` | Production build into `_site/` |
| `make check` | Build, then the same html-proofer run CI gates on |
| `make draft TITLE="..."` | Scaffold `_drafts/<slug>.md` — private |
| `make wip TITLE="..."` | Scaffold `_wip/<slug>.md` + `_research/<slug>/` — public but quiet |
| `make publish SLUG=<slug>` | Move a note out of `_wip/` or `_drafts/` into `_posts/` |

## Where things go

Getting this wrong is the most expensive mistake available, so:

| | |
|---|---|
| `_posts/` | **Finished.** `YYYY-MM-DD-slug.md`, live at `/posts/<slug>/`, in the sitemap, **in the RSS feed**. Publishing here notifies subscribers. |
| `_wip/` | **Live but quiet.** `<slug>.md`, live at `/posts/wip/<slug>/`, `noindex`, out of the sitemap, out of RSS, listed only inside a collapsed drawer. **This is where a cloud session writes.** |
| `_drafts/` | **Private.** Visible under `make serve` and nowhere else. Never published, never deployed. |
| `_research/` | **Raw artifacts.** Data pulls, scripts, source notes, working files. Never built — Jekyll skips `_`-prefixed directories on its own. |

The three published tiers are a real progression: `_drafts/` is invisible,
`_wip/` is readable but not announced, `_posts/` is announced. Moving between
them is a rename — see `make publish`.

## Front matter

Only `title` is required. Everything else is optional and the layout drops
whatever is missing.

| Field | |
|---|---|
| `title` | Required. |
| `excerpt` | The one-line summary. Shows in the log, the card, and the meta description. Write one. |
| `date` | **Required in `_wip/`**, where there is no date in the filename. In `_posts/` the filename carries it. |
| `tags_list` | A list of strings, renders as pills. |
| `image` / `image_fit` | Hero image from `assets/images/`. `image_fit: contain` letterboxes charts and screenshots instead of cropping them. |
| `facts` | `label`/`value` pairs, renders as the dotted-leader table under the header. |
| `links` | `label`/`icon`/`url` pill buttons. `icon` must be one of `external`, `github`, `file`. |

Do **not** set `layout`, `permalink`, `sitemap`, `noindex`, or `kicker` on a WIP
note. The `wip` defaults scope in `_config.yml` supplies all five.

Two placeholder files document every field by example:
`_posts/2026-06-14-placeholder-full-write-up.md` (everything) and
`_posts/2026-08-04-placeholder-second-entry.md` (the minimum). A WIP note takes
the same front matter with `date` moved in from the filename —
`_wip/automated-prompt-engineering.md` is the live example.

## Rules for cloud sessions

**A bare idea dump with no other instruction means: run the `wip-note` skill.**
That is the default and it needs no confirmation. See
`.claude/skills/wip-note/SKILL.md`.

Beyond that:

- **Always branch and open a PR. Never push to `master`.** The PR check builds
  the site and runs html-proofer; I merge from my phone once it is green.
- **Never edit a published `_posts/` entry** unless I ask for that specifically.
  Those went out on the feed already.
- **Do not run `make check`, `make build`, or `bundle install` here.** They will
  fail — see below. CI validates instead.
- **Keep the raw braindump verbatim** at the top of the note, in a
  `## The dump` section. It is the record of what I actually thought, and it is
  more useful later than a tidied paraphrase.
- **Cite sources inline** as Markdown links. Anything asserted as fact in a
  research note needs one.

## Ruby: why the session cannot build

`.ruby-version` pins **3.4**. Cloud VMs ship Ruby 3.1/3.2/3.3 under rbenv, so
`bundle install` fails out of the box and everything downstream of it —
`make build`, `make check`, `make serve` — fails with it. This is expected and
is not worth working around: building Ruby 3.4 from source does not fit the
setup budget, and relaxing the pin buys nothing the PR check does not already
give.

**So: write Markdown, push a branch, let CI validate.** The one class of error a
local build would catch that CI now catches instead is the Liquid trap below,
and catching that as a red PR check is fine, because the merge is manual anyway.

## Traps

Every one of these is silent or delayed. None of them is caught by review.

1. **Jekyll parses Liquid before Markdown — including inside fenced code
   blocks.** A note quoting anything containing `{{` or `{%` fails the build,
   and a research note is exactly the kind of writing that quotes templates,
   shell snippets with `${}`, or JSON with braces. Wrap the block in
   `{% raw %}` … `{% endraw %}`. **This is the most likely way a note written
   from a phone breaks the site.**

2. **`_includes/icon.html` is a `{% case %}` with no `else` branch.** An unknown
   icon name renders *nothing at all* — no error, no fallback, no html-proofer
   failure. The valid names are `github`, `linkedin`, `mail`, `file`,
   `download`, `external`, `book`, `chart`, `code`, `package`, `tool`, `pin`,
   `leaf`, `moon`, `sun`, `arrow`.

3. **`future: false` is Jekyll's default.** A post dated ahead of the build date
   silently does not publish. Never date anything forward.

4. **html-proofer gates the deploy.** Every internal link must resolve, and
   every image referenced must exist. A link to a page you are "about to
   create" turns the check red.

5. **`.reveal` inside a closed `<details>` never appears.** It has a zero-size
   bounding rect, never trips the IntersectionObserver, and stays invisible even
   after the reader opens the drawer. Put `.reveal` on the `<details>` itself.

6. **`exclude:` in `_config.yml` replaces Jekyll's defaults rather than
   extending them.** Adding an entry means the existing ones still have to be
   listed. `_`-prefixed directories need no entry at all.

7. **Do not slug a post `wip`.** `_posts/YYYY-MM-DD-wip.md` builds to
   `/posts/wip/index.html`, which coexists with the WIP notes but reads as a
   section index and is not one.

## Voice

The README, the section comments in `_sass/`, and the placeholder entries are
the tone reference. Plain, specific, and willing to say what something is not.
Explain *why* a thing is the way it is when the reason is not obvious from the
code — that is what every comment in this repo is doing. No marketing register,
no hedging, and no exclamation marks.

For a research note specifically: state what the data actually supports and
stop. If the answer is "this doesn't show what I hoped," write that down.

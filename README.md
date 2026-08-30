# ericvoss.com

A career landing page and everything I write, on a hand-written Jekyll theme.
No framework, no build step beyond Jekyll: the site ships as plain HTML, one
stylesheet, and one JavaScript file.

Anything with data in it is written as a [marimo](https://marimo.io) notebook
and the page is generated from it — see [Notebooks](#notebooks).

Live at **https://www.ericvoss.com** (custom domain, set by `CNAME`).

## Setup

One time:

```sh
brew install ruby@3.4          # macOS system Ruby is 2.6 and too old
# keg-only, so it needs to come first on PATH — add to ~/.zshrc:
export PATH="$(brew --prefix ruby@3.4)/bin:$PATH"

bundle config set --local path vendor/bundle
bundle install

brew install uv                # the notebook half
uv sync
```

`.ruby-version` pins the version CI uses, so local and CI resolve the same
gems out of the committed `Gemfile.lock`. Everything Jekyll 4.4 needs ships as
a precompiled `arm64-darwin` gem — no compiler toolchain required.

`pyproject.toml` and `.python-version` do the same job for Python, and the
dependency list is one line long: `marimo`, for the CLI that `make sync` drives.
A notebook's own analysis dependencies live in its PEP 723 header instead, so
`make edit` can run it isolated and no two notebooks can constrain each other.

## Working on it

`make` on its own lists the targets.

| Target | What it does |
|---|---|
| `make serve` | Preview at `localhost:4000`, drafts included, reloads on save |
| `make build` | Production build into `_site/` |
| `make check` | Notebooks, build, and the html-proofer run CI gates on |
| `make notebooks` | Just the notebook half of that gate — lint, then drift |
| `make notebook TITLE="..."` | Scaffold a notebook, its page, and `_research/<slug>/` |
| `make edit SLUG=<slug>` | Open the notebook in marimo |
| `make run SLUG=<slug>` | Execute it headless — redraws its figures |
| `make sync SLUG=<slug>` | Regenerate the page body from the notebook |
| `make fix` | Apply marimo's own formatting fixes to the notebooks |
| `make draft TITLE="..."` | Scaffold `_drafts/<slug>.md` with front matter filled in |
| `make wip TITLE="..."` | Scaffold `_wip/<slug>.md` plus `_research/<slug>/` — an essay |
| `make publish SLUG=<slug>` | Move a note out of `_wip/` or `_drafts/` into `_posts/`, stamped today |

Run `make check` before pushing. It catches broken internal links, missing
images, and notebook pages that have drifted from the notebook under them,
which is most of what actually breaks here.

## Where things live

| | |
|---|---|
| `_data/` | The content that repeats: `profile.yml` (name, tagline, portrait, links), `career.yml`, `education.yml`, `certifications.yml`, `skills.yml`, `focus.yml`, `navigation.yml`. Each file's header comment documents its fields. Edit these, not the markup. |
| `_notebooks/` | The marimo notebook behind an exploration, `<slug>.py`. The source; the page is generated from it. Never built. |
| `_posts/` | Everything finished, `YYYY-MM-DD-slug.md`, served at `/posts/<slug>/`. |
| `_wip/` | AI drafts. Live at `/posts/wip/<slug>/`, out of the feed and the sitemap, listed in a collapsed drawer. |
| `_drafts/` | Unfinished posts. Visible under `make serve`, never published. |
| `_research/` | Raw material behind a note — data pulls, sources, working files. Committed, never built. |
| `_bin/` | `sync-notebook.py`, which turns a notebook into a page body. Underscore-prefixed, so Jekyll skips it without an `exclude:` entry. |
| `_pages/` | The standalone pages — About and Posts — plus the redirect stubs preserving URLs from the pre-2026 site. |
| `_layouts/`, `_includes/` | The theme. `head.html` does canonical, OG, and Twitter card by hand. |
| `_sass/` | Nine partials, loaded in order by `assets/css/site.scss` and compiled to one minified `/assets/css/site.css`. Section numbering is load order. |
| `assets/` | `js/site.js`, the four self-hosted woff2 faces, images, favicons. |
| `CLAUDE.md`, `.claude/` | The briefing a Claude Code session gets, and the `data-analysis` and `experiment` skills it runs. See below. |

### Notebooks

Anything with data in it is a marimo notebook, and the notebook is the source.
The page on the site is generated from it, so the prose gets written once, in
the same file as the code that produced the numbers.

```sh
make notebook TITLE="Does anyone actually read the changelog"
make edit SLUG=does-anyone-actually-read-the-changelog   # marimo, live
make run  SLUG=does-anyone-actually-read-the-changelog   # headless, redraws figures
make sync SLUG=does-anyone-actually-read-the-changelog   # regenerate the page
```

`make sync` runs `marimo export md` and splices the result under the page's
front matter, which is the only hand-written part of the file left. What a cell
is decides where it ends up:

| In the notebook | On the page |
|---|---|
| `mo.md("""...""")`, a plain string literal | Prose |
| `mo.md(f"""...""")` | A code block showing the f-string — not what you want |
| A code cell | A ```` ```python ```` block |
| A code cell with `hide_code=True` | Nothing |
| Any cell's output | Nothing |

So `hide_code=True` is the publishing control: hide the imports and the
matplotlib style block, leave the code that carries the argument visible.
`make sync` prints both counts every run.

Cell outputs are never exported, which means **a chart reaches the page only as
a committed PNG**. The template's `savefig` writes it into `assets/images/` and
prints the Markdown line to paste into a prose cell. Same reason, a computed
number gets printed and typed in rather than interpolated — an f-string is not a
literal, so marimo leaves it as code.

Dependencies go in the notebook's PEP 723 header, which is what `--sandbox`
reads and why `make run` works on a machine that has never installed pandas.

Because the page is generated, it can go stale. `make notebooks` — which
`make check` and CI both run — lints every notebook with `marimo check --strict`
and then re-runs the export to prove each page is exactly what its notebook
produces. A page that has drifted fails the build rather than deploying quietly.

An essay has no data at the bottom of it and stays plain Markdown; `make wip` is
still the way to start one.

### Adding a post

```sh
make draft TITLE="What I learned shipping an eval harness"
# write it, preview with `make serve`
make publish SLUG=what-i-learned-shipping-an-eval-harness
```

Only `title` is required. `excerpt` is what the log page shows and what falls
through to the meta description. `tags_list` renders as pills; drop it and the
row closes up. An `image` gets the post a hero — put the file in
`assets/images/` and add `image_fit: contain` if it's a chart or screenshot
that shouldn't be cropped.

**Jekyll's `future: false` default means a post dated ahead of the build date
silently will not publish.** `make publish` stamps today, so this only bites if
you hand-name a file with tomorrow's date.

### Write-ups

A project write-up is a post with more front matter, not a separate section.
The extras are the `facts` table under the header and the `links` pill buttons
(`icon: external | github | file`).

One section rather than two, and now one treatment rather than two: the
difference between a write-up and a Sunday note is real, but it's a difference
in how much front matter an entry carries, not in URL and not in billing. A card
grid used to sit above the log for entries marked `featured: true`; it re-showed
entries the log already listed, so it's gone, and so are `featured` and `order`.
Everything is one dated log with newer/older links and `/feed.xml`.

### AI drafts

`_wip/<slug>.md` is the tier between `_drafts/` and `_posts/`: live at
`/posts/wip/<slug>/`, but `noindex`, out of `/sitemap.xml`, out of `/feed.xml`,
and listed only inside a collapsed drawer on `/posts/`. It exists so a rough
note can be published and iterated on without landing in the feed, and it is
where the notebooks I kick off from a phone land.

```sh
make notebook TITLE="Something with a number at the end of it"
make wip      TITLE="Something I want to argue in public"
# ... later, when it's finished:
make publish SLUG=<slug>
```

The front matter is a post's, minus the date-in-the-filename convention. Give
every note a `date` in its front matter instead: the drawer sorts on it, and a
note without one falls back to sorting by filename. `layout`, `sitemap`,
`noindex`, and the kicker all come from the `wip` defaults scope in
`_config.yml` — don't set them per-note.

Both scaffolds also create `_research/<slug>/` for the raw material behind a
note: data pulls, source notes, working files. It's committed but never built —
Jekyll skips `_`-prefixed directories on its own, so it needs no `exclude:`
entry.

`make publish` moves a note out of either `_wip/` or `_drafts/` and stamps
today's date onto the filename. Drop the now-redundant `date:` line from the
front matter afterwards; it reminds you. A notebook does not move — it stays in
`_notebooks/` and `make sync` follows its page into `_posts/`.

## Writing from a phone

The reason `_wip/` exists. Start a Claude Code session at
[claude.ai/code](https://claude.ai/code) on this repo, paste a raw idea with no
other instruction, and it scaffolds a notebook, does a research pass, syncs the
page, and opens a PR. The PR runs the build, html-proofer, and the notebook
checks, so a green tick is visible from the GitHub mobile app — merge there and
it deploys.

**What comes back is deliberately thin.** The point of the round trip is to get
a notebook that exists, is live, and has had a real research pass behind it —
not a finished piece. I open it with `make edit SLUG=<slug>` and work in the
live kernel from there, pairing through the
[marimo-pair](https://github.com/marimo-team/marimo-pair) skill, which drives
the running kernel rather than editing the file. The skill instructs the cloud
session to under-write on purpose: anything I have to delete first cost me more
than it saved.

`CLAUDE.md` is what makes that work: a cloud session gets the repo's `CLAUDE.md`
and `.claude/`, and nothing from `~/.claude/`, so everything a session needs to
know is committed. `.claude/skills/data-analysis/SKILL.md` owns the procedure
(`.claude/skills/experiment/SKILL.md` covers the run-something-first variant)
and `.claude/skills/data-analysis/notebook-template.py` is the notebook both
start from — the same file `make notebook` copies, so there is only one.

Two settings have to be right on the cloud environment, and neither lives in the
repo:

- **Network access must be Full, or Custom with the data sources listed.** The
  default Trusted level reaches package registries, GitHub, and cloud SDKs only
  — not Census, arXiv, or a state data portal. The research half does nothing
  without it.
- Optionally a setup script running `uv sync`, so the session does not spend its
  first minutes installing marimo. It's cached as a filesystem snapshot, so it
  costs about once a week.

A cloud session can't build the site: `.ruby-version` pins 3.4 and those VMs
ship 3.1–3.3, so `bundle install` fails. That's deliberate — CI validates the
Ruby half. The Python half it can run, and is required to: `make sync` after
every notebook change and `make notebooks` before pushing, or the drift check
turns the PR red. `CLAUDE.md` says so, and lists the traps that a local build
would otherwise have caught.

## Deploys

Push to `master`. `.github/workflows/deploy.yml` builds with Jekyll 4, runs
html-proofer, checks the notebooks in a parallel job, and publishes to GitHub
Pages. Failures show up as a workflow log, not an email.

The same workflow runs on every pull request against `master`, but stops after
the build and the link check — no artifact, no deploy. So a branch gets a real
green tick before it merges, which is legible from a phone. `workflow_dispatch`
is still enabled for running it by hand from the Actions tab.

`jekyll-feed` generates `/feed.xml` and `jekyll-sitemap` generates
`/sitemap.xml`; the redirect stubs carry `sitemap: false` so they stay out of
it.

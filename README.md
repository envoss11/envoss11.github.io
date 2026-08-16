# ericvoss.com

A career landing page and everything I write, on a hand-written Jekyll theme.
No framework, no build step beyond Jekyll: the site ships as plain HTML, one
stylesheet, and one JavaScript file.

Live at **https://www.ericvoss.com** (custom domain, set by `CNAME`).

## Setup

One time:

```sh
brew install ruby@3.4          # macOS system Ruby is 2.6 and too old
# keg-only, so it needs to come first on PATH — add to ~/.zshrc:
export PATH="$(brew --prefix ruby@3.4)/bin:$PATH"

bundle config set --local path vendor/bundle
bundle install
```

`.ruby-version` pins the version CI uses, so local and CI resolve the same
gems out of the committed `Gemfile.lock`. Everything Jekyll 4.4 needs ships as
a precompiled `arm64-darwin` gem — no compiler toolchain required.

## Working on it

`make` on its own lists the targets.

| Target | What it does |
|---|---|
| `make serve` | Preview at `localhost:4000`, drafts included, reloads on save |
| `make build` | Production build into `_site/` |
| `make check` | Build, then the same html-proofer run CI gates on |
| `make draft TITLE="..."` | Scaffold `_drafts/<slug>.md` with front matter filled in |
| `make wip TITLE="..."` | Scaffold `_wip/<slug>.md` plus `_research/<slug>/` |
| `make publish SLUG=<slug>` | Move a note out of `_wip/` or `_drafts/` into `_posts/`, stamped today |

Run `make check` before pushing. It catches broken internal links and missing
images, which is most of what actually breaks here.

## Where things live

| | |
|---|---|
| `_data/` | The content that repeats: `profile.yml` (name, tagline, portrait, links), `career.yml`, `education.yml`, `certifications.yml`, `skills.yml`, `focus.yml`, `navigation.yml`. Each file's header comment documents its fields. Edit these, not the markup. |
| `_posts/` | Everything finished, `YYYY-MM-DD-slug.md`, served at `/posts/<slug>/`. |
| `_wip/` | Notes being drafted in public. Live at `/posts/wip/<slug>/`, out of the feed and the sitemap, listed in a collapsed drawer. |
| `_drafts/` | Unfinished posts. Visible under `make serve`, never published. |
| `_research/` | Raw material behind a note — data pulls, scripts, sources. Committed, never built. |
| `_pages/` | The standalone pages — About and Posts — plus the redirect stubs preserving URLs from the pre-2026 site. |
| `_layouts/`, `_includes/` | The theme. `head.html` does canonical, OG, and Twitter card by hand. |
| `_sass/` | Nine partials, loaded in order by `assets/css/site.scss` and compiled to one minified `/assets/css/site.css`. Section numbering is load order. |
| `assets/` | `js/site.js`, the four self-hosted woff2 faces, images, favicons. |
| `CLAUDE.md`, `.claude/` | The briefing a Claude Code session gets, and the `wip-note` skill it runs. See below. |

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

`_posts/2026-07-19-placeholder-first-entry.md` documents every field.

**Jekyll's `future: false` default means a post dated ahead of the build date
silently will not publish.** `make publish` stamps today, so this only bites if
you hand-name a file with tomorrow's date.

### Write-ups

A project write-up is a post with more front matter, not a separate section.
`_posts/2026-06-14-placeholder-full-write-up.md` documents the extras — the
`facts` table under the header and the `links` pill buttons
(`icon: external | github | file`).

One section rather than two, and now one treatment rather than two: the
difference between a write-up and a Sunday note is real, but it's a difference
in how much front matter an entry carries, not in URL and not in billing. A card
grid used to sit above the log for entries marked `featured: true`; it re-showed
entries the log already listed, so it's gone, and so are `featured` and `order`.
Everything is one dated log with newer/older links and `/feed.xml`.

### Works in progress

`_wip/<slug>.md` is the tier between `_drafts/` and `_posts/`: live at
`/posts/wip/<slug>/`, but `noindex`, out of `/sitemap.xml`, out of `/feed.xml`,
and listed only inside a collapsed drawer on `/posts/`. It exists so a rough
note can be published and iterated on without landing in the feed.

```sh
make wip TITLE="Something I want to think about in public"
# ... later, when it's finished:
make publish SLUG=something-i-want-to-think-about-in-public
```

The front matter is a post's, minus the date-in-the-filename convention. Give
every note a `date` in its front matter instead: the drawer sorts on it, and a
note without one falls back to sorting by filename. `layout`, `sitemap`,
`noindex`, and the kicker all come from the `wip` defaults scope in
`_config.yml` — don't set them per-note.

`make wip` also creates `_research/<slug>/` for the raw material behind a note:
data pulls, scripts, source notes. It's committed but never built — Jekyll skips
`_`-prefixed directories on its own, so it needs no `exclude:` entry.

`make publish` moves a note out of either `_wip/` or `_drafts/` and stamps
today's date onto the filename. Drop the now-redundant `date:` line from the
front matter afterwards; it reminds you.

## Writing from a phone

The reason `_wip/` exists. Start a Claude Code session at
[claude.ai/code](https://claude.ai/code) on this repo, paste a raw idea with no
other instruction, and it scaffolds the note, does a research pass, and opens a
PR. The PR runs the build and html-proofer, so a green tick is visible from the
GitHub mobile app — merge there and it deploys.

`CLAUDE.md` is what makes that work: a cloud session gets the repo's `CLAUDE.md`
and `.claude/`, and nothing from `~/.claude/`, so everything a session needs to
know is committed. `.claude/skills/wip-note/SKILL.md` owns the procedure.

Two settings have to be right on the cloud environment, and neither lives in the
repo:

- **Network access must be Full, or Custom with the data sources listed.** The
  default Trusted level reaches package registries, GitHub, and cloud SDKs only
  — not Census, arXiv, or a state data portal. The research half does nothing
  without it.
- Optionally a setup script installing analysis libraries; pandas is not
  preinstalled. It's cached as a filesystem snapshot, so it costs about once a
  week.

A cloud session can't build the site: `.ruby-version` pins 3.4 and those VMs
ship 3.1–3.3, so `bundle install` fails. That's deliberate — the session writes
Markdown and CI validates. `CLAUDE.md` says so, and lists the traps that a local
build would otherwise have caught.

## Deploys

Push to `master`. `.github/workflows/deploy.yml` builds with Jekyll 4, runs
html-proofer, and publishes to GitHub Pages. Failures show up as a workflow
log, not an email.

The same workflow runs on every pull request against `master`, but stops after
the build and the link check — no artifact, no deploy. So a branch gets a real
green tick before it merges, which is legible from a phone. `workflow_dispatch`
is still enabled for running it by hand from the Actions tab.

`jekyll-feed` generates `/feed.xml` and `jekyll-sitemap` generates
`/sitemap.xml`; the redirect stubs carry `sitemap: false` so they stay out of
it.

# ericvoss.com

A career landing page, a blog, and project write-ups, on a hand-written Jekyll
theme. No framework, no build step beyond Jekyll: the site ships as plain HTML,
one stylesheet, and one JavaScript file.

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
| `make publish DRAFT=<slug>` | Move a draft into `_posts/`, stamped with today's date |

Run `make check` before pushing. It catches broken internal links and missing
images, which is most of what actually breaks here.

## Where things live

| | |
|---|---|
| `_data/` | The content that repeats: `profile.yml` (name, tagline, portrait, links), `career.yml`, `education.yml`, `certifications.yml`, `skills.yml`, `focus.yml`, `archive.yml`, `navigation.yml`. Each file's header comment documents its fields. Edit these, not the markup. |
| `_posts/` | Blog entries, `YYYY-MM-DD-slug.md`, served at `/blog/<slug>/`. |
| `_drafts/` | Unfinished posts. Visible under `make serve`, never published. |
| `_portfolio/` | Project write-ups, served at `/projects/<slug>/`. |
| `_pages/` | The standalone pages — About, Projects, Blog — plus six redirect stubs preserving URLs from the pre-2026 site. |
| `_layouts/`, `_includes/` | The theme. `head.html` does canonical, OG, and Twitter card by hand. |
| `_sass/` | Nine partials, loaded in order by `assets/css/site.scss` and compiled to one minified `/assets/css/site.css`. Section numbering is load order. |
| `assets/` | `js/site.js`, the four self-hosted woff2 faces, images, favicons. |

### Adding a post

```sh
make draft TITLE="What I learned shipping an eval harness"
# write it, preview with `make serve`
make publish DRAFT=what-i-learned-shipping-an-eval-harness
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

### Adding a project

Copy `_portfolio/placeholder-one.md` to `_portfolio/<slug>.md` and fill it in.
It documents every field: the `facts` table under the header, the `links` pill
buttons (`icon: external | github | file`), tags, and the hero image. `order`
sorts the cards on `/projects/`, lowest first.

Small pieces of work that don't merit a page go in `_data/archive.yml` instead
and render as the collapsible list at the bottom of `/projects/`.

Posts and projects stay separate on purpose: posts get date ordering,
newer/older links, and the RSS feed at `/feed.xml` for free; projects get the
facts table and outbound links, and no date.

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

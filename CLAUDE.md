# Working on this repo

Read this before writing anything. It is the whole briefing — a session started
from the cloud gets this file, `.claude/`, and nothing else from my machine.

## What the site is

`ericvoss.com`: a career landing page and everything I write, on a hand-written
Jekyll theme. No framework, no build step beyond Jekyll — plain HTML, one
stylesheet, one JavaScript file. `README.md` has the fuller tour; the section
comments in `_sass/` and the header comments in `_data/*.yml` are the real
documentation and are worth reading before changing anything they describe.

**Anything with data in it is a marimo notebook.** That is the first-class way
things get written here now: the notebook is the source, and the page on the
site is generated from it. A piece of pure writing is still Markdown, because
wrapping prose in a Python file buys nothing. See "Notebooks" below — it is the
format contract, not an aside.

The `make` interface is the whole toolchain:

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
| `make fix` | Apply marimo's own formatting fixes |
| `make draft TITLE="..."` | Scaffold `_drafts/<slug>.md` — private |
| `make wip TITLE="..."` | Scaffold `_wip/<slug>.md` — an essay, no notebook |
| `make publish SLUG=<slug>` | Move a note out of `_wip/` or `_drafts/` into `_posts/` |

## Where things go

Getting this wrong is the most expensive mistake available, so:

| | |
|---|---|
| `_notebooks/` | **The source of an exploration.** `<slug>.py`, a marimo notebook. Never built; nothing serves it. The page under `_wip/` or `_posts/` is generated from it. |
| `_posts/` | **Finished.** `YYYY-MM-DD-slug.md`, live at `/posts/<slug>/`, in the sitemap, **in the RSS feed**. Publishing here notifies subscribers. |
| `_wip/` | **Live but quiet.** `<slug>.md`, live at `/posts/wip/<slug>/`, `noindex`, out of the sitemap, out of RSS, listed only inside a collapsed drawer under "AI drafts". **This is where a cloud session writes.** |
| `_drafts/` | **Private.** Visible under `make serve` and nowhere else. Never published, never deployed. |
| `_research/` | **Raw artifacts.** Data pulls, source notes, working files. Never built — Jekyll skips `_`-prefixed directories on its own. |
| `_bin/` | **Tooling.** `sync-notebook.py`, which `make sync` drives. Underscore-prefixed so it needs no `exclude:` entry — see trap 6. |

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

For a note backed by a notebook, the front matter is the *only* hand-written
part of the file. Everything under it is generated and carries a comment saying
so. Editing below that line is wasted work — the next `make sync` overwrites it.

## Notebooks

An exploration lives in `_notebooks/<slug>.py` and the page is built from it:

```sh
make notebook TITLE="A question with a number at the end of it"
make edit SLUG=<slug>        # marimo, --sandbox for the notebook's own deps
make run  SLUG=<slug>        # headless; redraws figures into assets/images/
make sync SLUG=<slug>        # regenerate the page body. Not optional.
```

`make sync` runs `marimo export md` over the notebook and splices the result
under the page's front matter, so **what you put in a cell decides whether it
reaches the site**:

| In the notebook | On the page |
|---|---|
| `mo.md("""...""")`, plain string literal | Rendered as prose |
| `mo.md(f"""...""")` | A code block showing the f-string. Never what you want. |
| A code cell | A ```` ```python ```` block |
| A code cell with `hide_code=True` | Nothing. Dropped. |
| Any cell's **output** | Nothing. Outputs are never exported. |

Three consequences worth stating outright:

- **`hide_code=True` is the publish control.** Imports, the matplotlib style
  block, path setup — hide them and the page stays readable. The code that
  carries the argument stays visible. `make sync` prints both counts every run,
  so this is never silent.
- **A figure reaches the page only as a committed PNG.** The template's
  `savefig` writes `assets/images/<slug>-<name>.png` and prints the exact
  Markdown line; a prose cell has to link it by hand. There is no path by which
  a chart appears just because a cell drew it.
- **Numbers get typed in.** Because an f-string is not a literal, the way to
  put a computed number in prose is to print it in a code cell, read it, and
  write it down. Every number in the prose must trace to a cell in that
  notebook.

Also: no `# Heading` at the top of the first prose cell. The layout renders
`page.title` as the h1 already, and `make sync` drops a leading one and tells
you it did.

Marimo's own contract applies too, because the notebook has to stay a DAG: no
cycles, exactly one owning cell per public name, no `import *`. Prefix
intermediates that nothing else reads with `_`.

Dependencies go in the notebook's **PEP 723 header**, not in `pyproject.toml`.
That file exists to provide the `marimo` CLI and nothing else, and the header is
why `make edit` passes `--sandbox` and `make run` works on a machine that has
never installed pandas.

## Rules for cloud sessions

**A bare idea dump with no other instruction means: run the `wip-note` skill.**
That is the default and it needs no confirmation. See
`.claude/skills/wip-note/SKILL.md`.

What I want back from one of these is **a minimal notebook I can open and pair
on**, not a finished piece. The scaffold is the start of my session, not a
replacement for it — so under-write it. Anything I have to delete first was
worse than nothing. The skill has the specifics and they are binding.

Beyond that:

- **Always branch and open a PR. Never push to `master`.** The PR check builds
  the site, runs html-proofer, and checks the notebooks; I merge from my phone
  once it is green.
- **Never edit a published `_posts/` entry** unless I ask for that specifically.
  Those went out on the feed already. (Syncing a notebook whose page has been
  published is the exception — that is the notebook's page, not a hand edit.)
- **Run `make sync` after every notebook change, and `make notebooks` before
  pushing.** Both are Python and both work here. A page that has drifted from
  its notebook fails the PR check, which is exactly the thing that stops me
  merging from a phone.
- **Do not run `make check`, `make build`, or `bundle install` here.** They will
  fail — see below. Use `make notebooks` for the half that does work.
- **Keep the raw braindump verbatim** at the top, in a `## The dump` section.
  It is the record of what I actually thought, and it is more useful later than
  a tidied paraphrase.
- **Cite sources inline** as Markdown links. Anything asserted as fact in a
  research note needs one.

## Ruby: why the session cannot build

`.ruby-version` pins **3.4**. Cloud VMs ship Ruby 3.1/3.2/3.3 under rbenv, so
`bundle install` fails out of the box and everything downstream of it —
`make build`, `make check`, `make serve` — fails with it. This is expected and
is not worth working around: building Ruby 3.4 from source does not fit the
setup budget, and relaxing the pin buys nothing the PR check does not already
give.

**Python is a different story.** `make notebooks`, `make sync`, and `make run`
need only uv and the `marimo` CLI, both of which install here fine, so the
notebook half of the gate is yours to run and there is no excuse for pushing a
notebook whose page has not been synced. If marimo genuinely cannot be
installed, do not scaffold a notebook at all — you would be committing a page
you cannot generate. Write the idea as an essay and say why in the PR body.

**So: push a branch and let CI validate the Ruby half.** The one class of error
a local build would catch that CI now catches instead is the Liquid trap below,
and catching that as a red PR check is fine, because the merge is manual anyway.

## Traps

Every one of these is silent or delayed. None of them is caught by review.

1. **Jekyll parses Liquid before Markdown — including inside fenced code
   blocks.** A note quoting anything containing `{{` or `{%` fails the build,
   and a research note is exactly the kind of writing that quotes templates,
   shell snippets with `${}`, or JSON with braces. Wrap the block in
   `{% raw %}` … `{% endraw %}`. **This is the most likely way a hand-written
   note breaks the site.** A notebook page does not have this problem —
   `make sync` wraps the whole generated body unconditionally, because
   generated Python trips it constantly — so this is a rule about Markdown you
   type yourself.

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

8. **A running marimo session owns its file.** During a live session the kernel
   is the source of truth and it rewrites `_notebooks/<slug>.py` on save, so an
   `Edit` or `Write` against that file does not reach the kernel and gets
   overwritten. Pair through the `marimo-pair` skill, which drives the live
   kernel instead. This is the expensive one: the work is gone with no error.

9. **`marimo-pair`'s `create_cell` defaults to `hide_code=True`,** and a hidden
   cell does not reach the page. A cell added during a pairing session is
   therefore invisible on the site by default, which is the opposite of what
   you usually want for analysis code. Pass `hide_code=False`. `make sync`
   prints the hidden count every run — if it climbs after a session, this is
   why.

10. **`mo.md(f"...")` is not prose.** Marimo only turns a cell into Markdown
    when the argument is a plain string literal; an f-string cannot be resolved
    statically, so the cell lands on the page as a code block showing the
    f-string source. It looks completely normal in the notebook UI. Print the
    value in a code cell and type it into the prose.

11. **The page body below the front matter is generated.** Editing
    `_wip/<slug>.md` under a notebook is wasted work — `make sync` overwrites
    it — and skipping the sync after a notebook change fails the PR check
    instead. The file says so in a comment; the check is `make notebooks`.

## Voice

The README, the section comments in `_sass/`, and the placeholder entries are
the tone reference. Plain, specific, and willing to say what something is not.
Explain *why* a thing is the way it is when the reason is not obvious from the
code — that is what every comment in this repo is doing. No marketing register,
no hedging, and no exclamation marks.

For a research note specifically: state what the data actually supports and
stop. If the answer is "this doesn't show what I hoped," write that down.

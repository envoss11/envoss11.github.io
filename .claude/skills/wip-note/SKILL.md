---
name: wip-note
description: Turn a raw idea dump into an AI draft on ericvoss.com — usually a minimal marimo notebook that Eric opens and pairs on afterwards, or a written essay when there is no data at the bottom of the idea — then open a PR. Use this whenever Eric hands over an idea, a question, a braindump, or a link with no other instruction — that alone is the trigger. Also use it for explicit asks like "start a note on X", "research X", or "/idea".
---

# Turning an idea dump into an AI draft

Eric has ideas away from a laptop and very little time at one. He dictates or
types a rough thought from a phone; you turn it into something already live and
already iterable, and he finishes it later. **Zero further typing should be
required from him.** Do not ask clarifying questions before starting — make the
call, build the thing, and say what you assumed. Ambiguity is what the note is
for.

Read `CLAUDE.md` first if you have not. The traps section is not optional, and
the "Notebooks" section is the format contract this skill depends on.

## What you are actually producing

**A scaffold he opens in marimo and pairs on — not a finished piece.**

That framing decides everything below. The thing you hand back is the starting
point of his session, not a substitute for it. He will open the notebook with
`make edit SLUG=<slug>`, and from there he and a local Claude Code session work
in the live kernel through the `marimo-pair` skill. Anything you write that he
has to delete first is worse than not writing it.

So the standard is **minimal**, and it is a hard rule rather than a preference:

- **A prose cell exists to carry a section of the structure below, or a
  finding inside one.** That is about six prose cells for a notebook; treat
  more with suspicion, and keep each one short.
- **No prose cell that narrates the next cell.** The code says what the code
  does. "First we load the data" is noise in a notebook and noise on the page.
- **No preamble, no throat-clearing, no summary of what is about to happen.**
  No "In this notebook we will", no "Let's explore", no closing section that
  restates the opening one.
- **Around a dozen cells total**, template plumbing included. The pull, the
  general checks, one distribution figure, and one question-specific look is a
  complete first pass. A second question-specific figure needs a reason.
- **Write no conclusion you have not earned.** If the data settled it, one
  sentence. If it did not, say the question is open and stop. Padding around an
  absent finding is the single worst thing you can hand back.
- **`## Next steps` is a short list, not an essay.** Approaches he could take
  further, concrete enough to start from — a prompt for him, not a plan you
  are committing him to.

Everything you are tempted to add belongs in the next interaction, after he has
looked at it. Under-writing costs him one message; over-writing costs him a
cleanup.

None of this applies to the *research*. Go as deep as the sources allow — the
minimality is about what you write down, not about how hard you looked.

## The structure

Every note — notebook or essay — has exactly these sections, in this order,
every time:

0. **`## The dump`** — the raw idea, verbatim, blockquoted. Step 1 of the
   procedure below; nothing goes above it.
1. **`## The question(s)`** — the specific, answerable questions the analysis
   is trying to settle. If the dump already asks them clearly, use its wording
   with minimal edits. If it does not, do the converting yourself — turn the
   dump into questions the data could actually answer — and say in the PR body
   that you did.
2. **`## The data`** — the data sources that could bear on the question(s):
   list them, a line each on what they cover, then which one(s) you actually
   pulled for this analysis and why. A rejected source keeps its reason —
   "too coarse", "paywalled", "stops in 2019" — because the rejection is
   research he would otherwise redo.
3. **`## EDA`** — exploratory analysis of the chosen data. General first:
   data quality, coverage, missingness, the distributions of the key
   variables. Then whatever bears on the question(s) specifically, if the data
   supports a first look. The pull, the checks, and the figures all live here,
   and so does what the data *doesn't* show — the confounds, the gaps, the
   sample you wish you had.
4. **`## Next steps`** — deeper analysis approaches that might prove fruitful
   in answering the question(s). A short list, concrete enough to start from.

An essay follows the same structure. Without a notebook underneath them the
sections read differently, but they keep their names: `## The question(s)` is
what the argument would have to settle to hold; `## The data` surveys the
sources that could bear on it — including the dataset that would settle it
and does not exist, which is a finding; `## EDA` is the close look at the
evidence you did find — the concrete instance, the named disagreement, what
each supports and what it doesn't. `## Next steps` is the same list either
way: what a deeper pass would do.

## The procedure

### 1. Capture the dump verbatim

Before anything else, before any research, write the raw text down exactly as
given. Do not clean it up, reorder it, or fix the grammar — it is the record of
what he actually thought, and it is more useful in three weeks than a tidied
paraphrase would be.

It goes in a `## The dump` section at the top, blockquoted. In a notebook that
is the first `mo.md` cell; in an essay it is the first section.

### 2. Decide which shape this is

**An exploration is a notebook.** A question with a number at the end of it, a
dataset that could answer it, and a chart that settles the argument faster than
a paragraph would. This is the default and the one the site is built around.

**An essay is Markdown.** A position, a distinction, a reflection on how
something actually goes wrong. It can be entirely technical — "what enterprise
AI risk registers keep leaving out" is an essay — it just has no dataset at the
bottom of it, and no reason to be wrapped in a Python file.

The test is one question: **is there something here you could settle by running
code against data you can actually get?** Then the edges:

- One number to look up is not an exploration. Cite it and write prose. A
  notebook to carry a single statistic is machinery around a sentence.
- An idea that wants data nobody publishes is an essay about a question. Name
  the dataset that would settle it and say it does not exist — that is a
  finding.
- If it is honestly both, take the half the dump spends more words on and put
  the other in `## Next steps`. Something attempting both does neither.

Say which one you picked, and why, in the PR body.

### 3. Scaffold

Derive a slug from the idea: lowercase, hyphens, no articles, short enough to
read in a URL.

**An exploration:**

```sh
make notebook TITLE="The question, as a question"
```

That writes `_notebooks/<slug>.py` from the template with `SLUG` filled in,
`_wip/<slug>.md` with front matter and a generated body, and
`_research/<slug>/`. If `make` is unavailable, do the same three things by hand
— copy `.claude/skills/wip-note/notebook-template.py`, set `SLUG`, and run
`python3 _bin/sync-notebook.py <slug>`.

**An essay:**

```sh
make wip TITLE="The claim, as a claim"
```

Front matter either way is `title`, `date` (**required here** — there is no
date in the filename), `excerpt`, and `tags_list`. Nothing else, with one
exception: an exploration with a lead chart may set `image` and
`image_fit: contain`, which letterboxes it instead of cropping it. `layout`,
`permalink`, `sitemap`, `noindex`, and the kicker all come from the `wip`
defaults scope in `_config.yml`; setting them by hand is an error.

The date is today's, in `YYYY-MM-DD`. Never a future date — `future: false` is
Jekyll's default and a forward-dated entry silently does not publish.

### 4. Research

This is the half that makes it worth opening, and it applies to both shapes.
Work out what would have to be true for the idea to hold, then go and check.

- Find real sources. Prefer primary data — a statistical agency, a published
  dataset, a paper, the actual documentation — over somebody's summary of it.
- Keep the survey, not just the winner. Every source you seriously considered
  goes in `## The data` with a line on what it covers, and the one(s) you
  pulled get the why.
- Pull data down in the notebook itself, or into `_research/<slug>/` for an
  essay. Commit the code that pulled it, so the number can be re-derived.
- Cite everything inline as Markdown links. Any sentence asserting a fact needs
  one behind it.
- Note what you *could not* find. A gap in the evidence is a finding.

For an essay, two more, because an essay has no data to keep it honest:

- **Find the concrete instance.** A reflection on enterprise AI risk is worth
  nothing without a named incident, a specific regulation, or a real system.
  One real case is worth five paragraphs of general caution.
- **Find who disagrees, by name.** Not a strawman you built — a person or an
  organisation that argues the other way, quoted and linked. If you cannot find
  one, that is worth saying too, and usually means the claim is weaker than it
  looks rather than stronger.

Network access has to be set to Full or Custom for this to work; on Trusted the
research half silently gets nowhere. If sources are unreachable, say so plainly
at the top rather than writing around it.

### 5. Write the notebook

Skip this section for an essay and write Markdown instead — the same five
sections in the same order (see "The structure" above for how they read
without a notebook), and the same minimality rule does *not* apply, because
an essay under about 500 words is a paragraph with headings on it and has not
made its argument yet. An essay is the one thing here you should write in full.

For a notebook, the sections and their order are fixed — see "The structure"
above. Within them, the format contract in CLAUDE.md is what decides whether
your work reaches the page at all. The four rules that matter most:

- **Prose is `mo.md("""...""")` with a plain string literal.** An f-string is
  not a literal — marimo cannot resolve it statically, so `mo.md(f"...")` lands
  on the page as a code block showing the f-string. Compute the number in a
  code cell, print it, read the printed value, and type it into the prose.
- **`hide_code=True` means the cell does not reach the page.** That is the
  control for keeping plumbing off the site: imports, the style block, path
  setup. The code that carries the argument stays visible. `make sync` prints
  both counts every run.
- **Cell outputs never reach the page.** A chart gets there by `savefig`
  writing a PNG into `assets/images/` and a prose cell linking it by hand.
- **No `# Heading` at the top.** The layout renders the title already.

Then marimo's own contract, which is not optional because the notebook has to
stay a DAG: no cycles, one owning cell per public name, no `import *`. Use
`_name` for intermediates nothing else reads.

Every number the prose asserts has to come from a cell in that notebook.

**Check whether you can run it before you plan on it:**

```sh
make run SLUG=<slug>     # uv run --script; reads the PEP 723 header
```

- **If it runs:** it writes the figures and prints the exact Markdown line to
  paste. Commit the PNGs under `assets/images/` and reference them from a prose
  cell.
- **If it does not run: commit the notebook and reference no figures at all.**
  A page pointing at an image that is not in the repo turns html-proofer red
  and blocks the merge — trap 4. Say at the top that the analysis has not been
  run, repeat it in the PR body, and do not quote a number you have not
  computed.

Voice: plain and specific, per CLAUDE.md. State what the evidence supports and
stop. "This doesn't show what I hoped" is a legitimate and useful conclusion.

### 6. Sync, and check your own work

**`make sync SLUG=<slug>` is not optional for a notebook.** The page body is
generated from the notebook, CI re-runs the export and compares, and a PR whose
page has drifted from its notebook goes red — which is the one thing that stops
him merging from a phone.

You cannot build the site (see the Ruby section in CLAUDE.md), but the notebook
half of the gate is Python and you can run all of it:

```sh
make notebooks     # marimo check --strict, then the drift check
```

If marimo cannot be installed at all, do not scaffold a notebook — you would be
committing a page you cannot generate. Write the idea as an essay instead and
say why in the PR body.

Then check the rest by reading:

- **Any `{{` or `{%` in an *essay* body — including inside fenced code blocks —
  must be wrapped in `{% raw %}` … `{% endraw %}`.** Trap 1. A notebook page is
  already wrapped by `make sync`, so this applies to hand-written Markdown only.
- Every image referenced exists as a file you are committing, and every one has
  real alt text. The check fails on a missing file, on missing `alt`, on an
  `alt` that is empty or all spaces, and on a filename that still looks like
  `Screen Shot 2026-08-17 at 9.41.02.png`. All four are failures, not warnings.
- Every internal link resolves. A link to a page you meant to write next turns
  the check red too.
- Every number in the prose matches what the notebook actually printed.
- No forward date.
- Front matter is valid YAML: a `title` containing a colon needs quoting.

### 7. Branch, commit, PR

- Branch: `wip/<slug>`.
- Commit `_notebooks/<slug>.py`, `_wip/<slug>.md`, everything under
  `_research/<slug>/`, and any figures under `assets/images/<slug>-*.png`.
- **Those four paths are the whole diff.** This PR does not touch
  `_config.yml`, `_layouts/`, `_includes/`, `_sass/`, `_bin/`, `Makefile`,
  `CNAME`, or anything under `.github/`. If it genuinely seems to need one of
  those, do not make the change — say what it needs and why in the PR body and
  leave it to him. The point is that the diff can be approved from a phone at a
  glance, so anything outside those four paths is worth stopping over however
  good the reason sounds.
- Open a PR against `master`. **Never push to `master` directly.**
- PR body: which shape this is and why, what the idea was, what the research
  found, whether the notebook ran, and what is still open. It is what he reads
  on a phone before merging.

Then tell him the PR link, the URL it will live at once merged
(`/posts/wip/<slug>/`), and anything you assumed or could not check.

## Iterating

A follow-up about something that already exists means: push another commit to
the same branch. Do not open a second PR, and do not start a second note unless
the follow-up is plainly a new idea.

Two things to keep in mind when you come back to a notebook:

- **If he is in a live marimo session, you are not editing the file.** The
  running kernel is the source of truth and file edits do not reach it. That is
  the `marimo-pair` skill's territory, and it uses `marimo._code_mode` against
  the live kernel instead. Editing `_notebooks/<slug>.py` underneath a running
  session loses work.
- **Otherwise edit the file and re-run `make sync`.** Every time. The page does
  not regenerate itself.

A follow-up that turns an essay into an exploration — "actually, can we get
data on this" — stays on the same branch. Run `make notebook` for the slug,
move the prose into `mo.md` cells, and delete the hand-written `_wip/<slug>.md`
body so `make sync` owns it.

## When it is finished

Promotion out of the drawer is a laptop job and he will usually do it himself.
If he does ask: `make publish SLUG=<slug>` moves the page to
`_posts/YYYY-MM-DD-<slug>.md`, and the `date:` line comes out of the front
matter because the filename carries it from then on. That is the point at which
it enters the RSS feed, so it is never something to do unprompted.

The notebook does not move — it stays in `_notebooks/` and `make sync` follows
the page into `_posts/`. `_research/` and the figures stay where they are too.

---
name: wip-note
description: Turn a raw idea dump into a researched work-in-progress note on ericvoss.com — either a data exploration with a committed analysis script, or a written essay — then open a PR. Use this whenever Eric hands over an idea, a question, a braindump, or a link with no other instruction — that alone is the trigger. Also use it for explicit asks like "start a note on X", "research X", or "/idea".
---

# Turning an idea dump into a WIP note

The point of this is that Eric has ideas away from a laptop and very little time
at one. He dictates or types a rough thought from a phone; you turn it into a
researched note that is already live and already iterable, and he finishes it
later. **Zero further typing should be required from him.** Do not ask
clarifying questions before starting — make the call, write the note, and say
what you assumed. Ambiguity is what the note is for.

Read `CLAUDE.md` first if you have not. The traps section is not optional.

## The procedure

### 1. Capture the dump verbatim

Before anything else, before any research, write the raw text down exactly as
given. Do not clean it up, reorder it, or fix the grammar — it is the record of
what he actually thought, and it is more useful in three weeks than a tidied
paraphrase would be.

It goes in a `## The dump` section at the top of the note body.

### 2. Decide which kind of note this is

Two shapes. They share the capture, the sourcing, the checks and the PR, and
they diverge on everything in between — so decide before you scaffold, not
halfway through writing.

**An exploration** is the traditional data-science post: a question with a number
at the end of it, a dataset that could answer it, and a chart that settles the
argument faster than a paragraph would. It ships with a committed analysis script
and the figures that script drew.

**An essay** is a piece of writing: a position, a distinction, a reflection on
how something actually goes wrong. It can be entirely technical — "what
enterprise AI risk registers keep leaving out" is an essay — it just has no
dataset at the bottom of it. It ships with an argument and its sources.

The test is one question: **is there something here you could settle by running
code against data you can actually get?** Then the edges:

- One number to look up is not an exploration. Cite it and keep writing prose.
  A script and a chart to carry a single statistic is machinery around a sentence.
- An idea that wants data nobody publishes is an essay about a question. Name the
  dataset that would settle it and say it does not exist — that is a finding.
- If it is honestly both, take the half the dump spends more words on and put the
  other in "Where this goes." A note that attempts both does neither.

Do not invent a front-matter field for this. The table in `CLAUDE.md` is the whole
schema, and the shape of a note is obvious from reading it. Say which one you
picked, and why, in the PR body.

### 3. Pick a slug and scaffold

Derive a slug from the idea: lowercase, hyphens, no articles, short enough to
read in a URL. Then:

- `_wip/<slug>.md` — the note.
- `_research/<slug>/` — the working directory. Create it either way; a directory
  with only a `notes.md` in it is fine, and Jekyll never looks at it.

An exploration also gets `analysis.py` and `requirements.txt` in there — step 5.

Front matter is `title`, `date` (**required here** — there is no date in the
filename), `excerpt`, and `tags_list`. Nothing else, with one exception: an
exploration with a lead chart may set `image` and `image_fit: contain`, which
letterboxes it instead of cropping it. `layout`, `permalink`, `sitemap`,
`noindex`, and the kicker all come from the `wip` defaults scope in
`_config.yml`; setting them by hand is an error.

The date is today's, in `YYYY-MM-DD`. Never a future date — `future: false` is
Jekyll's default and a forward-dated entry silently does not publish.

### 4. Research

This is the half that makes the note worth reading, and it applies to both
shapes. Work out what would actually have to be true for the idea to hold, then
go and check.

- Find real sources. Prefer primary data — a statistical agency, a published
  dataset, a paper, the actual documentation — over somebody's summary of it.
- Pull data down into `_research/<slug>/` when there is data to pull. Commit the
  script that pulled it, not just the output, so the number can be re-derived.
- Cite everything inline as Markdown links. Any sentence asserting a fact needs
  one behind it.
- Note what you *could not* find. A gap in the evidence is a finding and belongs
  in the note.

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
at the top of the note rather than writing around it.

### 5. The analysis, if it is an exploration

Skip this whole section for an essay.

**Copy the two templates out of this skill's directory** — `analysis-template.py`
to `_research/<slug>/analysis.py` and `requirements-template.txt` to
`_research/<slug>/requirements.txt` — and edit them. Do not start from a blank
file: the template carries the site's chart palette, the repo-root lookup, and a
`savefig` that puts figures where Jekyll can serve them.

`analysis.py` is a plain `.py` in jupytext `# %%` cell format, not an `.ipynb`,
and that is deliberate. VS Code and PyCharm open it as a notebook with no
conversion and Jupyter opens it with jupytext, so it is still a notebook at a
laptop — but its diff is readable in the GitHub mobile app, and its outputs
cannot quietly drift out of sync with the code the way a committed `.ipynb`'s do.
Picking it up later is two commands, which is the whole point:

```sh
pip install -r requirements.txt && python analysis.py
```

Every number the note asserts has to come out of that script, and every figure in
the prose has to have the cell that drew it sitting in the script. Commit the raw
data next to it if it is small; if it is not, commit only the fetch and say in a
comment where it came from and how big it is.

**Check whether you can run any of this before you plan on it:**

```sh
python3 -c "import pandas, matplotlib"
```

A cloud VM does not have these unless a setup script installed them.

- **If it runs:** save the figures through the template's `savefig`, commit the
  PNGs under `assets/images/`, and embed them.
- **If it does not run: commit the script and embed no figures at all.** A note
  pointing at an image that is not in the repo turns html-proofer red and blocks
  the merge — see trap 4. Describe what the script will produce, say at the top
  of the note that the analysis has not been run yet, repeat that in the PR body,
  and do not quote a number you have not computed.

Leave the template's style block alone. It is dark because the site is not: the
theme flips between night glass and day parchment on a `data-theme` toggle and a
PNG cannot follow it, so a figure is a screen set into the page instead — which
is how `.prose p:has(> img)` already frames every image. Put each figure in a
paragraph of its own so it gets that slot, and give every one real alt text.

### 6. Write the note

An exploration:

```
## The dump              <- verbatim, untouched
## The question          <- what would have to be true, put as something checkable
## What the data says    <- the figures and numbers, each traceable to a cell
## What it doesn't show  <- the confounds, the sample you wish you had
## Where this goes
```

An essay:

```
## The dump                 <- verbatim, untouched
## The argument             <- one sentence you could be wrong about, then the case
## The strongest objection  <- named and sourced, not a strawman
## Where this goes
```

Voice: plain and specific, per CLAUDE.md. State what the evidence supports and
stop. "This doesn't show what I hoped" is a legitimate and useful conclusion —
write it down rather than padding around it.

Length: enough to be worth opening, not a finished essay. This is a note, and the
drawer it lands in says so. An exploration can be short because the figures carry
it. An essay cannot: under about 500 words it is a paragraph with headings on it,
and the argument has not been made yet.

### 7. Check your own work before pushing

You cannot build (see the Ruby section in CLAUDE.md), so check by reading:

- **Any `{{` or `{%` anywhere in the body — including inside fenced code blocks
  — must be wrapped in `{% raw %}` … `{% endraw %}`.** Jekyll parses Liquid
  before Markdown and does not care that it is inside a fence. This is the
  single most likely way the note breaks the build, and quoting a shell snippet
  with `${}` in it counts.
- Every image the note references exists as a file you are committing, and every
  one has real alt text. The image check fails on a missing file, on a missing
  `alt`, on an `alt` that is empty or all spaces, and on a filename that still
  looks like `Screen Shot 2026-08-17 at 9.41.02.png`. All four are failures, not
  warnings, and CI passes no ignore flags.
- Every internal link resolves to a page that exists. A link to a page you meant
  to write next turns the check red too.
- Every number in the prose matches what the script actually printed.
- No forward date.
- Front matter is valid YAML: a `title` containing a colon needs quoting.

### 8. Branch, commit, PR

- Branch: `wip/<slug>`.
- Commit `_wip/<slug>.md`, everything under `_research/<slug>/`, and any figures
  under `assets/images/<slug>-*.png`.
- **Those three paths are the whole diff.** A wip-note PR does not touch
  `_config.yml`, `_layouts/`, `_includes/`, `_sass/`, `CNAME`, or anything under
  `.github/`. If the note genuinely seems to need one of those, do not make the
  change — say what it needs and why in the PR body and leave it to him. The
  point is that the diff can be approved from a phone at a glance, so anything
  outside those three paths is worth stopping over however good the reason in
  the PR body sounds.
- Open a PR against `master`. **Never push to `master` directly.**
- PR body: which of the two kinds of note this is and why, what the idea was,
  what the research or the analysis found, whether the script ran, and what is
  still open. It is what he reads on a phone before merging.

Then tell him the PR link, the URL the note will live at once merged
(`/posts/wip/<slug>/`), and anything you assumed or could not check.

## Iterating

A follow-up message about a note that already exists means: push another commit
to the same branch. Do not open a second PR, and do not start a second note
unless the follow-up is plainly a new idea.

A follow-up that turns an essay into an exploration — "actually, can we get data
on this" — stays on the same branch and the same note. Add step 5 to it and swap
the headings for the exploration set.

## When it is finished

Promotion out of the drawer is a laptop job and he will usually do it himself.
If he does ask: `make publish SLUG=<slug>` moves the file to
`_posts/YYYY-MM-DD-<slug>.md`, and the `date` line comes out of the front matter
because the filename carries it from then on. That is the point at which it
enters the RSS feed, so it is never something to do unprompted. `_research/` and
the figures stay where they are; nothing about them moves.

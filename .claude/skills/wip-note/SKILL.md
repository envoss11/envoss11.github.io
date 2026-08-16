---
name: wip-note
description: Turn a raw idea dump into a researched work-in-progress note on ericvoss.com, then open a PR. Use this whenever Eric hands over an idea, a question, a braindump, or a link with no other instruction — that alone is the trigger. Also use it for explicit asks like "start a note on X", "research X", or "/idea".
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

### 2. Pick a slug and scaffold

Derive a slug from the idea: lowercase, hyphens, no articles, short enough to
read in a URL. Then:

- `_wip/<slug>.md` — the note.
- `_research/<slug>/` — the working directory. Create it even if you are not
  sure you will use it; a directory with only a `notes.md` in it is fine, and
  Jekyll never looks at it.

Front matter is `title`, `date` (**required here** — there is no date in the
filename), `excerpt`, and `tags_list`. Nothing else. `layout`, `permalink`,
`sitemap`, `noindex`, and the kicker all come from the `wip` defaults scope in
`_config.yml`; setting them by hand is an error.

The date is today's, in `YYYY-MM-DD`. Never a future date — `future: false` is
Jekyll's default and a forward-dated entry silently does not publish.

### 3. Research

This is the half that makes the note worth reading. Work out what would actually
have to be true for the idea to hold, then go and check.

- Find real sources. Prefer primary data — a statistical agency, a published
  dataset, a paper, the actual documentation — over somebody's summary of it.
- Pull data down into `_research/<slug>/` when there is data to pull. Commit the
  script that pulled it, not just the output, so the number can be re-derived.
- Cite everything inline as Markdown links. Any sentence asserting a fact needs
  one behind it.
- Note what you *could not* find. A gap in the evidence is a finding and belongs
  in the note.

Network access has to be set to Full or Custom for this to work; on Trusted the
research half silently gets nowhere. If sources are unreachable, say so plainly
at the top of the note rather than writing around it.

### 4. Write the note

Structure that has been working:

```
## The dump          <- verbatim, untouched
## What I found      <- the research, with sources
## Where this goes   <- what would make it a real post, and what is still open
```

Voice: plain and specific, per CLAUDE.md. State what the evidence supports and
stop. "This doesn't show what I hoped" is a legitimate and useful conclusion —
write it down rather than padding around it.

Length: enough to be worth opening, not a finished essay. This is a note, and
the drawer it lands in says so.

### 5. Check your own work before pushing

You cannot build (see the Ruby section in CLAUDE.md), so check by reading:

- **Any `{{` or `{%` anywhere in the body — including inside fenced code blocks
  — must be wrapped in `{% raw %}` … `{% endraw %}`.** Jekyll parses Liquid
  before Markdown and does not care that it is inside a fence. This is the
  single most likely way the note breaks the build.
- Every internal link resolves to a page that exists. html-proofer gates the
  deploy and a link to a page you meant to write next turns the check red.
- No forward date.
- Front matter is valid YAML: a `title` containing a colon needs quoting.

### 6. Branch, commit, PR

- Branch: `wip/<slug>`.
- Commit both `_wip/<slug>.md` and everything under `_research/<slug>/`.
- Open a PR against `master`. **Never push to `master` directly.**
- PR body: one paragraph on what the idea was, what the research found, and what
  is still open. It is what he reads on a phone before merging.

Then tell him the PR link, the URL the note will live at once merged
(`/posts/wip/<slug>/`), and anything you assumed or could not check.

## Iterating

A follow-up message about a note that already exists means: push another commit
to the same branch. Do not open a second PR, and do not start a second note
unless the follow-up is plainly a new idea.

## When it is finished

Promotion out of the drawer is a laptop job and he will usually do it himself.
If he does ask: `make publish SLUG=<slug>` moves the file to
`_posts/YYYY-MM-DD-<slug>.md`, and the `date` line comes out of the front matter
because the filename carries it from then on. That is the point at which it
enters the RSS feed, so it is never something to do unprompted.

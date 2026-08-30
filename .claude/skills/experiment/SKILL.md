---
name: experiment
description: Turn a raw idea that needs something run into an AI draft on ericvoss.com — build a small harness in _research/<slug>/, run the experiment where the environment allows, and analyze the results in a minimal marimo notebook, then open a PR. Use this when Eric's idea dump is about generating results rather than analyzing existing data — deploying and testing open-source models, benchmarking tools against each other, measuring what a system actually does. For a question that data somebody already publishes could answer, use the `data-analysis` skill instead; `/idea` routes between the two.
---

# Turning an idea dump into an experiment draft

The same deal as the `data-analysis` skill, and read that one first — its
posture is this one's posture: no clarifying questions, capture the dump
verbatim, a minimal scaffold he pairs on rather than a finished piece, the
same format contract, the same branch-and-PR rules. This file covers only
what an experiment does differently.

This skill is the newer of the two and intentionally rough. When its rules
collide with reality, do the sensible thing and say what you did in the PR
body — that is how it gets refined.

## What an experiment is here

A data analysis asks a question of data somebody already published. An
experiment generates its own: deploy the things, run them against inputs you
chose, record what happened, analyze that. "Which of these open-source OCR
models actually reads a scanned receipt" is an experiment; nobody publishes
that table, but an afternoon of running them produces it.

The deliverable is the same WIP note. The difference is that
`_research/<slug>/` carries a runnable harness and the raw outputs it
produced, and the notebook reads those outputs instead of pulling a public
dataset.

## The split that keeps it honest

- **The harness lives in `_research/<slug>/` as plain scripts**, committed
  alongside the raw outputs they produced (CSV, JSON, logs). Anyone reading
  the repo should be able to see exactly what was run, with which versions,
  on which inputs.
- **The notebook reads committed outputs; it does not run the experiment.**
  `make run` has to stay cheap and deterministic — a page whose numbers
  depend on re-deploying a model is not reproducible, and the notebook's
  PEP 723 header should carry analysis dependencies only, not the
  experiment's.
- **Versions are part of the result.** Model checkpoints, package versions,
  the hardware it ran on. An experiment result without its versions is an
  anecdote.
- **Inputs are part of the experiment.** Commit them when they are small
  enough to live in the repo; otherwise commit the script that fetched them
  and say exactly where they came from.

## The structure

The same five-beat shape as a data analysis, with the middle two sections
renamed for what an experiment actually has:

0. **`## The dump`** — the raw idea, verbatim, blockquoted.
1. **`## The question(s)`** — minimal edits if the dump asks them clearly;
   otherwise convert the dump into specific, answerable questions and say in
   the PR body that you did.
2. **`## The setup`** — the candidates considered (models, tools, methods), a
   line each; which you actually ran and why; versions, inputs, environment,
   and what was measured. A rejected candidate keeps its reason.
3. **`## Results`** — EDA of the experiment's outputs. Sanity checks first —
   did every run complete, are the outputs the shape you expected — then the
   comparisons that bear on the question(s). What the results *don't* show
   belongs here too: the inputs you didn't cover, the settings you didn't
   sweep.
4. **`## Next steps`** — deeper or better-controlled experiments worth
   running. A short list, concrete enough to start from.

Scaffold with `make notebook` like any other note — the template is shared
with the data-analysis skill — then rename the `## The data` and `## EDA`
headings in the prose cells to `## The setup` and `## Results`.

## Running it, honestly

Design the smallest experiment that answers the question. Two models on
twenty inputs with one metric is a complete first pass; a sweep is a next
step, not a first pass.

Then be realistic about the environment. A cloud session may not have the
disk, the memory, or the network access a model deploy needs. Find out by
trying the smallest piece first, and let the result decide:

- **If it runs:** commit the harness, the raw outputs, and the analysis.
  Every number in the prose traces to a cell that read a committed output
  file.
- **If it cannot run here:** commit the harness anyway, run nothing, and
  quote no numbers. Say plainly in the note and the PR body that the harness
  is unrun and what it needs to run. An unrun harness he can execute is a
  good scaffold; invented results are worse than nothing.

Everything else — `make sync` after every notebook change, `make notebooks`
before pushing, branch `wip/<slug>`, the four-path diff, PR against
`master` — is exactly as the `data-analysis` skill says, with one addition to
the commit list: the harness and its outputs under `_research/<slug>/` are
part of the deliverable, not scratch.

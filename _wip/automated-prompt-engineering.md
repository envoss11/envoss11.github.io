---
title: "What Automated Prompt Optimizers Are Actually Beating"
date: 2026-08-18
excerpt: "Fifty published head-to-head comparisons of hand-written prompts against DSPy-style optimizers. The optimizer wins about seven times in ten whoever it is up against — but the margin falls from +17 points against a default prompt to roughly nothing against a tuned one."
tags_list:
  - "Prompt Engineering"
  - "LLMs"
  - "Meta-analysis"
image: /assets/images/automated-prompt-engineering-margin-by-baseline.png
image_fit: contain
---

## The dump

> On the efficacy of automated prompt engineering; it seems to me that there is
> a drawback, LLMs are trained to mimic human thought patterns and you're
> basically sacrificing the advantage of that common language by taking the
> human out of prompt engineering  - the human practitioners basic intuition for
> what ought to work actually carries a lot of weight, since the human and the
> LLM share a lot of the same training data, so to speak.

## The question

The dump makes two claims that come apart under pressure, and only one of them
is checkable with data that exists.

The first is an outcome claim: taking the human out of prompt engineering costs
you something measurable. The second is a mechanism claim: it costs you
something *because* the practitioner and the model were trained on overlapping
text, so the practitioner's sense of what phrasing ought to work is a real prior
on what will.

The outcome claim has a testable consequence. Every paper proposing an
automated prompt optimizer reports a gain over some human-written prompt. If the
practitioner's intuition carries weight, that gain should shrink as the human on
the other side of the comparison gets better — and the papers vary enormously in
who that human is. Some compare against a one-line signature docstring nobody
iterated on. One compares against the best of sixty hand-written variants.
One compares against twenty hours of an expert's work.

So: **collect the published head-to-heads, and sort them by how hard the human
tried.**

One thing up front, because it shapes everything below. This is a meta-analysis,
not an experiment. Running DSPy against a human prompt for real needs an LLM API
budget this session did not have, so what follows re-reads comparisons other
people already ran and published rather than controlling them. The rerun that
would actually settle it is written out at the end.

The corpus is fifty paired comparisons from seven sources published between 2022
and 2026, transcribed by hand from results tables into
[`head-to-head.csv`](https://github.com/envoss11/envoss11.github.io/blob/master/_research/automated-prompt-engineering/head-to-head.csv);
every row carries the URL of the paper it came from. There is no machine-readable
corpus of "human prompt vs. optimized prompt" pairs to download, which is itself
worth noticing. Each row is binned by how strong the human baseline was —
`default`, `tuned`, or `expert` — and that binning is the one judgement call in
the dataset. Every assignment is defended in
[`notes.md`](https://github.com/envoss11/envoss11.github.io/blob/master/_research/automated-prompt-engineering/notes.md).

## What the data says

The optimizer wins 72% of the fifty comparisons. Sorting by how hard the human
tried barely moves that.

![Stacked bars showing optimizer wins, ties and human wins across three tiers of human baseline: 25 of 33 against a default prompt, 10 of 14 against a tuned prompt, and 1 of 3 against an expert prompt.](/assets/images/automated-prompt-engineering-win-rate.png)

Against a default prompt the optimizer wins 25 of 33. Against the best of a
deliberate human search it wins 10 of 14. The expert tier has three rows in it
and settles nothing. On win rate alone, the dump's outcome claim looks wrong:
the optimizer beats good prompts about as reliably as it beats bad ones.

The margin is a different story.

![Dot plot of optimizer-minus-human margins in points, split by baseline strength. Default baselines cluster between +8 and +47 with a mean of +16.7; tuned baselines cluster tightly around zero with a mean of +3.4; the two expert comparisons sit at -4.25 and +0.03.](/assets/images/automated-prompt-engineering-margin-by-baseline.png)

Against a default human prompt the optimizer gains a mean of **+16.7 points**.
Against a tuned one, **+3.4**. Against the two expert comparisons where the
margin is measured on the same split, **-2.1**. The wins do not stop; they stop
being worth anything.

The two ends of that range are worth naming, because the gap between them is not
subtle. [Opsahl-Ong et al.'s MIPRO benchmark](https://arxiv.org/abs/2406.11695)
reports +47.4 points on Heart Disease and +36.7 on Iris — and the human baseline
there is the DSPy signature docstring, which for Iris reads, in full, "Given the
petal and sepal dimensions in cm, predict the iris species." The authors are
explicit that the Heart Disease gain is large because their seed instruction
"does not convey any classification criteria". At the other end,
[Battle and Gollapudi](https://arxiv.org/abs/2402.10949) evaluated 60
hand-written "positive thinking" system messages on GSM8K, kept the best one,
and put it up against an automatic optimizer across three models and four
sample sizes. The optimizer won 8 of those 12 and lost 2, at a mean margin of
3.4 points.

And [APE's zero-shot chain-of-thought result](https://arxiv.org/abs/2211.01910),
the single cleanest case in the literature of a human idea and an automated
search stacked on the same task:

![Stacked bars for MultiArith and GSM8K showing the accuracy gained over no prompt at all: +61.0 and +30.3 from the human-written 'Let's think step by step', then +3.3 and +2.3 more from automated search over that prompt.](/assets/images/automated-prompt-engineering-invention-vs-refinement.png)

Kojima et al.'s "Let's think step by step" took text-davinci-002 from 17.7 to
78.7 on MultiArith and from 10.4 to 40.7 on GSM8K. APE then searched for a better
answer prefix and found "Let's work this out in a step by step way to be sure we
have the right answer", worth another 3.3 and 2.3 points. Pooled, the human idea
was worth **16 times** what the automated refinement of it was worth — and APE
improved on only 6 of the 12 tasks it tried this on.

The single best-documented expert comparison points the other way, and it is
the one the dump has to answer.
[The Prompt Report's case study](https://arxiv.org/abs/2406.06608) has an expert
prompt engineer — the author of a widely used prompting guide — spend about 20
hours across 47 recorded steps on detecting entrapment in Reddit posts, reaching
F1 0.53. DSPy, over 16 iterations, reached 0.548 on the test set, and the paper
says plainly that it "performs much better than the human prompt engineer's
prompts on the test set".

Read the components rather than the F1, though, and the two systems are not the
same system. The human's prompt ran 0.86 precision at 0.38 recall. DSPy's ran
0.385 precision at 0.952 recall. On a suicide-risk screening task those are
opposite products with a similar harmonic mean, and the metric the optimizer was
handed could not tell them apart. That is not a point about optimizers being
bad. It is a point about what the human contributed that never appeared in the
comparison.

## The mechanism, and why it isn't the one in the dump

The dump's mechanism is shared training data: the practitioner and the model
read the same internet, so the practitioner's ear for what phrasing will land is
a real signal. Everything I could find says the opposite about *wording*, and
something like the opposite of the opposite about *specification*.

Against the mechanism as stated, three findings:

The highest-scoring automatically optimized prompt in Battle and Gollapudi's
study asks Llama2-70B to solve grade-school math in the voice of a Star Trek
officer — system message "Command, we need you to plot a course through this
turbulence and locate the source of the anomaly", answer prefix "Captain's Log,
Stardate [insert date here]". Their own summary is that the optimized prompts
"diverge significantly from any prompts we might have devised independently" and
that "if presented with these optimized prompts before observing their
performance scores, one might have anticipated their inadequacy". The shared
language did not help the practitioners predict the winner; it made them
confident in the wrong direction.

Sclar et al.'s [FormatSpread](https://arxiv.org/abs/2310.11324) found up to **76
accuracy points** of spread on LLaMA-2-13B across prompt formats that are
meaning-preserving — separator characters, casing, spacing. A practitioner's
intuition has no purchase there at all, because these are not choices a human
reader would register as choices. The same paper reports that format performance
correlates only weakly between models, so there is nothing stable to build an
intuition about.

And measured directly:
[Prompting in the Dark](https://arxiv.org/abs/2502.11267) put 20 participants
through iterative prompt refinement on a labeling task without gold labels.
Average accuracy moved from .542 to .553 across four revisions. Nine
participants improved, ten got worse, one stayed put. Unaided human iteration on
prompt wording is roughly a coin flip.

Now the other direction. MIPRO's own limitations section says its optimizers
"have limited ability to infer the rules governing complex tasks without a
handwritten seed prompt", and the paper's third lesson is that instruction
optimization matters most for tasks with conditional rules the model cannot
guess — where "it's important that we optimize over a seed prompt, as our
optimizers are not yet able to infer all task rules". The Heart Disease result is
the same finding from the other side: the optimizer had to claw back 47 points
that a human could have supplied in one sentence of domain knowledge, and it only
got there because the metric told it what it was missing.

[Storf et al.](https://arxiv.org/abs/2603.00829), building prompted classifiers
to detect scheming in LLM agents, found performance saturating after a simple
sweep over 15 candidate prompts: heavier optimization "yields no significant
improvement or leads to degraded performance", with one exception — human-guided
prompt refinement on one of their two datasets, the only intervention that
produced a statistically significant gain over the sweep.

That is a coherent picture, and it is not the one in the dump. The practitioner's
advantage is not in the register. It is upstream of the prompt string entirely:
knowing what the task actually is, what counts as a correct answer, which
strategy class to reach for, and which failures matter more than others. An
optimizer hill-climbs the metric it is handed and cannot want anything the metric
does not encode.
[Hamel Husain](https://hamel.dev/blog/posts/evals-faq/), who has run evals work
across dozens of companies, puts the practitioner's version of this plainly:
"you should be skeptical of tools that promise to optimize prompts for you,
especially in early stages of development", because writing prompts by hand
forces you to clarify assumptions — and "once you have a high-quality set of
evals, prompt optimization can be effective for that last mile of performance".

So the dump is right that removing the human costs you something, and wrong
about what. What you lose is not a shared vocabulary with the model. It is the
person who decides what the model is being scored on.

## What it doesn't show

Enough that the finding should be read as a shape, not a measurement.

**These are other people's baselines.** Every optimizer paper picks the human
prompt it competes against, and has every incentive to pick a weak one. That is
not an accusation of bad faith — a default signature is the honest baseline for
the question "does compiling a DSPy program help?" — but it means the `default`
tier is selected in a way the `tuned` tier is not, and the +16.7 figure measures
the convention as much as the optimizers.

**The expert tier is three rows.** One of them
([The Prompt Report](https://arxiv.org/abs/2406.06608)) has its two numbers on
different splits and is excluded from the margin figure for that reason. Nothing
here establishes what happens against a strong practitioner; it establishes that
almost nobody has run that comparison and published it.

**The binning is mine.** `default` / `tuned` / `expert` is a reading of how each
paper described its baseline, not a measured quantity. Someone else reading the
same seven papers could move rows.

**Scales are pooled.** Exact match, F1, retrieval@21 and accuracy are all called
"points". APE's normalized BBH scores are excluded from the margin arithmetic
for exactly this reason, but the rest are pooled across metrics that are not
interchangeable.

**The measurement floor is soft.** Battle and Gollapudi could not reproduce
published GSM8K scores for two of their three models — Meta reported 0.29 for
Llama2-13B; they measured 0.07 without chain-of-thought and 0.43 with it. Several
of the margins in the tuned tier are smaller than that kind of gap.

**Nothing here is recent frontier-scale.** The strongest human baselines in the
corpus are from 2022 and 2024, on models nobody deploys now. Newer optimizers —
[GEPA](https://arxiv.org/abs/2507.19457), which reports beating MIPROv2 by over
10% and GRPO by 10% with up to 35x fewer rollouts — appear nowhere in the pairs,
because their published comparisons are against other optimizers rather than
against a human.

And the specific claim in the dump — that overlapping training data gives the
practitioner a usable prior on wording — is not supported by anything I found.
The closest evidence points the other way. The salvageable version of it is
narrower and lives one level up.

## Where this goes

Three things, in the order they are worth doing.

**The experiment that would settle it.** Fix a task with a real labeled test
set, fix one current model, and give N practitioners the same one-hour budget
and the same labeled dev set. Run GEPA and MIPROv2 on the same dev set under a
matched token budget. Score everything on the held-out split, several seeds
each, and report the spread rather than the best run. Nobody in this corpus has
done that, and it is not expensive — the binding constraint is recruiting the
practitioners, not the API bill.

**The specification experiment, which is cheaper and more interesting.** Hold
the optimizer fixed and vary only the seed prompt: naive signature, competent
description, expert description with the task's real edge cases in it. If the
optimizer converges to the same place from all three, the human contributes
nothing that survives compilation. If it does not, the gap is a direct measure of
what specification is worth. MIPRO's HotPotQA Conditional experiment is half of
this design already — they ran it with and without a handwritten seed and the
handwritten seed mattered — so the other half is a weekend.

**The error-profile point deserves its own note.** The entrapment case study
produced two systems with near-identical F1 and inverted precision/recall, and
the optimizer had no way to know which one was wanted. That generalizes past
prompt optimization to every place a scalar metric stands in for a judgement,
and it is probably the more useful thing sitting in this material.

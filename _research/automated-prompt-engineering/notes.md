# Working notes — automated prompt engineering

Where every row of `head-to-head.csv` came from, and why it was binned the way
it was. Written so the `baseline_strength` column — the one judgement call in
the dataset — can be argued with rather than taken on faith.

## What could not be done

No live experiment. Running DSPy against a human prompt for real needs an LLM
API key, and this session had none it could legitimately spend. So the empirical
half is a meta-analysis of comparisons other people already ran and published,
not a new benchmark. That is a genuine weakness and the note says so: every
paper here chose its own baseline, and I am re-reading those choices rather than
controlling them.

The rerun that would settle it is written up at the end of the note.

## Sources

| key | paper | what was pulled |
|---|---|---|
| `battle2024` | [The Unreasonable Effectiveness of Eccentric Automatic Prompts](https://arxiv.org/abs/2402.10949), Battle & Gollapudi, VMware NLP Lab | Table 5, all 12 rows. "Avg EM" for the best "positive thinking" prompt vs. the automatically optimized prompt, all with CoT. |
| `ape2022_bbh` | [Large Language Models Are Human-Level Prompt Engineers](https://arxiv.org/abs/2211.01910), Zhou et al. | Appendix Table 6, all 21 BBH tasks, normalized performance, human vs. APE. |
| `ape2022_cot` | same paper, §4.3 | Zero-shot CoT answer-prefix search on text-davinci-002: MultiArith 78.7 → 82.0, GSM8K 40.7 → 43.0. The no-prompt floors (17.7 and 10.4) come from the same paragraph and feed the third figure. |
| `mipro2024` | [Optimizing Instructions and Demonstrations for Multi-Stage LM Programs](https://arxiv.org/abs/2406.11695), Opsahl-Ong et al. | Table 2, test column only. Baseline row (`N/A` optimizer) vs. the full MIPRO row, Llama-3-8B. |
| `kg2025` | [Automatic Prompt Optimization for Knowledge Graph Construction](https://arxiv.org/abs/2506.19773), Mihindukulasooriya et al., IBM Research | Table 2, triple-F1 columns, six prompting strategies, baseline row vs. optimized row. Llama-3.3-70B on SynthIE. |
| `valdi2026` | [Pseudo-Deliberation in Language Models](https://arxiv.org/abs/2605.09893) | Appendix E.2. Macro-F1 for the hand-written prompt vs. the MIPROv2-optimized one: 0.4273 vs. 0.3848 (task 2), 0.3759 vs. 0.3762 (task 3). |
| `promptreport2024` | [The Prompt Report](https://arxiv.org/abs/2406.06608), Schulhoff et al., §6.2 | The entrapment-detection case study: 47 recorded steps, ~20 hours, human F1 0.53; DSPy 0.548 on the test set. |

## The binning

`default` — the human prompt was the first reasonable thing somebody wrote down
and nobody iterated on it:

- `mipro2024`. The baseline is the unoptimized DSPy program, i.e. the signature
  docstrings the authors wrote to define the task. The Iris one is literally
  "Given the petal and sepal dimensions in cm, predict the iris species."
  (Appendix E.5). The Heart Disease signature carries no classification criteria
  at all, which the authors themselves name as the reason optimization gained so
  much there.
- `kg2025`. Baseline prompts are the one-sentence task descriptions in Table 1.
- `ape2022_bbh`. The paper's own phrase is "the default human prompt".

`tuned` — the human prompt is the winner of a deliberate human search:

- `battle2024`. 60 hand-written system-message combinations were evaluated and
  the best one kept. This is the strongest human baseline in the corpus by
  construction, and the only one where the human search is quantified.
- `ape2022_cot`. "Let's think step by step" was itself selected by Kojima et al.
  as the best of at least nine human-designed prompts — APE says so explicitly
  when introducing the comparison.

`expert` — a practitioner iterated for hours against measured feedback:

- `promptreport2024`. ~20 hours, 47 steps, by the author of a widely used
  prompting guide.
- `valdi2026`. "Expert-designed prompts", the authors' term; the amount of work
  behind them is not quantified, so this bin is the weakest-supported of the
  three. With n=3 the expert row of every figure is illustrative, not evidence.

## Two rows that need flagging

`promptreport2024` is the only row where the two numbers do not come from the
same split: the human's 0.53 F1 is quoted for the development set and DSPy's
0.548 for the test set. The paper states outright that the DSPy prompt "performs
much better than the human prompt engineer's prompts on the test set", so the
direction is the authors', not mine — but the margin is not comparable, which is
why the row is `delta_comparable = False` and appears only in the win/tie/loss
figure.

`ape2022_bbh` rows are normalized scores, not accuracy points, and some are
negative. Fine for scoring a win or a loss; meaningless to average against
accuracy deltas. Also `delta_comparable = False`.

## Supporting material that is cited but not in the CSV

- [FormatSpread](https://arxiv.org/abs/2310.11324), Sclar et al. — up to 76
  accuracy points of spread across meaning-preserving format changes on
  LLaMA-2-13B; format performance correlates only weakly between models.
- [Prompting in the Dark](https://arxiv.org/abs/2502.11267), CHI-style user
  study — 20 participants iterating prompts without gold labels moved average
  accuracy from .542 to .553 over four revisions; 9 improved, 10 declined, 1
  unchanged.
- [Constitutional Black-Box Monitoring](https://arxiv.org/abs/2603.00829),
  Storf et al. — heavier optimization past a simple prompt sweep yields no
  significant gain or degrades, with human-guided refinement on one of the two
  datasets the single exception.
- [Hamel Husain's evals FAQ](https://hamel.dev/blog/posts/evals-faq/) — the
  named practitioner counter-position.

## Rerun

```sh
pip install -r requirements.txt && python analysis.py
```

Writes the three PNGs into `assets/images/` and prints every number the note
quotes.

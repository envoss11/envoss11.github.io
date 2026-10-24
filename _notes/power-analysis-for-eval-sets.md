---
title: "Power analysis for eval sets"
topic: evals-statistics
status: complete
writing: evaluation
published: true
sample: true          # SAMPLE CONTENT: remove before merging
excerpt: ""
---

How many examples does an eval set need to tell two systems apart?

## 2026-07-20

Two independent proportions, accuracy *p₁* vs *p₂*, per arm:

    n ≈ (z₁₋α/₂ + z₁₋β)² · [p₁(1−p₁) + p₂(1−p₂)] / (p₁ − p₂)²

For 0.80 vs 0.85 at α = 0.05 and 80% power, that is about 900 items per
system. Most eval sets I see are a few hundred.

## 2026-08-03

Pairing helps: both systems usually run on the same items, so only the items
where they disagree carry information (McNemar). The same idea as CUPED in
[[Trustworthy Online Controlled Experiments|Kohavi et al.]].

```python
# Wiki-link syntax inside code is left alone: [[not-a-link]]
from statsmodels.stats.power import NormalIndPower
```

## 2026-08-24

Next: does any of this hold for LLM-as-judge scores, where the judge has its
own noise? See [[llm-judge-agreement]].

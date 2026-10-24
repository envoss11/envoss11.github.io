---
title: "Trustworthy Online Controlled Experiments"
author: "Ron Kohavi, Diane Tang, and Ya Xu"
topic: evals-statistics
status: complete
started: 2026-06-01
finished: 2026-08-10
published: true
sample: true          # SAMPLE CONTENT: remove before merging
excerpt: ""
---

The A/B testing book. Most of it transfers directly to comparing two versions
of an AI system on an eval set: [[power-analysis-for-eval-sets]].

## 2026-06-01 · Part I

- Define one Overall Evaluation Criterion (OEC) up front. Without it, every
  experiment turns into an argument about which metric counts.
- Twyman's law: a result that looks surprising is usually a bug.

## 2026-06-22 · Threats to validity

- Sample ratio mismatch (SRM): if the arms are not the size you designed for,
  stop and find out why before reading any metric.

## 2026-07-13 · Variance reduction

- CUPED: use a pre-period covariate to cut variance. The eval analogue is
  pairing, scoring both systems on the same items.

## 2026-08-10 · Finished

- Main takeaway: build trust in the measurement process before trusting any
  single number it produces.

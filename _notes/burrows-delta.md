---
title: "Burrows' Delta"
topic: stylometry
status: idea
updated: 2026-09-14
published: true
sample: true          # SAMPLE CONTENT: remove before merging
excerpt: ""
---

The classic authorship-attribution distance. Take the most frequent words,
z-score each word's frequency across the corpus, and average the absolute
differences between two texts.

Idea: use it to fingerprint LLMs. How big a sample would it take to tell two
models apart? That is [[power-analysis-for-eval-sets]] again.

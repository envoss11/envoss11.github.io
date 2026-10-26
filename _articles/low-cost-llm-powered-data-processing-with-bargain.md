---
title: "Low-Cost LLM-Powered Data Processing with BARGAIN"
source: "https://data-people-group.github.io/blogs/2025/09/16/bargain/"
site: "data-people-group.github.io"
date_read: 2025-11-11
raindrop_id: 1429996882
---

> To process a data (i.e., text) record with an LLM given a prompt, BARGAIN first runs the cheap model on the data record. Based on the model’s output log-probabilities it decides whether to trust the cheap model or not. If it decides the cheap model’s output is inaccurate, it then runs the more expensive model.

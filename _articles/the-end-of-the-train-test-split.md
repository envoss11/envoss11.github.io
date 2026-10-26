---
title: "The End of the Train-Test Split"
source: "https://folio.benguzovsky.com/train-test"
site: "folio.benguzovsky.com"
date_read: 2025-12-03
raindrop_id: 1469450316
---

> Any task complicated enough to require an LLM will need policy expert labels

> Don’t train the LLM on any of the dataset. Address the inevitable biases with evaluation on blind, unlabeled data

> In production, we see anywhere from 15-30% error rates in data considered "golden sets" by operations teams.

> You still need to run blind tests: QA the models on new data. Organizations end up running their models in "shadow mode" on production data, creating test examples without taking real-world actions. Here, you'll likely need an in-house agent to review the examples, then forward edge cases to a policy expert.

> The "training" step for language models has to be policy alignment, not heating up GPUs. Since the data will always be flawed and the test set won't be blind, the machine learning engineer's priority should be spent working with policy teams to improve the data. That means surfacing edge cases and policy gray areas, clarifying policy definitions, and leveraging LLM outputs to find more discrepancies until data is high-quality and policy is clear.

---
title: "Frequently Asked Questions (And Answers) About AI Evals – Hamel’s Blog"
source: "https://hamel.dev/blog/posts/evals-faq/"
site: "hamel.dev"
date_read: 2025-07-11
raindrop_id: 1242566350
---

> Q: How many people should annotate my LLM outputs?  
> For most small to medium-sized companies, appointing a single domain expert as a “benevolent dictator” is the most effective approach

> Focus automated evaluators on failures that persist after fixing your prompts

> Build a custom annotation tool. This is the single most impactful investment you can make for your AI evaluation workflow

> RAG systems have two distinct components that require different evaluation approaches: retrieval and generation.

> Error analysis is the most important activity in evals

> Q: What’s a minimum viable evaluation setup?  
> Start with error analysis, not infrastructure. Spend 30 minutes manually reviewing 20-50 LLM outputs whenever you make significant changes. Use one domain expert who understands your users as your quality decision maker (a “benevolent dictator”).

> These two systems are complementary: when production monitoring reveals new failure patterns through error analysis and evals, add representative examples to your CI dataset. This mitigates regressions on new issues.

> User feedback signals: Prioritize traces with negative feedback, support tickets, or escalations.

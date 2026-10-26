---
title: "G-EVAL: NLG Evaluation using GPT-4 with Better Human Alignment"
source: "https://arxiv.org/pdf/2303.16634"
site: "arxiv.org"
date_read: 2025-04-24
raindrop_id: 1023144993
---

LLM-based eval method - authors note LLM-based methods greatly outperform other methods.

3 main components:
1. Prompt which defines the evaluation task and criteria
2. LLM-generated CoT (intermediate instructions) with detailed evaluation steps
3. " a scoring function that calls LLM and calculates
the score based on the probabilities of the return
tokens."

Component 1 is fairly self-explanatory.

Component 2 - e.g., add a pre-fill line of "Evaluation Steps:" -is this still necessary with newer models? Unclear to me. Paper is from 2023, pre-dates many recent developments (reasoning models, for example).

Component 3: We're still just asking for a pre-defined score (e.g., 1-3), BUT summing the weighted probability of each score rather than merely taking a single value given by the LLM. Produces more fine-grained, continuous, and better scores.

Note: to make this third component work in the manner described, we need a model/platform which supports output of token probabilities. HOWEVER, this can be worked around/replicated - "For GPT-4, as it
does not support the output of token probabilities,
we set ‘n = 20, temperature = 1, top p = 1’ to
sample 20 times to estimate the token probabilities."

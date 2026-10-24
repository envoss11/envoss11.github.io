---
title: "Bedrock Guardrails"
topic: aws-genai-cert
status: wip
published: true
sample: true          # SAMPLE CONTENT: remove before merging
excerpt: ""
---

Exam domain: safety and governance.

## 2026-10-08

- Policies: content filters, denied topics, word filters, sensitive information
  (PII) filters, and contextual grounding checks.
- Applied to the input, the output, or both.

## 2026-10-15

- `ApplyGuardrail` runs a guardrail without invoking a model, so it can sit in
  front of a model hosted outside Bedrock.
- Grounding checks score how well the answer is supported by the source and
  how relevant it is to the query. Worth comparing with
  [[power-analysis-for-eval-sets]] style measurement.

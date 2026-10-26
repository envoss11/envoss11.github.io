---
title: "Agents"
source: "https://huyenchip.com/2025/01/07/agents.html"
site: "huyenchip.com"
date_read: 2025-01-24
raindrop_id: 953705153
---

"An agent is anything that can perceive its environment and act upon that environment...This means that an agent is characterized by the environment it operates in and the set of actions it can perform."

**Tools** and **planning** are the two key elements (ReAct)

"To avoid fruitless execution, planning should be decoupled from execution. You ask the agent to first generate a plan, and only after this plan is validated is it executed" - can validate with simple rules and heuristics (e.g., number of steps), or an AI judge.

System components: Planner, validator, executor

A translator model (or 'program generator') can be added to translate natural language steps into executable commands. This can be done by a weaker model with low hallucination risk.

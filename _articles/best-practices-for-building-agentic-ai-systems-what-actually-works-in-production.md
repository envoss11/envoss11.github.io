---
title: "Best Practices for Building Agentic AI Systems: What Actually Works in Production - UserJot"
source: "https://userjot.com/blog/best-practices-building-agentic-ai-systems"
site: "userjot.com"
date_read: 2025-08-22
raindrop_id: 1308982821
---

> Should subagents really have zero memory?  
> Yes. When you add memory, you add state, and when you add state, you add bugs, so keep them stateless.

> How do you handle rate limits with parallel agents?  
> Implement a token bucket rate limiter to launch agents up to your limit, queue the rest, and process queued tasks as tokens become available.

> How do you test agent systems?  
> Test subagents with fixed inputs and expected outputs, orchestration with mocked subagent responses, and the full system with real but limited data.

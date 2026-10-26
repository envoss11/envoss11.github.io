---
title: "How LLM Inference Works"
source: "https://arpitbhayani.me/blogs/how-llm-inference-works"
site: "arpitbhayani.me"
date_read: 2025-11-24
raindrop_id: 1448762589
---

> LLMs are just neural networks built on the transformer architecture

> The most common tokenization approach in modern LLMs is Byte Pair Encoding (BPE). BPE starts with a vocabulary of individual characters and iteratively merges the most frequent pairs of adjacent tokens to create new tokens.

> The transformer processes embedding vectors through its layers. Each transformer layer applies two main operations: multi-head self-attention and feed-forward networks

> Inter-Token Latency (ITL) measures the time between consecutive token generations in the decode phase. This metric determines how fast text streams to the user after generation begins

> The prefill phase produces the first output token and builds the KV cache, which we will discuss shortly. Time to First Token (TTFT) measures how long this phase takes, directly impacting user experience since this is the wait time before seeing any output.

> The KV cache represents one of the most important optimizations in transformer inference. Without it, generating 100 tokens would require recomputing attention for all previous tokens 100 times, wasting enormous computational resources.

> There are two stages in practice: the model first handles your full prompt in parallel, then switches to generating tokens one by one, which shifts the bottleneck from math to memory access.

> Key optimizations include KV caching to avoid redundant computation, batching to improve GPU utilization, and quantization to reduce memory pressure.

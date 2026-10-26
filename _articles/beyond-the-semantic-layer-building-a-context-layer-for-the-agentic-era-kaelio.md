---
title: "Beyond the Semantic Layer: Building a Context Layer for the Agentic Era | Kaelio"
source: "https://www.kaelio.com/blog/building-a-context-layer-for-the-agentic-era"
site: "kaelio.com"
date_read: 2026-06-09
raindrop_id: 1751092988
---

idk about this in particular, but the general concept of an OSS context engine is appealing

> The idea is to pull two kinds of knowledge into one reviewable place: the hard semantics (your warehouse schema, joins, and metric definitions as YAML and SQL) and the soft semantics (the business context living in docs, wikis, and Notion that agents usually never see)

Useful vocabulary: hard vs. soft semantics

> The context layer primarily supports the accuracy of SQL queries, continuous updates to the business context, and governance. Additionally, with a newer context layer, we can include more relevant business insights that are stored internally, usually in unstructured form, in tools like Notion as business documentation.

Still seems like a narrow BI enrichment kind of view - the "why" should be broader than this

> If we look at a high-level overview, compared to a common semantic layer or logical layers in BI tools, you can build a knowledge layer around your business, with not only structured data but also unstructured knowledge from your company-wide internal documentation on Notion, or your data in Markdown or a git repository. ktx helps navigate and maintain this business knowledge.

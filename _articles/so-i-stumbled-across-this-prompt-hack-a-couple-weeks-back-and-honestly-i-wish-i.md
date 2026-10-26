---
title: "So I stumbled across this prompt hack a couple weeks back and honestly? I wish I could unlearn it."
source: "https://www.reddit.com/r/ClaudeAI/s/SkiuVikRG6"
site: "reddit.com"
date_read: 2026-01-06
raindrop_id: 1528375903
---

Try the "/code-review:code-review (plugin:code-review@claude-plugins-official)" plugin from anthropic. It's brilliant because it runs 5 agents in parallel to do a code review and then runs haiku agents to rate it and only flags the issues that are scored 80 or above.

The one caveat is, it only does that on PRs. I just asked claude to look at that plugin and create a local version that does the same thing on git diff "/local-review" and it works beautifully. One shot a review and move on with your life.

Edit: Since many of you are asking for this, I published the command as a plugin on GitHub (https://github.com/Agent-3-7/agent37-skills-collection). For now it's part of our hosted AI skills collection at https://agent37.com but will move it out to it's own thing if needed.

/plugin marketplace add Agent-3-7/agent37-skills-collection
/plugin install local-review@agent37-skills
-- Restart CC
/local-review:local-review

---
title: "Placeholder — A Note Being Written in Public"
date: 2026-08-10
excerpt: "Placeholder copy. This shows the shape of a work-in-progress note: live at its own URL, listed in the drawer on /posts/, and deliberately out of the feed and the sitemap."
tags_list:
  - "Tag One"
---

**Placeholder note.** This one exists to hold the works-in-progress tier open —
replace it or delete it once there is a real note in the drawer.

A note in `_wip/` is a published page that is not asking for readers. It has a
URL, it renders with the same layout every other entry uses, and anyone with the
link can read it. What it does not have is a place in `/feed.xml`, a row in
`/sitemap.xml`, or an invitation to a crawler — the `wip` defaults scope in
`_config.yml` handles all three, so nothing here needs to set them.

## Why the tier exists

The gap it fills is between `_drafts/`, which nobody can see, and `_posts/`,
which goes out on the feed the moment it lands. Some things want to be readable
before they are finished: a research thread, a half-argued position, a data pull
that hasn't decided what it means yet. Publishing those to the feed is a promise
the writing can't keep, and leaving them in `_drafts/` means they're invisible
from anywhere but a laptop.

## What is different about the page

Two things, both in `_layouts/post.html`. A note carries the standing banner
above the prose saying what it is, and it does not get the newer/older pair at
the foot — chaining unrelated half-formed notes to each other is noise rather
than navigation.

Front matter is a post's, with one difference: the date lives in the front
matter rather than the filename, because these files aren't named
`YYYY-MM-DD-`. Give every note one. Without it the drawer falls back to sorting
by filename, which is not the order anybody wants.

## Getting out of the drawer

Finishing a note is a rename: move it to `_posts/YYYY-MM-DD-<slug>.md` and drop
the `date` line, since the filename carries it from then on. The URL changes
from `/posts/wip/<slug>/` to `/posts/<slug>/`, and it joins the log and the feed
like anything else.

---
title: "“Consumer Rights” Led for Exactly One Decade"
date: 2026-08-18
excerpt: "In American books, consumer-identity language never achieved primacy: “workers” still outnumbers “consumers” four to one, and “consumer rights” out-ranked “workers' rights” only from 1969 to 1978. The mid-century pivot the dump suspects is real — but what is rising now is “workers' rights”, “labor rights”, and the critique of consumption itself."
tags_list:
  - "Language"
  - "Ngrams"
  - "Cultural History"
image: /assets/images/consumer-vs-producer-rights.png
image_fit: contain
---

## The dump

> Concept - relative frequency of “consumer rights” and the like, vs. terms that
> center other identities (worker rights, etc.), analysis of historical context,
> shift toward consumer identity primacy (negative) vs. identity centered around
> production, kind of a Wendell Berry vibe to it - is there anything to this?

## The question

The dump is three claims stacked up, and they separate cleanly. First, a claim
about levels: language that addresses people as consumers now outweighs language
that addresses them as workers or producers. Second, a claim about motion: there
was a historical shift in that direction, and it should be visible. Third, a
claim about value: the shift is a loss — the Wendell Berry half. The first two
are checkable against the print record; the third is an argument, taken up at
the end.

The data is the [Google Books Ngram corpus](https://books.google.com/ngrams/),
American English, 1900–2019, pulled through the JSON API by
[`analysis.py`](https://github.com/envoss11/envoss11.github.io/blob/master/_research/consumer-vs-producer/analysis.py),
with the raw responses committed as
[`ngrams-en-US-2019.json`](https://github.com/envoss11/envoss11.github.io/blob/master/_research/consumer-vs-producer/ngrams-en-US-2019.json)
so every number below can be re-derived offline. All series are 5-year centered
averages; "peak" always means the smoothed peak within 1900–2019.

## What the data says

Start with the phrase the dump names. "Consumer rights" barely existed before
1960, grew 52-fold between 1950 and its 1977–78 peak, and held a narrow lead
over "workers' rights" for precisely the years 1969–1978 (over "labor rights",
1965–1983). That window is the Nader decade almost to the year: [Kennedy's
special message to Congress](https://www.presidency.ucsb.edu/documents/special-message-the-congress-protecting-the-consumer-interest)
declaring the four consumer rights came in March 1962 — "Consumers, by
definition, include us all. They are the largest economic group in the economy" —
Ralph Nader's [*Unsafe at Any Speed*](https://www.britannica.com/topic/Unsafe-at-Any-Speed)
followed in 1965, and the [Consumer Product Safety Commission arrived in 1972](https://www.cpsc.gov/Newsroom/News-Releases/2022/CPSC-Celebrates-50-Years-of-Making-Consumer-Safety-our-Mission). Then the lead flipped back and never
returned. By 2019, "workers' rights" ran 3.8 times the frequency of "consumer
rights", and both "workers' rights" and "labor rights" stood at their all-time
highs — not their New Deal highs, their 2018–2019 highs.

![Line chart of the frequency of the phrases consumer rights, workers' rights, labor rights and employee rights in American books from 1930 to 2019. Consumer rights rises steeply after Kennedy's 1962 consumer message, holds a shaded narrow lead over workers' rights from 1969 to 1978, then flattens and declines; workers' rights and labor rights climb after 1980 to all-time highs in 2018 and 2019; employee rights towers over both during the 1970s and then falls away.](/assets/images/consumer-vs-producer-rights.png)

One more detail from that chart worth saying out loud: "employee rights" peaked
in 1979 at 2.7 times the level "consumer rights" ever reached. Even at the high
tide of the consumer movement, books had more to say about rights at work.

The identity nouns tell the same story at larger scale. "Workers" peaked in
1943, running seven times the frequency of "consumers" at the wartime high, and
still ran 4.2 times higher in 2019. The consumers-to-workers ratio traces a
shallow U: 0.39 in 1900, down to 0.16 in 1950, back up to 0.26 by 1977, and
0.24 in 2019 — meaning the much-discussed postwar "rise of the consumer" was,
in word frequency, a partial recovery to *below* where the ratio stood in 1900.
The one clean displacement in the whole dataset is "producers": roughly at
parity with "consumers" in 1900 (ratio 0.97), it traded places with them for
decades, fell behind for good in 1991, and ended 2019 at a ratio of 1.72 in the
consumers' favor.

![Line chart of the words consumers, workers, producers and citizens in American books from 1900 to 2019. Workers dwarfs the rest, peaking around 1943 near 195 occurrences per million words and declining to about 84; citizens drifts from about 70 down to 50; producers and consumers trade places for decades until consumers pulls ahead for good in 1991 and ends near 20 per million.](/assets/images/consumer-vs-producer-nouns.png)

Where the shift-toward-consumption claim genuinely holds is in *timing*. Sort
two dozen terms by the year each peaked and the vocabulary turns into a
timeline of eras: the production-side terms — "laborers" (1911), "workers"
(1943), "assembly line" (1944), "labor unions" (1947), "craftsmen" (1955),
"producers" and "labor movement" (1957) — peak before 1958 with two stragglers
("working class" in 1970, "shop floor" in 1988), and the consumer vocabulary
peaks in a cluster from "consumer goods" (1962) through "the consumer" and
"consumer protection" (1975), "consumers" (1977), "consumer rights" (1978), and
"consumer confidence" (1993). The print record really does
pivot from production to consumption across the middle of the century, exactly
while the thing itself pivoted: union membership peaked at [34.8% of wage and
salary workers in 1954](https://www.congress.gov/crs-product/R47596) and stood
at [9.9% in 2024](https://www.bls.gov/news.release/archives/union2_01282025.htm).
This is the era [Lizabeth Cohen's *A Consumers' Republic*](https://www.penguinrandomhouse.com/books/29448/a-consumers-republic-by-lizabeth-cohen/)
documents from the inside: a postwar settlement that recast the purchaser as
the citizen, in which buying well *was* participating in the nation.

![Dot plot of the year each of 24 terms peaked in American books between 1900 and 2019, sorted by peak year, colored by whether the term belongs to the labor and production vocabulary or the consumer vocabulary. Labor terms cluster between 1911 and 1957, consumer terms between 1962 and 1993, and the most recent peaks belong to consumer society and consumer culture in 2009, workers' rights in 2018, and labor rights and consumerism in 2019.](/assets/images/consumer-vs-producer-peaks.png)

Two dots on that chart break the pattern, and both are instructive. "Consumer
movement" peaked in 1939, not the Nader era — the 1930s consumer movement was
that large, and [Consumers Union itself was born in 1936 out of a strike](https://www.encyclopedia.com/books/politics-and-business-magazines/consumers-union)
at Consumers' Research, when staff who sided with the strikers broke away to
found it. Consumer identity and worker identity were entangled at the origin.
And the terms peaking *right now* are "workers' rights", "labor rights", and
"consumerism" — which brings us to the last chart.

"Consumerism" ran 25 times the frequency of "consumer rights" in 2019, about
1,700 times its own 1950 level, and still climbing. The word
[has meant two things](https://www.etymonline.com/word/consumerism): it was
coined in 1922 for the protection of consumer interests, and in the 1970s
"consumerism" mostly *meant* the Nader movement — that is the first hump in the
chart. Its dominant sense since is the name for a way of life organized around
buying, usually said with a curled lip. The analytic-critical vocabulary rose
with it: "consumer culture" and "consumer society" both peaked in 2009.

![Line chart from 1950 to 2019 showing consumerism rising in two waves, a hump peaking around 1974 and a long climb after 1990 reaching about 1,800 occurrences per billion ngrams, while consumer rights stays flat below 130 and consumer culture and consumer society rise after 1990 into the 200 to 600 range.](/assets/images/consumer-vs-producer-critique.png)

So the answer to "is there anything to this?" splits. The mid-century pivot
from a production vocabulary to a consumption vocabulary is real and sharply
visible, and "producers" really was displaced. But the primacy claim fails in
print — worker language still outweighs consumer language, and consumer-identity
language has been *falling* for forty years. What the corpus says is rising now
is talk about workers' rights and critique of consumption. And the Berry vibe
has a specific irony of timing: [*The Unsettling of America*](https://www.asu.edu/courses/aph294/total-readings/berry--%20unsettlingofamerica.pdf)
was published in 1977 — the precise peak year of "consumers" in American books.
Berry described the tide at its highest, and the language has been moving his
way since. His actual claim stands apart from the word counts, because it was
never about words. The commercial revolution he traces from the fur trade
forward "has deprived the mass of consumers of any independent access to the
staples of life: clothing, shelter, food, even water." That is a claim about
capacity, not vocabulary, and no ngram measures it.

## What it doesn't show

**Books are not discourse.** The Google Books corpus is a library — one copy of
each book, no weighting by readership — and
[Pechenick et al. showed](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0137041)
that academic and scientific publishing makes up a growing share of it across
the 1900s. The post-2000 surge in "workers' rights", "labor rights", and
"consumer culture" could be labor history and cultural studies publishing more
books, not America talking differently. This is the single biggest threat to
the "rising now" half of the finding, and settling it needs a genre-balanced
corpus.

**Frequency is not allegiance.** People write about what is contested or
disappearing. "Workers' rights" peaking while union membership sits at a record
low reads at least as plausibly as commentary on erosion as it does as evidence
of a producer-identity revival — and symmetrically, nobody needs to keep saying
"consumer rights" once they are settled law. Mentions measure attention, not
identity.

**The words are impure.** "Workers" includes social workers, health care
workers, and knowledge workers; "consumers" turns up in economics prose about
consumers of electricity; "consumerism" changed meanings mid-series. And the
displacement the dump is reaching for may have happened in a register books
dilute: "customers" — which peaked in 1999 and has run above "consumers" in
every year of the series — is where patients, passengers, and students got
renamed, and this note did not chase it.

**The value claim is untestable here.** Whether the consumer framing is a loss
is not something a frequency chart can say, and the disagreement is real and
named. [Lawrence Glickman's *Buying Power*](https://press.uchicago.edu/ucp/books/book/chicago/B/bo6682337.html)
argues that Americans have used purchasing power as serious citizenship since
before the word boycott existed — abolitionist free-produce campaigns, Jim Crow
boycotts — that consumer identity has been a lever, not a couch. Kennedy's 1962
framing is the same position from the center: consumers deserve advocacy
precisely because they include everyone. Against that stands Berry's point that
a person who can produce nothing negotiates from weakness no matter how loudly
they are advocated for.

## Where this goes

- Re-run the core comparisons on a genre-balanced corpus (COHA) and on
  political speech (the Congressional Record, the American Presidency Project)
  to kill or confirm the academic-drift confound. Political language is where
  "consumer identity primacy" would actually bite.
- Chase "customers" through the public-services register — patient, passenger,
  student, citizen — where the real displacement likely lives.
- The Berry-shaped follow-up is not lexical: measure household productive
  capacity directly — time-use surveys, share of food produced at home, repair
  versus replacement — and see whether "the mass of consumers" lost independent
  access to staples on the schedule the vocabulary suggests. That would be a
  different note, and probably a better one.

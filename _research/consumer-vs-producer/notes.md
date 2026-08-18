# Working notes — consumer-vs-producer

## Method decisions

- **Corpus:** Google Books Ngram, `en-US-2019`, 1900–2019, `smoothing=0` from the
  API; a 5-year centered rolling mean is applied in `analysis.py` so the window
  is stated in code rather than hidden in an API parameter. The general English
  corpus (`en-2019`) was checked first and tells the same story with slightly
  different levels; the note claims are about American discourse, so American
  English is the primary corpus.
- **Raw data committed** as `ngrams-en-US-2019.json` (~40 KB) so every number is
  re-derivable offline. Delete the file to force a re-fetch.
- **Term basket is a judgement call.** The labor side deliberately mixes identity
  nouns (workers, producers, laborers, craftsmen), institutions (labor unions,
  trade unions, labor movement), places (shop floor, assembly line), and rights
  compounds. The consumer side mirrors it. Terms considered and dropped:
  "shopping mall" (peaked 2019 in books, which says more about nostalgia
  publishing than malls), "customers" (commercial register, ambiguous between
  identity and bookkeeping — noted in the note as unfinished business),
  "tenant rights" / "patient rights" (worth a follow-up, out of scope here).
- **API quirk:** the JSON endpoint normalizes "workers' rights" to
  "workers ' rights" in the returned `ngram` key; `fetch()` cleans it.
- **Mixed ngram lengths:** "consumerism" (1-gram) is plotted against bigrams in
  the critique figure. Each series is a share of its own same-length denominator,
  which is how the Ngram Viewer plots mixed lengths too. The 25x gap dwarfs the
  denominator difference; peaks-only comparisons are unaffected.

## Findings that surprised me

- "Consumer rights" led "workers' rights" for exactly 1969–1978 (smoothed) and
  "labor rights" for 1965–1983, then lost the lead and never got it back.
- "Workers' rights" and "labor rights" hit their all-time highs in 2018–2019.
- "Employee rights" peaked in 1979 at 2.7x the peak of "consumer rights" —
  even at high tide, employment-rights talk was bigger.
- "Consumer movement" peaked in 1939, not the Nader era.
- Consumers/workers ratio in 1900 (0.392) is *higher* than in 2019 (0.239).
- "Consumerism" shows two waves that match its two meanings (etymonline):
  the 1970s hump when it named the Nader movement, the post-1990 climb as
  the name for a way of life.

## Key sources

- JFK, [Special Message on Protecting the Consumer Interest, 1962-03-15](https://www.presidency.ucsb.edu/documents/special-message-the-congress-protecting-the-consumer-interest)
- Wendell Berry, *The Unsettling of America* ch. 1, [full text PDF hosted by ASU](https://www.asu.edu/courses/aph294/total-readings/berry--%20unsettlingofamerica.pdf)
- Lizabeth Cohen, [*A Consumers' Republic*](https://www.penguinrandomhouse.com/books/29448/a-consumers-republic-by-lizabeth-cohen/)
- Lawrence Glickman, [*Buying Power*](https://press.uchicago.edu/ucp/books/book/chicago/B/bo6682337.html)
- Pechenick et al. 2015, [Characterizing the Google Books Corpus](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0137041)
- CRS, [union membership data, 1954 peak 34.8%](https://www.congress.gov/crs-product/R47596)
- BLS, [Union Members — 2024, 9.9%](https://www.bls.gov/news.release/archives/union2_01282025.htm)
- Etymonline, [consumerism](https://www.etymonline.com/word/consumerism)
- Encyclopedia.com, [Consumers Union](https://www.encyclopedia.com/books/politics-and-business-magazines/consumers-union) — born of the 1935 Consumers' Research strike

## Open threads

- COHA or the Congressional Record to control for the academic drift of the
  Google Books corpus (Pechenick's objection).
- The "customers" series (peaked 2000, bigger than "consumers") — the
  public-services displacement (patients/passengers/students → customers)
  probably lives there, and in British English.
- The Berry-shaped follow-up that word counts cannot answer: household
  productive capacity over time (ATUS time-use data, share of food home-grown,
  repair vs. replace).

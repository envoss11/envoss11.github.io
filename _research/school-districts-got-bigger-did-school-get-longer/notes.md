# Working notes for _notebooks/school-districts-got-bigger-did-school-get-longer.py

Raw pulls and sources. Never built — Jekyll skips _-prefixed dirs.

## What is in here

- `tabn214.10.xlsx`, `tabn201.10.xlsx`, `tabn202.10.xls` — the NCES Digest
  workbooks exactly as published, cached by the notebook's pull cell. Delete one
  and the next `make run` re-fetches it.
- `nces-long-arc.csv` — the seven tidy series the notebook derives from them.

## Sources used

- [Digest table 214.10](https://nces.ed.gov/programs/digest/d23/tables/dt23_214.10.asp),
  *Number of public school districts and public and private elementary and
  secondary schools: Selected years, 1869-70 through 2022-23*. Digest 2023.
  Districts are **regular** districts only: the table's footnote 1 excludes
  regional education service agencies, supervisory union administrative centers,
  state- and federally operated agencies, and independent charter LEAs.
- [Digest table 201.10](https://nces.ed.gov/programs/digest/d22/tables/dt22_201.10.asp),
  *Historical summary of public elementary and secondary school statistics:
  Selected school years, 1869-70 through 2019-20*. Digest 2022 — this table was
  not reissued in Digest 2023. Source series are the Commissioner of Education's
  Annual Report (1870–1910), the Biennial Survey (1919-20 – 1949-50), and CCD
  after that, so pre-1920 figures are a different collection than modern ones.
- [Digest table 202.10](https://nces.ed.gov/programs/digest/d19/tables/dt19_202.10.asp),
  *Enrollment of 3-, 4-, and 5-year-old children in preprimary programs … and
  attendance status: Selected years, 1970 through 2018*. Digest 2019 is the last
  edition to carry it; the underlying CPS October supplement item was dropped, so
  **there is no post-2018 national full-day/part-day kindergarten series.**
- Tom Loveless, [*2014 Brown Center Report on American Education*](https://www.brookings.edu/articles/2014-brown-center-report-on-american-education/)
  ("Homework in America"). NAEP long-term-trend homework question, 1984–2012:
  load "remarkably stable"; only 5–13% of students report more than two hours a
  night, depending on age.
- Christopher R. Berry and Martin R. West, [*Growing Pains: The School
  Consolidation Movement and Student Outcomes*](https://academic.oup.com/jleo/article-abstract/26/1/1/913468),
  Journal of Law, Economics, and Organization 26(1), 2010. Larger **schools**
  lowered later earnings and attainment; larger **districts** were modestly
  positive. Their own framing of the era: average school size 87 → 440 and
  average district size 170 → 2,300 between 1930 and 1970.

## Looked for and could not find

- **Hours in the school day, as a national time series.** This is the number the
  dump is actually about and the Digest does not publish it. Candidates for the
  next pull: the CCD state-level required instructional hours/days fields, the
  Education Commission of the States' instructional-time database, and the
  American Time Use Survey for the household side.
- **Extracurricular participation over a long horizon.** Nothing federal and
  comparable across decades turned up. HSLS/NELS/NLS-72 could be chained, but
  the items are not the same across them.
- **Post-2018 full-day kindergarten.** See table 202.10 above.

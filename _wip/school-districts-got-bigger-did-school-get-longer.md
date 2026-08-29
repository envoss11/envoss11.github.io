---
title: "School districts got bigger. Did school get longer?"
date: 2026-08-29
excerpt: "117,108 public school districts in 1939-40, 13,318 today. The consolidation is real — but the school year stopped getting longer in 1950, and the extra hours arrived at kindergarten instead."
tags_list:
  - "education"
  - "homeschooling"
  - "public data"
---

<!-- Generated from _notebooks/school-districts-got-bigger-did-school-get-longer.py by `make sync SLUG=school-districts-got-bigger-did-school-get-longer`. Edits below this line are overwritten. -->

{% raw %}
## The dump

> I'm really curious what the data say about how school district size in the
> United States has evolved over time. As a homeschooling family, one of the
> motivations for us has been this sense that school districts, public schools,
> have increasingly become these large bureaucracies unto themselves rather than
> a family community-driven resource. It sort of seems more like an imposition
> than something bottom-up, right?
>
> I get the sense that if we take a long-arc view of public schooling in the
> United States, all the way back to the early public schools in New England,
> there's been a shift to this industrial model. That has taken away a lot of
> effective local autonomy and control. There's school district size, there are
> financial elements, and quite a few things to explore here. I'd like to
> validate the extent to which this is true, kind of similar but with a slightly
> different angle.
>
> I remember when I was a kindergartner, kindergarten was a half-day program,
> right? Now it's almost universally full day. By the same token, extracurricular
> programs, homework, etc., seem like they're occupying a much greater percentage
> of a student's day and therefore a family's life. In other words, at the same
> time that school has perhaps become larger, more unwieldy, and out of local
> control, it's also consuming and controlling a much greater portion of a
> person's or a family's time and life. I'd also like to validate that idea and
> see if there is a coherent narrative that the data support here.

## The question

Two separate claims are bundled together here, and they have to be tested
apart. **Bigger and further away**: did the unit that runs a school actually
grow, and did the money for it stop being local? **More of a family's life**:
did school grow to take more of a child's year?

Both are answerable from long-run federal series that reach back to 1869-70.

```python
# Three tables from the NCES Digest of Education Statistics, one per claim.
# The published workbooks are cached into _research/ so every number below
# can be re-derived from the same bytes a year from now.
SOURCES = {
    # districts, public schools, one-teacher schools: 1869-70 to 2022-23
    "214.10": "https://nces.ed.gov/programs/digest/d23/tables/xls/tabn214.10.xlsx",
    # historical summary — enrollment, school term, revenue by source
    "201.10": "https://nces.ed.gov/programs/digest/d22/tables/xls/tabn201.10.xlsx",
    # preprimary enrollment by attendance status: 1970 to 2018
    "202.10": "https://nces.ed.gov/programs/digest/d19/tables/xls/tabn202.10.xls",
}

def workbook(number):
    path = RESEARCH / Path(SOURCES[number]).name
    if not path.exists():
        urllib.request.urlretrieve(SOURCES[number], path)
    return pd.read_excel(path, header=None)

def year_of(label):
    """`1939-40` -> 1939, `1999-2000` -> 1999, `2018\\1\\` -> 2018."""
    found = re.match(r"(\d{4})", str(label))
    return int(found.group(1)) if found else None

def value(cell):
    try:
        return float(cell)  # NCES writes "---" where a year has no figure
    except (TypeError, ValueError):
        return None

def across(sheet, row, header_row):
    """One row of a sheet whose years run left to right in `header_row`."""
    pairs = {
        year_of(sheet.iat[header_row, c]): value(sheet.iat[row, c])
        for c in range(sheet.shape[1])
    }
    return pd.Series({y: v for y, v in pairs.items() if y and v is not None}).sort_index()

def down(sheet, column, first_row):
    """One column of a sheet whose years run top to bottom in column 0."""
    pairs = {
        year_of(sheet.iat[r, 0]): value(sheet.iat[r, column])
        for r in range(first_row, sheet.shape[0])
    }
    return pd.Series({y: v for y, v in pairs.items() if y and v is not None}).sort_index()

_t214, _t201, _t202 = workbook("214.10"), workbook("201.10"), workbook("202.10")

# Row positions are hardcoded against the cached workbooks. Asserting each
# one against its own label means a re-download that shifts a row fails
# here rather than quietly plotting the wrong series.
assert _t201.iat[8, 0].strip().startswith("Total enrollment")
assert _t201.iat[18, 0].strip().startswith("Average length of school term")
assert _t201.iat[19, 0].strip().startswith("Average number of days attended")
assert _t201.iat[36, 0].strip().startswith("Local sources")
assert _t202.iat[27, 0].strip().startswith("Full-day kindergarten as a percent")

series = {
    "districts": down(_t214, 1, 5),
    "one_teacher_schools": down(_t214, 6, 5),
    "enrollment_k": across(_t201, 8, 1),
    "term_days": across(_t201, 18, 1),
    "days_attended": across(_t201, 19, 1),
    "local_revenue_pct": across(_t201, 36, 1),
    "full_day_k_pct": across(_t202, 27, 2),
}
tidy = pd.concat(series, names=["series", "year"]).rename("value").reset_index()
tidy.to_csv(RESEARCH / "nces-long-arc.csv", index=False)
tidy
```

```python
# Printed, not interpolated: `mo.md(f"...")` stops being Markdown and lands
# on the page as a code block, so the prose below quotes these by hand.
_d, _e = series["districts"], series["enrollment_k"]
for _y in (1939, 2019):
    print(
        f"{_y}-{str(_y + 1)[2:]}: {_d[_y]:>8,.0f} districts,"
        f" {_e[_y] * 1000:>12,.0f} pupils,"
        f" {_e[_y] * 1000 / _d[_y]:>6,.0f} per district"
    )
print(
    f"one-teacher schools:     {series['one_teacher_schools'][1909]:,.0f} (1909-10)"
    f" -> {series['one_teacher_schools'][2022]:,.0f} (2022-23)"
)
print(
    f"local share of revenue:  {series['local_revenue_pct'][1919]:.1f}% (1919-20)"
    f" -> {series['local_revenue_pct'][1979]:.1f}% (1979-80)"
    f" -> {series['local_revenue_pct'][2019]:.1f}% (2019-20)"
)
print(
    f"days attended per pupil: {series['days_attended'][1869]:.0f} (1869-70)"
    f" -> {series['days_attended'][1959]:.0f} (1959-60)"
    f" -> {series['days_attended'][2017]:.0f} (2017-18)"
)
print(
    f"full-day kindergarten:   {series['full_day_k_pct'][1970]:.1f}% (1970)"
    f" -> {series['full_day_k_pct'][2018]:.1f}% (2018)"
)
```

```python
_fig, _grid = plt.subplots(2, 2, figsize=(11, 7.5))
(_size, _money), (_year, _kinder) = _grid

def _line(ax, key, label=None, **kw):
    s = series[key]
    ax.plot(s.index, s.to_numpy(), marker="o", markersize=3, linewidth=2, label=label, **kw)

_line(_size, "districts", "Regular school districts")
_line(_size, "one_teacher_schools", "One-teacher schools")
_size.set_yscale("log")
_size.set_title("The units got fewer, so each one got bigger")
_size.set_ylabel("Count, log scale")
_size.legend(loc="lower left", fontsize=9)

_line(_money, "local_revenue_pct")
_money.set_ylim(0, 100)
_money.set_title("Local money receded, then stopped in 1980")
_money.set_ylabel("% of school revenue from local sources")

_line(_year, "days_attended", "Days attended per pupil")
_line(_year, "term_days", "Length of school term")
_year.set_ylim(0, 200)
_year.set_title("The school year has been flat since 1950")
_year.set_ylabel("Days")
_year.legend(loc="lower right", fontsize=9)

_line(_kinder, "full_day_k_pct")
_kinder.set_ylim(0, 100)
_kinder.set_title("Kindergarten is where the hours arrived")
_kinder.set_ylabel("% of kindergartners in a full-day program")

_fig.tight_layout(pad=2.0)
savefig(_fig, "long-arc")
_fig
```

## What the data says

![Four panels of long-run US public schooling data. Regular school districts
fall from 117,108 in 1939-40 to 13,318 in 2022-23 and one-teacher schools from
212,448 to 169, both on a log scale. The local share of school revenue drops
from 83% in 1919-20 to about 43% by 1980 and stays flat through 2019-20. Days
attended per pupil rise from 78 in 1869-70 to about 160 by 1959-60 and barely
move afterwards, tracking a school term that flattens at about 179 days. The
share of kindergartners in full-day programs climbs from 13.5% in 1970 to
80.8% in 2018.](/assets/images/school-districts-got-bigger-did-school-get-longer-long-arc.png)

The bundle comes apart. Three of the four numbers do not tell the same story
as the fourth.

**The consolidation is real and it is enormous.** [Digest table
214.10](https://nces.ed.gov/programs/digest/d23/tables/dt23_214.10.asp) counts
117,108 regular public school districts in 1939-40 and 13,318 in 2022-23.
Enrollment doubled over the same span, so the average district went from about
217 pupils to about 3,805 — seventeen times larger. One-teacher schools went
from 212,448 in 1909-10 to 169.

**Fiscal localism collapsed, and then stopped collapsing.** Local sources paid
83.2% of public school revenue in 1919-20, 43.4% in 1979-80, and 44.9% in
2019-20 ([table
201.10](https://nces.ed.gov/programs/digest/d22/tables/dt22_201.10.asp)). The
centralization is a 1920–1980 event. It has not moved in forty years.

**The school year is not the mechanism.** Average days attended per pupil went
78 in 1869-70, 160 in 1959-60, and 167 in 2017-18 — the whole increase happened
before the consolidation wave finished, and the term itself has sat at about
179 days since 1950.

**The hours arrived at the front end instead.** Full-day kindergarten went from
13.5% of kindergartners in 1970 to 80.8% in 2018 ([table
202.10](https://nces.ed.gov/programs/digest/d19/tables/dt19_202.10.asp)). The
half-day kindergarten in the dump is not a misremembering; it was the norm, and
it is now the exception.

## What it doesn't show

- **Fewer districts is not the same as less local control.** It is a proxy, and
  the revenue series argues against reading it as the whole story: the money
  finished centralizing before most of today's homeschooling parents were born.
- **Nothing here measures the length of the school day.** Days attended is an
  attendance average, not hours in a building — and hours per day is the number
  the dump is actually about. The Digest does not publish it.
- **Table 214.10 counts *regular* districts**, excluding regional service
  agencies, supervisory unions, and charter LEAs. That undercounts exactly the
  New England arrangement the dump reaches back to, where a town can still run
  its own school inside a supervisory union.
- **NCES stopped publishing the full-day/part-day split after 2018.** Digest
  2019 is the last edition to carry table 202.10.
- **Homework and extracurriculars are not in evidence, and one source says
  they are not there.** Tom Loveless's [2014 Brown Center
  Report](https://www.brookings.edu/articles/2014-brown-center-report-on-american-education/)
  reads NAEP's long-term-trend homework question from 1984 to 2012 and finds
  the load "remarkably stable" for thirty years.
- **The strongest disagreement is about which unit matters.** Berry and West,
  [*Growing Pains*](https://academic.oup.com/jleo/article-abstract/26/1/1/913468)
  (2010), find that larger *schools* lowered later earnings while larger
  *districts* were, if anything, mildly beneficial — the opposite sign from the
  "big district, remote bureaucracy" reading of the same consolidation.

## Where this goes

Hours in the building, not days on the calendar: the American Time Use Survey
and the CCD's instructional-hours fields are the next pull.
{% endraw %}

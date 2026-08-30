# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "matplotlib>=3.7",
#     "pandas>=2.0",
#     "tabulate>=0.9",
# ]
# ///
#
# The notebook behind an exploration on ericvoss.com. `make sync SLUG=<slug>`
# turns it into the page body; `make edit SLUG=<slug>` opens it.
#
# Add analysis dependencies to the PEP 723 list above, not to pyproject.toml —
# that one exists to provide the marimo CLI and nothing else. The list is why
# `make edit` passes --sandbox; without the flag marimo ignores it.
#
# What reaches the page and what does not is in CLAUDE.md under "Notebooks".
# The short version: prose is `mo.md("""...""")` with a plain literal, code
# cells publish unless marked hide_code=True, and cell outputs never publish —
# a chart reaches the page only via `savefig` plus a link from a prose cell.

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    from pathlib import Path

    import marimo as mo
    import matplotlib

    # Before pyplot, not after: there is no display here and a file never needs
    # one. Getting the order wrong picks an interactive backend and hangs.
    matplotlib.use("Agg")

    import matplotlib.pyplot as plt
    import pandas as pd

    SLUG = "REPLACE-ME"  # must match this file's name in _notebooks/
    return Path, SLUG, mo, pd, plt


@app.cell(hide_code=True)
def _(Path, SLUG, plt):
    # The night palette, lifted from _sass/_00-base.scss, so a figure looks cut
    # from the page rather than pasted onto it.
    #
    # Dark on purpose. The site flips between night glass and day parchment on
    # a `data-theme` toggle and a PNG cannot follow it, so a figure is a screen
    # set into the page instead — which is how the theme already frames every
    # image (.prose p:has(> img), section 50). One palette, correct in both.
    PLATE = "#0b1030"  # the deep stop of the night body wash
    INK = "#f2f5ff"  # --ink
    MUTED = "#93a0d8"  # --muted
    GRID = "#28336b"  # --muted, at about the alpha the theme's hairlines carry
    SERIES = [
        "#ffd76b",  # --gold
        "#7ef0e0",  # --crystal
        "#c79bff",  # --magic
        "#64d97a",  # --hp
        "#6aa8ff",  # --mp
        "#ff7a7a",  # --danger
    ]

    # The chart font is the matplotlib default, and that is settled: the site's
    # four faces are woff2 and matplotlib reads only ttf/otf. A legible axis
    # label beats a pixel one, and the frame around the figure carries the
    # theme regardless.
    plt.rcParams.update(
        {
            "figure.figsize": (8, 4.5),
            "figure.dpi": 160,
            "figure.facecolor": PLATE,
            "savefig.facecolor": PLATE,
            "axes.facecolor": PLATE,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.titlepad": 14,
            "axes.grid": True,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": plt.cycler(color=SERIES),
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK,
            "ytick.labelcolor": INK,
            "text.color": INK,
            "legend.frameon": False,
            "legend.labelcolor": INK,
            "font.size": 11,
        }
    )

    def _root():
        """Walk up to the directory holding _config.yml.

        By search rather than by counting parents: marimo's working directory
        depends on where it was launched from, and `__file__` is not reliable
        inside a kernel.
        """
        start = Path.cwd()
        for d in (start, *start.parents):
            if (d / "_config.yml").exists():
                return d
        raise RuntimeError("no _config.yml above here — run this inside the site repo")

    ROOT = _root()
    RESEARCH = ROOT / "_research" / SLUG
    RESEARCH.mkdir(parents=True, exist_ok=True)

    def savefig(fig, name):
        """Write assets/images/<SLUG>-<name>.png and print the line to paste.

        Cell outputs are not exported, so this plus a reference from a prose
        cell is the only way a chart reaches the site. html-proofer fails the
        build on a missing file and on missing or placeholder alt text, so
        write real alt text and never reference an image you have not made.
        """
        images = ROOT / "assets" / "images"
        images.mkdir(parents=True, exist_ok=True)
        out = images / f"{SLUG}-{name}.png"
        fig.savefig(out, bbox_inches="tight", pad_inches=0.3)
        print(f"![WRITE REAL ALT TEXT HERE](/assets/images/{out.name})")
        return out

    return RESEARCH, savefig


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The dump

    > REPLACE-ME — the raw idea, verbatim, exactly as it was handed over.
    > Do not tidy it up.

    ## The question(s)

    REPLACE-ME — the specific, answerable questions this notebook is trying
    to settle. If the dump already asks them clearly, keep its wording with
    minimal edits; otherwise convert the dump into questions the data could
    actually answer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Lit review

    REPLACE-ME — what already exists on the question(s): papers, published
    analyses, posts, anyone who has seriously tried to answer this before.
    A line each on what they found and where they stop short, cited inline.
    If prior work already settles the question, that is the finding — say so
    instead of re-deriving it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The data

    REPLACE-ME — the sources that could bear on the question(s), a line each
    on what they cover, then which one(s) this notebook actually pulls and
    why. A rejected source keeps its reason.

    ## EDA
    """)
    return


@app.cell
def _(RESEARCH, pd):
    # The pull. Prefer a primary source and fetch it here rather than typing
    # numbers in by hand — the point of committing this is that the number can
    # be re-derived a year from now. Save the raw response into _research/ if
    # it is small; if it is not, leave the fetch here and say in a comment
    # where it came from and how big it is.
    df = pd.DataFrame({"year": range(2016, 2026), "thing": [3, 5, 4, 8, 13, 21, 34, 30, 45, 61]})
    df.to_csv(RESEARCH / "data.csv", index=False)
    df
    return (df,)


@app.cell
def _(df):
    # General EDA before anything question-specific: shape, missingness, and
    # the spread of the key variables. The point is to find the data's
    # problems before the question does.
    print(df.shape)
    print(df.isna().sum())
    df.describe()
    return


@app.cell
def _(df, plt, savefig):
    _fig, _ax = plt.subplots()
    _ax.plot(df["year"], df["thing"], marker="o", linewidth=2)
    _ax.set_title("Say what the chart shows, not what it is")
    _ax.set_xlabel("Year")
    _ax.set_ylabel("Thing")
    savefig(_fig, "thing-by-year")
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    REPLACE-ME — what the EDA actually showed, general first and then
    question-specific. Every number here is one the cells above printed —
    paste the printed value, never a remembered one.

    A figure goes here as the `![alt](/assets/images/...)` line that `savefig`
    printed, and not before the PNG exists: html-proofer fails the build on a
    reference to an image that is not committed.

    What the data *doesn't* show belongs here too — the confounds, the gaps,
    the sample you wish you had. "This doesn't show what I hoped" is a
    finding.

    ## Next steps

    REPLACE-ME — deeper analysis approaches that might prove fruitful in
    answering the question(s). A short list, concrete enough to start from.
    """)
    return


if __name__ == "__main__":
    app.run()

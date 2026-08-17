# ---------------------------------------------------------------------------
# Template for the analysis behind an exploration note. Copy it to
# _research/<slug>/analysis.py and edit it. Nothing imports this file.
#
# The format is jupytext "percent": a plain .py cut into `# %%` cells. VS Code
# and PyCharm open it as a notebook with no conversion, Jupyter opens it with
# jupytext installed, and `python analysis.py` runs the whole thing headless.
#
# It is deliberately not a .ipynb. An .ipynb diff is JSON with base64 image
# blobs in it, which is unreviewable in a PR from a phone — and its stored
# outputs drift out of sync with the code that made them without ever saying so.
# A .py has neither problem and still opens as a notebook.
#
#   pip install -r requirements.txt
#   python analysis.py          # writes every figure the note references
#
# Figures go to assets/images/ because that is the only directory Jekyll serves.
# Everything else stays in _research/, which is committed and never built.
# ---------------------------------------------------------------------------

# %% setup
from pathlib import Path

import matplotlib

# Before pyplot, not after: a cloud VM has no display, and a file never needs
# one. Getting the order wrong picks an interactive backend and hangs.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SLUG = "REPLACE-ME"  # must match the filename of _wip/<slug>.md


def _repo_root() -> Path:
    """Walk up to the directory holding _config.yml.

    Resolved by search rather than by counting parents, because `__file__` is
    the path when this runs as a script and undefined when a cell runs in a
    notebook kernel, and the two have different working directories.
    """
    start = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    for d in (start, *start.parents):
        if (d / "_config.yml").exists():
            return d
    raise RuntimeError("no _config.yml above here — run this inside the site repo")


ROOT = _repo_root()
HERE = ROOT / "_research" / SLUG
IMAGES = ROOT / "assets" / "images"
HERE.mkdir(parents=True, exist_ok=True)


# %% site style
# The night palette, lifted from _sass/_00-base.scss, so a figure looks cut from
# the page rather than pasted onto it.
#
# Dark on purpose. The site flips between night glass and day parchment on a
# `data-theme` toggle and a PNG cannot follow it, so a figure is a screen set
# into the page instead — which is how the theme already frames every image
# (.prose p:has(> img), section 50). One palette, correct in both modes.
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

# The chart font is the matplotlib default, and that is settled: the site's four
# faces are woff2 and matplotlib reads only ttf/otf. A legible axis label beats a
# pixel one, and the frame around the figure carries the theme regardless.
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


def savefig(fig, name: str) -> Path:
    """Write assets/images/<SLUG>-<name>.png and print the line to paste.

    Every figure the note embeds has to exist as a committed file, and every one
    needs alt text: html-proofer checks both and either turns the PR red.
    """
    IMAGES.mkdir(parents=True, exist_ok=True)
    out = IMAGES / f"{SLUG}-{name}.png"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"![WRITE REAL ALT TEXT HERE](/assets/images/{out.name})")
    return out


# %% pull
# Prefer a primary source, and fetch it here rather than typing numbers in by
# hand — the point of committing this file is that the number can be re-derived
# a year from now. Save the raw response next to this file if it is small; if it
# is not, leave the fetch here and note in a comment where it came from and how
# big it is.
#
# Replace this frame with the real pull.
df = pd.DataFrame(
    {
        "year": range(2016, 2026),
        "thing": [3, 5, 4, 8, 13, 21, 34, 30, 45, 61],
    }
)
df.to_csv(HERE / "data.csv", index=False)


# %% figure
fig, ax = plt.subplots()
ax.plot(df["year"], df["thing"], marker="o", linewidth=2)
ax.set_title("Say what the chart shows, not what it is")
ax.set_xlabel("Year")
ax.set_ylabel("Thing")
savefig(fig, "thing-by-year")


# %% numbers
# Anything the prose asserts gets computed here, so the note and the script
# cannot drift apart. Print it, then paste the printed value — never a
# remembered one.
print(f"peak: {df['thing'].max()} in {df.loc[df['thing'].idxmax(), 'year']}")
print(df.to_markdown(index=False))  # to_markdown needs tabulate

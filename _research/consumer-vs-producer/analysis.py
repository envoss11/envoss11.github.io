# ---------------------------------------------------------------------------
# Analysis behind _wip/consumer-vs-producer.md: does the print record show
# consumer-identity language displacing worker/producer-identity language?
#
# The format is jupytext "percent": a plain .py cut into `# %%` cells. VS Code
# and PyCharm open it as a notebook with no conversion, Jupyter opens it with
# jupytext installed, and `python analysis.py` runs the whole thing headless.
#
#   pip install -r requirements.txt
#   python analysis.py          # writes every figure the note references
#
# Data: Google Books Ngram Viewer JSON API, American English 2019 corpus
# (en-US-2019), 1900-2019, smoothing=0 (raw annual values; smoothing is done
# here so the window is stated in code). The raw API responses are committed
# next to this file as ngrams-en-US-2019.json (~100 KB) so the numbers can be
# re-derived even if the API changes or disappears.
# ---------------------------------------------------------------------------

# %% setup
import json
import time
from pathlib import Path

import matplotlib

# Before pyplot, not after: a cloud VM has no display, and a file never needs
# one. Getting the order wrong picks an interactive backend and hangs.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import requests  # noqa: E402

SLUG = "consumer-vs-producer"


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
    """Write assets/images/<SLUG>-<name>.png and print the line to paste."""
    IMAGES.mkdir(parents=True, exist_ok=True)
    out = IMAGES / f"{SLUG}-{name}.png"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"figure -> /assets/images/{out.name}")
    return out


# %% pull
# One API call per group, cached to disk. The API drops a phrase that has no
# match and normalizes apostrophes ("workers' rights" comes back as
# "workers ' rights"), so keys are cleaned on the way in.
API = "https://books.google.com/ngrams/json"
CORPUS = "en-US-2019"
Y0, Y1 = 1900, 2019
YEARS = list(range(Y0, Y1 + 1))
RAW = HERE / f"ngrams-{CORPUS}.json"

GROUPS = {
    "rights": ["consumer rights", "workers' rights", "labor rights", "employee rights"],
    "nouns": ["consumers", "workers", "producers", "citizens"],
    "labor": [
        "laborers", "craftsmen", "labor movement", "labor unions", "trade unions",
        "working class", "shop floor", "assembly line",
    ],
    "consumer": [
        "consumer movement", "consumer goods", "consumer protection",
        "consumer confidence", "consumer culture", "consumer society", "consumerism",
    ],
    "singular": ["the consumer", "the worker"],
    # Not plotted; pulled because the prose compares it against "consumers".
    "extra": ["customers"],
}


def fetch(phrases: list[str]) -> dict[str, list[float]]:
    r = requests.get(
        API,
        params={
            "content": ",".join(phrases),
            "year_start": Y0,
            "year_end": Y1,
            "corpus": CORPUS,
            "smoothing": 0,
        },
        timeout=60,
    )
    r.raise_for_status()
    return {s["ngram"].replace(" ' ", "' "): s["timeseries"] for s in r.json()}


series = json.loads(RAW.read_text()) if RAW.exists() else {}
stale = [g for g in GROUPS.values() if any(p not in series for p in g)]
for phrases in stale:
    series.update(fetch(phrases))
    time.sleep(2)  # polite; the endpoint rate-limits bursts
if stale:
    RAW.write_text(json.dumps(series))

df = pd.DataFrame(series, index=YEARS)
missing = [p for g in GROUPS.values() for p in g if p not in df.columns]
assert not missing, f"API returned nothing for: {missing}"

# 5-year centered rolling mean: enough to kill single-year OCR spikes without
# moving a peak by more than a year or two. All peaks and plots use this.
sm = df.rolling(5, center=True, min_periods=1).mean()


# %% figure: rights compounds
# The dump's headline claim, tested directly. Frequencies are each phrase's
# share of all same-length ngrams that year, scaled to "per billion".
B = 1e9
fig, ax = plt.subplots()
for col in GROUPS["rights"]:
    ax.plot(sm.index, sm[col] * B, linewidth=2, label=f"“{col}”")
ax.axvline(1962, color=MUTED, linewidth=0.8, linestyle=":")
ax.text(1962.8, ax.get_ylim()[1] * 0.97, "JFK's consumer\nmessage, 1962",
        fontsize=8, color=MUTED, va="top")
ax.axvspan(1969, 1978, color=GRID, alpha=0.35, zorder=0)
ax.set_xlim(1930, 2019)
ax.set_title("“Consumer rights” led “workers' rights” for one decade: 1969–1978")
ax.set_xlabel("Year")
ax.set_ylabel("Occurrences per billion ngrams")
ax.legend(fontsize=9)
savefig(fig, "rights")

# %% figure: identity nouns
fig, ax = plt.subplots()
for col in GROUPS["nouns"]:
    ax.plot(sm.index, sm[col] * 1e6, linewidth=2, label=f"“{col}”")
ax.set_xlim(1900, 2019)
ax.set_title("American books never stopped talking about workers")
ax.set_xlabel("Year")
ax.set_ylabel("Occurrences per million words")
ax.legend(fontsize=9)
savefig(fig, "nouns")

# %% figure: peak years
# When did each term's smoothed frequency peak? Sorting by peak year turns the
# vocabulary into a timeline of eras. Mixed ngram lengths are fine here —
# only the year is compared, never the level.
LABOR_TERMS = (
    GROUPS["labor"]
    + ["workers", "producers", "the worker"]
    + ["workers' rights", "labor rights", "employee rights"]
)
CONSUMER_TERMS = GROUPS["consumer"] + ["consumers", "the consumer", "consumer rights"]

peaks = pd.DataFrame(
    {
        "term": LABOR_TERMS + CONSUMER_TERMS,
        "side": ["labor"] * len(LABOR_TERMS) + ["consumer"] * len(CONSUMER_TERMS),
    }
)
peaks["peak"] = [int(sm[t].idxmax()) for t in peaks["term"]]
peaks = peaks.sort_values("peak").reset_index(drop=True)

fig, ax = plt.subplots(figsize=(8, 6.5))
colors = {"labor": SERIES[0], "consumer": SERIES[1]}
for i, row in peaks.iterrows():
    ax.hlines(i, 1900, row["peak"], color=GRID, linewidth=0.8)
    ax.plot(row["peak"], i, "o", markersize=7, color=colors[row["side"]])
    ax.text(1898, i, f"{row['term']}  ", ha="right", va="center", fontsize=9)
    ax.text(row["peak"] + 2, i, str(row["peak"]), va="center", fontsize=8, color=MUTED)
ax.set_yticks([])
ax.set_xlim(1900, 2032)
ax.set_ylim(-1, len(peaks))
ax.grid(axis="y", visible=False)
ax.spines["left"].set_visible(False)
ax.set_title("Peak year of each term in American books, 1900–2019")
handles = [
    plt.Line2D([], [], marker="o", linestyle="", color=colors["labor"], label="labor / production terms"),
    plt.Line2D([], [], marker="o", linestyle="", color=colors["consumer"], label="consumer terms"),
]
ax.legend(handles=handles, fontsize=9, loc="upper left")
savefig(fig, "peaks")

# %% figure: the critique
# "consumerism" is a unigram plotted against bigrams; each is a share of its
# own denominator, which is how the Ngram Viewer itself plots mixed lengths.
# The gap is ~25x, far beyond anything the denominator difference could cause.
fig, ax = plt.subplots()
for col in ["consumerism", "consumer rights", "consumer culture", "consumer society"]:
    ax.plot(sm.index, sm[col] * B, linewidth=2, label=f"“{col}”")
ax.set_xlim(1950, 2019)
ax.set_title("The critique outgrew the cause")
ax.set_xlabel("Year")
ax.set_ylabel("Occurrences per billion ngrams")
ax.legend(fontsize=9)
savefig(fig, "critique")


# %% numbers
# Anything the prose asserts gets computed here, so the note and the script
# cannot drift apart.
def peak_of(col):
    return int(sm[col].idxmax()), sm[col].max()


print("\n== peak years (5yr-smoothed, en-US-2019) ==")
print(peaks.to_markdown(index=False))

print("\n== levels and ratios ==")
for col in ["consumer rights", "workers' rights", "labor rights", "consumerism"]:
    py, pv = peak_of(col)
    print(f"{col!r}: peak {py} at {pv:.3e}; 2019 raw {df[col].iloc[-1]:.3e}")

wr2019 = df["workers' rights"].iloc[-1]
print(f"\nworkers' rights / consumer rights, 2019: "
      f"{wr2019 / df['consumer rights'].iloc[-1]:.1f}x")
print(f"workers / consumers, 2019: {df['workers'].iloc[-1] / df['consumers'].iloc[-1]:.1f}x")
print(f"workers / consumers, 1942: {df['workers'].loc[1942] / df['consumers'].loc[1942]:.1f}x")

for y in (1900, 1950, 1977, 2019):
    print(f"consumers/workers ratio {y}: {df['consumers'].loc[y] / df['workers'].loc[y]:.3f}")
for y in (1900, 1950, 2019):
    print(f"consumers/producers ratio {y}: {df['consumers'].loc[y] / df['producers'].loc[y]:.2f}")
for y in (1950, 1976, 2019):
    print(f"'the consumer'/'the worker' ratio {y}: "
          f"{df['the consumer'].loc[y] / df['the worker'].loc[y]:.2f}")

print(f"\n'consumer rights' growth 1950 -> 1977 peak: "
      f"{sm['consumer rights'].loc[1977] / sm['consumer rights'].loc[1950]:.0f}x")
print(f"consumerism / consumer rights, 2019: "
      f"{df['consumerism'].iloc[-1] / df['consumer rights'].iloc[-1]:.0f}x")
print(f"'consumerism' growth 1950 -> 2019: "
      f"{df['consumerism'].iloc[-1] / df['consumerism'].loc[1950]:.0f}x")

lead_wr = [y for y in YEARS if sm['consumer rights'].loc[y] > sm["workers' rights"].loc[y]]
lead_lr = [y for y in YEARS if sm['consumer rights'].loc[y] > sm['labor rights'].loc[y]]
print(f"'consumer rights' above 'workers' rights': {min(lead_wr)}-{max(lead_wr)}")
print(f"'consumer rights' above 'labor rights': {min(lead_lr)}-{max(lead_lr)}")
er_py, er_pv = peak_of('employee rights')
cr_py, cr_pv = peak_of('consumer rights')
print(f"'employee rights' peak ({er_py}) vs 'consumer rights' peak ({cr_py}): "
      f"{er_pv / cr_pv:.1f}x higher")

cp = [y for y in YEARS if sm['consumers'].loc[y] > sm['producers'].loc[y]]
print(f"'consumers' above 'producers' since: {max(y for y in YEARS if y not in cp) + 1}")
cust_py, _ = peak_of('customers')
below = [y for y in YEARS if sm['customers'].loc[y] < sm['consumers'].loc[y]]
print(f"'customers': peak {cust_py}; below 'consumers' in "
      f"{len(below)} of {len(YEARS)} years ({min(below)}-{max(below)})" if below
      else f"'customers': peak {cust_py}; above 'consumers' in every year")

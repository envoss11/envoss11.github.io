# ---------------------------------------------------------------------------
# Analysis behind _wip/automated-prompt-engineering.md.
#
#   pip install -r requirements.txt
#   python analysis.py          # writes every figure the note references
#
# There is no fetch step. Every number here was transcribed by hand out of a
# results table in a published paper, because that is the only form this data
# exists in — nobody publishes a machine-readable corpus of "human prompt vs.
# optimized prompt" pairs, which is itself part of the finding. head-to-head.csv
# carries a `url` on every row so any figure can be checked against its source.
#
# The one column that is a judgement call rather than a transcription is
# `baseline_strength`, and it is the column the whole argument turns on:
#
#   default  the human prompt was the first reasonable thing written down — a
#            DSPy signature docstring, a one-line task description. Nobody
#            iterated on it.
#   tuned    the human prompt was the best of a deliberate human search. Battle
#            and Gollapudi picked the best of 60 hand-written system messages;
#            Kojima et al. picked "Let's think step by step" out of at least
#            nine candidates.
#   expert   a practitioner spent hours iterating against measured feedback.
#
# Read it as three coarse bins, not a scale. The assignment for every row is
# defended in notes.md.
# ---------------------------------------------------------------------------

# %% setup
from pathlib import Path

import matplotlib

# Before pyplot, not after: a cloud VM has no display, and a file never needs
# one. Getting the order wrong picks an interactive backend and hangs.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SLUG = "automated-prompt-engineering"


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
    print(f"  wrote /assets/images/{out.name}")
    return out


# %% load
df = pd.read_csv(HERE / "head-to-head.csv")

# Every paper reports on its own scale. Put the 0-1 metrics on 0-100 so a
# "point" means the same thing everywhere, and leave APE's normalized BBH
# figures out of the arithmetic entirely — they are a paired comparison, which
# is enough to score a win or a loss, but their units are not accuracy points.
scaled = df["scale"].eq("0-1")
df["human_pts"] = df["human"].where(~scaled, df["human"] * 100)
df["auto_pts"] = df["auto"].where(~scaled, df["auto"] * 100)
df["delta"] = df["auto_pts"] - df["human_pts"]

# A margin under a quarter of a point is a tie, not a win. Two rows sit exactly
# on zero (Battle and Gollapudi's Mistral-7B runs at n=10 and n=50); one is
# 0.03 points wide (Valdi's slow generation) and its own authors call it "well
# within the observed variance".
TIE = 0.25
df["outcome"] = pd.cut(
    df["delta"], [-1e9, -TIE, TIE, 1e9], labels=["human wins", "tie", "optimizer wins"]
)

ORDER = ["default", "tuned", "expert"]
LABELS = {
    "default": "Default\n(first thing written)",
    "tuned": "Tuned\n(best of a human search)",
    "expert": "Expert\n(hours of iteration)",
}

print(f"{len(df)} paired comparisons from {df['source'].nunique()} sources\n")


# %% figure — who wins, by how good the human prompt was
counts = (
    df.groupby(["baseline_strength", "outcome"], observed=False)
    .size()
    .unstack(fill_value=0)
    .reindex(ORDER)
)
shares = counts.div(counts.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(8, 4.2))
left = pd.Series(0.0, index=shares.index)
for col, colour in [
    ("optimizer wins", SERIES[1]),
    ("tie", SERIES[4]),
    ("human wins", SERIES[0]),
]:
    ax.barh(range(len(shares)), shares[col], left=left, color=colour, label=col, height=0.6)
    for i, (v, l) in enumerate(zip(shares[col], left)):
        if v >= 7:
            ax.text(l + v / 2, i, f"{counts[col].iloc[i]:.0f}", ha="center", va="center",
                    color=PLATE, fontweight="bold", fontsize=10)
    left += shares[col]

ax.set_yticks(range(len(shares)), [LABELS[i] for i in shares.index])
ax.set_xlabel("Share of comparisons (%)")
ax.set_xlim(0, 100)
ax.invert_yaxis()
ax.grid(axis="y", visible=False)
ax.set_title("The optimizer keeps winning — the human baseline barely changes that")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=3)
savefig(fig, "win-rate")


# %% figure — but the margin collapses
cmp = df[df["delta_comparable"]].copy()

fig, ax = plt.subplots(figsize=(8, 4.2))
for i, strength in enumerate(ORDER):
    d = cmp.loc[cmp["baseline_strength"] == strength, "delta"]
    if d.empty:
        continue
    ax.scatter(d, [i] * len(d), s=70, alpha=0.75, color=SERIES[i], zorder=3,
               edgecolors=PLATE, linewidths=0.8)
    ax.scatter([d.mean()], [i], marker="|", s=900, color=INK, zorder=4, linewidths=2.5)
    ax.text(d.mean(), i + 0.30, f"mean {d.mean():+.1f}", ha="center", va="top",
            color=INK, fontsize=10)

ax.axvline(0, color=MUTED, linewidth=1.2, zorder=2)
ax.set_yticks(range(len(ORDER)), [LABELS[s] for s in ORDER])
ax.set_xlabel("Optimizer minus human, in points of the paper's own metric")
ax.set_ylim(len(ORDER) - 0.4, -0.6)
ax.grid(axis="y", visible=False)
ax.set_title("What optimization is worth depends on what it is measured against")
savefig(fig, "margin-by-baseline")


# %% figure — invention versus refinement
# The zero-shot chain-of-thought stack is the cleanest case in the literature
# where a human idea and an automated search were applied to the same task, one
# on top of the other, and both were measured. Numbers from APE section 4.3:
# the no-prompt baseline and Kojima et al.'s "Let's think step by step", then
# APE's search over answer prefixes on top of it.
cot = pd.DataFrame(
    {
        "task": ["MultiArith", "GSM8K"],
        "no_prompt": [17.7, 10.4],
        "human_idea": [78.7, 40.7],
        "auto_search": [82.0, 43.0],
    }
)
cot["invention"] = cot["human_idea"] - cot["no_prompt"]
cot["refinement"] = cot["auto_search"] - cot["human_idea"]

fig, ax = plt.subplots(figsize=(8, 3.6))
y = range(len(cot))
ax.barh(y, cot["invention"], color=SERIES[0], height=0.55,
        label='human idea: "Let\'s think step by step"')
ax.barh(y, cot["refinement"], left=cot["invention"], color=SERIES[1], height=0.55,
        label="automated search over that prompt")
for i, r in cot.iterrows():
    ax.text(r["invention"] / 2, i, f"+{r['invention']:.1f}", ha="center", va="center",
            color=PLATE, fontweight="bold")
    ax.text(r["invention"] + r["refinement"] + 1.5, i, f"+{r['refinement']:.1f}",
            va="center", color=SERIES[1], fontweight="bold")
ax.set_yticks(list(y), cot["task"])
ax.set_xlabel("Accuracy points gained over no prompt at all (text-davinci-002)")
ax.set_xlim(0, 78)
ax.invert_yaxis()
ax.grid(axis="y", visible=False)
ax.set_title("Inventing the strategy was worth 16x refining its wording")
ax.legend(loc="lower right")
savefig(fig, "invention-vs-refinement")


# %% numbers
# Everything the note asserts is printed here, so the prose and the script
# cannot drift apart.
print("\n--- outcomes by baseline strength ---")
print(counts.to_markdown())
print(f"\noptimizer win rate overall: "
      f"{(df['outcome'] == 'optimizer wins').mean() * 100:.0f}% of {len(df)}")
for s in ORDER:
    sub = df[df["baseline_strength"] == s]
    print(f"  {s:<8} {(sub['outcome'] == 'optimizer wins').mean() * 100:5.0f}% "
          f"of {len(sub):2d}")

print("\n--- margin, comparable rows only ---")
print(cmp.groupby("baseline_strength", observed=False)["delta"]
      .agg(["count", "mean", "median", "min", "max"])
      .reindex(ORDER).round(2).to_markdown())

print("\n--- the two head-to-heads against a genuinely tuned human prompt ---")
print(cmp[cmp["baseline_strength"].isin(["tuned", "expert"])]
      [["source", "task", "model", "human_pts", "auto_pts", "delta"]]
      .round(2).to_markdown(index=False))

print("\n--- invention vs refinement ---")
print(cot.to_markdown(index=False))
ratio = cot["invention"].sum() / cot["refinement"].sum()
print(f"invention was worth {ratio:.1f}x refinement, pooled over both tasks")

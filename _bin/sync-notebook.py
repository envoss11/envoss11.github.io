#!/usr/bin/env python3
"""Regenerate a note's page body from the marimo notebook behind it.

    make sync SLUG=<slug>        one note
    make sync                    every notebook
    make sync-check              exit 1 if any page is stale (what CI runs)

The notebook is the source. `_wip/<slug>.md` (or `_posts/<date>-<slug>.md`
once it is published) keeps its Jekyll front matter and gets everything below
it rewritten from `marimo export md`. Editing the generated half by hand is
pointless — the next sync overwrites it — so the file says so in a comment
right under the front matter.

This lives in `_bin/` rather than `bin/` on purpose: Jekyll skips
`_`-prefixed directories on its own, so there is no `exclude:` entry to keep
in step with it. See trap 6 in CLAUDE.md for why that matters.

Three things happen between marimo's markdown and Jekyll's:

1. **Marimo's own YAML header comes off.** It carries `title:` and
   `marimo-version:`, which would collide with the page's real front matter.

2. **Cell fences are rewritten, and hidden cells are dropped.** Marimo emits
   ```` ```python {.marimo} ````, and kramdown's GFM parser does not recognise
   a fence with a brace attribute on it — the block renders as mangled prose
   rather than as code. So the info string is cut back to plain `python`.
   A cell marked `hide_code=True` is plumbing the author collapsed in the
   notebook UI, so it does not reach the page at all. That is a real editing
   control and the count is printed every run, never applied silently.

3. **The whole body is wrapped in `{% raw %}`.** Jekyll runs Liquid before
   Markdown, including inside fenced code blocks, so a notebook containing a
   dict literal, an f-string, or a `${}` would otherwise fail the build — trap
   1 in CLAUDE.md, and generated notebook code trips it constantly. Nothing in
   a note body wants Liquid, so the wrap is unconditional.

Only the standard library, and marimo is invoked as a subprocess rather than
imported, so `$MARIMO` can point at whatever holds it — `uv run marimo` here,
a bare `marimo` on a machine that has one.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "_notebooks"

# Opening or closing fence: three or more backticks or tildes, plus whatever
# info string follows. Length is captured because a longer fence nests inside a
# shorter one, and marimo lengthens the delimiter when a cell contains one.
FENCE = re.compile(r"^(?P<ticks>`{3,}|~{3,})(?P<info>.*)$")

# What marimo writes for a cell: ```python {.marimo} or
# ```python {.marimo hide_code="true"}.
CELL = re.compile(r"^python\s*\{\.marimo(?P<attrs>[^}]*)\}$")

# What marimo writes between two adjacent markdown cells.
SEPARATOR = "<!---->"

BANNER = (
    "<!-- Generated from _notebooks/{slug}.py by `make sync SLUG={slug}`. "
    "Edits below this line are overwritten. -->"
)


def fail(msg: str) -> None:
    sys.exit(f"sync-notebook: {msg}")


def page_for(slug: str) -> Path:
    """Find the page a notebook feeds, in either tier.

    `_wip/` first, then `_posts/`, because `make publish` moves the page and
    leaves the notebook where it is — a published note still syncs.
    """
    wip = ROOT / "_wip" / f"{slug}.md"
    posts = sorted((ROOT / "_posts").glob(f"*-{slug}.md"))
    if wip.exists() and posts:
        fail(f"{slug} has a page in both _wip/ and _posts/ — remove one")
    if wip.exists():
        return wip
    if len(posts) > 1:
        fail(f"{slug} matches more than one file in _posts/: {[p.name for p in posts]}")
    if posts:
        return posts[0]
    fail(f"no page for {slug} — expected _wip/{slug}.md or _posts/<date>-{slug}.md")
    raise AssertionError  # unreachable; keeps type checkers quiet


def export(notebook: Path) -> str:
    marimo = shlex.split(os.environ.get("MARIMO", "marimo"))
    try:
        proc = subprocess.run(
            [*marimo, "export", "md", str(notebook)],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        fail(f"{marimo[0]} not found — set $MARIMO, or `uv sync` to install it")
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        fail(f"marimo could not export {notebook.name}")
    return proc.stdout


def strip_header(md: str) -> str:
    """Drop marimo's own `---` block, which is not this page's front matter."""
    lines = md.splitlines()
    if not lines or lines[0].strip() != "---":
        return md
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1 :])
    return md


def convert(md: str) -> tuple[list[str], int, int]:
    """Rewrite marimo's fences for kramdown. Returns (lines, shown, hidden)."""
    out: list[str] = []
    shown = hidden = 0
    close: str | None = None  # the delimiter that ends the fence we are inside
    dropping = False

    for line in md.splitlines():
        if close is not None:
            # Inside a fence. Only a delimiter at least as long as the opening
            # one, with nothing after it, closes it.
            m = FENCE.match(line)
            if m and m["ticks"][0] == close[0] and len(m["ticks"]) >= len(close) and not m["info"].strip():
                if not dropping:
                    out.append(line)
                close, dropping = None, False
            elif not dropping:
                out.append(line)
            continue

        m = FENCE.match(line)
        if m:
            cell = CELL.match(m["info"].strip())
            close = m["ticks"]
            if cell is None:
                # A fence the author wrote inside a markdown cell. Leave it.
                out.append(line)
                continue
            if 'hide_code="true"' in cell["attrs"]:
                hidden += 1
                dropping = True
                # Drop the blank line this cell was separated by, so hiding a
                # cell does not leave a hole in the prose.
                while out and not out[-1].strip():
                    out.pop()
                continue
            shown += 1
            out.append(f"{m['ticks']}python")
            continue

        # Marimo separates two adjacent markdown cells with a bare `<!---->`
        # and no blank line around it. Kramdown reads that as a lazy
        # continuation and welds the two cells into one paragraph, so the
        # separator becomes the blank line it was standing in for.
        if line.strip() == SEPARATOR:
            line = ""

        # Outside any fence: collapse blank runs, which hidden cells, the
        # separator, and marimo's own spacing all leave behind.
        if not line.strip() and (not out or not out[-1].strip()):
            continue
        out.append(line)

    while out and not out[-1].strip():
        out.pop()
    return out, shown, hidden


def drop_leading_h1(lines: list[str]) -> tuple[list[str], str | None]:
    """The layout already renders `page.title` as the h1.

    A notebook that opens with `# Title` — which is the natural thing to write,
    and what it needs in the marimo UI — would put a second one on the page.
    Reported rather than dropped quietly.
    """
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if re.match(r"^#\s+\S", line):
            rest = lines[i + 1 :]
            while rest and not rest[0].strip():
                rest.pop(0)
            return lines[:i] + rest, line.strip()
        return lines, None
    return lines, None


def split_front_matter(page: Path) -> str:
    text = page.read_text()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{page.relative_to(ROOT)} has no front matter")
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[: i + 1])
    fail(f"{page.relative_to(ROOT)} has an unterminated front matter block")
    raise AssertionError  # unreachable


def render(slug: str, notebook: Path, page: Path) -> tuple[str, int, int, str | None]:
    body, shown, hidden = convert(strip_header(export(notebook)))
    body, dropped = drop_leading_h1(body)
    parts = [
        split_front_matter(page),
        "",
        BANNER.format(slug=slug),
        "",
        "{% raw %}",
        *body,
        "{% endraw %}",
        "",
    ]
    return "\n".join(parts), shown, hidden, dropped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slugs", nargs="*", help="notebook slugs; default is all of them")
    ap.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if a page is out of date with its notebook",
    )
    args = ap.parse_args()

    if args.slugs:
        notebooks = []
        for slug in args.slugs:
            nb = NOTEBOOKS / f"{slug}.py"
            if not nb.exists():
                fail(f"no such notebook: _notebooks/{slug}.py")
            notebooks.append(nb)
    else:
        notebooks = sorted(NOTEBOOKS.glob("*.py"))
        if not notebooks:
            print("no notebooks in _notebooks/ — nothing to sync")
            return 0

    stale = []
    for nb in notebooks:
        slug = nb.stem
        page = page_for(slug)
        text, shown, hidden, dropped = render(slug, nb, page)
        where = page.relative_to(ROOT)

        if args.check:
            if page.read_text() != text:
                stale.append(f"{where} is out of date with {nb.relative_to(ROOT)}")
            continue

        if page.read_text() == text:
            print(f"{where} already up to date")
            continue

        page.write_text(text)
        note = f"{shown} cell{'' if shown == 1 else 's'} published"
        if hidden:
            note += f", {hidden} hidden"
        print(f"wrote {where} — {note}")
        if dropped:
            print(f"  dropped the opening heading {dropped!r} — the layout renders the title")

    if stale:
        for line in stale:
            sys.stderr.write(f"sync-notebook: {line}\n")
        sys.stderr.write("run `make sync` and commit the result\n")
        return 1
    if args.check:
        print(f"{len(notebooks)} notebook(s) in sync with their pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

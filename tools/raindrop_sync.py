#!/usr/bin/env python3
"""Sync Raindrop.io bookmarks into _articles/.

Raindrop owns these files outright: notes and highlights are written there,
not here, and every run rewrites `_articles/` to match it. Each bookmark
becomes `_articles/<slug>.md`. Its highlights become blockquotes, so they show
up on the Excerpts page. A note on a highlight follows it as a paragraph, and
the bookmark's own note comes first. Bookmarks in a collection whose name
contains "queue" (any case), or in a collection nested under one, are left
out: those are still to be read. Notes listed in tools/raindrop_private.txt,
or on a bookmark tagged `private`, stay in Raindrop and off the site. A file whose bookmark is gone, or has moved
into a queue, is deleted. A slug is fixed when its file is first written, so
renaming a bookmark in Raindrop does not change its URL. Running the sync
twice in a row changes nothing.

    python3 tools/raindrop_sync.py [--dry-run]

It needs a Raindrop test token (app.raindrop.io/settings/integrations ->
create an app -> create test token), either in RAINDROP_TOKEN or in a file
named `.raindrop-token` at the repo root, which git ignores.

Standard library plus curl. Local use; CI and the site build never run it.
"""

import argparse
import html
import json
import os
import re
import sys
import subprocess
import time
import urllib.parse
from pathlib import Path

API = "https://api.raindrop.io/rest/v1"
PER_PAGE = 50  # the API's maximum
EXCLUDE = "queue"

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "_articles"
TOKEN_FILE = ROOT / ".raindrop-token"
PRIVATE_FILE = ROOT / "tools" / "raindrop_private.txt"
PRIVATE_TAG = "private"


# --- Raindrop ---------------------------------------------------------------

def read_token():
    tok = os.environ.get("RAINDROP_TOKEN", "").strip()
    if not tok and TOKEN_FILE.exists():
        tok = TOKEN_FILE.read_text().strip()
    if not tok:
        sys.exit(
            "no Raindrop token: set RAINDROP_TOKEN or put one in .raindrop-token\n"
            "(app.raindrop.io/settings/integrations -> create an app -> create test token)"
        )
    return tok


def get(path, tok, params=None, tries=4):
    """GET an API path through curl and return the parsed JSON. Python's
    http.client gets truncated chunked responses here, as it does from the
    Goodreads feed; curl does not. The token goes to curl on stdin, so it is
    not in the process list. Backs off when rate limited (the API allows 120
    requests a minute)."""
    query = "?" + "&".join(f"{k}={v}" for k, v in params.items()) if params else ""
    config = f'header = "Authorization: Bearer {tok}"\n'
    cmd = ["curl", "-sS", "--max-time", "60", "-A", "ericvoss.com raindrop_sync",
           "-K", "-", "-w", "\n%{http_code}", f"{API}{path}{query}"]
    for attempt in range(tries):
        run = subprocess.run(cmd, input=config, capture_output=True, text=True)
        body, _, code = run.stdout.rpartition("\n")
        if run.returncode == 0 and code == "200":
            return json.loads(body)
        if code == "401":
            sys.exit("Raindrop refused the token (401). Make a new test token and try again.")
        if attempt < tries - 1 and (run.returncode != 0 or code in ("429", "500", "502", "503", "504")):
            time.sleep(2 ** (attempt + 2))
            continue
        sys.exit(f"GET {path} failed: HTTP {code or '-'} {run.stderr.strip()}")


def collections(tok):
    """Every collection, root and nested, as {id: {"title", "parent"}}."""
    found = {}
    for path in ("/collections", "/collections/childrens"):
        for c in get(path, tok).get("items", []):
            parent = (c.get("parent") or {}).get("$id")
            found[c["_id"]] = {"title": c.get("title", ""), "parent": parent}
    return found


def excluded_collections(cols):
    """Ids of queue collections and of everything nested under them."""
    def queued(cid, seen=()):
        c = cols.get(cid)
        if c is None or cid in seen:
            return False
        return EXCLUDE in c["title"].casefold() or queued(c["parent"], seen + (cid,))
    return {cid for cid in cols if queued(cid)}


def all_raindrops(tok):
    """Every bookmark outside Trash, a page at a time."""
    page = 0
    while True:
        items = get("/raindrops/0", tok, {"perpage": PER_PAGE, "page": page, "sort": "created"}).get("items", [])
        yield from items
        if len(items) < PER_PAGE:
            return
        page += 1


def collection_id(item):
    return (item.get("collection") or {}).get("$id", item.get("collectionId"))


def highlights(item, tok):
    """The bookmark's highlights. List responses carry them; if one ever comes
    back without the field, ask for that bookmark on its own."""
    if "highlights" in item:
        return item["highlights"] or []
    return get(f"/raindrop/{item['_id']}", tok).get("item", {}).get("highlights") or []


# --- Markdown ---------------------------------------------------------------

def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80].strip("-") or "article"


def scalar(value):
    # JSON strings are valid YAML double-quoted scalars; ints and ISO dates
    # are written bare.
    if isinstance(value, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


LINE_START = re.compile(r"^(\s*)([#>+=-])")
NUMBERED = re.compile(r"^(\s*\d+)([.)])")


def quote_text(text):
    """A highlight is someone else's words, not Markdown: escape whatever
    kramdown would read as markup. Its paragraphs are joined by hard line
    breaks rather than split, so the blockquote stays one paragraph; a second
    paragraph would be styled as the excerpt's source."""
    lines = []
    for line in text.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if not line:
            continue
        line = html.escape(line, quote=False)
        line = re.sub(r"([\\`*_\[\]{}|$])", r"\\\1", line)
        line = LINE_START.sub(lambda m: m.group(1) + "\\" + m.group(2), line)
        line = NUMBERED.sub(lambda m: m.group(1) + "\\" + m.group(2), line)
        lines.append(line)
    return "  \n".join(f"> {line}" for line in lines)


CLICK_TRACKER = re.compile(r"^https?://[^/]+/CL0/([^/]+)/")
# Query parameters that only identify the reader or the campaign.
TRACKING = re.compile(r"^(utm_[^=]*|_bhlid|mc_cid|mc_eid|fbclid|gclid)(=|$)", re.I)


def drop_utm(part):
    """`a?x=1&utm_y=2` -> `a?x=1`: the parameters after the first `?`, without
    the tracking ones. Values are left as written, not re-encoded."""
    head, sep, query = part.partition("?")
    if not sep:
        return part
    kept = [p for p in query.split("&") if p and not TRACKING.match(p)]
    return head + ("?" + "&".join(kept) if kept else "")


def clean_link(url):
    """The link a reader should follow. Newsletter click-trackers of the form
    `<host>/CL0/<encoded target>/...` (TLDR uses them) carry a per-subscriber
    id, so the target is unwrapped. Tracking parameters are dropped from the
    query and from the fragment, where some sites put them."""
    m = CLICK_TRACKER.match(url)
    if m:
        url = urllib.parse.unquote(m.group(1))
    base, hash_, fragment = url.partition("#")
    return drop_utm(base) + hash_ + drop_utm(fragment)


def read_private(path=PRIVATE_FILE):
    """Bookmark and highlight ids whose notes are withheld, as strings."""
    if not path.exists():
        return set()
    lines = (line.split("#", 1)[0].strip() for line in path.read_text().splitlines())
    return {line for line in lines if line}


def render(item, hls, private=frozenset()):
    """The whole file for one bookmark. `private` holds ids whose notes are
    left out: a bookmark's id withholds all its notes, a highlight's just its own."""
    tags = {t.casefold() for t in item.get("tags") or []}
    withhold_all = str(item["_id"]) in private or PRIVATE_TAG in tags
    title = (item.get("title") or "").strip() or item.get("link", "")
    link = clean_link(item.get("link", ""))
    host = urllib.parse.urlsplit(link).hostname or item.get("domain") or ""
    fm = {
        "title": title,
        "source": link,
        "site": re.sub(r"^www\.", "", host),
        # When it was saved to Raindrop. Called date_read so articles sort
        # alongside books, which use the same key.
        "date_read": (item.get("created") or "")[:10] or None,
        "raindrop_id": item["_id"],
    }
    head = "".join(f"{k}: {scalar(v)}\n" for k, v in fm.items() if v not in (None, ""))

    blocks = []
    note = "" if withhold_all else (item.get("note") or "").strip()
    if note:
        blocks.append(note)
    for h in sorted(hls, key=lambda h: h.get("created") or ""):
        quoted = quote_text(h.get("text") or "")
        if not quoted:
            continue
        blocks.append(quoted)
        withhold = withhold_all or str(h.get("_id")) in private
        hnote = "" if withhold else (h.get("note") or "").strip()
        if hnote:
            blocks.append(hnote)

    body = "\n\n".join(blocks)
    return "---\n" + head + "---\n" + (f"\n{body}\n" if body else "")


# --- Files ------------------------------------------------------------------

def existing_by_id():
    found = {}
    for path in sorted(ARTICLES.glob("*.md")):
        m = re.search(r"^raindrop_id:\s*(\d+)\s*$", path.read_text(), re.M)
        if m:
            found[int(m.group(1))] = path
    return found


def plan(items, known, taken):
    """Pair each bookmark with its file. Returns [(path, item)]."""
    taken = set(taken)
    out = []
    for item in items:
        path = known.get(item["_id"])
        if path is None:
            slug = slugify((item.get("title") or "").strip() or item.get("domain") or "")
            if slug in taken:
                slug = f"{slug}-{item['_id']}"
            taken.add(slug)
            path = ARTICLES / f"{slug}.md"
        out.append((path, item))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    args = ap.parse_args()

    tok = read_token()
    private = read_private()
    cols = collections(tok)
    skip = excluded_collections(cols)
    if skip:
        names = sorted(cols[c]["title"] for c in skip)
        print("leaving out: " + ", ".join(names))

    items = [i for i in all_raindrops(tok) if collection_id(i) not in skip]

    known = existing_by_id()
    taken = {p.stem for p in ARTICLES.glob("*.md")}
    created, updated, unchanged = [], [], 0
    keep = set()

    if not args.dry_run:
        ARTICLES.mkdir(exist_ok=True)
    for path, item in plan(items, known, taken):
        keep.add(path)
        new = render(item, highlights(item, tok), private)
        old = path.read_text() if path.exists() else None
        if new == old:
            unchanged += 1
            continue
        (created if old is None else updated).append(path.name)
        if not args.dry_run:
            path.write_text(new)

    removed = [p for p in known.values() if p not in keep]
    for path in removed:
        if not args.dry_run:
            path.unlink()

    prefix = "would " if args.dry_run else ""
    print(f"{prefix}create {len(created)}, {prefix}update {len(updated)}, "
          f"{prefix}delete {len(removed)}, unchanged {unchanged}")
    for name in created:
        print(f"  + {name}")
    for name in updated:
        print(f"  ~ {name}")
    for path in removed:
        print(f"  - {path.name}")


if __name__ == "__main__":
    main()

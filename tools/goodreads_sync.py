#!/usr/bin/env python3
"""Sync a public Goodreads shelf into _books/.

Goodreads closed its API, but a public shelf still has an RSS feed. For each
book on the shelf this writes `_books/<slug>.md` if no file carries its
`goodreads_id`, and otherwise refreshes only the fields Goodreads owns (author,
rating, date_read, cover). The title is set on creation and never again, and
the body of a file, which is my notes, is never touched. Running it twice in a
row changes nothing.

Books with no read date are skipped: those were added from memory when the
account was set up, not as they were read, and stay off the site.

    python3 tools/goodreads_sync.py [--dry-run] [--no-covers]

Standard library plus curl. Local use; CI and the site build never run it.
"""

import argparse
import email.utils
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

USER_ID = "163299804"
SHELF = "read"
FEED = "https://www.goodreads.com/review/list_rss/{user}?shelf={shelf}&per_page=200&page={page}"

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "_books"
COVERS = ROOT / "assets" / "images" / "covers"

# Written back on every sync. Anything else in the front matter is left alone.
OWNED = ("author", "rating", "date_read", "cover")


def fetch(url):
    """GET through curl. Python's http.client gets truncated chunked responses
    from the shelf feed most of the time; curl does not."""
    cmd = ["curl", "-fsSL", "--retry", "3", "--max-time", "60", "-A", "ericvoss.com goodreads_sync", url]
    return subprocess.run(cmd, check=True, capture_output=True).stdout


def shelf_items():
    """Every item on the shelf, following pages until one comes back empty."""
    page = 1
    while True:
        root = ET.fromstring(fetch(FEED.format(user=USER_ID, shelf=SHELF, page=page)))
        items = root.findall(".//item")
        if not items:
            return
        yield from items
        page += 1


def text(item, tag):
    return (item.findtext(tag) or "").strip()


def to_book(item):
    read_at = text(item, "user_read_at")
    rating = int(text(item, "user_rating") or 0)
    return {
        "goodreads_id": text(item, "book_id"),
        "title": text(item, "title"),
        "author": text(item, "author_name"),
        "rating": rating or None,
        "date_read": email.utils.parsedate_to_datetime(read_at).date().isoformat() if read_at else None,
        "cover_url": text(item, "book_large_image_url"),
    }


def slugify(title):
    """The title before any subtitle, lowercased, as a filename slug."""
    short = re.split(r"[:(]", title, maxsplit=1)[0]
    return re.sub(r"[^a-z0-9]+", "-", short.lower()).strip("-") or "book"


def split_front_matter(raw):
    m = re.match(r"---\n(.*?\n)---\n?(.*)\Z", raw, re.S)
    return (m.group(1), m.group(2)) if m else ("", raw)


def front_matter_value(fm, key):
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    return json.loads(v) if v.startswith('"') else v


def scalar(value):
    # JSON strings are valid YAML double-quoted scalars; ints and ISO dates
    # are written bare.
    return json.dumps(value, ensure_ascii=False) if isinstance(value, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else str(value)


def set_fields(fm, fields):
    """Replace or append `key: value` lines, dropping keys whose value is None."""
    for key, value in fields.items():
        line = f"{key}: {scalar(value)}\n" if value is not None else ""
        if re.search(rf"^{key}:.*\n", fm, re.M):
            fm = re.sub(rf"^{key}:.*\n", lambda _: line, fm, count=1, flags=re.M)
        else:
            fm += line
    return fm


def existing_by_id():
    found = {}
    for path in sorted(BOOKS.glob("*.md")):
        gid = front_matter_value(split_front_matter(path.read_text())[0], "goodreads_id")
        if gid:
            found[gid] = path
    return found


def download_cover(book, dry_run):
    """Fetch the cover once; return its site path, or None if there isn't one."""
    dest = COVERS / f"{book['goodreads_id']}.jpg"
    site_path = f"/assets/images/covers/{dest.name}"
    if dest.exists():
        return site_path
    if not book["cover_url"] or "nophoto" in book["cover_url"]:
        return None
    if dry_run:
        return site_path
    try:
        data = fetch(book["cover_url"])
    except subprocess.CalledProcessError as err:
        print(f"  cover failed for {book['title']}: {err.stderr.decode().strip()}", file=sys.stderr)
        return None
    COVERS.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return site_path


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    ap.add_argument("--no-covers", action="store_true", help="skip downloading cover images")
    args = ap.parse_args()

    BOOKS.mkdir(exist_ok=True)
    known = existing_by_id()
    taken = {p.stem for p in BOOKS.glob("*.md")}
    created, updated, unchanged, undated = [], [], 0, 0

    for item in shelf_items():
        book = to_book(item)
        if book["date_read"] is None:
            undated += 1
            continue
        cover = None if args.no_covers else download_cover(book, args.dry_run)
        owned = {
            "author": book["author"],
            "rating": book["rating"],
            "date_read": book["date_read"],
            "cover": cover,
        }
        path = known.get(book["goodreads_id"])

        if path is None:
            slug = slugify(book["title"])
            if slug in taken:
                slug = f"{slug}-{book['goodreads_id']}"
            taken.add(slug)
            path = BOOKS / f"{slug}.md"
            fm = f"title: {scalar(book['title'])}\ngoodreads_id: {scalar(book['goodreads_id'])}\n"
            new = "---\n" + set_fields(fm, owned) + "---\n"
            created.append(path.name)
        else:
            raw = path.read_text()
            fm, body = split_front_matter(raw)
            # --no-covers must not strip covers a previous run fetched.
            fields = {k: v for k, v in owned.items() if not (k == "cover" and cover is None)}
            new = "---\n" + set_fields(fm, fields) + "---\n" + body
            if new == raw:
                unchanged += 1
                continue
            updated.append(path.name)

        if not args.dry_run:
            path.write_text(new)

    prefix = "would " if args.dry_run else ""
    print(f"{prefix}create {len(created)}, {prefix}update {len(updated)}, unchanged {unchanged}, skipped {undated} with no read date")
    for name in created:
        print(f"  + {name}")
    for name in updated:
        print(f"  ~ {name}")


if __name__ == "__main__":
    main()

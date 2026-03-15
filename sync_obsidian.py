#!/usr/bin/env python3
"""Sync Obsidian notes with publish: true to Hugo content/posts/.

Usage:
    python3 sync_obsidian.py /path/to/obsidian/vault

Requires Python 3.9+, no external dependencies.
"""

import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HUGO_POSTS = SCRIPT_DIR / "content" / "posts"
STATE_FILE = SCRIPT_DIR / ".sync_state.json"
END_PUBLISH_MARKER = "<!-- end-publish -->"


# ---------------------------------------------------------------------------
# YAML frontmatter parser (minimal, handles the simple Obsidian format)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from a markdown file's text."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 4:].lstrip("\n")
    fm: dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # Handle YAML lists written as [a, b, c]
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
            fm[key] = items
        # Handle booleans
        elif val.lower() in ("true", "false"):
            fm[key] = val.lower() == "true"
        # Strip quotes
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            fm[key] = val[1:-1]
        else:
            fm[key] = val
    return fm, body


def dump_frontmatter(fm: dict) -> str:
    """Serialize a dict to YAML frontmatter string."""
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f'  - "{item}"')
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

def strip_wikilinks(text: str) -> str:
    """Convert [[wikilinks]] and [[link|alias]] to plain text."""
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)  # [[target|alias]] → alias
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)  # [[target]] → target
    return text


def transform_frontmatter(fm: dict) -> dict:
    """Map Obsidian frontmatter fields to Hugo equivalents."""
    hugo: dict = {}

    # Title
    if "title" in fm:
        hugo["title"] = fm["title"]

    # Date: stamped at first sync, not pulled from Obsidian
    # (handled in sync() to preserve existing dates)

    # Categories: domain → categories
    if "domain" in fm:
        val = fm["domain"]
        hugo["categories"] = val if isinstance(val, list) else [val]
    elif "categories" in fm:
        hugo["categories"] = fm["categories"]

    # Tags
    if "tags" in fm:
        hugo["tags"] = fm["tags"] if isinstance(fm["tags"], list) else [fm["tags"]]

    # Author — strip wikilinks
    if "author" in fm:
        author = fm["author"]
        if isinstance(author, str):
            hugo["author"] = strip_wikilinks(author)

    # Source — pass through for commentary posts
    if "source" in fm:
        hugo["source"] = fm["source"]

    # Description / summary
    if "description" in fm:
        hugo["description"] = fm["description"]
    elif "summary" in fm:
        hugo["description"] = fm["summary"]

    # Draft
    if "draft" in fm:
        hugo["draft"] = fm["draft"]

    return hugo


def truncate_at_marker(body: str) -> str:
    """Return content before <!-- end-publish --> marker."""
    idx = body.find(END_PUBLISH_MARKER)
    if idx != -1:
        return body[:idx].rstrip() + "\n"
    return body


def slugify(name: str) -> str:
    """Generate URL slug from filename."""
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def sync(vault_path: Path) -> None:
    if not vault_path.is_dir():
        print(f"Error: {vault_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    new_state: dict = {}
    synced = 0
    skipped = 0

    for md_file in vault_path.rglob("*.md"):
        raw = md_file.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw)

        if not fm.get("publish"):
            continue

        # Transform
        hugo_fm = transform_frontmatter(fm)
        body = truncate_at_marker(body)
        body = strip_wikilinks(body)

        slug = slugify(md_file.stem)
        out_dir = HUGO_POSTS / slug
        out_file = out_dir / "index.md"

        # Date: preserve existing date from Hugo file, or stamp today
        if out_file.exists():
            existing_fm, _ = parse_frontmatter(out_file.read_text(encoding="utf-8"))
            if existing_fm.get("date"):
                hugo_fm["date"] = existing_fm["date"]
            else:
                hugo_fm["date"] = date.today().isoformat()
        else:
            hugo_fm["date"] = date.today().isoformat()

        output = dump_frontmatter(hugo_fm) + "\n" + body

        h = content_hash(output)
        new_state[slug] = h

        if state.get(slug) == h:
            skipped += 1
            continue

        out_dir.mkdir(parents=True, exist_ok=True)
        out_file.write_text(output, encoding="utf-8")
        synced += 1
        print(f"  synced: {slug}")

    save_state(new_state)
    print(f"\nDone. {synced} synced, {skipped} unchanged.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sync_obsidian.py <vault-path>", file=sys.stderr)
        sys.exit(1)
    sync(Path(sys.argv[1]))

#!/usr/bin/env python3
"""The local notebook editor: a small web app over the site's Markdown files.

    python3 tools/notebook/server.py [--port 4100]

It serves one page (index.html, app.js, app.css next to this file) and a JSON
API that reads and writes the same files Jekyll builds from:

    GET  /api/entries?section=reading      list a section
    GET  /api/entry/<section>/<slug>       one entry: front matter, body, mtime
    PUT  /api/entry/<section>/<slug>       save it (refused if the file changed
                                           on disk since it was read)
    POST /api/new                          {section, title} -> a new unpublished entry
    POST /api/sync-books                   run `make sync-books`, return its output

It binds to 127.0.0.1 only. Writes are confined to the two collection
directories and _pages/about.md, slugs are checked against a strict pattern,
and every file is replaced atomically. Requests must name this server as their
Host, and writes must come from its own page, so another website open in the
browser cannot use it. Git stays outside: commit and open a PR as usual.

Standard library only.
"""

import argparse
import json
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

# section -> directory. About is one file, not a collection.
SECTIONS = {
    "reading": ROOT / "_books",
    "writing": ROOT / "_writing",
}
ABOUT = ROOT / "_pages" / "about.md"

SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,120}")
DATED = re.compile(r"(\d{4}-\d{2}-\d{2})-(.+)")
FRONT_MATTER = re.compile(r"---\n(.*?\n)?---\n?(.*)\Z", re.S)

# The page and its two files, plus the site's own stylesheet and images.
STATIC = {"/": "index.html", "/app.js": "app.js", "/app.css": "app.css"}
ASSETS = ROOT / "assets"
SITE_CSS = ASSETS / "css" / "site.scss"


class Refused(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


# --- Files ------------------------------------------------------------------


def slugify(title):
    """Same rule as `make entry`: lowercase, non-alphanumerics become one dash."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def entry_path(section, slug):
    """The file for an entry, or Refused. Nothing outside the allowed files."""
    if section == "about":
        if slug != "about":
            raise Refused(HTTPStatus.NOT_FOUND, "about has one entry, 'about'")
        return ABOUT
    directory = SECTIONS.get(section)
    if directory is None:
        raise Refused(HTTPStatus.NOT_FOUND, f"no section {section!r}")
    if not SLUG.fullmatch(slug):
        raise Refused(HTTPStatus.BAD_REQUEST, f"bad slug {slug!r}")
    path = (directory / f"{slug}.md").resolve()
    if path.parent != directory.resolve():
        raise Refused(HTTPStatus.BAD_REQUEST, f"bad slug {slug!r}")
    return path


def split(raw):
    m = FRONT_MATTER.match(raw)
    return (m.group(1) or "", m.group(2)) if m else ("", raw)


def field(fm, key):
    """A top-level scalar from front matter, unquoted when it is double-quoted."""
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v.startswith('"'):
        try:
            return json.loads(v)
        except ValueError:
            return v.strip('"')
    if v.startswith("'") and v.endswith("'") and len(v) > 1:
        return v[1:-1].replace("''", "'")
    return v


def mtime(path):
    # A string: nanoseconds overflow JavaScript's exact integers.
    return str(path.stat().st_mtime_ns)


def summary(section, path):
    fm, body = split(path.read_text(encoding="utf-8"))
    slug = path.stem
    entry = {
        "section": section,
        "slug": slug,
        "title": field(fm, "title") or slug,
        "published": field(fm, "published") != "false",
        "has_body": bool(body.strip()),
    }
    if section == "reading":
        entry.update(author=field(fm, "author"), rating=field(fm, "rating"), date_read=field(fm, "date_read"))
    m = DATED.fullmatch(slug)
    if m:
        entry["date"] = m.group(1)
    return entry


def list_section(section):
    if section == "about":
        return [summary("about", ABOUT)]
    directory = SECTIONS.get(section)
    if directory is None:
        raise Refused(HTTPStatus.NOT_FOUND, f"no section {section!r}")
    entries = [summary(section, p) for p in directory.glob("*.md")] if directory.is_dir() else []
    if section == "reading":
        # Most recently read first; books with no read date after, by title.
        entries.sort(key=lambda e: e["title"].lower())
        entries.sort(key=lambda e: e.get("date_read") or "", reverse=True)
    else:
        entries.sort(key=lambda e: e["slug"], reverse=True)
    return entries


def read_entry(section, slug):
    path = entry_path(section, slug)
    if not path.is_file():
        raise Refused(HTTPStatus.NOT_FOUND, f"no entry {section}/{slug}")
    fm, body = split(path.read_text(encoding="utf-8"))
    return {
        "section": section,
        "slug": slug,
        "file": str(path.relative_to(ROOT)),
        "front_matter": fm,
        "body": body,
        "mtime": mtime(path),
        "url": url_for(section, slug, fm),
    }


def url_for(section, slug, fm):
    """Where the entry lives on the site, for the `make serve` link."""
    if section == "about":
        return field(fm, "permalink") or "/about/"
    m = DATED.fullmatch(slug)
    name = m.group(2) if m else slug
    return f"/{section}/{name}/"


def write_atomic(path, text):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.stem}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        if path.exists():
            os.chmod(tmp, path.stat().st_mode & 0o777)
        else:
            os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def save_entry(section, slug, data):
    path = entry_path(section, slug)
    if not path.is_file():
        raise Refused(HTTPStatus.NOT_FOUND, f"no entry {section}/{slug}")
    fm, body, base = data.get("front_matter"), data.get("body"), data.get("mtime")
    if not isinstance(fm, str) or not isinstance(body, str):
        raise Refused(HTTPStatus.BAD_REQUEST, "front_matter and body must be strings")
    fm = fm.replace("\r\n", "\n")
    body = body.replace("\r\n", "\n")
    if fm and not fm.endswith("\n"):
        fm += "\n"
    if body.strip() and not body.endswith("\n"):
        body += "\n"
    if re.search(r"^---[ \t]*$", fm, re.M):
        raise Refused(HTTPStatus.BAD_REQUEST, "front matter cannot contain a --- line")
    if not field(fm, "title"):
        raise Refused(HTTPStatus.BAD_REQUEST, "front matter needs a title")
    # Saving over a change made elsewhere (an editor, the Goodreads sync, git)
    # would lose it. The page reloads instead.
    if base != mtime(path):
        raise Refused(HTTPStatus.CONFLICT, "the file changed on disk since it was opened")
    text = f"---\n{fm}---\n{body}"
    if text != path.read_text(encoding="utf-8"):
        write_atomic(path, text)
    return {"mtime": mtime(path)}


def new_entry(data, today=None):
    section, title = data.get("section"), (data.get("title") or "").strip()
    if section not in SECTIONS:
        raise Refused(HTTPStatus.BAD_REQUEST, "section must be reading or writing")
    if not title or "\n" in title:
        raise Refused(HTTPStatus.BAD_REQUEST, "a one-line title is required")
    slug = slugify(title)
    if not slug:
        raise Refused(HTTPStatus.BAD_REQUEST, "that title slugifies to nothing; try another")
    if section == "writing":
        slug = f"{(today or date.today()).isoformat()}-{slug}"
    path = entry_path(section, slug)
    if path.exists():
        raise Refused(HTTPStatus.CONFLICT, f"{path.relative_to(ROOT)} already exists")
    path.parent.mkdir(exist_ok=True)
    fm = f"title: {json.dumps(title, ensure_ascii=False)}\npublished: false\nexcerpt: \"\"\n"
    # "x" mode: never overwrite a file that appeared since the check above.
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(f"---\n{fm}---\n\n")
    return {"section": section, "slug": slug}


def sync_books():
    try:
        run = subprocess.run(["make", "sync-books"], cwd=ROOT, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        raise Refused(HTTPStatus.GATEWAY_TIMEOUT, "the sync took over ten minutes and was stopped")
    return {"ok": run.returncode == 0, "output": (run.stdout + run.stderr).strip()}


def site_css():
    """The site stylesheet as plain CSS. It is SCSS only for its front matter
    and `//` comments, so stripping those is the whole compile step."""
    _, css = split(SITE_CSS.read_text(encoding="utf-8"))
    return re.sub(r"(?<![:\"'])//[^\n]*", "", css)


# --- HTTP -------------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):
    server_version = "notebook"

    def log_message(self, fmt, *args):
        if self.server.verbose:
            super().log_message(fmt, *args)

    # Guard against DNS rebinding (Host) and cross-site writes (Origin).
    def allowed(self, write):
        port = self.server.server_address[1]
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in hosts:
            return False
        if write:
            origin = self.headers.get("Origin")
            if origin is not None and origin not in {f"http://{h}" for h in hosts}:
                return False
            if not (self.headers.get("Content-Type") or "").startswith("application/json"):
                return False
        return True

    def send(self, status, body, content_type):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def json(self, status, obj):
        self.send(status, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def body_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > 5_000_000:
            raise Refused(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "too large")
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            raise Refused(HTTPStatus.BAD_REQUEST, "body is not JSON")
        if not isinstance(data, dict):
            raise Refused(HTTPStatus.BAD_REQUEST, "body must be a JSON object")
        return data

    def route(self, method):
        url = urlsplit(self.path)
        path = unquote(url.path)
        write = method != "GET"
        if not self.allowed(write):
            return self.json(HTTPStatus.FORBIDDEN, {"error": "request refused"})
        try:
            parts = path.strip("/").split("/")
            if method == "GET" and path in STATIC:
                name = STATIC[path]
                ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
                return self.send(HTTPStatus.OK, (HERE / name).read_bytes(), f"{ctype}; charset=utf-8")
            if method == "GET" and path == "/site.css":
                return self.send(HTTPStatus.OK, site_css(), "text/css; charset=utf-8")
            if method == "GET" and path.startswith("/assets/"):
                return self.asset(path)
            if path == "/api/entries" and method == "GET":
                section = parse_qs(url.query).get("section", ["reading"])[0]
                return self.json(HTTPStatus.OK, list_section(section))
            if parts[:2] == ["api", "entry"] and len(parts) == 4:
                if method == "GET":
                    return self.json(HTTPStatus.OK, read_entry(parts[2], parts[3]))
                if method == "PUT":
                    return self.json(HTTPStatus.OK, save_entry(parts[2], parts[3], self.body_json()))
            if path == "/api/new" and method == "POST":
                return self.json(HTTPStatus.CREATED, new_entry(self.body_json()))
            if path == "/api/sync-books" and method == "POST":
                self.body_json()
                return self.json(HTTPStatus.OK, sync_books())
            raise Refused(HTTPStatus.NOT_FOUND, "not found")
        except Refused as err:
            return self.json(err.status, {"error": str(err)})

    def asset(self, path):
        """Covers and images from the site's assets/, read-only."""
        target = (ROOT / path.lstrip("/")).resolve()
        if ASSETS.resolve() not in target.parents or not target.is_file():
            raise Refused(HTTPStatus.NOT_FOUND, "not found")
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        return self.send(HTTPStatus.OK, target.read_bytes(), ctype)

    def do_GET(self):
        self.route("GET")

    def do_PUT(self):
        self.route("PUT")

    def do_POST(self):
        self.route("POST")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=4100)
    ap.add_argument("--verbose", action="store_true", help="log every request")
    args = ap.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.verbose = args.verbose
    print(f"notebook at http://localhost:{args.port}/  (ctrl-c to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    sys.exit(main())

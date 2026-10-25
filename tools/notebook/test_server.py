"""Tests for the notebook server: paths, saves, new entries, and the request
guards. Each test points the server at a scratch copy of the content dirs.

    python3 -m unittest discover tools/notebook
"""

import http.client
import json
import shutil
import sys
import tempfile
import threading
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import server  # noqa: E402


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.saved = (server.ROOT, dict(server.SECTIONS), server.ABOUT)
        server.ROOT = self.tmp
        server.SECTIONS.update({k: self.tmp / d for k, d in
                                (("reading", "_books"), ("writing", "_writing"))})
        server.ABOUT = self.tmp / "_pages" / "about.md"
        for d in ("_books", "_writing", "_pages"):
            (self.tmp / d).mkdir()
        server.ABOUT.write_text('---\ntitle: About\npermalink: /about/\n---\n\nHello.\n')
        (self.tmp / "_books" / "dune.md").write_text('---\ntitle: "Dune"\nauthor: "Frank Herbert"\ndate_read: 2024-05-01\n---\n')

    def tearDown(self):
        server.ROOT, sections, server.ABOUT = self.saved
        server.SECTIONS.clear()
        server.SECTIONS.update(sections)
        shutil.rmtree(self.tmp)


class Paths(Scratch):
    def test_rejects_escapes(self):
        for slug in ("../about", "..", "a/b", "Dune", "", ".hidden", "dune.md", "a\x00b"):
            with self.assertRaises(server.Refused, msg=slug):
                server.entry_path("reading", slug)

    def test_rejects_unknown_section(self):
        with self.assertRaises(server.Refused):
            server.entry_path("_pages", "about")
        with self.assertRaises(server.Refused):
            server.entry_path("about", "redirect-blog")

    def test_allows_the_known_files(self):
        self.assertEqual(server.entry_path("reading", "dune"), (self.tmp / "_books" / "dune.md").resolve())
        self.assertEqual(server.entry_path("about", "about"), server.ABOUT)


class Saving(Scratch):
    def test_round_trip_keeps_the_file(self):
        before = (self.tmp / "_books" / "dune.md").read_text()
        e = server.read_entry("reading", "dune")
        server.save_entry("reading", "dune", e)
        self.assertEqual((self.tmp / "_books" / "dune.md").read_text(), before)

    def test_save_writes_body_and_front_matter(self):
        e = server.read_entry("reading", "dune")
        e["body"] = "\nSpice.\n"
        e["front_matter"] += "published: false\n"
        res = server.save_entry("reading", "dune", e)
        self.assertNotEqual(res["mtime"], e["mtime"])
        text = (self.tmp / "_books" / "dune.md").read_text()
        self.assertTrue(text.endswith("published: false\n---\n\nSpice.\n"))
        self.assertEqual(server.list_section("reading")[0]["published"], False)

    def test_refuses_a_stale_save(self):
        e = server.read_entry("reading", "dune")
        path = self.tmp / "_books" / "dune.md"
        path.write_text(path.read_text() + "Changed elsewhere.\n")
        with self.assertRaises(server.Refused) as ctx:
            server.save_entry("reading", "dune", e)
        self.assertEqual(ctx.exception.status, 409)
        self.assertIn("Changed elsewhere.", path.read_text())

    def test_refuses_broken_front_matter(self):
        e = server.read_entry("reading", "dune")
        for fm in ("title: x\n---\nfoo: y\n", "author: nobody\n"):
            with self.assertRaises(server.Refused):
                server.save_entry("reading", "dune", dict(e, front_matter=fm))

    def test_no_temp_files_left(self):
        e = server.read_entry("reading", "dune")
        server.save_entry("reading", "dune", dict(e, body="x\n"))
        self.assertEqual(sorted(p.name for p in (self.tmp / "_books").iterdir()), ["dune.md"])


class NewEntries(Scratch):
    def test_writing_gets_a_date(self):
        res = server.new_entry({"section": "writing", "title": "On Notebooks!"}, today=date(2026, 10, 25))
        self.assertEqual(res["slug"], "2026-10-25-on-notebooks")
        text = (self.tmp / "_writing" / "2026-10-25-on-notebooks.md").read_text()
        self.assertEqual(text, '---\ntitle: "On Notebooks!"\npublished: false\nexcerpt: ""\n---\n\n')
        self.assertEqual(server.read_entry("writing", res["slug"])["url"], "/writing/on-notebooks/")

    def test_refuses_duplicates_and_junk(self):
        with self.assertRaises(server.Refused):
            server.new_entry({"section": "reading", "title": "Dune"})
        for data in ({"section": "about", "title": "x"}, {"section": "projects", "title": "x"}, {"section": "writing", "title": "!!!"},
                     {"section": "writing", "title": ""}, {"section": "writing", "title": "a\nb"}):
            with self.assertRaises(server.Refused, msg=data):
                server.new_entry(data)


class Requests(Scratch):
    def setUp(self):
        super().setUp()
        self.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.httpd.verbose = False
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        super().tearDown()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        h = {"Host": f"localhost:{self.port}"}
        if body is not None:
            h["Content-Type"] = "application/json"
        h.update(headers or {})
        conn.request(method, path, json.dumps(body) if body is not None else None, h)
        res = conn.getresponse()
        return res.status, res.read()

    def test_lists_and_reads(self):
        status, data = self.request("GET", "/api/entries?section=reading")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)[0]["title"], "Dune")

    def test_traversal_over_http(self):
        for path in ("/api/entry/reading/..%2F_pages%2Fabout", "/api/entry/reading/%2e%2e", "/assets/../_books/dune.md"):
            status, _ = self.request("GET", path)
            self.assertIn(status, (400, 404), path)

    def test_foreign_host_refused(self):
        status, _ = self.request("GET", "/api/entries", headers={"Host": "evil.example:80"})
        self.assertEqual(status, 403)

    def test_cross_site_write_refused(self):
        status, _ = self.request("POST", "/api/new", {"section": "writing", "title": "x"},
                                 headers={"Origin": "https://evil.example"})
        self.assertEqual(status, 403)
        status, _ = self.request("POST", "/api/new", headers={"Content-Type": "text/plain"}, body=None)
        self.assertEqual(status, 403)

    def test_save_over_http(self):
        _, data = self.request("GET", "/api/entry/reading/dune")
        e = json.loads(data)
        status, _ = self.request("PUT", "/api/entry/reading/dune", dict(e, body="Notes.\n"),
                                 headers={"Origin": f"http://localhost:{self.port}"})
        self.assertEqual(status, 200)
        self.assertTrue((self.tmp / "_books" / "dune.md").read_text().endswith("---\nNotes.\n"))


class SiteCss(unittest.TestCase):
    def test_strips_scss_comments_only(self):
        css = server.site_css()
        self.assertNotIn("// ", css)
        self.assertIn("--lh: 1.75rem;", css)
        self.assertEqual(css.count("{"), css.count("}"))


if __name__ == "__main__":
    unittest.main()

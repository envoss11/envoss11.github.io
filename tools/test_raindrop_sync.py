"""Tests for raindrop_sync's offline parts: run with `make test-tools`."""

import unittest
from pathlib import Path

import raindrop_sync as rs


def item(**kw):
    base = {"_id": 1, "title": "An Article", "link": "https://example.com/a",
            "domain": "example.com", "created": "2026-10-20T12:00:00.000Z",
            "note": "", "collection": {"$id": 10}}
    base.update(kw)
    return base


class Exclusion(unittest.TestCase):
    def test_queue_and_its_children_are_left_out(self):
        cols = {
            1: {"title": "Reading Queue", "parent": None},
            2: {"title": "Longreads", "parent": 1},
            3: {"title": "Philosophy", "parent": None},
            4: {"title": "queue-later", "parent": 3},
        }
        self.assertEqual(rs.excluded_collections(cols), {1, 2, 4})

    def test_collection_id_reads_either_field(self):
        self.assertEqual(rs.collection_id({"collection": {"$id": 7}}), 7)
        self.assertEqual(rs.collection_id({"collectionId": -1}), -1)


class Quoting(unittest.TestCase):
    def test_markup_is_escaped(self):
        q = rs.quote_text("a *b* <i>c</i> {{ d }} [e](f)")
        self.assertEqual(q, r"> a \*b\* &lt;i&gt;c&lt;/i&gt; \{\{ d \}\} \[e\](f)")

    def test_line_start_markers_are_escaped(self):
        self.assertEqual(rs.quote_text("# not a heading"), r"> \# not a heading")
        self.assertEqual(rs.quote_text("1. not a list"), r"> 1\. not a list")

    def test_paragraphs_stay_one_paragraph(self):
        self.assertEqual(rs.quote_text("one\n\ntwo"), "> one  \n> two")

    def test_blank_text_quotes_nothing(self):
        self.assertEqual(rs.quote_text("  \n "), "")


class Render(unittest.TestCase):
    def test_front_matter_and_body(self):
        hls = [
            {"text": "Second", "note": "", "created": "2026-10-21"},
            {"text": "First", "note": "Why it matters.", "created": "2026-10-20"},
        ]
        out = rs.render(item(note="My take."), hls)
        self.assertEqual(out, (
            "---\n"
            'title: "An Article"\n'
            'source: "https://example.com/a"\n'
            'site: "example.com"\n'
            "date_read: 2026-10-20\n"
            "raindrop_id: 1\n"
            "---\n"
            "\nMy take.\n\n> First\n\nWhy it matters.\n\n> Second\n"
        ))

    def test_no_notes_means_empty_body(self):
        self.assertTrue(rs.render(item(), []).endswith("raindrop_id: 1\n---\n"))

    def test_untitled_falls_back_to_link(self):
        self.assertIn('title: "https://example.com/a"', rs.render(item(title=""), []))


class Links(unittest.TestCase):
    def test_tracking_parameters_are_dropped(self):
        self.assertEqual(rs.clean_link("https://a.com/x?utm_source=tldr&id=3&UTM_medium=e#s"), "https://a.com/x?id=3#s")
        self.assertEqual(rs.clean_link("https://a.com/x?utm_source=tldr"), "https://a.com/x")
        self.assertEqual(rs.clean_link("https://a.com/x?a=1&utm_source=t&b=2"), "https://a.com/x?a=1&b=2")
        self.assertEqual(rs.clean_link("https://a.com/x/?utm_source=s&utm_medium=e"), "https://a.com/x/")
        self.assertEqual(rs.clean_link("https://a.com/b.html#s.md?utm_source=t"), "https://a.com/b.html#s.md")

    def test_other_trackers_are_dropped(self):
        self.assertEqual(rs.clean_link("https://a.com/p?utm_source=x&_bhlid=abc&gift=1"), "https://a.com/p?gift=1")

    def test_site_comes_from_the_cleaned_link(self):
        url = "https://tracking.tldrnewsletter.com/CL0/https:%2F%2Fwww.b.org%2Fp/1/x"
        self.assertIn('site: "b.org"', rs.render(item(link=url, domain="tracking.tldrnewsletter.com"), []))

    def test_click_trackers_are_unwrapped(self):
        url = ("https://tracking.tldrnewsletter.com/CL0/https:%2F%2Fthinkingmachines.ai%2Fblog%2Flora%2F"
               "%3Futm_source=tldrai/1/0100019-abc/dXerf=424")
        self.assertEqual(rs.clean_link(url), "https://thinkingmachines.ai/blog/lora/")


class Plan(unittest.TestCase):
    def test_known_files_keep_their_slug_and_new_ones_avoid_collisions(self):
        old = rs.ARTICLES / "old-name.md"
        pairs = rs.plan(
            [item(_id=1, title="Renamed"), item(_id=2, title="Taken"), item(_id=3, title="Fresh")],
            known={1: old}, taken={"old-name", "taken"},
        )
        self.assertEqual([p.name for p, _ in pairs], ["old-name.md", "taken-2.md", "fresh.md"])

    def test_slugify(self):
        self.assertEqual(rs.slugify("Why Cities Matter: A Note"), "why-cities-matter-a-note")
        self.assertEqual(rs.slugify("!!!"), "article")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "export_anki_decks.py"

spec = importlib.util.spec_from_file_location("export_anki_decks", SCRIPT)
export_anki_decks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_anki_decks)


def parse_fallback(md_text: str) -> str:
    """Run parse_markdown_to_html with the `markdown` module forced missing."""
    with mock.patch.dict(sys.modules, {"markdown": None}):
        return export_anki_decks.parse_markdown_to_html(md_text)


class FallbackEmphasisTest(unittest.TestCase):
    def test_snake_case_stays_intact(self):
        html = parse_fallback("call snake_case_name here")

        self.assertIn("snake_case_name", html)
        self.assertNotIn("<i>", html)

    def test_underscore_italic_still_works(self):
        html = parse_fallback("say _word_ now")

        self.assertIn("<i>word</i>", html)

    def test_asterisk_italic_still_works(self):
        html = parse_fallback("say *word* now")

        self.assertIn("<i>word</i>", html)

    def test_bold_still_works(self):
        html = parse_fallback("say **bold** now")

        self.assertIn("<b>bold</b>", html)

    def test_spaced_asterisks_stay_plain(self):
        html = parse_fallback("compute a * b * c")

        self.assertIn("a * b * c", html)
        self.assertNotIn("<i>", html)

    def test_inline_code_is_protected(self):
        html = parse_fallback("use `__init__` and `_x_`")

        self.assertIn("<code>__init__</code>", html)
        self.assertIn("<code>_x_</code>", html)
        self.assertNotIn("<i>", html)
        self.assertNotIn("<b>", html)

    def test_fenced_code_block_is_protected(self):
        html = parse_fallback("before\n```\nfoo_bar_baz\n```\nafter")

        self.assertIn("<pre><code>", html)
        self.assertIn("foo_bar_baz", html)
        self.assertNotIn("<i>", html)


class ProcessFileTest(unittest.TestCase):
    def test_process_file_returns_front_back_pairs(self):
        content = (
            "Deck preamble.\n"
            "### Card 1\n"
            "**Front:** What is TCP?\n"
            "**Back:** A reliable transport protocol.\n"
            "### Card 2\n"
            "**Front:** A card with an empty back\n"
            "**Back:**\n"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            card_file = Path(tmp_dir) / "sample-deck.md"
            card_file.write_text(content, encoding="utf-8")

            deck_name, cards = export_anki_decks.process_file(str(card_file), True)

        self.assertEqual(deck_name, "sample-deck")
        self.assertEqual(
            cards,
            [
                ("What is TCP?", "A reliable transport protocol."),
                ("A card with an empty back", ""),
            ],
        )


class TagDeterminismTest(unittest.TestCase):
    def test_tag_order_is_stable_across_runs(self):
        first = " ".join(sorted(set(export_anki_decks.deck_tags("hld-concepts"))))
        second = " ".join(sorted(set(export_anki_decks.deck_tags("hld-concepts"))))

        self.assertEqual(first, second)
        self.assertEqual(first, " ".join(sorted(first.split())))
        self.assertIn("hld", first.split())
        self.assertIn("system-design", first.split())


if __name__ == "__main__":
    unittest.main()

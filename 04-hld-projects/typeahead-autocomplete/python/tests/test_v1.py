import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from trie_v1 import Trie  # noqa: E402


class TestV1Trie(unittest.TestCase):
    def test_insert_and_autocomplete(self):
        t = Trie()
        t.insert("apple")
        t.insert("app")
        t.insert("apricot")
        t.insert("banana")

        res = t.autocomplete("ap")
        self.assertEqual(res, ["app", "apple", "apricot"])

    def test_no_match(self):
        t = Trie()
        t.insert("apple")
        res = t.autocomplete("b")
        self.assertEqual(res, [])

    def test_exact_match(self):
        t = Trie()
        t.insert("apple")
        res = t.autocomplete("apple")
        self.assertEqual(res, ["apple"])

    def test_limit(self):
        t = Trie()
        for i in range(15):
            t.insert(f"app{i:02d}")
        res = t.autocomplete("app")
        self.assertEqual(len(res), 10)

    def test_empty_prefix(self):
        t = Trie()
        t.insert("a")
        t.insert("b")
        res = t.autocomplete("")
        self.assertEqual(res, ["a", "b"])

    def test_case_sensitive(self):
        t = Trie()
        t.insert("Apple")
        t.insert("apple")
        res = t.autocomplete("A")
        self.assertEqual(res, ["Apple"])


if __name__ == '__main__':
    unittest.main()

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'v2-scaled')))
from trie_v2 import Trie  # noqa: E402


class TestV2Trie(unittest.TestCase):
    def test_insert_and_autocomplete_top_k(self):
        t = Trie(k=2)
        t.insert("apple", 10)
        t.insert("app", 20)
        t.insert("apricot", 5)

        res = t.autocomplete("ap")
        self.assertEqual(res, ["app", "apple"])

    def test_update_frequency(self):
        t = Trie(k=2)
        t.insert("apple", 10)
        t.insert("app", 20)
        t.insert("apricot", 5)

        # update apricot frequency to be highest
        t.insert("apricot", 30)

        res = t.autocomplete("ap")
        self.assertEqual(res, ["apricot", "app"])

    def test_no_match(self):
        t = Trie()
        t.insert("apple", 10)
        res = t.autocomplete("b")
        self.assertEqual(res, [])

    def test_exact_match(self):
        t = Trie()
        t.insert("apple", 10)
        res = t.autocomplete("apple")
        self.assertEqual(res, ["apple"])

    def test_decay(self):
        t = Trie(k=2)
        t.insert("apple", 10)
        t.insert("app", 20)

        t.decay(0.5)

        node = t.root.children['a'].children['p']
        self.assertEqual(node.top_k, [("app", 10), ("apple", 5)])

    def test_decay_drop(self):
        t = Trie(k=2)
        t.insert("apple", 1)
        t.decay(0.5)  # 1 * 0.5 = 0.5 -> 0, should drop
        res = t.autocomplete("a")
        self.assertEqual(res, [])


if __name__ == '__main__':
    unittest.main()

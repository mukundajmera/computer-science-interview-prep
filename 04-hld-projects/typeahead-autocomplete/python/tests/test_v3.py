import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'v3-distributed')))
from trie_v3 import ShardedTrieManager  # noqa: E402


class TestV3Trie(unittest.TestCase):
    def test_sharding_distribution(self):
        manager = ShardedTrieManager(num_shards=3)

        manager.insert("apple", 10)  # Shard 0 (a-i)
        manager.insert("mango", 20)  # Shard 1 (j-r)
        manager.insert("zebra", 5)   # Shard 2 (s-z)

        # Verify they went to correct shards
        self.assertEqual(manager.autocomplete("a"), ["apple"])
        self.assertEqual(manager.autocomplete("m"), ["mango"])
        self.assertEqual(manager.autocomplete("z"), ["zebra"])

    def test_snapshot_swap(self):
        manager = ShardedTrieManager(num_shards=3)
        manager.insert("apple", 10)

        self.assertEqual(manager.autocomplete("a"), ["apple"])

        # Build new snapshot
        manager.build_snapshot([("apricot", 20), ("app", 15)])

        # Before swap, still old data
        self.assertEqual(manager.autocomplete("a"), ["apple"])

        # Swap
        manager.swap_snapshot()

        # After swap, new data
        self.assertEqual(manager.autocomplete("a"), ["apricot", "app"])

    def test_empty_prefix(self):
        manager = ShardedTrieManager(num_shards=3)
        manager.insert("apple", 10)
        # different shard for empty prefix won't show
        manager.insert("mango", 20)
        # empty prefix hashes to shard 0
        self.assertEqual(manager.autocomplete(""), ["apple"])

    def test_no_match(self):
        manager = ShardedTrieManager(num_shards=3)
        manager.insert("apple", 10)
        res = manager.autocomplete("b")
        self.assertEqual(res, [])

    def test_limit(self):
        manager = ShardedTrieManager(num_shards=3, k=2)
        manager.insert("apple", 10)
        manager.insert("app", 20)
        manager.insert("apricot", 30)

        res = manager.autocomplete("ap")
        self.assertEqual(res, ["apricot", "app"])

    def test_build_snapshot_multiple(self):
        manager = ShardedTrieManager(num_shards=3)
        data = [("apple", 10), ("mango", 20), ("zebra", 30), ("app", 5)]
        manager.build_snapshot(data)
        manager.swap_snapshot()

        self.assertEqual(manager.autocomplete("a"), ["apple", "app"])
        self.assertEqual(manager.autocomplete("m"), ["mango"])
        self.assertEqual(manager.autocomplete("z"), ["zebra"])


if __name__ == '__main__':
    unittest.main()

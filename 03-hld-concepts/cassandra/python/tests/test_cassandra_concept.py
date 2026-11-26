"""Unit tests for Cassandra concept skeleton."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-simple"))

from simple_cassandra_table import SimpleCassandraTable


class TestSimpleCassandraTable(unittest.TestCase):
    def test_upsert_and_get(self) -> None:
        table = SimpleCassandraTable()
        table.upsert("user-1", 1001, {"event": "login"})
        row = table.get("user-1", 1001)
        self.assertIsNotNone(row)
        self.assertEqual("login", row.columns["event"])

    def test_partition_ordering(self) -> None:
        table = SimpleCassandraTable()
        table.upsert("user-1", 3, {"event": "c"})
        table.upsert("user-1", 1, {"event": "a"})
        table.upsert("user-1", 2, {"event": "b"})
        rows = table.query_partition("user-1")
        self.assertEqual([1, 2, 3], [row.clustering_key for row in rows])

    def test_range_query(self) -> None:
        table = SimpleCassandraTable()
        table.upsert("order-1", 10, {"status": "created"})
        table.upsert("order-1", 20, {"status": "packed"})
        table.upsert("order-1", 30, {"status": "shipped"})
        rows = table.query_range("order-1", 15, 30)
        self.assertEqual(2, len(rows))

    def test_invalid_consistency(self) -> None:
        table = SimpleCassandraTable()
        with self.assertRaises(ValueError):
            table.set_read_consistency("LINEARIZABLE")


if __name__ == "__main__":
    unittest.main()

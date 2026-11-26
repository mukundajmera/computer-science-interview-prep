"""Unit tests for DynamoDB concept skeleton."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-simple"))

from simple_dynamo_table import SimpleDynamoTable


class TestSimpleDynamoTable(unittest.TestCase):
    def test_put_and_get(self) -> None:
        table = SimpleDynamoTable()
        table.put_item("chat-1", "0001", {"message": "hello", "user": "u1"})
        item = table.get_item("chat-1", "0001")
        self.assertIsNotNone(item)
        self.assertEqual("hello", item.attributes["message"])

    def test_range_query(self) -> None:
        table = SimpleDynamoTable()
        table.put_item("chat-1", "0001", {"message": "a"})
        table.put_item("chat-1", "0002", {"message": "b"})
        table.put_item("chat-1", "0003", {"message": "c"})
        items = table.query_range("chat-1", "0002", "0003")
        self.assertEqual(["0002", "0003"], [item.sort_key for item in items])

    def test_gsi_query(self) -> None:
        table = SimpleDynamoTable()
        table.define_gsi("user-index", partition_attr="user", sort_attr="ts")
        table.put_item("chat-1", "0001", {"user": "u1", "ts": "2026-01-01T10:00:00Z"})
        table.put_item("chat-2", "0001", {"user": "u1", "ts": "2026-01-01T11:00:00Z"})
        table.put_item("chat-2", "0002", {"user": "u2", "ts": "2026-01-01T12:00:00Z"})
        results = table.query_gsi("user-index", "u1")
        self.assertEqual(2, len(results))

    def test_scan_pagination(self) -> None:
        table = SimpleDynamoTable()
        table.put_item("chat-1", "0001", {"x": 1})
        table.put_item("chat-1", "0002", {"x": 2})
        table.put_item("chat-1", "0003", {"x": 3})
        page = table.scan(limit=2, offset=1)
        self.assertEqual(2, len(page))


if __name__ == "__main__":
    unittest.main()

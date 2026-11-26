import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from store_selector import Workload, choose_store


class TestStoreSelector(unittest.TestCase):
    def test_choose_sql_for_transactions(self):
        self.assertEqual(choose_store(Workload(True, False, False, False)), "SQL")

    def test_choose_sql_for_join_heavy_queries(self):
        self.assertEqual(choose_store(Workload(False, False, True, False)), "SQL")

    def test_choose_nosql_for_scale(self):
        self.assertEqual(choose_store(Workload(False, False, False, True)), "NoSQL")

    def test_choose_nosql_for_flexible_schema(self):
        self.assertEqual(choose_store(Workload(False, True, False, False)), "NoSQL")


if __name__ == '__main__':
    unittest.main()

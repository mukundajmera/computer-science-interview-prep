import sys, os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-advanced'))
from partitioning import PostgresPartitioner

class TestPartitioner(unittest.TestCase):
    def test_get_partition(self):
        p = PostgresPartitioner()
        self.assertEqual(p.get_partition("2023-10-15"), "part_2023_10")

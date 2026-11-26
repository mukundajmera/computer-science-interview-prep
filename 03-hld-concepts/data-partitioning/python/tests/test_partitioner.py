import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from partitioner import DataPartitioner


class TestPartitioner(unittest.TestCase):
    def test_hash_partition_within_bounds(self):
        partitioner = DataPartitioner(8)
        self.assertEqual(6, partitioner.hash_partition("user-123"))
        self.assertEqual(partitioner.hash_partition("user-123"), partitioner.hash_partition("user-123"))

    def test_range_partition_maps_expected_range(self):
        partitioner = DataPartitioner(3)
        partition = partitioner.range_partition(350, [(0, 99), (100, 399), (400, 999)])
        self.assertEqual(partition, 1)

    def test_range_partition_out_of_bounds_raises(self):
        partitioner = DataPartitioner(3)
        with self.assertRaises(ValueError):
            partitioner.range_partition(1200, [(0, 99), (100, 399), (400, 999)])

    def test_range_partition_rejects_overlapping_ranges(self):
        partitioner = DataPartitioner(3)
        with self.assertRaises(ValueError):
            partitioner.range_partition(50, [(0, 99), (50, 199)])


if __name__ == '__main__':
    unittest.main()

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from cap_mode import CapDecision, CapSystem


class TestCapSystem(unittest.TestCase):
    def test_cp_rejects_reads_during_partition(self):
        system = CapSystem(CapDecision("CP"))
        self.assertEqual(system.read_during_partition(), "REJECTED_FOR_CONSISTENCY")

    def test_ap_allows_stale_reads_during_partition(self):
        system = CapSystem(CapDecision("AP"))
        self.assertEqual(system.read_during_partition(), "STALE_OK")

    def test_invalid_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            CapDecision("CP-AP")


if __name__ == '__main__':
    unittest.main()

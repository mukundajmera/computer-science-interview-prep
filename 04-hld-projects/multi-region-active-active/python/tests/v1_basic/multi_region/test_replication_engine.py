import time
import unittest
from v1_basic.multi_region.region_database import RegionDatabase
from v1_basic.multi_region.hybrid_logical_clock import HybridLogicalClock
from v1_basic.multi_region.record import Record

"""
Simplifications in this simulator:
- Transport: In-memory method calls and local queues replace network communication, eliminating network partitions (unless simulated via boolean flags) and RPC overhead.
- Clock: Relies on the local machine's system time (time.time()) for Hybrid Logical Clocks, assuming no drift across simulated regions.
- Security: Authentication, authorization, and data encryption are omitted for simplicity.
- Consistency: Immediate local updates are provided, but replication relies on explicit `.replicate_to()` calls to simulate eventual consistency across regions.
"""

class TestReplicationEngine(unittest.TestCase):

    def test_basic_replication(self):
        us = RegionDatabase("US", ["EU", "APAC"])
        eu = RegionDatabase("EU", ["US", "APAC"])
        
        us.write("user1", "data-from-us")
        
        self.assertIsNone(eu.read("user1"))
        
        us.replicate_to(eu)
        
        record = eu.read("user1")
        self.assertIsNotNone(record)
        self.assertEqual(record.data, "data-from-us")

    def test_conflict_resolution_lww(self):
        us = RegionDatabase("US", ["EU"])
        eu = RegionDatabase("EU", ["US"])
        
        us.set_partitioned(True)
        eu.set_partitioned(True)
        
        us.write("user1", "data-from-us")
        time.sleep(0.01) # ensure physical time advances
        eu.write("user1", "data-from-eu")
        
        us.set_partitioned(False)
        eu.set_partitioned(False)
        
        us.replicate_to(eu)
        eu.replicate_to(us)
        
        self.assertEqual(us.read("user1").data, "data-from-eu")
        self.assertEqual(eu.read("user1").data, "data-from-eu")

    def test_conflict_resolution_tiebreaker(self):
        us = RegionDatabase("US", ["EU"])
        eu = RegionDatabase("EU", ["US"])
        
        clock = HybridLogicalClock(1000, 0)
        record_us = Record("user1", "data-us", clock, "US")
        record_eu = Record("user1", "data-eu", clock, "EU")
        
        us.apply_replication(record_us)
        eu.apply_replication(record_eu)
        
        us.apply_replication(record_eu)
        eu.apply_replication(record_us)
        
        self.assertEqual(us.read("user1").data, "data-us")
        self.assertEqual(eu.read("user1").data, "data-us")

    def test_network_partition_split_brain(self):
        us = RegionDatabase("US", ["EU"])
        eu = RegionDatabase("EU", ["US"])
        
        # Simulate network partition (split-brain) as mentioned in DESIGN.md
        us.set_partitioned(True)
        eu.set_partitioned(True)
        
        us.write("shared-doc", "content-from-us")
        time.sleep(0.01)
        
        # Replication attempts during partition should not affect peers
        us.replicate_to(eu)
        self.assertIsNone(eu.read("shared-doc")) # EU should not see US writes yet
        
        eu.write("shared-doc", "content-from-eu-updated")
        
        # Heal partition
        us.set_partitioned(False)
        eu.set_partitioned(False)
        
        # Anti-entropy / background replication simulation
        us.replicate_to(eu)
        eu.replicate_to(us)
        
        # EU's write happened later, LWW with HLC resolves conflict
        self.assertEqual(us.read("shared-doc").data, "content-from-eu-updated")
        self.assertEqual(eu.read("shared-doc").data, "content-from-eu-updated")

if __name__ == '__main__':
    unittest.main()

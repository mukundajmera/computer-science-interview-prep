"""Unit Tests for Contention Control Implementations."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))

from optimistic_reservation_service import OptimisticReservationService
from contention_policy_coordinator import ContentionPolicyCoordinator, ContentionPolicy
from distributed_contention_coordinator import DistributedContentionCoordinator, IdempotencyStore

class TestContentionControl(unittest.TestCase):
    
    # v1-simple
    def test_optimistic_reservation_success(self):
        service = OptimisticReservationService()
        service.upsert("seat-A", 1)
        self.assertTrue(service.reserve("seat-A", 1, 0))
    
    def test_optimistic_reservation_version_mismatch(self):
        service = OptimisticReservationService()
        service.upsert("seat-A", 1)
        self.assertFalse(service.reserve("seat-A", 1, 1))

    # v2-realistic
    def test_policy_coordinator_optimistic(self):
        coord = ContentionPolicyCoordinator()
        coord.set_policy("res-1", ContentionPolicy.OPTIMISTIC)
        res = coord.execute("res-1", lambda: "ok")
        self.assertEqual(res, "ok")
        
    def test_policy_coordinator_serial_queue(self):
        coord = ContentionPolicyCoordinator()
        coord.set_policy("res-2", ContentionPolicy.SERIAL_QUEUE)
        res = coord.execute("res-2", lambda: "serial_ok")
        self.assertEqual(res, "serial_ok")

    # v3-production
    def test_distributed_coordinator_execute_once(self):
        store = IdempotencyStore()
        coord = DistributedContentionCoordinator()
        
        counter = {"val": 0}
        def action():
            counter["val"] += 1
            return "done"
            
        res1 = coord.execute_once("key-1", action, store)
        res2 = coord.execute_once("key-1", action, store)
        
        self.assertEqual(res1, "done")
        self.assertEqual(res2, "done")
        self.assertEqual(counter["val"], 1)
        
    def test_distributed_coordinator_multiple_keys(self):
        store = IdempotencyStore()
        coord = DistributedContentionCoordinator()
        
        res1 = coord.execute_once("key-A", lambda: "A", store)
        res2 = coord.execute_once("key-B", lambda: "B", store)
        
        self.assertEqual(res1, "A")
        self.assertEqual(res2, "B")

if __name__ == '__main__':
    unittest.main()

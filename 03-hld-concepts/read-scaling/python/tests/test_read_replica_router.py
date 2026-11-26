import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from read_replica_router import ReadReplicaRouter

class TestReadReplicaRouter(unittest.TestCase):

    def test_writes_always_go_to_primary(self):
        router = ReadReplicaRouter("primary-db", ["replica-1", "replica-2"], max_lag_ms=5000)
        self.assertEqual(router.route_write("user1"), "primary-db")
        self.assertEqual(router.route_write("user2"), "primary-db")

    def test_reads_load_balance_across_healthy_replicas(self):
        router = ReadReplicaRouter("primary-db", ["replica-1", "replica-2"], max_lag_ms=5000)
        routed = set()
        for _ in range(10):
            routed.add(router.route_read("user-read-only"))

        self.assertIn("replica-1", routed)
        self.assertIn("replica-2", routed)
        self.assertNotIn("primary-db", routed)

    def test_eviction_on_unhealthy_replica(self):
        router = ReadReplicaRouter("primary-db", ["replica-1", "replica-2"], max_lag_ms=5000)
        router.update_replica_health("replica-1", False)

        routed = set()
        for _ in range(10):
            routed.add(router.route_read("user-read-only"))

        self.assertIn("replica-2", routed)
        self.assertNotIn("replica-1", routed)

        # All unhealthy -> fallback to primary
        router.update_replica_health("replica-2", False)
        self.assertEqual(router.route_read("user-read-only"), "primary-db")

    def test_eviction_on_high_lag(self):
        router = ReadReplicaRouter("primary-db", ["replica-1", "replica-2"], max_lag_ms=5000)
        router.update_replica_lag("replica-1", 6000)

        routed = set()
        for _ in range(10):
            routed.add(router.route_read("user-read-only"))

        self.assertIn("replica-2", routed)
        self.assertNotIn("replica-1", routed)

        # Both lag too much -> fallback to primary
        router.update_replica_lag("replica-2", 7000)
        self.assertEqual(router.route_read("user-read-only"), "primary-db")

    def test_read_your_own_writes(self):
        router = ReadReplicaRouter("primary-db", ["replica-1", "replica-2"], max_lag_ms=5000)

        router.set_mock_time(1000)
        router.route_write("user1") # user1 writes at t=1000

        router.set_mock_time(1500) # elapsed = 500ms

        # replica-1 is too stale (lag 600 >= elapsed 500)
        router.update_replica_lag("replica-1", 600)
        # replica-2 is fresh enough (lag 200 < elapsed 500)
        router.update_replica_lag("replica-2", 200)

        # user1 strictly reads from replica-2
        routed_user1 = set()
        for _ in range(10):
            routed_user1.add(router.route_read("user1"))

        self.assertIn("replica-2", routed_user1)
        self.assertNotIn("replica-1", routed_user1)
        self.assertNotIn("primary-db", routed_user1)

        # user2 hasn't written, reads from both
        routed_user2 = set()
        for _ in range(10):
            routed_user2.add(router.route_read("user2"))

        self.assertIn("replica-1", routed_user2)
        self.assertIn("replica-2", routed_user2)

if __name__ == '__main__':
    unittest.main()

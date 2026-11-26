"""Tests for Database Replication implementations."""

import unittest
import time
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))


class TestSimplePrimaryReplica(unittest.TestCase):
    """Tests for SimplePrimaryReplica."""

    def test_write_replicates_to_all(self):
        """Write should replicate to all replicas."""
        from simple_primary_replica import SimplePrimaryReplica

        db = SimplePrimaryReplica(replica_count=3)
        db.write("key", "value")

        # All replicas should have the data
        for i in range(3):
            value = db._replicas[i].get("key")
            self.assertEqual(value, "value")

    def test_read_from_replica(self):
        """Read should return value from replica."""
        from simple_primary_replica import SimplePrimaryReplica

        db = SimplePrimaryReplica(replica_count=2)
        db.write("user:1", "Alice")

        value = db.read("user:1")
        self.assertEqual(value, "Alice")

    def test_read_from_primary(self):
        """Read from primary should work."""
        from simple_primary_replica import SimplePrimaryReplica

        db = SimplePrimaryReplica(replica_count=2)
        db.write("user:1", "Bob")

        value = db.read_from_primary("user:1")
        self.assertEqual(value, "Bob")


class TestAsyncReplication(unittest.TestCase):
    """Tests for AsyncReplication."""

    def test_async_replication_with_delay(self):
        """Async replication should have delay."""
        from async_replication import AsyncReplication

        db = AsyncReplication(replica_count=1, replication_delay_ms=200)
        db.write("key", "value")

        # Immediate read from replica should miss
        # (replication not complete yet)
        immediate_value = db._replicas[0].get("key")
        self.assertIsNone(immediate_value)

        # After delay, should have value
        time.sleep(0.3)
        delayed_value = db._replicas[0].get("key")
        self.assertEqual(delayed_value, "value")

        db.shutdown()

    def test_consistent_read_fallback(self):
        """Consistent read should fallback to primary if replica behind."""
        from async_replication import AsyncReplication

        db = AsyncReplication(replica_count=1, replication_delay_ms=500)
        db.write("key", "value")

        # Consistent read should return value (from primary)
        value = db.read_consistent("key")
        self.assertEqual(value, "value")

        db.shutdown()


class TestMultiPrimaryReplication(unittest.TestCase):
    """Tests for MultiPrimaryReplication."""

    def test_write_to_different_primaries(self):
        """Should be able to write to different primaries."""
        from multi_primary_replication import MultiPrimaryReplication

        db = MultiPrimaryReplication(node_count=2, replication_delay_ms=50)

        db.write(0, "key1", "value1")
        db.write(1, "key2", "value2")

        # Each primary should have its own data
        self.assertEqual(db.read(0, "key1"), "value1")
        self.assertEqual(db.read(1, "key2"), "value2")

        db.shutdown()

    def test_replication_between_primaries(self):
        """Data should replicate between primaries."""
        from multi_primary_replication import MultiPrimaryReplication

        db = MultiPrimaryReplication(node_count=2, replication_delay_ms=50)

        db.write(0, "key", "value")

        # Wait for replication
        time.sleep(0.2)

        # Should be readable from other primary
        value = db.read(1, "key")
        self.assertEqual(value, "value")

        db.shutdown()

    def test_conflict_resolution(self):
        """Conflicts should be resolved using LWW."""
        from multi_primary_replication import MultiPrimaryReplication, VersionedValue, LastWriteWinsResolver

        resolver = LastWriteWinsResolver()

        old = VersionedValue("old", 100.0, "node1")
        new = VersionedValue("new", 200.0, "node2")

        winner = resolver.resolve(old, new)
        self.assertEqual(winner.value, "new")


if __name__ == "__main__":
    unittest.main()

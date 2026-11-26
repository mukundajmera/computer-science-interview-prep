"""
Tests for Database Sharding implementations.
"""

import unittest
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))

from hash_shard_router import HashShardRouter
from range_shard_router import RangeShardRouter
from consistent_hash_router import ConsistentHashShardRouter


class TestHashShardRouter(unittest.TestCase):
    """Tests for v1 simple hash-based sharding."""

    def test_distribution(self):
        """Test that data is distributed across shards."""
        router = HashShardRouter(4)
        
        # Insert 1000 items
        for i in range(1000):
            key = f"user_{i}"
            router.put(key, key, {"id": i})
        
        # Check distribution - each shard should have items
        for i in range(4):
            self.assertGreater(router.get_shard_size(i), 0)
        
        self.assertEqual(router.get_total_size(), 1000)

    def test_consistency(self):
        """Test that same key always maps to same shard."""
        router = HashShardRouter(4)
        
        key = "test_user_123"
        shard1 = router.get_shard_id(key)
        shard2 = router.get_shard_id(key)
        shard3 = router.get_shard_id(key)
        
        self.assertEqual(shard1, shard2)
        self.assertEqual(shard2, shard3)

    def test_get_and_put(self):
        """Test storing and retrieving data."""
        router = HashShardRouter(4)
        
        router.put("user_1", "profile", {"name": "Alice"})
        router.put("user_1", "settings", {"theme": "dark"})
        
        self.assertEqual(router.get("user_1", "profile"), {"name": "Alice"})
        self.assertEqual(router.get("user_1", "settings"), {"theme": "dark"})

    def test_delete(self):
        """Test deleting data."""
        router = HashShardRouter(4)
        
        router.put("user_1", "data", "value")
        self.assertTrue(router.delete("user_1", "data"))
        self.assertIsNone(router.get("user_1", "data"))
        
        # Deleting non-existent key
        self.assertFalse(router.delete("user_1", "nonexistent"))


class TestRangeShardRouter(unittest.TestCase):
    """Tests for v2 range-based sharding."""

    def test_routing(self):
        """Test that keys route to correct shards."""
        router = RangeShardRouter()
        router.add_shard("shard_1", 0, 1000)
        router.add_shard("shard_2", 1000, 2000)
        router.add_shard("shard_3", 2000, 3000)
        
        self.assertEqual(router.route_to_shard(500).shard_id, "shard_1")
        self.assertEqual(router.route_to_shard(1500).shard_id, "shard_2")
        self.assertEqual(router.route_to_shard(2500).shard_id, "shard_3")

    def test_range_query(self):
        """Test range queries across shards."""
        router = RangeShardRouter()
        router.add_shard("shard_1", 0, 1000)
        router.add_shard("shard_2", 1000, 2000)
        
        # Insert data
        for i in range(1500):
            router.put(i, {"id": i})
        
        # Range query across shards
        results = router.range_query(500, 1200)
        
        # Should include items from 500-1199 (700 items)
        self.assertEqual(len(results), 700)

    def test_health_check(self):
        """Test unhealthy shard handling."""
        router = RangeShardRouter()
        router.add_shard("shard_1", 0, 1000)
        
        # Should work when healthy
        router.put(500, {"id": 500})
        
        # Mark unhealthy
        router.mark_shard_unhealthy("shard_1")
        
        # Should fail when unhealthy
        with self.assertRaises(RuntimeError):
            router.put(600, {"id": 600})

    def test_key_not_found(self):
        """Test error when key doesn't map to any shard."""
        router = RangeShardRouter()
        router.add_shard("shard_1", 0, 1000)
        
        with self.assertRaises(ValueError):
            router.route_to_shard(2000)


class TestConsistentHashShardRouter(unittest.TestCase):
    """Tests for v3 production consistent hash sharding."""

    def test_minimal_redistribution(self):
        """Test that adding shard causes minimal key movement."""
        router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=1)
        router.add_shard("shard_1")
        router.add_shard("shard_2")
        router.add_shard("shard_3")
        
        # Track initial mapping
        before_mapping = {f"key_{i}": router.get_shard_for_key(f"key_{i}") 
                         for i in range(1000)}
        
        # Add new shard
        router.add_shard("shard_4")
        
        # Count changes
        changed = sum(1 for i in range(1000) 
                     if before_mapping[f"key_{i}"] != router.get_shard_for_key(f"key_{i}"))
        
        # With consistent hashing, roughly 25% should change (allow 15-40% range)
        change_percent = changed * 100 / 1000
        self.assertLess(change_percent, 40, f"Too many keys changed: {change_percent}%")

    def test_replication(self):
        """Test that replication returns correct number of shards."""
        router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=3)
        router.add_shard("shard_1")
        router.add_shard("shard_2")
        router.add_shard("shard_3")
        
        replicas = router.get_shards_for_replication("test_key")
        
        # Should get 3 unique replicas
        self.assertEqual(len(replicas), 3)
        self.assertEqual(len(set(replicas)), 3)

    def test_failover(self):
        """Test reading from replica when primary fails."""
        router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=2)
        router.add_shard("shard_1")
        router.add_shard("shard_2")
        router.add_shard("shard_3")
        
        # Insert data
        router.put("test_key", {"value": "test"})
        
        # Mark primary shard as unhealthy
        primary = router.get_shard_for_key("test_key")
        router.mark_shard_unhealthy(primary)
        
        # Should still be able to read from replica
        retrieved = router.get("test_key")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["value"], "test")

    def test_remove_shard(self):
        """Test removing a shard returns data for migration."""
        router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=1)
        router.add_shard("shard_1")
        router.add_shard("shard_2")
        
        # Insert data
        for i in range(100):
            router.put(f"key_{i}", {"id": i})
        
        initial_count = router.get_shard_count()
        
        # Remove shard
        migrated = router.remove_shard("shard_1")
        
        # Should have data to migrate
        self.assertGreater(len(migrated), 0)
        self.assertEqual(router.get_shard_count(), initial_count - 1)

    def test_duplicate_shard_error(self):
        """Test adding duplicate shard raises error."""
        router = ConsistentHashShardRouter()
        router.add_shard("shard_1")
        
        with self.assertRaises(ValueError):
            router.add_shard("shard_1")

    def test_no_shards_error(self):
        """Test error when no shards available."""
        router = ConsistentHashShardRouter()
        
        with self.assertRaises(RuntimeError):
            router.get_shard_for_key("any_key")


if __name__ == "__main__":
    unittest.main()

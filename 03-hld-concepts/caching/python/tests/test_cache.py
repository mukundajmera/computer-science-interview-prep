"""
Unit Tests for Cache Implementations
"""

import unittest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))


class TestSimpleCache(unittest.TestCase):
    """Tests for SimpleCache implementation."""
    
    def test_put_and_get(self):
        """Should store and retrieve values."""
        from simple_cache import SimpleCache
        
        cache = SimpleCache(default_ttl_seconds=60)
        cache.put("key", "value")
        
        self.assertEqual(cache.get("key"), "value")
    
    def test_cache_miss(self):
        """Should return None for missing keys."""
        from simple_cache import SimpleCache
        
        cache = SimpleCache(default_ttl_seconds=60)
        
        self.assertIsNone(cache.get("nonexistent"))
    
    def test_ttl_expiration(self):
        """Should expire entries after TTL."""
        from simple_cache import SimpleCache
        
        cache = SimpleCache(default_ttl_seconds=1)
        cache.put("key", "value", ttl_seconds=1)
        
        # Should exist initially
        self.assertEqual(cache.get("key"), "value")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        self.assertIsNone(cache.get("key"))
    
    def test_remove(self):
        """Should remove entries."""
        from simple_cache import SimpleCache
        
        cache = SimpleCache(default_ttl_seconds=60)
        cache.put("key", "value")
        cache.remove("key")
        
        self.assertIsNone(cache.get("key"))
    
    def test_clear(self):
        """Should clear all entries."""
        from simple_cache import SimpleCache
        
        cache = SimpleCache(default_ttl_seconds=60)
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cache.clear()
        
        self.assertEqual(cache.size(), 0)
    
    def test_cleanup(self):
        """Should remove expired entries on cleanup."""
        from simple_cache import SimpleCache
        
        cache = SimpleCache(default_ttl_seconds=60)
        cache.put("expired", "value", ttl_seconds=0)  # Already expired
        cache.put("valid", "value", ttl_seconds=60)
        
        time.sleep(0.1)
        removed = cache.cleanup()
        
        self.assertEqual(removed, 1)
        self.assertIsNone(cache.get("expired"))
        self.assertIsNotNone(cache.get("valid"))


class TestLRUCache(unittest.TestCase):
    """Tests for LRUCache implementation."""
    
    def test_lru_eviction(self):
        """Should evict least recently used when at capacity."""
        from lru_cache import LRUCache
        
        cache = LRUCache(capacity=2, default_ttl_seconds=60)
        cache.put("A", "1")
        cache.put("B", "2")
        
        # Access A to make B the LRU
        cache.get("A")
        
        # Add C - should evict B
        cache.put("C", "3")
        
        self.assertIsNotNone(cache.get("A"))
        self.assertIsNone(cache.get("B"))  # Evicted
        self.assertIsNotNone(cache.get("C"))
    
    def test_hit_rate_tracking(self):
        """Should track hit rate correctly."""
        from lru_cache import LRUCache
        
        cache = LRUCache(capacity=10, default_ttl_seconds=60)
        cache.put("key", "value")
        
        cache.get("key")      # hit
        cache.get("key")      # hit
        cache.get("missing")  # miss
        cache.get("missing2") # miss
        
        self.assertEqual(cache.stats.hits, 2)
        self.assertEqual(cache.stats.misses, 2)
        self.assertAlmostEqual(cache.stats.hit_rate(), 50.0, places=1)
    
    def test_get_or_compute(self):
        """Should compute and cache on miss."""
        from lru_cache import LRUCache
        
        cache = LRUCache(capacity=10, default_ttl_seconds=60)
        compute_count = [0]
        
        def loader():
            compute_count[0] += 1
            return 42
        
        result1 = cache.get_or_compute("key", loader)
        result2 = cache.get_or_compute("key", loader)
        
        self.assertEqual(result1, 42)
        self.assertEqual(result2, 42)
        self.assertEqual(compute_count[0], 1)  # Only computed once
    
    def test_capacity_limit(self):
        """Should respect capacity limit."""
        from lru_cache import LRUCache
        
        cache = LRUCache(capacity=3, default_ttl_seconds=60)
        
        for i in range(10):
            cache.put(i, f"value{i}")
        
        self.assertEqual(cache.size(), 3)
    
    def test_thread_safety(self):
        """Should handle concurrent access."""
        from lru_cache import LRUCache
        
        cache = LRUCache(capacity=100, default_ttl_seconds=60)
        
        def worker(worker_id):
            for i in range(100):
                cache.put(f"{worker_id}:{i}", f"value")
                cache.get(f"{worker_id}:{i}")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for f in futures:
                f.result()
        
        # No exceptions = success
        self.assertLessEqual(cache.size(), 100)


class TestWriteThruCache(unittest.TestCase):
    """Tests for WriteThruCache implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        from write_thru_cache import InMemoryDataSource, WriteThruCache
        
        self.data_source = InMemoryDataSource()
        self.cache = WriteThruCache(
            capacity=100,
            default_ttl_seconds=60,
            data_source=self.data_source
        )
    
    def tearDown(self):
        """Clean up."""
        self.cache.shutdown()
    
    def test_write_through(self):
        """Should write through to data source."""
        self.cache.put("key", "value")
        
        self.assertEqual(self.cache.get("key"), "value")
        self.assertEqual(self.data_source.get("key"), "value")
    
    def test_load_on_miss(self):
        """Should load from data source on miss."""
        self.data_source.put("key", "fromDB")
        
        result = self.cache.get("key")
        
        self.assertEqual(result, "fromDB")
        self.assertEqual(self.cache.stats.loads, 1)
    
    def test_stampede_prevention(self):
        """Should prevent cache stampede."""
        self.data_source.put("key", "value")
        self.data_source.set_delay(50)  # 50ms delay
        self.data_source.reset_call_count()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.cache.get, "key") for _ in range(10)]
            for f in futures:
                f.result()
        
        # With stampede prevention, should only load once (or very few times)
        self.assertLessEqual(self.data_source.get_call_count(), 2)
    
    def test_statistics(self):
        """Should track statistics correctly."""
        self.data_source.put("key", "value")
        
        self.cache.get("key")     # miss + load
        self.cache.get("key")     # hit
        self.cache.get("key")     # hit
        self.cache.put("new", "v") # write-thru
        
        self.assertEqual(self.cache.stats.hits, 2)
        self.assertEqual(self.cache.stats.misses, 1)
        self.assertEqual(self.cache.stats.loads, 1)
        self.assertEqual(self.cache.stats.write_thrus, 1)
    
    def test_invalidate(self):
        """Should invalidate without touching data source."""
        self.cache.put("key", "value")
        self.cache.invalidate("key")
        
        # Should trigger reload
        self.data_source.reset_call_count()
        self.cache.get("key")
        
        self.assertEqual(self.data_source.get_call_count(), 1)

    def test_shutdown_stops_background_cleanup_thread(self):
        """Should not leave cleanup executor thread alive after shutdown."""
        from write_thru_cache import InMemoryDataSource, WriteThruCache

        self.cache.shutdown()
        time.sleep(0.05)

        cache = WriteThruCache(
            capacity=10,
            default_ttl_seconds=60,
            data_source=InMemoryDataSource(),
            cleanup_interval_seconds=3600,
        )

        cache.shutdown()
        time.sleep(0.05)

        cache_threads = [
            thread.name for thread in threading.enumerate()
            if thread.name.startswith("cache-bg")
        ]
        self.assertEqual(cache_threads, [])


class TestIntegration(unittest.TestCase):
    """Integration tests for cache patterns."""
    
    def test_cache_aside_pattern(self):
        """Test cache-aside pattern workflow."""
        from simple_cache import SimpleCache
        
        cache = SimpleCache(default_ttl_seconds=60)
        db = {"user:1": "Alice", "user:2": "Bob"}
        
        def get_user(user_id):
            # Try cache first
            user = cache.get(user_id)
            if user is not None:
                return user, "HIT"
            
            # Miss - fetch from DB
            user = db.get(user_id)
            if user:
                cache.put(user_id, user)
            return user, "MISS"
        
        # First call - miss
        user, status = get_user("user:1")
        self.assertEqual(user, "Alice")
        self.assertEqual(status, "MISS")
        
        # Second call - hit
        user, status = get_user("user:1")
        self.assertEqual(user, "Alice")
        self.assertEqual(status, "HIT")


if __name__ == '__main__':
    unittest.main()

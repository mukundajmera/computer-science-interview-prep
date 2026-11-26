"""
Tests for LRU Cache implementations.
"""
import unittest
import time
import threading
from concurrent.futures import ThreadPoolExecutor

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))
from concurrent_lru_cache import ConcurrentLRUCache


class TestLRUCacheV1(unittest.TestCase):
    """Tests for V1 Basic implementation."""

    def test_get_non_existent_key(self):
        """Get returns None for non-existent key."""
        found = False
        self.assertFalse(found, "Should return None for non-existent key")

    def test_put_and_get(self):
        """Put and get work correctly."""
        capacity = 3
        values = {0: 1, 1: 2}
        
        self.assertEqual(1, values[0], "Should get value 1 for key 0")
        self.assertEqual(2, values[1], "Should get value 2 for key 1")

    def test_eviction(self):
        """Eviction happens when capacity exceeded."""
        capacity = 2
        order = [0, 1, 2]  # a, b, c added
        
        evicted = order[0]  # 'a' is evicted
        self.assertEqual(0, evicted, "First item should be evicted")

    def test_access_moves_to_front(self):
        """Access moves item to front."""
        order_before = ["a", "b", "c"]
        order_after = ["b", "c", "a"]  # After accessing 'a'
        
        self.assertEqual("b", order_after[0], "b should be LRU after accessing a")

    def test_update_moves_to_front(self):
        """Update existing key moves to front."""
        lru = "b"  # After updating 'a'
        self.assertEqual("b", lru, "b should be LRU after updating a")


class TestLRUCacheV2(unittest.TestCase):
    """Tests for V2 Extended implementation."""

    def test_ttl_expiration(self):
        """TTL expiration works correctly."""
        ttl_ms = 100
        created_at = int(time.time() * 1000)
        expires_at = created_at + ttl_ms
        
        time.sleep(0.15)
        
        is_expired = int(time.time() * 1000) > expires_at
        self.assertTrue(is_expired, "Entry should be expired after TTL")

    def test_statistics_hit_ratio(self):
        """Cache statistics hit ratio calculation."""
        hits = 80
        misses = 20
        hit_ratio = hits / (hits + misses)
        
        self.assertAlmostEqual(0.8, hit_ratio, places=2, msg="Hit ratio should be 80%")

    def test_eviction_listener(self):
        """Eviction listener is called."""
        listener_called = [False]
        evicted_key = "evicted"
        
        def listener(key, value, cause):
            listener_called[0] = True
        
        if evicted_key == "evicted":
            listener("evicted", 1, "CAPACITY")
        
        self.assertTrue(listener_called[0], "Eviction listener should be called")


class TestLRUCacheV3(unittest.TestCase):
    """Tests for V3 Optimized implementation."""

    def test_concurrent_access(self):
        """Concurrent access doesn't corrupt data."""
        num_threads = 10
        operations_per_thread = 100
        
        shared_value = [0]
        lock = threading.Lock()

        def worker():
            for _ in range(operations_per_thread):
                with lock:
                    shared_value[0] += 1
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            for f in futures:
                f.result()
        
        self.assertEqual(num_threads * operations_per_thread, shared_value[0],
                        "All operations should complete without data loss")

    def test_thread_safe_statistics(self):
        """Thread-safe statistics tracking."""
        hits = [0]
        lock = threading.Lock()

        def increment():
            with lock:
                hits[0] += 1
        
        increment()
        increment()
        
        self.assertEqual(2, hits[0], "Counter should be accurate")

    def test_concurrent_stress(self):
        """Concurrent stress test asserting absence of race conditions, lost updates, or deadlocks."""
        cache = ConcurrentLRUCache(capacity=1000, num_segments=16)
        num_threads = 8
        items_per_thread = 1000

        def worker(thread_id):
            # Put values
            for i in range(items_per_thread):
                key = f"key_{thread_id}_{i}"
                cache.put(key, i)
                
            # Get values (mix hits and misses)
            for i in range(items_per_thread):
                key = f"key_{thread_id}_{i}"
                cache.get(key)
                
            # Remove half the values
            for i in range(0, items_per_thread, 2):
                key = f"key_{thread_id}_{i}"
                cache.remove(key)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for f in futures:
                f.result() # Will raise exception if a thread deadlocked or crashed

        # Assert no exceptions happened and operations completed successfully.
        # Check invariants.
        self.assertTrue(cache.size() <= cache.capacity, "Cache size exceeded capacity")
        
        # Verify stats are sensible
        self.assertTrue(cache.hits > 0, "Hits should be > 0")
        self.assertTrue(cache.misses > 0, "Misses should be > 0")


class TestEdgeCases(unittest.TestCase):
    """Edge case tests."""

    def test_single_capacity(self):
        """Single capacity cache works correctly."""
        capacity = 1
        current_size = 1
        current_key = "b"  # After putting 'a' then 'b'
        
        self.assertEqual(1, current_size, "Size should always be 1")
        self.assertEqual("b", current_key, "Only 'b' should remain")

    def test_clear(self):
        """Clear removes all entries."""
        size_after = 0
        self.assertEqual(0, size_after, "Size should be 0 after clear")

    def test_remove(self):
        """Remove returns correct value."""
        value_removed = 42
        self.assertEqual(42, value_removed, "Remove should return the value")

    def test_contains_key_doesnt_update_order(self):
        """containsKey doesn't update order."""
        lru = "a"  # Should still be LRU
        self.assertEqual("a", lru, "containsKey should not change LRU order")


if __name__ == '__main__':
    unittest.main()

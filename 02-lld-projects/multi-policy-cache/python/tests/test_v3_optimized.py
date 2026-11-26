import pytest
import time
import sys
import os
import threading
import concurrent.futures

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))
for module_name in ["multi_policy_cache"]:
    sys.modules.pop(module_name, None)

from multi_policy_cache import MultiPolicyCache, EvictionPolicy

def test_v3_ttl_active_background_expiry():
    cache = MultiPolicyCache(capacity=100, policy=EvictionPolicy.LRU, num_segments=4)
    # Insert multiple items so probabilistic sweeping catches them
    for i in range(20):
        cache.put(f"key{i}", "val", ttl_ms=100)
    
    time.sleep(1.5) # Background sweeper runs every 1 sec
    
    assert cache.size() < 20 # Some or all should be expired and swept.
    # Actually wait, probabilistic sweeping might not catch all 20, but it will catch some.
    cache.shutdown()

def test_v3_read_concurrency_high_throughput():
    cache = MultiPolicyCache(capacity=4096, policy=EvictionPolicy.LFU, num_segments=16)
    
    def worker(worker_id):
        for i in range(100):
            cache.put(f"key_{worker_id}_{i}", i)
            cache.get(f"key_{worker_id}_{i}")
            
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert cache.size() == 1000
    cache.shutdown()

def test_v3_thread_safe_statistics():
    cache = MultiPolicyCache(capacity=100, policy=EvictionPolicy.FIFO, num_segments=4)
    
    def worker():
        for i in range(50):
            cache.put(f"key_{i}", i) # 50 puts
            cache.get(f"key_{i}")    # 50 hits
            cache.get(f"miss_{i}")   # 50 misses
            
    threads = []
    for _ in range(4):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    stats = cache.get_stats()
    assert stats.hits == 200
    assert stats.misses == 200
    assert stats.evictions >= 0
    cache.shutdown()

def test_v3_segmented_eviction():
    cache = MultiPolicyCache(capacity=16, policy=EvictionPolicy.LRU, num_segments=4)
    # capacity per segment = 16 // 4 = 4.
    
    for i in range(100):
        cache.put(f"key_{i}", i)
        
    assert cache.size() <= 16
    stats = cache.get_stats()
    assert stats.evictions > 0
    cache.shutdown()

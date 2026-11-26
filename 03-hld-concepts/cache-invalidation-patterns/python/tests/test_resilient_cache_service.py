import time
import threading
import sys
import os
import pytest

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from resilient_cache_service import ResilientCacheService

def test_bloom_filter_prevents_db_hit():
    db_hits = [0]
    
    def mock_db_loader(key):
        db_hits[0] += 1
        return "data"

    # Bloom filter always returns False
    cache = ResilientCacheService(bloom_filter=lambda k: False, base_ttl_sec=1.0, jitter_sec=0.1, null_ttl_sec=0.5)
    
    result = cache.get("invalid_key", mock_db_loader)
    
    assert result is None
    assert db_hits[0] == 0, "DB should not be hit if Bloom filter rejects key"

def test_null_caching_prevents_db_hits():
    db_hits = [0]
    
    def mock_db_loader(key):
        db_hits[0] += 1
        return None

    # Bloom filter always returns True
    cache = ResilientCacheService(bloom_filter=lambda k: True, base_ttl_sec=1.0, jitter_sec=0.1, null_ttl_sec=0.5)
    
    result1 = cache.get("missing_key", mock_db_loader)
    result2 = cache.get("missing_key", mock_db_loader)
    
    assert result1 is None
    assert result2 is None
    assert db_hits[0] == 1, "DB should only be hit once due to null object caching"
    
    entry = cache._get_raw_entry("missing_key")
    assert entry is not None
    assert entry.is_null_object is True

def test_singleflight_thundering_herd_mitigation():
    db_hits = [0]
    
    def mock_db_loader(key):
        db_hits[0] += 1
        time.sleep(0.05)  # Simulate DB latency
        return "viral_content"

    cache = ResilientCacheService(bloom_filter=lambda k: True, base_ttl_sec=5.0, jitter_sec=0.1, null_ttl_sec=0.5)
    
    num_threads = 50
    threads = []
    
    start_event = threading.Event()
    
    def worker():
        start_event.wait()
        cache.get("hot_key", mock_db_loader)
        
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
        
    start_event.set()
    
    for t in threads:
        t.join()
        
    assert db_hits[0] == 1, "DB should exactly be hit 1 time despite 50 concurrent threads"
    assert cache.get("hot_key", lambda k: "wrong") == "viral_content"

def test_ttl_jitter_distribution():
    base_ttl = 1.0
    jitter = 0.5
    
    cache = ResilientCacheService(bloom_filter=lambda k: True, base_ttl_sec=base_ttl, jitter_sec=jitter, null_ttl_sec=0.5)
    
    cache.get("key1", lambda k: "data1")
    cache.get("key2", lambda k: "data2")
    
    entry1 = cache._get_raw_entry("key1")
    entry2 = cache._get_raw_entry("key2")
    
    assert entry1 is not None
    assert entry2 is not None
    
    now = time.time()
    
    assert now + base_ttl - 0.1 <= entry1.expire_at <= now + base_ttl + jitter + 0.1
    assert now + base_ttl - 0.1 <= entry2.expire_at <= now + base_ttl + jitter + 0.1
    
    # It is highly probable that the TTls are not exactly the same
    assert entry1.expire_at != entry2.expire_at

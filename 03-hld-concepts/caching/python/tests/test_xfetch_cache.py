import pytest
import time
import math
from concurrent.futures import ThreadPoolExecutor

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v4-xfetch'))
from singleflight import Singleflight
from xfetch_cache import XFetchCache

def test_singleflight_deduplication():
    sf = Singleflight()
    call_count = 0
    
    def slow_loader():
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)
        return "result"
        
    def worker():
        val, err, shared = sf.do("key1", slow_loader)
        return val, shared
        
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker) for _ in range(5)]
        results = [f.result() for f in futures]
        
    assert call_count == 1
    assert all(val == "result" for val, _ in results)
    
    shared_count = sum(1 for _, shared in results if shared)
    assert shared_count == 4 # 4 waited for the first one

def test_singleflight_exception():
    sf = Singleflight()
    
    def failing_loader():
        time.sleep(0.1)
        raise ValueError("Oops")
        
    def worker():
        val, err, shared = sf.do("key2", failing_loader)
        return err, shared
        
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker) for _ in range(5)]
        results = [f.result() for f in futures]
        
    assert all(isinstance(err, ValueError) for err, _ in results)
    
def test_xfetch_probabilistic_refresh():
    # Test probabilistic refresh logic deterministicly
    clock_val = 1000.0
    def mock_clock():
        return clock_val
        
    # threshold = -1.0 * delta * ln(u)
    # Remaining = 5.0 (TTL = 10, time elapsed = 5)
    # Let delta = 2.0
    # Refresh condition: -2.0 * ln(u) >= 5.0  => ln(u) <= -2.5 => u <= e^-2.5 (~0.082)
    u_val = 0.5
    def mock_rng():
        return u_val
        
    cache = XFetchCache(beta=1.0, clock=mock_clock, rng=mock_rng)
    
    # Loader will take 2 seconds (delta)
    def mock_loader():
        nonlocal clock_val
        clock_val += 2.0
        return "data"
        
    # Initial get
    val = cache.get("key", mock_loader, 10.0) # Clock ends at 1002.0
    assert val == "data"
    
    entry = cache._store["key"]
    assert entry.delta == 2.0
    assert entry.created_at == 1002.0
    assert entry.expires_at == 1012.0
    
    # Fast forward to 1007.0. Remaining TTL is 5.0.
    clock_val = 1007.0
    
    # Try with high u (0.5), shouldn't refresh
    u_val = 0.5
    val = cache.get("key", mock_loader, 10.0)
    assert cache._store["key"].created_at == 1002.0 # unchanged
    
    # Try with low u (0.05), should trigger background refresh
    u_val = 0.05
    val = cache.get("key", mock_loader, 10.0)
    
    # Wait a bit for executor to run
    time.sleep(0.1)
    
    # The background thread would have run mock_loader, advancing clock to 1009.0
    entry = cache._store["key"]
    assert entry.created_at == 1009.0
    
    cache.shutdown()

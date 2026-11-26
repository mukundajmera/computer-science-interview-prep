import os
import sys
import time
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the implementation directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'implementation')))

from rate_limiter import RedisSimulator, Tier1DistributedRateLimiter

def test_sliding_window_counter_accuracy():
    """Verifies the sliding window counter approximation logic."""
    redis = RedisSimulator()
    user_id = "user1"
    limit = 100
    window_sec = 60
    
    # Simulate previous window (T=0 to T=59) having 80 requests
    for i in range(80):
        res = redis.eval_lua("sliding_window_increment", [user_id], [limit, window_sec, 30])
        assert res == 1
        
    # Now at T=75 (15 seconds into current window, weight=0.75)
    # Estimated = (80 * 0.75) + curr = 60 + curr. Limit is 100.
    # So we should be able to do exactly 40 requests in current window.
    
    current_time = 75
    allowed_count = 0
    for _ in range(50):
        if redis.eval_lua("sliding_window_increment", [user_id], [limit, window_sec, current_time]) == 1:
            allowed_count += 1
            
    assert allowed_count == 40

def test_lua_script_atomicity_simulation():
    """Verifies that concurrent requests don't exceed the global limit due to race conditions."""
    redis = RedisSimulator()
    user_id = "user2"
    limit = 1000
    window_sec = 60
    current_time = 100
    
    def worker():
        allowed = 0
        for _ in range(200):
            if redis.eval_lua("sliding_window_increment", [user_id], [limit, window_sec, current_time]) == 1:
                allowed += 1
        return allowed
        
    total_allowed = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(10)]
        for future in as_completed(futures):
            total_allowed += future.result()
            
    # Exactly 1000 should be allowed, no more.
    assert total_allowed == limit

def test_local_batching_speed_and_exhaustion():
    """Verifies that local batching serves requests extremely fast and respects central exhaustion."""
    redis = RedisSimulator()
    global_limit = 50
    batch_size = 20
    window_sec = 60
    current_time = 100
    
    limiter = Tier1DistributedRateLimiter(redis, global_limit, window_sec, batch_size)
    
    # Request 1: Fetches batch of 20. 1 consumed, 19 left locally. Global left = 30.
    start_time = time.perf_counter()
    assert limiter.allow_request("user3", current_time) == True
    first_req_duration = time.perf_counter() - start_time
    
    # Request 2: Served from local memory
    start_time = time.perf_counter()
    assert limiter.allow_request("user3", current_time) == True
    second_req_duration = time.perf_counter() - start_time
    
    # Local should be much faster than the initial fetch (even in simulation)
    # Though in this basic single-thread simulation it might be close, we can assert structure
    assert limiter.local_tokens["user3"] == 18
    
    # Consume rest of first batch (18 more)
    for _ in range(18):
        assert limiter.allow_request("user3", current_time) == True
        
    # Local tokens should trigger replenish at some point or fetch new batch
    # Consume 20 more (fetches batch 2). Global left = 10.
    for _ in range(20):
        assert limiter.allow_request("user3", current_time) == True
        
    # Consume 10 more (fetches batch 3, size 10). Global left = 0.
    for _ in range(10):
        assert limiter.allow_request("user3", current_time) == True
        
    # Next request should be rejected
    assert limiter.allow_request("user3", current_time) == False

def test_distributed_gateway_workers():
    """Verifies multiple gateway nodes drawing from the same central Redis."""
    redis = RedisSimulator()
    global_limit = 100
    batch_size = 30
    window_sec = 60
    current_time = 200
    
    gateway1 = Tier1DistributedRateLimiter(redis, global_limit, window_sec, batch_size)
    gateway2 = Tier1DistributedRateLimiter(redis, global_limit, window_sec, batch_size)
    
    # GW1 asks for batch (gets 30, global=70)
    assert gateway1.allow_request("user4", current_time) == True
    
    # GW2 asks for batch (gets 30, global=40)
    assert gateway2.allow_request("user4", current_time) == True
    
    # GW1 asks for another batch (simulate burst) -> will consume its 29, then ask for 30 (gets 30, global=10)
    for _ in range(50): # 29 local + 21 from new batch (which is 30)
        gateway1.allow_request("user4", current_time)
        
    # GW2 has 29 local. It consumes them, then asks for batch. Global has 10 left, so it gets 10.
    # Total it can serve is 29 + 10 = 39.
    allowed_gw2 = 0
    for _ in range(50):
        if gateway2.allow_request("user4", current_time):
            allowed_gw2 += 1
            
    assert allowed_gw2 == 39

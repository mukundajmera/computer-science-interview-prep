import pytest
import time
import threading

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from resilience_orchestrator import ResilienceOrchestrator, CircuitBreaker, RetryPolicy

def test_circuit_breaker_trips_to_open():
    orchestrator = ResilienceOrchestrator(cb_threshold=2, cb_timeout_ms=1000, bulkhead_capacity=10, max_retries=0, base_delay_ms=10)
    
    calls = [0]
    
    def fail_action():
        calls[0] += 1
        raise RuntimeError("fail")

    def success_action():
        calls[0] += 1
        return "success"
        
    def fallback_action():
        return "fallback"

    # 1st failure
    assert orchestrator.execute(fail_action, fallback_action) == "fallback"
    
    # 2nd failure - threshold reached, trips to open
    assert orchestrator.execute(fail_action, fallback_action) == "fallback"
    
    # 3rd call - Circuit is OPEN, fast fail, so action is not called
    assert orchestrator.execute(success_action, fallback_action) == "fallback"
    
    assert calls[0] == 2

def test_circuit_breaker_half_open_recovery():
    cb = CircuitBreaker(threshold=2, timeout_ms=100)
    
    def fail_action():
        raise RuntimeError("fail")
        
    def success_action():
        return "success"
        
    # Fail twice
    with pytest.raises(RuntimeError):
        cb.execute(fail_action)
    with pytest.raises(RuntimeError):
        cb.execute(fail_action)
        
    assert cb.state == CircuitBreaker.State.OPEN
    
    time.sleep(0.15) # Wait for reset timeout
    
    # Probe 1
    assert cb.execute(success_action) == "success"
    assert cb.state == CircuitBreaker.State.HALF_OPEN
    
    # Probe 2
    assert cb.execute(success_action) == "success"
    
    # Probe 3
    assert cb.execute(success_action) == "success"
    
    assert cb.state == CircuitBreaker.State.CLOSED

def test_bulkhead_rejection():
    orchestrator = ResilienceOrchestrator(cb_threshold=5, cb_timeout_ms=1000, bulkhead_capacity=2, max_retries=0, base_delay_ms=10)
    
    latch = threading.Event()
    success_count = [0]
    fallback_count = [0]
    
    def action():
        latch.wait()
        return "success"
        
    def fallback():
        return "fallback"
        
    def task():
        result = orchestrator.execute(action, fallback)
        if result == "success":
            success_count[0] += 1
        else:
            fallback_count[0] += 1
            
    t1 = threading.Thread(target=task)
    t2 = threading.Thread(target=task)
    t3 = threading.Thread(target=task)
    
    t1.start()
    t2.start()
    
    time.sleep(0.1) # ensure first two threads are blocking in semaphore
    
    t3.start()
    time.sleep(0.1)
    
    latch.set()
    
    t1.join()
    t2.join()
    t3.join()
    
    assert success_count[0] == 2
    assert fallback_count[0] == 1

def test_jitter_delay():
    policy = RetryPolicy(max_retries=3, base_delay_ms=100)
    calls = [0]
    
    def fail_action():
        calls[0] += 1
        raise RuntimeError("fail")
        
    start_time = time.time()
    
    with pytest.raises(RuntimeError):
        policy.execute_with_retry(fail_action)
        
    duration = (time.time() - start_time) * 1000
    
    assert calls[0] == 4
    # Max possible delay: 100 + 200 + 400 = 700
    assert 0 <= duration <= 800

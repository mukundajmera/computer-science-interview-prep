import pytest
import time
import threading
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

def test_monotonic_state_transitions_and_half_open_probes():
    from config import CircuitBreakerConfig
    from circuit_breaker import CircuitBreaker
    from circuit_breaker_state import CircuitBreakerState
    from exceptions import CircuitBreakerOpenException

    virtual_time = [1000000.0]
    def clock_stub():
        return virtual_time[0]

    config = CircuitBreakerConfig(50, 4, 1000, 2, 50, 1000)
    cb = CircuitBreaker(config, clock=clock_stub)

    def fail_call():
        raise RuntimeError("Fail")

    for _ in range(4):
        try:
            cb.execute(fail_call)
        except Exception:
            pass

    assert cb.state == CircuitBreakerState.OPEN

    # Elapse enough time for OPEN -> HALF_OPEN
    virtual_time[0] += 1100.0

    executed_in_half_open = 0
    rejected_by_half_open = 0
    lock = threading.Lock()
    
    start_event = threading.Event()
    
    def slow_fail_call():
        nonlocal executed_in_half_open
        with lock:
            executed_in_half_open += 1
        time.sleep(0.5)
        raise RuntimeError("Fail")

    def run_thread():
        nonlocal rejected_by_half_open
        start_event.wait()
        try:
            cb.execute(slow_fail_call)
        except CircuitBreakerOpenException:
            with lock:
                rejected_by_half_open += 1
        except Exception:
            pass

    threads = [threading.Thread(target=run_thread) for _ in range(8)]
    for t in threads:
        t.start()
        
    start_event.set()
    
    for t in threads:
        t.join()

    assert executed_in_half_open == 2
    assert rejected_by_half_open == 6
    assert cb.state == CircuitBreakerState.OPEN

def test_stale_closed_callback_does_not_affect_open_state():
    from config import CircuitBreakerConfig
    from circuit_breaker import CircuitBreaker
    from circuit_breaker_state import CircuitBreakerState
    from exceptions import CircuitBreakerOpenException

    virtual_time = [1000000.0]
    def clock_stub():
        return virtual_time[0]

    config = CircuitBreakerConfig(50, 4, 1000, 2, 50, 1000)
    cb = CircuitBreaker(config, clock=clock_stub)

    slow_call_started = threading.Event()
    fast_failures_finished = threading.Event()

    def slow_call():
        slow_call_started.set()
        fast_failures_finished.wait()
        return "Slow Success"

    def run_slow():
        try:
            cb.execute(slow_call)
        except Exception:
            pass

    slow_thread = threading.Thread(target=run_slow)
    slow_thread.start()

    slow_call_started.wait()

    def fail_call():
        raise RuntimeError("Fail")

    for _ in range(4):
        try:
            cb.execute(fail_call)
        except Exception:
            pass

    assert cb.state == CircuitBreakerState.OPEN

    fast_failures_finished.set()
    slow_thread.join()

    # The slow success should not have transitioned the state or reset metrics for the new OPEN generation
    assert cb.state == CircuitBreakerState.OPEN

import pytest
import time
import sys
import importlib
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

def test_initial_state_is_closed():
    # Setup sys path and modules to avoid cross-contamination
    if 'circuit_breaker' in sys.modules: del sys.modules['circuit_breaker']
    from circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerConfig
    config = CircuitBreakerConfig(50, 10, 1000, 2, 50, 1000)
    cb = CircuitBreaker(config)
    assert cb.state == CircuitBreakerState.CLOSED

def test_successful_calls_keep_state_closed():
    if 'circuit_breaker' in sys.modules: del sys.modules['circuit_breaker']
    from circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerConfig
    config = CircuitBreakerConfig(50, 10, 1000, 2, 50, 1000)
    cb = CircuitBreaker(config)
    
    def success_call():
        return "Success"
        
    for _ in range(5):
        assert cb.execute(success_call) == "Success"
    assert cb.state == CircuitBreakerState.CLOSED

def test_transition_to_open_on_failure_threshold():
    if 'circuit_breaker' in sys.modules: del sys.modules['circuit_breaker']
    from circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerConfig, CircuitBreakerOpenException
    config = CircuitBreakerConfig(50, 4, 1000, 2, 50, 1000)
    cb = CircuitBreaker(config)
    
    def fail_call():
        raise RuntimeError("Fail")
    def success_call():
        return "Success"

    try: cb.execute(fail_call)
    except: pass
    try: cb.execute(fail_call)
    except: pass
    try: cb.execute(success_call)
    except: pass
    try: cb.execute(fail_call)
    except: pass
    
    # 3 failures out of 4 calls = 75% > 50%
    assert cb.state == CircuitBreakerState.OPEN

def test_transition_to_half_open_after_wait():
    if 'circuit_breaker' in sys.modules: del sys.modules['circuit_breaker']
    from circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerConfig
    config = CircuitBreakerConfig(50, 2, 100, 2, 50, 1000)
    cb = CircuitBreaker(config)
    
    def fail_call():
        raise RuntimeError("Fail")

    try: cb.execute(fail_call)
    except: pass
    try: cb.execute(fail_call)
    except: pass
    
    assert cb.state == CircuitBreakerState.OPEN
    
    time.sleep(0.15) # wait duration is 100ms
    
    try: cb.execute(fail_call)
    except: pass
    assert cb.state == CircuitBreakerState.OPEN

def test_fallback_execution():
    if 'circuit_breaker' in sys.modules: del sys.modules['circuit_breaker']
    from circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerConfig
    config = CircuitBreakerConfig(50, 2, 100, 2, 50, 1000)
    cb = CircuitBreaker(config)
    
    def fail_call():
        raise RuntimeError("Fail")
    def fallback(e):
        return "FallbackResult"
        
    result = cb.execute(fail_call, fallback=fallback)
    assert result == "FallbackResult"

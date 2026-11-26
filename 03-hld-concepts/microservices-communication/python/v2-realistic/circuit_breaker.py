"""
V2: Circuit Breaker Pattern

Prevents cascading failures by stopping calls to failing services.
"""

import time
from enum import Enum
from typing import TypeVar, Callable
import threading

T = TypeVar('T')


class State(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    Circuit breaker for resilient service calls.
    
    Example:
        cb = CircuitBreaker("user-service", failure_threshold=3, open_duration_seconds=30)
        result = cb.call(
            action=lambda: call_user_service(),
            fallback=lambda: "cached_data"
        )
    """
    
    def __init__(self, name: str, failure_threshold: int = 5, open_duration_seconds: float = 30):
        self.name = name
        self._failure_threshold = failure_threshold
        self._open_duration = open_duration_seconds
        self._state = State.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._lock = threading.Lock()

    def call(self, action: Callable[[], T], fallback: Callable[[], T]) -> T:
        """Execute action with circuit breaker protection."""
        if not self._allow_request():
            print(f"[{self.name}] Circuit OPEN - using fallback")
            return fallback()
        
        try:
            result = action()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            print(f"[{self.name}] Call failed: {e}")
            return fallback()

    def _allow_request(self) -> bool:
        with self._lock:
            if self._state == State.CLOSED:
                return True
            
            if self._state == State.OPEN:
                if time.time() - self._last_failure_time > self._open_duration:
                    self._state = State.HALF_OPEN
                    print(f"[{self.name}] Circuit HALF_OPEN - testing")
                    return True
                return False
            
            return True  # HALF_OPEN

    def _on_success(self) -> None:
        with self._lock:
            if self._state == State.HALF_OPEN:
                self._state = State.CLOSED
                self._failure_count = 0
                print(f"[{self.name}] Circuit CLOSED - recovered")

    def _on_failure(self) -> None:
        with self._lock:
            self._last_failure_time = time.time()
            self._failure_count += 1
            
            if self._failure_count >= self._failure_threshold:
                self._state = State.OPEN
                print(f"[{self.name}] Circuit OPEN - threshold reached")

    @property
    def state(self) -> State:
        return self._state


if __name__ == "__main__":
    cb = CircuitBreaker("user-service", failure_threshold=3, open_duration_seconds=2)
    
    # Simulate failing service
    def failing_call():
        raise RuntimeError("Service down")
    
    fallback = lambda: "Cached user data"
    
    for i in range(5):
        result = cb.call(failing_call, fallback)
        print(f"Result: {result}, State: {cb.state.value}")
    
    print("\nWaiting for circuit to half-open...")
    time.sleep(2.5)
    
    # Service recovers
    working_call = lambda: "Live user data"
    result = cb.call(working_call, fallback)
    print(f"Result: {result}, State: {cb.state.value}")

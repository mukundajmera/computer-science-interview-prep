"""
V3: Retry with Exponential Backoff and Jitter

Production-grade retry mechanism for transient failures.
"""

import time
import random
from typing import TypeVar, Callable

T = TypeVar('T')


class RetryWithBackoff:
    """
    Retry with exponential backoff and jitter.
    
    Example:
        retry = RetryWithBackoff.default_config()
        result = retry.execute(lambda: call_flaky_service())
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay_ms: int = 100,
        multiplier: float = 2.0,
        max_delay_ms: int = 5000,
        jitter_factor: float = 0.3
    ):
        self._max_retries = max_retries
        self._initial_delay_ms = initial_delay_ms
        self._multiplier = multiplier
        self._max_delay_ms = max_delay_ms
        self._jitter_factor = jitter_factor

    def execute(self, action: Callable[[], T]) -> T:
        """Execute action with retries."""
        last_exception = None
        delay = self._initial_delay_ms
        
        for attempt in range(1, self._max_retries + 1):
            try:
                print(f"Attempt {attempt}/{self._max_retries}")
                return action()
            except Exception as e:
                last_exception = e
                print(f"Attempt {attempt} failed: {e}")
                
                if attempt < self._max_retries:
                    jitter = delay * self._jitter_factor * random.random()
                    sleep_time = min(delay + jitter, self._max_delay_ms)
                    print(f"Waiting {sleep_time:.0f}ms before retry")
                    time.sleep(sleep_time / 1000.0)
                    delay = delay * self._multiplier
        
        raise RuntimeError(f"All retries failed: {last_exception}")

    @classmethod
    def default_config(cls) -> 'RetryWithBackoff':
        return cls(
            max_retries=3,
            initial_delay_ms=100,
            multiplier=2.0,
            max_delay_ms=5000,
            jitter_factor=0.3
        )


if __name__ == "__main__":
    retry = RetryWithBackoff.default_config()
    
    attempt_counter = [0]
    
    def flaky_operation():
        attempt_counter[0] += 1
        if attempt_counter[0] < 3:
            raise RuntimeError("Transient failure")
        return f"Success on attempt {attempt_counter[0]}"
    
    try:
        result = retry.execute(flaky_operation)
        print(f"\nFinal result: {result}")
    except Exception as e:
        print(f"Failed: {e}")

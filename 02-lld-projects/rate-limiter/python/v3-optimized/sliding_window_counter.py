"""
Rate Limiter - V3 Optimized

Thread-safe Sliding Window Counter algorithm.
Memory efficient with O(1) space per client.
"""
import time
import threading
from dataclasses import dataclass
from rate_limit_config import (
    RateLimitAlgorithm, RateLimitConfig, RateLimitResult, ClientState
)


@dataclass
class CounterSnapshot:
    """Immutable snapshot of counter state."""
    previous_count: int
    current_count: int
    window_start: int


class SlidingWindowCounterState(ClientState):
    """Thread-safe state for Sliding Window Counter."""
    
    def __init__(self):
        self._created_at = int(time.time() * 1000)
        self._lock = threading.Lock()
        self._snapshot = CounterSnapshot(0, 0, self._created_at)

    def update_and_get(self, current_time_ms: int, window_size_ms: int) -> CounterSnapshot:
        """Update state for current time and return snapshot. Thread-safe."""
        with self._lock:
            window_end = self._snapshot.window_start + window_size_ms
            
            if current_time_ms >= window_end:
                # Calculate how many windows have passed
                windows_passed = (current_time_ms - self._snapshot.window_start) // window_size_ms
                
                if windows_passed == 1:
                    # Move to next window: current becomes previous
                    self._snapshot = CounterSnapshot(
                        self._snapshot.current_count,
                        0,
                        self._snapshot.window_start + window_size_ms
                    )
                else:
                    # Multiple windows passed: reset everything
                    new_window_start = self._snapshot.window_start + (windows_passed * window_size_ms)
                    self._snapshot = CounterSnapshot(0, 0, new_window_start)
            
            return self._snapshot

    def increment_current_count(self) -> None:
        """Increment current window count atomically."""
        with self._lock:
            self._snapshot = CounterSnapshot(
                self._snapshot.previous_count,
                self._snapshot.current_count + 1,
                self._snapshot.window_start
            )

    @property
    def created_at(self) -> int:
        return self._created_at

    @property
    def memory_usage(self) -> int:
        # Fixed size: 3 ints + overhead
        return 32


class SlidingWindowCounter(RateLimitAlgorithm):
    """
    Thread-safe Sliding Window Counter algorithm.
    Memory efficient with O(1) space per client.
    
    Algorithm:
    - Maintain count for current and previous window
    - Calculate weighted average based on window overlap
    - Approximate but accurate for practical use
    """
    
    ALGORITHM_NAME = "SlidingWindowCounter"

    @property
    def algorithm_name(self) -> str:
        return self.ALGORITHM_NAME

    def create_initial_state(self) -> ClientState:
        return SlidingWindowCounterState()

    def try_acquire(self, state: ClientState, config: RateLimitConfig) -> RateLimitResult:
        if not isinstance(state, SlidingWindowCounterState):
            raise ValueError("Invalid state type for SlidingWindowCounter")

        current_time_ms = int(time.time() * 1000)

        # Thread-safe state update
        snapshot = state.update_and_get(current_time_ms, config.window_size_ms)
        
        # Calculate weighted count
        weight = self._calculate_weight(current_time_ms, snapshot.window_start, 
                                         config.window_size_ms)
        estimated_count = snapshot.previous_count * weight + snapshot.current_count

        if estimated_count < config.max_requests:
            # Allow and increment
            state.increment_current_count()
            remaining = int(max(0, config.max_requests - estimated_count - 1))

            return RateLimitResult(
                allowed=True,
                remaining_requests=remaining,
                reset_time_ms=snapshot.window_start + config.window_size_ms,
                retry_after_ms=0,
                algorithm_used=self.ALGORITHM_NAME
            )
        else:
            # Reject
            reset_time_ms = snapshot.window_start + config.window_size_ms
            retry_after_ms = max(0, reset_time_ms - current_time_ms)

            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time_ms=reset_time_ms,
                retry_after_ms=retry_after_ms,
                algorithm_used=self.ALGORITHM_NAME
            )

    def get_remaining_requests(self, state: ClientState, config: RateLimitConfig) -> int:
        if not isinstance(state, SlidingWindowCounterState):
            return config.max_requests

        current_time_ms = int(time.time() * 1000)
        snapshot = state.update_and_get(current_time_ms, config.window_size_ms)
        weight = self._calculate_weight(current_time_ms, snapshot.window_start,
                                         config.window_size_ms)
        estimated_count = snapshot.previous_count * weight + snapshot.current_count

        return int(max(0, config.max_requests - estimated_count))

    def _calculate_weight(self, current_time_ms: int, window_start: int, 
                          window_size_ms: int) -> float:
        """
        Calculate weight for previous window based on overlap.
        Weight = portion of previous window that overlaps with our sliding window
        """
        # How much time has passed in current window
        elapsed_in_current_window = current_time_ms - window_start
        
        # Weight is portion of window size that extends into previous window
        weight = 1.0 - (elapsed_in_current_window / window_size_ms)
        
        return max(0.0, min(1.0, weight))

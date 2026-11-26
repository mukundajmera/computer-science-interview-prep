"""
Rate Limiter - V2 Extended

Sliding Window Log algorithm.
Stores exact timestamps of all requests within the window.
"""
import time
from collections import deque
from typing import Deque
from rate_limit_config import (
    RateLimitAlgorithm, RateLimitConfig, RateLimitResult, ClientState
)


class SlidingWindowLogState(ClientState):
    """State for Sliding Window Log algorithm."""
    
    def __init__(self):
        self._request_timestamps: Deque[int] = deque()
        self._created_at = int(time.time() * 1000)

    def add_request(self, timestamp: int) -> None:
        self._request_timestamps.append(timestamp)

    def remove_oldest(self) -> None:
        if self._request_timestamps:
            self._request_timestamps.popleft()

    @property
    def oldest_timestamp(self) -> int:
        return self._request_timestamps[0] if self._request_timestamps else 0

    @property
    def request_count(self) -> int:
        return len(self._request_timestamps)

    @property
    def is_empty(self) -> bool:
        return len(self._request_timestamps) == 0

    @property
    def created_at(self) -> int:
        return self._created_at

    @property
    def memory_usage(self) -> int:
        # Approximate: 8 bytes per timestamp
        return 8 * len(self._request_timestamps)


class SlidingWindowLog(RateLimitAlgorithm):
    """
    Sliding Window Log rate limiting algorithm.
    
    Properties:
    - Exact request counting
    - Memory usage proportional to request count
    - No burst allowance - strict limit
    """
    
    ALGORITHM_NAME = "SlidingWindowLog"

    @property
    def algorithm_name(self) -> str:
        return self.ALGORITHM_NAME

    def create_initial_state(self) -> ClientState:
        return SlidingWindowLogState()

    def try_acquire(self, state: ClientState, config: RateLimitConfig) -> RateLimitResult:
        if not isinstance(state, SlidingWindowLogState):
            raise ValueError("Invalid state type for SlidingWindowLog")

        current_time_ms = int(time.time() * 1000)
        window_start_ms = current_time_ms - config.window_size_ms

        # Remove timestamps outside the current window
        self._clean_old_entries(state, window_start_ms)

        current_count = state.request_count

        if current_count < config.max_requests:
            # Allow request - add timestamp
            state.add_request(current_time_ms)

            return RateLimitResult(
                allowed=True,
                remaining_requests=config.max_requests - current_count - 1,
                reset_time_ms=self._calculate_reset_time(state, config, current_time_ms),
                retry_after_ms=0,
                algorithm_used=self.ALGORITHM_NAME
            )
        else:
            # Reject - calculate when oldest request expires
            oldest_timestamp = state.oldest_timestamp
            retry_after_ms = oldest_timestamp + config.window_size_ms - current_time_ms

            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time_ms=oldest_timestamp + config.window_size_ms,
                retry_after_ms=max(0, retry_after_ms),
                algorithm_used=self.ALGORITHM_NAME
            )

    def get_remaining_requests(self, state: ClientState, config: RateLimitConfig) -> int:
        if not isinstance(state, SlidingWindowLogState):
            return config.max_requests

        current_time_ms = int(time.time() * 1000)
        window_start_ms = current_time_ms - config.window_size_ms
        self._clean_old_entries(state, window_start_ms)

        return max(0, config.max_requests - state.request_count)

    def _clean_old_entries(self, state: SlidingWindowLogState, window_start_ms: int) -> None:
        while not state.is_empty and state.oldest_timestamp < window_start_ms:
            state.remove_oldest()

    def _calculate_reset_time(self, state: SlidingWindowLogState, 
                              config: RateLimitConfig, current_time_ms: int) -> int:
        if state.is_empty:
            return current_time_ms + config.window_size_ms
        return state.oldest_timestamp + config.window_size_ms

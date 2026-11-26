"""
V2: Sliding Window Counter Rate Limiter

A more accurate rate limiter using sliding window counter algorithm.
Combines the accuracy of sliding window with low memory overhead.

Features:
- Per-user rate limiting
- Sliding window for accuracy
- Configurable limits
- Statistics tracking

Algorithm:
- Divide time into fixed windows
- Weight previous window by overlap percentage
- weighted_count = prev_count * overlap + current_count
"""

import time
import threading
from dataclasses import dataclass
from typing import Dict


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int
    limit: int
    retry_after_ms: int
    
    def __str__(self) -> str:
        return f"RateLimitResult(allowed={self.allowed}, remaining={self.remaining})"


@dataclass
class Stats:
    """Rate limiter statistics."""
    allowed: int = 0
    rejected: int = 0
    
    @property
    def acceptance_rate(self) -> float:
        total = self.allowed + self.rejected
        return 100.0 if total == 0 else (self.allowed * 100.0) / total
    
    def __str__(self) -> str:
        return f"Stats(allowed={self.allowed}, rejected={self.rejected}, rate={self.acceptance_rate:.1f}%)"


class UserWindow:
    """Window state for a single user."""
    
    def __init__(self, window_start: float):
        self.window_start = window_start
        self.prev_count = 0
        self.curr_count = 0


class SlidingWindowRateLimiter:
    """
    Sliding window counter rate limiter.
    
    Example:
        limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)
        
        result = limiter.try_acquire("user-123")
        if result.allowed:
            # Process request
        else:
            # Return 429 with Retry-After header
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Creates a sliding window rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Window size in seconds
        """
        self._max_requests = max_requests
        self._window_ms = window_seconds * 1000
        self._user_windows: Dict[str, UserWindow] = {}
        self._lock = threading.Lock()
        self._stats = Stats()
    
    def try_acquire(self, user_id: str) -> RateLimitResult:
        """
        Checks if a request should be allowed.
        
        Args:
            user_id: User identifier
            
        Returns:
            RateLimitResult with allowed status and metadata
        """
        now = time.time() * 1000  # Convert to ms
        
        with self._lock:
            window = self._user_windows.get(user_id)
            if window is None:
                window = UserWindow(now)
                self._user_windows[user_id] = window
            
            # Slide window if needed
            self._slide_window(window, now)
            
            # Calculate weighted count
            prev_weight = self._get_previous_window_weight(window, now)
            weighted_count = window.prev_count * prev_weight + window.curr_count
            
            if weighted_count < self._max_requests:
                window.curr_count += 1
                self._stats.allowed += 1
                return RateLimitResult(
                    allowed=True,
                    remaining=int(self._max_requests - weighted_count - 1),
                    limit=self._max_requests,
                    retry_after_ms=0
                )
            else:
                self._stats.rejected += 1
                retry_after = int(prev_weight * self._window_ms)
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    limit=self._max_requests,
                    retry_after_ms=retry_after
                )
    
    def _slide_window(self, window: UserWindow, now: float) -> None:
        """Slides the window forward if current window has passed."""
        elapsed = now - window.window_start
        
        if elapsed >= self._window_ms * 2:
            # Both windows expired
            window.window_start = now
            window.prev_count = 0
            window.curr_count = 0
        elif elapsed >= self._window_ms:
            # Previous window expired
            window.window_start = window.window_start + self._window_ms
            window.prev_count = window.curr_count
            window.curr_count = 0
    
    def _get_previous_window_weight(self, window: UserWindow, now: float) -> float:
        """Gets the weight of the previous window based on overlap."""
        elapsed_in_window = now - window.window_start
        return max(0.0, 1.0 - (elapsed_in_window / self._window_ms))
    
    @property
    def stats(self) -> Stats:
        """Returns statistics."""
        return self._stats


# ============ Demo ============

def main():
    print("=== Sliding Window Rate Limiter Demo ===\n")
    
    # Demo 1: Basic per-user limiting
    print("1. Per-User Rate Limiting:")
    per_user_demo()
    
    # Demo 2: Multiple users
    print("\n2. Multiple Users:")
    multi_user_demo()
    
    # Demo 3: Window sliding
    print("\n3. Window Sliding Behavior:")
    window_sliding_demo()
    
    print("\n=== Demo Complete ===")


def per_user_demo():
    # 5 requests per 10 seconds
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)
    
    user_id = "user-123"
    
    for i in range(1, 9):
        result = limiter.try_acquire(user_id)
        print(f"   Request {i}: {'ALLOWED' if result.allowed else 'REJECTED'}, "
              f"remaining: {result.remaining}")
    
    print(f"   {limiter.stats}")


def multi_user_demo():
    # 3 requests per 10 seconds per user
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10)
    
    users = ["alice", "bob", "charlie"]
    
    for user in users:
        for i in range(1, 6):
            result = limiter.try_acquire(user)
            print(f"   {user} request {i}: {'OK' if result.allowed else 'BLOCKED'}")
    
    print(f"   {limiter.stats}")


def window_sliding_demo():
    # 5 requests per 2 seconds
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=2)
    
    user_id = "user-456"
    
    # Use up all tokens
    print("   Initial burst:")
    for i in range(1, 6):
        result = limiter.try_acquire(user_id)
        print(f"   Request {i}: {'OK' if result.allowed else 'BLOCKED'}")
    
    # Next request should be blocked
    result = limiter.try_acquire(user_id)
    print(f"   Request 6: {'OK' if result.allowed else 'BLOCKED'}")
    
    # Wait 1 second (half window)
    print("\n   Waiting 1 second (half window)...")
    time.sleep(1)
    
    result = limiter.try_acquire(user_id)
    print(f"   Request 7: {'OK' if result.allowed else 'BLOCKED'} "
          "(sliding window allows partial recovery)")
    
    # Wait another 1.5 seconds
    print("\n   Waiting 1.5 more seconds...")
    time.sleep(1.5)
    
    for i in range(3):
        result = limiter.try_acquire(user_id)
        print(f"   Request: {'OK' if result.allowed else 'BLOCKED'}")


if __name__ == "__main__":
    main()

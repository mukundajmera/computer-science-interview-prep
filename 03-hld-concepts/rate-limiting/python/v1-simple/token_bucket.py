"""
V1: Simple Token Bucket Rate Limiter

A basic implementation of the token bucket algorithm.
Allows bursting up to bucket capacity while maintaining
average rate over time.

Features:
- Configurable capacity and refill rate
- Thread-safe
- Simple API

Limitations:
- Single user only
- Not distributed
"""

import time
import threading



class TokenBucketRateLimiter:
    """
    Token bucket rate limiter.
    
    Example:
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate_per_second=2)
        
        if limiter.try_acquire():
            # Process request
        else:
            # Return 429 Too Many Requests
    """
    
    def __init__(self, capacity: int, refill_rate_per_second: float):
        """
        Creates a token bucket rate limiter.
        
        Args:
            capacity: Maximum tokens (burst size)
            refill_rate_per_second: Tokens added per second
        """
        self._capacity = capacity
        self._refill_rate = refill_rate_per_second
        self._tokens = float(capacity)  # Start full
        self._last_refill_time = time.time()
        self._lock = threading.Lock()
    
    def try_acquire(self, tokens_needed: int = 1) -> bool:
        """
        Attempts to consume tokens.
        
        Args:
            tokens_needed: Number of tokens to consume
            
        Returns:
            True if request allowed, False if rate limited
        """
        with self._lock:
            self._refill()
            
            if self._tokens >= tokens_needed:
                self._tokens -= tokens_needed
                return True
            
            return False
    
    def _refill(self) -> None:
        """Refills tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill_time
        
        tokens_to_add = elapsed * self._refill_rate
        self._tokens = min(self._capacity, self._tokens + tokens_to_add)
        self._last_refill_time = now
    
    @property
    def available_tokens(self) -> float:
        """Returns current token count."""
        with self._lock:
            self._refill()
            return self._tokens
    
    def get_wait_time_seconds(self) -> float:
        """Returns time until next token is available."""
        with self._lock:
            self._refill()
            if self._tokens >= 1:
                return 0
            return (1 - self._tokens) / self._refill_rate


# ============ Demo ============

def main():
    print("=== Token Bucket Rate Limiter Demo ===\n")
    
    # Demo 1: Basic usage
    print("1. Basic Usage (10 tokens, 2 per second refill):")
    basic_usage_demo()
    
    # Demo 2: Burst handling
    print("\n2. Burst Handling:")
    burst_demo()
    
    # Demo 3: Sustained rate
    print("\n3. Sustained Rate:")
    sustained_rate_demo()
    
    print("\n=== Demo Complete ===")


def basic_usage_demo():
    limiter = TokenBucketRateLimiter(capacity=10, refill_rate_per_second=2)
    
    # Make 15 requests quickly
    for i in range(1, 16):
        allowed = limiter.try_acquire()
        print(f"   Request {i}: {'ALLOWED' if allowed else 'REJECTED'} "
              f"(tokens: {limiter.available_tokens:.1f})")
    
    # Wait for refill
    print("   Waiting 2 seconds...")
    time.sleep(2)
    
    allowed = limiter.try_acquire()
    print(f"   After wait: {'ALLOWED' if allowed else 'REJECTED'} "
          f"(tokens: {limiter.available_tokens:.1f})")


def burst_demo():
    # High capacity allows bursts
    limiter = TokenBucketRateLimiter(capacity=100, refill_rate_per_second=10)
    
    # Simulate burst of 50 requests
    allowed = sum(1 for _ in range(50) if limiter.try_acquire())
    
    print(f"   Burst of 50 requests: {allowed} allowed")
    print(f"   Remaining tokens: {limiter.available_tokens:.1f}")


def sustained_rate_demo():
    # 5 requests per second sustained
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_second=5)
    
    total_allowed = 0
    total_rejected = 0
    
    start_time = time.time()
    
    # Try 50 requests over 5 seconds (10 per second attempted)
    for _ in range(5):
        for _ in range(10):
            if limiter.try_acquire():
                total_allowed += 1
            else:
                total_rejected += 1
        time.sleep(1)
    
    elapsed = time.time() - start_time
    
    print(f"   Duration: {elapsed:.1f} seconds")
    print(f"   Total allowed: {total_allowed} (expected ~25)")
    print(f"   Total rejected: {total_rejected}")
    print(f"   Effective rate: {total_allowed / elapsed:.1f} req/sec")


if __name__ == "__main__":
    main()

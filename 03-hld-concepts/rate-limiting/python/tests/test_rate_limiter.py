"""
Unit Tests for Rate Limiter Implementations
"""

import unittest
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))


class TestTokenBucketRateLimiter(unittest.TestCase):
    """Tests for TokenBucketRateLimiter."""
    
    def test_allows_up_to_capacity(self):
        """Should allow requests up to capacity."""
        from token_bucket import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_second=1)
        
        for _ in range(5):
            self.assertTrue(limiter.try_acquire())
        
        self.assertFalse(limiter.try_acquire())  # 6th should fail
    
    def test_refills_over_time(self):
        """Should refill tokens over time."""
        from token_bucket import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter(capacity=1, refill_rate_per_second=10)
        
        self.assertTrue(limiter.try_acquire())
        self.assertFalse(limiter.try_acquire())
        
        time.sleep(0.15)  # Wait for refill
        
        self.assertTrue(limiter.try_acquire())
    
    def test_burst(self):
        """Should allow bursting up to capacity."""
        from token_bucket import TokenBucketRateLimiter
        
        limiter = TokenBucketRateLimiter(capacity=100, refill_rate_per_second=1)
        
        allowed = sum(1 for _ in range(100) if limiter.try_acquire())
        
        self.assertEqual(allowed, 100)


class TestSlidingWindowRateLimiter(unittest.TestCase):
    """Tests for SlidingWindowRateLimiter."""
    
    def test_per_user_limiting(self):
        """Should limit per user."""
        from sliding_window import SlidingWindowRateLimiter
        
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
        
        for _ in range(5):
            self.assertTrue(limiter.try_acquire("user1").allowed)
        
        self.assertFalse(limiter.try_acquire("user1").allowed)
        self.assertTrue(limiter.try_acquire("user2").allowed)  # Different user
    
    def test_remaining_count(self):
        """Should return correct remaining count."""
        from sliding_window import SlidingWindowRateLimiter
        
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
        
        self.assertEqual(limiter.try_acquire("user").remaining, 4)
        self.assertEqual(limiter.try_acquire("user").remaining, 3)
        self.assertEqual(limiter.try_acquire("user").remaining, 2)
    
    def test_stats_tracking(self):
        """Should track statistics."""
        from sliding_window import SlidingWindowRateLimiter
        
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
        
        limiter.try_acquire("user")
        limiter.try_acquire("user")
        limiter.try_acquire("user")  # Rejected
        
        self.assertEqual(limiter.stats.allowed, 2)
        self.assertEqual(limiter.stats.rejected, 1)


class TestDistributedRateLimiter(unittest.TestCase):
    """Tests for DistributedRateLimiter."""
    
    def test_tier_limits(self):
        """Should respect tier limits."""
        from distributed_limiter import (
            DistributedRateLimiter, InMemoryRateLimitStore, TierConfig
        )
        
        store = InMemoryRateLimitStore()
        limiter = DistributedRateLimiter(store)
        limiter.add_tier(TierConfig("test", 3, 60, 1))
        
        for _ in range(3):
            self.assertTrue(limiter.check_rate_limit("user", "test").allowed)
        
        self.assertFalse(limiter.check_rate_limit("user", "test").allowed)
    
    def test_headers(self):
        """Should return proper headers."""
        from distributed_limiter import DistributedRateLimiter, InMemoryRateLimitStore
        
        store = InMemoryRateLimitStore()
        limiter = DistributedRateLimiter(store)
        
        result = limiter.check_rate_limit("user", "free")
        headers = result.get_headers()
        
        self.assertIn("X-RateLimit-Limit", headers)
        self.assertIn("X-RateLimit-Remaining", headers)
    
    def test_metrics(self):
        """Should track metrics."""
        from distributed_limiter import (
            DistributedRateLimiter, InMemoryRateLimitStore, TierConfig
        )
        
        store = InMemoryRateLimitStore()
        limiter = DistributedRateLimiter(store)
        limiter.add_tier(TierConfig("test", 2, 60, 1))
        
        limiter.check_rate_limit("user", "test")  # allowed
        limiter.check_rate_limit("user", "test")  # allowed
        limiter.check_rate_limit("user", "test")  # rejected
        
        self.assertEqual(limiter.metrics.total_requests, 3)
        self.assertEqual(limiter.metrics.allowed_requests, 2)
        self.assertEqual(limiter.metrics.rejected_requests, 1)


if __name__ == '__main__':
    unittest.main()

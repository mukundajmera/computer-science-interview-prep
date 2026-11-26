"""
Rate Limiter - V2 Extended

Factory for creating rate limiters with different algorithms.
"""
from rate_limit_config import RateLimitConfig
from rate_limiter import RateLimiter
from token_bucket import TokenBucket
from sliding_window_log import SlidingWindowLog


class RateLimiterFactory:
    """Factory for creating rate limiters."""

    @staticmethod
    def create_token_bucket_limiter(config: RateLimitConfig) -> RateLimiter:
        """
        Create a rate limiter using Token Bucket algorithm.
        
        Best for: APIs that want to allow bursts up to capacity
        """
        return RateLimiter(TokenBucket(), config)

    @staticmethod
    def create_sliding_window_log_limiter(config: RateLimitConfig) -> RateLimiter:
        """
        Create a rate limiter using Sliding Window Log algorithm.
        
        Best for: Exact rate limiting with no burst allowance
        Note: Higher memory usage - stores all request timestamps
        """
        return RateLimiter(SlidingWindowLog(), config)

    @staticmethod
    def per_second(requests_per_second: int) -> RateLimiter:
        """Create a rate limiter for a specific number of requests per second."""
        config = RateLimitConfig.per_second(requests_per_second)
        return RateLimiterFactory.create_token_bucket_limiter(config)

    @staticmethod
    def per_minute(requests_per_minute: int) -> RateLimiter:
        """Create a rate limiter for a specific number of requests per minute."""
        config = RateLimitConfig.per_minute(requests_per_minute)
        return RateLimiterFactory.create_token_bucket_limiter(config)

"""
Rate Limiter - V1 Basic

Token Bucket algorithm implementation.
Simple rate limiting with configurable bucket size and refill rate.
"""
from dataclasses import dataclass


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining_tokens: int
    reset_time_ms: int

    def __str__(self) -> str:
        return f"RateLimitResult(allowed={self.allowed}, remaining={self.remaining_tokens}, reset_ms={self.reset_time_ms})"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    bucket_capacity: int
    refill_rate_per_ms: float

    @classmethod
    def per_second(cls, requests_per_second: int) -> 'RateLimitConfig':
        """Create a config for X requests per second."""
        return cls(
            bucket_capacity=requests_per_second,
            refill_rate_per_ms=requests_per_second / 1000.0
        )

    @classmethod
    def per_minute(cls, requests_per_minute: int) -> 'RateLimitConfig':
        """Create a config for X requests per minute."""
        burst_capacity = max(1, requests_per_minute // 60)
        return cls(
            bucket_capacity=burst_capacity,
            refill_rate_per_ms=requests_per_minute / 60000.0
        )

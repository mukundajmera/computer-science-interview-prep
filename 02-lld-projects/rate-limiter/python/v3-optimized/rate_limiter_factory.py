"""
Rate Limiter - V3 Optimized

Factory helpers for constructing illustrative limiter variants.
"""
from typing import Optional

from rate_limit_config import RateLimitConfig
from rate_limiter import DistributedQuotaStore, RateLimiter


class RateLimiterFactory:
    """Factory for creating rate limiters."""

    @staticmethod
    def create_sliding_window_counter_limiter(
        config: RateLimitConfig,
        enable_cleanup: bool = True,
        quota_store: Optional[DistributedQuotaStore] = None,
    ) -> RateLimiter:
        """
        Keeps API compatibility with existing callers.

        `enable_cleanup` is accepted for signature compatibility but not used
        in this illustrative skeleton.
        """
        _ = enable_cleanup
        return RateLimiter(config=config, quota_store=quota_store)

    @staticmethod
    def per_second(
        requests_per_second: int,
        quota_store: Optional[DistributedQuotaStore] = None,
    ) -> RateLimiter:
        config = RateLimitConfig.per_second(requests_per_second)
        return RateLimiterFactory.create_sliding_window_counter_limiter(
            config=config,
            quota_store=quota_store,
        )

    @staticmethod
    def per_minute(
        requests_per_minute: int,
        quota_store: Optional[DistributedQuotaStore] = None,
    ) -> RateLimiter:
        config = RateLimitConfig.per_minute(requests_per_minute)
        return RateLimiterFactory.create_sliding_window_counter_limiter(
            config=config,
            quota_store=quota_store,
        )

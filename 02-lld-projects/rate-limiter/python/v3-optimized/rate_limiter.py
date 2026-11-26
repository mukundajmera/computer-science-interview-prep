"""
Rate Limiter - V3 Optimized (illustrative)

Supports local token bucket limiting and optional distributed quota delegation.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Protocol
import time

from rate_limit_config import RateLimitConfig, RateLimitResult
from token_bucket import TokenBucket, TokenBucketState


@dataclass(frozen=True)
class QuotaDecision:
    allowed: bool
    remaining_tokens: int
    reset_time_ms: int


class DistributedQuotaStore(Protocol):
    """External quota store abstraction for distributed enforcement."""

    def consume(
        self, client_key: str, max_requests: int, window_size_ms: int, now_ms: int
    ) -> QuotaDecision:
        ...

    def peek(
        self, client_key: str, max_requests: int, window_size_ms: int, now_ms: int
    ) -> QuotaDecision:
        ...


class RateLimiter:
    """Rate limiter using local token bucket plus optional distributed store."""

    def __init__(
        self,
        config: RateLimitConfig,
        quota_store: Optional[DistributedQuotaStore] = None,
    ):
        self._config = config
        self._quota_store = quota_store
        self._algorithm = TokenBucket(config)
        self._client_states: Dict[str, TokenBucketState] = {}

    def allow_request(self, client_key: str) -> RateLimitResult:
        if not client_key:
            raise ValueError("Client key cannot be null or empty")

        if self._quota_store is not None:
            now_ms = int(time.time() * 1000)
            decision = self._quota_store.consume(
                client_key,
                self._config.bucket_capacity,
                self._default_window_size_ms(),
                now_ms,
            )
            return RateLimitResult(
                allowed=decision.allowed,
                remaining_tokens=decision.remaining_tokens,
                reset_time_ms=decision.reset_time_ms,
            )

        state = self._get_or_create_state(client_key)
        return self._algorithm.try_acquire(state)

    def get_remaining_requests(self, client_key: str) -> int:
        if self._quota_store is not None:
            now_ms = int(time.time() * 1000)
            decision = self._quota_store.peek(
                client_key,
                self._config.bucket_capacity,
                self._default_window_size_ms(),
                now_ms,
            )
            return decision.remaining_tokens

        state = self._client_states.get(client_key)
        if state is None:
            return self._algorithm.get_remaining_tokens(
                self._algorithm.create_initial_state()
            )
        return self._algorithm.get_remaining_tokens(state)

    def reset_client(self, client_key: str) -> None:
        self._client_states.pop(client_key, None)

    def _get_or_create_state(self, client_key: str) -> TokenBucketState:
        if client_key not in self._client_states:
            self._client_states[client_key] = self._algorithm.create_initial_state()
        return self._client_states[client_key]

    def _default_window_size_ms(self) -> int:
        if self._config.refill_rate_per_ms <= 0:
            return 1000
        return max(1, int(self._config.bucket_capacity / self._config.refill_rate_per_ms))

    @property
    def client_count(self) -> int:
        return len(self._client_states)

"""
Rate Limiter - V1 Basic

Main rate limiter class using Token Bucket algorithm.
Simple implementation for single-threaded use.
"""
from typing import Dict
from rate_limit_config import RateLimitConfig, RateLimitResult
from token_bucket import TokenBucket, TokenBucketState


class RateLimiter:
    """Rate limiter using Token Bucket algorithm."""
    
    def __init__(self, config: RateLimitConfig):
        self._algorithm = TokenBucket(config)
        self._client_states: Dict[str, TokenBucketState] = {}

    def allow_request(self, client_key: str) -> RateLimitResult:
        """
        Check if a request from the given client should be allowed.
        
        Args:
            client_key: Unique identifier for the client (user ID, IP, API key)
            
        Returns:
            RateLimitResult indicating if request is allowed
        """
        if not client_key:
            raise ValueError("Client key cannot be null or empty")

        state = self._get_or_create_state(client_key)
        return self._algorithm.try_acquire(state)

    def get_remaining_requests(self, client_key: str) -> int:
        """Get remaining requests for a client without consuming quota."""
        state = self._client_states.get(client_key)
        if state is None:
            return self._algorithm.get_remaining_tokens(
                self._algorithm.create_initial_state()
            )
        return self._algorithm.get_remaining_tokens(state)

    def reset_client(self, client_key: str) -> None:
        """Reset rate limit state for a client."""
        self._client_states.pop(client_key, None)

    def _get_or_create_state(self, client_key: str) -> TokenBucketState:
        """Get or create state for a client."""
        if client_key not in self._client_states:
            self._client_states[client_key] = self._algorithm.create_initial_state()
        return self._client_states[client_key]

    @property
    def client_count(self) -> int:
        """Get the number of tracked clients."""
        return len(self._client_states)

"""
Rate Limiter - V1 Basic

Token Bucket algorithm - core implementation.
Tokens are added at a constant rate and consumed by requests.
"""
import time
from rate_limit_config import RateLimitConfig, RateLimitResult


class TokenBucketState:
    """State for a single client's token bucket."""
    
    def __init__(self, initial_tokens: float):
        self.tokens = initial_tokens
        self.last_refill_time_ms = int(time.time() * 1000)


class TokenBucket:
    """
    Token Bucket rate limiting algorithm.
    
    Properties:
    - Allows burst up to bucket capacity
    - Smooth rate limiting over time
    - O(1) time and space per operation
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config

    def create_initial_state(self) -> TokenBucketState:
        """Create initial state for a new client."""
        return TokenBucketState(self.config.bucket_capacity)

    def _refill_tokens(self, state: TokenBucketState, current_time_ms: int) -> None:
        """Refill tokens based on elapsed time."""
        elapsed_ms = current_time_ms - state.last_refill_time_ms
        
        if elapsed_ms > 0:
            tokens_to_add = elapsed_ms * self.config.refill_rate_per_ms
            new_tokens = min(
                self.config.bucket_capacity,
                state.tokens + tokens_to_add
            )
            state.tokens = new_tokens
            state.last_refill_time_ms = current_time_ms

    def try_acquire(self, state: TokenBucketState) -> RateLimitResult:
        """Try to acquire a token for a request."""
        current_time_ms = int(time.time() * 1000)
        
        # Refill tokens based on elapsed time
        self._refill_tokens(state, current_time_ms)
        
        if state.tokens >= 1.0:
            # Consume a token
            state.tokens -= 1.0
            
            return RateLimitResult(
                allowed=True,
                remaining_tokens=int(state.tokens),
                reset_time_ms=self._calculate_reset_time(current_time_ms)
            )
        else:
            # No tokens available
            wait_time_ms = int((1.0 - state.tokens) / self.config.refill_rate_per_ms)
            
            return RateLimitResult(
                allowed=False,
                remaining_tokens=0,
                reset_time_ms=current_time_ms + wait_time_ms
            )

    def get_remaining_tokens(self, state: TokenBucketState) -> int:
        """Get remaining tokens without consuming."""
        current_time_ms = int(time.time() * 1000)
        self._refill_tokens(state, current_time_ms)
        return int(state.tokens)

    def _calculate_reset_time(self, current_time_ms: int) -> int:
        """Calculate when bucket would be full."""
        return current_time_ms + int(self.config.bucket_capacity / self.config.refill_rate_per_ms)

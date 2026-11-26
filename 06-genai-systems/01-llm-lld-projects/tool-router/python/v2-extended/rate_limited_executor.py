import time
from typing import Dict, Any, Callable
from threading import Lock

class RateLimitedExecutor:
    """Executes tools with token-bucket and rate-limiting."""

    def __init__(self, capacity: int, fill_rate: float):
        """
        capacity: Maximum tokens in the bucket.
        fill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens = capacity
        self.last_fill = time.time()
        self.lock = Lock()

    def _consume_tokens(self, tokens_needed: int) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_fill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
            self.last_fill = now

            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False

    def execute(self, tool_name: str, handler: Callable[[Dict[str, Any]], Any], args: Dict[str, Any], cost: int = 1) -> Any:
        """
        Executes the handler if enough tokens are available.
        Raises RateLimitExceeded if not enough tokens.
        """
        if not self._consume_tokens(cost):
            raise RateLimitExceeded(f"Rate limit exceeded for tool {tool_name}")

        return handler(args)

class RateLimitExceeded(Exception):
    pass

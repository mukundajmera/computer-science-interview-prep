"""
URL Shortener - V2 Scaled

Key Generation Service (KGS) for distributed unique ID generation.
Rate limiter for API protection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Set
import threading
import random
import string
import time


class KeyRepository(ABC):
    """Repository for key pool management."""
    
    @abstractmethod
    def get_unused_keys(self, count: int) -> List[str]:
        """Get batch of unused keys."""
        pass
    
    @abstractmethod
    def mark_as_used(self, short_code: str) -> None:
        """Mark a key as used."""
        pass
    
    @abstractmethod
    def add_keys(self, keys: List[str]) -> None:
        """Add new keys to the pool."""
        pass
    
    @abstractmethod
    def get_unused_key_count(self) -> int:
        """Get count of unused keys."""
        pass


class InMemoryKeyRepository(KeyRepository):
    """In-memory key repository for testing."""
    
    BASE62_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
    
    def __init__(self):
        self._unused_keys: List[str] = []
        self._used_keys: Set[str] = set()
        self._lock = threading.Lock()
        
        # Pre-populate
        self._generate_initial_keys(10000)
    
    def _generate_initial_keys(self, count: int) -> None:
        """Generate random keys."""
        for _ in range(count):
            key = ''.join(random.choices(self.BASE62_CHARS, k=7))
            if key not in self._used_keys and key not in self._unused_keys:
                self._unused_keys.append(key)
    
    def get_unused_keys(self, count: int) -> List[str]:
        with self._lock:
            result = []
            for _ in range(count):
                if not self._unused_keys:
                    self._generate_initial_keys(count * 2)
                if self._unused_keys:
                    result.append(self._unused_keys.pop())
            return result
    
    def mark_as_used(self, short_code: str) -> None:
        with self._lock:
            self._used_keys.add(short_code)
    
    def add_keys(self, keys: List[str]) -> None:
        with self._lock:
            for key in keys:
                if key not in self._used_keys:
                    self._unused_keys.append(key)
    
    def get_unused_key_count(self) -> int:
        return len(self._unused_keys)


class KeyGenerationService:
    """
    Key Generation Service for pre-generating unique short codes.
    Eliminates collision detection at runtime.
    """
    
    BATCH_SIZE = 1000
    REFILL_THRESHOLD = 100
    
    def __init__(self, key_repository: KeyRepository):
        self._key_repository = key_repository
        self._local_pool: List[str] = []
        self._lock = threading.Lock()
        
        # Initial fill
        self._refill_local_pool()
    
    def generate(self) -> str:
        """Generate a unique short code."""
        with self._lock:
            if len(self._local_pool) < self.REFILL_THRESHOLD:
                self._refill_local_pool()
            
            if not self._local_pool:
                self._refill_local_pool()
            
            if self._local_pool:
                key = self._local_pool.pop()
                self._key_repository.mark_as_used(key)
                return key
            
            raise RuntimeError("No keys available")
    
    def is_valid_custom_alias(self, alias: str) -> bool:
        """Validate custom alias format."""
        if not alias or len(alias) < 3 or len(alias) > 20:
            return False
        
        for char in alias:
            if not (char.isalnum() or char in '-_'):
                return False
        
        return not alias.startswith('-') and not alias.endswith('-')
    
    def _refill_local_pool(self) -> None:
        """Refill local pool from repository."""
        batch = self._key_repository.get_unused_keys(self.BATCH_SIZE)
        self._local_pool.extend(batch)
    
    def get_pool_size(self) -> int:
        """Get current pool size."""
        return len(self._local_pool)


class RateLimiter(ABC):
    """Rate limiter interface."""
    
    @abstractmethod
    def allow_request(self, key: str) -> bool:
        """Check if request should be allowed."""
        pass
    
    @abstractmethod
    def get_remaining_tokens(self, key: str) -> int:
        """Get remaining tokens for a key."""
        pass


@dataclass
class Bucket:
    """Token bucket for rate limiting."""
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float
    
    def try_consume(self) -> bool:
        """Try to consume a token."""
        self._refill()
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
    
    def get_tokens(self) -> int:
        """Get current token count."""
        self._refill()
        return int(self.tokens)
    
    def _refill(self) -> None:
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now


class TokenBucketRateLimiter(RateLimiter):
    """Token Bucket rate limiter implementation."""
    
    def __init__(self, bucket_capacity: int, refill_rate: float):
        self._bucket_capacity = bucket_capacity
        self._refill_rate = refill_rate
        self._buckets: dict = {}
        self._lock = threading.Lock()
    
    def allow_request(self, key: str) -> bool:
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = Bucket(
                    capacity=self._bucket_capacity,
                    refill_rate=self._refill_rate,
                    tokens=float(self._bucket_capacity),
                    last_refill=time.time()
                )
            
            return self._buckets[key].try_consume()
    
    def get_remaining_tokens(self, key: str) -> int:
        with self._lock:
            bucket = self._buckets.get(key)
            return bucket.get_tokens() if bucket else self._bucket_capacity


class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window rate limiter for more accurate limiting."""
    
    def __init__(self, max_requests: int, window_size_seconds: float):
        self._max_requests = max_requests
        self._window_size_ms = window_size_seconds * 1000
        self._request_logs: dict = {}
        self._lock = threading.Lock()
    
    def allow_request(self, key: str) -> bool:
        with self._lock:
            now = time.time() * 1000
            window_start = now - self._window_size_ms
            
            if key not in self._request_logs:
                self._request_logs[key] = []
            
            log = self._request_logs[key]
            
            # Remove expired entries
            log[:] = [ts for ts in log if ts >= window_start]
            
            if len(log) < self._max_requests:
                log.append(now)
                return True
            
            return False
    
    def get_remaining_tokens(self, key: str) -> int:
        with self._lock:
            log = self._request_logs.get(key, [])
            now = time.time() * 1000
            window_start = now - self._window_size_ms
            
            valid_count = sum(1 for ts in log if ts >= window_start)
            return max(0, self._max_requests - valid_count)

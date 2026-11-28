"""
V3: Production-Ready Distributed Rate Limiter

A production-grade rate limiter with:
- Multi-tier limits (per user, per endpoint, global)
- Redis-like storage abstraction
- Tiered rate limits (free, premium, enterprise)
- Comprehensive metrics
- HTTP headers support

This demonstrates patterns used in production API gateways
like Kong, AWS API Gateway, and Stripe.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol
from collections import defaultdict


class RateLimitStore(Protocol):
    """Storage interface for rate limit data."""
    
    def increment(self, key: str, window_ms: int) -> tuple[int, int]:
        """
        Increments counter and returns (new_count, ttl_ms).
        Should be atomic operation.
        """
        ...
    
    def get_count(self, key: str) -> int:
        """Gets current count for a key."""
        ...


@dataclass
class TierConfig:
    """Configuration for a rate limit tier."""
    name: str
    requests_per_window: int
    window_seconds: int
    burst_capacity: int = 0
    
    @property
    def window_ms(self) -> int:
        return self.window_seconds * 1000


@dataclass
class RateLimitDecision:
    """Rate limit decision."""
    allowed: bool
    tier: str
    limit: int
    remaining: int
    reset_ms: int
    retry_after_ms: int
    limited_by: Optional[str] = None  # Which limit was hit
    
    def get_headers(self) -> Dict[str, str]:
        """Returns HTTP headers for rate limit response."""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(0, self.remaining)),
            "X-RateLimit-Reset": str(int(time.time() * 1000) + self.reset_ms),
        }
        if not self.allowed:
            headers["Retry-After"] = str(self.retry_after_ms // 1000)
        return headers


@dataclass
class Metrics:
    """Rate limiter metrics."""
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    rejections_by_tier: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    rejections_by_user: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def record_allowed(self) -> None:
        with self._lock:
            self.total_requests += 1
            self.allowed_requests += 1
    
    def record_rejected(self, tier: str, user_id: str) -> None:
        with self._lock:
            self.total_requests += 1
            self.rejected_requests += 1
            self.rejections_by_tier[tier] += 1
            self.rejections_by_user[user_id] += 1
    
    @property
    def acceptance_rate(self) -> float:
        if self.total_requests == 0:
            return 100.0
        return (self.allowed_requests * 100.0) / self.total_requests
    
    def __str__(self) -> str:
        return (f"Metrics(total={self.total_requests}, allowed={self.allowed_requests}, "
                f"rejected={self.rejected_requests}, rate={self.acceptance_rate:.1f}%)")


class InMemoryRateLimitStore:
    """
    In-memory implementation of RateLimitStore.
    In production, replace with Redis implementation.
    """
    
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._expiries: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def increment(self, key: str, window_ms: int) -> tuple[int, int]:
        with self._lock:
            now = time.time() * 1000
            
            # Check if key expired
            expiry = self._expiries.get(key)
            if expiry is not None and now > expiry:
                del self._counters[key]
                del self._expiries[key]
            
            # Increment counter
            if key not in self._counters:
                self._counters[key] = 0
                self._expiries[key] = now + window_ms
            
            self._counters[key] += 1
            count = self._counters[key]
            ttl = max(0, int(self._expiries.get(key, now + window_ms) - now))
            
            return count, ttl
    
    def get_count(self, key: str) -> int:
        return self._counters.get(key, 0)


class DistributedRateLimiter:
    """
    Production-ready distributed rate limiter.
    
    Example:
        store = InMemoryRateLimitStore()  # Or RedisRateLimitStore
        limiter = DistributedRateLimiter(store)
        
        decision = limiter.check_rate_limit("user-123", "premium")
        if decision.allowed:
            # Process request
        else:
            # Return 429 with headers
            headers = decision.get_headers()
    """
    
    DEFAULT_TIERS = {
        "free": TierConfig("free", 100, 60, 10),
        "basic": TierConfig("basic", 500, 60, 50),
        "premium": TierConfig("premium", 2000, 60, 200),
        "enterprise": TierConfig("enterprise", 10000, 60, 1000),
    }
    
    def __init__(self, store: RateLimitStore):
        self._store = store
        self._tiers: Dict[str, TierConfig] = dict(self.DEFAULT_TIERS)
        self._metrics = Metrics()
    
    def add_tier(self, config: TierConfig) -> None:
        """Adds or updates a rate limit tier."""
        self._tiers[config.name] = config
    
    def check_rate_limit(
        self,
        user_id: str,
        tier_name: str,
        endpoint: Optional[str] = None
    ) -> RateLimitDecision:
        """
        Checks rate limit for a request.
        
        Args:
            user_id: User identifier
            tier_name: Tier name (free, premium, etc.)
            endpoint: Optional endpoint for per-endpoint limits
            
        Returns:
            Decision with allowed status and headers
        """
        tier = self._tiers.get(tier_name, self._tiers["free"])
        
        now = time.time() * 1000
        window_start = now - (now % tier.window_ms)
        
        # Check per-user limit
        user_key = f"rate:{tier_name}:{user_id}:{int(window_start)}"
        count, ttl = self._store.increment(user_key, tier.window_ms)
        
        if count > tier.requests_per_window:
            self._metrics.record_rejected(tier_name, user_id)
            return RateLimitDecision(
                allowed=False,
                tier=tier_name,
                limit=tier.requests_per_window,
                remaining=0,
                reset_ms=ttl,
                retry_after_ms=ttl,
                limited_by="user"
            )
        
        # Optional: Check per-endpoint limit
        if endpoint:
            endpoint_key = f"rate:{tier_name}:endpoint:{endpoint}:{int(window_start)}"
            ep_count, ep_ttl = self._store.increment(endpoint_key, tier.window_ms)
            
            endpoint_limit = tier.requests_per_window * 10
            if ep_count > endpoint_limit:
                self._metrics.record_rejected(tier_name, user_id)
                return RateLimitDecision(
                    allowed=False,
                    tier=tier_name,
                    limit=endpoint_limit,
                    remaining=0,
                    reset_ms=ep_ttl,
                    retry_after_ms=ep_ttl,
                    limited_by="endpoint"
                )
        
        self._metrics.record_allowed()
        return RateLimitDecision(
            allowed=True,
            tier=tier_name,
            limit=tier.requests_per_window,
            remaining=tier.requests_per_window - count,
            reset_ms=ttl,
            retry_after_ms=0
        )
    
    @property
    def metrics(self) -> Metrics:
        return self._metrics


# ============ Demo ============

def main():
    import random
    
    print("=== Production Rate Limiter Demo ===\n")
    
    # Create rate limiter with in-memory store
    store = InMemoryRateLimitStore()
    limiter = DistributedRateLimiter(store)
    
    # Demo 1: Different tiers
    print("1. Tiered Rate Limiting:")
    tiered_demo(limiter)
    
    # Demo 2: HTTP headers
    print("\n2. HTTP Response Headers:")
    headers_demo(limiter)
    
    # Demo 3: Rate limiting simulation
    print("\n3. API Usage Simulation:")
    simulation_demo(limiter)
    
    # Demo 4: Metrics
    print("\n4. Metrics:")
    print(f"   {limiter.metrics}")
    
    print("\n=== Demo Complete ===")


def tiered_demo(limiter: DistributedRateLimiter):
    # Add custom tiers for demo
    limiter.add_tier(TierConfig("demo-free", 5, 60, 2))
    limiter.add_tier(TierConfig("demo-premium", 20, 60, 5))
    
    print("   Free tier (5/min):")
    for i in range(1, 8):
        result = limiter.check_rate_limit("free-user", "demo-free")
        print(f"      Request {i}: {'OK' if result.allowed else 'BLOCKED'} "
              f"(remaining: {result.remaining})")
    
    print("\n   Premium tier (20/min):")
    for i in range(1, 8):
        result = limiter.check_rate_limit("premium-user", "demo-premium")
        print(f"      Request {i}: {'OK' if result.allowed else 'BLOCKED'} "
              f"(remaining: {result.remaining})")


def headers_demo(limiter: DistributedRateLimiter):
    limiter.add_tier(TierConfig("header-demo", 3, 60, 1))
    
    for i in range(1, 6):
        result = limiter.check_rate_limit("header-user", "header-demo")
        status = "200 OK" if result.allowed else "429 Too Many Requests"
        print(f"   Request {i} - Status: {status}")
        for key, value in result.get_headers().items():
            print(f"      {key}: {value}")
        print()


def simulation_demo(limiter: DistributedRateLimiter):
    import random
    
    limiter.add_tier(TierConfig("sim", 10, 60, 3))
    
    users = ["user-A", "user-B", "user-C"]
    random.seed(42)
    
    total = allowed = rejected = 0
    
    for _ in range(50):
        user = random.choice(users)
        result = limiter.check_rate_limit(user, "sim")
        
        total += 1
        if result.allowed:
            allowed += 1
        else:
            rejected += 1
    
    print(f"   Simulated {total} requests from 3 users")
    print(f"   Allowed: {allowed}, Rejected: {rejected}")
    print(f"   Acceptance rate: {(allowed * 100.0) / total:.1f}%")


if __name__ == "__main__":
    main()

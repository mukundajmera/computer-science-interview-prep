"""
V1: Simple Proxy Cache

A basic CDN edge node simulation with TTL-based caching.
Demonstrates the fundamental concept of caching content
at a proxy layer to reduce origin requests.

Features:
- Simple dict cache with TTL
- Cache hit/miss tracking
- Simulated origin fetching
"""

import time
from typing import TypeVar, Generic, Optional, Dict, Callable
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Cache entry with content and expiration."""
    content: str
    expiration_time: float

    def is_expired(self) -> bool:
        return time.time() > self.expiration_time


class SimpleProxyCache:
    """
    Simple proxy cache with TTL support.
    
    Example:
        origin = lambda url: f"Content for {url}"
        cache = SimpleProxyCache(origin, default_ttl_seconds=300)
        
        content = cache.fetch("/index.html")  # Fetches from origin
        content = cache.fetch("/index.html")  # Returns cached
    """
    
    def __init__(self, origin: Callable[[str], str], default_ttl_seconds: int = 300):
        """
        Creates a proxy cache.
        
        Args:
            origin: Function to fetch content from origin
            default_ttl_seconds: Default TTL in seconds
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._origin = origin
        self._default_ttl = default_ttl_seconds
        self._hits = 0
        self._misses = 0

    def fetch(self, url: str) -> Optional[str]:
        """
        Fetches content, serving from cache if available.
        
        Args:
            url: URL to fetch
            
        Returns:
            Content string or None
        """
        entry = self._cache.get(url)
        
        if entry is not None and not entry.is_expired():
            self._hits += 1
            print(f"CACHE HIT: {url}")
            return entry.content
        
        # Cache miss - fetch from origin
        self._misses += 1
        print(f"CACHE MISS: {url} - fetching from origin")
        
        content = self._origin(url)
        if content is not None:
            self._cache[url] = CacheEntry(
                content=content,
                expiration_time=time.time() + self._default_ttl
            )
        
        return content

    def purge(self, url: str) -> None:
        """Invalidates a URL from cache."""
        if url in self._cache:
            del self._cache[url]
            print(f"PURGED: {url}")

    def purge_all(self) -> None:
        """Invalidates all cached content."""
        self._cache.clear()
        print("PURGED ALL")

    @property
    def hit_rate(self) -> float:
        """Returns cache hit rate as percentage."""
        total = self._hits + self._misses
        return (self._hits * 100.0 / total) if total > 0 else 0.0

    def get_stats(self) -> str:
        """Returns cache statistics."""
        return f"Hits: {self._hits}, Misses: {self._misses}, Hit Rate: {self.hit_rate:.2f}%"


# Demo
if __name__ == "__main__":
    print("=== Simple Proxy Cache Demo ===\n")
    
    # Create mock origin server
    def origin_fetch(url: str) -> str:
        time.sleep(0.1)  # Simulate origin latency
        return f"Content for: {url} (fetched at {time.time():.0f})"
    
    # Create proxy cache with 5 second TTL
    cache = SimpleProxyCache(origin_fetch, default_ttl_seconds=5)
    
    # First request - cache miss
    print("Request 1:")
    result1 = cache.fetch("/index.html")
    print(f"Result: {result1}\n")
    
    # Second request - cache hit
    print("Request 2 (same URL):")
    result2 = cache.fetch("/index.html")
    print(f"Result: {result2}\n")
    
    # Different URL - cache miss
    print("Request 3 (different URL):")
    result3 = cache.fetch("/about.html")
    print(f"Result: {result3}\n")
    
    # Multiple hits
    print("Multiple requests to cached URLs:")
    for _ in range(5):
        cache.fetch("/index.html")
        cache.fetch("/about.html")
    print()
    
    # Stats
    print("Cache Statistics:")
    print(cache.get_stats())
    print()
    
    # Purge demonstration
    print("Purging /index.html:")
    cache.purge("/index.html")
    print()
    
    # After purge - cache miss
    print("Request after purge:")
    cache.fetch("/index.html")
    
    print(f"\nFinal Statistics: {cache.get_stats()}")

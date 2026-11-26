"""
V1: Simple Cache Implementation

A basic in-memory cache with TTL (Time-To-Live) support.
This demonstrates the core concept of caching: storing data
for fast retrieval with automatic expiration.

Features:
- Dictionary-based storage
- TTL-based expiration
- Simple API

Limitations:
- No size limit (can grow unbounded)
- No eviction policy
- Not thread-safe
- Expired entries cleaned only on access
"""

import time
from typing import TypeVar, Generic, Optional, Dict

K = TypeVar('K')
V = TypeVar('V')


class CacheEntry(Generic[V]):
    """Entry wrapper that stores value with expiration time."""
    
    def __init__(self, value: V, expiration_time: float):
        self.value = value
        self.expiration_time = expiration_time
    
    def is_expired(self) -> bool:
        return time.time() > self.expiration_time


class SimpleCache(Generic[K, V]):
    """
    A basic TTL-based cache.
    
    Example:
        cache = SimpleCache(default_ttl_seconds=60)
        cache.put("user:123", user_data)
        user = cache.get("user:123")
    """
    
    def __init__(self, default_ttl_seconds: int = 300):
        """
        Creates a cache with specified default TTL.
        
        Args:
            default_ttl_seconds: Default time-to-live in seconds
        """
        self._cache: Dict[K, CacheEntry[V]] = {}
        self._default_ttl = default_ttl_seconds
    
    def put(self, key: K, value: V, ttl_seconds: Optional[int] = None) -> None:
        """
        Stores a value with optional custom TTL.
        
        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Custom TTL in seconds (uses default if None)
        """
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        expiration_time = time.time() + ttl
        self._cache[key] = CacheEntry(value, expiration_time)
    
    def get(self, key: K) -> Optional[V]:
        """
        Retrieves a value from cache.
        
        Returns None if key doesn't exist or is expired.
        """
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.value
    
    def remove(self, key: K) -> None:
        """Removes an entry from cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clears all entries from cache."""
        self._cache.clear()
    
    def size(self) -> int:
        """Returns the number of entries (including potentially expired ones)."""
        return len(self._cache)
    
    def contains(self, key: K) -> bool:
        """Checks if a key exists and is not expired."""
        return self.get(key) is not None
    
    def cleanup(self) -> int:
        """
        Removes all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)


# ============ Demo ============

def main():
    print("=== Simple Cache Demo ===\n")
    
    # Create cache with 5 second default TTL
    cache: SimpleCache[str, str] = SimpleCache(default_ttl_seconds=5)
    
    # Demo 1: Basic put and get
    print("1. Basic Operations:")
    cache.put("user:1", "Alice")
    cache.put("user:2", "Bob")
    
    print(f"   user:1 = {cache.get('user:1')}")  # Alice
    print(f"   user:2 = {cache.get('user:2')}")  # Bob
    print(f"   user:3 = {cache.get('user:3')}")  # None (cache miss)
    print(f"   Cache size: {cache.size()}")
    
    # Demo 2: TTL expiration
    print("\n2. TTL Expiration:")
    cache.put("session:abc", "session_data", ttl_seconds=2)
    print(f"   session:abc = {cache.get('session:abc')}")
    
    print("   Waiting 2.5 seconds...")
    time.sleep(2.5)
    
    print(f"   session:abc = {cache.get('session:abc')}")  # None (expired)
    
    # Demo 3: Cache-aside pattern
    print("\n3. Cache-Aside Pattern:")
    product_id = "product:42"
    
    def get_product_with_cache(pid: str) -> str:
        product = cache.get(pid)
        if product is not None:
            print("   [CACHE HIT]")
            return product
        
        print("   [CACHE MISS] - Fetching from database...")
        # Simulate database fetch
        time.sleep(0.1)
        product = f"Product data for {pid}"
        cache.put(pid, product)
        return product
    
    result = get_product_with_cache(product_id)
    print(f"   First call: {result}")
    
    result = get_product_with_cache(product_id)
    print(f"   Second call: {result}")
    
    # Demo 4: Cache invalidation
    print("\n4. Cache Invalidation:")
    cache.put("config:version", "v1.0")
    print(f"   Before invalidation: {cache.get('config:version')}")
    
    cache.remove("config:version")
    print(f"   After invalidation: {cache.get('config:version')}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

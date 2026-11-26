"""
V2: LRU Cache Implementation

A Least Recently Used (LRU) cache with size limit.
When the cache reaches capacity, the least recently
accessed entry is automatically evicted.

This implementation uses OrderedDict to efficiently
track usage and implement LRU eviction in O(1) time.

Features:
- Fixed size capacity
- LRU eviction policy
- O(1) get and put operations
- TTL support per entry
- Statistics tracking

Use Case:
- Limited memory environments
- When you want to keep "hot" data in cache
- Session caching, API response caching
"""

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Callable
import threading

K = TypeVar('K')
V = TypeVar('V')


@dataclass
class CacheEntry(Generic[V]):
    """Wrapper for cached values with TTL support."""
    value: V
    expiration_time: float  # 0 means no expiration
    
    def is_expired(self) -> bool:
        return self.expiration_time > 0 and time.time() > self.expiration_time


@dataclass
class CacheStats:
    """Statistics tracking for the cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    
    def hit_rate(self) -> float:
        """Returns hit rate as percentage."""
        total = self.hits + self.misses
        return (self.hits * 100.0 / total) if total > 0 else 0.0
    
    def __str__(self) -> str:
        return (
            f"CacheStats(hits={self.hits}, misses={self.misses}, "
            f"hit_rate={self.hit_rate():.2f}%, evictions={self.evictions})"
        )


class LRUCache(Generic[K, V]):
    """
    LRU Cache with eviction and TTL support.
    
    Thread-safe implementation using a lock for all operations.
    
    Example:
        cache = LRUCache(capacity=100, default_ttl_seconds=300)
        cache.put("user:123", user_data)
        user = cache.get("user:123")
        
        # With loader function
        user = cache.get_or_compute("user:456", lambda: fetch_from_db(456))
    """
    
    def __init__(self, capacity: int, default_ttl_seconds: int = 0):
        """
        Creates an LRU cache.
        
        Args:
            capacity: Maximum number of entries
            default_ttl_seconds: Default TTL in seconds (0 for no expiration)
        """
        self._capacity = capacity
        self._default_ttl = default_ttl_seconds
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self._stats = CacheStats()
        self._lock = threading.Lock()
    
    def put(self, key: K, value: V, ttl_seconds: Optional[int] = None) -> None:
        """
        Stores a value with optional custom TTL.
        
        If key exists, it's moved to most recently used position.
        If at capacity, evicts the least recently used entry.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        expiration_time = time.time() + ttl if ttl > 0 else 0
        
        with self._lock:
            # If key exists, remove it first (will be re-added at end)
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self._capacity:
                # Evict LRU (first item in OrderedDict)
                self._cache.popitem(last=False)
                self._stats.evictions += 1
            
            self._cache[key] = CacheEntry(value, expiration_time)
    
    def get(self, key: K) -> Optional[V]:
        """
        Retrieves a value, moving it to most recently used.
        
        Returns None if not found or expired.
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats.misses += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._stats.misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._stats.hits += 1
            return entry.value
    
    def get_or_compute(self, key: K, loader: Callable[[], V]) -> Optional[V]:
        """
        Gets value if present, otherwise computes and caches it.
        
        Args:
            key: Cache key
            loader: Function to compute value on cache miss
            
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute and cache
        value = loader()
        if value is not None:
            self.put(key, value)
        return value
    
    def remove(self, key: K) -> None:
        """Removes an entry from cache."""
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clears all entries and resets stats."""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()
    
    def size(self) -> int:
        """Returns current number of entries."""
        return len(self._cache)
    
    @property
    def capacity(self) -> int:
        """Returns cache capacity."""
        return self._capacity
    
    @property
    def stats(self) -> CacheStats:
        """Returns cache statistics."""
        return self._stats
    
    def cleanup(self) -> int:
        """
        Removes all expired entries.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)


# ============ Demo ============

def main():
    import random
    
    print("=== LRU Cache Demo ===\n")
    
    # Create cache with capacity=3, 60 second TTL
    cache: LRUCache[str, str] = LRUCache(capacity=3, default_ttl_seconds=60)
    
    # Demo 1: LRU Eviction
    print("1. LRU Eviction (capacity=3):")
    cache.put("A", "Value A")
    cache.put("B", "Value B")
    cache.put("C", "Value C")
    print(f"   Added A, B, C - Size: {cache.size()}")
    
    # Access A to make it "recently used"
    cache.get("A")
    print("   Accessed A (now most recently used)")
    
    # Add D - should evict B (least recently used)
    cache.put("D", "Value D")
    print(f"   Added D - Size: {cache.size()}")
    print(f"   A = {cache.get('A')}")  # Still exists
    print(f"   B = {cache.get('B')}")  # Evicted!
    print(f"   C = {cache.get('C')}")  # Still exists
    print(f"   D = {cache.get('D')}")  # Just added
    print(f"   {cache.stats}")
    
    # Demo 2: Hit Rate Tracking
    print("\n2. Hit Rate Tracking:")
    cache.clear()
    
    keys = ["user:1", "user:2", "user:3", "user:1", "user:1", "user:2"]
    for key in keys:
        value = cache.get(key)
        if value is None:
            value = f"Data for {key}"
            cache.put(key, value)
            print(f"   {key} -> MISS -> cached")
        else:
            print(f"   {key} -> HIT")
    print(f"   {cache.stats}")
    
    # Demo 3: get_or_compute Pattern
    print("\n3. get_or_compute Pattern:")
    cache.clear()
    
    def expensive_operation() -> str:
        print("   Computing expensive value...")
        time.sleep(0.1)
        return "Expensive result"
    
    result = cache.get_or_compute("expensive:key", expensive_operation)
    print(f"   Result: {result}")
    
    result = cache.get_or_compute("expensive:key", expensive_operation)
    print(f"   Result: {result}")
    print(f"   {cache.stats}")
    
    # Demo 4: Simulating workload with Zipf distribution
    print("\n4. Simulating Workload:")
    cache = LRUCache(capacity=100, default_ttl_seconds=300)
    total_requests = 1000
    
    random.seed(42)
    for _ in range(total_requests):
        # 80% requests go to 20% of keys
        if random.random() < 0.8:
            key = random.randint(0, 19)  # Hot keys
        else:
            key = random.randint(0, 199)  # Cold keys
        
        cache.get_or_compute(key, lambda k=key: f"Data for {k}")
    
    print(f"   After {total_requests} requests:")
    print(f"   {cache.stats}")
    print("   Expected high hit rate due to Pareto distribution")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

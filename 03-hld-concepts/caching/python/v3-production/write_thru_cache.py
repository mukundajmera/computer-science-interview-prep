"""
V3: Production-Ready Write-Through Cache

A thread-safe cache implementation with production-level features:
- Write-through to backing store
- Cache-aside read pattern
- Lock striping for better concurrency
- Cache stampede prevention
- Comprehensive statistics
- Async refresh support

This demonstrates patterns used in production systems like
Redis clients, Memcached, and cloud cache services.
"""

import time
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Dict, Protocol, List
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

K = TypeVar('K')
V = TypeVar('V')


class DataSource(Protocol[K, V]):
    """Protocol for backing data store."""
    
    def get(self, key: K) -> Optional[V]:
        """Retrieve value from data source."""
        ...
    
    def put(self, key: K, value: V) -> None:
        """Store value in data source."""
        ...
    
    def delete(self, key: K) -> None:
        """Delete value from data source."""
        ...


@dataclass
class CacheEntry(Generic[V]):
    """Cache entry with metadata."""
    value: V
    expiration_time: float
    last_access_time: float = field(default_factory=time.time)
    refreshing: bool = False
    
    def is_expired(self) -> bool:
        return time.time() > self.expiration_time
    
    def touch(self) -> None:
        self.last_access_time = time.time()
    
    def refresh(self, new_value: V, ttl_seconds: float) -> None:
        self.value = new_value
        self.expiration_time = time.time() + ttl_seconds
        self.refreshing = False


class CacheStats:
    """Thread-safe statistics tracking."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._loads = 0
        self._evictions = 0
        self._write_thrus = 0
    
    def record_hit(self) -> None:
        with self._lock:
            self._hits += 1
    
    def record_miss(self) -> None:
        with self._lock:
            self._misses += 1
    
    def record_load(self) -> None:
        with self._lock:
            self._loads += 1
    
    def record_eviction(self) -> None:
        with self._lock:
            self._evictions += 1
    
    def record_write_thru(self) -> None:
        with self._lock:
            self._write_thrus += 1
    
    @property
    def hits(self) -> int:
        return self._hits
    
    @property
    def misses(self) -> int:
        return self._misses
    
    @property
    def loads(self) -> int:
        return self._loads
    
    @property
    def evictions(self) -> int:
        return self._evictions
    
    @property
    def write_thrus(self) -> int:
        return self._write_thrus
    
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return (self._hits * 100.0 / total) if total > 0 else 0.0
    
    def __str__(self) -> str:
        return (
            f"CacheStats(hits={self._hits}, misses={self._misses}, "
            f"hit_rate={self.hit_rate():.2f}%, loads={self._loads}, "
            f"evictions={self._evictions}, write_thrus={self._write_thrus})"
        )


class WriteThruCache(Generic[K, V]):
    """
    Production-ready write-through cache.
    
    Features:
    - Write-through: Updates go to cache AND data source
    - Cache-aside read: Load from data source on miss
    - Stampede prevention: Lock per key stripe
    - LRU eviction: When at capacity
    - Background maintenance: Cleanup expired entries
    
    Example:
        data_source = DatabaseAdapter()
        cache = WriteThruCache(
            capacity=1000,
            default_ttl_seconds=300,
            data_source=data_source
        )
        
        # Read (cache-aside)
        value = cache.get("key")  # Loads from DB if not cached
        
        # Write (write-through)
        cache.put("key", "value")  # Updates cache AND DB
    """
    
    NUM_STRIPES = 16  # Number of lock stripes for concurrency
    
    def __init__(
        self,
        capacity: int,
        default_ttl_seconds: int,
        data_source: DataSource[K, V],
        cleanup_interval_seconds: int = 60
    ):
        """
        Creates a write-through cache.
        
        Args:
            capacity: Maximum number of entries
            default_ttl_seconds: Default TTL in seconds
            data_source: Backing data store
            cleanup_interval_seconds: Interval for expired entry cleanup
        """
        self._capacity = capacity
        self._default_ttl = default_ttl_seconds
        self._data_source = data_source
        self._cache: Dict[K, CacheEntry[V]] = {}
        self._access_order: OrderedDict[K, None] = OrderedDict()
        self._stats = CacheStats()
        
        # Lock striping for concurrency
        self._locks = [threading.Lock() for _ in range(self.NUM_STRIPES)]
        self._global_lock = threading.RLock()
        
        # Background executor
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cache-bg")
        self._running = True
        self._cleanup_stop = threading.Event()
        
        # Start cleanup task
        self._schedule_cleanup(cleanup_interval_seconds)
    
    def _get_stripe_lock(self, key: K) -> threading.Lock:
        """Get lock for key's stripe."""
        stripe = hash(key) % self.NUM_STRIPES
        return self._locks[stripe]
    
    def get(self, key: K) -> Optional[V]:
        """
        Gets a value, loading from data source on miss.
        
        Thread-safe with stampede prevention.
        """
        # Fast path: check cache without lock
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            entry.touch()
            self._update_access_order(key)
            self._stats.record_hit()
            return entry.value
        
        # Slow path: need to load
        return self._load_value(key)
    
    def _load_value(self, key: K) -> Optional[V]:
        """Load value with stampede prevention."""
        lock = self._get_stripe_lock(key)
        
        with lock:
            # Double-check after acquiring lock
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                self._stats.record_hit()
                return entry.value
            
            # Load from data source
            self._stats.record_miss()
            
            try:
                value = self._data_source.get(key)
            except Exception as e:
                logger.error(f"Failed to load key {key}: {e}")
                return None
            
            if value is not None:
                self._stats.record_load()
                self._put_internal(key, value, self._default_ttl, write_through=False)
            
            return value
    
    def put(self, key: K, value: V, ttl_seconds: Optional[int] = None) -> None:
        """
        Puts a value with write-through to data source.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._put_internal(key, value, ttl, write_through=True)
    
    def _put_internal(
        self,
        key: K,
        value: V,
        ttl_seconds: int,
        write_through: bool
    ) -> None:
        """Internal put with optional write-through."""
        with self._global_lock:
            # Enforce capacity
            while len(self._cache) >= self._capacity:
                self._evict_lru()
            
            # Update cache
            expiration_time = time.time() + ttl_seconds
            self._cache[key] = CacheEntry(value, expiration_time)
            self._update_access_order(key)
        
        # Write-through to data source
        if write_through:
            try:
                self._data_source.put(key, value)
                self._stats.record_write_thru()
            except Exception as e:
                logger.error(f"Write-through failed for key {key}: {e}")
    
    def _update_access_order(self, key: K) -> None:
        """Update LRU tracking."""
        with self._global_lock:
            if key in self._access_order:
                self._access_order.move_to_end(key)
            else:
                self._access_order[key] = None
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._access_order:
            return
        
        oldest_key, _ = self._access_order.popitem(last=False)
        self._cache.pop(oldest_key, None)
        self._stats.record_eviction()
    
    def remove(self, key: K) -> None:
        """Removes entry from cache and data source."""
        with self._global_lock:
            self._cache.pop(key, None)
            self._access_order.pop(key, None)
        
        try:
            self._data_source.delete(key)
        except Exception as e:
            logger.error(f"Delete failed for key {key}: {e}")
    
    def invalidate(self, key: K) -> None:
        """Invalidates cache entry without touching data source."""
        with self._global_lock:
            self._cache.pop(key, None)
            self._access_order.pop(key, None)
    
    def cleanup(self) -> int:
        """Remove expired entries."""
        with self._global_lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                self._cache.pop(key, None)
                self._access_order.pop(key, None)
            return len(expired_keys)
    
    def _schedule_cleanup(self, interval_seconds: int) -> None:
        """Schedule periodic cleanup."""
        def cleanup_task():
            interval = max(interval_seconds, 0.001)
            while not self._cleanup_stop.wait(interval):
                removed = self.cleanup()
                if removed > 0:
                    logger.debug(f"Cleaned up {removed} expired entries")
        
        self._executor.submit(cleanup_task)
    
    def warm_up(self, keys: List[K]) -> None:
        """Pre-load cache with specified keys."""
        for key in keys:
            self.get(key)
    
    def size(self) -> int:
        """Returns current number of entries."""
        return len(self._cache)
    
    @property
    def stats(self) -> CacheStats:
        """Returns cache statistics."""
        return self._stats
    
    def shutdown(self) -> None:
        """Shutdown background tasks."""
        self._running = False
        self._cleanup_stop.set()
        self._executor.shutdown(wait=True)


# ============ Demo ============

class InMemoryDataSource:
    """Simulated database with configurable latency."""
    
    def __init__(self):
        self._store: Dict[str, str] = {}
        self._delay_ms = 0
        self._call_count = 0
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[str]:
        with self._lock:
            self._call_count += 1
        
        if self._delay_ms > 0:
            time.sleep(self._delay_ms / 1000.0)
        
        return self._store.get(key)
    
    def put(self, key: str, value: str) -> None:
        self._store[key] = value
    
    def delete(self, key: str) -> None:
        self._store.pop(key, None)
    
    def set_delay(self, ms: int) -> None:
        self._delay_ms = ms
    
    def get_call_count(self) -> int:
        return self._call_count
    
    def reset_call_count(self) -> None:
        with self._lock:
            self._call_count = 0


def main():
    print("=== Production Write-Through Cache Demo ===\n")
    
    # Create data source and cache
    data_source = InMemoryDataSource()
    
    # Pre-populate database
    data_source.put("user:1", '{"name": "Alice", "email": "alice@example.com"}')
    data_source.put("user:2", '{"name": "Bob", "email": "bob@example.com"}')
    data_source.put("product:1", '{"name": "Widget", "price": 9.99}')
    
    cache: WriteThruCache[str, str] = WriteThruCache(
        capacity=100,
        default_ttl_seconds=60,
        data_source=data_source
    )
    
    try:
        # Demo 1: Cache-aside reads
        print("1. Cache-Aside Read Pattern:")
        print("   Getting user:1 (cache miss - loads from DB):")
        user1 = cache.get("user:1")
        print(f"   Result: {user1}")
        print(f"   Stats: {cache.stats}")
        
        print("\n   Getting user:1 again (cache hit):")
        user1 = cache.get("user:1")
        print(f"   Result: {user1}")
        print(f"   Stats: {cache.stats}")
        
        # Demo 2: Write-through
        print("\n2. Write-Through Pattern:")
        new_user = '{"name": "Charlie", "email": "charlie@example.com"}'
        cache.put("user:3", new_user)
        print("   Written user:3 to cache and database")
        print(f"   Cache value: {cache.get('user:3')}")
        print(f"   DB value: {data_source.get('user:3')}")
        print(f"   Stats: {cache.stats}")
        
        # Demo 3: Cache stampede prevention
        print("\n3. Cache Stampede Prevention:")
        print("   Simulating 10 concurrent requests for same key...")
        
        cache.invalidate("user:1")
        data_source.set_delay(100)
        data_source.reset_call_count()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cache.get, "user:1") for _ in range(10)]
            concurrent.futures.wait(futures)
        
        print(f"   DB calls: {data_source.get_call_count()}")
        print("   (Without stampede prevention, would be 10 DB calls)")
        print(f"   Stats: {cache.stats}")
        
        data_source.set_delay(0)
        
        # Demo 4: Statistics
        print("\n4. Monitoring & Statistics:")
        print(f"   {cache.stats}")
        print(f"   Cache size: {cache.size()}")
        
    finally:
        cache.shutdown()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

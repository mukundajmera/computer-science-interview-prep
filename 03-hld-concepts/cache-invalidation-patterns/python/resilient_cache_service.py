import time
import random
import threading
from typing import TypeVar, Generic, Callable, Optional, Dict

K = TypeVar('K')
V = TypeVar('V')

class CacheEntry(Generic[V]):
    def __init__(self, value: Optional[V], expire_at: float, is_null_object: bool):
        self.value = value
        self.expire_at = expire_at
        self.is_null_object = is_null_object

class ResilientCacheService(Generic[K, V]):
    def __init__(self, bloom_filter: Callable[[K], bool], base_ttl_sec: float, jitter_sec: float, null_ttl_sec: float):
        self.cache: Dict[K, CacheEntry[V]] = {}
        self.locks: Dict[K, threading.Lock] = {}
        self.global_lock = threading.Lock()
        
        self.bloom_filter = bloom_filter
        self.base_ttl_sec = base_ttl_sec
        self.jitter_sec = jitter_sec
        self.null_ttl_sec = null_ttl_sec

    def _get_lock(self, key: K) -> threading.Lock:
        with self.global_lock:
            if key not in self.locks:
                self.locks[key] = threading.Lock()
            return self.locks[key]

    def get(self, key: K, db_loader: Callable[[K], Optional[V]]) -> Optional[V]:
        # 1. Bloom Filter Check (Cache Penetration Mitigation)
        if not self.bloom_filter(key):
            return None

        entry = self.cache.get(key)
        
        # Logical Expiration Check
        if entry and time.time() < entry.expire_at:
            return None if entry.is_null_object else entry.value

        # Cache Miss or Expired (Thundering Herd Mitigation via Singleflight/Mutex)
        lock = self._get_lock(key)
        with lock:
            # Double-checked locking
            entry = self.cache.get(key)
            if entry and time.time() < entry.expire_at:
                return None if entry.is_null_object else entry.value

            # Load from DB
            db_value = db_loader(key)

            # Null Object Caching (Cache Penetration Mitigation)
            if db_value is None:
                expire_at = time.time() + self.null_ttl_sec
                self.cache[key] = CacheEntry(None, expire_at, True)
                return None

            # Jittered TTL (Cache Avalanche Mitigation)
            jitter = random.uniform(0, self.jitter_sec) if self.jitter_sec > 0 else 0
            ttl = self.base_ttl_sec + jitter
            expire_at = time.time() + ttl
            
            self.cache[key] = CacheEntry(db_value, expire_at, False)
            return db_value

    def _get_raw_entry(self, key: K) -> Optional[CacheEntry[V]]:
        """For testing purposes."""
        return self.cache.get(key)

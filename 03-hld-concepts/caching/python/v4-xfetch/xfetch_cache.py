import time
import math
import random
from typing import Callable, Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor

try:
    from .singleflight import Singleflight
except ImportError:
    from singleflight import Singleflight

class CacheEntry:
    def __init__(self, value: Any, ttl: float, delta: float, created_at: float):
        self.value = value
        self.ttl = ttl
        self.delta = delta
        self.created_at = created_at
        self.expires_at = created_at + ttl

class XFetchCache:
    """
    XFetch Cache with Singleflight for stampede protection.
    Uses probabilistic early expiration to refresh items before they expire.
    """
    def __init__(self, beta: float = 1.0, 
                 clock: Optional[Callable[[], float]] = None,
                 rng: Optional[Callable[[], float]] = None,
                 executor_workers: int = 4):
        self.beta = beta
        self.clock = clock or time.time
        self.rng = rng or random.random
        
        self._store: Dict[Any, CacheEntry] = {}
        self._sf = Singleflight()
        self._executor = ThreadPoolExecutor(max_workers=executor_workers)
        
    def _compute_and_store(self, key: Any, loader: Callable[[], Any], ttl: float) -> Any:
        start_time = self.clock()
        try:
            val = loader()
        except Exception as e:
            raise e
        end_time = self.clock()
        delta = max(0.001, end_time - start_time) # Ensure positive delta
        
        entry = CacheEntry(val, ttl, delta, end_time)
        self._store[key] = entry
        return val
        
    def _should_refresh(self, entry: CacheEntry, now: float) -> bool:
        # Remaining TTL
        remaining = entry.expires_at - now
        
        # If already logically expired, definitely refresh
        if remaining <= 0:
            return True
            
        # XFetch probabilistic early expiration: 
        # -beta * delta * ln(rand()) >= remaining
        # We need a random value in (0, 1]
        u = self.rng()
        while u == 0.0:
            u = self.rng()
            
        threshold = -self.beta * entry.delta * math.log(u)
        return threshold >= remaining

    def get(self, key: Any, loader: Callable[[], Any], ttl: float) -> Any:
        now = self.clock()
        entry = self._store.get(key)
        
        if entry is None:
            # Cache miss, block and load (deduplicated via singleflight)
            val, err, _ = self._sf.do(key, lambda: self._compute_and_store(key, loader, ttl))
            if err:
                raise err
            return val
            
        if self._should_refresh(entry, now):
            # Asynchronous background refresh
            # We don't wait for it, just return the stale value for now
            # Note that singleflight handles the deduplication if multiple requests try to refresh
            self._executor.submit(self._sf.do, key, lambda: self._compute_and_store(key, loader, ttl))
            
        return entry.value
        
    def shutdown(self):
        self._executor.shutdown(wait=False)

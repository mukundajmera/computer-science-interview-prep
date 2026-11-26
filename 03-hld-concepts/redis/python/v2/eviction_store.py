import time
from typing import Any, Dict, Optional, List

class EvictionStore:
    def __init__(self, capacity: int, policy: str = "allkeys-lru"):
        self.capacity = capacity
        self.policy = policy
        self.store: Dict[str, Any] = {}
        self.ttls: Dict[str, float] = {}
        # LRU usage tracking
        self.lru_order: List[str] = []
        
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        is_new = key not in self.store
        if is_new:
            self._enforce_capacity()
        self.store[key] = value
        if ttl is not None:
            self.ttls[key] = time.time() + ttl
            
        if key in self.lru_order:
            self.lru_order.remove(key)
        self.lru_order.append(key)
        
    def get(self, key: str) -> Optional[Any]:
        if key not in self.store:
            return None
            
        if key in self.ttls and time.time() > self.ttls[key]:
            self._delete(key)
            return None
            
        if key in self.lru_order:
            self.lru_order.remove(key)
            self.lru_order.append(key)
            
        return self.store[key]
        
    def _enforce_capacity(self) -> None:
        # Before enforcing capacity, remove expired keys passively
        now = time.time()
        expired = [k for k, t in self.ttls.items() if now > t]
        for k in expired:
            self._delete(k)
            
        while len(self.store) >= self.capacity:
            if self.policy == "allkeys-lru":
                self._evict_allkeys_lru()
            elif self.policy == "volatile-lru":
                success = self._evict_volatile_lru()
                if not success:
                    raise MemoryError("OOM command not allowed when used memory > 'maxmemory'.")
            else:
                raise ValueError(f"Unknown policy: {self.policy}")
                
    def _evict_allkeys_lru(self) -> None:
        if not self.lru_order:
            return
        lru_key = self.lru_order[0]
        self._delete(lru_key)
        
    def _evict_volatile_lru(self) -> bool:
        for key in self.lru_order:
            if key in self.ttls:
                self._delete(key)
                return True
        return False
        
    def _delete(self, key: str) -> None:
        self.store.pop(key, None)
        self.ttls.pop(key, None)
        if key in self.lru_order:
            self.lru_order.remove(key)

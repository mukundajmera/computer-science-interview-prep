"""
Proxy Pattern - V3 Advanced: Caching Proxy.

Adds TTL-based read caching and write-through invalidation around a data
service without changing the service interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional
import time


class DataService(ABC):
    """Subject interface for data access."""

    @abstractmethod
    def fetch_data(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def update_data(self, key: str, value: str) -> None:
        pass


class DatabaseService(DataService):
    """Real subject simulating a backing database."""

    def __init__(self):
        self._data: Dict[str, str] = {
            "user:1": "Alice",
            "user:2": "Bob",
            "product:1": "Laptop",
        }

    def fetch_data(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def update_data(self, key: str, value: str) -> None:
        self._data[key] = value


@dataclass
class CacheEntry:
    """Cached value with an absolute expiration timestamp."""

    value: str
    expire_time: float

    @classmethod
    def create(cls, value: str, ttl_seconds: float) -> "CacheEntry":
        return cls(value=value, expire_time=time.time() + ttl_seconds)

    def is_expired(self) -> bool:
        return time.time() > self.expire_time


class CachingDataServiceProxy(DataService):
    """Caching proxy that wraps any DataService implementation."""

    def __init__(self, real_service: DataService, ttl_seconds: float = 60):
        self._real_service = real_service
        self._cache: Dict[str, CacheEntry] = {}
        self._ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0

    def fetch_data(self, key: str) -> Optional[str]:
        entry = self._cache.get(key)
        if entry is not None and not entry.is_expired():
            self.hits += 1
            return entry.value

        self.misses += 1
        value = self._real_service.fetch_data(key)
        if value is not None:
            self._cache[key] = CacheEntry.create(value, self._ttl_seconds)
        return value

    def update_data(self, key: str, value: str) -> None:
        self._real_service.update_data(key, value)
        self._cache.pop(key, None)

    def clear_cache(self) -> None:
        self._cache.clear()

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total else 0.0

    def get_stats(self) -> str:
        return f"Hits: {self.hits}, Misses: {self.misses}, Rate: {self.hit_rate:.1f}%"


if __name__ == "__main__":
    cached_service = CachingDataServiceProxy(DatabaseService(), ttl_seconds=10)

    print(cached_service.fetch_data("user:1"))
    print(cached_service.fetch_data("user:1"))
    cached_service.update_data("user:1", "Alicia")
    print(cached_service.fetch_data("user:1"))
    print(cached_service.get_stats())

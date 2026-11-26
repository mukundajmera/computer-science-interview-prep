"""Simple DNS resolver simulation with cache and round-robin answers."""

from dataclasses import dataclass
from typing import Dict, List, Optional
import time


@dataclass
class CacheEntry:
    ip: str
    expires_at: float


class DnsResolver:
    def __init__(self, records: Dict[str, List[str]]):
        if not records:
            raise ValueError("records cannot be empty")
        self._records = records
        self._cache: Dict[str, CacheEntry] = {}
        self._indices: Dict[str, int] = {}

    def resolve(self, domain: str, ttl_seconds: int = 60) -> Optional[str]:
        now = time.time()
        cached = self._cache.get(domain)
        if cached and cached.expires_at > now:
            return cached.ip

        addresses = self._records.get(domain)
        if not addresses:
            return None

        idx = self._indices.get(domain, 0)
        ip = addresses[idx % len(addresses)]
        self._indices[domain] = idx + 1
        self._cache[domain] = CacheEntry(ip=ip, expires_at=now + ttl_seconds)
        return ip


if __name__ == "__main__":
    resolver = DnsResolver({"api.example.com": ["10.0.0.1", "10.0.0.2"]})
    print(resolver.resolve("api.example.com", ttl_seconds=1))
    print(resolver.resolve("api.example.com", ttl_seconds=1))
    time.sleep(1.1)
    print(resolver.resolve("api.example.com", ttl_seconds=1))

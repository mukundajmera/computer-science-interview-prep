"""TTL-aware in-memory DNS resolver demo."""

from dataclasses import dataclass
from time import sleep, time
from typing import Dict, Optional


@dataclass
class DnsRecord:
    value: str
    expires_at: float


class SimpleDnsResolver:
    def __init__(self) -> None:
        self._cache: Dict[str, DnsRecord] = {}
        self._authoritative: Dict[str, str] = {}

    def upsert_authoritative_record(self, host: str, address: str) -> None:
        self._authoritative[host] = address

    def resolve(self, host: str, ttl_seconds: float) -> Optional[str]:
        cached = self._cache.get(host)
        now = time()
        if cached and now < cached.expires_at:
            print(f"CACHE_HIT host={host} value={cached.value}")
            return cached.value

        if cached:
            print(f"CACHE_STALE host={host}")
            self._cache.pop(host, None)
        else:
            print(f"CACHE_MISS host={host}")

        resolved = self._authoritative.get(host)
        if resolved is None:
            print(f"AUTHORITATIVE_MISS host={host}")
            return None

        self._cache[host] = DnsRecord(value=resolved, expires_at=now + ttl_seconds)
        print(f"AUTHORITATIVE_HIT host={host} value={resolved}")
        return resolved


if __name__ == "__main__":
    resolver = SimpleDnsResolver()
    resolver.upsert_authoritative_record("api.example.com", "10.0.1.12")

    ttl_seconds = 0.7
    print("First resolve: ", resolver.resolve("api.example.com", ttl_seconds))
    print("Second resolve:", resolver.resolve("api.example.com", ttl_seconds))

    sleep(0.8)
    resolver.upsert_authoritative_record("api.example.com", "10.0.2.44")
    print("After expiry: ", resolver.resolve("api.example.com", ttl_seconds))

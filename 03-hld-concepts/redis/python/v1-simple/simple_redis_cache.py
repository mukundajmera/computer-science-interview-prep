"""Interview-scale Redis-like cache primitives with TTL and counters."""

from dataclasses import dataclass
from time import sleep, time
from typing import Dict, Optional


@dataclass
class _Entry:
    value: str
    expires_at: float


class SimpleRedisCache:
    def __init__(self) -> None:
        self._data: Dict[str, _Entry] = {}

    def set(self, key: str, value: str, ttl_seconds: float) -> None:
        self._validate_ttl(ttl_seconds)
        self._data[key] = _Entry(value=value, expires_at=time() + ttl_seconds)

    def set_if_absent(self, key: str, value: str, ttl_seconds: float) -> bool:
        self._validate_ttl(ttl_seconds)
        if self.get(key) is not None:
            return False
        self._data[key] = _Entry(value=value, expires_at=time() + ttl_seconds)
        return True

    def get(self, key: str) -> Optional[str]:
        entry = self._data.get(key)
        if entry is None:
            return None
        if time() >= entry.expires_at:
            self._data.pop(key, None)
            return None
        return entry.value

    def increment(self, key: str, delta: int = 1, ttl_seconds: float = 60.0) -> int:
        self._validate_ttl(ttl_seconds)
        current = self.get(key)
        next_value = (int(current) if current is not None else 0) + delta
        self.set(key, str(next_value), ttl_seconds)
        return next_value

    @staticmethod
    def _validate_ttl(ttl_seconds: float) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than 0")


if __name__ == "__main__":
    cache = SimpleRedisCache()
    cache.set("session:42", "active", 0.5)
    print("session:42 ->", cache.get("session:42"))
    print("counter ->", cache.increment("counter"))
    sleep(0.6)
    print("session:42 after ttl ->", cache.get("session:42"))

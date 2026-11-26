"""
LRU Cache - V2 Extended

Cache statistics tracking hits, misses, and evictions.
"""
from dataclasses import dataclass


@dataclass
class CacheStatistics:
    """Cache statistics tracking."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    puts: int = 0
    removes: int = 0

    def record_hit(self) -> None:
        self.hits += 1

    def record_miss(self) -> None:
        self.misses += 1

    def record_eviction(self) -> None:
        self.evictions += 1

    def record_expiration(self) -> None:
        self.expirations += 1

    def record_put(self) -> None:
        self.puts += 1

    def record_remove(self) -> None:
        self.removes += 1

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_ratio(self) -> float:
        """Get cache hit ratio (0.0 to 1.0)."""
        total = self.total_requests
        return self.hits / total if total > 0 else 0.0

    @property
    def miss_ratio(self) -> float:
        """Get cache miss ratio (0.0 to 1.0)."""
        return 1.0 - self.hit_ratio

    def reset(self) -> None:
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.puts = 0
        self.removes = 0

    def __str__(self) -> str:
        return (f"CacheStatistics(hits={self.hits}, misses={self.misses}, "
                f"hitRatio={self.hit_ratio:.2%}, evictions={self.evictions}, "
                f"expirations={self.expirations}, puts={self.puts}, removes={self.removes})")

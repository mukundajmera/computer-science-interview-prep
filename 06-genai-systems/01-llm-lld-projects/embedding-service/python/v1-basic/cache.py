"""
In-memory embedding cache with TTL-based expiry and oldest-entry eviction.

The :class:`EmbeddingCache` provides O(1) lookups for previously computed
embeddings, bounded by a configurable maximum size and time-to-live.
"""

import time
from typing import Dict, List, Optional, Tuple


class EmbeddingCache:
    """In-memory cache for embedding vectors.

    Each entry is stored with a timestamp.  Entries older than
    *ttl_seconds* are treated as expired and evicted on access.  When
    the cache reaches *max_size*, the oldest entry (by insertion time)
    is removed before inserting a new one.

    Args:
        max_size: Maximum number of entries to store (default 1000).
        ttl_seconds: Time-to-live in seconds for each entry (default 300.0).
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300.0) -> None:
        if max_size < 0:
            raise ValueError("max_size must be non-negative")
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")
        self._cache: Dict[str, Tuple[List[float], float]] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[List[float]]:
        """Retrieve a cached embedding by *key*.

        Returns ``None`` on a miss or if the entry has expired.  Updates
        internal hit/miss counters accordingly.

        Args:
            key: Cache key (typically ``model_name:text``).

        Returns:
            The cached embedding vector, or ``None``.
        """
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None

        embedding, timestamp = entry
        if self._ttl_seconds == 0 or (
            self._ttl_seconds > 0 and (time.time() - timestamp) > self._ttl_seconds
        ):
            # Expired — remove and count as miss
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return embedding

    def put(self, key: str, embedding: List[float]) -> None:
        """Store an embedding under *key*.

        If the cache is at capacity, the oldest entry (by insertion
        time) is evicted first.

        Args:
            key: Cache key.
            embedding: The embedding vector to cache.
        """
        # If key already present, overwrite in-place (no eviction needed)
        if key in self._cache:
            self._cache[key] = (embedding, time.time())
            return

        # Evict oldest entry if at capacity
        if self._max_size > 0 and len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        if self._max_size > 0:
            self._cache[key] = (embedding, time.time())

    def clear(self) -> None:
        """Remove all entries and reset hit/miss counters."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        """Return cache statistics.

        Returns:
            A dict with keys ``hits``, ``misses``, ``hit_rate``, and ``size``.
        """
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
            "size": len(self._cache),
        }

    @property
    def hit_rate(self) -> float:
        """Proportion of lookups that were cache hits."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        """Number of entries currently stored."""
        return len(self._cache)

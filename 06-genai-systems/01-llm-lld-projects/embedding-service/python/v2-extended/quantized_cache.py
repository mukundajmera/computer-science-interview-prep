"""
Quantized Embedding Cache.

Simulates int8 scalar quantization to reduce cache memory footprint.
Float32 embeddings (assumed in range [-1.0, 1.0] from normalization)
are mapped to int8 integers [-128, 127] on cache put, and dequantized on cache get.
"""

import time
from typing import Dict, List, Optional, Tuple


class QuantizedCache:
    """In-memory cache storing embeddings as simulated int8 to save space.

    Args:
        max_size: Maximum number of entries to store.
        ttl_seconds: Time-to-live in seconds for each entry.
    """
    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300.0) -> None:
        if max_size < 0 or ttl_seconds < 0:
            raise ValueError("max_size and ttl_seconds must be non-negative")
        # Stores quantized representation
        self._cache: Dict[str, Tuple[List[int], float]] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0

    def _quantize(self, vector: List[float]) -> List[int]:
        """Convert float vector [-1.0, 1.0] to int vector [-127, 127]."""
        # We use 127 as max value to keep it symmetrical
        return [max(-127, min(127, int(round(val * 127)))) for val in vector]

    def _dequantize(self, quantized: List[int]) -> List[float]:
        """Convert int vector back to float vector."""
        return [val / 127.0 for val in quantized]

    def get(self, key: str) -> Optional[List[float]]:
        """Retrieve and dequantize a cached embedding."""
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None

        quantized, timestamp = entry
        if self._ttl_seconds > 0 and (time.time() - timestamp) > self._ttl_seconds:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return self._dequantize(quantized)

    def put(self, key: str, embedding: List[float]) -> None:
        """Quantize and store an embedding."""
        if key in self._cache:
            self._cache[key] = (self._quantize(embedding), time.time())
            return

        if self._max_size > 0 and len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        if self._max_size > 0:
            self._cache[key] = (self._quantize(embedding), time.time())

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
            "size": len(self._cache),
        }

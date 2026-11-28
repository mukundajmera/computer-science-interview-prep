"""
v2-extended pastebin service.

Improvements over v1-basic (each has dedicated tests):

1. Burn-after-reading pastes (FOLLOW-UPS.md #2): a paste created with
   burn_after_reading=True is returned exactly once. The read and delete
   happen atomically under one lock, so concurrent readers cannot both
   receive the content - the first wins, everyone else gets a 404-style
   miss. Burned pastes never enter the read cache.

2. Hot-key read cache with metrics (FOLLOW-UPS.md #1 viral paste): a
   small, short-lived in-memory LRU cache sits in front of the blob
   store, absorbing repeat reads of a viral paste the way the doc's
   5-second local cache on API servers does. Cache hits and misses are
   counted so the shielding effect is observable, and expired or deleted
   pastes are purged from the cache.

3. KGS-style key block allocation (FOLLOW-UPS.md #3): instead of a bare
   counter, short-link ids come from a KeyBlockAllocator that hands out
   pre-allocated blocks of ids, the way a Key Generation Service
   pre-generates keys. Exhaustion is loud and explicit instead of a
   silent collision.
"""

import collections
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from base62_v2 import encode


@dataclass
class PasteMetadata:
    id: int
    short_link: str
    created_at: float
    expires_at: Optional[float]
    burn_after_reading: bool = False


class KeyBlockAllocator:
    """KGS-style allocator (improvement #3): ids are handed out from
    pre-allocated blocks rather than a shared counter."""

    def __init__(self, start_id: int = 1000000000, block_size: int = 1000, max_blocks: Optional[int] = None):
        if block_size <= 0:
            raise ValueError("block_size must be positive")
        self._next_block_start = start_id
        self._block_size = block_size
        self._max_blocks = max_blocks
        self._blocks_allocated = 0
        self._current_block: List[int] = []
        self._index = 0
        self.lock = threading.Lock()

    def next_id(self) -> int:
        with self.lock:
            if self._index >= len(self._current_block):
                if self._max_blocks is not None and self._blocks_allocated >= self._max_blocks:
                    raise RuntimeError("KeyPoolExhausted: no free key blocks left")
                start = self._next_block_start
                self._current_block = list(range(start, start + self._block_size))
                self._index = 0
                self._next_block_start += self._block_size
                self._blocks_allocated += 1
            paste_id = self._current_block[self._index]
            self._index += 1
            return paste_id

    @property
    def blocks_allocated(self) -> int:
        with self.lock:
            return self._blocks_allocated


class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens = float(capacity)
        self.last_fill = time.time()
        self.lock = threading.Lock()

    def consume(self) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_fill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
            self.last_fill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class PastebinService:
    def __init__(self, capacity: int = 10, fill_rate: float = 1.0,
                 key_allocator: Optional[KeyBlockAllocator] = None,
                 read_cache_max_entries: int = 128,
                 read_cache_ttl_seconds: float = 5.0):
        self.metadata_store: Dict[str, PasteMetadata] = {}
        self.blob_store: Dict[str, str] = {}
        self.rate_limiters: Dict[str, TokenBucket] = {}

        self.capacity = capacity
        self.fill_rate = fill_rate
        self.key_allocator = key_allocator if key_allocator is not None else KeyBlockAllocator()

        # Improvement #2: hot-key read cache (short-lived LRU) + metrics.
        self.read_cache_max_entries = read_cache_max_entries
        self.read_cache_ttl_seconds = read_cache_ttl_seconds
        self.read_cache: "collections.OrderedDict[str, tuple]" = collections.OrderedDict()
        self.read_cache_hits = 0
        self.read_cache_misses = 0

        self.lock = threading.RLock()

    def _get_limiter(self, ip_address: str) -> TokenBucket:
        with self.lock:
            if ip_address not in self.rate_limiters:
                self.rate_limiters[ip_address] = TokenBucket(self.capacity, self.fill_rate)
            return self.rate_limiters[ip_address]

    def create_paste(self, content: str, ip_address: str, ttl_seconds: Optional[int] = None,
                     burn_after_reading: bool = False) -> Optional[str]:
        limiter = self._get_limiter(ip_address)
        if not limiter.consume():
            return None  # Rate limit exceeded

        with self.lock:
            paste_id = self.key_allocator.next_id()  # raises KeyPoolExhausted when dry

            short_link = encode(paste_id)
            # Pad to 7 characters if needed (for realism)
            while len(short_link) < 7:
                short_link = "0" + short_link

            now = time.time()
            expires_at = now + ttl_seconds if ttl_seconds is not None else None

            metadata = PasteMetadata(
                id=paste_id,
                short_link=short_link,
                created_at=now,
                expires_at=expires_at,
                burn_after_reading=burn_after_reading,
            )

            self.metadata_store[short_link] = metadata
            self.blob_store[short_link] = content

            return short_link

    def _cache_get(self, short_link: str) -> Optional[str]:
        entry = self.read_cache.get(short_link)
        if entry is None:
            return None
        content, cached_at = entry
        if time.time() - cached_at > self.read_cache_ttl_seconds:
            del self.read_cache[short_link]
            return None
        self.read_cache.move_to_end(short_link)
        return content

    def _cache_put(self, short_link: str, content: str):
        self.read_cache[short_link] = (content, time.time())
        self.read_cache.move_to_end(short_link)
        while len(self.read_cache) > self.read_cache_max_entries:
            self.read_cache.popitem(last=False)

    def get_paste(self, short_link: str) -> Optional[str]:
        with self.lock:
            if short_link not in self.metadata_store:
                return None

            metadata = self.metadata_store[short_link]
            if metadata.expires_at is not None and time.time() > metadata.expires_at:
                # Active TTL validation on read
                self._delete_paste(short_link)
                return None

            # Improvement #1: burn-after-reading - atomic read + delete so
            # only one reader ever receives the content. Never cached.
            if metadata.burn_after_reading:
                content = self.blob_store.get(short_link)
                self._delete_paste(short_link)
                return content

            # Improvement #2: serve viral pastes from the hot-key cache.
            cached = self._cache_get(short_link)
            if cached is not None:
                self.read_cache_hits += 1
                return cached
            self.read_cache_misses += 1
            content = self.blob_store.get(short_link)
            if content is not None:
                self._cache_put(short_link, content)
            return content

    def _delete_paste(self, short_link: str):
        self.metadata_store.pop(short_link, None)
        self.blob_store.pop(short_link, None)
        self.read_cache.pop(short_link, None)

    def sweep_expired_pastes(self) -> int:
        """Batch TTL cleanup sweep (also purges the read cache)."""
        now = time.time()
        expired_links = []
        with self.lock:
            for short_link, metadata in self.metadata_store.items():
                if metadata.expires_at is not None and now > metadata.expires_at:
                    expired_links.append(short_link)

            for short_link in expired_links:
                self._delete_paste(short_link)
        return len(expired_links)

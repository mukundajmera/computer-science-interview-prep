"""v2-extended CDN simulator.

Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
1. Cache-key normalization at the edge (PITFALLS #6, FOLLOW-UPS #3):
   non-whitelisted query parameters are stripped and the key is
   Customer_ID + normalized path, so random cache-busters like ?cb=123
   can no longer bypass the cache and flood the customer origin.
2. TTL expiry with stale-on-error (PITFALLS #7): edge entries carry a TTL;
   expired entries are revalidated, and while the origin errors, entries
   still inside the stale window are served instead of failing the request
   (the synchronous analog of stale-while-revalidate).
3. Bounded LRU edge cache (PITFALLS #2 and the v2 "expiry or eviction"
   weakness): the edge cache evicts the least-recently-used entry once it
   exceeds max_entries instead of growing without bound.
"""

import time
from collections import OrderedDict


class OriginError(Exception):
    """The customer origin is unreachable or erroring (injectable in tests)."""


def normalize_key(path, customer_id="default", allowed_params=None):
    """Build the cache key: customer_id + path + whitelisted, sorted params.

    Parameters not in allowed_params are dropped, so /a?cb=123 and /a?cb=456
    share one cache entry. With no whitelist, all parameters are stripped.
    """
    allowed = set(allowed_params) if allowed_params else set()
    base, sep, query = path.partition("?")
    kept = []
    if sep and query:
        for pair in query.split("&"):
            name, eq, value = pair.partition("=")
            if name and name in allowed:
                kept.append(name + eq + value if eq else name)
    kept.sort()
    normalized = base + ("?" + "&".join(kept) if kept else "")
    return customer_id + ":" + normalized


class _CacheEntry:
    __slots__ = ("value", "stored_at")

    def __init__(self, value, stored_at):
        self.value = value
        self.stored_at = stored_at


class CustomerOrigin:
    def __init__(self):
        self.data_store = {}
        self.fetch_count = 0
        self.fail = False

    def put(self, path, data):
        self.data_store[path] = data

    def fetch(self, path):
        self.fetch_count += 1
        if self.fail:
            raise OriginError("origin unreachable")
        return self.data_store.get(path)


class OriginShield:
    """Same coalescing semantics as v1; keyed by the normalized path it
    receives from the edge."""

    def __init__(self, origin):
        self.origin = origin
        self.cache = {}
        self.in_flight_requests = {}
        self.cache_hit_count = 0
        self.fetch_count = 0

    def fetch(self, path):
        self.fetch_count += 1
        if path in self.cache:
            self.cache_hit_count += 1
            return self.cache[path]

        if path in self.in_flight_requests:
            return "COALESCED"

        self.in_flight_requests[path] = []
        try:
            data = self.origin.fetch(path)
        finally:
            # Always release the in-flight marker, even when the origin
            # errors, or later fetches would be coalesced forever.
            del self.in_flight_requests[path]
        if data is not None:
            self.cache[path] = data
        return data

    def simulate_concurrent_fetches(self, path, num_requests, results):
        self.fetch_count += num_requests
        if path in self.cache:
            self.cache_hit_count += num_requests
            results.extend([self.cache[path]] * num_requests)
            return

        data = self.origin.fetch(path)
        if data is not None:
            self.cache[path] = data
        results.extend([data] * num_requests)


class EdgeNode:
    def __init__(self, shield, ttl=60.0, stale_window=300.0, max_entries=10000,
                 clock=None):
        if ttl < 0:
            raise ValueError("ttl must be >= 0")
        if stale_window < 0:
            raise ValueError("stale_window must be >= 0")
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self.shield = shield
        self.ttl = ttl
        self.stale_window = stale_window
        self.max_entries = max_entries
        self._clock = clock if clock is not None else time.time
        self.cache = OrderedDict()  # normalized key -> _CacheEntry, LRU ordered
        self.cache_hit_count = 0
        self.stale_served_count = 0

    def _lookup_fresh(self, key):
        entry = self.cache.get(key)
        if entry is None:
            return None
        if self._clock() - entry.stored_at <= self.ttl:
            self.cache.move_to_end(key)  # LRU: a fresh hit refreshes recency
            self.cache_hit_count += 1
            return entry.value
        return None

    def _store(self, key, data):
        self.cache[key] = _CacheEntry(data, self._clock())
        self.cache.move_to_end(key)
        while len(self.cache) > self.max_entries:
            self.cache.popitem(last=False)  # evict least-recently-used

    def fetch(self, path, customer_id="default", allowed_params=None):
        key = normalize_key(path, customer_id, allowed_params)

        fresh = self._lookup_fresh(key)
        if fresh is not None:
            return fresh

        normalized_path = key.split(":", 1)[1]
        entry = self.cache.get(key)
        try:
            data = self.shield.fetch(normalized_path)
        except OriginError:
            # Stale-on-error: serve the expired entry if it is still inside
            # the stale window instead of failing the request (PITFALLS #7).
            if entry is not None and (
                self._clock() - entry.stored_at <= self.ttl + self.stale_window
            ):
                self.stale_served_count += 1
                return entry.value
            raise
        if data is not None and data != "COALESCED":
            self._store(key, data)
        return data

    def fetch_batch(self, path, count, results, customer_id="default",
                    allowed_params=None):
        key = normalize_key(path, customer_id, allowed_params)
        fresh = self._lookup_fresh(key)
        if fresh is not None:
            results.extend([fresh] * count)
            return

        normalized_path = key.split(":", 1)[1]
        self.shield.simulate_concurrent_fetches(normalized_path, count, results)
        if results and results[0] is not None:
            self._store(key, results[0])

    def purge(self, path, customer_id="default", allowed_params=None):
        key = normalize_key(path, customer_id, allowed_params)
        self.cache.pop(key, None)

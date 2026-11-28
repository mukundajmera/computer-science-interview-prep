"""
Semantic Embedding Cache - v2-extended.

This module is a deliberate step up from ``v1-basic/semantic_cache.py``. It keeps
the v1 public API names (``SemanticCache``, ``TenantCache``, ``CacheEntry``,
``cosine_similarity``, ``compute_hash`` and the ``get``/``put`` signatures with
injectable ``current_time``) but addresses weaknesses the project docs already
name:

1. **Thread safety.** v1 mutates shared ``OrderedDict`` state with no locking;
   concurrent ``get``/``put`` calls can corrupt LRU order or raise
   ``RuntimeError`` from mutation during the expiry scan. v2 guards all cache
   operations with a reentrant lock (coarse-grained, per-orchestrator; the
   trade-off is documented in ``SemanticCache``). Locking can be disabled for
   single-threaded embeddings pipelines via ``enable_locking=False``.

2. **Configurable eviction policy and metrics hooks.** v1 hardcodes LRU and
   exposes no observability. v2 adds an ``EvictionPolicy`` (LRU or FIFO) and a
   ``CacheMetrics`` counter set (exact hits, semantic hits, misses, expirations,
   evictions, invalidations) plus an optional ``metrics_hook`` callback invoked
   per event, so callers can bridge to their own monitoring without modifying
   the cache.

3. **Config (system-prompt) versioning.** FOLLOW-UPS.md names this gap: if the
   LLM system prompt changes, every cached response is stale even when the
   semantic query still matches. v2 stamps each entry with the tenant's current
   ``config_version``; ``set_config_version`` bumps it and invalidates stale
   entries, which is the cheap, deterministic form of cache versioning.

Additionally, embedding dimensions are validated at write time per tenant
(fail-fast), instead of only failing later inside a similarity scan.

Standard library only. Python 3.8 compatible. In-memory; no external services.
"""

import hashlib
import math
import threading
import time
from collections import OrderedDict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Computes the cosine similarity between two vectors.

    Complexity: O(D) where D is the dimensionality of the vectors.

    Raises:
        ValueError: If the vectors have different lengths or are empty.
    """
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same length")
    if not v1 or not v2:
        raise ValueError("Vectors cannot be empty")

    dot_prod = sum(a * b for a, b in zip(v1, v2))
    norm_1 = math.sqrt(sum(a * a for a in v1))
    norm_2 = math.sqrt(sum(b * b for b in v2))

    if norm_1 == 0 or norm_2 == 0:
        return 0.0

    return dot_prod / (norm_1 * norm_2)


def compute_hash(query: str) -> str:
    """
    Computes a SHA-256 hash for a given string query.

    Complexity: O(K) where K is the length of the string query.
    """
    encoded_query = query.encode('utf-8')
    return hashlib.sha256(encoded_query).hexdigest()


class EvictionPolicy(Enum):
    """
    Eviction strategy for a bounded tenant cache.

    LRU: on every hit the entry becomes most-recently-used; the oldest-used
         entry is evicted first.
    FIFO: hits do not change eviction order; the oldest-inserted entry is
          evicted first. Useful when hit-driven reordering is undesirable,
          e.g. workloads where recency of insertion approximates freshness.
    """
    LRU = "lru"
    FIFO = "fifo"


class CacheMetrics:
    """
    In-memory event counters for cache observability.

    Thread safety is provided by the caller's lock (``SemanticCache`` holds
    its reentrant lock while recording), so increments stay simple.
    """

    EVENTS = (
        "exact_hit",
        "semantic_hit",
        "miss",
        "expired",
        "evicted",
        "invalidated",
    )

    def __init__(self) -> None:
        """Initializes all counters to zero. Complexity: O(1)."""
        self._counts: Dict[str, int] = {event: 0 for event in self.EVENTS}

    def record(self, event: str) -> None:
        """
        Increments the counter for one event.

        Complexity: O(1).

        Raises:
            ValueError: If the event name is unknown.
        """
        if event not in self._counts:
            raise ValueError("Unknown metrics event: %r" % event)
        self._counts[event] += 1

    def snapshot(self) -> Dict[str, int]:
        """Returns a copy of the current counters. Complexity: O(E)."""
        return dict(self._counts)


class CacheEntry:
    """
    A single cached response, stamped with the tenant config version that
    produced it so system-prompt changes can invalidate it logically.
    """

    def __init__(self, query: str, embedding: List[float], response: Any,
                 expiration_time: float, config_version: str) -> None:
        """
        Initializes a new cache entry.

        Complexity: O(1).
        """
        self.query = query
        self.embedding = embedding
        self.response = response
        self.expiration_time = expiration_time
        self.config_version = config_version

    def is_expired(self, current_time: float) -> bool:
        """
        Checks if the cache entry has expired based on the current time.

        Complexity: O(1).
        """
        return current_time > self.expiration_time


class TenantCache:
    """
    Cache storage for one tenant: an OrderedDict keyed by query hash.

    Eviction order follows the configured ``EvictionPolicy``; expiry is lazy
    on access, exactly as in v1. All methods must be called under the
    orchestrator's lock when locking is enabled.
    """

    def __init__(self, capacity: int, tau: float, eviction_policy: EvictionPolicy,
                 metrics: CacheMetrics, tenant_id: str,
                 metrics_hook: Optional[Callable[[str, str], None]] = None) -> None:
        """
        Initializes the TenantCache.

        Complexity: O(1).
        """
        self.capacity = capacity
        self.tau = tau
        self.eviction_policy = eviction_policy
        self.metrics = metrics
        self.tenant_id = tenant_id
        self.metrics_hook = metrics_hook
        self.config_version: str = "1"
        self.expected_dimension: Optional[int] = None
        self.exact_cache: "OrderedDict[str, CacheEntry]" = OrderedDict()

    def _record(self, event: str) -> None:
        """Records a metrics event and invokes the optional hook. O(1)."""
        self.metrics.record(event)
        if self.metrics_hook is not None:
            self.metrics_hook(event, self.tenant_id)

    def _evict_if_needed(self) -> None:
        """
        Evicts from the front of the ordering while over capacity.

        Under LRU the front is the least recently used entry; under FIFO it is
        the oldest-inserted entry, because hits never reorder.

        Complexity: O(1) amortized.
        """
        while len(self.exact_cache) > self.capacity:
            self.exact_cache.popitem(last=False)
            self._record("evicted")

    def _cleanup_expired(self, current_time: float) -> None:
        """
        Removes all expired entries from the cache.

        Complexity: O(N) where N is the number of cache entries.
        """
        expired_keys = [key for key, entry in self.exact_cache.items()
                        if entry.is_expired(current_time)]
        for key in expired_keys:
            del self.exact_cache[key]
            self._record("expired")

    def _mark_used(self, key: str) -> None:
        """Applies the eviction policy's access semantics to a hit. O(1)."""
        if self.eviction_policy is EvictionPolicy.LRU:
            self.exact_cache.move_to_end(key)
        # FIFO: intentionally no reorder on access.

    def put(self, query: str, embedding: List[float], response: Any,
            ttl_seconds: float, current_time: float) -> None:
        """
        Inserts or replaces an entry, stamping it with the current
        ``config_version``. Enforces a consistent embedding dimension per
        tenant at write time.

        Complexity: O(K) for the query hash; eviction O(1) amortized.

        Raises:
            ValueError: If the embedding dimension differs from the tenant's
                established dimension.
        """
        if self.expected_dimension is None:
            self.expected_dimension = len(embedding)
        elif len(embedding) != self.expected_dimension:
            raise ValueError(
                "Embedding dimension %d does not match tenant dimension %d"
                % (len(embedding), self.expected_dimension)
            )

        self._cleanup_expired(current_time)
        q_hash = compute_hash(query)
        exp_time = current_time + ttl_seconds

        if q_hash in self.exact_cache:
            del self.exact_cache[q_hash]

        self.exact_cache[q_hash] = CacheEntry(
            query, embedding, response, exp_time, self.config_version
        )
        self._evict_if_needed()

    def get(self, query: str, embedding: List[float], current_time: float) -> Optional[Any]:
        """
        Retrieves a cached response via exact match, then best semantic match.

        Complexity: O(1) for exact match; O(N * D) for the semantic scan.

        Raises:
            ValueError: If the embedding dimension differs from the tenant's
                established dimension.
        """
        if self.expected_dimension is not None and len(embedding) != self.expected_dimension:
            raise ValueError(
                "Embedding dimension %d does not match tenant dimension %d"
                % (len(embedding), self.expected_dimension)
            )

        self._cleanup_expired(current_time)

        q_hash = compute_hash(query)
        if q_hash in self.exact_cache:
            entry = self.exact_cache[q_hash]
            if not entry.is_expired(current_time):
                self._mark_used(q_hash)
                self._record("exact_hit")
                return entry.response

        best_key: Optional[str] = None
        best_sim = -1.0

        for key, entry in self.exact_cache.items():
            if not entry.is_expired(current_time):
                sim = cosine_similarity(embedding, entry.embedding)
                if sim >= self.tau and sim > best_sim:
                    best_sim = sim
                    best_key = key

        if best_key is not None:
            self._mark_used(best_key)
            self._record("semantic_hit")
            return self.exact_cache[best_key].response

        self._record("miss")
        return None

    def invalidate_stale_versions(self) -> int:
        """
        Removes entries stamped with an older ``config_version`` than the
        current one.

        Complexity: O(N).

        Returns:
            The number of entries invalidated.
        """
        stale_keys = [key for key, entry in self.exact_cache.items()
                      if entry.config_version != self.config_version]
        for key in stale_keys:
            del self.exact_cache[key]
            self._record("invalidated")
        return len(stale_keys)


class _NullLock:
    """A no-op context manager used when locking is disabled."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        return False


class SemanticCache:
    """
    Orchestrator routing queries to per-tenant caches with namespace isolation.

    v2 concurrency contract: a single coarse reentrant lock serializes all
    cache operations. This favors correctness and simplicity over throughput;
    a production variant would shard the lock per tenant. For single-threaded
    callers, ``enable_locking=False`` removes the small lock overhead.

    Architecture is scoped as a single microcomponent with model/provider-
    independent interfaces. Production safety, tokenization, and embedding
    guarantees remain unsupported, as in v1.
    """

    def __init__(self, capacity: int = 1000, tau: float = 0.90,
                 eviction_policy: EvictionPolicy = EvictionPolicy.LRU,
                 metrics_hook: Optional[Callable[[str, str], None]] = None,
                 enable_locking: bool = True) -> None:
        """
        Initializes the SemanticCache orchestrator.

        Complexity: O(1).

        Raises:
            ValueError: If capacity < 1 or tau is outside (0.0, 1.0].
        """
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        if not 0.0 < tau <= 1.0:
            raise ValueError("tau must be in (0.0, 1.0]")
        self.capacity = capacity
        self.tau = tau
        self.eviction_policy = eviction_policy
        self.metrics_hook = metrics_hook
        self.metrics = CacheMetrics()
        self.namespaces: Dict[str, TenantCache] = {}
        self._lock = threading.RLock() if enable_locking else _NullLock()

    def _get_tenant_cache(self, tenant_id: str) -> TenantCache:
        """
        Retrieves or creates a TenantCache for the given tenant ID.

        Complexity: O(1) amortized. Must be called under the lock.
        """
        if tenant_id not in self.namespaces:
            self.namespaces[tenant_id] = TenantCache(
                self.capacity, self.tau, self.eviction_policy,
                self.metrics, tenant_id, self.metrics_hook,
            )
        return self.namespaces[tenant_id]

    @staticmethod
    def _validate_inputs(tenant_id: str, query: str, embedding: List[float]) -> None:
        """Validates shared get/put inputs. Complexity: O(1)."""
        if not tenant_id:
            raise ValueError("Tenant ID cannot be empty")
        if not query:
            raise ValueError("Query string cannot be empty")
        if not embedding:
            raise ValueError("Embedding vector cannot be empty")

    def put(self, tenant_id: str, query: str, embedding: List[float], response: Any,
            ttl_seconds: float = 3600.0, current_time: Optional[float] = None) -> None:
        """
        Routes the put request to the specific tenant's cache.

        Complexity: O(K) for the query hash; eviction O(1) amortized.

        Raises:
            ValueError: On empty tenant/query/embedding, or on an embedding
                dimension that differs from the tenant's established dimension.
        """
        self._validate_inputs(tenant_id, query, embedding)
        active_time = time.time() if current_time is None else current_time
        with self._lock:
            self._get_tenant_cache(tenant_id).put(
                query, embedding, response, ttl_seconds, active_time
            )

    def get(self, tenant_id: str, query: str, embedding: List[float],
            current_time: Optional[float] = None) -> Optional[Any]:
        """
        Routes the get request to the specific tenant's cache.

        Complexity: O(N * D) for semantic match, O(1) for exact match lookup.

        Raises:
            ValueError: On empty tenant/query/embedding, or on an embedding
                dimension that differs from the tenant's established dimension.
        """
        self._validate_inputs(tenant_id, query, embedding)
        active_time = time.time() if current_time is None else current_time
        with self._lock:
            if tenant_id not in self.namespaces:
                self.metrics.record("miss")
                if self.metrics_hook is not None:
                    self.metrics_hook("miss", tenant_id)
                return None
            return self.namespaces[tenant_id].get(query, embedding, active_time)

    def set_config_version(self, tenant_id: str, config_version: str) -> int:
        """
        Bumps a tenant's config version (e.g. after a system-prompt change) and
        invalidates every entry stamped with an older version.

        Complexity: O(N) for the tenant's entries.

        Returns:
            The number of entries invalidated.

        Raises:
            ValueError: If the tenant ID or config version is empty.
        """
        if not tenant_id:
            raise ValueError("Tenant ID cannot be empty")
        if not config_version:
            raise ValueError("Config version cannot be empty")
        with self._lock:
            tenant_cache = self._get_tenant_cache(tenant_id)
            tenant_cache.config_version = config_version
            return tenant_cache.invalidate_stale_versions()

    def metrics_snapshot(self) -> Dict[str, int]:
        """Returns a copy of the cache's metrics counters. Complexity: O(E)."""
        with self._lock:
            return self.metrics.snapshot()

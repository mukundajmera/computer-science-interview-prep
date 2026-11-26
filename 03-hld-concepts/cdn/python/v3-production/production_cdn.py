"""
V3: Production CDN with Cache Invalidation

Production-grade CDN simulator with versioning, purge API,
stale-while-revalidate, and comprehensive metrics.

Features:
- Versioned URL support
- Purge API with global propagation
- Stale-while-revalidate
- Cache-Control header parsing
- Metrics and monitoring
- Thread-safe operations
"""

import time
import threading
import re
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future
from collections import defaultdict


@dataclass
class CacheControl:
    """Cache control directives parsed from headers."""
    max_age_seconds: int = 3600
    stale_while_revalidate_seconds: int = 0
    no_cache: bool = False
    no_store: bool = False
    
    # Pre-compiled regex patterns for performance
    _MAX_AGE_PATTERN = re.compile(r'max-age=(\d+)')
    _SWR_PATTERN = re.compile(r'stale-while-revalidate=(\d+)')

    @classmethod
    def parse(cls, header: Optional[str]) -> 'CacheControl':
        """Parses Cache-Control header string."""
        if not header:
            return cls()
        
        max_age = 3600
        swr = 0
        no_cache = "no-cache" in header
        no_store = "no-store" in header
        
        max_age_match = cls._MAX_AGE_PATTERN.search(header)
        if max_age_match:
            max_age = int(max_age_match.group(1))
        
        swr_match = cls._SWR_PATTERN.search(header)
        if swr_match:
            swr = int(swr_match.group(1))
        
        return cls(max_age, swr, no_cache, no_store)


@dataclass
class CacheEntry:
    """Cache entry with TTL and stale-while-revalidate support."""
    content: str
    source: str
    was_cache_hit: bool
    expiration_time: float
    stale_until_time: float

    def is_fresh(self) -> bool:
        return time.time() < self.expiration_time

    def is_stale(self) -> bool:
        now = time.time()
        return self.expiration_time <= now < self.stale_until_time

    def is_expired(self) -> bool:
        return time.time() >= self.stale_until_time


@dataclass
class CdnResponse:
    """Response from CDN fetch."""
    content: str
    served_by_edge: str
    source: str
    latency_ms: float
    cache_hit: bool

    def __str__(self) -> str:
        return f"Edge: {self.served_by_edge}, Source: {self.source}, Latency: {self.latency_ms:.2f}ms, CacheHit: {self.cache_hit}"


@dataclass
class PurgeResult:
    """Result of a purge operation."""
    pattern: str
    nodes_affected: int
    duration_ms: float

    def __str__(self) -> str:
        return f"Purged '{self.pattern}' from {self.nodes_affected} nodes in {self.duration_ms:.0f}ms"


class CdnMetrics:
    """Thread-safe CDN metrics."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._purges = 0
        self._total_latency_ms = 0.0
        self._request_count = 0

    def record_hit(self) -> None:
        with self._lock:
            self._hits += 1

    def record_miss(self) -> None:
        with self._lock:
            self._misses += 1

    def record_purge(self) -> None:
        with self._lock:
            self._purges += 1

    def record_latency(self, ms: float) -> None:
        with self._lock:
            self._total_latency_ms += ms
            self._request_count += 1

    @property
    def hit_rate(self) -> float:
        with self._lock:
            total = self._hits + self._misses
            return (self._hits * 100.0 / total) if total > 0 else 0.0

    @property
    def average_latency_ms(self) -> float:
        with self._lock:
            return (self._total_latency_ms / self._request_count) if self._request_count > 0 else 0.0

    def __str__(self) -> str:
        with self._lock:
            return (f"CDN Metrics: Hits={self._hits}, Misses={self._misses}, "
                   f"HitRate={self.hit_rate:.2f}%, AvgLatency={self.average_latency_ms:.2f}ms, "
                   f"Purges={self._purges}")


class EdgeNode:
    """Edge node with production caching features."""
    
    def __init__(
        self,
        name: str,
        parent: Optional['EdgeNode'],
        origin: Optional[Callable[[str], str]],
        metrics: CdnMetrics,
        executor: ThreadPoolExecutor
    ):
        self.name = name
        self._parent = parent
        self._origin = origin
        self._metrics = metrics
        self._executor = executor
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._revalidating: Dict[str, bool] = {}

    def fetch(self, url: str, cc: CacheControl) -> CacheEntry:
        """Fetches content with cache control handling."""
        if cc.no_store:
            return self._fetch_from_upstream(url, cc)
        
        with self._lock:
            entry = self._cache.get(url)
        
        if entry is not None and entry.is_fresh() and not cc.no_cache:
            if self._parent is not None:
                self._metrics.record_hit()
            return CacheEntry(
                content=entry.content,
                source=f"{self.name} (hit)",
                was_cache_hit=True,
                expiration_time=entry.expiration_time,
                stale_until_time=entry.stale_until_time
            )
        
        if entry is not None and entry.is_stale() and not cc.no_cache:
            # Stale-while-revalidate
            self._trigger_revalidation(url, cc)
            if self._parent is not None:
                self._metrics.record_hit()
            return CacheEntry(
                content=entry.content,
                source=f"{self.name} (stale)",
                was_cache_hit=True,
                expiration_time=0,
                stale_until_time=0
            )
        
        if self._parent is not None:
            self._metrics.record_miss()
        return self._fetch_from_upstream(url, cc)

    def _fetch_from_upstream(self, url: str, cc: CacheControl) -> CacheEntry:
        if self._parent is not None:
            parent_entry = self._parent.fetch(url, cc)
            content = parent_entry.content
            source = parent_entry.source
        elif self._origin is not None:
            content = self._origin(url)
            source = "origin"
        else:
            return CacheEntry("", "none", False, 0, 0)
        
        if not cc.no_store and content:
            ttl_ms = cc.max_age_seconds
            swr_ms = cc.stale_while_revalidate_seconds
            new_entry = CacheEntry(
                content=content,
                source=source,
                was_cache_hit=False,
                expiration_time=time.time() + ttl_ms,
                stale_until_time=time.time() + ttl_ms + swr_ms
            )
            with self._lock:
                self._cache[url] = new_entry
        
        return CacheEntry(content, source, False, 0, 0)

    def _trigger_revalidation(self, url: str, cc: CacheControl) -> None:
        with self._lock:
            if url in self._revalidating:
                return
            self._revalidating[url] = True
        
        def revalidate():
            try:
                self._fetch_from_upstream(url, cc)
            finally:
                with self._lock:
                    del self._revalidating[url]
        
        self._executor.submit(revalidate)

    def purge(self, url_pattern: str) -> None:
        """Purges URLs matching pattern."""
        with self._lock:
            if url_pattern.endswith("*"):
                prefix = url_pattern[:-1]
                keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
                for key in keys_to_remove:
                    del self._cache[key]
            else:
                if url_pattern in self._cache:
                    del self._cache[url_pattern]


class ProductionCDN:
    """
    Production-grade CDN with comprehensive features.
    
    Example:
        cdn = ProductionCDN(origin_server)
        response = cdn.fetch("japan", "/video.mp4", {"Cache-Control": "max-age=3600"})
        cdn.purge("/video/*").result()
    """
    
    def __init__(self, origin: Callable[[str], str]):
        self._origin = origin
        self._metrics = CdnMetrics()
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        self._shield = EdgeNode("shield", None, origin, self._metrics, self._executor)
        
        regions = ["us-east", "us-west", "eu-west", "eu-central", "asia-east", "asia-south"]
        self._edges: Dict[str, EdgeNode] = {}
        for region in regions:
            self._edges[region] = EdgeNode(region, self._shield, None, 
                                          self._metrics, self._executor)

    def fetch(self, user_region: str, url: str, headers: Dict[str, str]) -> CdnResponse:
        """Fetches content with full CDN behavior."""
        edge = self._route_to_edge(user_region)
        start_time = time.time()
        
        cc = CacheControl.parse(headers.get("Cache-Control"))
        entry = edge.fetch(url, cc)
        
        latency_ms = (time.time() - start_time) * 1000
        self._metrics.record_latency(latency_ms)
        
        return CdnResponse(
            content=entry.content,
            served_by_edge=edge.name,
            source=entry.source,
            latency_ms=latency_ms,
            cache_hit=entry.was_cache_hit
        )

    def purge(self, url_pattern: str) -> Future:
        """Purges content globally across all edges."""
        start_time = time.time()
        
        def do_purge():
            self._shield.purge(url_pattern)
            for edge in self._edges.values():
                edge.purge(url_pattern)
            
            duration = (time.time() - start_time) * 1000
            self._metrics.record_purge()
            return PurgeResult(url_pattern, len(self._edges) + 1, duration)
        
        return self._executor.submit(do_purge)

    def warm_cache(self, url: str) -> Future:
        """Pre-warms cache by fetching content to all edges."""
        def warm():
            cc = CacheControl()
            for edge in self._edges.values():
                edge.fetch(url, cc)
        
        return self._executor.submit(warm)

    @property
    def metrics(self) -> CdnMetrics:
        return self._metrics

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False)

    def _route_to_edge(self, user_region: str) -> EdgeNode:
        region_lower = user_region.lower()
        if any(r in region_lower for r in ["asia", "japan", "korea"]):
            return self._edges.get("asia-east", self._edges["us-east"])
        elif any(r in region_lower for r in ["india", "australia"]):
            return self._edges.get("asia-south", self._edges["us-west"])
        elif any(r in region_lower for r in ["europe", "uk", "germany"]):
            return self._edges.get("eu-west", self._edges["us-east"])
        elif any(r in region_lower for r in ["west", "california"]):
            return self._edges.get("us-west", self._edges["us-east"])
        return self._edges["us-east"]


# Demo
if __name__ == "__main__":
    print("=== Production CDN Demo ===\n")
    
    def origin_fetch(url: str) -> str:
        time.sleep(0.1)
        return f"Content: {url} @ {time.time():.0f}"
    
    cdn = ProductionCDN(origin_fetch)
    
    # Basic caching
    print("=== Basic Caching ===")
    r1 = cdn.fetch("japan", "/video/movie.mp4", {})
    print(f"Request 1 (cold): {r1}")
    
    r2 = cdn.fetch("japan", "/video/movie.mp4", {})
    print(f"Request 2 (warm): {r2}")
    
    # Cache-Control headers
    print("\n=== Cache-Control Headers ===")
    r3 = cdn.fetch("germany", "/api/data.json", 
                   {"Cache-Control": "max-age=5, stale-while-revalidate=10"})
    print(f"With short TTL: {r3}")
    
    # Geographic routing
    print("\n=== Geographic Routing ===")
    regions = ["japan", "germany", "california", "india", "uk"]
    for region in regions:
        r = cdn.fetch(region, "/global/asset.js", {})
        print(f"User {region:12} -> {r}")
    
    # Cache warming
    print("\n=== Cache Warming ===")
    warm_url = "/launch/new-feature.js"
    print(f"Warming cache for: {warm_url}")
    cdn.warm_cache(warm_url).result()
    print("Cache warmed across all edges")
    
    # Purge API
    print("\n=== Purge API ===")
    purge_result = cdn.purge("/video/*").result()
    print(purge_result)
    
    r4 = cdn.fetch("japan", "/video/movie.mp4", {})
    print(f"After purge: {r4}")
    
    # Metrics
    print("\n=== CDN Metrics ===")
    print(cdn.metrics)
    
    cdn.shutdown()

"""
V2: Geographic CDN Simulator

Simulates a CDN with multiple edge locations and geographic routing.
Demonstrates how users are routed to nearest edge and how
content propagates through the CDN.

Features:
- Multiple edge nodes by region
- Geographic routing simulation
- Origin shield tier
- Latency simulation
"""

import time
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Cache entry with content and expiration."""
    content: str
    expiration_time: float

    def is_expired(self) -> bool:
        return time.time() > self.expiration_time


@dataclass
class FetchResult:
    """Result of a fetch operation."""
    content: str
    served_by: str
    latency_ms: float
    source: str

    def __str__(self) -> str:
        return f"Served by: {self.served_by}, Source: {self.source}, Latency: {self.latency_ms:.0f}ms"


class EdgeNode:
    """Edge node with caching capability."""
    
    def __init__(
        self,
        name: str,
        parent: Optional['EdgeNode'] = None,
        origin: Optional[Callable[[str], str]] = None,
        ttl_seconds: int = 300,
        base_latency_ms: int = 10
    ):
        self.name = name
        self._parent = parent
        self._origin = origin
        self._ttl = ttl_seconds
        self._base_latency_ms = base_latency_ms
        self._cache: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
        self._last_source = ""

    def fetch(self, url: str) -> str:
        """Fetches content from cache or upstream."""
        self._simulate_latency(self._base_latency_ms)
        
        entry = self._cache.get(url)
        if entry is not None and not entry.is_expired():
            self._hits += 1
            self._last_source = f"{self.name} (cache)"
            return entry.content
        
        self._misses += 1
        
        if self._parent is not None:
            content = self._parent.fetch(url)
            self._last_source = self._parent.last_source
        elif self._origin is not None:
            content = self._origin(url)
            self._last_source = "origin"
        else:
            return ""
        
        if content:
            self._cache[url] = CacheEntry(
                content=content,
                expiration_time=time.time() + self._ttl
            )
        
        return content

    def purge(self, url: str) -> None:
        """Removes URL from cache."""
        if url in self._cache:
            del self._cache[url]

    @property
    def last_source(self) -> str:
        return self._last_source

    def get_stats(self) -> str:
        total = self._hits + self._misses
        hit_rate = (self._hits * 100.0 / total) if total > 0 else 0
        return f"Hits: {self._hits}, Misses: {self._misses}, Hit Rate: {hit_rate:.1f}%"

    def _simulate_latency(self, ms: int) -> None:
        time.sleep(ms / 1000.0)


class GeographicCDN:
    """
    CDN with geographic routing and tiered caching.
    
    Example:
        cdn = GeographicCDN(origin_server, shield_ttl=60, edge_ttl=30)
        result = cdn.fetch("japan", "/video/movie.mp4")
    """
    
    def __init__(
        self,
        origin: Callable[[str], str],
        shield_ttl_seconds: int = 60,
        edge_ttl_seconds: int = 30
    ):
        self._origin = origin
        self._shield = EdgeNode("shield", None, origin, shield_ttl_seconds, 50)
        self._edges: Dict[str, EdgeNode] = {
            "us-east": EdgeNode("us-east", self._shield, None, edge_ttl_seconds, 10),
            "us-west": EdgeNode("us-west", self._shield, None, edge_ttl_seconds, 10),
            "eu-west": EdgeNode("eu-west", self._shield, None, edge_ttl_seconds, 10),
            "asia-east": EdgeNode("asia-east", self._shield, None, edge_ttl_seconds, 10),
        }

    def route_to_edge(self, user_region: str) -> EdgeNode:
        """Routes user to nearest edge based on their region."""
        edge_region = self._map_user_to_edge(user_region)
        return self._edges.get(edge_region, self._edges["us-east"])

    def _map_user_to_edge(self, user_region: str) -> str:
        region_lower = user_region.lower()
        if any(r in region_lower for r in ["asia", "japan", "korea", "china"]):
            return "asia-east"
        elif any(r in region_lower for r in ["europe", "uk", "germany"]):
            return "eu-west"
        elif any(r in region_lower for r in ["california", "oregon", "washington"]):
            return "us-west"
        return "us-east"

    def fetch(self, user_region: str, url: str) -> FetchResult:
        """Fetches content for a user from their nearest edge."""
        edge = self.route_to_edge(user_region)
        start_time = time.time()
        
        content = edge.fetch(url)
        
        latency_ms = (time.time() - start_time) * 1000
        return FetchResult(content, edge.name, latency_ms, edge.last_source)

    def purge_global(self, url: str) -> None:
        """Purges content from all edges and shield."""
        self._shield.purge(url)
        for edge in self._edges.values():
            edge.purge(url)
        print(f"Global purge: {url}")

    def print_stats(self) -> None:
        """Prints statistics for all nodes."""
        print("\n=== CDN Statistics ===")
        print(f"Shield: {self._shield.get_stats()}")
        for name, edge in self._edges.items():
            print(f"{name}: {edge.get_stats()}")


# Demo
if __name__ == "__main__":
    print("=== Geographic CDN Demo ===\n")
    
    def origin_fetch(url: str) -> str:
        time.sleep(0.2)  # Simulate origin latency
        return f"Content: {url}"
    
    cdn = GeographicCDN(origin_fetch, shield_ttl_seconds=60, edge_ttl_seconds=30)
    
    # User from Japan requests content
    print("=== User from Japan ===")
    result1 = cdn.fetch("japan", "/video/popular.mp4")
    print(f"Request 1: {result1}")
    
    result2 = cdn.fetch("japan", "/video/popular.mp4")
    print(f"Request 2: {result2}")
    
    # User from Germany
    print("\n=== User from Germany ===")
    result3 = cdn.fetch("germany", "/video/popular.mp4")
    print(f"Request 1: {result3}")
    print("(Shield already has content, no origin fetch)")
    
    # Multiple users
    print("\n=== Multiple Users, Same Content ===")
    regions = ["japan", "germany", "california", "uk", "korea", "oregon"]
    for region in regions:
        result = cdn.fetch(region, "/video/popular.mp4")
        print(f"User from {region:12} -> Edge: {result.served_by:10} Source: {result.source}")
    
    # Global purge
    print("\n=== Global Purge ===")
    cdn.purge_global("/video/popular.mp4")
    
    result4 = cdn.fetch("japan", "/video/popular.mp4")
    print(f"Japan after purge: {result4}")
    
    cdn.print_stats()

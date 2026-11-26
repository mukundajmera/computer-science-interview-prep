"""
URL Shortener - V3 Distributed

Global load balancer, health checking, and conflict resolution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set, Optional
from abc import ABC, abstractmethod
from enum import Enum
import threading
import time


class RegionStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class RegionHealth:
    """Region health information."""
    region: str
    status: RegionStatus = RegionStatus.HEALTHY
    last_health_check: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    latency_ms: float = 0.0
    
    def record_success(self, latency: float) -> None:
        self.status = RegionStatus.HEALTHY
        self.last_health_check = time.time()
        self.consecutive_failures = 0
        self.latency_ms = latency
    
    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.last_health_check = time.time()
        
        if self.consecutive_failures >= 3:
            self.status = RegionStatus.UNHEALTHY
        elif self.consecutive_failures >= 1:
            self.status = RegionStatus.DEGRADED
    
    def is_healthy(self) -> bool:
        return self.status == RegionStatus.HEALTHY


class GlobalLoadBalancer(ABC):
    """Global load balancer interface."""
    
    @abstractmethod
    def get_best_region(self, client_location: str) -> str:
        """Get the best region for a request."""
        pass
    
    @abstractmethod
    def get_healthy_regions(self) -> Set[str]:
        """Get healthy regions."""
        pass
    
    @abstractmethod
    def mark_unhealthy(self, region: str) -> None:
        """Mark a region as unhealthy."""
        pass
    
    @abstractmethod
    def mark_healthy(self, region: str) -> None:
        """Mark a region as healthy."""
        pass


class GeographicLoadBalancer(GlobalLoadBalancer):
    """Geographic load balancer implementation."""
    
    def __init__(self, location_preferences: Dict[str, List[str]],
                 regions: Set[str]):
        self._location_preferences = dict(location_preferences)
        self._region_health: Dict[str, RegionHealth] = {
            region: RegionHealth(region=region) for region in regions
        }
        self._lock = threading.Lock()
    
    def get_best_region(self, client_location: str) -> str:
        preferences = self._location_preferences.get(client_location, [])
        
        # Find first healthy region in preference order
        for region in preferences:
            health = self._region_health.get(region)
            if health and health.is_healthy():
                return region
        
        # Fallback: any healthy region
        for health in self._region_health.values():
            if health.is_healthy():
                return health.region
        
        # All unhealthy - return first preference
        if preferences:
            return preferences[0]
        
        # Last resort
        return next(iter(self._region_health.keys()))
    
    def get_healthy_regions(self) -> Set[str]:
        return {
            region for region, health in self._region_health.items()
            if health.is_healthy()
        }
    
    def mark_unhealthy(self, region: str) -> None:
        health = self._region_health.get(region)
        if health:
            health.record_failure()
    
    def mark_healthy(self, region: str) -> None:
        health = self._region_health.get(region)
        if health:
            health.record_success(0)
    
    def update_health(self, region: str, latency_ms: float,
                      success: bool) -> None:
        with self._lock:
            health = self._region_health.get(region)
            if health:
                if success:
                    health.record_success(latency_ms)
                else:
                    health.record_failure()
    
    def get_region_health(self) -> Dict[str, RegionHealth]:
        return dict(self._region_health)


class HealthCheckService(threading.Thread):
    """Health check service for monitoring regions."""
    
    def __init__(self, load_balancer: GeographicLoadBalancer,
                 health_endpoints: Dict[str, str],
                 check_interval_seconds: float = 30.0):
        super().__init__(daemon=True)
        self._load_balancer = load_balancer
        self._health_endpoints = health_endpoints
        self._check_interval = check_interval_seconds
        self._running = True
    
    def run(self) -> None:
        while self._running:
            for region, endpoint in self._health_endpoints.items():
                try:
                    start = time.time()
                    healthy = self._check_health(endpoint)
                    latency = (time.time() - start) * 1000
                    
                    self._load_balancer.update_health(region, latency, healthy)
                    
                except Exception as e:
                    self._load_balancer.mark_unhealthy(region)
                    print(f"Health check failed for {region}: {e}")
            
            time.sleep(self._check_interval)
    
    def _check_health(self, endpoint: str) -> bool:
        """Check health of an endpoint."""
        # Simulated - in production use HTTP client
        return True
    
    def stop(self) -> None:
        self._running = False


# Conflict Resolution

class ConflictResolutionStrategy(Enum):
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"


@dataclass
class VectorClock:
    """Vector clock for causality tracking."""
    clocks: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, node_id: str) -> None:
        self.clocks[node_id] = self.clocks.get(node_id, 0) + 1
    
    def merge(self, other: 'VectorClock') -> 'VectorClock':
        merged = dict(self.clocks)
        for node_id, count in other.clocks.items():
            merged[node_id] = max(merged.get(node_id, 0), count)
        return VectorClock(clocks=merged)
    
    def happened_before(self, other: 'VectorClock') -> bool:
        """Check if this clock happened before another."""
        at_least_one_less = False
        
        for node_id, value in self.clocks.items():
            other_value = other.clocks.get(node_id, 0)
            if value > other_value:
                return False
            if value < other_value:
                at_least_one_less = True
        
        for node_id in other.clocks:
            if node_id not in self.clocks and other.clocks[node_id] > 0:
                at_least_one_less = True
        
        return at_least_one_less
    
    def is_concurrent(self, other: 'VectorClock') -> bool:
        """Check if clocks are concurrent."""
        return not self.happened_before(other) and not other.happened_before(self)


@dataclass
class VersionedUrlEntity:
    """Versioned URL entity for conflict detection."""
    short_code: str
    long_url: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    origin_region: str = ""
    version: int = 0
    vector_clock: VectorClock = field(default_factory=VectorClock)


class ConflictResolver:
    """Conflict resolver for multi-region consistency."""
    
    def __init__(self, strategy: ConflictResolutionStrategy):
        self._strategy = strategy
    
    def resolve(self, local: Optional[VersionedUrlEntity],
                remote: Optional[VersionedUrlEntity]) -> Optional[VersionedUrlEntity]:
        if local is None:
            return remote
        if remote is None:
            return local
        
        # Check causality
        if local.vector_clock.happened_before(remote.vector_clock):
            return remote
        if remote.vector_clock.happened_before(local.vector_clock):
            return local
        
        # Concurrent - apply strategy
        if self._strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            return local if local.updated_at > remote.updated_at else remote
        elif self._strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
            return local if local.created_at < remote.created_at else remote
        else:
            # Default to last write wins
            return local if local.updated_at > remote.updated_at else remote


class SyncManager:
    """Sync manager for cross-region synchronization."""
    
    def __init__(self, local_region: str,
                 regional_services: Dict[str, 'RegionalService'],
                 conflict_resolver: ConflictResolver):
        self._local_region = local_region
        self._regional_services = regional_services
        self._conflict_resolver = conflict_resolver
        self._sync_positions: Dict[str, int] = {}
    
    def sync_with_region(self, remote_region: str) -> int:
        """Sync with a remote region."""
        # In production: Get changes since last sync position
        return 0
    
    def full_sync(self) -> int:
        """Full sync across all regions."""
        total = 0
        for region in self._regional_services:
            if region != self._local_region:
                total += self.sync_with_region(region)
        return total


class AntiEntropyService(threading.Thread):
    """Anti-entropy service for detecting inconsistencies."""
    
    def __init__(self, sync_manager: SyncManager,
                 interval_seconds: float = 300.0):
        super().__init__(daemon=True)
        self._sync_manager = sync_manager
        self._interval = interval_seconds
        self._running = True
    
    def run(self) -> None:
        while self._running:
            try:
                synced = self._sync_manager.full_sync()
                if synced > 0:
                    print(f"Anti-entropy: synced {synced} records")
            except Exception as e:
                print(f"Anti-entropy error: {e}")
            
            time.sleep(self._interval)
    
    def stop(self) -> None:
        self._running = False

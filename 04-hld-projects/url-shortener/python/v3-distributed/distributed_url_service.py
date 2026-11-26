from enum import Enum
"""
URL Shortener - V3 Distributed

Multi-region distributed URL shortening service.
Handles global traffic with regional routing and replication.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Callable, TypeVar
from abc import ABC, abstractmethod
import threading
import hashlib
from concurrent.futures import ThreadPoolExecutor


T = TypeVar('T')


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int
    misses: int
    evictions: int
    
    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class DistributedCache(ABC):
    """Distributed cache interface for multi-region caching."""
    
    @abstractmethod
    def get(self, short_code: str) -> Optional[str]:
        """Get from cache."""
        pass
    
    @abstractmethod
    def get_local(self, short_code: str) -> Optional[str]:
        """Get from local cache only."""
        pass
    
    @abstractmethod
    def put(self, short_code: str, long_url: str, ttl_seconds: int) -> None:
        """Put in cache."""
        pass
    
    @abstractmethod
    def evict(self, short_code: str) -> None:
        """Evict from local cache."""
        pass
    
    @abstractmethod
    def invalidate_global(self, short_code: str) -> None:
        """Invalidate across all regions."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class CircuitBreaker(ABC):
    """Circuit breaker for fault tolerance."""
    
    @abstractmethod
    def is_open(self) -> bool:
        """Check if circuit is open."""
        pass
    
    @abstractmethod
    def record_success(self) -> None:
        """Record a success."""
        pass
    
    @abstractmethod
    def record_failure(self) -> None:
        """Record a failure."""
        pass
    
    @abstractmethod
    def execute(self, operation: Callable[[], T], 
                fallback: Callable[[], T]) -> T:
        """Execute with circuit breaker protection."""
        pass


class SimpleCircuitBreaker(CircuitBreaker):
    """Simple circuit breaker implementation."""
    
    def __init__(self, failure_threshold: int = 5, reset_time_ms: int = 30000):
        self._failure_threshold = failure_threshold
        self._reset_time_ms = reset_time_ms
        self._failure_count = 0
        self._last_failure_time = 0
        self._open = False
        self._lock = threading.Lock()
    
    def is_open(self) -> bool:
        with self._lock:
            if self._open:
                import time
                if (time.time() * 1000) - self._last_failure_time > self._reset_time_ms:
                    self._open = False
                    self._failure_count = 0
            return self._open
    
    def record_success(self) -> None:
        with self._lock:
            self._failure_count = 0
            self._open = False
    
    def record_failure(self) -> None:
        with self._lock:
            import time
            self._failure_count += 1
            self._last_failure_time = time.time() * 1000
            
            if self._failure_count >= self._failure_threshold:
                self._open = True
    
    def execute(self, operation: Callable[[], T], 
                fallback: Callable[[], T]) -> T:
        if self.is_open():
            return fallback()
        
        try:
            result = operation()
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            return fallback()


class ConsistentHashRouter:
    """Consistent hash router for data placement."""
    
    def __init__(self, regions: Set[str], virtual_nodes: int = 100):
        self._ring: Dict[int, str] = {}
        self._virtual_nodes = virtual_nodes
        
        for region in regions:
            self._add_region(region)
    
    def _add_region(self, region: str) -> None:
        for i in range(self._virtual_nodes):
            key = f"{region}-{i}"
            hash_val = self._hash(key)
            self._ring[hash_val] = region
    
    def get_region(self, key: str) -> str:
        if not self._ring:
            raise RuntimeError("No regions available")
        
        hash_val = self._hash(key)
        
        # Find first node with hash >= key hash
        sorted_hashes = sorted(self._ring.keys())
        
        for node_hash in sorted_hashes:
            if node_hash >= hash_val:
                return self._ring[node_hash]
        
        # Wrap around
        return self._ring[sorted_hashes[0]]
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31)


class RegionalService(ABC):
    """Regional service interface."""
    
    @abstractmethod
    def create_url(self, request, base_url: str) -> dict:
        pass
    
    @abstractmethod
    def get_url(self, short_code: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def get_stats(self, short_code: str) -> Optional[dict]:
        pass
    
    @abstractmethod
    def delete_url(self, short_code: str) -> bool:
        pass
    
    @abstractmethod
    def replicate(self, short_code: str, long_url: str) -> None:
        pass
    
    @abstractmethod
    def get_region(self) -> str:
        pass


class ReplicationManager:
    """Replication manager for async cross-region replication."""
    
    def __init__(self, regional_services: Dict[str, RegionalService]):
        self._regional_services = regional_services
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def replicate_async(self, short_code: str, long_url: str,
                       target_regions: List[str]) -> None:
        for region in target_regions:
            self._executor.submit(
                self._replicate_to_region,
                short_code, long_url, region
            )
    
    def _replicate_to_region(self, short_code: str, long_url: str,
                            region: str) -> None:
        try:
            service = self._regional_services.get(region)
            if service:
                service.replicate(short_code, long_url)
        except Exception as e:
            print(f"Replication failed to {region}: {e}")
    
    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)


class MultiRegionUrlService:
    """
    Multi-region URL shortening service.
    Handles cross-region replication and conflict resolution.
    """
    
    def __init__(self, current_region: str,
                 regional_services: Dict[str, RegionalService],
                 cache: DistributedCache,
                 base_url: str):
        self._current_region = current_region
        self._regional_services = regional_services
        self._router = ConsistentHashRouter(set(regional_services.keys()))
        self._cache = cache
        self._replication_manager = ReplicationManager(regional_services)
        self._circuit_breaker = SimpleCircuitBreaker(5, 30000)
        self._base_url = base_url
    
    def create_short_url(self, request) -> dict:
        """Create URL locally and replicate."""
        local_service = self._regional_services[self._current_region]
        response = local_service.create_url(request, self._base_url)
        
        # Async replication to other regions
        other_regions = [
            r for r in self._regional_services.keys()
            if r != self._current_region
        ]
        
        self._replication_manager.replicate_async(
            response['short_code'],
            request.long_url,
            other_regions
        )
        
        # Populate cache
        self._cache.put(response['short_code'], request.long_url, 86400)
        
        return response
    
    def get_original_url(self, short_code: str) -> Optional[str]:
        """Get URL with cache and fallback."""
        # Try local cache
        cached = self._cache.get_local(short_code)
        if cached:
            return cached
        
        # Try distributed cache
        cached = self._cache.get(short_code)
        if cached:
            return cached
        
        # Determine data region
        data_region = self.get_data_region(short_code)
        service = self._regional_services[data_region]
        
        # Execute with circuit breaker
        def operation():
            url = service.get_url(short_code)
            if url:
                self._cache.put(short_code, url, 86400)
            return url
        
        def fallback():
            # Try other regions
            for region, svc in self._regional_services.items():
                if region != data_region:
                    url = svc.get_url(short_code)
                    if url:
                        return url
            return None
        
        return self._circuit_breaker.execute(operation, fallback)
    
    def get_stats(self, short_code: str) -> Optional[dict]:
        data_region = self.get_data_region(short_code)
        return self._regional_services[data_region].get_stats(short_code)
    
    def delete_url(self, short_code: str) -> bool:
        """Delete from all regions."""
        deleted = False
        for service in self._regional_services.values():
            if service.delete_url(short_code):
                deleted = True
        
        self._cache.invalidate_global(short_code)
        return deleted
    
    def get_current_region(self) -> str:
        return self._current_region
    
    def get_data_region(self, short_code: str) -> str:
        return self._router.get_region(short_code)
    
    def replicate_to_regions(self, short_code: str,
                            target_regions: List[str]) -> None:
        local_service = self._regional_services[self._current_region]
        url = local_service.get_url(short_code)
        
        if url:
            for region in target_regions:
                if region != self._current_region:
                    self._regional_services[region].replicate(short_code, url)


# ============================================================================
# Pattern Integration Hooks (Real-time transport, contention, workflow durability)
# ============================================================================

class DeliveryMode(Enum):
    POLLING = "POLLING"
    LONG_POLLING = "LONG_POLLING"
    SSE = "SSE"
    WEBSOCKET = "WEBSOCKET"
    # WebRTC could be used for peer handoff of QR previews if needed.


class ContentionPolicy(Enum):
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"
    SERIAL_QUEUE = "SERIAL_QUEUE"
    DISTRIBUTED_LOCK = "DISTRIBUTED_LOCK"


@dataclass
class ExecutionResult:
    success: bool
    checkpoint_id: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False


class WorkflowStep(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def execute(self) -> ExecutionResult:
        ...


class CompensationStep(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def compensate(self, checkpoint_id: Optional[str]) -> None:
        ...


class WorkflowOrchestrator(ABC):
    @abstractmethod
    def run_step(self, step: WorkflowStep, idempotency_key: str, store: "IdempotencyStore") -> ExecutionResult:
        ...

    @abstractmethod
    def register_compensation(self, checkpoint_id: str, compensation_step: CompensationStep) -> None:
        ...


class IdempotencyStore(ABC):
    @abstractmethod
    def has_processed(self, key: str) -> bool:
        ...

    @abstractmethod
    def mark_processed(self, key: str, result: ExecutionResult) -> None:
        ...

    @abstractmethod
    def get_result(self, key: str) -> Optional[ExecutionResult]:
        ...

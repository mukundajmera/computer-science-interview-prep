"""
E-commerce Backend - V3 Distributed Implementation

Multi-region deployment with global inventory coordination,
cross-region order routing, and partition tolerance.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set
from datetime import datetime
from decimal import Decimal
from abc import ABC, abstractmethod
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
import threading


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Product:
    product_id: str = ""
    name: str = ""
    price: Decimal = Decimal("0")
    regional_stock: int = 0


@dataclass
class OrderItem:
    product_id: str
    quantity: int


@dataclass
class Order:
    order_id: str = ""
    user_id: str = ""


@dataclass
class CreateOrderRequest:
    shipping_address_id: str = ""
    payment_method_id: str = ""


@dataclass
class InventoryReservation:
    reservation_id: str
    items: List[OrderItem]
    region: str
    expires_at: datetime


@dataclass
class OrderSyncEvent:
    order: Order
    source_region: str
    timestamp: datetime


# ============================================================================
# Exceptions
# ============================================================================

class InsufficientInventoryException(Exception):
    pass


class InsufficientGlobalInventoryException(Exception):
    pass


# ============================================================================
# Pattern Integration Hooks (Real-time transport, contention, workflow durability)
# ============================================================================

class DeliveryMode(Enum):
    POLLING = "POLLING"
    LONG_POLLING = "LONG_POLLING"
    SSE = "SSE"
    WEBSOCKET = "WEBSOCKET"
    # WebRTC can be layered for media/voice handoff when P2P is acceptable.


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


# ============================================================================
# Interfaces
# ============================================================================

class CrossRegionMessaging(ABC):
    @abstractmethod
    def forward_order(self, region: str, user_id: str,
                      request: CreateOrderRequest) -> Future:
        pass


class InventoryReplicationService(ABC):
    @abstractmethod
    def schedule_transfer(self, product_id: str, to_region: str,
                          quantity: int) -> None:
        pass


class GeoSearchIndex(ABC):
    """Geo lookup abstraction for location-indexed entities."""

    @abstractmethod
    def nearby_entities(
        self, lat: float, lng: float, radius_km: float, limit: int
    ) -> List["GeoSearchHit"]:
        pass

    @abstractmethod
    def upsert_position(
        self, entity_type: str, entity_id: str, lat: float, lng: float, timestamp_ms: int
    ) -> None:
        pass


@dataclass(frozen=True)
class GeoSearchHit:
    entity_id: str
    distance_km: float


class MessageQueue(ABC):
    @abstractmethod
    def publish(self, topic: str, message) -> None:
        pass
    
    @abstractmethod
    def poll_batch(self, topic: str, max_messages: int) -> List:
        pass


class OrderRepository(ABC):
    @abstractmethod
    def upsert(self, order: Order) -> None:
        pass


# ============================================================================
# Geo Router
# ============================================================================

class GeoRouter:
    """Routes requests to appropriate region based on geography."""
    
    def get_optimal_region(self, lat: float, lng: float) -> str:
        """Determine optimal region for coordinates."""
        if lng < -100:
            return "us-west"
        elif lng < -30:
            return "us-east"
        elif lng < 40:
            return "eu-west"
        else:
            return "ap-south"


# ============================================================================
# Region Service
# ============================================================================

class RegionService:
    """Service instance for a specific region."""
    
    def __init__(self, region: str):
        self.region = region
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def create_order(self, user_id: str, request: CreateOrderRequest) -> Future:
        """Create order in this region."""
        return self.executor.submit(self._create_order_sync, user_id, request)
    
    def _create_order_sync(self, user_id: str,
                           request: CreateOrderRequest) -> Order:
        """Synchronous order creation."""
        return Order()
    
    def get_product(self, product_id: str) -> Product:
        """Get product from this region."""
        return Product(product_id=product_id)
    
    def shutdown(self):
        """Shutdown the service."""
        self.executor.shutdown(wait=True)


# ============================================================================
# Inventory Record
# ============================================================================

class InventoryRecord:
    """Thread-safe inventory record."""
    
    def __init__(self, product_id: str, available: int):
        self.product_id = product_id
        self._available = available
        self._reserved = 0
        self._lock = threading.Lock()
    
    @property
    def available(self) -> int:
        return self._available
    
    def try_reserve(self, quantity: int) -> bool:
        """Try to reserve quantity atomically."""
        with self._lock:
            if self._available >= quantity:
                self._available -= quantity
                self._reserved += quantity
                return True
            return False
    
    def commit(self, quantity: int) -> None:
        """Commit a reservation."""
        with self._lock:
            self._reserved -= quantity
    
    def release(self, quantity: int) -> None:
        """Release a reservation."""
        with self._lock:
            self._reserved -= quantity
            self._available += quantity


# ============================================================================
# Regional Inventory
# ============================================================================

class RegionalInventory:
    """Inventory management for a specific region."""
    
    def __init__(self, region: str):
        self.region = region
        self.inventory: Dict[str, InventoryRecord] = {}
        self.reservations: Dict[str, InventoryReservation] = {}
        self._lock = threading.Lock()
    
    def get_available_quantity(self, product_id: str) -> int:
        """Get available quantity for a product."""
        record = self.inventory.get(product_id)
        return record.available if record else 0
    
    def reserve(self, reservation_id: str,
                items: List[OrderItem]) -> InventoryReservation:
        """Reserve inventory for items."""
        with self._lock:
            # Try to reserve all items
            for item in items:
                record = self.inventory.get(item.product_id)
                if not record or not record.try_reserve(item.quantity):
                    # Rollback previous reservations
                    raise InsufficientInventoryException(item.product_id)
            
            # Create reservation
            from datetime import timedelta
            reservation = InventoryReservation(
                reservation_id=reservation_id,
                items=items,
                region=self.region,
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            self.reservations[reservation_id] = reservation
            return reservation
    
    def commit(self, reservation_id: str) -> None:
        """Commit a reservation."""
        with self._lock:
            reservation = self.reservations.get(reservation_id)
            if reservation:
                for item in reservation.items:
                    record = self.inventory.get(item.product_id)
                    if record:
                        record.commit(item.quantity)
                del self.reservations[reservation_id]
    
    def release(self, reservation_id: str) -> None:
        """Release a reservation."""
        with self._lock:
            reservation = self.reservations.get(reservation_id)
            if reservation:
                for item in reservation.items:
                    record = self.inventory.get(item.product_id)
                    if record:
                        record.release(item.quantity)
                del self.reservations[reservation_id]


# ============================================================================
# Global Inventory Coordinator
# ============================================================================

class GlobalInventoryCoordinator:
    """Coordinates inventory across all regions."""
    
    def __init__(self, regional_inventories: Dict[str, RegionalInventory],
                 replication_service: InventoryReplicationService):
        self.regional_inventories = regional_inventories
        self.replication_service = replication_service
    
    def get_regional_stock(self, product_id: str, region: str) -> int:
        """Get stock in a specific region."""
        inv = self.regional_inventories.get(region)
        return inv.get_available_quantity(product_id) if inv else 0
    
    def get_global_stock(self, product_id: str) -> int:
        """Get total stock across all regions."""
        return sum(
            inv.get_available_quantity(product_id)
            for inv in self.regional_inventories.values()
        )
    
    def reserve_global(self, reservation_id: str, items: List[OrderItem],
                       preferred_region: str) -> InventoryReservation:
        """Reserve inventory with cross-region coordination."""
        # Try preferred region first
        preferred = self.regional_inventories.get(preferred_region)
        if preferred and self._can_fulfill(preferred, items):
            return preferred.reserve(reservation_id, items)
        
        # Try other regions
        for region, inv in self.regional_inventories.items():
            if region != preferred_region and self._can_fulfill(inv, items):
                return inv.reserve(reservation_id, items)
        
        raise InsufficientGlobalInventoryException(
            "Cannot fulfill order globally"
        )
    
    def _can_fulfill(self, inventory: RegionalInventory,
                     items: List[OrderItem]) -> bool:
        """Check if region can fulfill all items."""
        for item in items:
            if inventory.get_available_quantity(item.product_id) < item.quantity:
                return False
        return True
    
    def rebalance_inventory(self, product_id: str) -> None:
        """Rebalance inventory across regions based on demand."""
        current_stock = {
            region: self.get_regional_stock(product_id, region)
            for region in self.regional_inventories
        }
        
        demand_score = {
            region: self._calculate_demand_score(product_id, region)
            for region in self.regional_inventories
        }
        
        total_stock = self.get_global_stock(product_id)
        optimal = self._calculate_optimal_distribution(total_stock, demand_score)
        
        for region, optimal_qty in optimal.items():
            current = current_stock[region]
            if current < optimal_qty:
                needed = optimal_qty - current
                self._transfer_inventory(product_id, region, needed)
    
    def _calculate_demand_score(self, product_id: str, region: str) -> float:
        """Calculate demand score for a region.
        
        Note: Stub implementation for HLD demonstration.
        In production, calculate based on:
        - Recent order volume
        - Page views / cart additions
        - Seasonal patterns
        - Historical trends
        """
        # TODO: Implement actual demand scoring
        return 1.0
    
    def _calculate_optimal_distribution(self, total_stock: int,
                                         demand_score: Dict[str, float]) -> Dict[str, int]:
        """Calculate optimal stock distribution."""
        total_demand = sum(demand_score.values())
        if total_demand == 0:
            return {r: 0 for r in demand_score}
        
        return {
            region: int(total_stock * (score / total_demand))
            for region, score in demand_score.items()
        }
    
    def _transfer_inventory(self, product_id: str, to_region: str,
                            quantity: int) -> None:
        """Schedule inventory transfer to a region."""
        self.replication_service.schedule_transfer(product_id, to_region, quantity)


# ============================================================================
# Circuit Breaker
# ============================================================================

class CircuitBreaker:
    """Circuit breaker for cross-region communication."""
    
    def __init__(self, threshold: int = 5, reset_timeout_ms: int = 30000):
        self.threshold = threshold
        self.reset_timeout_ms = reset_timeout_ms
        self._states: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def is_open(self, region: str) -> bool:
        """Check if circuit is open for a region."""
        with self._lock:
            state = self._states.get(region)
            if not state:
                return False
            
            if state['is_open']:
                import time
                elapsed = (time.time() * 1000) - state['last_failure']
                if elapsed > self.reset_timeout_ms:
                    state['is_open'] = False
                    state['failures'] = 0
            
            return state['is_open']
    
    def record_success(self, region: str) -> None:
        """Record a successful request."""
        with self._lock:
            if region in self._states:
                self._states[region]['failures'] = 0
                self._states[region]['is_open'] = False
    
    def record_failure(self, region: str) -> None:
        """Record a failed request."""
        with self._lock:
            if region not in self._states:
                self._states[region] = {
                    'failures': 0,
                    'last_failure': 0,
                    'is_open': False
                }
            
            import time
            state = self._states[region]
            state['failures'] += 1
            state['last_failure'] = time.time() * 1000
            
            if state['failures'] >= self.threshold:
                state['is_open'] = True


# ============================================================================
# Fallback Strategy
# ============================================================================

class FallbackStrategy:
    """Determines fallback regions for failed requests."""
    
    def __init__(self):
        self.fallbacks = {
            "us-east": "us-west",
            "us-west": "us-east",
            "eu-west": "us-east",
            "ap-south": "eu-west"
        }
    
    def get_fallback(self, region: str) -> str:
        """Get fallback region."""
        return self.fallbacks.get(region, "us-east")


# ============================================================================
# Cross-Region Order Router
# ============================================================================

class CrossRegionOrderRouter:
    """Routes orders across regions with circuit breaker."""
    
    def __init__(self, regions: Dict[str, RegionService]):
        self.regions = regions
        self.circuit_breaker = CircuitBreaker()
        self.fallback_strategy = FallbackStrategy()
    
    def route_order(self, target_region: str, user_id: str,
                    request: CreateOrderRequest) -> Future:
        """Route order with circuit breaker and fallback."""
        if self.circuit_breaker.is_open(target_region):
            fallback = self.fallback_strategy.get_fallback(target_region)
            return self.regions[fallback].create_order(user_id, request)
        
        try:
            result = self.regions[target_region].create_order(user_id, request)
            self.circuit_breaker.record_success(target_region)
            return result
        except Exception:
            self.circuit_breaker.record_failure(target_region)
            fallback = self.fallback_strategy.get_fallback(target_region)
            return self.regions[fallback].create_order(user_id, request)


# ============================================================================
# Order Event Sync
# ============================================================================

class OrderEventSync:
    """Syncs order events across regions."""
    
    def __init__(self, message_queue: MessageQueue,
                 regional_repositories: Dict[str, OrderRepository]):
        self.message_queue = message_queue
        self.regional_repositories = regional_repositories
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running = True
    
    def publish_order_event(self, order: Order, source_region: str) -> None:
        """Publish order event for cross-region sync."""
        event = OrderSyncEvent(order, source_region, datetime.utcnow())
        self.message_queue.publish("order-sync", event)
    
    def start_sync(self) -> None:
        """Start consuming order sync events."""
        self.executor.submit(self._consume_events)
    
    def _consume_events(self) -> None:
        """Consume and process events."""
        while self._running:
            try:
                events = self.message_queue.poll_batch("order-sync", 100)
                for event in events:
                    self._sync_to_other_regions(event)
            except Exception:
                pass
    
    def _sync_to_other_regions(self, event: OrderSyncEvent) -> None:
        """Sync order to other regions."""
        for region, repo in self.regional_repositories.items():
            if region != event.source_region:
                try:
                    repo.upsert(event.order)
                except Exception:
                    pass  # Queue for retry
    
    def shutdown(self) -> None:
        """Shutdown the sync service."""
        self._running = False
        self.executor.shutdown(wait=True)


# ============================================================================
# Global E-commerce Platform
# ============================================================================

class GlobalEcommercePlatform:
    """Global e-commerce platform coordinator."""
    
    def __init__(self, local_region: str, all_regions: List[str],
                 geo_router: GeoRouter,
                 inventory_coordinator: GlobalInventoryCoordinator,
                 messaging: CrossRegionMessaging):
        self.local_region = local_region
        self.geo_router = geo_router
        self.inventory_coordinator = inventory_coordinator
        self.messaging = messaging
        self.regions: Dict[str, RegionService] = {
            r: RegionService(r) for r in all_regions
        }
        self.executor = ThreadPoolExecutor(max_workers=20)
    
    def create_order(self, user_id: str, request: CreateOrderRequest,
                     user_lat: float, user_lng: float) -> Future:
        """Route order to appropriate region."""
        target_region = self.geo_router.get_optimal_region(user_lat, user_lng)
        
        if target_region == self.local_region:
            return self._process_order_locally(user_id, request)
        else:
            return self._forward_order_to_region(user_id, request, target_region)
    
    def _process_order_locally(self, user_id: str,
                                request: CreateOrderRequest) -> Future:
        """Process order in local region."""
        service = self.regions[self.local_region]
        return service.create_order(user_id, request)
    
    def _forward_order_to_region(self, user_id: str,
                                  request: CreateOrderRequest,
                                  target_region: str) -> Future:
        """Forward order to another region."""
        return self.messaging.forward_order(target_region, user_id, request)
    
    def get_product(self, product_id: str, region: str) -> Product:
        """Get product with regional inventory."""
        service = self.regions[region]
        product = service.get_product(product_id)
        
        regional_stock = self.inventory_coordinator.get_regional_stock(
            product_id, region
        )
        product.regional_stock = regional_stock
        
        return product
    
    def shutdown(self) -> None:
        """Shutdown the platform."""
        self.executor.shutdown(wait=True)
        for service in self.regions.values():
            service.shutdown()

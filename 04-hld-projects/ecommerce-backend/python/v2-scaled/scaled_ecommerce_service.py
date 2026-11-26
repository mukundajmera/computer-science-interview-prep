"""
E-commerce Backend - V2 Scaled Implementation

Adds Redis caching, Elasticsearch search, async order processing,
and saga pattern for distributed transactions.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
import threading
import json


# ============================================================================
# Data Classes
# ============================================================================

class OrderStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class SagaState(Enum):
    STARTED = "started"
    INVENTORY_RESERVED = "inventory_reserved"
    PAYMENT_PROCESSED = "payment_processed"
    INVENTORY_COMMITTED = "inventory_committed"
    COMPLETED = "completed"


@dataclass
class Product:
    product_id: str
    name: str
    price: Decimal


@dataclass
class CartItem:
    product_id: str
    quantity: int
    unit_price: Decimal
    
    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Cart:
    user_id: str
    items: List[CartItem] = field(default_factory=list)
    subtotal: Decimal = Decimal("0")
    
    def add_item(self, item: CartItem) -> None:
        self.items.append(item)
    
    def recalculate_totals(self) -> None:
        self.subtotal = sum((item.subtotal for item in self.items), Decimal("0"))


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Decimal


@dataclass
class Order:
    order_id: str = ""
    user_id: str = ""
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    items: List[OrderItem] = field(default_factory=list)
    subtotal: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    payment_method_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreateOrderRequest:
    shipping_address_id: str = ""
    payment_method_id: str = ""


@dataclass
class PaymentResult:
    payment_id: str
    successful: bool
    failure_reason: Optional[str] = None


@dataclass
class SearchRequest:
    query: str
    filters: Dict[str, str] = field(default_factory=dict)
    page: int = 1
    limit: int = 20


@dataclass
class SearchResult:
    products: List[Product]
    total_count: int
    facets: Dict[str, List[Dict]] = field(default_factory=dict)


@dataclass
class OrderEvent:
    pass


@dataclass
class OrderConfirmedEvent(OrderEvent):
    order: Order


@dataclass
class OrderShippedEvent(OrderEvent):
    order: Order


# ============================================================================
# Exceptions
# ============================================================================

class ProductNotFoundException(Exception):
    pass


class EmptyCartException(Exception):
    pass


class PaymentFailedException(Exception):
    pass


class OptimisticLockException(Exception):
    pass


class InventoryConflictException(Exception):
    pass


class InsufficientInventoryException(Exception):
    pass


# ============================================================================
# Interfaces
# ============================================================================

class Cache(ABC):
    @abstractmethod
    def get(self, key: str):
        pass
    
    @abstractmethod
    def put(self, key: str, value, ttl: timedelta) -> None:
        pass
    
    @abstractmethod
    def invalidate(self, key: str) -> None:
        pass


class RedisClient(ABC):
    @abstractmethod
    def hgetall(self, key: str) -> Dict[str, str]:
        pass
    
    @abstractmethod
    def hget(self, key: str, field: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def hset(self, key: str, field: str, value: str) -> None:
        pass
    
    @abstractmethod
    def hdel(self, key: str, field: str) -> None:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        pass
    
    @abstractmethod
    def expire(self, key: str, seconds: int) -> None:
        pass


class SearchIndex(ABC):
    @abstractmethod
    def search(self, request: SearchRequest) -> SearchResult:
        pass


class MessageQueue(ABC):
    @abstractmethod
    def publish(self, topic: str, message) -> None:
        pass
    
    @abstractmethod
    def poll_batch(self, topic: str, max_messages: int) -> List:
        pass


class InventoryService(ABC):
    @abstractmethod
    def reserve(self, reservation_id: str, items: List[OrderItem]) -> None:
        pass
    
    @abstractmethod
    def commit(self, reservation_id: str) -> None:
        pass
    
    @abstractmethod
    def release(self, reservation_id: str) -> None:
        pass


class PaymentService(ABC):
    @abstractmethod
    def process_payment(self, order_id: str, amount: Decimal,
                        payment_method_id: str) -> PaymentResult:
        pass
    
    @abstractmethod
    def refund(self, order_id: str) -> None:
        pass


class ProductService(ABC):
    @abstractmethod
    def get_product(self, product_id: str) -> Optional[Product]:
        pass


class NotificationService(ABC):
    @abstractmethod
    def send_order_confirmation(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def send_shipping_notification(self, order: Order) -> None:
        pass


class ProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: str) -> Optional[Product]:
        pass


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        pass


class InventoryRepository(ABC):
    @abstractmethod
    def find_by_product_id(self, product_id: str):
        pass
    
    @abstractmethod
    def update_with_version(self, inventory, expected_version: int) -> bool:
        pass
    
    @abstractmethod
    def save_reservation(self, reservation) -> None:
        pass


# ============================================================================
# Cached Product Service
# ============================================================================

class CachedProductService:
    """Product service with caching and Elasticsearch search."""
    
    def __init__(self, product_repository: ProductRepository,
                 product_cache: Cache, search_index: SearchIndex):
        self.product_repository = product_repository
        self.product_cache = product_cache
        self.search_index = search_index
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product with cache-aside pattern."""
        cached = self.product_cache.get(product_id)
        if cached:
            return cached
        
        product = self.product_repository.find_by_id(product_id)
        if product:
            self.product_cache.put(product_id, product, timedelta(minutes=5))
        return product
    
    def search_products(self, request: SearchRequest) -> SearchResult:
        """Search products using Elasticsearch."""
        return self.search_index.search(request)
    
    def invalidate_cache(self, product_id: str) -> None:
        """Invalidate product cache on update."""
        self.product_cache.invalidate(product_id)


# ============================================================================
# Redis Cart Service
# ============================================================================

class RedisCartService:
    """Shopping cart service using Redis."""
    
    def __init__(self, redis: RedisClient, product_service: ProductService):
        self.redis = redis
        self.product_service = product_service
        self.cart_ttl_days = 30
    
    def get_cart(self, user_id: str) -> Cart:
        """Get cart from Redis."""
        cart_key = f"cart:{user_id}"
        items_data = self.redis.hgetall(cart_key)
        
        cart = Cart(user_id=user_id)
        for data in items_data.values():
            item = self._deserialize_cart_item(data)
            cart.add_item(item)
        cart.recalculate_totals()
        return cart
    
    def add_item(self, user_id: str, product_id: str, quantity: int) -> Cart:
        """Add item to cart atomically."""
        cart_key = f"cart:{user_id}"
        
        product = self.product_service.get_product(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        
        # Check existing quantity
        existing = self.redis.hget(cart_key, product_id)
        new_quantity = quantity
        if existing:
            existing_item = self._deserialize_cart_item(existing)
            new_quantity += existing_item.quantity
        
        # Update cart
        item = CartItem(product_id, new_quantity, product.price)
        self.redis.hset(cart_key, product_id, self._serialize_cart_item(item))
        self.redis.expire(cart_key, self.cart_ttl_days * 24 * 3600)
        
        return self.get_cart(user_id)
    
    def remove_item(self, user_id: str, product_id: str) -> Cart:
        """Remove item from cart."""
        cart_key = f"cart:{user_id}"
        self.redis.hdel(cart_key, product_id)
        return self.get_cart(user_id)
    
    def clear_cart(self, user_id: str) -> None:
        """Clear cart after successful order."""
        cart_key = f"cart:{user_id}"
        self.redis.delete(cart_key)
    
    def _serialize_cart_item(self, item: CartItem) -> str:
        return f"{item.product_id}:{item.quantity}:{item.unit_price}"
    
    def _deserialize_cart_item(self, data: str) -> CartItem:
        parts = data.split(":")
        return CartItem(parts[0], int(parts[1]), Decimal(parts[2]))


# ============================================================================
# Order Saga
# ============================================================================

class OrderSaga:
    """Saga for managing distributed order transaction."""
    
    def __init__(self, saga_id: str, order: Order, cart: Cart):
        self.saga_id = saga_id
        self.order = order
        self.cart = cart
        self.reservation_id: Optional[str] = None
        self.payment_id: Optional[str] = None
        self.state = SagaState.STARTED
    
    def reserve_inventory(self, inventory_service: InventoryService) -> None:
        """Step 1: Reserve inventory."""
        self.reservation_id = f"res_{self.order.order_id}"
        inventory_service.reserve(self.reservation_id, self.order.items)
        self.state = SagaState.INVENTORY_RESERVED
    
    def process_payment(self, payment_service: PaymentService) -> None:
        """Step 2: Process payment."""
        result = payment_service.process_payment(
            self.order.order_id,
            self.order.total,
            self.order.payment_method_id
        )
        if not result.successful:
            raise PaymentFailedException(result.failure_reason or "Unknown error")
        self.payment_id = result.payment_id
        self.state = SagaState.PAYMENT_PROCESSED
    
    def commit_inventory(self, inventory_service: InventoryService) -> None:
        """Step 3: Commit inventory."""
        inventory_service.commit(self.reservation_id)
        self.state = SagaState.INVENTORY_COMMITTED
    
    def compensate(self, inventory_service: InventoryService,
                   payment_service: PaymentService) -> None:
        """Execute compensating transactions in reverse order."""
        if self.state.value >= SagaState.PAYMENT_PROCESSED.value:
            payment_service.refund(self.order.order_id)
        
        if self.state.value >= SagaState.INVENTORY_RESERVED.value:
            inventory_service.release(self.reservation_id)


# ============================================================================
# Saga Order Service
# ============================================================================

class SagaOrderService:
    """Order service using saga pattern."""
    
    def __init__(self, order_repository: OrderRepository,
                 cart_service: RedisCartService,
                 inventory_service: InventoryService,
                 payment_service: PaymentService,
                 message_queue: MessageQueue):
        self.order_repository = order_repository
        self.cart_service = cart_service
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.message_queue = message_queue
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def create_order_async(self, user_id: str,
                           request: CreateOrderRequest) -> Future:
        """Create order using saga pattern asynchronously."""
        return self.executor.submit(
            self._create_order_sync, user_id, request
        )
    
    def _create_order_sync(self, user_id: str,
                           request: CreateOrderRequest) -> Order:
        """Synchronous order creation with saga."""
        # Get cart
        cart = self.cart_service.get_cart(user_id)
        if not cart.items:
            raise EmptyCartException()
        
        # Create order
        order = self._create_pending_order(user_id, cart, request)
        self.order_repository.save(order)
        
        # Execute saga
        saga_id = f"saga_{order.order_id}"
        saga = OrderSaga(saga_id, order, cart)
        
        try:
            # Step 1: Reserve inventory
            saga.reserve_inventory(self.inventory_service)
            
            # Step 2: Process payment
            saga.process_payment(self.payment_service)
            
            # Step 3: Commit inventory
            saga.commit_inventory(self.inventory_service)
            
            # Step 4: Confirm order
            order.status = OrderStatus.CONFIRMED
            self.order_repository.save(order)
            
            # Step 5: Clear cart
            self.cart_service.clear_cart(user_id)
            
            # Step 6: Send notification
            self.message_queue.publish(
                "order-notifications",
                OrderConfirmedEvent(order)
            )
            
            return order
            
        except Exception as e:
            # Execute compensating transactions
            saga.compensate(self.inventory_service, self.payment_service)
            order.status = OrderStatus.CANCELLED
            self.order_repository.save(order)
            raise
    
    def _create_pending_order(self, user_id: str, cart: Cart,
                               request: CreateOrderRequest) -> Order:
        """Create pending order from cart."""
        import uuid
        
        order_items = [
            OrderItem(ci.product_id, ci.quantity, ci.unit_price)
            for ci in cart.items
        ]
        
        subtotal = cart.subtotal
        tax = subtotal * Decimal("0.08")
        total = subtotal + tax
        
        return Order(
            order_id=f"ord_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            status=OrderStatus.PENDING_PAYMENT,
            items=order_items,
            subtotal=subtotal,
            tax=tax,
            total=total,
            payment_method_id=request.payment_method_id
        )
    
    def shutdown(self):
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)


# ============================================================================
# Optimistic Locking Inventory Service
# ============================================================================

@dataclass
class Inventory:
    product_id: str
    available_quantity: int
    reserved_quantity: int
    version: int


@dataclass
class InventoryReservation:
    reservation_id: str
    items: List[OrderItem]


class OptimisticLockingInventoryService:
    """Inventory service with optimistic locking."""
    
    def __init__(self, inventory_repository: InventoryRepository,
                 hot_inventory_cache: Cache):
        self.inventory_repository = inventory_repository
        self.hot_inventory_cache = hot_inventory_cache
        self.max_retries = 3
    
    def reserve(self, reservation_id: str, items: List[OrderItem]) -> None:
        """Reserve inventory with optimistic locking and retry."""
        for attempt in range(self.max_retries):
            try:
                self._attempt_reservation(reservation_id, items)
                return
            except OptimisticLockException:
                if attempt == self.max_retries - 1:
                    raise InventoryConflictException(
                        f"Failed after {self.max_retries} attempts"
                    )
                import time
                time.sleep((2 ** attempt) * 0.01)
        
        raise InventoryConflictException("Unexpected state")
    
    def _attempt_reservation(self, reservation_id: str,
                              items: List[OrderItem]) -> None:
        """Single attempt at reservation."""
        inventories = {}
        
        # Check all items
        for item in items:
            inv = self.inventory_repository.find_by_product_id(item.product_id)
            if not inv or inv.available_quantity < item.quantity:
                raise InsufficientInventoryException(item.product_id)
            inventories[item.product_id] = inv
        
        # Update with optimistic locking
        for item in items:
            inv = inventories[item.product_id]
            expected_version = inv.version
            
            inv.available_quantity -= item.quantity
            inv.reserved_quantity += item.quantity
            inv.version += 1
            
            if not self.inventory_repository.update_with_version(
                inv, expected_version
            ):
                raise OptimisticLockException(
                    f"Version conflict for {item.product_id}"
                )
            
            self.hot_inventory_cache.invalidate(item.product_id)
        
        # Save reservation
        reservation = InventoryReservation(reservation_id, items)
        self.inventory_repository.save_reservation(reservation)
    
    def commit(self, reservation_id: str) -> None:
        """Commit a reservation."""
        pass
    
    def release(self, reservation_id: str) -> None:
        """Release a reservation."""
        pass


# ============================================================================
# Order Event Processor
# ============================================================================

class OrderEventProcessor:
    """Async processor for order events."""
    
    def __init__(self, message_queue: MessageQueue,
                 notification_service: NotificationService,
                 num_workers: int = 4):
        self.message_queue = message_queue
        self.notification_service = notification_service
        self.num_workers = num_workers
        self.workers = []
        self._running = True
    
    def start(self):
        """Start processing workers."""
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self._process_events)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def _process_events(self):
        """Worker loop."""
        while self._running:
            try:
                events = self.message_queue.poll_batch("order-notifications", 10)
                for event in events:
                    self._process_event(event)
            except Exception:
                pass
    
    def _process_event(self, event: OrderEvent):
        """Process a single event."""
        if isinstance(event, OrderConfirmedEvent):
            self.notification_service.send_order_confirmation(event.order)
        elif isinstance(event, OrderShippedEvent):
            self.notification_service.send_shipping_notification(event.order)
    
    def shutdown(self):
        """Shutdown the processor."""
        self._running = False
        for worker in self.workers:
            worker.join(timeout=5.0)

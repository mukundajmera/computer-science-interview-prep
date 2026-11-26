"""
E-commerce Backend - V1 Basic Implementation

Core product catalog, cart, order, and inventory functionality.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from abc import ABC, abstractmethod
import uuid


# ============================================================================
# Enums
# ============================================================================

class OrderStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ReservationStatus(Enum):
    ACTIVE = "active"
    COMMITTED = "committed"
    RELEASED = "released"
    EXPIRED = "expired"


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Product:
    product_id: str
    name: str
    description: str
    price: Decimal
    category_id: str
    rating: float = 0.0
    in_stock: bool = True


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
    cart_id: str
    user_id: str
    items: List[CartItem] = field(default_factory=list)
    subtotal: Decimal = Decimal("0")
    
    def get_item(self, product_id: str) -> Optional[CartItem]:
        for item in self.items:
            if item.product_id == product_id:
                return item
        return None
    
    def add_item(self, item: CartItem) -> None:
        self.items.append(item)
    
    def remove_item(self, product_id: str) -> None:
        self.items = [i for i in self.items if i.product_id != product_id]
    
    def clear(self) -> None:
        self.items.clear()
        self.subtotal = Decimal("0")
    
    def recalculate_totals(self) -> None:
        self.subtotal = sum((item.subtotal for item in self.items), Decimal("0"))


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Decimal


@dataclass
class Order:
    order_id: str
    user_id: str
    status: OrderStatus
    items: List[OrderItem]
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    shipping_address_id: str = ""
    payment_method_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Inventory:
    product_id: str
    available_quantity: int
    reserved_quantity: int = 0


@dataclass
class InventoryReservation:
    reservation_id: str
    items: List[OrderItem]
    status: ReservationStatus
    expires_at: datetime


@dataclass
class Payment:
    payment_id: str
    order_id: str
    amount: Decimal
    status: PaymentStatus
    failure_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class PaymentResult:
    payment_id: str
    successful: bool
    failure_reason: Optional[str] = None


@dataclass
class CreateOrderRequest:
    shipping_address_id: str
    payment_method_id: str


# ============================================================================
# Exceptions
# ============================================================================

class ProductNotFoundException(Exception):
    def __init__(self, product_id: str):
        super().__init__(f"Product not found: {product_id}")


class InsufficientInventoryException(Exception):
    def __init__(self, product_id: str):
        super().__init__(f"Insufficient inventory: {product_id}")


class InvalidReservationException(Exception):
    def __init__(self, reservation_id: str):
        super().__init__(f"Invalid reservation: {reservation_id}")


class EmptyCartException(Exception):
    def __init__(self):
        super().__init__("Cart is empty")


class OrderNotFoundException(Exception):
    def __init__(self, order_id: str):
        super().__init__(f"Order not found: {order_id}")


class PaymentFailedException(Exception):
    def __init__(self, reason: str):
        super().__init__(f"Payment failed: {reason}")


# ============================================================================
# Repository Interfaces
# ============================================================================

class ProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: str) -> Optional[Product]:
        pass
    
    @abstractmethod
    def search_by_name(self, query: str, page: int, limit: int) -> List[Product]:
        pass
    
    @abstractmethod
    def find_by_category(self, category_id: str, page: int, limit: int) -> List[Product]:
        pass


class CartRepository(ABC):
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[Cart]:
        pass
    
    @abstractmethod
    def save(self, cart: Cart) -> None:
        pass


class InventoryRepository(ABC):
    @abstractmethod
    def find_by_product_id(self, product_id: str) -> Optional[Inventory]:
        pass
    
    @abstractmethod
    def save(self, inventory: Inventory) -> None:
        pass
    
    @abstractmethod
    def find_reservation(self, reservation_id: str) -> Optional[InventoryReservation]:
        pass
    
    @abstractmethod
    def save_reservation(self, reservation: InventoryReservation) -> None:
        pass


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str, page: int, limit: int) -> List[Order]:
        pass


class PaymentRepository(ABC):
    @abstractmethod
    def save(self, payment: Payment) -> None:
        pass
    
    @abstractmethod
    def find_by_order_id(self, order_id: str) -> Optional[Payment]:
        pass


# ============================================================================
# Product Service
# ============================================================================

class ProductService:
    """Product catalog service."""
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self.product_repository.find_by_id(product_id)
    
    def search_products(self, query: str, page: int, limit: int) -> List[Product]:
        return self.product_repository.search_by_name(query, page, limit)
    
    def get_products_by_category(self, category_id: str, 
                                  page: int, limit: int) -> List[Product]:
        return self.product_repository.find_by_category(category_id, page, limit)


# ============================================================================
# Cart Service
# ============================================================================

class CartService:
    """Shopping cart service."""
    
    def __init__(self, cart_repository: CartRepository,
                 product_repository: ProductRepository):
        self.cart_repository = cart_repository
        self.product_repository = product_repository
    
    def get_cart(self, user_id: str) -> Cart:
        cart = self.cart_repository.find_by_user_id(user_id)
        if cart is None:
            cart = Cart(
                cart_id=self._generate_cart_id(),
                user_id=user_id
            )
            self.cart_repository.save(cart)
        return cart
    
    def add_item(self, user_id: str, product_id: str, quantity: int) -> Cart:
        cart = self.get_cart(user_id)
        product = self.product_repository.find_by_id(product_id)
        
        if product is None:
            raise ProductNotFoundException(product_id)
        
        existing_item = cart.get_item(product_id)
        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(product_id, quantity, product.price)
            cart.add_item(new_item)
        
        cart.recalculate_totals()
        self.cart_repository.save(cart)
        return cart
    
    def update_item_quantity(self, user_id: str, product_id: str, 
                              quantity: int) -> Cart:
        cart = self.get_cart(user_id)
        
        if quantity <= 0:
            return self.remove_item(user_id, product_id)
        
        item = cart.get_item(product_id)
        if item:
            item.quantity = quantity
            cart.recalculate_totals()
            self.cart_repository.save(cart)
        return cart
    
    def remove_item(self, user_id: str, product_id: str) -> Cart:
        cart = self.get_cart(user_id)
        cart.remove_item(product_id)
        cart.recalculate_totals()
        self.cart_repository.save(cart)
        return cart
    
    def clear_cart(self, user_id: str) -> None:
        cart = self.get_cart(user_id)
        cart.clear()
        self.cart_repository.save(cart)
    
    def _generate_cart_id(self) -> str:
        return f"cart_{uuid.uuid4().hex[:12]}"


# ============================================================================
# Inventory Service
# ============================================================================

class InventoryService:
    """Inventory management service."""
    
    def __init__(self, inventory_repository: InventoryRepository):
        self.inventory_repository = inventory_repository
    
    def check_availability(self, product_id: str, quantity: int) -> bool:
        inventory = self.inventory_repository.find_by_product_id(product_id)
        return inventory is not None and inventory.available_quantity >= quantity
    
    def reserve(self, reservation_id: str, 
                items: List[OrderItem]) -> InventoryReservation:
        # Check all items first
        for item in items:
            if not self.check_availability(item.product_id, item.quantity):
                raise InsufficientInventoryException(item.product_id)
        
        # Reserve all items
        for item in items:
            inventory = self.inventory_repository.find_by_product_id(item.product_id)
            inventory.available_quantity -= item.quantity
            inventory.reserved_quantity += item.quantity
            self.inventory_repository.save(inventory)
        
        # Create reservation record
        from datetime import timedelta
        reservation = InventoryReservation(
            reservation_id=reservation_id,
            items=items,
            status=ReservationStatus.ACTIVE,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        self.inventory_repository.save_reservation(reservation)
        
        return reservation
    
    def commit(self, reservation_id: str) -> None:
        reservation = self.inventory_repository.find_reservation(reservation_id)
        if reservation is None or reservation.status != ReservationStatus.ACTIVE:
            raise InvalidReservationException(reservation_id)
        
        # Convert reserved to committed
        for item in reservation.items:
            inventory = self.inventory_repository.find_by_product_id(item.product_id)
            inventory.reserved_quantity -= item.quantity
            self.inventory_repository.save(inventory)
        
        reservation.status = ReservationStatus.COMMITTED
        self.inventory_repository.save_reservation(reservation)
    
    def release(self, reservation_id: str) -> None:
        reservation = self.inventory_repository.find_reservation(reservation_id)
        if reservation is None:
            return
        
        if reservation.status == ReservationStatus.ACTIVE:
            # Restore available quantity
            for item in reservation.items:
                inventory = self.inventory_repository.find_by_product_id(item.product_id)
                inventory.available_quantity += item.quantity
                inventory.reserved_quantity -= item.quantity
                self.inventory_repository.save(inventory)
            
            reservation.status = ReservationStatus.RELEASED
            self.inventory_repository.save_reservation(reservation)


# ============================================================================
# Payment Service
# ============================================================================

class PaymentService:
    """Payment processing service."""
    
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
    
    def process_payment(self, order_id: str, amount: Decimal,
                        payment_method_id: str) -> PaymentResult:
        # Create payment record
        payment = Payment(
            payment_id=f"pay_{uuid.uuid4().hex[:12]}",
            order_id=order_id,
            amount=amount,
            status=PaymentStatus.PENDING
        )
        self.payment_repository.save(payment)
        
        # Simulate payment processing
        import random
        success = random.random() < 0.95  # 95% success rate
        
        if success:
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = "Payment declined"
        
        self.payment_repository.save(payment)
        
        return PaymentResult(
            payment_id=payment.payment_id,
            successful=success,
            failure_reason=payment.failure_reason
        )
    
    def refund(self, order_id: str) -> None:
        payment = self.payment_repository.find_by_order_id(order_id)
        if payment and payment.status == PaymentStatus.COMPLETED:
            payment.status = PaymentStatus.REFUNDED
            self.payment_repository.save(payment)


# ============================================================================
# Order Service
# ============================================================================

class OrderService:
    """Order management service."""
    
    def __init__(self, order_repository: OrderRepository,
                 cart_service: CartService,
                 inventory_service: InventoryService,
                 payment_service: PaymentService):
        self.order_repository = order_repository
        self.cart_service = cart_service
        self.inventory_service = inventory_service
        self.payment_service = payment_service
    
    def create_order(self, user_id: str, request: CreateOrderRequest) -> Order:
        # Get cart items
        cart = self.cart_service.get_cart(user_id)
        if not cart.items:
            raise EmptyCartException()
        
        # Create order
        order_items = [
            OrderItem(ci.product_id, ci.quantity, ci.unit_price)
            for ci in cart.items
        ]
        
        subtotal = cart.subtotal
        tax = subtotal * Decimal("0.08")  # 8% tax
        total = subtotal + tax
        
        order = Order(
            order_id=self._generate_order_id(),
            user_id=user_id,
            status=OrderStatus.PENDING_PAYMENT,
            items=order_items,
            subtotal=subtotal,
            tax=tax,
            total=total,
            shipping_address_id=request.shipping_address_id,
            payment_method_id=request.payment_method_id
        )
        self.order_repository.save(order)
        
        # Reserve inventory
        reservation_id = f"res_{order.order_id}"
        try:
            self.inventory_service.reserve(reservation_id, order_items)
        except InsufficientInventoryException:
            order.status = OrderStatus.CANCELLED
            self.order_repository.save(order)
            raise
        
        # Process payment
        try:
            payment_result = self.payment_service.process_payment(
                order.order_id, order.total, request.payment_method_id
            )
            
            if payment_result.successful:
                self.inventory_service.commit(reservation_id)
                order.status = OrderStatus.CONFIRMED
                self.cart_service.clear_cart(user_id)
            else:
                self.inventory_service.release(reservation_id)
                order.status = OrderStatus.CANCELLED
        except Exception as e:
            self.inventory_service.release(reservation_id)
            order.status = OrderStatus.CANCELLED
            self.order_repository.save(order)
            raise PaymentFailedException(str(e))
        
        self.order_repository.save(order)
        return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.order_repository.find_by_id(order_id)
    
    def get_user_orders(self, user_id: str, page: int, limit: int) -> List[Order]:
        return self.order_repository.find_by_user_id(user_id, page, limit)
    
    def cancel_order(self, order_id: str) -> Order:
        order = self.order_repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundException(order_id)
        
        if order.status not in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
            raise ValueError("Order cannot be cancelled")
        
        order.status = OrderStatus.CANCELLED
        self.order_repository.save(order)
        
        return order
    
    def _generate_order_id(self) -> str:
        return f"ord_{uuid.uuid4().hex[:12]}"

"""v2 service: state-dependent cancellation with refunds, and
idempotent order placement.

Two doc-named improvements over v1:
1. Cancellation policy per state (FOLLOW-UPS): cancelling no longer just
   raises after preparation starts. Each state decides whether cancel is
   allowed and what the customer is refunded: full refund before
   preparation, a preparation penalty while cooking, and a polite
   rejection (route to support) once food is ready or on the road.
2. Idempotency keys (FOLLOW-UPS): OrderService.place_order keys each
   placement so a client retry after a timeout returns the original
   order instead of creating and charging a duplicate.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Dict, Tuple
import threading

from enums_v2 import OrderStatus
from models_v2 import Customer, Restaurant, Driver, OrderItem, Subject, Observer
from strategies_v2 import PricingStrategy


class CancelResult:
    def __init__(self, cancelled: bool, refund: float, reason: str):
        self.cancelled = cancelled
        self.refund = refund
        self.reason = reason


# Fraction of the total kept as a preparation penalty when the customer
# cancels after the restaurant has started cooking.
PREPARATION_PENALTY = 0.2


class OrderState(ABC):
    @abstractmethod
    def next_state(self, order: 'Order') -> None:
        pass

    @abstractmethod
    def cancel(self, order: 'Order') -> CancelResult:
        pass

    @abstractmethod
    def get_status(self) -> OrderStatus:
        pass

    def _reject(self, order: 'Order', reason: str) -> CancelResult:
        return CancelResult(False, 0.0, reason)


class PlacedState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(PreparingState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> CancelResult:
        refund = order.get_total()
        order.set_state(CancelledState())
        order.notify_observers()
        return CancelResult(True, refund, "Cancelled before preparation; full refund.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.PLACED


class PreparingState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(ReadyForPickupState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> CancelResult:
        refund = order.get_total() * (1.0 - PREPARATION_PENALTY)
        order.set_state(CancelledState())
        order.notify_observers()
        return CancelResult(True, refund, "Cancelled during preparation; refund less 20% penalty.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.PREPARING


class ReadyForPickupState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(OutForDeliveryState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> CancelResult:
        return self._reject(order, "Food is ready; contact support to cancel.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.READY_FOR_PICKUP


class OutForDeliveryState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(DeliveredState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> CancelResult:
        return self._reject(order, "Order is out for delivery; contact support.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.OUT_FOR_DELIVERY


class DeliveredState(OrderState):
    def next_state(self, order: 'Order') -> None:
        raise ValueError("Order already delivered.")

    def cancel(self, order: 'Order') -> CancelResult:
        return self._reject(order, "Already delivered; use the returns flow.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.DELIVERED


class CancelledState(OrderState):
    def next_state(self, order: 'Order') -> None:
        raise ValueError("Order is cancelled.")

    def cancel(self, order: 'Order') -> CancelResult:
        return self._reject(order, "Already cancelled.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.CANCELLED


class Order(Subject):
    def __init__(self, order_id: str, customer: Customer, restaurant: Restaurant, strategy: PricingStrategy):
        self.id = order_id
        self.customer = customer
        self.restaurant = restaurant
        self.pricing_strategy = strategy
        self.state: OrderState = PlacedState()
        self.driver: Optional[Driver] = None
        self.items: List[OrderItem] = []
        self.observers: List[Observer] = []
        self._lock = threading.Lock()

    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)

    def get_total(self) -> float:
        return self.pricing_strategy.calculate_pricing(self.items).total

    def set_state(self, state: OrderState) -> None:
        self.state = state

    def get_state(self) -> OrderState:
        return self.state

    def next_state(self) -> None:
        self.state.next_state(self)

    def cancel(self) -> CancelResult:
        return self.state.cancel(self)

    def assign_driver(self, driver: Driver) -> bool:
        with self._lock:
            if self.driver is None:
                self.driver = driver
                return True
            return False

    def add_observer(self, o: Observer) -> None:
        self.observers.append(o)

    def remove_observer(self, o: Observer) -> None:
        self.observers.remove(o)

    def notify_observers(self) -> None:
        for o in self.observers:
            o.update(self)


class OrderService:
    """Places orders behind idempotency keys. A client that retries a
    timed-out placement gets the original order back with created=False
    instead of a second order and a second charge."""

    def __init__(self):
        self._orders_by_key: Dict[str, Order] = {}
        self._lock = threading.Lock()

    def place_order(self, idempotency_key: str, build: Callable[[], Order]) -> Tuple[Order, bool]:
        with self._lock:
            existing = self._orders_by_key.get(idempotency_key)
            if existing is not None:
                return existing, False
            order = build()
            self._orders_by_key[idempotency_key] = order
            return order, True

    def order_count(self) -> int:
        return len(self._orders_by_key)

from abc import ABC, abstractmethod
from typing import List, Optional
import threading

from enums import OrderStatus
from models import Customer, Restaurant, Driver, OrderItem, Subject, Observer
from strategies import PricingStrategy


class OrderState(ABC):
    @abstractmethod
    def next_state(self, order: 'Order') -> None:
        pass

    @abstractmethod
    def cancel(self, order: 'Order') -> None:
        pass

    @abstractmethod
    def get_status(self) -> OrderStatus:
        pass


class PlacedState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(PreparingState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> None:
        order.set_state(CancelledState())
        order.notify_observers()

    def get_status(self) -> OrderStatus:
        return OrderStatus.PLACED


class PreparingState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(ReadyForPickupState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> None:
        raise ValueError("Cannot cancel after preparation has started without manager approval.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.PREPARING


class ReadyForPickupState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(OutForDeliveryState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> None:
        raise ValueError("Cannot cancel. Food is ready.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.READY_FOR_PICKUP


class OutForDeliveryState(OrderState):
    def next_state(self, order: 'Order') -> None:
        order.set_state(DeliveredState())
        order.notify_observers()

    def cancel(self, order: 'Order') -> None:
        raise ValueError("Cannot cancel. Out for delivery.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.OUT_FOR_DELIVERY


class DeliveredState(OrderState):
    def next_state(self, order: 'Order') -> None:
        raise ValueError("Order already delivered.")

    def cancel(self, order: 'Order') -> None:
        raise ValueError("Cannot cancel. Already delivered.")

    def get_status(self) -> OrderStatus:
        return OrderStatus.DELIVERED


class CancelledState(OrderState):
    def next_state(self, order: 'Order') -> None:
        raise ValueError("Order is cancelled.")

    def cancel(self, order: 'Order') -> None:
        raise ValueError("Already cancelled.")

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
        return self.pricing_strategy.calculate_total(self.items)

    def set_state(self, state: OrderState) -> None:
        self.state = state

    def get_state(self) -> OrderState:
        return self.state

    def next_state(self) -> None:
        self.state.next_state(self)

    def cancel(self) -> None:
        self.state.cancel(self)

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

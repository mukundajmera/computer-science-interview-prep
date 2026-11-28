"""v2 models: identical to v1. The domain objects were not the weakness
the docs name; the changes live in service_v2 (state-dependent
cancellation) and strategies_v2 (decorator pricing)."""
from abc import ABC, abstractmethod
from typing import List, Any
from enums_v2 import OrderStatus


class User(ABC):
    def __init__(self, user_id: str, name: str):
        self.id = user_id
        self.name = name


class Observer(ABC):
    @abstractmethod
    def update(self, order: Any) -> None:
        pass


class Customer(User, Observer):
    def __init__(self, user_id: str, name: str):
        super().__init__(user_id, name)

    def update(self, order: Any) -> None:
        print(f"Notify Customer {self.name}: Order is now {order.get_state().get_status().name}")


class Driver(User, Observer):
    def __init__(self, user_id: str, name: str):
        super().__init__(user_id, name)
        self.is_available = True

    def update(self, order: Any) -> None:
        if order.get_state().get_status() == OrderStatus.READY_FOR_PICKUP:
            print(f"Notify Driver {self.name}: New order available for pickup!")


class Restaurant:
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name


class RestaurantOwner(User, Observer):
    def __init__(self, user_id: str, name: str, restaurant: Restaurant):
        super().__init__(user_id, name)
        self.restaurant = restaurant

    def update(self, order: Any) -> None:
        print(f"Notify Restaurant {self.restaurant.get_name()}: Order update - {order.get_state().get_status().name}")


class MenuItem:
    def __init__(self, item_id: str, name: str, price: float):
        self.id = item_id
        self.name = name
        self.price = price

    def get_price(self) -> float:
        return self.price


class OrderItem:
    def __init__(self, item: MenuItem, quantity: int):
        self.item = item
        self.quantity = quantity

    def get_menu_item(self) -> MenuItem:
        return self.item

    def get_quantity(self) -> int:
        return self.quantity


class Subject(ABC):
    @abstractmethod
    def add_observer(self, o: Observer) -> None:
        pass

    @abstractmethod
    def remove_observer(self, o: Observer) -> None:
        pass

    @abstractmethod
    def notify_observers(self) -> None:
        pass

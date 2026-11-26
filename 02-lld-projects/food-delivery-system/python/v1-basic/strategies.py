from abc import ABC, abstractmethod
from typing import List
from models import OrderItem


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_total(self, items: List[OrderItem]) -> float:
        pass


class StandardPricingStrategy(PricingStrategy):
    def calculate_total(self, items: List[OrderItem]) -> float:
        subtotal = sum(item.get_menu_item().get_price() * item.get_quantity() for item in items)
        return subtotal + 5.0  # $5 delivery fee


class SurgePricingStrategy(PricingStrategy):
    def calculate_total(self, items: List[OrderItem]) -> float:
        subtotal = sum(item.get_menu_item().get_price() * item.get_quantity() for item in items)
        return subtotal + 15.0  # $15 delivery fee

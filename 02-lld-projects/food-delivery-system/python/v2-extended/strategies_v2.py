"""v2 pricing: Strategy for the base fee model plus Decorator for
stackable promotions.

v1's weakness the docs name: promotions had to become whole new
strategies. v2 keeps one base strategy and wraps it in decorators, so
"10% off food" and "free delivery" combine in any order instead of
multiplying into N strategy subclasses.
"""
from abc import ABC, abstractmethod
from typing import List

from models_v2 import OrderItem


class PricingResult:
    """Itemized breakdown so decorators can adjust one component
    (food subtotal, delivery fee) without touching the other."""

    def __init__(self, subtotal: float, delivery_fee: float):
        self.subtotal = subtotal
        self.delivery_fee = delivery_fee

    @property
    def total(self) -> float:
        return self.subtotal + self.delivery_fee


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_pricing(self, items: List[OrderItem]) -> PricingResult:
        pass


def _subtotal(items: List[OrderItem]) -> float:
    return sum(item.get_menu_item().get_price() * item.get_quantity() for item in items)


class BasePricingStrategy(PricingStrategy):
    """Food subtotal plus a flat delivery fee."""

    def __init__(self, delivery_fee: float):
        self.delivery_fee = delivery_fee

    def calculate_pricing(self, items: List[OrderItem]) -> PricingResult:
        return PricingResult(_subtotal(items), self.delivery_fee)


class StandardPricingStrategy(BasePricingStrategy):
    """v1 parity: $5 delivery fee."""

    def __init__(self):
        super().__init__(5.0)


class SurgePricingStrategy(BasePricingStrategy):
    """v1 parity: $15 delivery fee during peak demand."""

    def __init__(self):
        super().__init__(15.0)


class PricingDecorator(PricingStrategy):
    def __init__(self, inner: PricingStrategy):
        self.inner = inner


class PercentDiscountDecorator(PricingDecorator):
    """Takes `percent` off the food subtotal only; the delivery fee is
    untouched so the courier is still paid."""

    def __init__(self, inner: PricingStrategy, percent: float):
        super().__init__(inner)
        self.percent = percent

    def calculate_pricing(self, items: List[OrderItem]) -> PricingResult:
        base = self.inner.calculate_pricing(items)
        return PricingResult(base.subtotal * (1.0 - self.percent / 100.0), base.delivery_fee)


class FreeDeliveryDecorator(PricingDecorator):
    """Zeroes the delivery fee; the food subtotal is untouched."""

    def calculate_pricing(self, items: List[OrderItem]) -> PricingResult:
        base = self.inner.calculate_pricing(items)
        return PricingResult(base.subtotal, 0.0)

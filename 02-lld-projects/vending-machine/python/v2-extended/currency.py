"""
Vending Machine System - V2 Extended

Currency enums with extended features.
"""
from enum import Enum


class Coin(Enum):
    """Enumeration of coin denominations."""
    PENNY = 0.01
    NICKEL = 0.05
    DIME = 0.10
    QUARTER = 0.25
    HALF_DOLLAR = 0.50
    DOLLAR = 1.00

    @property
    def value(self) -> float:
        return self._value_

    def __str__(self) -> str:
        return f"{self.name} (${self.value:.2f})"


class Note(Enum):
    """Enumeration of note denominations."""
    ONE = 1.00
    FIVE = 5.00
    TEN = 10.00
    TWENTY = 20.00

    @property
    def value(self) -> float:
        return self._value_

    def __str__(self) -> str:
        return f"${int(self.value)} bill"


class ProductCategory(Enum):
    """Product categories for organization."""
    SNACK = "SNACK"
    BEVERAGE = "BEVERAGE"
    CANDY = "CANDY"
    HEALTHY = "HEALTHY"

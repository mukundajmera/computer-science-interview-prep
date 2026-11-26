"""
Vending Machine System - V3 Optimized

Thread-safe currency enums.
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
    
    @property
    def value_in_cents(self) -> int:
        return round(self._value_ * 100)

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
    """Product categories."""
    SNACK = "SNACK"
    BEVERAGE = "BEVERAGE"
    CANDY = "CANDY"
    HEALTHY = "HEALTHY"

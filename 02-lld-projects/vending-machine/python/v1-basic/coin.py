"""
Vending Machine System - V1 Basic

Coin enum representing valid currency denominations.
"""
from enum import Enum


class Coin(Enum):
    """Enumeration of coin denominations accepted by the vending machine."""
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

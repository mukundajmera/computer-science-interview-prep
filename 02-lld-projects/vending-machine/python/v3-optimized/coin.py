"""
Vending Machine System - V3 Optimized

Compatibility module - re-exports Coin from the extended currency module
so that internal modules and tests use the same Coin type.
"""
from currency import Coin

__all__ = ['Coin']

"""
Vending Machine System - V1 Basic

Slot class representing a product slot in the vending machine.
"""
from typing import Optional
from product import Product


class Slot:
    """Represents a slot in the vending machine that holds products."""
    
    def __init__(self, code: str, product: Product, quantity: int, max_capacity: int):
        if not code:
            raise ValueError("Slot code cannot be null or empty")
        if product is None:
            raise ValueError("Product cannot be null")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if max_capacity < 1:
            raise ValueError("Max capacity must be at least 1")
        if quantity > max_capacity:
            raise ValueError("Quantity cannot exceed max capacity")
        
        self._code = code
        self._product = product
        self._quantity = quantity
        self._max_capacity = max_capacity
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def product(self) -> Product:
        return self._product
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @property
    def max_capacity(self) -> int:
        return self._max_capacity
    
    @property
    def is_empty(self) -> bool:
        return self._quantity == 0
    
    @property
    def is_full(self) -> bool:
        return self._quantity == self._max_capacity
    
    def dispense_one(self) -> Optional[Product]:
        """Dispense one product from this slot."""
        if self.is_empty:
            return None
        self._quantity -= 1
        return self._product
    
    def restock(self, count: int) -> int:
        """Restock products to this slot. Returns actual number added."""
        if count < 0:
            raise ValueError("Restock count cannot be negative")
        space_available = self._max_capacity - self._quantity
        added = min(count, space_available)
        self._quantity += added
        return added
    
    def __str__(self) -> str:
        return f"[{self._code}] {self._product.name} (${self._product.price:.2f}) - {self._quantity}/{self._max_capacity}"

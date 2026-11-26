"""
Vending Machine System - V1 Basic

Product class representing items sold in the vending machine.
"""


class Product:
    """Represents a product in the vending machine."""
    
    def __init__(self, code: str, name: str, price: float):
        if not code:
            raise ValueError("Product code cannot be null or empty")
        if not name:
            raise ValueError("Product name cannot be null or empty")
        if price < 0:
            raise ValueError("Product price cannot be negative")
        
        self._code = code
        self._name = name
        self._price = price
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def price(self) -> float:
        return self._price
    
    def __str__(self) -> str:
        return f"{self._code}: {self._name} - ${self._price:.2f}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return False
        return self._code == other._code
    
    def __hash__(self) -> int:
        return hash(self._code)

"""
Decorator Pattern - V1 Basic: Coffee Shop

Classic example demonstrating how to add condiments to beverages
without creating a class for each combination.
"""
from abc import ABC, abstractmethod


# Component Interface
class Beverage(ABC):
    def __init__(self):
        self._description = "Unknown Beverage"
    
    @property
    def description(self) -> str:
        return self._description
    
    @abstractmethod
    def cost(self) -> float:
        pass


# Concrete Components
class Espresso(Beverage):
    def __init__(self):
        super().__init__()
        self._description = "Espresso"
    
    def cost(self) -> float:
        return 1.99


class HouseBlend(Beverage):
    def __init__(self):
        super().__init__()
        self._description = "House Blend Coffee"
    
    def cost(self) -> float:
        return 0.89


class DarkRoast(Beverage):
    def __init__(self):
        super().__init__()
        self._description = "Dark Roast"
    
    def cost(self) -> float:
        return 1.49


# Abstract Decorator
class CondimentDecorator(Beverage):
    def __init__(self, beverage: Beverage):
        super().__init__()
        self._beverage = beverage
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass


# Concrete Decorators
class Milk(CondimentDecorator):
    @property
    def description(self) -> str:
        return f"{self._beverage.description}, Milk"
    
    def cost(self) -> float:
        return self._beverage.cost() + 0.30


class Mocha(CondimentDecorator):
    @property
    def description(self) -> str:
        return f"{self._beverage.description}, Mocha"
    
    def cost(self) -> float:
        return self._beverage.cost() + 0.50


class Whip(CondimentDecorator):
    @property
    def description(self) -> str:
        return f"{self._beverage.description}, Whip"
    
    def cost(self) -> float:
        return self._beverage.cost() + 0.40


class Soy(CondimentDecorator):
    @property
    def description(self) -> str:
        return f"{self._beverage.description}, Soy"
    
    def cost(self) -> float:
        return self._beverage.cost() + 0.45


# Demo
if __name__ == "__main__":
    # Order 1: Simple Espresso
    beverage1 = Espresso()
    print(f"{beverage1.description} ${beverage1.cost():.2f}")
    
    # Order 2: Dark Roast with double Mocha and Whip
    beverage2 = DarkRoast()
    beverage2 = Mocha(beverage2)
    beverage2 = Mocha(beverage2)  # Double mocha
    beverage2 = Whip(beverage2)
    print(f"{beverage2.description} ${beverage2.cost():.2f}")
    
    # Order 3: House Blend with Soy, Mocha, and Whip
    beverage3 = HouseBlend()
    beverage3 = Soy(beverage3)
    beverage3 = Mocha(beverage3)
    beverage3 = Whip(beverage3)
    print(f"{beverage3.description} ${beverage3.cost():.2f}")
    
    # Order 4: Espresso with everything
    beverage4 = Espresso()
    beverage4 = Milk(beverage4)
    beverage4 = Mocha(beverage4)
    beverage4 = Soy(beverage4)
    beverage4 = Whip(beverage4)
    print(f"{beverage4.description} ${beverage4.cost():.2f}")

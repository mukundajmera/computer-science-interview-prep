"""
Strategy Pattern - V3 Advanced: Composable Discount Strategies

Demonstrates:
- Protocol-based strategy interface
- Composable/chainable strategies
- Strategy selection algorithms
- Dataclass-based strategies
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, List, Callable
from functools import reduce

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')



# Protocol-based strategy (Python 3.8+)
class DiscountStrategy(Protocol):
    def apply(self, price: float) -> float: ...
    def description(self) -> str: ...


# Concrete strategies using dataclasses
@dataclass
class NoDiscount:
    """No discount applied"""
    
    def apply(self, price: float) -> float:
        return price
    
    def description(self) -> str:
        return "No discount"


@dataclass
class PercentageDiscount:
    """Percentage-based discount"""
    percentage: float
    
    def apply(self, price: float) -> float:
        return price * (1 - self.percentage / 100)
    
    def description(self) -> str:
        return f"{self.percentage:.0f}% off"


@dataclass
class FixedDiscount:
    """Fixed amount discount"""
    amount: float
    
    def apply(self, price: float) -> float:
        return max(0, price - self.amount)
    
    def description(self) -> str:
        return f"${self.amount:.2f} off"


@dataclass
class ThresholdDiscount:
    """Apply discount only above threshold"""
    threshold: float
    discount: DiscountStrategy
    
    def apply(self, price: float) -> float:
        if price >= self.threshold:
            return self.discount.apply(price)
        return price
    
    def description(self) -> str:
        return f"{self.discount.description()} (orders over ${self.threshold:.0f})"


@dataclass
class BuyXGetYDiscount:
    """Buy X items, get Y free"""
    buy: int
    get_free: int
    unit_price: float
    
    def apply(self, price: float) -> float:
        # Calculate effective discount
        full_sets = int(price / self.unit_price) // (self.buy + self.get_free)
        savings = full_sets * self.get_free * self.unit_price
        return price - savings
    
    def description(self) -> str:
        return f"Buy {self.buy} Get {self.get_free} Free"


# Composite strategies
class CompositeDiscount:
    """Chain multiple discounts (applied sequentially)"""
    
    def __init__(self, *strategies: DiscountStrategy):
        self._strategies = list(strategies)
    
    def add(self, strategy: DiscountStrategy) -> "CompositeDiscount":
        self._strategies.append(strategy)
        return self
    
    def apply(self, price: float) -> float:
        return reduce(lambda p, s: s.apply(p), self._strategies, price)
    
    def description(self) -> str:
        return " + ".join(s.description() for s in self._strategies)


class BestDiscount:
    """Select the best discount for the customer"""
    
    def __init__(self, *strategies: DiscountStrategy):
        self._strategies = list(strategies)
    
    def add(self, strategy: DiscountStrategy) -> "BestDiscount":
        self._strategies.append(strategy)
        return self
    
    def apply(self, price: float) -> float:
        if not self._strategies:
            return price
        return min(s.apply(price) for s in self._strategies)
    
    def description(self) -> str:
        return "Best available discount"


# Context
@dataclass
class PricingEngine:
    strategy: DiscountStrategy = None
    
    def __post_init__(self):
        if self.strategy is None:
            self.strategy = NoDiscount()
    
    def set_strategy(self, strategy: DiscountStrategy) -> None:
        self.strategy = strategy
        print(f"Strategy: {strategy.description()}")
    
    def calculate(self, base_price: float) -> float:
        final = self.strategy.apply(base_price)
        savings = base_price - final
        print(f"  ${base_price:.2f} -> ${final:.2f} (saved ${savings:.2f})")
        return final


# Functional approach - strategy as callable
DiscountFn = Callable[[float], float]


def make_percentage_discount(pct: float) -> DiscountFn:
    return lambda price: price * (1 - pct / 100)


def make_fixed_discount(amount: float) -> DiscountFn:
    return lambda price: max(0, price - amount)


def compose_discounts(*fns: DiscountFn) -> DiscountFn:
    return lambda price: reduce(lambda p, f: f(p), fns, price)


if __name__ == "__main__":
    engine = PricingEngine()
    
    print("=== Simple Discounts ===")
    engine.set_strategy(PercentageDiscount(20))
    engine.calculate(100)
    
    engine.set_strategy(FixedDiscount(15))
    engine.calculate(100)
    
    print("\n=== Threshold Discount ===")
    threshold = ThresholdDiscount(50, PercentageDiscount(10))
    engine.set_strategy(threshold)
    engine.calculate(40)   # Below threshold
    engine.calculate(100)  # Above threshold
    
    print("\n=== Composite Discount ===")
    combo = CompositeDiscount(
        PercentageDiscount(10),  # 10% off first
        FixedDiscount(5)         # Then $5 off
    )
    engine.set_strategy(combo)
    engine.calculate(100)  # 100 -> 90 -> 85
    
    print("\n=== Best Discount Selector ===")
    best = BestDiscount(
        PercentageDiscount(15),  # $85
        FixedDiscount(20)        # $80 <- Best
    )
    engine.set_strategy(best)
    engine.calculate(100)
    
    print("\n=== Functional Approach ===")
    ten_off = make_percentage_discount(10)
    five_dollars_off = make_fixed_discount(5)
    combined = compose_discounts(ten_off, five_dollars_off)
    
    price = 100
    print(f"  10% off: ${ten_off(price):.2f}")
    print(f"  $5 off: ${five_dollars_off(price):.2f}")
    print(f"  Combined: ${combined(price):.2f}")

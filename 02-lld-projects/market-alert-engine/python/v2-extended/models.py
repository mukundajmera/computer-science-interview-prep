from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from typing import List

@dataclass(frozen=True)
class Tick:
    symbol: str
    price: float
    volume: int
    timestamp: int

class Operator(Enum):
    GREATER_THAN = 1
    LESS_THAN = 2
    EQUAL = 3

class Condition(ABC):
    @abstractmethod
    def evaluate(self, tick: Tick) -> bool:
        pass

class PriceCondition(Condition):
    def __init__(self, threshold: float, operator: Operator):
        self.threshold = threshold
        self.operator = operator

    def evaluate(self, tick: Tick) -> bool:
        if self.operator == Operator.GREATER_THAN:
            return tick.price > self.threshold
        elif self.operator == Operator.LESS_THAN:
            return tick.price < self.threshold
        elif self.operator == Operator.EQUAL:
            return tick.price == self.threshold
        return False

class VolumeCondition(Condition):
    def __init__(self, threshold: int, operator: Operator):
        self.threshold = threshold
        self.operator = operator

    def evaluate(self, tick: Tick) -> bool:
        if self.operator == Operator.GREATER_THAN:
            return tick.volume > self.threshold
        elif self.operator == Operator.LESS_THAN:
            return tick.volume < self.threshold
        elif self.operator == Operator.EQUAL:
            return tick.volume == self.threshold
        return False

class AndCondition(Condition):
    def __init__(self, left: Condition, right: Condition):
        self.left = left
        self.right = right

    def evaluate(self, tick: Tick) -> bool:
        return self.left.evaluate(tick) and self.right.evaluate(tick)

class OrCondition(Condition):
    def __init__(self, left: Condition, right: Condition):
        self.left = left
        self.right = right

    def evaluate(self, tick: Tick) -> bool:
        return self.left.evaluate(tick) or self.right.evaluate(tick)

class NotCondition(Condition):
    def __init__(self, condition: Condition):
        self.condition = condition

    def evaluate(self, tick: Tick) -> bool:
        return not self.condition.evaluate(tick)

class Sink(ABC):
    @abstractmethod
    def send(self, rule: 'AlertRule', tick: Tick):
        pass

@dataclass(frozen=True)
class AlertRule:
    rule_id: str
    symbol: str
    condition: Condition
    cooldown_ms: int
    sinks: List[Sink]

class PercentChangeCondition(Condition):
    def __init__(self, percent_threshold: float, time_window_ms: int):
        self.percent_threshold = percent_threshold
        self.time_window_ms = time_window_ms
        self.tick_history = {}  # type: dict[str, list[Tick]]
        import threading
        self.lock = threading.Lock()

    def evaluate(self, tick: Tick) -> bool:
        with self.lock:
            if tick.symbol not in self.tick_history:
                self.tick_history[tick.symbol] = []
            
            window = self.tick_history[tick.symbol]
            window.append(tick)
            
            # Evict old ticks
            cutoff_time = tick.timestamp - self.time_window_ms
            # Filter out old ones
            window = [t for t in window if t.timestamp >= cutoff_time]
            self.tick_history[tick.symbol] = window
            
            if len(window) < 2:
                return False
                
            min_price = min(t.price for t in window)
            max_price = max(t.price for t in window)
            
            current_change = ((max_price - min_price) / min_price) * 100.0
            return current_change > self.percent_threshold

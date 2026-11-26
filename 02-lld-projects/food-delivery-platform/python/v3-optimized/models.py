from enum import Enum
import threading

class OrderState(Enum):
    CREATED = 1
    ACCEPTED = 2
    PREPARING = 3
    OUT_FOR_DELIVERY = 4
    DELIVERED = 5

class PricingStrategy:
    def calculate_price(self, base_total: float, active_orders: int, available_drivers: int) -> float:
        pass

class SurgePricingStrategy(PricingStrategy):
    def calculate_price(self, base_total: float, active_orders: int, available_drivers: int) -> float:
        if available_drivers == 0:
            return base_total * 2.0
        ratio = active_orders / available_drivers
        if ratio > 2.0:
            return base_total * 1.5
        elif ratio > 1.0:
            return base_total * 1.2
        return base_total

class Order:
    def __init__(self, order_id: str, base_total: float):
        self.id = order_id
        self.base_total = base_total
        self.final_total = base_total
        self._state = OrderState.CREATED
        self._lock = threading.Lock()
        
    @property
    def state(self) -> OrderState:
        with self._lock:
            return self._state
            
    def transition_state(self, expected_current: OrderState, next_state: OrderState):
        with self._lock:
            if self._state != expected_current:
                raise ValueError("Concurrent modification or invalid state")
            if not self._is_valid_transition(self._state, next_state):
                raise ValueError("Invalid state transition")
            self._state = next_state
            
    def _is_valid_transition(self, current: OrderState, next_state: OrderState) -> bool:
        if current == OrderState.CREATED and next_state == OrderState.ACCEPTED: return True
        if current == OrderState.ACCEPTED and next_state == OrderState.PREPARING: return True
        if current == OrderState.PREPARING and next_state == OrderState.OUT_FOR_DELIVERY: return True
        if current == OrderState.OUT_FOR_DELIVERY and next_state == OrderState.DELIVERED: return True
        return False

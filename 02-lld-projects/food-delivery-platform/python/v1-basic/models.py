from enum import Enum
from typing import List
import threading

class MenuItem:
    def __init__(self, item_id: str, name: str, price: float):
        self.id = item_id
        self.name = name
        self.price = price

class Menu:
    def __init__(self):
        self.items: List[MenuItem] = []
        
    def add_item(self, item: MenuItem):
        self.items.append(item)

class Cart:
    def __init__(self):
        self.items: List[MenuItem] = []
        
    def add_item(self, item: MenuItem):
        self.items.append(item)
        
    def get_total(self) -> float:
        return sum(item.price for item in self.items)
        
    def clear(self):
        self.items.clear()

class OrderState(Enum):
    CREATED = 1
    RESERVATION = 2
    ACCEPTED = 3
    PREPARING = 4
    OUT_FOR_DELIVERY = 5
    DELIVERED = 6
    PAYMENT = 7
    COURIER_DISPATCH = 8

class Order:
    def __init__(self, order_id: str, items_or_total, total: float = None):
        self.id = order_id
        if total is None:
            # called as Order(id, total)
            self.items = []
            self.total = items_or_total
            self.final_total = items_or_total
        else:
            # called as Order(id, items, total)
            self.items = items_or_total
            self.total = total
            self.final_total = total
            
        self.state = OrderState.CREATED
        self._state_lock = threading.Lock()
        
    def set_state(self, state: OrderState):
        with self._state_lock:
            self.state = state
            
    def transition_state(self, expected_current: OrderState, next_state: OrderState):
        with self._state_lock:
            if not self._is_valid_transition(expected_current, next_state):
                raise ValueError("Invalid state transition")
            if self.state != expected_current:
                raise ValueError("Concurrent modification or invalid state")
            self.state = next_state
            
    def _is_valid_transition(self, current: OrderState, next_state: OrderState) -> bool:
        if current == OrderState.CREATED and next_state == OrderState.RESERVATION: return True
        if current == OrderState.RESERVATION and next_state == OrderState.ACCEPTED: return True
        if current == OrderState.ACCEPTED and next_state == OrderState.COURIER_DISPATCH: return True
        if current == OrderState.COURIER_DISPATCH and next_state == OrderState.PAYMENT: return True
        return False

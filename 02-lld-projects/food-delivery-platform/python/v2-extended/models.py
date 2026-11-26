import math
from typing import List, Optional

class Location:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        
    def distance_to(self, other: 'Location') -> float:
        return math.sqrt((self.latitude - other.latitude)**2 + (self.longitude - other.longitude)**2)

import threading

class Driver:
    def __init__(self, driver_id: str, location: Location):
        self.id = driver_id
        self.location = location
        self._lock = threading.Lock()
        
    @property
    def available(self):
        return not self._lock.locked()
        
    def set_available(self, available: bool):
        if not available:
            self._lock.acquire(blocking=False)
        else:
            try:
                self._lock.release()
            except RuntimeError:
                pass
                
    def try_claim(self) -> bool:
        return self._lock.acquire(blocking=False)
        
    def release(self):
        try:
            self._lock.release()
        except RuntimeError:
            pass

class Restaurant:
    def __init__(self, restaurant_id: str, location: Location):
        self.id = restaurant_id
        self.location = location

class DispatchStrategy:
    def dispatch(self, restaurant: Restaurant, drivers: List[Driver]) -> Optional[Driver]:
        pass

class NearestDriverStrategy(DispatchStrategy):
    def dispatch(self, restaurant: Restaurant, drivers: List[Driver]) -> Optional[Driver]:
        nearest = None
        min_distance = float('inf')
        
        for driver in drivers:
            if driver.available:
                distance = driver.location.distance_to(restaurant.location)
                if distance < min_distance:
                    min_distance = distance
                    nearest = driver
                    
        return nearest

class DriverManager:
    def __init__(self, strategy: DispatchStrategy):
        self.drivers: List[Driver] = []
        self.strategy = strategy
        
    def add_driver(self, driver: Driver):
        self.drivers.append(driver)
        
    def assign_driver(self, restaurant: Restaurant) -> Optional[Driver]:
        while True:
            assigned = self.strategy.dispatch(restaurant, self.drivers)
            if not assigned:
                return None
            if assigned.try_claim():
                return assigned

from enum import Enum

class OrderState(Enum):
    CREATED = 1
    RESERVATION = 2
    ACCEPTED = 3
    COURIER_DISPATCH = 4
    PAYMENT = 5

class Order:
    def __init__(self, order_id: str, final_total: float):
        self.id = order_id
        self.final_total = final_total
        self.state = OrderState.CREATED
        self._state_lock = threading.Lock()
        
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

class FoodDeliveryPlatform:
    def __init__(self, driver_manager: Optional[DriverManager] = None):
        self.driver_manager = driver_manager

    def process_order(self, order: Order, restaurant: Restaurant, restaurant_accepts: bool, stock_available: bool) -> bool:
        if not stock_available:
            return False
            
        try:
            order.transition_state(OrderState.CREATED, OrderState.RESERVATION)
        except ValueError:
            return False
            
        if not restaurant_accepts:
            return False
            
        try:
            order.transition_state(OrderState.RESERVATION, OrderState.ACCEPTED)
        except ValueError:
            return False
            
        if not self.driver_manager:
            return False
            
        assigned = self.driver_manager.assign_driver(restaurant)
        if not assigned:
            return False
            
        try:
            order.transition_state(OrderState.ACCEPTED, OrderState.COURIER_DISPATCH)
            return True
        except ValueError:
            assigned.release()
            return False

import threading
import uuid
from typing import List, Optional, Dict
from models import Driver, Rider, Trip, Location, DriverState, TripState

class PricingEngine:
    def __init__(self, base_fare: float = 5.0, per_mile_rate: float = 2.0):
        self.base_fare = base_fare
        self.per_mile_rate = per_mile_rate
        # For simulation, surge is based on demand vs supply in a grid or global
        self.active_requests = 0
        self.available_drivers = 0
        self.lock = threading.RLock()

    def update_supply_demand(self, supply_delta: int, demand_delta: int):
        with self.lock:
            self.available_drivers += supply_delta
            self.active_requests += demand_delta

    def calculate_surge_multiplier(self) -> float:
        with self.lock:
            if self.available_drivers == 0:
                return 2.0 if self.active_requests > 0 else 1.0
            
            ratio = self.active_requests / self.available_drivers
            if ratio > 2.0:
                return 2.0
            elif ratio > 1.0:
                return 1.5
            return 1.0

    def estimate_price(self, origin: Location, destination: Location) -> float:
        distance = origin.distance_to(destination)
        surge = self.calculate_surge_multiplier()
        price = (self.base_fare + distance * self.per_mile_rate) * surge
        return round(price, 2)


class MatchingEngine:
    """
    V1 Basic Version: Uses brute force spatial search and lock-free/coarse-grained driver lists.
    """
    def __init__(self, pricing_engine: PricingEngine, search_radius: float = 10.0):
        self.pricing_engine = pricing_engine
        self.search_radius = search_radius
        self.drivers: Dict[str, Driver] = {}
        self.trips: Dict[str, Trip] = {}
        self.lock = threading.RLock()

    def register_driver(self, driver: Driver):
        if not driver:
            return
        with self.lock:
            if driver.driver_id in self.drivers:
                return
            self.drivers[driver.driver_id] = driver
            if driver.state == DriverState.IDLE:
                self.pricing_engine.update_supply_demand(1, 0)

    def update_driver_state(self, driver_id: str, new_state: DriverState) -> bool:
        with self.lock:
            driver = self.drivers.get(driver_id)
            if not driver:
                return False
            
            old_state = driver.state
            success = driver.transition_state(new_state)
            
            if success:
                # Update supply based on IDLE state
                if old_state == DriverState.IDLE and new_state != DriverState.IDLE:
                    self.pricing_engine.update_supply_demand(-1, 0)
                elif old_state != DriverState.IDLE and new_state == DriverState.IDLE:
                    self.pricing_engine.update_supply_demand(1, 0)
            return success

    def find_nearest_drivers(self, location: Location, limit: int = 5) -> List[Driver]:
        with self.lock:
            idle_drivers = [d for d in self.drivers.values() if d.state == DriverState.IDLE and d.location.distance_to(location) <= self.search_radius]
            # Spatial ranking: Sort by distance
            idle_drivers.sort(key=lambda d: d.location.distance_to(location))
            return idle_drivers[:limit]

    def request_ride(self, rider: Rider, destination: Location) -> Optional[Trip]:
        if not rider or not destination:
            return None
        origin = rider.location
        
        self.pricing_engine.update_supply_demand(0, 1)
        price = self.pricing_engine.estimate_price(origin, destination)
        
        trip_id = str(uuid.uuid4())
        trip = Trip(trip_id, rider, origin, destination, price)
        
        with self.lock:
            self.trips[trip_id] = trip
        
        # Atomic driver allocation
        nearest_drivers = self.find_nearest_drivers(origin)
        for driver in nearest_drivers:
            # Try to transition the driver atomically to ASSIGNED
            if driver.transition_state(DriverState.ASSIGNED):
                if trip.assign_driver(driver):
                    # Successfully matched
                    self.pricing_engine.update_supply_demand(-1, -1) # Driver no longer available, demand fulfilled
                    return trip
                else:
                    # Rollback driver state if trip somehow cannot be assigned
                    driver.transition_state(DriverState.IDLE)
        
        # Failed to find a driver
        self.pricing_engine.update_supply_demand(0, -1)
        trip.state = TripState.CANCELLED
        return None

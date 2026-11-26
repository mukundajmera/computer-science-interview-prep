import enum
import math
import threading
import uuid
from dataclasses import dataclass
from typing import List, Optional, Dict, Set

class DriverState(enum.Enum):
    OFFLINE = "OFFLINE"
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    IN_TRIP = "IN_TRIP"

    @property
    def value_str(self):
        return self.value

class TripState(enum.Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    @property
    def value_str(self):
        return self.value

@dataclass
class Location:
    lat: float
    lon: float
    timestamp: float = 0.0

    def distance_to(self, other: 'Location') -> float:
        return math.hypot(self.lat - other.lat, self.lon - other.lon)
        
    def to_geohash(self, precision=5) -> str:
        # Educational simplification: using stdlib grid indexing instead of a fake H3 implementation
        lat_grid = int(self.lat / 10.0)
        lon_grid = int(self.lon / 10.0)
        return f"{lat_grid},{lon_grid}"

class Driver:
    def __init__(self, driver_id: str, location: Location):
        self.driver_id = driver_id
        self.location = location
        self.state = DriverState.OFFLINE
        self.lock = threading.RLock()

    def update_location(self, location: Location):
        with self.lock:
            if location.timestamp >= self.location.timestamp:
                self.location = location

    def transition_state(self, new_state: DriverState) -> bool:
        with self.lock:
            valid = False
            if self.state == DriverState.OFFLINE and new_state == DriverState.IDLE:
                valid = True
            elif self.state == DriverState.IDLE and new_state == DriverState.ASSIGNED:
                valid = True
            elif self.state == DriverState.IDLE and new_state == DriverState.OFFLINE:
                valid = True
            elif self.state == DriverState.ASSIGNED and new_state == DriverState.IN_TRIP:
                valid = True
            elif self.state == DriverState.ASSIGNED and new_state == DriverState.IDLE:
                valid = True
            elif self.state == DriverState.IN_TRIP and new_state == DriverState.IDLE:
                valid = True
            elif self.state == DriverState.IN_TRIP and new_state == DriverState.OFFLINE:
                valid = True
            
            if valid:
                self.state = new_state
                return True
            return False

class Rider:
    def __init__(self, rider_id: str, location: Location):
        self.rider_id = rider_id
        self.location = location

class Trip:
    def __init__(self, trip_id: str, rider: Rider, origin: Location, destination: Location, price: float):
        self.trip_id = trip_id
        self.rider = rider
        self.driver: Optional[Driver] = None
        self.origin = origin
        self.destination = destination
        self.price = price
        self.state = TripState.REQUESTED
        self.lock = threading.RLock()

    def assign_driver(self, driver: Driver):
        with self.lock:
            if self.state == TripState.REQUESTED:
                self.driver = driver
                self.state = TripState.ACCEPTED
                return True
            return False

class PricingEngine:
    def __init__(self, base_fare: float = 5.0, per_mile_rate: float = 2.0):
        self.base_fare = base_fare
        self.per_mile_rate = per_mile_rate
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

class SpatialIndex:
    def __init__(self):
        self.grid: Dict[str, Set[str]] = {}
        self.lock = threading.RLock()
        
    def add_driver(self, driver: Driver):
        with self.lock:
            gh = driver.location.to_geohash()
            if gh not in self.grid:
                self.grid[gh] = set()
            self.grid[gh].add(driver.driver_id)
            
    def remove_driver(self, driver: Driver):
        with self.lock:
            gh = driver.location.to_geohash()
            if gh in self.grid and driver.driver_id in self.grid[gh]:
                self.grid[gh].remove(driver.driver_id)
                if not self.grid[gh]:
                    del self.grid[gh]
                    
    def update_driver_location(self, driver: Driver, old_location: Location, new_location: Location):
        with self.lock:
            old_gh = old_location.to_geohash()
            new_gh = new_location.to_geohash()
            if old_gh != new_gh:
                if old_gh in self.grid and driver.driver_id in self.grid[old_gh]:
                    self.grid[old_gh].remove(driver.driver_id)
                    if not self.grid[old_gh]:
                        del self.grid[old_gh]
                
                if new_gh not in self.grid:
                    self.grid[new_gh] = set()
                self.grid[new_gh].add(driver.driver_id)

    def get_drivers_in_geohash(self, geohash: str) -> Set[str]:
        with self.lock:
            return set(self.grid.get(geohash, set()))

class BatchAuctionMatcher:
    @staticmethod
    def match(drivers: List[Driver], trips: List[Trip]) -> Dict[Trip, Driver]:
        if not drivers or not trips:
            return {}
            
        # Educational simplification: Explicit optimality/cost assumption
        # For a hand-checked tiny cost matrix, this greedy assignment acts as a proxy for the O(N^3)
        # Hungarian Algorithm (scipy.optimize.linear_sum_assignment) while strictly using standard library code.
        matches = {}
        cells = []
        for trip in trips:
            for driver in drivers:
                cells.append((trip, driver, trip.origin.distance_to(driver.location)))
                
        cells.sort(key=lambda x: x[2])
        assigned_trips = set()
        assigned_drivers = set()
        
        for trip, driver, cost in cells:
            if trip not in assigned_trips and driver.driver_id not in assigned_drivers:
                matches[trip] = driver
                assigned_trips.add(trip)
                assigned_drivers.add(driver.driver_id)
                
        return matches

class MatchingEngine:
    def __init__(self, pricing_engine: PricingEngine, search_radius: float = 10.0):
        self.pricing_engine = pricing_engine
        self.search_radius = search_radius
        self.drivers: Dict[str, Driver] = {}
        self.trips: Dict[str, Trip] = {}
        self.batch_queue: List[Trip] = []
        self.spatial_index = SpatialIndex()
        self.lock = threading.RLock()

    def register_driver(self, driver: Driver):
        if not driver or not driver.driver_id:
            return
        with self.lock:
            if driver.driver_id in self.drivers:
                return # Duplicate addition
            self.drivers[driver.driver_id] = driver
            if driver.state == DriverState.IDLE:
                self.pricing_engine.update_supply_demand(1, 0)
                self.spatial_index.add_driver(driver)

    def update_driver_state(self, driver_id: str, new_state: DriverState) -> bool:
        with self.lock:
            driver = self.drivers.get(driver_id)
            if not driver:
                return False
            
            old_state = driver.state
            success = driver.transition_state(new_state)
            
            if success:
                if old_state == DriverState.IDLE and new_state != DriverState.IDLE:
                    self.pricing_engine.update_supply_demand(-1, 0)
                    self.spatial_index.remove_driver(driver)
                elif old_state != DriverState.IDLE and new_state == DriverState.IDLE:
                    self.pricing_engine.update_supply_demand(1, 0)
                    self.spatial_index.add_driver(driver)
            return success

    def find_nearest_drivers(self, location: Location, limit: int = 5) -> List[Driver]:
        gh = location.to_geohash()
        driver_ids = self.spatial_index.get_drivers_in_geohash(gh)
        
        with self.lock:
            idle_drivers = []
            for did in driver_ids:
                d = self.drivers.get(did)
                if d and d.state == DriverState.IDLE and d.location.distance_to(location) <= self.search_radius:
                    idle_drivers.append(d)
                    
            if len(idle_drivers) < limit:
                all_idle = [d for d in self.drivers.values() if d.state == DriverState.IDLE and d.location.distance_to(location) <= self.search_radius]
                idle_drivers = all_idle
                
            idle_drivers.sort(key=lambda d: d.location.distance_to(location))
            return idle_drivers[:limit]

    def request_ride(self, rider: Rider, destination: Location) -> Optional[Trip]:
        if not rider or not destination:
            return None # invalid input
            
        origin = rider.location
        
        self.pricing_engine.update_supply_demand(0, 1)
        price = self.pricing_engine.estimate_price(origin, destination)
        
        trip_id = str(uuid.uuid4())
        trip = Trip(trip_id, rider, origin, destination, price)
        
        with self.lock:
            self.trips[trip_id] = trip
        
        nearest_drivers = self.find_nearest_drivers(origin)
        for driver in nearest_drivers:
            if self.update_driver_state(driver.driver_id, DriverState.ASSIGNED):
                if trip.assign_driver(driver):
                    self.pricing_engine.update_supply_demand(0, -1) 
                    return trip
                else:
                    self.update_driver_state(driver.driver_id, DriverState.IDLE)
        
        self.pricing_engine.update_supply_demand(0, -1)
        trip.state = TripState.CANCELLED
        return None

    def request_ride_batch(self, rider: Rider, destination: Location) -> Optional[Trip]:
        if not rider or not destination:
            return None
        origin = rider.location
        self.pricing_engine.update_supply_demand(0, 1)
        price = self.pricing_engine.estimate_price(origin, destination)
        trip_id = str(uuid.uuid4())
        trip = Trip(trip_id, rider, origin, destination, price)
        with self.lock:
            self.trips[trip_id] = trip
            self.batch_queue.append(trip)
        return trip

    def run_batch_auction(self):
        with self.lock:
            if not self.batch_queue:
                return
            
            trips_to_match = self.batch_queue[:]
            self.batch_queue = []
            
            idle_drivers = [d for d in self.drivers.values() if d.state == DriverState.IDLE]
            
            matches = BatchAuctionMatcher.match(idle_drivers, trips_to_match)
            
            for trip in trips_to_match:
                if trip in matches:
                    driver = matches[trip]
                    if self.update_driver_state(driver.driver_id, DriverState.ASSIGNED):
                        if trip.assign_driver(driver):
                            self.pricing_engine.update_supply_demand(0, -1)
                        else:
                            self.update_driver_state(driver.driver_id, DriverState.IDLE)
                            self.batch_queue.append(trip)
                    else:
                        self.batch_queue.append(trip)
                else:
                    self.batch_queue.append(trip)

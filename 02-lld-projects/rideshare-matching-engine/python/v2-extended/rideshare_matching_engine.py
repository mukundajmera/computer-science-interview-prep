import threading
import uuid
import time
from typing import List, Optional, Dict, Set
import math

from models import Driver, Rider, Trip, Location, DriverState, TripState

class HungarianAlgorithm:
    """
    O(n^3) Hungarian matching algorithm.
    Optimality/Cost assumptions: 
    - Cost is typically Euclidean or Haversine distance, representing travel time/fuel.
    - Finds the global minimum cost bipartite matching (optimal assignment).
    - Minimizes total distance traveled by all drivers to reach all riders, 
      rather than just assigning the closest driver sequentially.
    """
    def __init__(self, cost_matrix):
        self.rows = len(cost_matrix)
        self.cols = len(cost_matrix[0]) if self.rows > 0 else 0
        self.dim = max(self.rows, self.cols)
        
        self.cost_matrix = [[0.0] * self.dim for _ in range(self.dim)]
        for w in range(self.dim):
            if w < self.rows:
                for j in range(self.cols):
                    self.cost_matrix[w][j] = float(cost_matrix[w][j])
                    
        self.label_by_worker = [0.0] * self.dim
        self.label_by_job = [0.0] * self.dim
        self.min_slack_worker_by_job = [0] * self.dim
        self.min_slack_value_by_job = [0.0] * self.dim
        self.match_job_by_worker = [-1] * self.dim
        self.match_worker_by_job = [-1] * self.dim
        self.parent_worker_by_committed_job = [-1] * self.dim
        self.committed_workers = [False] * self.dim

    def compute_initial_feasible_solution(self):
        for j in range(self.dim):
            self.label_by_job[j] = float('inf')
        for w in range(self.dim):
            for j in range(self.dim):
                if self.cost_matrix[w][j] < self.label_by_worker[w]:
                    self.label_by_worker[w] = self.cost_matrix[w][j]

    def execute(self):
        self.reduce()
        self.compute_initial_feasible_solution()
        self.greedy_match()
        w = self.fetch_unmatched_worker()
        while w < self.dim:
            self.initialize_phase(w)
            self.execute_phase()
            w = self.fetch_unmatched_worker()
        
        result = self.match_job_by_worker[:self.rows]
        for i in range(len(result)):
            if result[i] >= self.cols:
                result[i] = -1
        return result

    def execute_phase(self):
        while True:
            min_slack_worker = -1
            min_slack_job = -1
            min_slack_value = float('inf')
            
            for j in range(self.dim):
                if self.parent_worker_by_committed_job[j] == -1:
                    if self.min_slack_value_by_job[j] < min_slack_value:
                        min_slack_value = self.min_slack_value_by_job[j]
                        min_slack_worker = self.min_slack_worker_by_job[j]
                        min_slack_job = j
                        
            if min_slack_value > 0:
                self.update_labels(min_slack_value)
                
            self.parent_worker_by_committed_job[min_slack_job] = min_slack_worker
            if self.match_worker_by_job[min_slack_job] == -1:
                committed_job = min_slack_job
                parent_worker = self.parent_worker_by_committed_job[committed_job]
                while True:
                    temp = self.match_job_by_worker[parent_worker]
                    self.match(parent_worker, committed_job)
                    committed_job = temp
                    if committed_job == -1:
                        break
                    parent_worker = self.parent_worker_by_committed_job[committed_job]
                return
            else:
                worker = self.match_worker_by_job[min_slack_job]
                self.committed_workers[worker] = True
                for j in range(self.dim):
                    if self.parent_worker_by_committed_job[j] == -1:
                        slack = self.cost_matrix[worker][j] - self.label_by_worker[worker] - self.label_by_job[j]
                        if self.min_slack_value_by_job[j] > slack:
                            self.min_slack_value_by_job[j] = slack
                            self.min_slack_worker_by_job[j] = worker

    def fetch_unmatched_worker(self):
        for w in range(self.dim):
            if self.match_job_by_worker[w] == -1:
                return w
        return self.dim

    def greedy_match(self):
        for w in range(self.dim):
            for j in range(self.dim):
                if self.match_job_by_worker[w] == -1 and self.match_worker_by_job[j] == -1 and abs(self.cost_matrix[w][j] - self.label_by_worker[w] - self.label_by_job[j]) < 1e-9:
                    self.match(w, j)

    def initialize_phase(self, w):
        for i in range(self.dim):
            self.committed_workers[i] = False
            self.parent_worker_by_committed_job[i] = -1
        self.committed_workers[w] = True
        for j in range(self.dim):
            self.min_slack_value_by_job[j] = self.cost_matrix[w][j] - self.label_by_worker[w] - self.label_by_job[j]
            self.min_slack_worker_by_job[j] = w

    def match(self, w, j):
        self.match_job_by_worker[w] = j
        self.match_worker_by_job[j] = w

    def reduce(self):
        for w in range(self.dim):
            min_val = float('inf')
            for j in range(self.dim):
                if self.cost_matrix[w][j] < min_val:
                    min_val = self.cost_matrix[w][j]
            for j in range(self.dim):
                self.cost_matrix[w][j] -= min_val
                
        min_vals = [float('inf')] * self.dim
        for w in range(self.dim):
            for j in range(self.dim):
                if self.cost_matrix[w][j] < min_vals[j]:
                    min_vals[j] = self.cost_matrix[w][j]
        for w in range(self.dim):
            for j in range(self.dim):
                self.cost_matrix[w][j] -= min_vals[j]

    def update_labels(self, slack):
        for w in range(self.dim):
            if self.committed_workers[w]:
                self.label_by_worker[w] += slack
        for j in range(self.dim):
            if self.parent_worker_by_committed_job[j] != -1:
                self.label_by_job[j] -= slack
            else:
                self.min_slack_value_by_job[j] -= slack

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


class BatchAuctionMatcher:
    @staticmethod
    def match(drivers: List[Driver], trips: List[Trip]) -> Dict[Trip, Driver]:
        if not drivers or not trips:
            return {}
            
        # Build cost matrix
        # Cost is distance between trip origin and driver location
        cost_matrix = [[0.0] * len(drivers) for _ in range(len(trips))]
        
        for i, trip in enumerate(trips):
            for j, driver in enumerate(drivers):
                cost_matrix[i][j] = trip.origin.distance_to(driver.location)
                
        # Hungarian Algorithm
        hungarian = HungarianAlgorithm(cost_matrix)
        result = hungarian.execute()
        
        matches = {}
        for i in range(len(result)):
            if result[i] != -1 and i < len(trips):
                matches[trips[i]] = drivers[result[i]]
            
        return matches

class SpatialIndex:
    """
    Educational simplification using standard library geohash/grid indexing.
    Not a fake H3 implementation.
    """
    def __init__(self):
        self.grid = {}
        self.lock = threading.RLock()

    def add_driver(self, driver: Driver):
        gh = self._to_geohash(driver.location)
        with self.lock:
            if gh not in self.grid:
                self.grid[gh] = set()
            self.grid[gh].add(driver.driver_id)

    def remove_driver(self, driver: Driver):
        gh = self._to_geohash(driver.location)
        with self.lock:
            if gh in self.grid:
                self.grid[gh].discard(driver.driver_id)
                if not self.grid[gh]:
                    del self.grid[gh]

    def get_drivers_in_geohash(self, geohash: str) -> Set[str]:
        with self.lock:
            return set(self.grid.get(geohash, set()))
            
    def _to_geohash(self, location: Location, precision=5) -> str:
        # Mock geohash based on simple grid mapping.
        # In a real system, you'd use a geohash library.
        lat_grid = round(location.lat * precision)
        lon_grid = round(location.lon * precision)
        return f"{lat_grid},{lon_grid}"

class RideshareMatchingEngine:
    def __init__(self, pricing_engine: PricingEngine, search_radius: float = 10.0):
        self.pricing_engine = pricing_engine
        self.search_radius = search_radius
        self.drivers: Dict[str, Driver] = {}
        self.trips: Dict[str, Trip] = {}
        self.spatial_index = SpatialIndex()
        self.batch_queue: List[Trip] = []
        
        self.lock = threading.RLock()

    def register_driver(self, driver: Driver):
        with self.lock:
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
                # Update supply based on IDLE state
                if old_state == DriverState.IDLE and new_state != DriverState.IDLE:
                    self.pricing_engine.update_supply_demand(-1, 0)
                    self.spatial_index.remove_driver(driver)
                elif old_state != DriverState.IDLE and new_state == DriverState.IDLE:
                    self.pricing_engine.update_supply_demand(1, 0)
                    self.spatial_index.add_driver(driver)
            return success

    def find_nearest_drivers(self, location: Location, limit: int = 5) -> List[Driver]:
        with self.lock:
            gh = self.spatial_index._to_geohash(location)
            driver_ids = self.spatial_index.get_drivers_in_geohash(gh)
            
            idle_drivers = []
            if len(driver_ids) >= limit:
                 idle_drivers = [self.drivers[d_id] for d_id in driver_ids if self.drivers[d_id].state == DriverState.IDLE and self.drivers[d_id].location.distance_to(location) <= self.search_radius]
            else:
                 idle_drivers = [d for d in self.drivers.values() if d.state == DriverState.IDLE and d.location.distance_to(location) <= self.search_radius]
                 
            idle_drivers.sort(key=lambda d: d.location.distance_to(location))
            return idle_drivers[:limit]

    def request_ride(self, rider: Rider, destination: Location) -> Trip:
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
                    if driver.transition_state(DriverState.ASSIGNED):
                        self.spatial_index.remove_driver(driver)
                        if trip.assign_driver(driver):
                            self.pricing_engine.update_supply_demand(-1, -1)
                        else:
                            driver.transition_state(DriverState.IDLE)
                            self.spatial_index.add_driver(driver)
                            self.batch_queue.append(trip) # retry next batch
                    else:
                        self.batch_queue.append(trip) # retry next batch
                else:
                    self.batch_queue.append(trip)
